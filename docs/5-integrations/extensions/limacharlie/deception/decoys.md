# Deception: Decoys and Coverage

## Decoy kinds

A **kind** is a mechanism built into the extension: how a decoy is placed, how a hit on it is detected, and what it needs from your organization. A **template** is data: one concrete decoy of a kind. Most new decoys are a new template of an existing kind, and you can write them yourself. Run `list_kinds` for each kind's version and JSON schema of its settings.

| Kind | What it plants | Alerts |
| --- | --- | --- |
| `file` | A credential file, service configuration or note on the endpoint. Secrets inside point at LimaCharlie's collector. | read, modify, delete (sensor); use (collector) |
| `hostname` | A file (inventory note, FTP/SFTP client config) naming decoy hostnames. Registry form: names under LimaCharlie-operated decoy domains. Internal form (names under your own internal domain): **not available in this release**, see below. | read, modify, delete (sensor); use (DNS lookup seen by the sensor, request on the collector) |
| `phantom_account` | A file naming a username that exists nowhere, with a fake password. UPN form (`user@domain`) for Entra ID or Okta. The AD form (`DOMAIN\user`) is **not available in this release**. | read, modify, delete (sensor); use (failed sign-in in your logs) |
| `document` | A generated Word (`docx`) or SVG (`svg`) document whose linked image is on the collector. | read, modify, delete (sensor); use (the document opened in a viewer that loads the image, see [Documents](drops.md#documents)) |

Decoys that no sensor places (a link, a QR code, a host name or a document you put in a wiki, a ticket or an email) are [tokens](drops.md).

### Alert layers

Every hit carries a `layer`:

| Layer | Meaning | Default rule |
| --- | --- | --- |
| `read` | The decoy file was opened, or its path appeared on a command line. | Priority 10 |
| `modify` | The decoy file was modified. | Priority 10 |
| `delete` | The decoy file was deleted unexpectedly. The decoy is planted again afterward. | Priority 5, never isolates |
| `use` | A secret inside the decoy was used, or a document decoy was opened. | Priority 10 |

Priority 10 applies to the default rules, which you can edit. While a policy is in [observe mode](configuration.md#observe-mode), its read and modify hits are priority 2 instead, with no automatic response; its use hits stay priority 10. A `use` hit that arrives from the collector or a sign-in log never isolates the host, by design, even when the secret is used from the original host: a network address is not proof of which machine used the secret. Only an event reported by the decoy's own sensor can isolate (see [Isolation](detections.md#isolation)). That is a read, a modification, a command-line match, or, for a `hostname` decoy, the DNS lookup of a decoy name reported by the sensor of the host the decoy was planted on, which is a `use` hit with on-host evidence. All of them are subject to the usual guards.

A modification counts as a hit because on Linux an open for read-write is reported by the sensor as a modification, not a read. An unexpected delete is more often cleanup than an attack, so it gets a lower priority.

### One access, one hit

One access to a decoy raises one alert, even when the sensor reports it in several ways:

- A shell that names the decoy on its command line and then reads it (for example `type <decoy>`) is one hit, not a command-line hit plus a file-read hit.
- A launcher shell and the shell it starts, which both carry the decoy path, are one hit.

The events must come from the same process lineage (a process and its parent or child), on the same decoy and layer, within 30 seconds of each other by the sensor's clock. Two file-read events never collapse directly into each other, and neither do different processes that merely share a parent, different decoys or different layers. The extension cannot tell separate reads from one access by the same process, though: within the 30-second window, several reads by a process that started the access can join that process's hit. A chain of three processes whose events arrive with the middle one last can still leave two hits.

### The extension's own reads never alert

Placing and verifying a decoy makes the sensor read the file itself, and the placement helper touches it too. Neither raises a hit. The extension does not trust a path, a parent process or a start event to tell the sensor from an attacker's process, because a local administrator can fake all three. When a read by a process it does not know falls inside one of its own operations on that decoy, it holds the read and asks the sensor, with tasks it already sends (`get_debug_data`, `os_processes`), which process is the sensor itself: the sensor reports its own process id, and the read is the sensor's only when that id and the process holding it match the reader. Any other answer, or no answer, makes the read a real hit. A console or API `file_hash` of a decoy outside the extension's own operations alerts like any other read. The delay this adds is described under [Alert latency](detections.md#alert-latency).

## Default template library

The library is built into the extension and ships with each release, so a newer release can add or improve templates. `list_kinds` returns it in its `library` field, and the **Templates** tab of the web app shows it under **Add from library**. Adding a template copies it into your organization's configuration: the copy is yours to edit, and the library itself never changes. The library entries are starting points for your own templates. Nothing in the library is placed until you copy a template into your configuration and a policy selects it.

| Template | Kind | Platforms | What it imitates |
| --- | --- | --- | --- |
| `aws-config-backup` | file | Linux, macOS, Windows | A saved AWS CLI config with a decoy profile whose `endpoint_url` points at the collector. Use is caught when the file is passed with `AWS_CONFIG_FILE` and its profile is selected with `--profile` or `AWS_PROFILE`. |
| `aws-credentials-backup` | file | Linux, macOS, Windows | A saved AWS credentials file whose profile carries `endpoint_url`, so the key goes to the collector when the file is used: pass it with `AWS_SHARED_CREDENTIALS_FILE` and select its generated profile with `--profile` or `AWS_PROFILE` (the profile is named, not `default`). No separate config file is needed. Verified clients: botocore-based ones (AWS CLI, boto3), which read `endpoint_url` from the credentials file. Other SDKs, and endpoint overrides in general, are **not verified**. |
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
| `win-web-config` | file | Windows | A leftover IIS `web.config` with an API base URL and key on the collector, under a generated folder. It has no database connection string. |
| `mysql-dump-backup` | file | Linux, macOS, Windows | A `mysqldump` of an application database in a backup folder: a planted account and password hash, and a settings row naming a sign-in portal on the collector with that account's password. A sign-in with it is a use hit. Nothing listens for MySQL itself. |
| `svn-auth-cache` | file | Linux, macOS, Windows | A leftover copy of a Subversion credential cache entry for a repository server on the collector. Using the credential (`svn ls <url> --username … --password …`) is a use hit. |
| `doc-network-passwords-docx`, `doc-vpn-setup-docx` | document | Windows, macOS | A Word note of office Wi-Fi and router logins, and of a VPN setup, in a folder of the user's documents. Opening it in Word, on the host or after it was copied off, is a use hit. |
| `doc-network-diagram-svg` | document | Linux, macOS, Windows | An SVG network diagram in the user's documents. Opening it in a browser is a use hit. A file-share and desktop decoy, not one to mail. |
| `hostname-registry-inventory` | hostname | Linux, macOS, Windows | An inventory note naming decoy hosts under a decoy domain |
| `hostname-internal-inventory` | hostname | Windows | An inventory note naming decoy hosts under your internal domain. **Not available in this release**: every alert layer reports unavailable and nothing is planted. |
| `win-filezilla-sitemanager`, `win-winscp-ini` | hostname | Windows | FileZilla and WinSCP site lists naming decoy hosts |
| `win-desktop-ini-folder` | hostname | Windows | **Opt-in.** A generated System folder whose `desktop.ini` icon is on a decoy host that does not resolve. Showing the folder in Explorer (browsing its parent) makes Windows look the host up, and the sensor reports the lookup as a use hit. Windows stops at the failed lookup: it never connects and never offers a login. Fires for anyone who browses the parent folder, the machine's own user included, and never for a shell, so it suits hosts nobody browses and interactive (RDP) intruders. |
| `phantom-upn-credentials` | phantom_account | Linux, macOS, Windows | A note with a phantom cloud account |
| `phantom-ad-credentials`, `win-groups-xml`, `win-unattend-xml` | phantom_account | Windows | A note, a Group Policy Preferences `Groups.xml` and an `unattend.xml` with a phantom AD account. **Not available in this release**: every alert layer reports unavailable and nothing is planted. |

The service names a decoy uses (for example the fake Kubernetes API or fake AWS API) are per-organization labels under the decoy domains. Names written inside decoy files (clusters, users, folders, hosts) come from the same per-organization vocabulary. Nothing on the collector's public side names LimaCharlie, and a template whose content mentions `limacharlie` is rejected.

## What the collector answers

Decoy secrets that carry their own destination point at a public collector that answers like the real service, so the attacker keeps going and the extension learns more. It serves a fake Kubernetes API, a fake AWS API (including STS identity, S3 listings and Secrets Manager), web logins and JSON APIs (SSO login, Grafana, Jenkins, Vault), a fake MCP server (a tool call is the hit, connecting and listing tools is not), a git server, and npm and PyPI registries. Its answers are derived per organization, from a private key that only LimaCharlie holds: the fake MCP server's name and tools, bucket and secret names, identities and pages differ in every organization, and a fake host label belongs to one fake application, so every path, link and redirect on it answers like that application. A decoy login session carries the lifetime the fake service advertises and expires on it (for example a Vault login 32 days, a Grafana cookie 30 days, a Jenkins session 30 minutes, a portal session 12 hours; package registry tokens do not expire). An expired session authenticates nobody, but is still attributed to the decoy it came from. It records the source IP, User-Agent, an allowlist of headers and the token. The collector holds no organization credential. It only forwards what it receives, and the extension decides whether it is a real hit by looking the token up in its registry.

## File names and paths

- File names come from a vocabulary generated once per organization and never regenerated. A template refers to a vocabulary entry such as `{{vocab "kubeconfig_backup"}}`.
- Templates that use a generated file name work on Linux, macOS and Windows. A template with a fixed file name (`web.config`, `Groups.xml`, `unattend.xml`, `WinSCP.ini`, `sitemanager.xml`) is Windows-only and must sit under a generated folder. A bare common file name is never used as a match rule.
- A template whose folder has a fixed name (for example `~/.aws` or `~/.kube`) is placed only where that folder already exists. If it is missing on a host, the template is **skipped on purpose** there: the Decoys tab shows it as "Folder not on host" (cause `directory_missing`), and it is not a fault. Nothing is broken, and the host's status is not lowered by it (see [Host status](#host-status)). The extension never creates a folder that other software owns, such as `~/.aws` or `~/.kube`, because a lone one would look planted. If the software is not on the host, do nothing. Otherwise check that the folder exists, or add a template whose folder exists there. The host is checked again by an explicit `deploy` (at most once every 10 minutes per target), by the next [rollout](operations.md#rollouts) round, and by the daily run's [retry of failed placements](#failed-decoys), which backs off after repeated misses.
- A template whose folder has a generated name (an ops or backup folder, a generated Windows web folder) is placed in a folder the host does not have, so the extension creates the generated levels itself. It never creates a folder that already exists, never follows a symbolic link or reparse point, and gives the folder a normal folder's permissions (POSIX `0755`, owned by the decoy's owner; on Windows it inherits the parent's ACL). It records each folder it made, and removes it again when the last decoy in it is removed (retire, rotate or uninstall), only if it is still the folder it made and holds nothing but the extension's decoy. A folder with anything else in it stays, and the removed decoy's reason says so.
- It never overwrites a file it did not create. If something already exists at the path, placement fails as `path in use` and is reported. A decoy whose contents changed is retired, never rewritten.
- Placement goes only at paths that look like leftovers (for example `~/.kube/config.prod-old`, `~/backup/aws-credentials`), never at a tool's default path. A template can name separate directories for Linux hosts with no human users (`linux-server`), such as `/root` or `/opt`.

## Platforms

The extension places decoys on Windows, Linux and macOS sensors. The placement helper is built for x86-64 and ARM64 on each. Other architectures are not supported.

A template declares its platforms. The planner skips a host whose platform a template does not list, a host where the tool the template imitates is absent (`requires_packages`, `requires_files`), and a host where a fixed-name target folder does not exist. A folder with a generated name is created by the extension (see [File names and paths](#file-names-and-paths)).

## Sensor modes and what they cost

The extension never changes a sensor's mode. It plans around it:

| Sensor | Placement | Read / modify / delete alerts | Use alerts |
| --- | --- | --- | --- |
| Normal mode | Yes | Yes | Yes |
| `lc:epp` or performance mode | Yes | **No.** These modes drop the file collectors. | Yes. Decoys here are use-only, and count as covered only once verified. |
| `lc:response` | **No.** `put` and `run` are disabled. | Not covered | Not covered |
| `lc:sleeper` | **No.** The sensor runs nothing. | Not covered | Not covered |
| Kubernetes DaemonSet sensor | **No.** It sees the node through a read-only mount and writes only inside its own container. | Not covered | Not covered |

A sensor in one of the excluded modes, and a Kubernetes DaemonSet sensor, gets no decoys (a sensor in `lc:epp` or performance mode gets use-only decoys). The extension works this out per sensor while it plans, and `list_hosts` shows the result per host: a targeted sensor that nothing can be placed on has the status `no_decoy` and a `rollout` outcome of `blocked` with the reason (`host_daemonset`, `host_sleeper_mode`, `host_response_mode`, `host_cloud_sensor`: see [Host status](#host-status)). `plan` gives counts per policy (sensors targeted, placed, to place, to retire), the missing requirements per policy and a list of issues. `coverage` is an organization-level view of each template and layer: it does not list hosts, and an `active` status is not proof that every selected host is covered. To see which sensors have decoys, use `list_hosts` or the **Decoys** tab: a targeted sensor with no decoy is a `no_decoy` row. Kubernetes nodes that run the sensor installed on the node itself are covered. Decoys inside containers are not supported.

On Linux, read alerts need the eBPF-capable sensor. The extension checks the sensor mode only, not the Linux tier: whether a legacy (non-eBPF) Linux sensor raises read alerts is **not verified**.

## Sensor versions (Windows)

Read, modify and delete alerts come from the sensor's file events. Windows sensors from 5.2.2 up to 5.3.15, and from 5.4.0 to 5.4.2, stop reporting file events after their first `ext-exfil` update while still looking healthy, so those three alerts can never fire on them. Use sensor **5.3.16 or later** on the 5.3 line, or **5.4.3 or later**. The use alert is not affected. A Windows sensor whose kernel acquisition is not running reports no file events either, and is handled the same way.

The extension reads the version from the sensor itself (`get_debug_data`) during the daily inventory, so nothing depends on what you tell it. On an affected sensor:

- The read, modify and delete alerts cannot work there, so a decoy placed on that sensor carries only the layers that can (check a decoy's `layers` in `list`), and a template whose only alert is read is not placed there. The extension treats this as "unavailable on that sensor" and never as `broken`. It works this out per sensor, and no request returns this one per sensor today: neither the organization-level `coverage` request nor `list_hosts` carries sensor versions.
- `test_fire` places its test decoy for the read and modify paths only on a sensor that reports file events (the use path does not need them), and says that a path was not tested when it finds none. A test decoy already on an affected sensor is left alone.

When the version could not be read, the extension keeps the host's behavior: it places and watches as usual, and does not confirm that file events arrive. Linux and macOS sensors are not checked this way.

## What each decoy needs from the organization

| Decoy | Needs | Without it |
| --- | --- | --- |
| File decoys, placement | `ext-artifact` subscribed, a supported sensor | Placement is Unavailable for the whole organization, with "Subscribe ext-artifact". |
| File decoys, read alert | `ext-exfil` subscribed, file collectors on, and on Windows a sensor that [reports file events](#sensor-versions-windows) | Each layer is judged on its own. A template that also alerts on use is still planted: the read layer shows `partial`, and use is caught (plus modify and delete when `ext-integrity` is subscribed). A template whose only alert is read has three layers (read, modify, delete): it is planted as long as at least one of them works, for example with `ext-integrity` subscribed and `ext-exfil` missing, when only modify and delete are caught. It is not planted, and shows `unavailable`, only when none of its layers can work. |
| File decoys, modify and delete alerts | `ext-integrity` subscribed, file collectors on | The modify and delete layers show `partial` or `unavailable` in the same way. Losing `ext-integrity` does not remove the read layer, which depends on `ext-exfil`. |
| File, MCP and registry-hostname decoys, use alert | Nothing else | Always available. |
| Document decoys | The same as file decoys for placement and the read, modify and delete alerts. The opened (use) alert needs nothing else. | As for file decoys. |
| [Tokens](drops.md) | Nothing: no sensor and no other extension. | Always available. |
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

**Template tags.** The read, modify and delete alerts of a template reach a sensor only while it carries the template's tag (see [Per-host watch rules](#per-host-watch-rules)). `coverage` checks this for verified decoys. When some of the sensors holding a verified decoy of a template lack its tag, the item's note says how many, and `coverage.tag_gaps` lists `{policy, template, verified_sensors, untagged_sensors}`. When none of them carries it, an `active` item becomes `partial` with the missing requirement `template-tag`. A `deploy` or the daily run adds the missing tags, and the gaps then go away on their own. At most 25 templates are checked per request, within a time budget: past that, `coverage.tag_check_note` says the tags were not all checked, and no gap listed is not proof that there is none. The `use` layer does not depend on the tag.

**Lower bounds.** Counts of verified, pending and failed decoys are read from the registry in bounded pages. On a very large organization they are lower bounds, and the item's note says so.

**Tokens.** The top-level `drops` of the `coverage` answer has one row per token form your organization uses: `active`, `broken` or `unverified`. See [Testing and coverage](drops.md#testing-and-coverage).

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

## Host status

A host's status says whether it holds a decoy to touch. It is judged over the host's decoys that match the filters you are looking at (test decoys only with `include_test`), and over **current** failures only (see [Failed decoys](#failed-decoys)).

| Status | Meaning |
| --- | --- |
| `protected` | At least one decoy on the host is verified, and none of the decoys its policies want there is missing because of a fault. A decoy [skipped on purpose](#file-names-and-paths) does not count against it: such a host reads protected, with a "skipped" note. |
| `partial` | A decoy is verified, but another decoy the host's policy wants is missing: it has a current failure, or its template was added to the policy after the host's last planning pass (the host's `to_place` names it, for example because the host was offline when the rollout reached it). A host is never `protected` while something it should hold is missing. |
| `pending` | Decoys are planned or placed, and none is verified yet. |
| `failed` | No live decoy, and at least one decoy failed with a fault: nothing protects the host. |
| `skipped` | The host has no live decoy, no decoy failed with a fault, and the decoys that did not go on it were skipped on purpose, for example because the folder its templates need does not exist. Nothing is wrong and nothing needs fixing. |
| `no_decoy` | A policy targets the host and no decoy is placed on it yet (nothing planned, or the host was offline or blocked when the rollout reached it). The last rollout visit says why. |
| `none` | Only retired or removed decoys. |

`list_hosts` lists **every targeted host**, with or without a decoy, so "which hosts are not protected" has an answer: a targeted host with nothing placed is a `no_decoy` row, not a missing one. Each row carries `rollout`, the outcome of the last rollout visit to that host (`offline`, `blocked` with the reason, `inventory`, `planned`, `nothing_planned` or `failed`), the policies that targeted it and when, so you can tell an offline host from one nothing can be placed on (a cloud sensor, a Kubernetes DaemonSet sensor, a sensor in sleeper or response mode). It is the state at that visit, not live. A host appears once a rollout round has visited it: while the first round runs, the response says how many targeted sensors it has not reached yet.

The web app shows this in **Decoys** > **View: Hosts**, with a count per status, and on the sensor's own **Overview** page. The Overview tab's **Hosts protected: N of M targeted** counts the hosts with a verified decoy out of the hosts your enabled policies target, and says how many have failed, are being placed, were offline at the last rollout, or have no decoy yet. A host number that is a lower bound reads "at least". `coverage` also returns the organization's host counts as `sensors` (hosts targeted, and hosts holding a placed or verified decoy: see [`coverage`](requests.md#coverage)).

## Failed decoys

The failed view lists what is **not protected now**, not every attempt that ever failed. A failed decoy is current while no other decoy of the same template on that sensor is live (planned, placed or verified), and no later attempt was made at the same path. So there is one row per host, template and path, the latest attempt, and none while a live decoy of that template is on the host: a start failure from before a fix does not sit next to the verified decoy that replaced it, and a container that retried a missing folder five times shows one row. The failed filter, the cause filter, the summary, the host counts and the host status all use current failures. Earlier attempts are not deleted: `include_superseded` on `list` and `list_hosts` brings them back, and a failed decoy still expires after its retention period. A decoy skipped on purpose is a failed record with the cause `directory_missing` and is flagged `skipped`; it is counted apart from faults everywhere (see [`list`](requests.md#list)).

A test decoy of a policy no longer stands in for the real one: a sensor that held a test decoy of a template is still given the real decoy.

**The daily run retries a failed placement.** A placement that failed for a transient reason (a start failure, a timeout, a task that was not sent) used to wait for the next rollout round: a configuration change, a deploy, or the weekly recheck. The daily run now walks the organization's sensors with a current failure, first in the run and under a time budget of its own, and deploys a sensor again when it is online and not a cloud sensor, an enabled policy that targets it selects the failed template, and the failure is due: its newest failed attempt at that target is at least 6 hours old, and it has failed fewer than three times in a row there, or the newest failure is a week old. A run retries a sensor at most once, so with one run a day a template is retried on three runs in a row (each at least 6 hours after the last failure), then at most once a week; a template that does reach the host starts over. The retry deploys the whole sensor, so it counts against every template with a current failure there. A run retries at most 200 sensors and 10 deploys, continues where it stopped the next day, and never retries test decoys or a failure caused by the organization being unsubscribed. A sensor that is offline costs nothing and is not retried until it is online. While a rollout round is under way the round itself visits every sensor, so the retry step does not run. The run reports "N sensors whose last placement of a wanted decoy failed were deployed again".

**What `coverage` says about skips.** A skip is not a failed placement. The note "N placements failed" counts faults only, and the skips are noted apart ("skipped on N sensors where the template's folder does not exist"), with `skipped_sensors` on the item. A path that has no verified decoy is still `partial`, because nothing there can alert yet, and when skips are all that is missing, its one missing requirement is `decoy-skipped`: nothing to fix.

## New and short-lived sensors

A policy with `setup_on_new_sensors: true` places decoys when a matching sensor first connects, without waiting for the daily run. The policy matches by sensor tags, so tags applied by the installation key at enrollment work. Placement only tasks a sensor that is online. The daily reconcile compares the registry with the sensor list: a sensor that is gone has its placement state dropped, but its tokens stay in the registry for a retention period, so a credential stolen from a node that no longer exists is still caught when used, and the hit names the original host.

A clone of a sensor carries the source host's decoy files at the template paths, so it gets no decoys of its own for those templates (they are skipped as `path in use`), and no template tags for them either. The copies on a clone alert on use and through the command-line rule, not on a plain file read (see [Copied decoys](#copied-decoys)).

## Per-host watch rules

Read, modify and delete alerts come from rules the extension writes in `ext-exfil` (watch rules, for reads) and `ext-integrity` (FIM rules, for modifications and deletions). Those rules reach only the sensors that hold a decoy of their template, so a sensor's rules grow with what is on that host, never with the number of templates or sensors in the organization:

- While a sensor holds a decoy of a template, the extension puts a tag named `deception-t-` followed by 16 hexadecimal characters on it (one tag per template; the name comes from a hash of the template's name). The tag goes on before the first decoy of the template is placed and comes off with the last one.
- The template's watch and FIM rules are filtered by that tag and by the platforms of the policies that select the template. Your policy's targeting tags decide where decoys go; they are not part of these rules.
- A `deploy`, a rollout, and the daily run put back a template tag that is missing on a sensor holding its decoy. The daily run also removes template tags that no decoy accounts for. Do not remove `deception-t-` tags yourself: a sensor without the tag stops reporting reads, modifications and deletions of that template's decoys until the tag is back (use alerts and the command-line rule keep working), and `coverage` reports it as a [tag gap](#coverage-statuses).
- A sensor reloads its watch and FIM rules about every 5 minutes, not when a tag changes. A plain read or modification in the first minutes after the first decoy of a template lands on a host can therefore be missed. The command-line rule and use alerts are not affected.
- The platform keeps at most 256 tags per sensor and silently ignores a tag past that. On a sensor already at that limit a decoy is placed, but its read, modify and delete rules never reach it.

### Copied decoys

A decoy copied to another host is caught there by its use, which names the host it was planted on, and by the command-line rule when a command names the file. A plain read or modification of the copy is not caught on a host that holds no decoy of that template, because no watch or FIM rule reaches that host.

## Watch-rule budget

A sensor keeps at most 100 Exfil watch rules, shared with everything else you collect on it. A template's read alert costs a sensor one watch rule per file-name pattern it watches, and only on sensors that hold a decoy of that template. So the cost on a host is the sum over the templates it holds, not over the organization.

`plan` returns `watch_budget` per sensor, over the sensors it planned in detail (at most 100): the busiest of them (`sid`, the rules the extension `owned`, your own `customer` rules that reach it, the `total`, and `at_risk`: the names of the newest rules that sensor would drop past the limit), plus `over` and up to 20 `over_sensors`. It counts the templates the sensor holds or would get from this plan, so it is an estimate for that sample, not a check of every sensor. The **Coverage** tab shows the same figure under **Exfil watch rules**. Whether the extension's own rules sort ahead of yours on a sensor depends on `ext-exfil` behavior that is **not verified** here, so keep each sensor under 100.
