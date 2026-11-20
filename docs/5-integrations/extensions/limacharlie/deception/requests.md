# Deception: Requests

You drive Deception with extension requests, from the CLI, the API, MCP or a D&R rule. The CLI form is:

```bash
limacharlie extension request --name ext-deception --action <action> --data '<json>' --oid "$OID"
```

Every request is idempotent and listed in the extension's request schema, so the CLI, the web app and MCP discover them. Sending a request needs the `ext.request` permission. Requests that plan, place, remove, verify or test decoys are refused for an organization that is not subscribed or is being unsubscribed.

Requests that read your policies and templates (`plan`, `deploy`, `verify`, `rotate`, `remove`, `test_fire`, `coverage`, and `list` with a policy) also refuse while the `ext-deception` configuration record is disabled, with "the ext-deception configuration is disabled". The extension never writes that record, so it never enables it for you: see [Enabling the configuration record](configuration.md#enabling-the-configuration-record). `list` (without a policy), `list_hosts`, `list_hits` and `list_test_runs` read the extension's own store and keep working while the record is disabled. `uninstall` and `uninstall_status` need only a subscribed organization, so they work even when your configuration is broken.

Secret values never appear in any response or log. Decoys are described by instance id, template, path and type.

## Errors

A request that fails with a mistake in your request or your own configuration says what is wrong, naming the field. A failure on the extension's side, a store or platform error for example, never shows its internal text. It reads `internal error (ref <id>)`, with an id that is new for each failure and that LimaCharlie support can use to find the details. Quote the id when you contact support. The same applies to the `issues` of `deploy`, `test_fire`, `uninstall` and the daily run, and to the `reason` of a failed decoy (for example `placement could not start: internal error [placement_start_failed]`, where the bracketed code is stable).

| Action | Purpose |
| --- | --- |
| [`plan`](#plan) | Read-only preview of what `deploy` would do. |
| [`deploy`](#deploy) | Converge rules and configuration entries, then start placement. |
| [`list`](#list) | Page through decoys, with filters. |
| [`list_hosts`](#list_hosts) | Page through the sensors that have decoys. |
| [`verify`](#verify) | Re-check that decoys are still in place. |
| [`rotate`](#rotate) | Retire decoys and plant replacements. |
| [`remove`](#remove) | Remove decoys from their hosts. |
| [`test_fire`](#test_fire) | Check the synthetic detection path of each alert. |
| [`list_test_runs`](#list_test_runs) | Page through recent `test_fire` runs and their outcomes. |
| [`list_hits`](#list_hits) | Page through the hits the extension recorded. |
| [`coverage`](#coverage) | What is active, unavailable, partial or broken, per template and layer. |
| [`list_kinds`](#list_kinds) | Decoy kinds, their schemas, and the default template library. |
| [`uninstall`](operations.md#uninstalling-before-you-unsubscribe) | Remove everything the extension owns, before you unsubscribe. |
| [`uninstall_status`](#uninstall_status) | Read where an uninstall stands, without changing anything. |
| [`respond`](detections.md#the-respond-request) | Called by detection rules on a hit. |

`list`, `list_hosts`, `list_test_runs`, `list_hits` and `uninstall_status` are the read-only requests the web app is built on. Every `list*` request applies its filters before it cuts a page, so a page holds `page_size` rows unless it is the last one, and `next_page_token` is empty exactly when nothing more exists. A token is opaque and tied to the filters it was issued for.

`candidate`, `task_reply`, `helper_start`, `sweep`, `connected`, `daily` and `test_detected` are internal. The extension's own rules call them, they are not user-facing, and you do not need to send them. The `daily` request is how the extension advances each organization once a day. The `sweep` request runs every 30 minutes.

Most requests accept `policy` (limit to one policy) and `sid` (limit to one sensor). An unknown policy name is rejected.

## plan

Read-only. Shows, per policy, how many sensors match, how many decoys are placed already, how many would be placed or retired, and what is unavailable and why. It also reports:

- `pack`: the state of each shipped detection rule (`missing`, `current` or `modified`). For a modified rule it includes the current shipped version, so you can compare it with yours. A newer shipped version is offered here and never applied implicitly.
- `watch_budget`: Exfil watch rules against the sensor limit of 100.
- `sources`: which of `ext-artifact`, `ext-exfil`, `ext-integrity` are subscribed and which adapters the organization has.
- `warnings`: configuration records skipped on read, rule signals that would be skipped as unsafe, and a warning for each policy that sets `dc_logon_collection` (the field is ignored in this release).

```bash
limacharlie extension request --name ext-deception --action plan \
  --data '{"policy":"linux-servers"}' --oid "$OID"
```

```json
{
  "plan": {
    "policies": [
      {"policy": "linux-servers", "enabled": true, "sensors": 42,
       "already_placed": 0, "to_place": 84, "to_retire": 0,
       "unavailable": [{"id": "ext-exfil", "human": "Subscribe ext-exfil"}]}
    ]
  },
  "pack": [{"name": "deception-alert", "state": "current"}],
  "watch_budget": {"limit": 100, "owned": 0, "customer": 12, "total": 12, "over": false},
  "sources": {"ext_artifact": true, "ext_exfil": false, "ext_integrity": true}
}
```

## deploy

Idempotent. Converges, in order:

1. the webhook adapter,
2. the plumbing rules in `dr-service`,
3. the missing shipped detection rules in `dr-general` (never overwriting one you edited),
4. the `ext-deception-` entries in the `ext-exfil` and `ext-integrity` configurations (and removes any `ext-deception-` entry an earlier build left in `ext-artifact`; this release adds none there),

then starts decoy placement. It never subscribes the organization to another extension: extensions it needs that are not subscribed are listed in `not_subscribed`.

| Parameter | Meaning |
| --- | --- |
| `policy`, `sid` | Limit placement to a policy or a sensor. |
| `apply_pack` | List of shipped rule names to overwrite with the current shipped version, for example `["deception-alert"]`. The rule is restored as a whole, including its tags and expiry, so it also repairs a rule that reads `unverified`. |
| `apply_all_pack` | Overwrite every shipped rule. Replaces your edits. |

```bash
limacharlie extension request --name ext-deception --action deploy --oid "$OID"
limacharlie extension request --name ext-deception --action deploy \
  --data '{"apply_pack":["deception-alert"]}' --oid "$OID"
```

The response has `ops` (`started`, `skipped`, `operations` ids, `issues`), `plumbing_written`, `pack_installed`, `pack_applied`, `others_updated`, `not_subscribed` and `warnings` (which include the `dc_logon_collection` warning). Placement is asynchronous: sensors reply later, and a decoy counts only after its hash is verified. Use `list` and `coverage` to follow it. Only sensors that are online are tasked. The daily run places decoys on matching sensors that lack them.

## list

Paginated list of decoys. Test decoys are hidden unless you ask. It lists decoy instances only: coverage-warning events are not returned here.

| Parameter | Meaning |
| --- | --- |
| `policy`, `sid` | Filters. |
| `template`, `kind` | Only decoys of this template name, or of this kind. |
| `states` | Any of `planned`, `placed`, `verified`, `retired`, `gone`, `failed`. Default: `planned`, `placed`, `verified`. |
| `text` | Only decoys whose path, template, policy, hostname or sensor id contains this text (case-insensitive, at most 128 characters). |
| `include_test` | Include test-fire decoys. |
| `page_token`, `page_size` | Paging. `page_size` up to 500, default 100. Follow `next_page_token` until it is empty. |

```json
{"instances": [{
  "id": "…", "sid": "…", "hostname": "web-01", "policy": "linux-servers", "template": "kubeconfig-backup",
  "kind": "file", "state": "verified", "path": "/root/.kube/config.prod-old",
  "sha256": "…", "layers": ["read", "modify", "delete", "use"], "is_test": false,
  "created_at": "…", "verified_at": "…"}],
 "next_page_token": ""}
```

`hostname` is the sensor's hostname when the decoy was placed (absent on a decoy placed before it was recorded); the sensor id is the identity. `reason` explains a `failed`, `retired` or `gone` state. A failure caused by the extension's own side shows a stable code, not the underlying error (see [Errors](#errors)). Instance states:

| State | Meaning |
| --- | --- |
| `planned` | Chosen, not yet sent. |
| `placed` | The sensor acknowledged, not yet verified. |
| `verified` | The file's hash matched on the host. This is the state that counts as covered. |
| `retired` | Changed or removed. Never overwritten. |
| `gone` | The sensor is gone. Tokens are kept for a retention period. |
| `failed` | Placement or removal failed. |

## list_hosts

Paginated by sensor id: each sensor that has a decoy record, with its hostname, a `status` and its decoys. It answers which hosts a template covers without one sensor lookup per row.

| Parameter | Meaning |
| --- | --- |
| `policy`, `template` | Filters. `template` keeps the sensors that have a decoy of that template. |
| `text` | Only sensors with a decoy whose hostname, sensor id, path, template or policy contains this text (case-insensitive). |
| `states` | Default: `planned`, `placed`, `verified`, `failed`. |
| `include_test` | Include test-fire decoys. |
| `page_token`, `page_size` | Paging. |

The `status` is `protected` (a verified decoy), `pending` (planned or placed only), `failed` or `none`. Each row has the counts per state and up to 50 decoys in the same shape as `list` (`more` marks a cut list; the status and counts cover all of them). A sensor in scope that has no decoy record yet (nothing planned, or everything unavailable) has no row: `plan` and `coverage` say why.

## verify

Starts hash verification of the decoys named by `instance_ids`, or of a sensor's or policy's decoys. Verification is a read-only `file_hash` task. The daily run also verifies the decoys of the sensors it reconciles.

```bash
limacharlie extension request --name ext-deception --action verify \
  --data '{"sid":"<sid>"}' --oid "$OID"
```

## rotate

Retires the given decoys and plants replacements with new secrets, for example after you learn a decoy leaked, or a decoy domain is burned. Requires `instance_ids`, a `sid` or a `policy`. It refuses to act on the whole organization.

A replacement is planted only where the helper can create the file exclusively. If a changed file still occupies the path, the replacement fails as `path in use` and is reported, not retried on the same inventory.

## remove

Removes the given decoys from their hosts after checking that each file is still the one the extension placed. Requires `instance_ids`, a `sid` or a `policy`; it refuses to act on the whole organization. A file the extension cannot prove is its own is left in place and the instance is retired. It never counts as removed.

For a full cleanup before unsubscribing, use [`uninstall`](operations.md#uninstalling-before-you-unsubscribe) instead.

## test_fire

Fires the test-only decoys of a policy, one run per alert path (for example read and use of a credential file are separate runs), to check that each path reaches a detection. The detection is the synthetic `deception-test` rule: a passing test does not prove that the real-alert rules, cases or isolation work. See [Test-fire](detections.md#test-fire) for what a test does and does not do.

```bash
limacharlie extension request --name ext-deception --action test_fire \
  --data '{"policy":"linux-servers"}' --oid "$OID"
```

`test_fire` takes only an optional `policy`: the extension picks the test decoys and their sensors. The response lists the started `runs` (run id, policy, template, layer, deadline; never a token or planted name), `issues`, and a `pack_check` object with the result of the [rule integrity](decoys.md#rule-integrity) check. A call starts at most 20 runs. A large configuration is covered by repeated calls, and the daily run walks it over time. Only alert paths whose requirements you meet are tested, since testing a path that cannot work would only report it broken. Paths that are not available in this release (fake AD accounts, internal-domain hostnames) are not tested: `issues` names at most 10 of those policy and template pairs and says how many more there are, and `coverage` lists every one. Refused while an uninstall is in progress.

The outcome of a run is final about an hour after it starts, not when it ends (see [When the result is final](detections.md#test-fire)). A test detection is reported under the reserved `__deception-test` category, which the platform never lists, so read the outcome with `list_test_runs` and `coverage`. A Windows sensor that does not report file events is not used for the paths that need them (see [Sensor versions](decoys.md#sensor-versions-windows)).

## list_test_runs

Read-only, paginated, newest first: the retained runs of `test_fire` (kept for 30 days after their deadline), one per alert path. Needs no configuration.

| Parameter | Meaning |
| --- | --- |
| `policy`, `template`, `layer` | Filters. `layer` is `read`, `modify`, `delete` or `use`. |
| `state` | `pending` (outcome not recorded yet) or `finished`. Default: both. |
| `page_token`, `page_size` | Paging. |

Each run has `run_id`, `policy`, `template`, `layer`, `instance_id`, `state`, `opened_at`, `deadline` and, for a pending run, `expected_final_at`, or for a finished one `finalized_at`. The `state` is `pending`, `detected` (the detection came back) or `not_detected`. A run's binding, planted names and tokens are never returned.

## list_hits

Read-only, paginated, newest first: the hits the extension recorded, as they were sent to the `ext-deception` adapter. They come from the extension's own store (kept for 90 days), so the request runs no detection query and needs no configuration.

| Parameter | Meaning |
| --- | --- |
| `since`, `until` | Unix seconds. `until` is exclusive. |
| `layer`, `template`, `policy`, `sid`, `classification` | Filters. |
| `event_type` | `deception_hit` or `deception_coverage_warning`. Default: both. |
| `include_test` | Include the synthetic hits of `test_fire` runs, which are left out by default. |
| `page_token`, `page_size` | Paging. |

A row is the [`deception_hit` event](detections.md#the-deception_hit-event): `hit_id`, `event_type`, `time`, `decoy_id`, `kind`, `template`, `policy`, `layer`, `sid`, `hostname`, `on_host`, `classification`, `synthetic`, `case_group_key`, `source_ip`, `user_agent`, `process` and `details`.

```bash
limacharlie extension request --name ext-deception --action list_hits \
  --data '{"layer":"read","page_size":50}' --oid "$OID"
```

## coverage

Per template and layer: `active`, `unavailable` with the missing piece, `partial` or `broken` (`blind` is not set in this release). A template that uses the AD phantom-account form or the internal hostname form shows every layer `unavailable` with "not available in this release". A quiet Entra ID or Okta sign-in feed adds an informational note ("no sign-in observed in N hours") and never changes a status. The view is organization-level: it does not list hosts, and `active` is not proof that every selected host is covered. Host-level exclusions (sensor mode, Kubernetes DaemonSet sensors) show in `plan`. See [Coverage statuses](decoys.md#coverage-statuses). Coverage-warning events are not part of this answer: they are emitted as events and detections (see [Detections](detections.md#the-deception_coverage_warning-event)). Also returns:

- `sources`: what the organization sends.
- `metering`: the covered-sensor numbers reported for billing, for the last completed UTC day (`covered_sensors` and `covered_sensors_distinct`).
- `pack_check` and `pack_issues`: the [rule integrity](decoys.md#rule-integrity) result for the shipped detection rules (`checked_at`, `attempted_at`, and each rule that is missing, disabled or edited).
- `test_results_unread`: how many alert paths' latest test result this request could not read. Those paths are not marked `broken` by it.
- `coverage.time_to_protected_seconds`, per policy: the average time from a sensor's enrollment to its first verified decoy, estimated from a bounded sample, when known.

Counts are read from the registry in bounded pages. When a registry is very large, the counts are lower bounds and the item's note says so.

## list_kinds

Every decoy kind with its settings version and JSON schema, plus `library` (the default templates, built into the extension and shipped with each release) and the record `schema_version`. Use it to write a valid template for a kind you have not used, including from an AI agent.

## uninstall_status

Read-only view of the [uninstall](operations.md#uninstalling-before-you-unsubscribe). Unlike `uninstall`, it never starts an uninstall, removes a decoy, deletes a rule, renews a lease or cancels anything, and it takes no parameters. It answers with `state` (`not_started`, `removing_decoys`, `removing_rules`, `done`, `cancelled` or `engine_unavailable`), `safe_to_unsubscribe`, a `message`, the `decoys` counts, `rules_kept`, `leftovers`, `started_at` and, once done, `finished_at`. It needs no configuration.
