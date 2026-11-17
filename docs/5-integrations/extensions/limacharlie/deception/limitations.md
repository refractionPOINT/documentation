# Deception: Known Limitations

Read this page before you rely on Deception. Items marked **not verified** have not been confirmed on real hosts or tenants.

## Not built

- **Real AWS keys** from a key source (your own decoy AWS account, or a LimaCharlie-operated pool). The `key_sources` field must be empty. AWS decoys use fake keys against a fake AWS endpoint.
- **Bring-your-own decoy domains.** `custom_domains` is validated and stored, but no decoy uses it yet.
- **Raw TCP decoys** (SSH, databases, RDP), **decoy email messages**, **LimaCharlie-operated DNS**, registry decoys, honeyports and decoys inside containers.
- **Starting an AI triage session** from the extension (`respond` with `ai_triage`, `responses.start_ai`). Use a `start ai agent` response in your own rule.
- **Declaring your own AI agents** so their reads get the lower-priority label. The `sanctioned-agent-touched-decoy` label and its rule exist but never apply.
- **Listing and approving learned readers.** See [Learning window](configuration.md#learning-window).
- **Classification by decoy-touch rate** (how many decoys one process or address touched within a minute), and joining a file read to its process start by itself.
- **Alerts for a quiet source or a broken path.** These appear in `coverage` only.
- **Kubernetes DaemonSet sensors.** They cannot place decoys on the node and show as not covered. Sensors installed on the node itself are covered.

## Sensor and platform limits

- Sensors in `lc:response` or `lc:sleeper` mode get no decoys. Sensors in `lc:epp` or performance mode get use-only decoys, and only once verified. The extension never changes a sensor's mode.
- The sensor's file-read event (`FILE_READ`) is reported once per file each time a different process reads it on Windows, and never for the process that created the file. On macOS every open counts as a read, including opens for writing. On Linux an open for read-write is reported as a modification, which the extension treats as a hit.
- The Linux file collector has no in-kernel path filter and can drop records silently under load, so on a busy server a decoy read can be missed.
- Linux paths are not normalized by the sensor (`./`, `..`, symlinks and separate mounts change the reported string), so read matching uses the decoy's generated file name, not its full path. This is why Linux and macOS templates use generated file names.
- A sensor keeps at most 100 Exfil watch rules, shared with everything else you collect. See [Watch-rule budget](decoys.md#watch-rule-budget).
- DNS lookups: Windows sensors report failed lookups. Linux and macOS report a lookup only if the name resolves. Decoy hostnames under your internal domain are therefore caught on Windows only.
- The command-line fallback rule sees an argument vector truncated at 511 bytes on Linux eBPF sensors.
- Placement needs an existing directory. A template whose directory is missing on a host is skipped there.
- Supported architectures are x86-64 and ARM64. Other architectures are not covered.

## Log source limits

- **Not verified:** that Entra ID, Okta and domain controllers each log sign-in attempts for non-existent usernames in a form the extension can match. Google Workspace is not a supported source.
- Entra ID sign-in logs need Entra ID P1 or P2.
- A failed logon is recorded on the domain controller that answers it. A sensor is needed on every domain controller, and failure auditing must be on. The failed logon recorded on the member machine itself is not collected.
- Domain controller collection streams successful logons too, since the `wel://` collection filters by event ID only. That adds ingestion volume that grows with your logon rate. This is why it is opt-in per policy.

## Detection limits

- **A decoy used outside LimaCharlie's view is not caught.** An attacker who copies decoy keys to another machine and uses them against the real service gets an invalid-credentials answer and you see nothing. The file read on the original host is still caught.
- **Residual risk in recognizing the extension's own file traffic (documented).** The extension's placement helper touches decoys, and those file events must not alert. It recognizes its own helper through the process that the sensor reports starting it, and grants silence only when the whole launch chain verifies and exactly one process claims the run. No sensor event carries the sensor's own process id, so the extension cannot check that the launcher's parent is the very sensor process reporting for that host. An attacker who runs the genuine sensor binary separately, holds the live per-attempt nonce from the helper's command line, and whose process start is the only claim for that attempt, can have their own reads of that one decoy suppressed during that one attempt, at most 64 seconds of sensor time. The genuine helper's reads then alert instead. If the genuine helper's own event also arrives, two claimants exist and nobody owns the attempt, so nothing is suppressed. Every other decoy, attempt and event is judged normally. If the chain cannot be verified, the extension's own traffic alerts: a false alert is accepted, a suppressed attacker read is not.
- **The 72-hour learning window drops reads**, including an attacker's, when the process's image path is known. See [Learning window](configuration.md#learning-window).
- **Alert latency.** No latency measurements exist for read alerts. Cloud sign-in logs add their own delay. A file event held while the extension decides whether its own helper caused it waits at most about 40 minutes. See [Alert latency](detections.md#alert-latency).
- **Hit delivery is deduplicated per process only.** A redelivered hit handled by another instance can be sent twice. It carries the same `hit_id` and case grouping key, so it does not open a second case.
- Hits from the collector carry no hostname (the collector path has no organization credential to look the sensor up). `sid` is set.

## Security limits

- **The placement helper is not code-signed.** The extension ships a small static program per operating system and architecture and runs it on the host by absolute path. Endpoint protection products or application control policies on the host may flag or block an unsigned binary. **Not verified** against any specific product. Allow it by its hash if needed. No signed build exists.
- **A user with read access to your organization can learn some decoys** from detections, the files on disk, placement payloads and events. Generated secrets are never returned by a request or written to a readable record.
- Decoy file names and the fake services' host labels are generated per organization so defaults are not a public list, but a determined attacker who has seen decoys in your environment can learn your names. `rotate` replaces secrets.
- The extension checks a decoy's contents by hash and never rewrites a changed decoy, so an attacker who edits a decoy causes a `modify` hit and a retired instance, not a silent overwrite.

## Lifecycle limits

- A reconcile that is paused between its lifecycle check and its write can recreate a rule after cleanup removed it, and a cleanup can overlap a new subscription's setup. Closing this needs a stored per-organization lifecycle lease. The next `deploy` or daily run converges the state, and your own `cancel` repairs a cleanup that overreached.
- If the platform loses the subscribe event of a re-subscribe, the organization stays inactive (nothing alerts) until its stored data is purged and a later update sets it up fresh. An update never reactivates an organization the extension saw unsubscribe.
- Final cleanup mutations the platform already received when a cleanup lease ended cannot be recalled, and can still delete a rule, entry, tag, payload, key or the adapter that a newer owner or a `cancel` had restored. Repair it with `cancel`, `deploy`, or the next daily run. Nothing is lost permanently.
- Test-fire history is bounded (see [Test-fire](detections.md#test-fire)).
