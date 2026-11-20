# Deception: Configuration

Everything you can change lives in one record: the `ext-deception` record in the `extension_config` [Config Hive](../../../../7-administration/config-hive/index.md). It is a normal hive record, so you can read it, edit it, version it and sync it with Git Sync or your infrastructure-as-code like any other extension configuration. See [Using Extensions](../../using-extensions.md).

Only the generated decoy instances and their secrets are kept out of the record. They live in the extension's own store, and no request returns a secret value.

```bash
limacharlie extension config-get --name ext-deception --oid "$OID"
limacharlie extension config-set --name ext-deception --input-file deception.yaml --oid "$OID"
```

You can also edit the record in the web app: the **Policies** tab edits policies and templates, copies templates from the Template Library, and has a raw editor for the whole record (custom domains, the reader allowlist, the isolation cap and template settings). The extension validates a save the same way, and a save that conflicts with a newer version is refused without overwriting it.

## Enabling the configuration record

The extension reads your configuration from the record named `ext-deception`. The platform gives an extension an empty configuration when that record is disabled, and a record saved with `limacharlie extension config-set` is disabled unless its `usr_mtd.enabled` says otherwise (the CLI's normal behavior for a new record). Enable it once after the first `config-set`:

```bash
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

- `plan`, `deploy`, `verify`, `rotate`, `remove`, `test_fire` and `coverage` (and `list` or `list_hosts` with a `policy` filter) refuse with "the ext-deception configuration is disabled".
- Hits on decoys already planted are still judged and alerted.
- The daily run and a configuration update leave the candidate rules derived from your templates and the entries in other extensions' configurations as they are and retire no decoy (the base plumbing rules and any missing shipped detection rules are still repaired), and the daily response says why until the record is enabled. A disabled or unreadable record is never read as "you removed everything".
- `respond` refuses to isolate, because your isolation cap is unknown. Tagging still works.

The extension never writes this record, so it never enables it for you. The web app shows a banner with **Enable configuration** to anyone who can read and write the record (`ext.conf.get` and `ext.conf.set`).

## Validation

The extension validates the whole record when it is saved, including each template's `spec`, and rejects it with errors that name the field (for example `templates[3].spec.file_name: required`). Unknown fields are rejected too.

A record can still reach the extension without that check (written while the extension was down, or written for a newer format than the running extension supports). On read, the extension skips individual policy and template records it cannot use (for example one written for a newer record or kind version) and reports each, with the field and the reason, in the `warnings` of `plan` and in `coverage`. The top-level record is different: if its own `schema_version` is newer than the running extension supports, the whole record is refused and requests that read the configuration fail with an error (`respond` also refuses to isolate) until you rewrite the record or the extension is upgraded. A skipped record's already-placed decoys stay as they are. The extension never removes what it does not understand, and never rewrites your records.

Limits: 100 policies, 300 templates, 20 custom domains, 200 reader allowlist entries per list. The record is capped at 1 MB by the hive. Names are lowercase letters, digits, `.`, `_` and `-`, 1 to 64 characters, starting with a letter or digit. Template tags follow the same pattern, up to 32 characters, at most 16 per template.

## Top-level fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Version of the record format. Currently `1`. Required. A newer value than the extension supports makes requests fail (see [Validation](#validation)). |
| `policies` | Which templates go on which sensors, and what to do on a hit. |
| `templates` | The decoys you use. |
| `custom_domains` | Bring-your-own decoy domains. See [Custom domains](#custom-domains). |
| `reader_allowlist` | Benign readers of decoys, applied to every policy. |
| `isolation_cap_per_hour` | Most automatic isolations per hour for the organization. `0` or absent means the default of **5**. Maximum 1000. |
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
    dc_logon_collection: false
    reader_allowlist: []
```

| Field | Meaning |
| --- | --- |
| `name` | Unique. Required. |
| `enabled` | A disabled policy plants nothing and watches nothing. |
| `targeting` | `tags`, `platforms` and `sids` combine. At least one must be set: an empty targeting would match every sensor and is rejected. |
| `templates` | `select_tags` and `names`; at least one required. Only templates in this same record are selectable. The default library is outside it. |
| `responses.isolate` | Lets the default `deception-respond` rule isolate the host when the evidence is an event the decoy's own sensor reported. Default `false`. See [Isolation](detections.md#isolation). |
| `responses.start_ai`, `responses.ai_sop` | Recorded, but starting an AI triage session from the extension is **not built**: `respond` with `ai_triage` answers that it is not available. To launch an AI agent, add a `start ai agent` response to your own detection rule. `ai_sop` is accepted only together with `start_ai`. |
| `setup_on_new_sensors` | Place decoys when a matching sensor first connects. |
| `dc_logon_collection` | Reserved for the AD-form phantom accounts, which are **not available in this release**. The field is accepted and **ignored**: nothing is tagged on your domain controllers and no Windows event collection is installed because of it, and `plan` and `deploy` warn about it for each policy that sets it. Leave it `false`. |
| `reader_allowlist` | Benign readers for this policy, in addition to the organization-wide list. |

A policy that names a template that does not exist, or a tag no template carries, is rejected when you save the record. If such a record is already stored, the policy stays usable for the rest of its selection and `plan` reports a warning.

Policies that match the same sensor and select the same template share its placements. A decoy is keyed by sensor and template, so the policy that places it owns it and supplies its response settings, and another policy that selects the same template adds nothing on that sensor while the decoy exists. When one planning pass covers several policies (a `deploy` or the daily run without a `policy`), the first matching policy in the order the policies are stored in the record is the one that places it. A decoy that already exists keeps its owner: a `deploy` scoped to a later policy that runs first makes that policy the owner, and a decoy is not handed to another policy if its owner is removed while another policy keeps the decoy alive, so a hit on it finds no policy and the `policy` response does nothing. A decoy is retired when no enabled policy selects its template any more, not when one of several policies that select it is removed. A sensor that stops matching a policy's targeting does not retire its decoys either, but it is no longer fully watched: the read and modify alerts rely on watch rules scoped to the policy's sensor tags and platforms, so a sensor that loses a required tag stops reporting reads and modifications of its decoys, while use alerts keep working. `list_hosts` still shows such a sensor as `protected`. Restore the tag, or remove its decoys with `remove` and `sid`.

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

Content must not mention `limacharlie`. A template is checked by rendering it once at write time. Write your own templates the same way as the library ones: take every name you put in or on a file from `{{vocab "..."}}` rather than typing a fixed word, because a fixed word is the same in every organization that copies it.

The `hostname` kind adds `form` (`registry` or `internal`) and `hosts`, and holds a `file` spec for the file that names the hosts. The `phantom_account` kind adds `form` (`upn` or `ad`), `source` (`any`, `entra`, `okta`, UPN form only), `upn_domain`, `ad_domain` and a `file` spec; its content uses `{{account}}` and `{{password}}`. Copy these from the default library, or read the schema from `list_kinds`. The library is built into the extension and ships with each release. A template you copy from it is stored in your configuration and is yours to edit: a later release does not change your copy, and the library itself is never changed. In the web app, the **Template Library** copies templates for you, and the template viewer and editor edit your own templates as a form or as JSON. Library templates are read-only in the editor: customize a copy.

The `internal` hostname form and the `ad` phantom-account form are **not available in this release**. They still validate, so an existing configuration keeps loading, but every alert layer of a template that uses one reports as unavailable ("not available in this release"), nothing is planted, and a decoy of these forms planted by an earlier build is retired by the daily run. Use the `registry` hostname form and the `upn` phantom-account form.

## Reader allowlist

Reads of a decoy by a known-benign program (indexers, backup agents, sync clients) should not page an analyst. An allowlist entry approves a reader. It is never matched by process name alone:

```yaml
reader_allowlist:
  - platform: windows
    image_path: 'C:\Program Files\Backup Agent\agent.exe'
    signer: Example Software Ltd
    comment: nightly backup
  - platform: linux
    image_path: /usr/sbin/backupd
    file_hash: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
    user: root
```

- `image_path` is a full absolute path with no wildcards.
- Windows and macOS entries need the code `signer`. Linux entries need the image's SHA-256 in `file_hash`, since Linux has no code signer.
- A shared interpreter (Python, Node, a shell, PowerShell and similar) is only approved when you also set `user` and `ancestry`, the image paths of at least one required ancestor (the service that launches it). An ancestry entry may not itself be a shared interpreter.
- `package` (Linux), `user` and `ancestry` narrow the match further. Every field you set must match.
- A missing field on the observed process never matches, so unknown data fails toward alerting.

An approved reader's read or modification is dropped before it becomes a hit. A decoy **use** is never dropped by the allowlist.

### Learning window

The first decoys of each combination of policy, operating system and template start a 72-hour learning window. During it, reads and modifications by a process whose image path is known are dropped and recorded as candidate readers instead of becoming hits, so the first hosts of a new combination do not flood you with indexer reads. Use alerts are not affected. A combination that has finished learning is live from the first minute on every later host.

Be aware of two consequences in this release:

- A read by an attacker's process during the window is dropped the same as a benign one, if the extension knows the process's image path. If you cannot tolerate that, deploy to a small set of hosts first, wait out the window, then widen the policy, or approve readers explicitly in the allowlist and treat the first 72 hours as reduced read coverage.
- The recorded candidate readers are not returned by any request yet, so you cannot list and approve them. Add readers to the allowlist by hand.

## Custom domains

```yaml
custom_domains:
  - domain: decoy.example.com
```

A custom domain is a subdomain you control (at least three labels, no wildcard, no `limacharlie` in the name). It is validated and stored. **In this release no decoy uses it.** Hostnames and URLs in decoys are generated under LimaCharlie-operated decoy domains only. Do not rely on a custom domain until the release notes say it is used. The `verified` field is set only by the extension after its own ownership check, and a value you write is never trusted.

## AWS key sources

`key_sources` is reserved for decoys made of real AWS access keys with a deny-all policy, which would also catch a key used from anywhere, not only from the host. It is **not built**: the field must be empty, and a non-empty value is rejected.

What exists today for AWS are two decoy templates whose keys are not real AWS keys, and whose `endpoint_url` points at the collector's fake AWS API:

- `aws-config-backup` is a config file with a named profile. It catches use when the file is passed explicitly with `AWS_CONFIG_FILE` and its profile is selected with `--profile` or `AWS_PROFILE`.
- `aws-credentials-backup` is a credentials file whose profile itself carries `endpoint_url`, so use is caught when the file is passed with `AWS_SHARED_CREDENTIALS_FILE` and its generated profile is selected with `--profile` or `AWS_PROFILE`, without a separate config file.

The clients verified to honor `endpoint_url` in the credentials file are botocore-based ones (the AWS CLI and boto3). Other SDKs, and endpoint overrides set through other mechanisms, are **not verified**. Keys copied to another machine without the file go to real AWS, where they are invalid and nothing is reported.

## Isolation cap

`isolation_cap_per_hour` bounds how many hosts the extension may isolate automatically per hour for the organization. Absent or `0` means the default, 5. The cap also applies when the extension re-tries an incident whose earlier attempt failed. If the organization's configuration cannot be read, or this field is invalid, `respond` refuses to isolate at all, because the cap would be unknown.
