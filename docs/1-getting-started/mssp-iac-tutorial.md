# Tutorial: Run Your MSSP from Git with Git Sync

By the end of this tutorial, every customer organization you run is configured from one private Git repository. A merge to `main` changes the detection rules, false-positive rules, outputs and extension settings of every customer. Nobody runs a CLI to deploy. The [Git Sync extension](../5-integrations/extensions/limacharlie/git-sync.md) does the work, and a new customer takes a few minutes to add.

It uses the fictional MSSP from the [MSSP walkthrough](mssp-walkthrough.md): **Northwind Security**, with customers **ACME**, **Globex** and, later, **Initech**. The walkthrough tours the whole platform. This page covers only the infrastructure-as-code part.

You need:

- A LimaCharlie account and the [`limacharlie` CLI](../6-developer-guide/cli-quickstart.md), signed in. Most steps also have a web app path, shown where it exists.
- `git`, `ssh-keygen` and `jq`.
- A Git host that serves repositories over SSH and supports deploy keys. The examples use GitHub. GitLab, Bitbucket and self-hosted servers work the same way.

## How Git Sync works

Read this first. It explains most of the choices below.

- **Each organization is configured separately.** Git Sync stores its settings (repository, branch, key, what to sync, schedules) in each org. You set it up once per org, and a script makes that cheap.
- **One repository serves every org.** An org reads only `orgs/<its OID>/index.yaml` from the repository. That file includes shared files, so a rule written once in `global/` reaches every customer.
- **Pull applies Git to the org.** The extension calls this *apply* (the UI button is **PULL FROM GIT**). It adds and updates records. **It never deletes.** If you remove a rule from Git, the rule stays in the org until you delete it there. [Step 11](#step-11-delete-things) shows how.
- **Push writes the org to Git.** The extension calls this *export* (**PUSH TO GIT**). It writes to `exports/orgs/<OID>/` and never touches `orgs/`. You use it once to bootstrap the repository, and afterwards to catch changes made in the UI.
- **Nothing syncs by default.** Every "sync this type" and "export this type" switch starts off. A type is only pulled if its switch is on **and** your `index.yaml` includes a file that contains it.
- **Git Sync reads only the `hives:` form** of the configuration files, plus `outputs`, `resources`, `extensions`, `org-value` and `installation_keys`. The older top-level `rules`, `fps`, `integrity`, `exfil`, `artifact` and `yara` keys are ignored without an error. Everything in this tutorial uses `hives:`.

## Step 1: Create the organizations

Create a control org for your own team and one org per customer. Keep every org in one data center region for now (see [Pick one region](mssp-walkthrough.md#pick-one-region-and-stick-with-it-for-now)).

```bash
limacharlie org create --name northwind-control --location usa
limacharlie org create --name northwind-acme --location usa
limacharlie org create --name northwind-globex --location usa
limacharlie org list --output json
```

Put the OIDs in shell variables. The rest of this tutorial uses them.

```bash
export CONTROL_OID=<northwind-control OID>
export ACME_OID=<northwind-acme OID>
export GLOBEX_OID=<northwind-globex OID>
```

## Step 2: Create the repository and a deploy key

Create a private, empty repository on your Git host, for example `northwindsec/mssp-iac`. Do not add a README yet.

Generate an SSH key used by Git Sync and nothing else:

```bash
mkdir -p ~/.ssh/gitsync && chmod 700 ~/.ssh/gitsync
ssh-keygen -t ed25519 -N "" -C "limacharlie-gitsync" -f ~/.ssh/gitsync/id_ed25519
cat ~/.ssh/gitsync/id_ed25519.pub
```

Add the public key to the repository as a deploy key with **write access**. On GitHub: repository **Settings**, **Deploy keys**, **Add deploy key**, paste the key, check **Allow write access**. Git Sync needs write access only to export. If you never export, a read-only key is enough.

Use one key per repository. The same private key goes into every org that uses the repository.

## Step 3: Plan the repository layout

Here is the layout you will have by the end of Step 7. Git Sync creates `exports/`. You write the rest.

```text
mssp-iac/
├── global/                          # shared by every org
│   ├── extensions.yaml
│   ├── outputs.yaml
│   ├── installation_keys.yaml
│   └── hives/
│       ├── dr-general.yaml          # detection rules
│       ├── fp.yaml                  # false-positive rules
│       ├── query.yaml               # saved queries
│       └── extension_config.yaml    # Exfil, Integrity, Artifact, Cases settings
├── orgs/
│   ├── <CONTROL_OID>/
│   │   └── index.yaml
│   ├── <ACME_OID>/
│   │   ├── index.yaml
│   │   └── hives/
│   │       └── dr-general.yaml      # rules only ACME gets
│   └── <GLOBEX_OID>/
│       └── index.yaml
└── exports/                         # written by Git Sync, one folder per org
```

Rules that keep this layout working:

- **The folder name under `orgs/` is the OID.** The extension looks for exactly `orgs/<OID>/index.yaml`. A layout such as `customers/acme/main.yaml` is not found, and the pull fails with `organization not found in the repository`. The control org needs its own folder too.
- **`include:` paths are relative to the file that contains them.** Includes can nest.
- **Name every file in `include:`.** Git Sync does not expand wildcards such as `hives/*.yaml`. The `limacharlie sync` command does, so a repository that works with the CLI can still fail here.
- **Start each file with `version: 3`.**
- **Use `hives:` for rules, false-positive rules, lookups, saved queries, YARA and extension settings.** Each hive is a map of record name to `data:` and `usr_mtd:`. Put `usr_mtd: {enabled: true}` on every record, or the record is created disabled.
- **Do not put the same record name in two files unless you mean it.** When two included files define the same record, the one included later wins, and a record in an included file beats the same record in the file that includes it. Unique names are simpler.

## Step 4: Store the deploy key as a secret in each org

Git Sync reads the key from the org's `secret` hive, so the private key is never pasted into a configuration field that gets exported to Git.

```bash
for OID in $CONTROL_OID $ACME_OID $GLOBEX_OID; do
  jq -Rs '{secret: .}' ~/.ssh/gitsync/id_ed25519 \
    | limacharlie secret set --key gitsync-deploy-key --enabled --oid "$OID"
done
```

In the web app, the same thing is **Organization Settings**, then **Secrets Manager**, then add a secret and paste the private key.

If you do paste the private key straight into the Git Sync **SSH Key** field and later export `extension_config`, the private key is written into your repository. Always use a `hive://secret/...` reference.

## Step 5: Subscribe and configure Git Sync

Write the configuration once, then apply it to each org. The file below turns on the types this tutorial uses, for both pull and export, and leaves schedules off until Step 9.

```yaml title="gitsync.yaml"
data:
  repo_url: git@github.com:northwindsec/mssp-iac.git
  branch: main
  user_name: git
  ssh_key: hive://secret/gitsync-deploy-key
  schedule: "-"
  schedule_export: "-"
  sync_outputs: true
  sync_extensions: true
  sync_installation_keys: true
  sync_hives:
    dr-general: true
    fp: true
    query: true
    extension_config: true
  export_outputs: true
  export_extensions: true
  export_installation_keys: true
  export_hives:
    dr-general: true
    fp: true
    query: true
    extension_config: true
usr_mtd:
  enabled: true
```

`usr_mtd: {enabled: true}` matters. A disabled configuration record is ignored, and every request fails with `ssh key is required`. The web app enables it for you.

```bash
for OID in $CONTROL_OID $ACME_OID $GLOBEX_OID; do
  limacharlie extension subscribe --name ext-infrastructure --oid "$OID"
  limacharlie extension subscribe --name ext-git-sync --oid "$OID"
  limacharlie extension config-set --name ext-git-sync \
    --input-file gitsync.yaml --oid "$OID"
done
```

Git Sync requires the [Infrastructure](../5-integrations/extensions/limacharlie/infrastructure.md) extension, so the loop subscribes to both.

To do this in the web app instead, subscribe from the [Marketplace](https://app.limacharlie.io/add-ons/extension-detail/ext-git-sync), then open **Extensions** in the org's sidebar and select **Git Sync**. Fill in:

| Section | Field | Value |
| --- | --- | --- |
| Git Options | Repository URL | `git@github.com:northwindsec/mssp-iac.git` |
| Git Options | Branch | `main` |
| Git Options | SSH Key | pick the `gitsync-deploy-key` secret |
| Git Options | User Name | `git` |
| Sync Options | PUSH and PULL checkboxes | the types in `gitsync.yaml` |
| Schedule Options | Push Schedule, Pull Schedule | leave empty for now |

Then press **SAVE SETTINGS**.

What the switches mean:

| Setting | Meaning |
| --- | --- |
| `sync_*`, `sync_hives.<hive>` | Types that **pull** applies to the org. Each switch is ignored if no included file holds that type. |
| `export_*`, `export_hives.<hive>` | Types that **push** writes to `exports/`. |
| `user_name` | `git` on GitHub, GitLab and Bitbucket. |
| `schedule`, `schedule_export` | Pull and push intervals: `-` (off), `1h`, `3h`, `6h`, `12h`, `24h` or `168h`. |

Types you should leave off:

- **`secret` hive.** Keep secrets out of Git. Everywhere a config needs a credential, write `hive://secret/<name>` and create the secret in each org.
- **`acl` hive.** Git Sync refuses it.
- **`dr-managed` hive.** Extensions own those rules. Git Sync's own schedule rules live there.
- **Organization values** (`org_values`). They can hold literal third-party API keys, and export would write them to Git.
- **`lookup` and `yara` hives**, until you need them. They can be very large.

Which hives you can name is listed by `limacharlie extension schema --name ext-git-sync`.

## Step 6: Export once to bootstrap the repository

Let the extension write what you already built by hand. First, check what it would write. Outputs and extension settings can contain literal passwords and tokens that someone typed into the UI, and an export commits them to Git as they are.

Dump the two risky types to a local file and search it:

```bash
for OID in $CONTROL_OID $ACME_OID $GLOBEX_OID; do
  limacharlie sync pull --config-file "/tmp/audit-$OID.yaml" --oid "$OID" \
    --outputs --hive-extension-config
  grep -n -i -E 'password|token|secret|api_?key|BEGIN .*PRIVATE KEY' "/tmp/audit-$OID.yaml" \
    | grep -v 'hive://secret/'
done
```

What is left should be harmless names such as `max_tokens`. A credential must read `hive://secret/<name>`. For every literal value, create a secret in that org, change the output or extension setting to the `hive://secret/<name>` reference, and run the check again. Delete the `/tmp/audit-*.yaml` files when you are done. If you skip this and a credential reaches the repository, treat it as leaked and rotate it. Removing the commit is not enough.

Now export. In the web app, press **PUSH TO GIT**. From the CLI:

```bash
for OID in $CONTROL_OID $ACME_OID $GLOBEX_OID; do
  limacharlie extension request --name ext-git-sync --action export --oid "$OID"
done
```

The extension clones the repository, writes `exports/orgs/<OID>/`, commits as "LC Git Sync" and pushes. It also works on an empty repository. Clone it and look:

```bash
git clone git@github.com:northwindsec/mssp-iac.git && cd mssp-iac
find exports -type f | sort
```

```text
exports/orgs/<ACME_OID>/extensions.yaml
exports/orgs/<ACME_OID>/hives/dr-general.yaml
exports/orgs/<ACME_OID>/hives/extension_config.yaml
exports/orgs/<ACME_OID>/hives/fp.yaml
exports/orgs/<ACME_OID>/hives/query.yaml
exports/orgs/<ACME_OID>/index.yaml
exports/orgs/<ACME_OID>/installation_keys.yaml
exports/orgs/<ACME_OID>/outputs.yaml
...
```

Each export replaces that org's whole `exports/orgs/<OID>/` folder, so deletions in the org show up as deletions in Git. If nothing changed, it makes no commit. Run the same search over `exports/` as a second check: `git grep -n -i -E 'password|token|secret|api_?key' -- exports | grep -v 'hive://secret/'`.

Exports go straight to the configured branch. If `main` requires pull requests, the push fails with `protected branch hook declined`. Either let the deploy key bypass the rule (on GitHub, add **Deploy keys** to the bypass list of a branch ruleset), or turn exports off once you have bootstrapped. Pull is read-only and works either way.

## Step 7: Move the shared parts into `global/`

`exports/` is a record of what is in each org. It is not an input: pull never reads it. To manage an org from Git, copy what you want into `global/` and `orgs/`, and delete what you do not.

Start with two detection rules that every customer gets. A rule is a record under the `dr-general` hive:

```yaml title="global/hives/dr-general.yaml"
version: 3
hives:
  dr-general:
    northwind-evil-exe:
      data:
        detect:
          event: NEW_PROCESS
          op: ends with
          path: event/FILE_PATH
          value: northwind-evil.exe
        respond:
          - action: report
            name: northwind-evil-exe
      usr_mtd:
        enabled: true
    northwind-encoded-powershell:
      data:
        detect:
          event: NEW_PROCESS
          op: contains
          path: event/COMMAND_LINE
          value: -EncodedCommand
        respond:
          - action: report
            name: northwind-encoded-powershell
      usr_mtd:
        enabled: true
```

A false-positive rule, and a saved query:

```yaml title="global/hives/fp.yaml"
version: 3
hives:
  fp:
    northwind-fp-backup-agent:
      data:
        op: is
        path: detect/event/FILE_PATH
        value: C:\Program Files\Backup\agent.exe
      usr_mtd:
        enabled: true
```

```yaml title="global/hives/query.yaml"
version: 3
hives:
  query:
    northwind-powershell-launches:
      data:
        query: '-1h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" | event/FILE_PATH as path event/COMMAND_LINE as command_line routing/hostname as host'
      usr_mtd:
        enabled: true
```

The settings of the Exfil, Integrity and Artifact extensions are no longer separate `exfil:`, `integrity:` and `artifact:` sections. Each lives in one record of the `extension_config` hive, named after the extension (`ext-exfil`, `ext-integrity`, `ext-artifact`). Take the record from your export and move it over. For example, file-integrity monitoring on Linux and Windows hosts:

```yaml title="global/hives/extension_config.yaml"
version: 3
hives:
  extension_config:
    ext-integrity:
      data:
        fim_rules:
          linux-ssh-keys:
            filters:
              platforms:
                - linux
              tags: []
            patterns:
              - /root/.ssh/authorized_keys
              - /home/*/.ssh/*
          windows-hosts-file:
            filters:
              platforms:
                - windows
              tags: []
            patterns:
              - c:\windows\system32\drivers\etc\hosts
      usr_mtd:
        enabled: true
```

A pull replaces a record as a whole. After the pull, each org's `ext-integrity` holds exactly the rules in this file, and any rule that existed only in the org is gone. Start from the record in your export so nothing is lost. A customer that needs different Integrity rules gets its own copy of `extension_config.yaml` with the complete `ext-integrity` record, listed in that customer's `index.yaml` instead of the global file. That way no record is defined twice.

Check a record before you commit it. This asks the platform to validate it and changes nothing:

```bash
python3 -c 'import sys, yaml; print(yaml.safe_dump(yaml.safe_load(open(sys.argv[1]))["hives"]["extension_config"]["ext-integrity"]))' \
  global/hives/extension_config.yaml > /tmp/ext-integrity.yaml
limacharlie hive validate --hive-name extension_config --key ext-integrity \
  --input-file /tmp/ext-integrity.yaml --oid "$CONTROL_OID"
```

Add the extension list, an output and the installation keys. The output password is a secret reference. Create that secret in every org that pulls this file, or the output cannot authenticate:

```yaml title="global/extensions.yaml"
version: 3
extensions:
  - ext-cases
  - ext-exfil
  - ext-integrity
```

```yaml title="global/outputs.yaml"
version: 3
outputs:
  northwind-archive-scp:
    dest_host: 203.0.113.10
    dir: /srv/lc-output/
    for: event
    module: scp
    password: hive://secret/northwind-scp-password
    username: lc-export
```

```yaml title="global/installation_keys.yaml"
version: 3
installation_keys:
  northwind-server:
    tags:
      - server
  northwind-workstation:
    tags:
      - workstation
  northwind-vip:
    tags:
      - vip
      - workstation
  northwind-sleeper:
    tags:
      - lc:sleeper
```

The name of an installation key in the file is its description in the org. Git Sync matches existing keys by that description, and a `desc:` field next to the tags is ignored.

Now one folder per org. ACME gets everything global plus one rule of its own:

```yaml title="orgs/<ACME_OID>/index.yaml"
version: 3
include:
  - ../../global/extensions.yaml
  - ../../global/outputs.yaml
  - ../../global/installation_keys.yaml
  - ../../global/hives/dr-general.yaml
  - ../../global/hives/fp.yaml
  - ../../global/hives/query.yaml
  - ../../global/hives/extension_config.yaml
  - hives/dr-general.yaml
```

```yaml title="orgs/<ACME_OID>/hives/dr-general.yaml"
version: 3
hives:
  dr-general:
    acme-bad-domain:
      data:
        detect:
          event: DNS_REQUEST
          op: ends with
          path: event/DOMAIN_NAME
          value: .acme-bad.example
        respond:
          - action: report
            name: acme-bad-domain
      usr_mtd:
        enabled: true
```

Globex, with nothing of its own, includes only the global files:

```yaml title="orgs/<GLOBEX_OID>/index.yaml"
version: 3
include:
  - ../../global/extensions.yaml
  - ../../global/outputs.yaml
  - ../../global/installation_keys.yaml
  - ../../global/hives/dr-general.yaml
  - ../../global/hives/fp.yaml
  - ../../global/hives/query.yaml
  - ../../global/hives/extension_config.yaml
```

The control org gets the same global includes plus its own files. Make `orgs/<CONTROL_OID>/index.yaml` the same as Globex's.

Check three things:

1. **The folder name is the OID**, with no extra characters.
2. **Every included file exists** at that relative path.
3. **Every type in an `index.yaml` has its switch on in `gitsync.yaml`.** The switch is `sync_outputs` for `outputs.yaml`, `sync_extensions` for `extensions.yaml`, `sync_installation_keys` for `installation_keys.yaml` and `sync_hives.<hive>` for a hive file. A file whose type is off is silently skipped.

Commit and push:

```bash
git add global orgs
git commit -m "Global rules and per-org indexes"
git push origin main
```

## Step 8: Pull for the first time, and check it worked

In the web app, press **PULL FROM GIT**. From the CLI:

```bash
limacharlie extension request --name ext-git-sync --action apply --oid "$ACME_OID"
```

A successful request returns without an error. A failed one prints the reason (see [Troubleshooting](#troubleshooting)) and also records an `apply_failed` event on the extension's sensor, so a scheduled pull that fails does not go unnoticed (see [Get alerted when a run fails](#get-alerted-when-a-run-fails) below).

The extension also reports what it did as an `apply` event on its own sensor (or `apply_failed` if it failed). In the web app, **Extensions**, **Git Sync**, then the **ASSOCIATED SENSOR** link at the top of the page, then the Timeline. From the CLI, find the sensor by its tag and list its events:

```bash
SID=$(limacharlie sensor list --selector '"ext:ext-git-sync" in tags' \
  --oid "$ACME_OID" --output json | jq -r '.[0].sid')

limacharlie event list --sid "$SID" --event-type apply --oid "$ACME_OID" \
  --start "$(date -d '1 hour ago' +%s)" --end "$(date +%s)" --output json \
  | jq -c 'sort_by(.routing.event_time) | .[-1].event
           | {changed: [.changed[].name], unchanged: [.unchanged[].name]}'
```

Use `date -v-1H +%s` instead of `date -d '1 hour ago' +%s` on macOS.

The first run lists everything it added under `changed`. Hive records are named `<hive>/<record>`, for example `dr-general/acme-bad-domain`. Outputs, installation keys and extensions appear under their own name. Run the pull again. Nothing changed, so `changed` is empty and `unchanged` lists every record. That is the check you want: Git and the org agree.

Confirm in the org:

```bash
limacharlie dr list --metadata-only --oid "$ACME_OID" --output yaml | grep -E '^(northwind|acme)'
```

Repeat the pull for Globex and the control org.

### Get alerted when a run fails

Nobody is watching a scheduled run, and a repository that stops applying is easy to miss for weeks. Every failed pull or push records an `apply_failed` or `export_failed` event with the `stage` it failed at and the `error` text, so a D&R rule can alert on it. Add this to the control org, or to the shared rules in `global/`:

```yaml
detect:
  target: edr
  events:
    - apply_failed
    - export_failed
  op: is tagged
  tag: ext:ext-git-sync
respond:
  - action: report
    name: git-sync-failed
```

The detection holds the whole event, so `detect/event/stage` and `detect/event/error` say what went wrong. Add an output or a notification action to the rule to be told. The [Git Sync reference](../5-integrations/extensions/limacharlie/git-sync.md#seeing-the-results) lists every `stage`, and how to ignore the failures of an org whose Git Sync is not configured yet.

## Step 9: Turn on schedules

Change `schedule` in `gitsync.yaml` and save it again. Pull every hour on every org:

```bash
sed -i 's/^  schedule: "-"/  schedule: 1h/' gitsync.yaml     # macOS: sed -i ''
for OID in $CONTROL_OID $ACME_OID $GLOBEX_OID; do
  limacharlie extension config-set --name ext-git-sync \
    --input-file gitsync.yaml --oid "$OID"
done
```

In the web app, set **Pull Schedule** and press **SAVE SETTINGS**.

Notes on schedules:

- **Saving the configuration installs or removes the schedule.** The extension keeps a D&R rule in each org's `dr-managed` hive, `ext-git-sync-sync` for pull and `ext-git-sync-export` for push. Setting `-` removes the rule. You can see them with `limacharlie dr list --namespace managed --metadata-only --oid <OID>`.
- **Subscribing alone starts a 12 hour pull.** The extension installs the pull rule at 12 hours when an org subscribes. Saving your first configuration with `schedule: "-"` removes it. Saving a configuration identical to the stored one writes nothing, so it does not touch the schedule rules.
- **The shortest interval is one hour.** For a change that cannot wait, press **PULL FROM GIT**, or run the `apply` request above. A script can run it on every org after a merge.
- **Be careful with scheduled exports.** Every org writes to the same repository, and two exports that overlap can lose the push (`a concurrent push to the same repo can also cause this`). The loser retries on its next run. Schedule export on the control org only, or leave export off and run it by hand when you want a snapshot.

## Step 10: Run changes through pull requests

From now on the repository is the way you change customers.

1. Create a branch and edit files under `global/` or `orgs/`.
2. Open a pull request. Your team reviews the diff, which is the whole change.
3. Merge to `main`.
4. Within the pull interval every org applies it. To apply right away, press **PULL FROM GIT** or run the `apply` request.

Add a check to the pull request, so a typo never reaches `main`. This one needs no LimaCharlie credentials. It fails on a missing include, a wildcard include, a missing `version`, or one of the ignored legacy keys:

```python title="scripts/check_iac.py"
import os
import pathlib
import sys

import yaml

LEGACY = {"rules", "fps", "integrity", "exfil", "artifact", "yara"}
KNOWN = {"version", "include", "hives", "outputs", "resources", "extensions",
         "org-value", "installation_keys"}


def check(path, errors, seen):
    if path in seen:
        return
    seen.add(path)
    if not path.is_file():
        errors.append(f"missing file: {path}")
        return
    doc = yaml.safe_load(path.read_text()) or {}
    if doc.get("version") != 3:
        errors.append(f"{path}: needs 'version: 3'")
    for key in doc:
        if key in LEGACY:
            errors.append(f"{path}: '{key}:' is ignored by Git Sync, use 'hives:'")
        elif key not in KNOWN:
            errors.append(f"{path}: unknown key '{key}'")
    includes = doc.get("include") or []
    if isinstance(includes, str):
        includes = [includes]
    for inc in includes:
        if any(c in inc for c in "*?["):
            errors.append(f"{path}: wildcard include '{inc}' is not supported by Git Sync")
            continue
        check(pathlib.Path(os.path.normpath(path.parent / inc)), errors, seen)


errors = []
indexes = sorted(pathlib.Path("orgs").glob("*/index.yaml"))
if not indexes:
    errors.append("no orgs/<OID>/index.yaml found")
for index in indexes:
    check(index, errors, set())
print("\n".join(errors) or f"ok: {len(indexes)} org(s)")
sys.exit(1 if errors else 0)
```

```yaml title=".github/workflows/check-iac.yml"
name: check-iac
on:
  pull_request:
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install pyyaml
      - run: python scripts/check_iac.py
```

To see what a change would do to an org before you merge, the CLI can dry-run it. From CI that takes an Organization API key for each org. See [Doing it with the CLI](#doing-it-with-the-cli-instead).

## Step 11: Delete things

Git Sync adds and updates. It does not delete, so removing a rule from a file leaves it running in every org. Deleting takes two moves, in this order:

1. **Remove it from Git and merge.** If you delete it from the org first, the next scheduled pull puts it back.
2. **Delete it in the org.** In the web app, or for one record:

   ```bash
   limacharlie dr delete --key northwind-encoded-powershell --confirm --oid "$ACME_OID"
   limacharlie hive delete --hive-name query --key northwind-temp-hunt --confirm --oid "$ACME_OID"
   limacharlie output delete --name northwind-archive-scp --confirm --oid "$ACME_OID"
   ```

To make an org match its files exactly, push with `--force`. It deletes every record of the selected types that is not in the files, including records someone created in the web app. Always run it with `--dry-run` first, name only the types you manage as code (never `--hive-secret`), and give it the same `index.yaml` the extension reads:

```bash
limacharlie sync push --config-file orgs/$ACME_OID/index.yaml \
  --hive-dr-general --hive-fp --hive-query \
  --force --dry-run --oid "$ACME_OID"
```

Each line starts with `=` (already matches), `+` (would be added or updated) or `-` (would be deleted). When the `-` lines are what you want, run it again without `--dry-run`.

Be careful with `--force` on the other types. With `--extensions` it unsubscribes extensions that are not in the files, with `--installation-keys` it deletes keys that are not in the files, and with `--outputs` it deletes outputs that are not in the files.

## Step 12: Onboard the next customer

Initech signs. A script creates the org, gives it the key and the Git Sync configuration, and opens the pull request that gives it an `index.yaml`. Run it from a clone of the repository on `main`, with `gitsync.yaml` from Step 5 beside it and `GLOBEX_OID` set.

```bash
#!/usr/bin/env bash
set -euo pipefail

NAME="$1"                       # for example: northwind-initech
KEY=~/.ssh/gitsync/id_ed25519

limacharlie org create --name "$NAME" --location usa >/dev/null
OID=$(limacharlie org list --output json | jq -r --arg n "$NAME" '.[] | select(.name == $n) | .oid')
[ "$(printf %s "$OID" | grep -c .)" -eq 1 ] || { echo "expected exactly one org named $NAME" >&2; exit 1; }
echo "created $NAME: $OID"

# Key, extension, configuration (Steps 4 and 5)
jq -Rs '{secret: .}' "$KEY" | limacharlie secret set --key gitsync-deploy-key --enabled --oid "$OID"
limacharlie extension subscribe --name ext-infrastructure --oid "$OID"
limacharlie extension subscribe --name ext-git-sync --oid "$OID"
limacharlie extension config-set --name ext-git-sync --input-file gitsync.yaml --oid "$OID"

# The org's folder: the same global includes as everyone (Step 7)
git switch -c "onboard-$NAME"
mkdir -p "orgs/$OID"
cp "orgs/$GLOBEX_OID/index.yaml" "orgs/$OID/index.yaml"
git add "orgs/$OID" && git commit -m "Onboard $NAME"
git push -u origin HEAD
gh pr create --fill

echo "Merge the pull request, then run:"
echo "  limacharlie extension request --name ext-git-sync --action apply --oid $OID"
```

Until the pull request is merged, a pull fails with `organization not found in the repository`, so merge first. Create any secrets the global files refer to (such as `northwind-scp-password`) in the new org before the first pull.

## Troubleshooting

An error from a pull or push shows in the web app as a toast, and on the CLI as the request's error text. It is also recorded as an `apply_failed` or `export_failed` event on the extension's sensor, which is how you find out about a failed scheduled run: see [Get alerted when a run fails](#get-alerted-when-a-run-fails).

| Error text | Cause and fix |
| --- | --- |
| `organization not found in the repository: no orgs/<OID>/index.yaml on branch <branch>` | The branch has no `orgs/<OID>/index.yaml` for this org. Check the OID in the folder name and that the file is on the configured branch. |
| `failed to apply configuration: file not found: <path>` | An `include:` path does not exist, or it is a wildcard. Paths are relative to the including file. List every file. |
| `failed to apply configuration: yaml: ...` | A YAML syntax error in an included file. |
| `invalid version found (<file>): 0` | The file has no `version: 3`. |
| `Git Sync is not configured for this organization, or its configuration is disabled` | There is no `ext-git-sync` configuration record, or it is disabled. Save it with `usr_mtd: {enabled: true}`. |
| `ssh key is required` | The configuration is enabled but has no `ssh_key`. |
| `failed using secret ssh_key: ... RECORD_NOT_FOUND` | The secret named in `ssh_key` does not exist in this org. |
| `ssh: no key found` | `ssh_key` is a literal that is not a private key. Use `hive://secret/<name>`. |
| `failed to clone repo: repository not found` | The URL is wrong, or the deploy key is not on that repository. |
| `couldn't find remote ref "refs/heads/<branch>"` | The branch does not exist. |
| `failed to push (...): ... protected branch hook declined` | The branch is protected. See Step 6. |
| `failed to push (...): ... marked as read only` | The deploy key was added without write access. |
| `sync_hives: ... requires <permission>` | The extension was subscribed before it needed that permission. Run `limacharlie extension rekey --name ext-git-sync --oid <OID>` and retry. |
| The pull succeeds but nothing changes | The type's switch is off, or the file is not in the `index.yaml`. Compare Step 7's three checks. |
| A removed rule is still in the org | Pull never deletes. See Step 11. |

## Doing it with the CLI instead

You can skip Git Sync and push from your own machine or from CI. The `limacharlie sync` commands read the same files and call the [Infrastructure extension](../5-integrations/extensions/limacharlie/infrastructure.md). They suit CI that pushes on merge, one-off imports and dry runs.

```bash
# Org to files (one file; split it up by hand)
limacharlie sync pull --config-file org.yaml --oid "$ACME_OID" \
  --outputs --extensions --installation-keys \
  --hive-dr-general --hive-fp --hive-query --hive-extension-config

# Files to org, dry run first
limacharlie sync push --config-file orgs/$ACME_OID/index.yaml --oid "$ACME_OID" \
  --outputs --extensions --installation-keys \
  --hive-dr-general --hive-fp --hive-query --hive-extension-config --dry-run
```

To keep the files readable by Git Sync, name the types with `--hive-*` flags. Avoid `--all`, which includes the `secret` and `acl` hives, and the legacy `--integrity`, `--exfil`, `--artifact` and `--yara` flags, which write the top-level sections Git Sync ignores. Use `--hive-extension-config` and `--hive-yara` instead.

The CLI differs from Git Sync in two ways. It expands wildcards in `include:`, and when two files define the same record it picks one of them in no fixed order. Keep record names unique and do not use wildcards, and the two tools give the same result.

An Organization API key works on one org only, so CI needs a key per org. See [API keys](../7-administration/access/api-keys.md).

## What you have now

- A private repository that is the source of truth for every customer.
- Shared rules written once in `global/`, and per-customer rules in `orgs/<OID>/`.
- Scheduled pulls, one-click pulls, and a pull request check.
- A script that onboards a customer.

Next, add [Cases](../5-integrations/extensions/limacharlie/cases.md), more detections and AI agents to `global/`, as described in the [MSSP walkthrough](mssp-walkthrough.md). For every option, see the [Git Sync reference](../5-integrations/extensions/limacharlie/git-sync.md).
