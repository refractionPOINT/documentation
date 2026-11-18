# Deception: Decoys and Coverage

## Decoy kinds

A **kind** is a mechanism built into the extension: how a decoy is placed, how a hit on it is detected, and what it needs from your organization. A **template** is data: one concrete decoy of a kind. Most new decoys are a new template of an existing kind, and you can write them yourself. Run `list_kinds` for each kind's version and JSON schema of its settings.

| Kind | What it plants | Alerts |
| --- | --- | --- |
| `file` | A credential file, service configuration or note on the endpoint. Secrets inside point at LimaCharlie's collector. | read, modify, delete (sensor); use (collector) |
| `hostname` | A file (inventory note, FTP/SFTP client config) naming decoy hostnames. Registry form: names under LimaCharlie-operated decoy domains. Internal form (names under your own internal domain): **not available in this release**, see below. | read, modify, delete (sensor); use (DNS lookup seen by the sensor, request on the collector) |
| `phantom_account` | A file naming a username that exists nowhere, with a fake password. UPN form (`user@domain`) for Entra ID or Okta. The AD form (`DOMAIN\user`) is **not available in this release**. | read, modify, delete (sensor); use (failed sign-in in your logs) |

### Alert layers

Every hit carries a `layer`:

| Layer | Meaning | Default rule |
| --- | --- | --- |
| `read` | The decoy file was opened, or its path appeared on a command line. | Priority 10 |
| `modify` | The decoy file was modified. | Priority 10 |
| `delete` | The decoy file was deleted unexpectedly. The decoy is planted again afterward. | Priority 5, never isolates |
| `use` | A secret inside the decoy was used. | Priority 10 |

Priority 10 applies to the default rules, which you can edit. A `use` hit never isolates the host, by design, even when the secret is used from the original host: it arrives from the collector or a sign-in log, and a network address is not proof of which machine used the secret. Only an event reported by the decoy's own sensor (a read, a modification or a command-line match) can isolate (see [Isolation](detections.md#isolation)).

A modification counts as a hit because on Linux an open for read-write is reported by the sensor as a modification, not a read. An unexpected delete is more often cleanup than an attack, so it gets a lower priority.

## Default template library

`list_kinds` returns the library in its `library` field. These are starting points for your own templates. Nothing in the library is placed until you copy a template into your configuration.

| Template | Kind | Platforms | What it imitates |
| --- | --- | --- | --- |
| `aws-config-backup` | file | Linux, macOS, Windows | A saved AWS CLI config with a decoy profile whose `endpoint_url` points at the collector. Use is caught when the file is passed with `--config-file` or `AWS_CONFIG_FILE`. |
| `aws-credentials-backup` | file | Linux, macOS, Windows | A saved AWS credentials file whose profile carries `endpoint_url`, so the key goes to the collector when the file is used (for example with `AWS_SHARED_CREDENTIALS_FILE`). Verified clients: botocore-based ones (AWS CLI, boto3), which read `endpoint_url` from the credentials file. Other SDKs, and endpoint overrides in general, are **not verified**. |
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
| `hostname-internal-inventory` | hostname | Windows | An inventory note naming decoy hosts under your internal domain. **Not available in this release**: every alert layer reports unavailable and nothing is planted. |
| `win-filezilla-sitemanager`, `win-winscp-ini` | hostname | Windows | FileZilla and WinSCP site lists naming decoy hosts |
| `phantom-upn-credentials` | phantom_account | Linux, macOS, Windows | A note with a phantom cloud account |
| `phantom-ad-credentials`, `win-groups-xml`, `win-unattend-xml` | phantom_account | Windows | A note, a Group Policy Preferences `Groups.xml` and an `unattend.xml` with a phantom AD account. **Not available in this release**: every alert layer reports unavailable and nothing is planted. |

The service names a decoy uses (for example the fake Kubernetes API or fake AWS API) are per-organization labels under the decoy domains. Names written inside decoy files (clusters, users, folders, hosts) come from the same per-organization vocabulary. Nothing on the collector's public side names LimaCharlie, and a template whose content mentions `limacharlie` is rejected.

## What the collector answers

Decoy secrets that carry their own destination point at a public collector that answers like the real service, so the attacker keeps going and the extension learns more. It serves a fake Kubernetes API, a fake AWS API (including STS identity, S3 listings and Secrets Manager), web logins and JSON APIs (SSO login, Grafana, Jenkins, Vault), a fake MCP server (a tool call is the hit, connecting and listing tools is not), a git server, and npm and PyPI registries. Its answers are derived per organization, from a private key that only LimaCharlie holds: the fake MCP server's name and tools, bucket and secret names, identities and pages differ in every organization, and a fake host label belongs to one fake application, so every path, link and redirect on it answers like that application. A decoy login session carries the lifetime the fake service advertises and expires on it (for example a Vault login 32 days, a Grafana cookie 30 days, a Jenkins session 30 minutes, a portal session 12 hours; package registry tokens do not expire). An expired session authenticates nobody, but is still attributed to the decoy it came from. It records the source IP, User-Agent, an allowlist of headers and the token. The collector holds no organization credential. It only forwards what it receives, and the extension decides whether it is a real hit by looking the token up in its registry.

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

The mode and DaemonSet exclusions are reported per host in `plan`. `coverage` is an organization-level view of each template and layer: it does not list hosts, and an `active` status is not proof that every selected host is covered. Kubernetes nodes that run the sensor installed on the node itself are covered. Decoys inside containers are not supported.

On Linux, read alerts need the eBPF-capable sensor. The extension checks the sensor mode only, not the Linux tier: whether a legacy (non-eBPF) Linux sensor raises read alerts is **not verified**.

## What each decoy needs from the organization

| Decoy | Needs | Without it |
| --- | --- | --- |
| File decoys, placement | `ext-artifact` subscribed, a supported sensor | Placement is Unavailable for the whole organization, with "Subscribe ext-artifact". |
| File decoys, read alert | `ext-exfil` subscribed, file collectors on | A template that also alerts on use is still planted: the read layer shows `partial` and only use is caught. A template whose only alert is read has no working alert path, shows `unavailable`, and is not planted. |
| File decoys, modify and delete alerts | `ext-integrity` subscribed, file collectors on | The modify and delete layers show `partial` or `unavailable` in the same way. |
| File, MCP and registry-hostname decoys, use alert | Nothing else | Always available. |
| Hostnames under your internal domain | **Not available in this release.** Internal-domain hostname decoys are deferred to a later release. | Not planted. Every alert layer reports unavailable. |
| Phantom accounts, UPN form | Entra ID adapter with the `sign_ins` source (Entra ID P1 or P2), or the Okta adapter | Not planted. |
| Phantom accounts, AD form | **Not available in this release.** Fake Active Directory accounts are deferred to a later release, whatever your tenant does. | Not planted. Every alert layer reports unavailable. |

## Log sources and their limits

| Source | What the extension reads | Limits |
| --- | --- | --- |
| Entra ID, `sign_ins` source | Failed sign-ins with status `50034` (user not found), checked against the planted usernames | Needs Entra ID P1 or P2. Successful sign-ins are not alerted in this release. |
| Okta, system log | Failed sign-ins (`FAILURE`), checked against the planted usernames | Successful sign-ins are not alerted in this release. The quiet-feed note (below) is based only on authentication events (`user.session.start`, `user.authentication.*`) of an adapter whose platform is `okta`. |
| Windows domain controllers | **Not used in this release.** No domain controller is tagged and no Windows event collection is installed. | |
| Sensor DNS | `DNS_REQUEST` for names under decoy domains. | Failed lookups are reported by Windows sensors only. On Linux and macOS a lookup is reported only if the name resolves. |

Google Workspace is not a supported source. **Not verified:** that Entra ID and Okta each log sign-in attempts for non-existent usernames in a form the extension can match, in every tenant configuration. Treat phantom accounts as unproven until `test_fire` and a real attempt against your tenant confirm them.

**Quiet sign-in feeds.** The platform does not report when an adapter last delivered data, so the extension cannot tell a quiet source from a broken one. It observes the sign-in events it is sent (at most one observation request an hour) and, when none has been seen for a day, adds an informational note to the affected coverage items: "no sign-in observed in N hours". The note is not a failure and never changes a status: a tenant whose users rarely sign in has a healthy feed with no sign-ins. An Okta adapter registered under another platform name (for example the generic `json` platform) is not observed at all, so no note is made about it.

**Successful sign-ins are not alerted.** Only failed sign-ins against a planted username raise a `use` hit. A successful sign-in under a phantom name raises nothing and does not retire the decoy. If a planted name later becomes a real account (for example because someone creates an account with that name), remove the decoy with `remove`, or replace it with `rotate`, and check the template so the new name is not reused. Until then, that account's failed sign-ins (typos, for example) can raise `use` hits.

## Coverage statuses

`coverage` lists each template and layer with one status:

| Status | Meaning |
| --- | --- |
| `active` | Requirements are met and at least one verified decoy exists. |
| `partial` | Some layers of the template work and this one does not (for example "read alerts not covered"), or the layer's requirements are met but no decoy of the template is verified yet. |
| `unavailable` | A requirement is missing, named exactly (for example "Connect Entra ID with sign-in logs (needs Entra ID P1 or P2)"). For fake AD accounts and internal-domain hostnames the reason is "not available in this release", on every layer of the template. |
| `blind` | **Never set in this release.** The platform does not report when an adapter last delivered data, so the extension cannot tell. A quiet sign-in feed shows as an informational note instead (see above). Monitor the health of your sign-in log sources independently. |
| `broken` | The latest `test_fire` for that layer produced no detection, or a shipped alert rule is missing or disabled (see below). |

`broken` appears in `coverage` only. The extension does not send an alert or event when a path breaks, so check `coverage` after changes to a rule.

### Rule integrity

Besides the test result, `coverage` checks each shipped detection rule in `dr-general` against what the extension wrote. The check compares the whole stored record, not just the detection logic: the detect and respond sections, scoping, options and the rule's tags and expiry. It gives each rule one of three outcomes:

| Outcome | Meaning |
| --- | --- |
| verified | The stored rule is identical to the shipped one. |
| `unverified (rule edited: <rule>)` | The rule differs from the shipped one in any way. The extension does not evaluate rules, so it neither calls an edit healthy nor broken. Check that the rule still fires on `deception_hit` events as the shipped one does, or restore it with `deploy` and `apply_pack`. |
| `broken` | The rule is missing, or disabled. |

A missing or disabled `deception-alert` marks the read, modify and use layers `broken`; a missing or disabled `deception-alert-decoy-deleted` marks the delete layer `broken`. For the other shipped rules the finding is reported but marks no path. The answer carries `pack_issues` and a `pack_check` object: `status` (`ok`: every rule verified; `issues`: one is missing or disabled; `unverified`: a rule was edited, or the check itself could not run, with a `reason`), `checked_at` (the last check that ran to an answer) and `attempted_at` (the latest attempt). If an attempt fails, the platform error is logged and not returned, `checked_at` keeps the last good result, and the two times differ. Never read `unverified` as healthy.

Test results are read for every alert path of the configuration, in bounded batches. If a request could not read some of them, `test_results_unread` says how many; those paths are not marked broken by that request. The `deception_coverage_warning` event is a separate, narrower signal, described under [Detections](detections.md#the-deception_coverage_warning-event).

## New and short-lived sensors

A policy with `setup_on_new_sensors: true` places decoys when a matching sensor first connects, without waiting for the daily run. The policy matches by sensor tags, so tags applied by the installation key at enrollment work. Placement only tasks a sensor that is online. The daily reconcile compares the registry with the sensor list: a sensor that is gone has its placement state dropped, but its tokens stay in the registry for a retention period, so a credential stolen from a node that no longer exists is still caught when used, and the hit names the original host.

A clone of a sensor carries the source host's decoy files at the template paths, so it gets no decoys of its own for those templates (they are skipped as `path in use`).

## Watch-rule budget

A sensor keeps at most 100 Exfil watch rules, shared with everything else you collect. A read alert costs one watch rule per template for the whole organization, not one per host. A template that several policies deploy with different sensor tags costs one rule for each distinct tag set. `plan` returns `watch_budget` with the limit, the number of rules the extension owns, the number that are yours, and, when the total exceeds the limit, the names of your newest rules that a sensor would drop. The figure is an organization-level upper bound: per-sensor tag and platform filters are not applied. Whether the extension's own rules sort ahead of yours on a sensor depends on `ext-exfil` behavior that is **not verified** here, so keep the total under 100.
