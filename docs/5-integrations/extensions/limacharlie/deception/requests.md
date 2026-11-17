# Deception: Requests

You drive Deception with extension requests, from the CLI, the API, MCP or a D&R rule. The CLI form is:

```bash
limacharlie extension request --name ext-deception --action <action> --data '<json>' --oid "$OID"
```

Every request is idempotent and listed in the extension's request schema, so the CLI, the web app and MCP discover them. Sending a request needs the `ext.request` permission. Requests that plan, place, remove, verify or test decoys are refused for an organization that is not subscribed or is being unsubscribed.

Secret values never appear in any response or log. Decoys are described by instance id, template, path and type.

| Action | Purpose |
| --- | --- |
| [`plan`](#plan) | Read-only preview of what `deploy` would do. |
| [`deploy`](#deploy) | Converge rules and configuration entries, then start placement. |
| [`list`](#list) | Page through decoys. |
| [`verify`](#verify) | Re-check that decoys are still in place. |
| [`rotate`](#rotate) | Retire decoys and plant replacements. |
| [`remove`](#remove) | Remove decoys from their hosts. |
| [`test_fire`](#test_fire) | Check the synthetic detection path of each alert. |
| [`coverage`](#coverage) | What is active, unavailable, partial or broken, per template and layer. |
| [`list_kinds`](#list_kinds) | Decoy kinds, their schemas, and the default template library. |
| [`uninstall`](operations.md#uninstalling-before-you-unsubscribe) | Remove everything the extension owns, before you unsubscribe. |
| [`respond`](detections.md#the-respond-request) | Called by detection rules on a hit. |

`candidate`, `task_reply`, `helper_start`, `sweep`, `connected`, `daily` and `test_detected` are internal. The extension's own rules call them, they are not user-facing, and you do not need to send them. The `daily` request is how the extension advances each organization once a day. The `sweep` request runs every 30 minutes.

Most requests accept `policy` (limit to one policy) and `sid` (limit to one sensor). An unknown policy name is rejected.

## plan

Read-only. Shows, per policy, how many sensors match, how many decoys are placed already, how many would be placed or retired, and what is unavailable and why. It also reports:

- `pack`: the state of each shipped detection rule (`missing`, `current` or `modified`). For a modified rule it includes the current shipped version, so you can compare it with yours. A newer shipped version is offered here and never applied implicitly.
- `watch_budget`: Exfil watch rules against the sensor limit of 100.
- `sources`: which of `ext-artifact`, `ext-exfil`, `ext-integrity` are subscribed and which adapters the organization has.
- `warnings`: configuration records skipped on read, and rule signals that would be skipped as unsafe.

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
4. the `ext-deception-` entries in the `ext-exfil`, `ext-integrity` and `ext-artifact` configurations,

then starts decoy placement. It never subscribes the organization to another extension: extensions it needs that are not subscribed are listed in `not_subscribed`.

| Parameter | Meaning |
| --- | --- |
| `policy`, `sid` | Limit placement to a policy or a sensor. |
| `apply_pack` | List of shipped rule names to overwrite with the current shipped version, for example `["deception-alert"]`. |
| `apply_all_pack` | Overwrite every shipped rule. Replaces your edits. |

```bash
limacharlie extension request --name ext-deception --action deploy --oid "$OID"
limacharlie extension request --name ext-deception --action deploy \
  --data '{"apply_pack":["deception-alert"]}' --oid "$OID"
```

The response has `ops` (`started`, `skipped`, `operations` ids, `issues`), `plumbing_written`, `pack_installed`, `pack_applied`, `others_updated`, `not_subscribed` and `warnings`. Placement is asynchronous: sensors reply later, and a decoy counts only after its hash is verified. Use `list` and `coverage` to follow it. Only sensors that are online are tasked. The daily run places decoys on matching sensors that lack them.

## list

Paginated list of decoys. Test decoys are hidden unless you ask. It lists decoy instances only: coverage-warning events are not returned here.

| Parameter | Meaning |
| --- | --- |
| `policy`, `sid` | Filters. |
| `states` | Any of `planned`, `placed`, `verified`, `retired`, `gone`, `failed`. |
| `include_test` | Include test-fire decoys. |
| `page_token`, `page_size` | Paging. `page_size` up to 500, default 100. A page can hold fewer rows than `page_size` when a filter is applied to it. Follow `next_page_token` until it is empty. |

```json
{"instances": [{
  "id": "…", "sid": "…", "policy": "linux-servers", "template": "kubeconfig-backup",
  "kind": "file", "state": "verified", "path": "/root/.kube/config.prod-old",
  "sha256": "…", "layers": ["read", "modify", "delete", "use"], "is_test": false,
  "created_at": "…", "verified_at": "…"}],
 "next_page_token": ""}
```

`reason` explains a `failed`, `retired` or `gone` state. Instance states:

| State | Meaning |
| --- | --- |
| `planned` | Chosen, not yet sent. |
| `placed` | The sensor acknowledged, not yet verified. |
| `verified` | The file's hash matched on the host. This is the state that counts as covered. |
| `retired` | Changed or removed. Never overwritten. |
| `gone` | The sensor is gone. Tokens are kept for a retention period. |
| `failed` | Placement or removal failed. |

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

The response lists the started `runs` (run id, policy, template, layer, deadline; never a token or planted name). A call starts at most 20 runs. A large configuration is covered by repeated calls, and the daily run walks it over time. Only alert paths whose requirements you meet are tested, since testing a path that cannot work would only report it broken. Refused while an uninstall is in progress.

## coverage

Per template and layer: `active`, `unavailable` with the missing piece, `partial` or `broken` (`blind` is not set in this release). The view is organization-level: it does not list hosts, and `active` is not proof that every selected host is covered. Host-level exclusions (sensor mode, Kubernetes DaemonSet sensors) show in `plan`. See [Coverage statuses](decoys.md#coverage-statuses). Coverage-warning events are not part of this answer: they are emitted as events and detections (see [Detections](detections.md#the-deception_coverage_warning-event)). Also returns:

- `sources`: what the organization sends.
- `metering`: the covered-sensor numbers reported for billing, for the last completed UTC day (`covered_sensors` and `covered_sensors_distinct`).
- `coverage.time_to_protected_seconds`, per policy: the average time from a sensor's enrollment to its first verified decoy, estimated from a bounded sample, when known.

Counts are read from the registry in bounded pages. When a registry is very large, the counts are lower bounds and the item's note says so.

## list_kinds

Every decoy kind with its settings version and JSON schema, plus `library` (the default templates) and the record `schema_version`. Use it to write a valid template for a kind you have not used, including from an AI agent.
