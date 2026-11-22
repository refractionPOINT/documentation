# Deception: Detections, Cases and Response

## The `deception_hit` event

Every confirmed hit is one normalized event of type `deception_hit`, sent through the organization's `ext-deception` webhook adapter. Only a candidate that the extension matched against its registry of planted decoys becomes a hit. Anything else is dropped.

```json
{
  "event_type": "deception_hit",
  "hit_id": "…",
  "decoy_id": "…",
  "kind": "file",
  "template": "kubeconfig-backup",
  "policy": "linux-servers",
  "layer": "use",
  "sid": "…",
  "hostname": "",
  "reporting_sid": "",
  "on_host": false,
  "classification": "automated",
  "mode": "live",
  "platform": "linux",
  "reader_key": "",
  "synthetic": false,
  "case_group_key": "<sid>:<incident id>",
  "source_ip": "198.51.100.7",
  "user_agent": "kubectl/…",
  "process": {},
  "details": {"source": "collector", "service": "k8s", "matched_by": "…",
              "source_ip_evidence": {"status": "not_available"}},
  "time": "…"
}
```

| Field | Meaning |
| --- | --- |
| `decoy_id`, `kind`, `template`, `policy` | Which decoy was hit. |
| `layer` | `read`, `modify`, `delete` or `use`. |
| `sid` | The endpoint the decoy was **planted on**, even when the evidence came from elsewhere. |
| `hostname` | The hostname of that endpoint: the sensor's current name when the extension can look it up, otherwise the hostname recorded when the decoy was placed. A collector hit therefore carries it too. It is empty only for a decoy placed before the extension recorded hostnames. |
| `reporting_sid` | The sensor that reported it, when different from `sid`. |
| `on_host` | True only when the evidence is an event the decoy's own sensor reported (a file read, a modification, a command-line match or, for a `hostname` decoy, a DNS lookup of a decoy name, on the host the decoy was planted on); `details.on_host_basis` is then `sensor_event`. **It is always `false` for a collector hit and for a sign-in**, whatever the source address, by design: see [Isolation](#isolation). |
| `classification` | A label, see below. |
| `mode` | `observe` for an on-host read or modification of a decoy whose policy is in [observe mode](configuration.md#observe-mode), `live` for everything else, uses included. |
| `platform` | The decoy sensor's platform, when known. |
| `reader_key` | A stable key of the reader's identity (platform, image path, and signer or SHA-256), the same one `list_readers` groups by. Empty when the event names no process. |
| `synthetic` | True only for the extension's own test hits. It is set on the server side. Nothing in an incoming request can set it. |
| `case_group_key` | `<sid>:<incident id>`. Hits on the same sensor within an incident window (30 minutes by default) share an incident. |
| `source_ip`, `user_agent` | For collector hits. |
| `process` | The acting process, when the event carried it. |
| `details` | Kind-specific, from an allowlist of fields. Secret values are scrubbed from every string, and headers that carry credentials are never copied. For collector hits it includes the service, method, path and request details such as an MCP tool name. For sensor events: the event type, the observed path and the decoy path. For hits that carry a source address, it also holds [address evidence](#address-evidence-is-enrichment-only). |

The envelope is common to every kind, so the default rules match on it and a new kind raises detections with no rule change. Token hits use the same envelope under their own event type, `deception_drop_hit` (see [What a token hit looks like](drops.md#what-a-hit-looks-like)), so rules written for `deception_hit` do not match them. An approved reader's read is not a hit: it is a [`deception_read_allowed`](configuration.md#every-approved-read-is-recorded) event.

A command-line match and the file read of the same access, and a launcher shell and the shell it starts, are collapsed into one hit (see [One access, one hit](decoys.md#one-access-one-hit)). The extension's own placement and verification reads never raise a hit (see [The extension's own reads never alert](decoys.md#the-extensions-own-reads-never-alert)).

You can read the hits the extension recorded with the `list_hits` request, or in the **Hits** tab of the web app. They are kept for 90 days. See [Requests](requests.md#list_hits).

### Address evidence is enrichment only

A collector hit or a sign-in hit carries a source address. Where the extension can look up the decoy's sensor, the hit also records whether that address is one of the addresses the sensor last reported, as `details.source_ip_matches_sensor`, with `details.source_ip_evidence`:

| Field | Meaning |
| --- | --- |
| `status` | `match`, `no_match`, or `not_available` (the sensor's addresses were not looked up where the hit was recorded, which is the case for hits recorded from the collector). |
| `address_kind` | `external` or `internal`, on a match. |
| `sensor_last_seen` | When the sensor last reported, when known. |
| `uniqueness` | Always `not_established`: the address is not compared with the rest of your sensors, so a shared egress or a reused range would match many hosts. `complete` is `false`. |

This is information for the analyst. It never changes `on_host`, never changes the classification, and never lets a hit isolate a host.

### Delivery

Each confirmed hit is delivered to the `ext-deception` adapter once across all the instances of the extension, with narrow exceptions that each send another identical event (same `hit_id`, same `case_group_key`): the adapter accepted the event but the acknowledgement was lost, and the extension then retried; or the extension process stopped, or every write of its sent marker failed, after the adapter accepted the event. There is no ceiling of two copies if the failure repeats. The platform does not drop such a duplicate, so the shipped rules would report it twice. A duplicate does not isolate a host again, because a recorded isolation prevents repeats (see [Isolation](#isolation) for the one narrow exception). If you need exactly-once handling, deduplicate on `hit_id` in your own rules or downstream. How `ext-cases` handles a second detection with the same grouping key is **not verified**.

### Classification

A label only ever sits on top of a confirmed hit and never decides whether a hit exists. In order of precedence:

| Label | Set when |
| --- | --- |
| `unknown` | A synthetic hit, or nothing below applies. |
| `copied-decoy` | The decoy's file or secret showed up on a sensor it was not planted on. The hit names the source host. |
| `sanctioned-agent-touched-decoy` | Reserved for your own AI agents reading a decoy. **Not active in this release**: the configuration has no field to declare your own agents yet, so nothing is labelled this way. |
| `scanner-likely` | A collector hit with no on-host evidence, from a known scanner User-Agent (TruffleHog, gitleaks, nuclei, Shodan and similar) or a network the operator lists as a scanner network. |
| `ai-agent-likely` | An MCP tool call, or a User-Agent naming a known AI client or agent framework. |
| `automated` | A scripting or CLI User-Agent (curl, wget, Python, Go, kubectl, aws-cli, git and similar). |
| `human-likely` | A browser User-Agent on the collector, or a read from a graphical file manager. |
| `link-preview-likely` | Tokens only: a link unfurler, a link checker or an entry of your preview list. See [Link previews](drops.md#link-previews-and-mail-scanners). |

The labels based on how many decoys one process or address touched within a minute are **not active** in this release. The extension collapses the events of one access into one hit, but it does not join a file read to its process's `NEW_PROCESS` event to fill in the process, so `process` and the reader matching below depend on what the forwarded event carries. Neither is verified on real hosts.

## Default detection rules

On subscribe the extension installs nine rules in your `dr-general` hive, named `deception-*`. They are ordinary D&R rules. You own them: edit, disable or replace them. The extension installs a shipped rule that is missing (on subscribe, on every `deploy` and configuration update, and in the daily run), but it never overwrites one that exists, whether you edited it or it is an older shipped version. When a newer shipped version differs, `plan` shows it as `modified` with the shipped copy, and `deploy` applies it only when you pass `apply_pack` or `apply_all_pack`; applying a rule restores the shipped rule as a whole, including its tags and expiry. See [Upgrading](operations.md#upgrading). `coverage` checks the stored rules against the shipped ones (see [Rule integrity](decoys.md#rule-integrity)). On unsubscribe or uninstall, only rules still equal to the shipped version are removed. A rule you edited stays.

| Rule | Matches | Does |
| --- | --- | --- |
| `deception-alert` | A real (not synthetic) hit, layer not `delete`, mode not `observe`, and not a sanctioned-agent read | Report, category `deception.<kind>.<layer>`, **priority 10**, with the case grouping key |
| `deception-alert-observe` | A real hit, layer not `delete`, mode `observe` | Report, priority 2. No response. |
| `deception-alert-sanctioned-agent` | A real hit classified as a sanctioned agent, layer not `use`, mode not `observe` | Report, priority 6 (never matches in this release, see above) |
| `deception-alert-decoy-deleted` | A real hit with layer `delete` | Report, priority 5. Never isolates. |
| `deception-respond` | A real hit, not `delete`, mode not `observe`, `on_host` true, classification neither `scanner-likely` nor sanctioned | Calls the extension's `respond` request with the hit id and action `policy` (which isolates only if the hit's policy sets `responses.isolate`) |
| `deception-test` | A synthetic hit | Report under the reserved category `__deception-test`, no response |
| `deception-coverage-warning` | A `deception_coverage_warning` event | Report `deception.coverage`, priority 3 |
| `deception-drop-alert` | A real `deception_drop_hit`, live, not `link-preview-likely` or `scanner-likely` | Report, priority 10, filed with no sensor (see [Tokens](drops.md#cases-and-response)) |
| `deception-drop-preview` | A real `deception_drop_hit` that is `link-preview-likely`, `scanner-likely` or in observe mode | Report, priority 3 |

The detection metadata carries `case_group_key`, `case_sid` and `case_hostname` (the hit's own endpoint, so a case is filed under the host the decoy was planted on, not under the extension's adapter), and a `deception` object (`hit_id`, `decoy_id`, `kind`, `template`, `layer`, `classification`) so your own rules and cases can use them.

The shipped alert rule looks like this:

```yaml
detect:
  target: edr
  event: deception_hit
  op: and
  rules:
    - op: is
      path: event/synthetic
      value: false
    - op: is
      path: event/layer
      value: delete
      not: true
    - op: is
      path: event/mode
      value: observe
      not: true
    - op: or
      rules:
        - op: is
          path: event/classification
          value: sanctioned-agent-touched-decoy
          not: true
        - op: is
          path: event/layer
          value: use
respond:
  - action: report
    name: "deception.{{ .event.kind }}.{{ .event.layer }}"
    priority: 10
    metadata:
      case_group_key: "{{ .detect.event.case_group_key }}"
      deception:
        hit_id: "{{ .detect.event.hit_id }}"
        kind: "{{ .detect.event.kind }}"
        layer: "{{ .detect.event.layer }}"
```

(Shortened. The installed rule carries the full metadata.) The rules contain no generated value (no token, planted username or per-host path), so they stay the same size whatever your fleet does.

Do not use a plain `isolate network` response in a rule that matches `deception_hit`. The event arrives through the extension's adapter, so a plain isolation would act on the adapter instead of the endpoint. Call the extension's `respond` request instead, as the shipped rule does.

If you disable or edit the `deception-test` rule so it no longer produces a detection, the next `test_fire` marks the path `broken`. Deleting or disabling `deception-alert` or `deception-alert-decoy-deleted` marks the paths they serve `broken` in `coverage` through the [rule integrity](decoys.md#rule-integrity) check, not through `test_fire`. An edit to a shipped rule reads `unverified (rule edited: <rule>)`: the extension does not evaluate your rule, so it can neither call an edit working nor broken.

## Hits are detections first

Cases are optional. Deception does not need `ext-cases` for anything. Every confirmed hit becomes a `deception_hit` event on the `ext-deception` adapter, and the [default rules](#default-detection-rules) turn it into an ordinary detection (a `deception.*` category: priority 10 for a real hit that is not a deletion, 5 for a deletion, 2 for a hit in observe mode, and 3 for a token hit that looks like a link preview or a scanner). That detection is the same kind as one from any other rule:

- it appears in the organization's **Detections** list and stream, with the hit's evidence;
- it goes to every [output](../../../outputs/index.md) you have set up for detections (syslog, a webhook, a SIEM, a bucket and so on), and your own D&R rules can react to the `deception_hit` event or to the detection;
- the **Hits** tab of the Deception page reads the extension's own store, so it lists every hit whether or not anything else is subscribed.

`ext-cases` only reads those detections. If it is subscribed and ingesting detections, it opens a case for each one as described below; if it is not, nothing about the detection, its priority, an output or an isolation changes, and no case exists. Subscribe it when you want hits grouped into cases and worked as incidents.

## Cases

If the `ext-cases` extension is subscribed and ingesting your detections, a `deception.*` detection at priority 10 opens a critical case (priorities 8 to 10 map to critical). With the default rules this is the case for real hits that are not deletions. Deletion hits are priority 5, observe-mode hits priority 2, token hits that look like a preview or a scanner priority 3, and synthetic (test) hits never open a case. If you edit the rules, the priorities and cases follow your edits. The case grouping key keeps hits from different machines in different cases, even though they all arrive through the same adapter. Hits on one machine within an incident window group together. A hit that came through the collector (a secret used over the network) is filed under the host the decoy was planted on, with that host's hostname, not under the extension's adapter.

**Observe mode.** An observe-mode hit (priority 2) opens a low-severity case. A critical hit on the same host joins that case and raises it.

**Tokens.** A token hit opens one case per token and incident, filed with no sensor, with the token's label where the host name usually is. Priority 10 is critical and priority 3 (a link preview, a scanner or an observe-mode token) is medium. See [Tokens](drops.md#cases-and-response).

**In the web app**, a case that holds Deception detections shows a **Deception** section: up to five hits with what happened (layer and class), when, the endpoint (or "No endpoint (token)"), the policy or the token's label, the process, user and signer, whether the hit was in observe mode, and links to the hit and the decoy or token in the Deception page.

Test hits are reported under `__deception-test`. `ext-cases` ignores categories that start with `__`, so tests never open a case. The `deception.coverage` detection (priority 3) is a normal detection. Whether it opens a case depends on how Cases ingests your detections, which is **not verified** here.

## Response

### The `respond` request

`respond` is called by detection rules and by the web app's manual **Isolate host** and **Tag host** actions on a hit. It takes `hit_id` and an `action`: `isolate`, `tag`, `ai_triage` or `policy`. It resolves the endpoint from the stored hit, under the organization of the caller, and applies the guards to that stored record, never to anything the caller supplies. An edited rule or a caller that lies cannot turn a test or a cleanup into an isolation.

| Action | Does |
| --- | --- |
| `isolate` | Network-isolates the decoy's sensor, behind the guards below. |
| `tag` | Tags the sensor `deception-hit` for 30 days. Refused for a synthetic hit, a hit that names no sensor, or an inactive organization. The shipped rules do not call it. |
| `ai_triage` | **Not built.** The request says so. Add a `start ai agent` response to your own detection rule instead. |
| `policy` | Does what the hit's policy asks: `isolate` if `responses.isolate` is `true`. `responses.start_ai` produces the `ai_triage` answer above. It does nothing, whatever the rule that calls it, when the hit was in observe mode (`observe_mode_hit`), its policy is disabled (`policy_disabled`) or no longer in the configuration (`policy_not_in_config`), or the policy asks for nothing (`no_automatic_response`). The hit still alerts. |

The answer lists each action with `done` and, for an action not done, its `reason` and a stable `code` (see [Errors and refusal codes](requests.md#errors-and-refusal-codes)). An explicit `isolate` or `tag`, from the web app or your own rule, is a person's or a rule's decision: it still acts on an observe-mode hit or a hit whose policy is disabled, behind the same guards.

### Isolation

A secret can be replayed long after it leaked, from anywhere, so a use hit with no matching activity on the host means "this host leaked a credential", not "this host is under attack right now". Automatic isolation is therefore opt-in (`responses.isolate: true` in the policy) and guarded, and it rests only on on-host evidence: a read, a modification, a command-line match or a DNS lookup of a decoy hostname that the decoy's own sensor reported. A `use` hit can therefore isolate when its evidence is such a lookup, but never when it arrives from the collector or a sign-in log.

!!! note "A network address never isolates a host (by design)"
    A source address is a poor proof of which machine sent a request: NAT, DHCP churn, shared cloud egress, VPNs and an offline sensor's stale address all put one address on many machines or move one machine across addresses, and a wrong answer would isolate the wrong host. So a hit that arrives through the collector, and a sign-in hit, never has `on_host` true, even when the secret is used from the decoy's own host and the address matches the sensor's. `respond` also refuses any stored hit that rests on an address, including hits stored before this rule. These hits still raise the priority 10 detection and, if `ext-cases` is subscribed, open a case. The [address evidence](#address-evidence-is-enrichment-only) on the hit helps an analyst decide.

The extension refuses to isolate, whatever your rules say, when the hit is:

| Refusal reason | Case |
| --- | --- |
| `no_endpoint` | A token hit, or a hit that names no sensor: there is no machine to isolate. |
| `synthetic_hit`, `unmatched_test_instance_hit` | A test hit, or a hit on a test decoy that no test run claims. |
| `delete_only_hit` | A deletion. |
| `off_host_hit` | Not from the decoy's own host: not `on_host`, or resting on a source address. |
| `scanner_likely_hit` | Classified as a scanner. |
| `sensor_gone`, `host_rebuilt` | The sensor was deleted, or enrolled again after the hit. |
| `hit_too_old` | Older than 7 days. |
| `org_inactive` | The organization is unsubscribing or unsubscribed (checked at the start and again right before acting). |
| `already_isolated_for_incident`, `isolation_in_progress` | A recorded isolation prevents repeats: an incident is isolated once, even if an analyst later releases the host. A concurrent delivery sees it in progress. If the host was isolated but the extension could not record it (a storage failure that outlasts its retries), nothing marks the incident as done, and a later delivery can isolate it again once the claim lapses. This is a narrow window. |
| `org_hourly_cap` | The organization already isolated its [hourly cap](configuration.md#isolation-cap) of hosts in the last hour (default 5). |

A failed isolation frees the incident for a retry. `respond` also refuses to isolate when it cannot know your isolation cap: the configuration is disabled (`config_disabled`), cannot be read (`config_unreadable`), or its `isolation_cap_per_hour` is invalid (`isolation_cap_invalid`). `plan` shows the cap in effect as `isolation_cap`.

## Test-fire

Test-fire checks that each read, modify and use alert path works, on demand with `test_fire` and automatically each day, without ever hiding a real attack. It does not exercise deletion: a test touches a test decoy to read, modify and use it, never to delete it. The `deception-alert-decoy-deleted` rule gets only the [rule integrity](decoys.md#rule-integrity) check, which marks the delete layer `broken` if the rule is missing or disabled.

!!! warning "What test-fire does not prove"
    A test hit is synthetic, so it matches only the `deception-test` rule, which reports under `__deception-test`. Test-fire therefore checks the extension's detection path, from the decoy to a detection. It does **not** prove that the real-alert rules (`deception-alert` and the others), cases or isolation work. A test never opens a case and never isolates. To check those, review your rules and the case integration yourself.

- **Test decoys only.** Each policy gets its own test-only decoys, recorded as test instances. A real decoy is never fired, so a hit on a real decoy is always real.
- **Bound to a run the extension started.** A hit on a test decoy counts as a test only when it matches a run the extension started, within the run's 5-minute window. File reads, command lines and modifications must come from the process the extension tasked on that sensor. Collector tests go over an internal, authenticated path, never the public one. Sign-in tests are injected by the extension straight into its hit pipeline, because real failed sign-ins to your tenant every day would look like a password spray.
- **Anything unmatched is real.** A hit on a test decoy that matches no run is a real `deception_hit`. This is deliberate: it covers an attacker who found the test file. The [reader allowlist](configuration.md#reader-allowlist) still applies, as on a real decoy: a read or modification of a test decoy by a reader your allowlist approves (a backup agent or antivirus sweeping the disk) is dropped and recorded as a `deception_read_allowed` event with `test_decoy: true`.
- **A path it cannot check.** If a run covers the event's time but its binding cannot be verified, the extension emits a `deception_coverage_warning` instead of an alert, so a rule of yours cannot isolate a host on the extension's own traffic.
- **Tests never open cases or act.** Test hits are marked `synthetic` on the server side, reported under `__deception-test`, skipped by `ext-cases`, and refused by `respond`.
- **Broken paths show up.** If a run produces no detection (the `deception-test` rule was edited, disabled or deleted, for example), `coverage` marks the path `broken`. `coverage` reads the latest test result of every alert path in your configuration, in bounded batches, and says how many it could not read (`test_results_unread`). The response of `test_fire` also carries a `pack_check` object with the rule integrity result (see [Rule integrity](decoys.md#rule-integrity)).
- **Paths that are unavailable in this release are not tested.** `test_fire` runs nothing for the fake AD account and internal-domain hostname templates. It lists at most 10 such policy and template pairs in its `issues` ("not tested: the alert paths are unavailable"), then says how many more there are. The `coverage` request lists every one.

- **New test decoys wait for their rules.** A read or modify test runs only once the test decoy's sensor has carried the template's [tag](decoys.md#per-host-watch-rules) for 10 minutes (two rule reloads), counted from the decoy's creation or from the last time the tag was put back. Until then the issue says why, and the use test runs at once.
- **Tokens are tested too.** One hidden test token per form your organization uses is fired each day, and `test_fire` with `drop_id` fires one token now. See [Testing and coverage](drops.md#testing-and-coverage).

Which alert paths a test can reach depends on the deployment: a collector test needs the extension's internal collector path, and a path the deployment cannot test is reported in the `issues` of the answer rather than silently passed.

**When the result is final.** A run whose detection comes back is final at once, as `detected`, and `coverage` shows it from then on. A run whose helper the sensor never started is final at once as `not_detected`, since nothing touched the decoy. Otherwise a run's detection can be held for a while (see [Alert latency](#alert-latency)), so a run is not finalized as "no detection" until its window, the hold time and a margin have passed: about an hour after the run starts (5 minutes of run window, 10 minutes of hold, then up to 42 minutes for the extension to settle held events and a slow detection). Until then `list_test_runs` shows the run as `pending` with the time its outcome is due (`expected_final_at`), and `coverage` does not mark its path `broken` for it. A run past its due time is recorded by the extension's next maintenance pass, not by the 30-minute sweep that releases held events. A test detection is reported under the reserved `__deception-test` category, which the platform never lists or sends to outputs: it does not appear in the detection list whatever filter you use, so read the outcome with `list_test_runs` and `coverage`.

Test history is bounded: a test operation's full record expires 7 days after it closes, and its idempotency record and run rows 30 days after, so a `test_fire` request replayed after 30 days is a new request.

## The `deception_coverage_warning` event

`deception_coverage_warning` is a non-alerting event. In this release the extension emits it in one case: a hit on its own test decoy that falls inside a test run's window, but whose run binding cannot be checked. The extension sends it as an event through its adapter. It is not returned by `list` or `coverage`: you see it as the emitted event, as the detection of the shipped rule, and in `list_hits` (filter with `event_type`). It carries no case grouping key and never isolates. The shipped `deception-coverage-warning` rule reports it as a priority 3 detection named `deception.coverage`.

It is not sent when a log source goes quiet or an alert path breaks. A broken path shows in `coverage` only, and the quiet-source status is not active in this release (see [Coverage statuses](decoys.md#coverage-statuses)).

## Alert latency

Decoy reads reach the extension through the sensor and a forwarding rule, and use hits through the collector or your log sources. **No latency measurements exist yet** for read alerts on busy hosts, and cloud log sources add their own delay (Entra ID and Okta sign-in logs are not real time). Known delays and limits:

- A file event that arrives before the extension has confirmed whether its own placement helper caused it is held for up to 10 minutes, and a 30-minute sweep releases held events. About 40 minutes is therefore the **nominal** delay for such a real hit when there is no backlog and nothing fails. It is not a maximum: when many held events are waiting, or a step fails and is retried, the release can take longer, each retry being a platform retry or the next 30-minute sweep. This only affects events on a decoy that has an operation running a helper at that moment. It does not delay hits on idle decoys.
- A read by an unknown process that falls inside one of the extension's own operations on that decoy is held while it asks the sensor whether the reader is the sensor itself. That normally takes a second or two. When the answers never come, the read becomes due for judgment after two minutes and is then judged like any other read: a real hit. It is released by the next event of that sensor or, at the latest, by the 30-minute sweep, so it can wait up to about 32 minutes in the nominal case, and longer under backlog or failures. The extension asks a given sensor one question at a time and at most 12 per ten minutes; beyond that every read is judged as it arrives.
- A host's first decoy of a template is watched for reads and modifications only once the sensor reloads its rules, 0 to 5 minutes after the template's tag is put on it (see [Per-host watch rules](decoys.md#per-host-watch-rules)). Use alerts and the command-line rule are not affected. This delay has not been measured on a live sensor.
- Sensor drops under load: the Linux file collector can drop records silently on a busy host, so a decoy read can be missed. This is a sensor limitation.
