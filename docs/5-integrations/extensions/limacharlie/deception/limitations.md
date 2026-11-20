# Deception: Known Limitations

Read this page before you rely on Deception. Items marked **not verified** have not been confirmed on real hosts or tenants.

## Not built

- **Real AWS keys** from a key source (your own decoy AWS account, or a LimaCharlie-operated pool). The `key_sources` field must be empty. AWS decoys use fake keys against a fake AWS endpoint.
- **Hostname decoys under your internal domain.** Deferred to a later release. `hostname-internal-inventory` and the internal form of the `hostname` kind report every alert layer as unavailable ("not available in this release"), in `plan`, `coverage` and `test_fire`, and nothing is planted, forwarded or collected for them.
- **Fake Active Directory accounts** (`phantom-ad-credentials`, `win-groups-xml`, `win-unattend-xml`, and the `ad` form of `phantom_account`). Deferred to a later release, with the same behavior: every layer reports unavailable and nothing is planted. The policy field `dc_logon_collection` is accepted for compatibility and ignored: no domain controller is tagged and no Windows event collection is installed.
- **Alerts on a successful sign-in under a phantom cloud account.** Deferred to a later release. Failed sign-ins against a phantom account still alert.
- **Bring-your-own decoy domains.** `custom_domains` is validated and stored, but no decoy uses it yet.
- **Raw TCP decoys** (SSH, databases, RDP), **decoy email messages**, **LimaCharlie-operated DNS**, registry decoys, honeyports and decoys inside containers.
- **Starting an AI triage session** from the extension (`respond` with `ai_triage`, `responses.start_ai`). Use a `start ai agent` response in your own rule.
- **Declaring your own AI agents** so their reads get the lower-priority label. The `sanctioned-agent-touched-decoy` label and its rule exist but never apply.
- **Listing and approving learned readers.** See [Learning window](configuration.md#learning-window).
- **Classification by decoy-touch rate** (how many decoys one process or address touched within a minute), and joining a file read to its process start by itself.
- **Alerts for a quiet source or a broken path.** A broken path appears in `coverage` only. The quiet-source (`blind`) status is never set: the platform does not report when an adapter last delivered data, so the extension cannot tell. The most it offers is an informational "no sign-in observed in N hours" note on the affected coverage items. Monitor the health of your Entra ID and Okta sign-in sources independently.
- **Retiring a phantom account that becomes real.** A successful sign-in does not retire a phantom account, because successful sign-ins are not observed. If a planted name becomes a real account, remove or rotate the decoy yourself.
- **Kubernetes DaemonSet sensors.** They cannot place decoys on the node and show as not covered in `plan`. Sensors installed on the node itself are covered.

## Design choices that limit automation

- **Isolation rests only on an event from the decoy's own sensor.** A hit that arrives through the collector, and a sign-in hit, never isolate a host, even when the secret is used from the decoy's own host. A source address is not proof of a machine (NAT, DHCP churn, VPNs, shared cloud egress, an offline sensor's last address), and a wrong guess isolates the wrong host. These hits still raise the priority 10 detection and can open a case. See [Isolation](detections.md#isolation).
- **A change to a shipped rule is never judged.** If you edit a shipped detection rule, the extension reports it as `unverified (rule edited: <rule>)` instead of working or broken. It does not evaluate your rule. See [Rule integrity](decoys.md#rule-integrity).

## Sensor and platform limits

- **Windows sensors that do not report file events.** Sensors 5.2.2 to 5.3.15 and 5.4.0 to 5.4.2 stop reporting file events after their first `ext-exfil` update, so read, modify and delete alerts cannot fire on them. Use 5.3.16 or later on the 5.3 line, or 5.4.3 or later. The extension reads the version from the sensor and reports those alerts as unavailable on that sensor, not broken; when the version could not be read it says the version is unknown and keeps the host's behavior. The use alert is not affected. See [Sensor versions](decoys.md#sensor-versions-windows).
- Sensors in `lc:response` or `lc:sleeper` mode get no decoys. Sensors in `lc:epp` or performance mode get use-only decoys, and only once verified. The extension never changes a sensor's mode.
- The sensor's file-read event (`FILE_READ`) is reported once per file each time a different process reads it on Windows, and never for the process that created the file. On macOS every open counts as a read, including opens for writing. On Linux an open for read-write is reported as a modification, which the extension treats as a hit.
- The Linux file collector has no in-kernel path filter and can drop records silently under load, so on a busy server a decoy read can be missed.
- Linux paths are not normalized by the sensor (`./`, `..`, symlinks and separate mounts change the reported string), so read matching uses the decoy's generated file name, not its full path. This is why Linux and macOS templates use generated file names.
- A sensor keeps at most 100 Exfil watch rules, shared with everything else you collect. See [Watch-rule budget](decoys.md#watch-rule-budget).
- DNS lookups: Windows sensors report failed lookups. Linux and macOS report a lookup only if the name resolves.
- The command-line fallback rule sees an argument vector truncated at 511 bytes on Linux eBPF sensors.
- A template with a fixed folder (such as `~/.aws` or `~/.kube`) needs that folder to exist. Where it is missing the template is skipped, and shown as `directory missing`. The extension creates only the folders a template names with a generated name, and removes them again with the last decoy in them; a folder that holds anything else stays.
- Supported architectures are x86-64 and ARM64. Other architectures are not covered.

## Log source limits

- **Not verified:** that Entra ID and Okta each log sign-in attempts for non-existent usernames in a form the extension can match. Google Workspace is not a supported source.
- **Not verified:** that every Okta adapter reports the platform name `okta`. The extension observes an Okta feed (for the quiet-feed note) only when it does, and a feed registered under another platform name, such as `json`, is not observed.
- Entra ID sign-in logs need Entra ID P1 or P2.

## Detection limits

- **A test result is final about an hour after the run starts.** A run's detection can be held while the extension decides whether its own helper caused it, so `list_test_runs` shows the run as pending, with the time its outcome is due, until then. See [Test-fire](detections.md#test-fire).
- **Test-fire checks the synthetic detection path only.** It uses the `deception-test` rule. It does not prove that the real-alert rules, cases or isolation work. A coverage `broken` status comes from that test path, or from a shipped alert rule that is missing or disabled; an edited rule reads `unverified`. Rule comments and UI shortcuts are not part of the comparison.
- **`coverage` is organization-level.** Per-host exclusions (sensor mode, Kubernetes DaemonSet sensors) show in `plan`. An `active` status does not prove every selected host is covered.
- **Coverage warnings are events, not records.** `deception_coverage_warning` events are not returned by `list` or `coverage`.

- **A decoy used outside LimaCharlie's view is not caught.** An attacker who copies decoy keys to another machine and uses them against the real service gets an invalid-credentials answer and you see nothing. The file read on the original host is still caught.
- **Residual risk in recognizing the extension's own file traffic (documented).** The extension's placement helper, and the sensor when it hashes a freshly placed file, touch decoys, and those file events must not alert. The extension recognizes its own helper only through the helper's verified launch chain, and the sensor only by asking the sensor for its own process id (see [The extension's own reads never alert](decoys.md#the-extensions-own-reads-never-alert)). It stays silent only for events inside one short run of that helper, or while it is working on that very decoy. In that narrow window an attacker with local code execution could cause one read of that one decoy to be treated as the extension's own activity. All other decoys, all later reads and all use alerts are unaffected. If the helper or the sensor cannot be verified, the read alerts: a false alert is accepted, a suppressed attacker read is not. Until the plumbing rules have converged after an upgrade (the next `deploy`, configuration update or daily run), the extension's own reads are not recognized and may alert.
- **The 72-hour learning window drops reads**, including an attacker's, when the process's image path is known. See [Learning window](configuration.md#learning-window).
- **Alert latency.** No latency measurements exist for read alerts. Cloud sign-in logs add their own delay. A file event held while the extension decides whether its own helper caused it waits about 40 minutes in the nominal case (no backlog, no failures), and longer under backlog or retries. See [Alert latency](detections.md#alert-latency).
- **Hit delivery can duplicate in two narrow cases.** A hit is delivered once across instances, except when the adapter accepted it but the acknowledgement was lost, or the extension stopped right after the adapter accepted it. The duplicate carries the same `hit_id` and case grouping key, and never isolates twice. The platform does not drop it, so a rule reports it twice. Deduplicate on `hit_id` if you need exactly-once. How `ext-cases` treats the second detection is **not verified**.
- A collector hit's hostname is the one recorded when the decoy was placed unless a live sensor lookup is available. A sensor that was renamed since can show its old name on such a hit, and a decoy placed before hostnames were recorded has none. `sid` is always set.
- **One access is one hit, with a limit.** The command-line match and the file read of one access, and a launcher shell and the shell it starts, collapse into one hit. A chain of three processes whose events arrive with the middle one last can still leave two hits. See [One access, one hit](decoys.md#one-access-one-hit).

## Security limits

- **The placement helper is not code-signed.** The extension ships a small static program per operating system and architecture and runs it on the host by absolute path. Endpoint protection products or application control policies on the host may flag or block an unsigned binary. **Not verified** against any specific product. Allow it by its hash if needed. No signed build exists.
- **A user with read access to your organization can learn some decoys** from detections, the files on disk, placement payloads and events. Generated secrets are never returned by a request or written to a readable record.
- Decoy file names, the names inside files and the fake services' answers are generated per organization so defaults are not a public list, but a determined attacker who has seen decoys in your environment can learn your names. `rotate` replaces secrets.
- Decoys planted by an earlier build keep the service names they were planted with, which are not per-organization. Replace those decoys with `rotate` to move them to per-organization names.
- The extension checks a decoy's contents by hash and never rewrites a changed decoy, so an attacker who edits a decoy causes a `modify` hit and a retired instance, not a silent overwrite.

## Lifecycle limits

- A reconcile that is paused between its lifecycle check and its write can recreate a rule after cleanup removed it, and a cleanup can overlap a new subscription's setup. Closing this needs a stored per-organization lifecycle lease. The next `deploy` or daily run converges the state, and your own `cancel` repairs a cleanup that overreached.
- If the platform loses the subscribe event of a re-subscribe, the organization stays inactive (nothing alerts) until its stored data is purged and a later update sets it up fresh. An update never reactivates an organization the extension saw unsubscribe.
- Final cleanup mutations the platform already received when a cleanup lease ended cannot be recalled, and can still delete a rule, entry, tag, payload, key or the adapter that a newer owner or a `cancel` had restored. Repair it with `cancel`, `deploy`, or the next daily run. Nothing is lost permanently.
- Test-fire history is bounded (see [Test-fire](detections.md#test-fire)).
