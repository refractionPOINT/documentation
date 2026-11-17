# Deception: Decoys and Coverage

## Decoy kinds

A **kind** is a mechanism built into the extension: how a decoy is placed, how a hit on it is detected, and what it needs from your organization. A **template** is data: one concrete decoy of a kind. Most new decoys are a new template of an existing kind, and you can write them yourself. Run `list_kinds` for each kind's version and JSON schema of its settings.

| Kind | What it plants | Alerts |
| --- | --- | --- |
| `file` | A credential file, service configuration or note on the endpoint. Secrets inside point at LimaCharlie's collector. | read, modify, delete (sensor); use (collector) |
| `hostname` | A file (inventory note, FTP/SFTP client config) naming decoy hostnames. Registry form: names under LimaCharlie-operated decoy domains. Internal form: names under your own internal domain, deliberately non-existent. | read, modify, delete (sensor); use (DNS lookup seen by the sensor, request on the collector) |
| `phantom_account` | A file naming a username that exists nowhere, with a fake password. UPN form (`user@domain`) for Entra ID or Okta, AD form (`DOMAIN\user`) for domain controllers. | read, modify, delete (sensor); use (failed sign-in in your logs) |

### Alert layers

Every hit carries a `layer`:

| Layer | Meaning | Default rule |
| --- | --- | --- |
| `read` | The decoy file was opened, or its path appeared on a command line. | Priority 10 |
| `modify` | The decoy file was modified. | Priority 10 |
| `delete` | The decoy file was deleted unexpectedly. The decoy is planted again afterward. | Priority 5, never isolates |
| `use` | A secret inside the decoy was used. | Priority 10 |

A modification counts as a hit because on Linux an open for read-write is reported by the sensor as a modification, not a read. An unexpected delete is more often cleanup than an attack, so it gets a lower priority.

## Default template library

`list_kinds` returns the library in its `library` field. These are starting points for your own templates. Nothing in the library is placed until you copy a template into your configuration.

| Template | Kind | Platforms | What it imitates |
| --- | --- | --- | --- |
| `aws-config-backup`, `aws-credentials-backup` | file | Linux, macOS, Windows | Leftover AWS CLI config and credentials with a decoy profile whose `endpoint_url` points at the collector |
| `kubeconfig-backup` | file | Linux, macOS | Old kubeconfig whose server is a fake Kubernetes API |
| `docker-config-backup` | file | Linux, macOS, Windows | Docker `config.json` backup naming a fake registry |
| `env-ops-file` | file | Linux, macOS, Windows | `.env` with internal API base URLs and bearer tokens |
| `git-credentials-backup`, `git-checkout-config-leftover` | file | Linux, macOS, Windows | Git credentials file and a leftover checkout config pointing at a fake git server |
| `npmrc-backup`, `pypirc-backup` | file | Linux, macOS, Windows | Package registry credentials for a fake registry |
| `pip-conf-backup` | file | Linux, macOS | `pip.conf` pointing at a fake index |
| `rclone-backup`, `minio-client-backup`, `s3cfg-backup` | file | Linux, macOS, Windows (`s3cfg-backup`: Linux, macOS) | Storage client configs whose endpoint is the collector |
| `mcp-config-ops` | file | Linux, macOS, Windows | A standalone MCP server configuration pointing at a fake MCP server |
| `ops-runbook-breadcrumb` | file | Linux, macOS, Windows | A runbook naming the decoy API, decoy MCP server and decoy credentials, so an agent follows several decoys in sequence |
| `passwords-note`, `passwords-csv` | file | Linux, macOS, Windows | A notes file and an exported-browser-passwords CSV naming decoy login pages |
| `root-api-config`, `root-backup-credentials` | file | Linux | Root-only files in `/root`, `/etc`, `/opt` or `/var/backups` |
| `win-web-config` | file | Windows | IIS `web.config` with connection strings, under a generated folder |
| `hostname-registry-inventory` | hostname | Linux, macOS, Windows | An inventory note naming decoy hosts under a decoy domain |
| `hostname-internal-inventory` | hostname | Windows | An inventory note naming decoy hosts under your internal domain |
| `win-filezilla-sitemanager`, `win-winscp-ini` | hostname | Windows | FileZilla and WinSCP site lists naming decoy hosts |
| `phantom-upn-credentials` | phantom_account | Linux, macOS, Windows | A note with a phantom cloud account |
| `phantom-ad-credentials`, `win-groups-xml`, `win-unattend-xml` | phantom_account | Windows | A note, a Group Policy Preferences `Groups.xml` and an `unattend.xml` with a phantom AD account |

The service names a decoy uses (for example the fake Kubernetes API or fake AWS API) are per-organization labels under the decoy domains. Nothing on the collector's public side names LimaCharlie, and a template whose content mentions `limacharlie` is rejected.

## What the collector answers

Decoy secrets that carry their own destination point at a public collector that answers like the real service, so the attacker keeps going and the extension learns more. It serves a fake Kubernetes API, a fake AWS API (including STS identity, S3 listings and Secrets Manager), web logins and JSON APIs (SSO login, Grafana, Jenkins, Vault), a fake MCP server (a tool call is the hit, connecting and listing tools is not), a git server, and npm and PyPI registries. It records the source IP, User-Agent, an allowlist of headers and the token. The collector holds no organization credential. It only forwards what it receives, and the extension decides whether it is a real hit by looking the token up in its registry.

## File names and paths

- File names come from a vocabulary generated once per organization and never regenerated. A template refers to a vocabulary entry such as `{{vocab "kubeconfig_backup"}}`.
- Templates that use a generated file name work on Linux, macOS and Windows. A template with a fixed file name (`web.config`, `Groups.xml`, `unattend.xml`, `WinSCP.ini`, `sitemanager.xml`) is Windows-only and must sit under a generated folder. A bare common file name is never used as a match rule.
- The extension places a decoy only into a directory that already exists. If the directory is missing on a host, the template is skipped on that host and shown as `directory missing`. It retries after the next daily inventory. It never creates directories.
- It never overwrites a file it did not create. If something already exists at the path, placement fails as `path in use` and is reported. A decoy whose contents changed is retired, never rewritten.
- Placement goes only at paths that look like leftovers (for example `~/.kube/config.prod-old`, `~/backup/aws-credentials`), never at a tool's default path. A template can name separate directories for Linux hosts with no human users (`linux-server`), such as `/root` or `/opt`.

## Platforms

The extension places decoys on Windows, Linux and macOS sensors. The placement helper is built for x86-64 and ARM64 on each. Other architectures are not supported.

A template declares its platforms. The planner skips a host whose platform a template does not list, a host where the tool the template imitates is absent (`requires_packages`, `requires_files`), and a host where the target directory does not exist.

## Sensor modes and what they cost

The extension never changes a sensor's mode. It plans around it:

| Sensor | Placement | Read / modify / delete alerts | Use alerts |
| --- | --- | --- | --- |
| Normal mode | Yes | Yes | Yes |
| `lc:epp` or performance mode | Yes | **No.** These modes drop the file collectors. | Yes. Decoys here are use-only, and count as covered only once verified. |
| `lc:response` | **No.** `put` and `run` are disabled. | Not covered | Not covered |
| `lc:sleeper` | **No.** The sensor runs nothing. | Not covered | Not covered |
| Kubernetes DaemonSet sensor | **No.** It sees the node through a read-only mount and writes only inside its own container. | Not covered | Not covered |

Hosts in the last three rows show in `plan` and `coverage` as not covered, with the reason. Kubernetes nodes that run the sensor installed on the node itself are covered. Decoys inside containers are not supported.

On Linux, read alerts need the eBPF-capable sensor. The extension checks the sensor mode only, not the Linux tier: whether a legacy (non-eBPF) Linux sensor raises read alerts is **not verified**.

## What each decoy needs from the organization

| Decoy | Needs | Without it |
| --- | --- | --- |
| File decoys, placement | `ext-artifact` subscribed, a supported sensor | Placement is Unavailable for the whole organization, with "Subscribe ext-artifact". |
| File decoys, read alert | `ext-exfil` subscribed, file collectors on | The decoy is still planted. Reads are not caught, only use. |
| File decoys, modify and delete alerts | `ext-integrity` subscribed, file collectors on | Same as above. |
| File, MCP and registry-hostname decoys, use alert | Nothing else | Always available. |
| Hostnames under your internal domain | At least one Windows sensor (only Windows reports failed lookups) | Not offered. |
| Phantom accounts, UPN form | Entra ID adapter with the `sign_ins` source (Entra ID P1 or P2), or the Okta adapter | Not planted. |
| Phantom accounts, AD form | `ext-artifact` and `ext-exfil` subscribed, a sensor on every domain controller, failure auditing on, `dc_logon_collection: true` in the policy | Not planted, with the missing piece named. |

## Log sources and their limits

| Source | What the extension reads | Limits |
| --- | --- | --- |
| Entra ID, `sign_ins` source | Failed sign-ins with status `50034` (user not found), checked against the planted usernames | Needs Entra ID P1 or P2. |
| Okta, system log | Failed sign-ins (`FAILURE`), checked against the planted usernames | |
| Windows domain controllers | `WEL` events 4776 (NTLM) and 4768 (Kerberos) with the unknown-user result codes, collected through `ext-artifact` `wel://` rules and `ext-exfil` `WEL` | See below. |
| Sensor DNS | `DNS_REQUEST` for names under decoy domains, and failed lookups under your internal domain | Failed lookups are reported by Windows sensors only. On Linux and macOS a lookup is reported only if the name resolves. |

Google Workspace is not a supported source. **Not verified:** that Entra ID, Okta and domain controllers each log sign-in attempts for non-existent usernames in a form the extension can match, in every tenant configuration. Treat phantom accounts as unproven until `test_fire` and a real attempt against your tenant confirm them.

Domain controller collection is opt-in per policy. The extension tags your domain controllers `deception-dc` and scopes both the `wel://` collection and the `WEL` event to that tag, so no other sensor's collection changes. The collection filters by event ID only, so with success auditing on, successful Kerberos ticket requests and NTLM validations stream too. That volume grows with your logon rate. A failed logon for a missing user also comes from typos and password sprays, so a hit counts only when the username is exactly one of the planted ones.

If a planted username later signs in successfully (for example because someone created a real account with that name), the decoy is retired.

## Coverage statuses

`coverage` lists each template and layer with one status:

| Status | Meaning |
| --- | --- |
| `active` | Requirements are met and at least one verified decoy exists. |
| `partial` | Some layers of the template work and this one does not (for example "read alerts not covered"), or the layer's requirements are met but no decoy of the template is verified yet. |
| `unavailable` | A requirement is missing, named exactly (for example "Connect Entra ID with sign-in logs (needs Entra ID P1 or P2)"). |
| `blind` | The layer's requirements are met but its source delivered no data for over 24 hours. Applies to Entra ID and Okta sources. The decoys stay in place. |
| `broken` | The latest `test_fire` for that layer produced no detection, for example because a default rule was edited or disabled. |

`blind` and `broken` appear in `coverage` only. In this release the extension does not send an alert or event when a source goes blind or a path breaks, so check `coverage` after changes to a source or a rule. The `deception_coverage_warning` event is a separate, narrower signal, described under [Detections](detections.md#the-deception_coverage_warning-event).

## New and short-lived sensors

A policy with `setup_on_new_sensors: true` places decoys when a matching sensor first connects, without waiting for the daily run. The policy matches by sensor tags, so tags applied by the installation key at enrollment work. Placement only tasks a sensor that is online. The daily reconcile compares the registry with the sensor list: a sensor that is gone has its placement state dropped, but its tokens stay in the registry for a retention period, so a credential stolen from a node that no longer exists is still caught when used, and the hit names the original host.

A clone of a sensor carries the source host's decoy files at the template paths, so it gets no decoys of its own for those templates (they are skipped as `path in use`).

## Watch-rule budget

A sensor keeps at most 100 Exfil watch rules, shared with everything else you collect. A read alert costs one watch rule per template for the whole organization, not one per host. `plan` returns `watch_budget` with the limit, the number of rules the extension owns, the number that are yours, and, when the total exceeds the limit, the names of your newest rules that a sensor would drop. The figure is an organization-level upper bound: per-sensor tag and platform filters are not applied. Whether the extension's own rules sort ahead of yours on a sensor depends on `ext-exfil` behavior that is **not verified** here, so keep the total under 100.
