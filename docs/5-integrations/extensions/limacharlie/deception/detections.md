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
  "synthetic": false,
  "case_group_key": "<sid>:<incident id>",
  "source_ip": "198.51.100.7",
  "user_agent": "kubectl/…",
  "process": {},
  "details": {"source": "collector", "service": "k8s", "matched_by": "…"},
  "time": "…"
}
```

| Field | Meaning |
| --- | --- |
| `decoy_id`, `kind`, `template`, `policy` | Which decoy was hit. |
| `layer` | `read`, `modify`, `delete` or `use`. |
| `sid` | The endpoint the decoy was **planted on**, even when the evidence came from elsewhere. |
| `hostname` | The hostname of that endpoint. Empty for a hit that came through the collector, because that path holds no organization credential to look the sensor up. |
| `reporting_sid` | The sensor that reported it, when different from `sid`. |
| `on_host` | True when the evidence comes from the decoy's own host: a sensor event from that sensor, or a collector hit whose source IP is the sensor's own address. |
| `classification` | A label, see below. |
| `synthetic` | True only for the extension's own test hits. It is set on the server side. Nothing in an incoming request can set it. |
| `case_group_key` | `<sid>:<incident id>`. Hits on the same sensor within an incident window (30 minutes by default) share an incident. |
| `source_ip`, `user_agent` | For collector hits. |
| `process` | The acting process, when the event carried it. |
| `details` | Kind-specific, from an allowlist of fields. Secret values are scrubbed from every string, and headers that carry credentials are never copied. For collector hits it includes the service, method, path and request details such as an MCP tool name. For sensor events: the event type, the observed path and the decoy path. |

The envelope is common to every kind, so the default rules match on it and a new kind raises detections with no rule change.

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

The labels based on how many decoys one process or address touched within a minute are **not active** in this release. The extension also does not join a file read to its process's `NEW_PROCESS` event by itself, so `process` and the reader matching below depend on what the forwarded event carries. Neither is verified on real hosts.

## Default detection rules

On subscribe the extension installs six rules in your `dr-general` hive, named `deception-*`. They are ordinary D&R rules. You own them: edit, disable or replace them. The extension never overwrites one you changed. When a newer shipped version exists, `plan` shows it as `modified` with the shipped copy, and `deploy` applies it only when you pass `apply_pack` or `apply_all_pack`. On unsubscribe or uninstall, only rules still equal to the shipped version are removed. A rule you edited stays.

| Rule | Matches | Does |
| --- | --- | --- |
| `deception-alert` | A real (not synthetic) hit, layer not `delete`, and not a sanctioned-agent read | Report, category `deception.<kind>.<layer>`, **priority 10**, with the case grouping key |
| `deception-alert-sanctioned-agent` | A real hit classified as a sanctioned agent, layer not `use` | Report, priority 6 (never matches in this release, see above) |
| `deception-alert-decoy-deleted` | A real hit with layer `delete` | Report, priority 5. Never isolates. |
| `deception-respond` | A real hit, not `delete`, `on_host` true, classification neither `scanner-likely` nor sanctioned | Calls the extension's `respond` request with the hit id and action `policy` |
| `deception-test` | A synthetic hit | Report under the reserved category `__deception-test`, no response |
| `deception-coverage-warning` | A `deception_coverage_warning` event | Report `deception.coverage`, priority 3 |

The detection metadata carries `case_group_key` and a `deception` object (`hit_id`, `decoy_id`, `kind`, `template`, `layer`, `classification`) so your own rules and cases can use them.

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

If you disable or edit a rule so it no longer produces a detection, the next `test_fire` marks the path `broken`.

## Cases

If the `ext-cases` extension is subscribed and ingesting your detections, a `deception.*` detection at priority 10 opens a critical case (priorities 8 to 10 map to critical). The case grouping key keeps hits from different machines in different cases, even though they all arrive through the same adapter. Hits on one machine within an incident window group together.

Test hits are reported under `__deception-test`. `ext-cases` ignores categories that start with `__`, so tests never open a case. The `deception.coverage` detection (priority 3) is a normal detection. Whether it opens a case depends on how Cases ingests your detections, which is **not verified** here.

## Response

### The `respond` request

`respond` is called by detection rules, not by people. It takes `hit_id` and an `action`: `isolate`, `tag`, `ai_triage` or `policy`. It resolves the endpoint from the stored hit, under the organization of the caller, and applies the guards to that stored record, never to anything the caller supplies. An edited rule or a caller that lies cannot turn a test or a cleanup into an isolation.

| Action | Does |
| --- | --- |
| `isolate` | Network-isolates the decoy's sensor, behind the guards below. |
| `tag` | Tags the sensor `deception-hit` for 30 days. Refused for a synthetic hit, a hit that names no sensor, or an inactive organization. The shipped rules do not call it. |
| `ai_triage` | **Not built.** The request says so. Add a `start ai agent` response to your own detection rule instead. |
| `policy` | Does what the hit's policy asks: `isolate` if `responses.isolate` is `true`. `responses.start_ai` produces the `ai_triage` answer above. A policy that asks for nothing answers "no automatic response". |

The answer lists each action and whether it was done, or why it was refused.

### Isolation

A secret can be replayed long after it leaked, from anywhere, so a use hit with no matching activity on the host means "this host leaked a credential", not "this host is under attack right now". Automatic isolation is therefore opt-in (`responses.isolate: true` in the policy) and guarded, and the default rules isolate only on on-host evidence: a read, a command line, or a use from the host's own address.

The extension refuses to isolate, whatever your rules say, when the hit is:

| Refusal reason | Case |
| --- | --- |
| `synthetic_hit`, `unmatched_test_instance_hit` | A test hit, or a hit on a test decoy that no test run claims. |
| `delete_only_hit` | A deletion. |
| `off_host_hit` | Not from the decoy's own host. |
| `scanner_likely_hit` | Classified as a scanner. |
| `sensor_gone`, `host_rebuilt` | The sensor was deleted, or enrolled again after the hit. |
| `hit_too_old` | Older than 7 days. |
| `org_inactive` | The organization is unsubscribing or unsubscribed (checked at the start and again right before acting). |
| `already_isolated_for_incident`, `isolation_in_progress` | Isolation runs at most once per incident, ever, even if an analyst later releases the host. A concurrent delivery sees it in progress. |
| `org_hourly_cap` | The organization already isolated its [hourly cap](configuration.md#isolation-cap) of hosts in the last hour (default 5). |

A failed isolation frees the incident for a retry. `respond` also refuses to isolate when the organization's configuration cannot be read.

## Test-fire

Test-fire proves that each alert path works, on demand with `test_fire` and automatically each day, without ever hiding a real attack.

- **Test decoys only.** Each policy gets its own test-only decoys, recorded as test instances. A real decoy is never fired, so a hit on a real decoy is always real.
- **Bound to a run the extension started.** A hit on a test decoy counts as a test only when it matches a run the extension started, within the run's 5-minute window. File reads, command lines and modifications must come from the process the extension tasked on that sensor. Collector tests go over an internal, authenticated path, never the public one. Sign-in tests are injected by the extension straight into its hit pipeline, because real failed sign-ins to your tenant every day would look like a password spray.
- **Anything unmatched is real.** A hit on a test decoy that matches no run is a real `deception_hit`. This is deliberate: it covers an attacker who found the test file.
- **A path it cannot check.** If a run covers the event's time but its binding cannot be verified, the extension emits a `deception_coverage_warning` instead of an alert, so a rule of yours cannot isolate a host on the extension's own traffic.
- **Tests never open cases or act.** Test hits are marked `synthetic` on the server side, reported under `__deception-test`, skipped by `ext-cases`, and refused by `respond`.
- **Broken paths show up.** If a run produces no detection (a rule was edited, disabled or deleted), `coverage` marks the path `broken`.

Which alert paths a test can reach depends on the deployment: a collector test needs the extension's internal collector path, and a path the deployment cannot test is reported in the `issues` of the answer rather than silently passed. Test history is bounded: a test operation's full record expires 7 days after it closes, and its idempotency record and run rows 30 days after, so a `test_fire` request replayed after 30 days is a new request.

## The `deception_coverage_warning` event

`deception_coverage_warning` is a non-alerting event. In this release the extension emits it in one case: a hit on its own test decoy that falls inside a test run's window, but whose run binding cannot be checked. The event is recorded (visible in `list` and `coverage`), carries no case grouping key, and never isolates. The shipped `deception-coverage-warning` rule reports it as a priority 3 detection named `deception.coverage`.

It is not sent when a log source goes quiet or an alert path breaks. Those show in `coverage` only.

## Alert latency

Decoy reads reach the extension through the sensor and a forwarding rule, and use hits through the collector or your log sources. **No latency measurements exist yet** for read alerts on busy hosts, and cloud log sources add their own delay (Entra ID and Okta sign-in logs are not real time). Two documented bounds:

- A file event that arrives before the extension has confirmed whether its own placement helper caused it is held, for at most 10 minutes. A 30-minute sweep releases held events, so such a real hit waits at most about 40 minutes. This only affects events on a decoy that has an operation running a helper at that moment. It does not delay hits on idle decoys.
- Sensor drops under load: the Linux file collector can drop records silently on a busy host, so a decoy read can be missed. This is a sensor limitation.
