# Deception: Configuration

Everything you can change lives in one record: the `ext-deception` record in the `extension_config` [Config Hive](../../../../7-administration/config-hive/index.md). It is a normal hive record, so you can read it, edit it, version it and sync it with Git Sync or your infrastructure-as-code like any other extension configuration. See [Using Extensions](../../using-extensions.md).

Everything that decides what alerts is in this record: policies, templates, observe mode, approved readers and declared tokens. The extension keeps no learned state that changes what alerts. Only the generated decoy instances and their secrets are kept out of the record. They live in the extension's own store, and no request returns a secret value of a decoy placed on a host.

```bash
limacharlie deception config get --output yaml --oid "$OID" > ext-deception.yaml
limacharlie deception config set --input-file ext-deception.yaml --oid "$OID"
```

`config get` prints the whole record: the configuration under `data`, its metadata and its etag. Edit `data` and give the file back to `config set`: the etag makes the save a compare-and-set, refused without overwriting anything if someone saved the record since you read it. `config set` also takes a file holding only the configuration (`schema_version`, `policies`, `templates`, ...). These commands are in the LimaCharlie CLI from version 5.14.0; with an older CLI, use `limacharlie extension config-get --name ext-deception` and `limacharlie extension config-set --name ext-deception --input-file <file>`.

You can also edit the record in the web app: the **Policies** tab edits policies (a policy's mode and observe end are in the policy editor), the **Templates** tab edits templates and copies them from the Template library, and the **Settings** tab edits the reader allowlists, link previews and the isolation cap, and copies the whole record as YAML with the CLI lines that apply it. A save from the web app keeps every field the page does not show (`schema_version`, `key_sources`, `drops`, `custom_domains`, and any field a newer release adds). Tokens made in the **Tokens** tab are not part of the record; tokens you declare under `drops` are. The extension validates a save the same way, and a save that conflicts with a newer version is refused without overwriting it.

## Enabling the configuration record

The extension reads your configuration from the record named `ext-deception`. The platform gives an extension an empty configuration when that record is disabled.

- `limacharlie deception config set` creates a new record enabled (`--disabled` creates it disabled). With a file holding only the configuration, an existing record keeps its metadata. With a whole record (a top-level `data` key, as `config get` prints it), its `usr_mtd` replaces the stored metadata. `--enabled` and `--disabled` win over both.
- `limacharlie extension config-set`, and the generic `hive set`, create a new record disabled unless its `usr_mtd.enabled` says otherwise; an existing record keeps its metadata when the file has no `usr_mtd`.

Enable a disabled record once:

```bash
limacharlie deception config enable --oid "$OID"
# or, with any CLI version:
limacharlie hive enable --hive-name extension_config --key ext-deception --oid "$OID"
```

Or enable it in the same `config-set`, by putting the record under a top-level `data` key and `usr_mtd` beside it:

```yaml
data:
  schema_version: 1
  templates: []
  policies: []
usr_mtd:
  enabled: true
```

The CLI treats a file with a top-level `data` key as a whole hive record, `usr_mtd` included. A file without it is stored as the record's data, and a `usr_mtd` key in it fails validation like any other unknown field.

While the record is disabled:

- `plan`, `deploy`, `verify`, `rotate`, `remove`, `test_fire`, `list_test_paths`, `coverage` and the token requests (and `list` or `list_hosts` with a `policy` filter) refuse with "the ext-deception configuration is disabled" (the full list is in [Requests](requests.md)).
- Hits on decoys already planted are still judged and alerted.
- The daily run and a configuration update leave the candidate rules derived from your templates and the entries in other extensions' configurations as they are and retire no decoy (the base plumbing rules and any missing shipped detection rules are still repaired), and the daily response says why until the record is enabled. A disabled or unreadable record is never read as "you removed everything".
- `respond` refuses to isolate, because your isolation cap is unknown. Tagging still works.

The extension never writes this record, so it never enables it for you. The web app shows a banner with **Enable configuration** to anyone who can read and write the record (`ext.conf.get` and `ext.conf.set`).

## Validation

The extension validates the whole record when it is saved, including each template's `spec`, and rejects it with errors that name the field (for example `templates[3].spec.file_name: required`). Unknown fields are rejected too.

A record can still reach the extension without that check (written while the extension was down, or written for a newer format than the running extension supports). On read, the extension skips individual policy and template records it cannot use (for example one written for a newer record or kind version) and reports each, with the field and the reason, in the `warnings` of `plan` and in `coverage`. The top-level record is different: if its own `schema_version` is newer than the running extension supports, the whole record is refused and requests that read the configuration fail with an error (`respond` also refuses to isolate) until you rewrite the record or the extension is upgraded. A skipped record's already-placed decoys stay as they are. The extension never removes what it does not understand, and never rewrites your records.

A record that cannot be saved is refused with the code `invalid_config` at the end of its message (see [Errors and refusal codes](requests.md#errors-and-refusal-codes)).

Limits: 100 policies, 300 templates, 20 custom domains, 200 reader allowlist entries per list (at most 8 of them Lookup references), 10,000 `drops` entries, 50 `drop_preview_match` entries. The record is capped at 1 MB by the hive. Names are lowercase letters, digits, `.`, `_` and `-`, 1 to 64 characters, starting with a letter or digit. Template tags follow the same pattern, up to 32 characters, at most 16 per template.

## Top-level fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Version of the record format. Currently `1`. Required. A newer value than the extension supports makes requests fail (see [Validation](#validation)). |
| `policies` | Which templates go on which sensors, and what to do on a hit. |
| `templates` | The decoys you use. |
| `custom_domains` | Bring-your-own decoy domains. See [Custom domains](#custom-domains). |
| `reader_allowlist` | Approved readers of decoys, applied to every policy. See [Reader allowlist](#reader-allowlist). |
| `isolation_cap_per_hour` | Most automatic isolations per hour for the organization. `0` or absent means the default, **5**. Maximum 1000. `plan` reports the cap in effect as `isolation_cap` (`per_hour`, and `source`: `config` or `default`). |
| `drops` | Tokens declared as code. See [Declare tokens in the configuration](drops.md#declare-tokens-in-the-configuration). |
| `drop_preview_match` | What fetches your tokens with no person behind it (a mail gateway, a chat unfurler). See [Link previews](drops.md#link-previews-and-mail-scanners). |
| `key_sources` | Reserved for real AWS decoy keys. Must be empty. See [AWS key sources](#aws-key-sources). |

## Policies

A policy decides which sensors get which templates.

```yaml
policies:
  - schema_version: 1
    name: linux-servers
    enabled: true
    targeting:
      tags: [prod]            # all must be present
      platforms: [linux]      # any of: windows, linux, macos
      sids: []                # explicit sensors, at most 500
    templates:
      select_tags: [credentials]   # every template in this record with one of these tags
      names: [mcp-config-ops]      # plus these, by name
    responses:
      isolate: true
      start_ai: false
    setup_on_new_sensors: true
    mode: observe                         # live (default) or observe
    observe_until: "2026-12-15T00:00:00Z" # optional: live again from then on
    dc_logon_collection: false
    reader_allowlist: []
```

| Field | Meaning |
| --- | --- |
| `name` | Unique. Required. |
| `enabled` | A disabled policy plants nothing and supplies nothing to a hit: no allowlist, no mode and no automatic response. The daily run retires its decoys unless another enabled policy still selects their templates. Until then, a hit on one of them is judged live and only the organization-wide `reader_allowlist` approves its reader, but the rules that forward a template's on-host events (reads, modifications, deletions, command lines) are removed at the next configuration update once no enabled policy selects it, so only use hits still reach those decoys: through the collector, and DNS lookups of a hostname decoy reported by your sensors. A failed sign-in under a phantom account still reaches it only while another enabled policy selects a template that needs the same sign-in source. |
| `targeting` | `tags`, `platforms` and `sids` combine. At least one must be set: an empty targeting would match every sensor and is rejected. |
| `templates` | `select_tags` and `names`; at least one required. Only templates in this same record are selectable. The default library is outside it. |
| `responses.isolate` | Lets the default `deception-respond` rule isolate the host when the evidence is an event the decoy's own sensor reported. Default `false`. See [Isolation](detections.md#isolation). |
| `responses.start_ai`, `responses.ai_sop` | Recorded, but starting an AI triage session from the extension is **not built**: `respond` with `ai_triage` answers that it is not available. To launch an AI agent, add a `start ai agent` response to your own detection rule. `ai_sop` is accepted only together with `start_ai`. |
| `setup_on_new_sensors` | Place decoys when a matching sensor first connects. |
| `dc_logon_collection` | Reserved for the AD-form phantom accounts, which are **not available in this release**. The field is accepted and **ignored**: nothing is tagged on your domain controllers and no Windows event collection is installed because of it, and `plan` and `deploy` warn about it for each policy that sets it. Leave it `false`. |
| `mode` | `live` (default) or `observe`. See [Observe mode](#observe-mode). Any other value skips the policy with a problem on its `mode` field. |
| `observe_until` | An RFC 3339 time, with `mode: observe` only: from then on the policy is live, judged by the time the extension processes the event. Unset: observe until you set `mode: live`. |
| `reader_allowlist` | Approved readers for this policy's decoys, in addition to the organization-wide list. |

A policy that names a template that does not exist, or a tag no template carries, is rejected when you save the record. If such a record is already stored, the policy stays usable for the rest of its selection and `plan` reports a warning.

Policies that match the same sensor and select the same template share its placements. A decoy is keyed by sensor and template, so the policy that places it owns it and supplies its response settings, and another policy that selects the same template adds nothing on that sensor while the decoy exists. When one planning pass covers several policies (a `deploy` or the daily run without a `policy`), the first matching policy in the order the policies are stored in the record is the one that places it. A `deploy` with a `policy` still plans every enabled policy in that order; only a `deploy` with both `policy` and `sid` plans that one policy on that sensor. A decoy that already exists keeps its owner: a `deploy` with a later policy and a `sid` that runs first makes that policy the owner on that sensor, and a decoy is not handed to another policy if its owner is removed while another policy keeps the decoy alive, so a hit on it finds no policy and the `policy` response does nothing. A decoy is retired when no enabled policy selects its template any more, not when one of several policies that select it is removed. A sensor that stops matching a policy's targeting (for example it loses a targeting tag) does not retire its decoys either, and they stay fully watched: the read, modify and delete rules reach a sensor through a tag the extension manages for each template it holds (see [Per-host watch rules](decoys.md#per-host-watch-rules)), not through your targeting tags. Remove such decoys with `remove` and `sid` if you no longer want them there.

### Which policy's settings apply to a hit

A hit follows the policy that placed its decoy, by name, and nothing else:

- That policy's `reader_allowlist` and `mode` apply, plus the organization-wide `reader_allowlist`. Another policy that also selects the template, or also targets the host, lends the hit nothing: its allowlist does not approve the read and its mode does not change it.
- A disabled policy, or one no longer in the record, contributes no allowlist, no mode (its decoys are live) and no automatic response.
- So, in infrastructure as code: to approve a reader for every decoy whatever placed it, put it in the organization-wide list. To observe a rollout, set `mode: observe` on the policy that places those decoys.

## Templates

A template is one concrete decoy.

```yaml
templates:
  - schema_version: 1
    kind: file
    kind_version: 1
    name: kubeconfig-backup
    tags: [credentials, kubernetes, linux, macos]
    description: Old kubeconfig for a "prod" cluster, left next to the real one. The server is a fake Kubernetes API on the hit collector.
    enabled: true
    spec:
      platforms: [linux, macos]
      requires_packages: [kubectl, kubernetes-client, kubernetes-cli]
      requires_files: [kubectl]
      file_name: '{{vocab "kubeconfig_backup"}}'
      directories:
        default: ["~/.kube"]
        linux-server: ["/root/.kube"]
      alerts: [read, use]
      secrets:
        - {name: token, type: bearer_token, style: jwt}
      content: |
        apiVersion: v1
        kind: Config
        clusters:
        - cluster:
            server: https://{{collector "k8s_api"}}
          name: {{vocab "k8s_cluster"}}
        contexts:
        - context:
            cluster: {{vocab "k8s_cluster"}}
            user: {{vocab "k8s_user"}}
          name: {{vocab "k8s_cluster"}}-{{vocab "k8s_user"}}
        current-context: {{vocab "k8s_cluster"}}-{{vocab "k8s_user"}}
        users:
        - name: {{vocab "k8s_user"}}
          user:
            token: {{secret "token"}}
```

This is the complete `kubeconfig-backup` library template. Every name written in the file (cluster, user) is a `{{vocab "..."}}` entry, generated once per organization, so the file reads differently in every organization.

`schema_version` on a template or policy is the version of the record format. `kind_version` is the version of that kind's `spec` schema. They change independently. A newer version on a template or policy than the extension knows causes that record to be skipped with a warning, not guessed at. Run `list_kinds` for each kind's schema.

### `file` spec

| Field | Meaning |
| --- | --- |
| `platforms` | `windows`, `linux`, `macos`. At least one. |
| `requires_packages`, `requires_files` | Plant only where one of the named packages is installed or one of the named binaries is found. Empty means every host. |
| `file_name` | A generated name (`{{vocab "key"}}`) or, for Windows only, a fixed name under a generated folder. |
| `directories` | Keyed by `default`, `windows`, `linux`, `macos`, `linux-server`. `~` is the user's home. Never a tool's default path. A folder with a fixed name must already exist on the host. A folder with a generated name (taken from a vocabulary entry) is created by the extension and removed again with its last decoy; the extension never creates a tool's default folder such as `~/.aws`. See [File names and paths](decoys.md#file-names-and-paths). |
| `alerts` | `read`, `use`, or both. `use` needs at least one secret in the file. |
| `secrets` | Up to 12. Each has a `name`, a `type` (`bearer_token`, `url_token`, `aws_access_key`, `password`, `username`) and for tokens an optional `style` (`jwt`, `hex40`, `hex32`, `b62_40`, `vault`, `npm`, `git_pat`). Every secret must be used in `content`. |
| `content` | A restricted Go template, up to the extension's size limit. Functions: `secret`, `aws_secret`, `collector`, `vocab`, `home`, `user`, `hostname`, `domain`, `guid`, `timestamp`, plus escapers `xml`, `json`, `csv`, `ini`. |
| `mode` | POSIX mode as four digits, default `0600`. |
| `mtime_days_min`, `mtime_days_max` | Backdate the file so it looks like a leftover. Default 30 to 400 days. |
| `max_users` | User homes per host, 1 to 3, default 1. |
| `line_endings` | `lf` (default) or `crlf`. |
| `windows_attributes` | Windows only: `folder` and `file`, each a list of `hidden` and `system`, the attributes to set. Folder attributes apply only to folders the extension created. `readonly` is refused: the extension could no longer test or remove the decoy. |

Content must not mention `limacharlie`. A template is checked by rendering it once at write time. Write your own templates the same way as the library ones: take every name you put in or on a file from `{{vocab "..."}}` rather than typing a fixed word, because a fixed word is the same in every organization that copies it.

The `hostname` kind adds `form` (`registry` or `internal`), `hosts` and `zone` (`resolved`, the default, or `unresolved`: names that answer "does not exist", used by `win-desktop-ini-folder` so that Windows stops at the lookup and never connects), and holds a `file` spec for the file that names the hosts. The `document` kind takes the `file` placement fields (`platforms`, `file_name`, `directories`, `alerts`, `mode`, `mtime_days_*`, `max_users`) and, instead of `content`, a `document` block: `format` (`docx` or `svg` in this release), `title`, `lines` (1 to 20) and optionally `author` and `company`. Each of those is a template limited to `vocab`, `user`, `hostname`, `guid` and `timestamp` (not `domain`, `collector` or `home`). `alerts` must include `use` (`[use]` or `[read, use]`), because a document always carries its beacon. The file name must end in the format's extension. Its `use` layer is the document being opened (see [Documents](drops.md#documents) for which viewers fire). The `phantom_account` kind adds `form` (`upn` or `ad`), `source` (`any`, `entra`, `okta`, UPN form only), `upn_domain`, `ad_domain` and a `file` spec; its content uses `{{account}}` and `{{password}}`. Copy these from the default library, or read the schema from `list_kinds`. The library is built into the extension and ships with each release. A template you copy from it is stored in your configuration and is yours to edit: a later release does not change your copy, and the library itself is never changed. In the web app, **Templates** > **Add from library** copies templates for you, and the template viewer and editor edit your own templates as a form or as JSON. Library templates are read-only in the editor: customize a copy.

The `internal` hostname form and the `ad` phantom-account form are **not available in this release**. They still validate, so an existing configuration keeps loading, but every alert layer of a template that uses one reports as unavailable ("not available in this release"), nothing is planted, and a decoy of these forms planted by an earlier build is retired by the daily run. Use the `registry` hostname form and the `upn` phantom-account form.

## Observe mode

Indexers, antivirus and backup agents open files, and some of them will open your decoys. Observe mode lets you roll a policy out, see who reads its decoys, and approve the benign readers before those reads page anyone.

```yaml
policies:
  - schema_version: 1
    name: workstations
    enabled: true
    mode: observe
    observe_until: "2026-12-15T00:00:00Z"
    targeting: {tags: [workstation]}
    templates: {select_tags: [credentials]}
```

- **Reads and modifications.** In observe mode, an on-host read or modification of one of the policy's decoys by a reader no allowlist approves is still a `deception_hit`, with `mode: observe`, and is recorded. The shipped `deception-alert-observe` rule reports it at priority 2: `ext-cases` files it as a low-severity case, and a critical hit on the same host joins that case and raises it. There is no automatic response: the shipped alert and respond rules leave observe hits out, and `respond` with `action: policy` refuses them (`observe_mode_hit`) whatever an edited rule asks. An analyst can still isolate or tag by hand.
- **A use is never observed.** A decoy credential, link or host name being used means someone extracted it and acted on it, which no indexer or backup agent does. A use alerts at full priority in either mode. So does a copied decoy (seen on another sensor) and a read of a test decoy that no test run claims, by a reader no allowlist approves.
- **Nothing is dropped and nothing is learned.** Observe mode only lowers the priority of reads and modifications while it lasts. The extension never decides on its own that a reader is benign: you approve readers in the `reader_allowlist`.
- **Going live.** Set `mode: live`, or set `observe_until`, after which the policy is live by itself. `plan` lists the policies that observe and until when, and says when an `observe_until` has passed.
- **The shipped rules must be current.** Observe hits are told apart by the shipped rules. If your `deception-alert`, `deception-alert-observe`, `deception-alert-sanctioned-agent` or `deception-respond` rule is missing or older than the release's, `plan` warns while a policy observes: an older `deception-alert` reports observe hits at priority 10. Install the current ones with `deploy` and `apply_pack` (see [Upgrading](operations.md#upgrading)).

Tokens have an observe mode of their own, at priority 3: see [Observe mode for tokens](drops.md#observe-mode-for-tokens).

## Reader allowlist

An allowlist entry approves a reader of decoys. It is never matched by process name alone:

```yaml
reader_allowlist:
  - platform: windows
    image_path: 'C:\Windows\System32\SearchIndexer.exe'
    signer: 'C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Windows'
    comment: Windows Search
  - platform: linux
    image_path: /usr/libexec/tracker-miner-fs-3
    match: path
    comment: GNOME desktop indexer
```

- `image_path` is a full absolute path with no wildcards.
- Windows and macOS entries need the code `signer`, written the way LimaCharlie renders a certificate subject (take it from `list_readers`).
- A Linux entry is either `match: path` or the image's SHA-256 in `file_hash` (Linux has no code signer). No Linux event carries the image's hash, so a `file_hash` entry approves no Linux read today: use `match: path`.
- `match: path` (Linux only) approves a program by its exact, case-sensitive path, with no hash and no `signer`. The program must be in a root-owned system folder (`/usr/bin`, `/usr/sbin`, `/usr/libexec`, `/usr/lib`, `/usr/lib32`, `/usr/lib64`, `/bin`, `/sbin`, `/lib`, `/lib32`, `/lib64`, or inside a vendor's folder: `/opt/<vendor>/…/<program>`), written in canonical form (no `.`, `..`, `//` or trailing `/`, at most 255 characters), and it must not be a shell, an interpreter, the dynamic loader, a program runner, a browser or editor, a file or web server, or a general-purpose tool: the entry approves every run of the program, by anyone. `user` may narrow it; `package` and `ancestry` are refused. It matches only a read whose file event names the reader (the event's `PARENT`), never a process the sensor reports in a container, and only on hosts whose sensor release reports `PARENT`.
- A shared interpreter (Python, Node, a shell, PowerShell and similar) is only approved when you also set `user` and `ancestry`, the image paths of at least one required ancestor (the service that launches it). An ancestry entry may not itself be a shared interpreter.
- `package` (Linux), `user` and `ancestry` narrow the match further. Every field you set must match.
- A field missing from the observed event never matches, so unknown data fails toward alerting.

In the web app, **Settings** > **Reader allowlists** lists every entry of the organization's list or of one policy's (choose it in **Allowlist**), and adds, edits and removes them, with the checks above made before the save.

The organization-wide `reader_allowlist` applies to every decoy. A policy's `reader_allowlist` applies to the decoys that policy placed (see [Which policy's settings apply to a hit](#which-policys-settings-apply-to-a-hit)).

An approved reader's read or modification is dropped, in either mode, and never becomes a hit. A decoy **use** is never dropped by the allowlist.

**An entry can only match what the event names.** On Windows and macOS a reader is approved by its code signer, and many sensor file events carry the acting process's path and user but no signer. On Linux a reader is approved by its path (`match: path`), and only when the file event names it. Reads that carry neither cannot be approved by any entry: they keep alerting, and `list_readers` shows them with the reason (`not_approvable_reason`). A plain file-read event that names no process at all is never approvable.

### Every approved read is recorded

An approved read or modification is recorded as a `deception_read_allowed` event in your own telemetry, through the extension's `ext-deception` adapter, at most once per reader, decoy and UTC day. No shipped rule matches it. Write your own rule if you want to count approved reads or alert on them.

```json
{
  "event_type": "deception_read_allowed",
  "event_id": "ra_…",
  "oid": "…", "decoy_id": "…", "kind": "file", "template": "aws-credentials-backup", "policy": "workstations",
  "layer": "read", "sid": "…", "hostname": "ws-17", "platform": "windows",
  "reader_key": "r_…",
  "process": {"image_path": "C:\\Windows\\System32\\SearchIndexer.exe", "signer": "C=US, …", "sha256": "…",
              "user": "SYSTEM", "ancestry": ["C:\\Windows\\System32\\services.exe"]},
  "allowed_by": {"scope": "policy", "policy": "workstations", "index": 0, "comment": "Windows Search"},
  "day": "2026-11-20",
  "time": "2026-11-20T14:03:11.512Z"
}
```

`allowed_by` names the entry that approved the read: `scope` (`org` or `policy`), the policy, the entry's index and comment, and, for an entry from a Lookup, `lookup` and `record`. `test_decoy: true` is added when the decoy read is a policy's test decoy (outside any test run); the field is absent for a real decoy. The event never carries a command line or any decoy content.

### Find the readers: `list_readers`

Put a policy in observe mode, let it run, then call [`list_readers`](requests.md#list_readers). It returns one row per reader identity and policy, with its hit counts (observe and live), decoys and hosts, first and last seen, whether the current allowlist approves it and by which entry, and, when the identity has what an entry needs, an `allowlist_entry` you can paste as is. Entries that also constrain the user, package or ancestry show as `conditional`. Reads whose event named no process are one `unknown_process` group: they can never be approved.

### Share one list across organizations: Lookups

An allowlist entry, organization-wide or in a policy, can reference one of the organization's [Lookups](../../../../7-administration/config-hive/lookups.md) instead of naming a reader, so you keep one list of approved readers and reference it from every tenant's configuration:

```yaml
reader_allowlist:
  - lookup: mssp-approved-readers
    comment: shared approved readers
```

Each record of the Lookup is one allowlist entry in the same format as an inline one. The record key names it:

```yaml
# The Lookup's content
backup-agent-linux:
  platform: linux
  image_path: /opt/backup/bin/agent
  match: path
  comment: nightly backup, folder checked root-owned
av-scanner-windows:
  platform: windows
  image_path: C:\Program Files\AV\scanner.exe
  signer: <signer as list_readers shows it>
```

- A reference sets `lookup` (letters, digits and `. _ : -`, starting with a letter or digit, up to 128 characters) and an optional `comment`, and nothing else. At most 8 references per allowlist, each Lookup once.
- Records are checked with the same rules as inline entries. An invalid record approves nothing (the read alerts), and `plan` lists it with the reason under `reader_lookups`. A Lookup written as a plain list of keys (`newline_content`) has no values, so none of its records is an entry.
- A Lookup that is missing, disabled, unreadable, over 1,000 records or 1 MiB, or that could not be read at that moment, approves nothing, and `plan` warns about it. Nothing is cut short: a Lookup over a bound is not used at all. A Lookup outage can therefore cause alerts on approved readers, never a missed one.
- An edit to a Lookup takes effect within a minute. `plan` always reads the Lookups as they are now.
- **Organizations subscribed before Lookup support need a re-key.** Reading a Lookup needs the `lookup.get` permission on the extension's API key, and an existing subscription keeps the key it was given. Until it is re-keyed, `plan` shows its Lookups as `unreadable` and they approve nothing. Re-key once:

    ```bash
    limacharlie extension rekey --name ext-deception --oid "$OID"
    ```

### Starter list of benign readers

`list_kinds` returns `benign_readers`, a starter list of well-known benign readers to copy into your `reader_allowlist`. It is never applied automatically. It holds Windows Search (`SearchIndexer.exe`, `SearchProtocolHost.exe`, with entries ready to paste), Microsoft Defender (`MsMpEng.exe`, `MpCmdRun.exe`, whose path carries the platform version: take the exact path from `list_readers`), and the Linux desktop indexers as `match: path` entries: the GNOME Tracker and LocalSearch miners (`/usr/libexec/tracker-miner-fs-3`, `/usr/libexec/localsearch-3`, `/usr/lib/localsearch-3`) and KDE Baloo (`baloo_file` and `baloo_file_extractor` at their distributions' paths). These Linux paths are the only ones `list_readers` offers an entry for; any other Linux program is written by hand. Spotlight, OneDrive, Dropbox and backup agents are not in it, because their signers could not be verified in LimaCharlie's format: find them with `list_readers`.

## Custom domains

```yaml
custom_domains:
  - domain: decoy.example.com
```

A custom domain is a subdomain you control (at least three labels, no wildcard, no `limacharlie` in the name). It is validated and stored. **In this release no decoy uses it.** Hostnames and URLs in decoys are generated under LimaCharlie-operated decoy domains only. Do not rely on a custom domain until the release notes say it is used. The `verified` field is set only by the extension after its own ownership check, and a value you write is never trusted. The web app does not show custom domains while no decoy uses them: set them in your configuration as code, and a save from the web app keeps them as they are.

## AWS key sources

`key_sources` is reserved for decoys made of real AWS access keys with a deny-all policy, which would also catch a key used from anywhere, not only from the host. It is **not built**: the field must be empty, and a non-empty value is rejected.

What exists today for AWS are two decoy templates whose keys are not real AWS keys, and whose `endpoint_url` points at the collector's fake AWS API:

- `aws-config-backup` is a config file with a named profile. It catches use when the file is passed explicitly with `AWS_CONFIG_FILE` and its profile is selected with `--profile` or `AWS_PROFILE`.
- `aws-credentials-backup` is a credentials file whose profile itself carries `endpoint_url`, so use is caught when the file is passed with `AWS_SHARED_CREDENTIALS_FILE` and its generated profile is selected with `--profile` or `AWS_PROFILE`, without a separate config file.

The clients verified to honor `endpoint_url` in the credentials file are botocore-based ones (the AWS CLI and boto3). Other SDKs, and endpoint overrides set through other mechanisms, are **not verified**. Keys copied to another machine without the file go to real AWS, where they are invalid and nothing is reported.

## Isolation cap

`isolation_cap_per_hour` bounds how many hosts the extension may isolate automatically per hour for the organization. Absent or `0` means the default, 5. The cap also applies when the extension re-tries an incident whose earlier attempt failed. If the organization's configuration cannot be read, or this field is invalid, `respond` refuses to isolate at all, because the cap would be unknown. The value is a whole number from 0 to 1,000. The **Settings** tab of the web app shows the cap in force (and whether it is yours or the default) and sets it; **Use the default** removes the field.
