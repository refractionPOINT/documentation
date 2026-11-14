# Git Sync

The Git Sync extension keeps an organization's configuration in a Git repository. It can **pull** a repository into an organization (apply the configuration in Git) and **push** an organization into a repository (export what the organization has now). Either can run on a schedule or on demand.

One repository can serve many organizations, and organizations can share files. That makes it the natural way to run an MSSP: write a detection rule once in the repository, and every customer gets it.

For a step-by-step walkthrough, follow the [MSSP Git Sync tutorial](../../../1-getting-started/mssp-iac-tutorial.md). This page is the reference.

**What Git Sync does:**

- **Recurring pull.** Applies the repository to the organization every hour, 3, 6, 12 or 24 hours, or every week.
- **Recurring push.** Exports the organization to the repository on the same set of intervals.
- **On-demand pull and push.** Buttons in the web app, or an extension request from the CLI or API.
- **Shared configuration.** One repository holds a configuration per organization, and the organizations can include common files.
- **Operation log.** Each successful operation is recorded as an event on the extension's sensor.

Git Sync lists the [Infrastructure](infrastructure.md) extension as a requirement, so subscribe to both.

## Pull and push

### Pull: Git to the organization

The repository holds a file for each organization. A pull reads it and creates or updates the matching records in the organization.

![d2 (1).png "pull config(1).png"](../../../assets/images/d2-(1).png "pull_config(1).png")

!!! warning "A pull never deletes"
    Pull adds new records and updates existing ones. It does not remove a record that is no longer in Git. If you delete a rule from the repository, the rule keeps running in the organization until you delete it there. See [Removing things](#removing-things).

### Push: the organization to Git

A push writes the organization's current configuration to the repository, under `exports/`. Use it to bootstrap a repository from an organization you configured by hand, and to record changes someone made in the web app.

![d2 (2).png "push config(1).png"](../../../assets/images/d2-(2).png "push_config(1).png")

A push:

- writes to `exports/orgs/<OID>/` and never touches `orgs/`, so it cannot overwrite what you pull from;
- replaces the whole `exports/orgs/<OID>/` folder each time, so records you deleted in the organization disappear from Git;
- makes no commit when nothing changed, and otherwise commits as `LC Git Sync` directly to the configured branch;
- works on an empty repository.

If the branch requires pull requests, a push is rejected (`protected branch hook declined`). Either allow the deploy key to bypass the rule, or leave push off.

## What is synced

Git Sync handles these types:

| Type | In the configuration file | Switch |
| --- | --- | --- |
| Outputs | `outputs:` | `sync_outputs`, `export_outputs` |
| Resources | `resources:` | `sync_resources`, `export_resources` |
| Extension subscriptions | `extensions:` | `sync_extensions`, `export_extensions` |
| Organization values | `org-value:` | `sync_org_values`, `export_org_values` |
| Installation keys | `installation_keys:` | `sync_installation_keys`, `export_installation_keys` |
| Hive records | `hives: <hive>:` | `sync_hives.<hive>`, `export_hives.<hive>` |

Detection rules, false-positive rules, lookups, saved queries, YARA rules, AI agents and the settings of extensions such as Exfil, Integrity and Artifact are all hive records: `dr-general`, `fp`, `lookup`, `query`, `yara`, `ai_agent` and `extension_config` (one record per extension, named after it, for example `ext-exfil`). The hives you can enable are listed by `limacharlie extension schema --name ext-git-sync`.

The older top-level sections `rules`, `fps`, `integrity`, `exfil`, `artifact` and `yara` that the `limacharlie sync` command can write are **ignored** by Git Sync, without an error. Write them as `hives:` records.

A few types need care:

- **`secret` hive.** Offered under *Sensitive Data Options*. Enabling it exports secret values to Git and lets Git overwrite them. Leave it off, and refer to secrets as `hive://secret/<name>`.
- **`acl` hive.** Refused. Resource ACL membership stays out of Git.
- **`dr-managed` hive.** Extensions own these rules, including Git Sync's own schedule rules.
- **Installation keys.** The name of each key in the file is its description in the organization, and how a later pull finds it again.
- **Outputs and organization values.** An export writes them as stored. A credential typed into an output, or an API key stored as an organization value, is written to the repository in clear text. Use `hive://secret/<name>` references in outputs and leave `export_org_values` off.
- **`resources` export.** The list comes out in a different order each time, so every export produces a commit.

## Repository structure

A pull needs this file for each organization:

```text
orgs/<OID>/index.yaml
```

`<OID>` is the organization's ID. If the file is missing at the head of the configured branch, the pull fails with `organization not found in the repository`.

`index.yaml` lists the other files that make up the configuration:

```yaml
version: 3
include:
  - extensions.yaml
  - outputs.yaml
  - hives/dr-general.yaml
  - hives/fp.yaml
```

- `include:` paths are relative to the file that contains them, and included files can include others.
- List every file. Wildcards (`hives/*.yaml`) are not expanded by Git Sync. The `limacharlie sync` command does expand them, so a repository that works with the CLI can fail here.
- Every file starts with `version: 3`.
- When two files define the same record, the file included later wins, and an included file wins over the file that includes it.
- A type is applied only when its switch in the Git Sync configuration is on **and** an included file holds it. A file for a type whose switch is off is skipped silently.

A hive file looks like this. Put `enabled: true` in each record's `usr_mtd`, or the record is created disabled:

```yaml
version: 3
hives:
  dr-general:
    suspicious-encoded-powershell:
      data:
        detect:
          event: NEW_PROCESS
          op: contains
          path: event/COMMAND_LINE
          value: -EncodedCommand
        respond:
          - action: report
            name: suspicious-encoded-powershell
      usr_mtd:
        enabled: true
```

### One organization, all files local

When everything belongs to one organization, keep it in the organization's folder:

```text
.
└── orgs
    └── a326700d-3cd7-49d1-ad08-20b396d8549d
        ├── extensions.yaml
        ├── hives
        │   ├── cloud_sensor.yaml
        │   ├── dr-general.yaml
        │   ├── extension_config.yaml
        │   ├── fp.yaml
        │   ├── lookup.yaml
        │   ├── query.yaml
        │   └── yara.yaml
        ├── index.yaml
        ├── installation_keys.yaml
        ├── org_values.yaml
        ├── outputs.yaml
        └── resources.yaml
```

```yaml
version: 3
include:
  - extensions.yaml
  - outputs.yaml
  - resources.yaml
  - org_values.yaml
  - installation_keys.yaml
  - hives/cloud_sensor.yaml
  - hives/dr-general.yaml
  - hives/extension_config.yaml
  - hives/fp.yaml
  - hives/lookup.yaml
  - hives/query.yaml
  - hives/yara.yaml
```

### Sharing configuration across organizations

Put what is common in a shared folder, and have each organization include it:

```text
.
├── global
│   └── hives
│       ├── dr-general.yaml
│       └── yara.yaml
└── orgs
    ├── 7e41e07b-c44c-43a3-b78d-41f34204789d
    │   └── index.yaml
    ├── a326700d-3cd7-49d1-ad08-20b396d8549d
    │   └── index.yaml
    └── cb639126-e0bc-4563-a577-2e559c0610b2
        └── index.yaml
```

```yaml
version: 3
include:
  - ../../global/hives/yara.yaml
  - ../../global/hives/dr-general.yaml
```

Add an organization's own files after the shared ones, and list them in that organization's `index.yaml` only.

### Export layout

```text
.
└── exports
    └── orgs
        └── a326700d-3cd7-49d1-ad08-20b396d8549d
            ├── extensions.yaml
            ├── hives
            │   ├── dr-general.yaml
            │   ├── extension_config.yaml
            │   ├── fp.yaml
            │   └── query.yaml
            ├── index.yaml
            ├── installation_keys.yaml
            ├── org_values.yaml
            ├── outputs.yaml
            └── resources.yaml
```

Only the types whose export switch is on get a file, plus an `index.yaml` that includes them. To manage an organization from Git, copy what you want from `exports/` into `orgs/<OID>/` or a shared folder. A pull never reads `exports/`.

## Configuration

The configuration is stored in each organization, in the `extension_config` hive under the key `ext-git-sync`. Edit it in the web app (**Extensions** in the sidebar, then **Git Sync**), or with the CLI:

```bash
limacharlie extension config-set --name ext-git-sync --input-file gitsync.yaml --oid <OID>
limacharlie extension config-get --name ext-git-sync --oid <OID>
```

```yaml title="gitsync.yaml"
data:
  repo_url: git@github.com:example/iac.git
  branch: main
  user_name: git
  ssh_key: hive://secret/gitsync-deploy-key
  schedule: 6h
  schedule_export: "-"
  sync_outputs: true
  sync_extensions: true
  sync_hives:
    dr-general: true
    fp: true
usr_mtd:
  enabled: true
```

The record must be enabled (`usr_mtd: {enabled: true}`). A disabled record is ignored and requests fail with `ssh key is required`. The web app enables it for you.

| Field | Web app label | Description |
| --- | --- | --- |
| `repo_url` | Repository URL | SSH URL of the repository, such as `git@github.com:example/iac.git`. |
| `branch` | Branch | Branch to pull from and push to. Defaults to `main` if empty. The web app requires a value. |
| `user_name` | User Name | SSH user. `git` on GitHub, GitLab and Bitbucket. |
| `ssh_key` | SSH Key | Private key. Use `hive://secret/<name>`. |
| `schedule` | Pull Schedule | How often to pull. |
| `schedule_export` | Push Schedule | How often to push. |
| `sync_outputs`, `sync_resources`, `sync_extensions`, `sync_org_values`, `sync_installation_keys` | Pull checkboxes | Types a pull applies. |
| `sync_hives.<hive>` | Pull checkboxes | Hives a pull applies. |
| `export_outputs`, `export_resources`, `export_extensions`, `export_org_values`, `export_installation_keys` | Push checkboxes | Types a push writes. |
| `export_hives.<hive>` | Push checkboxes | Hives a push writes. |

`repo_url`, `ssh_key` and `user_name` accept a `hive://secret/<name>` reference. Every switch defaults to off, so nothing syncs until you turn it on.

### Schedules

`schedule` and `schedule_export` take one of `-` (off), `1h`, `3h`, `6h`, `12h`, `24h` or `168h`. Nothing shorter is available. For a change that cannot wait, run a pull by hand.

Saving the configuration installs or removes the schedule. Git Sync keeps two D&R rules in the organization's `dr-managed` hive: `ext-git-sync-sync` for pull and `ext-git-sync-export` for push. A schedule of `-` removes the rule. Saving a configuration identical to the stored one writes nothing and leaves the rules as they are.

Subscribing to the extension installs the pull rule at 12 hours, before any configuration exists. Saving a configuration with `schedule: "-"` removes it.

Several organizations pushing to one repository at the same moment can lose the race for the branch (`may be a concurrent push to the same repo`). The loser tries again on its next run. Prefer scheduling push on one organization, or none.

## Running a pull or push by hand

In the web app, open **Extensions**, then **Git Sync**. **PULL FROM GIT** runs a pull and **PUSH TO GIT** runs a push. They use the saved configuration.

From the CLI or the API, send the extension request `apply` (pull) or `export` (push):

```bash
limacharlie extension request --name ext-git-sync --action apply --oid <OID>
limacharlie extension request --name ext-git-sync --action export --oid <OID>
```

Neither takes parameters.

## Seeing the results

A failed operation returns its reason to the caller: a toast in the web app, or the error text from the CLI. A successful one adds an event to the extension's sensor, the sensor tagged `ext:ext-git-sync`. In the web app it is the **ASSOCIATED SENSOR** link on the Git Sync page. From the CLI:

```bash
SID=$(limacharlie sensor list --selector '"ext:ext-git-sync" in tags' --oid <OID> --output json | jq -r '.[0].sid')
limacharlie event list --sid "$SID" --event-type apply --oid <OID> \
  --start "$(date -d '1 hour ago' +%s)" --end "$(date +%s)" --output json
```

An `apply` event has two lists. `changed` holds the records that were added or updated, and `unchanged` the ones that already matched. Hive records are named `<hive>/<record>`. An `export` event records the options used.

## Removing things

Because a pull only adds and updates, remove something in two steps. First remove it from the repository and merge, so the next pull does not put it back. Then delete it in the organization, in the web app or with the CLI:

```bash
limacharlie dr delete --key <rule> --confirm --oid <OID>
limacharlie hive delete --hive-name <hive> --key <record> --confirm --oid <OID>
limacharlie output delete --name <output> --confirm --oid <OID>
```

To make an organization match its files exactly, run `limacharlie sync push --force` with the same `index.yaml` and the same types. Force deletes every record of those types that is not in the files, including records created in the web app, so run it with `--dry-run` first. See [the tutorial](../../../1-getting-started/mssp-iac-tutorial.md#step-11-delete-things).

## Setting up Git Sync

The [tutorial](../../../1-getting-started/mssp-iac-tutorial.md) does this for a whole MSSP. For a single organization:

1. **Create a private repository** on any Git host that serves SSH and supports deploy keys.
2. **Create an SSH key** used only for Git Sync:

    ```bash
    mkdir -p ~/.ssh/gitsync && chmod 700 ~/.ssh/gitsync
    ssh-keygen -t ed25519 -N "" -C "limacharlie-gitsync" -f ~/.ssh/gitsync/id_ed25519
    ```

3. **Add the public key to the repository as a deploy key.** On GitHub: **Settings**, **Deploy keys**, **Add deploy key**. Check **Allow write access** if you will push. A read-only key is enough for pull only. Use one key per repository.
4. **Store the private key as a secret.** In the web app, **Organization Settings**, **Secrets Manager**. Or:

    ```bash
    jq -Rs '{secret: .}' ~/.ssh/gitsync/id_ed25519 \
      | limacharlie secret set --key gitsync-deploy-key --enabled --oid <OID>
    ```

5. **Subscribe** to Git Sync from the [Marketplace](https://app.limacharlie.io/add-ons/extension-detail/ext-git-sync), or with the CLI. Git Sync requires Infrastructure, so subscribe to both:

    ```bash
    limacharlie extension subscribe --name ext-infrastructure --oid <OID>
    limacharlie extension subscribe --name ext-git-sync --oid <OID>
    ```

6. **Configure it.** Open **Extensions**, then **Git Sync**. Set the Repository URL, Branch, User Name (`git`) and SSH Key (pick the secret), tick the types to push and pull, choose schedules if you want them, and press **SAVE SETTINGS**. Or use `config-set` as shown above.
7. **Check for literal credentials before the first push.** A push writes outputs and extension settings as stored. Follow the audit in [Step 6 of the tutorial](../../../1-getting-started/mssp-iac-tutorial.md#step-6-export-once-to-bootstrap-the-repository), or leave outputs and `extension_config` off until you have checked them.
8. **Try it.** Press **PUSH TO GIT** and check that `exports/orgs/<OID>/` appears in the repository.

## Troubleshooting

| Error text | Cause |
| --- | --- |
| `organization not found in the repository` | No `orgs/<OID>/index.yaml` on the configured branch. |
| `file not found: <path>` | An `include:` path does not exist, or it is a wildcard. |
| `invalid version found` | An included file has no `version: 3`. |
| `ssh key is required` | The configuration record is disabled or has no `ssh_key`. |
| `failed using secret ssh_key ... RECORD_NOT_FOUND` | The secret named in `ssh_key` does not exist in the organization. |
| `ssh: no key found` | `ssh_key` holds a literal value that is not a private key. |
| `failed to clone repo: repository not found` | Wrong URL, or the deploy key is not on that repository. |
| `couldn't find remote ref "refs/heads/<branch>"` | The branch does not exist. |
| `protected branch hook declined` | A push to a branch that requires pull requests. |
| `requires <permission>` | The extension was subscribed before it needed that permission. Run `limacharlie extension rekey --name ext-git-sync --oid <OID>`. |

The tutorial's [troubleshooting section](../../../1-getting-started/mssp-iac-tutorial.md#troubleshooting) explains each one.

[Infrastructure](infrastructure.md)
