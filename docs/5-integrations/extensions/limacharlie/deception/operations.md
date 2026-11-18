# Deception: Operations

## The daily run

Once a day per organization, and on every configuration update, the extension converges its rules and entries so a deleted plumbing rule or a missing adapter heals without anyone asking. The daily run also:

- verifies the decoys of the sensors it reconciles, drops sensors that no longer exist, and times out stale operations,
- retires the decoys of a policy or template you removed from the configuration (when any record was skipped as invalid on read, nothing is retired for configuration reasons, so a typo cannot remove decoys),
- places decoys on matching sensors that lack them, for example sensors that started matching a policy after the last `deploy`,
- recovers decoys stranded in the `planned` state: a decoy that was chosen more than 10 minutes ago but never moved on is settled: if its placement operation already ended it is treated as placed and waits for verification, and if no placement ever started it is marked failed (with a stable reason) so its target is free for the next pass. A bounded number is looked at per run,
- removes a `deception-dc` tag that an earlier build may have left on a domain controller (this release tags none),
- starts the next test-fire runs, and recomputes coverage,
- reports the covered-sensor numbers for [billing](#billing).

Each step is bounded and continues from a stored cursor, so a large organization is covered over several days rather than in one call. A failed step does not stop the others and is retried.

## Permissions

### For you

| To | You need |
| --- | --- |
| Send requests (`plan`, `deploy`, `uninstall` and the rest) | `ext.request` |
| Read or write the extension's configuration record | `ext.conf.get`, `ext.conf.set` |

### For the extension

The extension acts in your organization through an API key that needs these permissions. It uses them only for what this page describes.

| Permission | Why |
| --- | --- |
| `sensor.list`, `sensor.get` | List sensors and their liveness, read one sensor and its tags. |
| `sensor.task` | Task sensors (placement, verification, removal, inventory) and isolate a sensor for `respond`. |
| `sensor.tag` | Tag hit sensors `deception-hit`, and remove a leftover `deception-dc` tag. |
| `dr.list.service`, `dr.set.service`, `dr.del.service` | Its plumbing rules in `dr-service`. |
| `dr.list`, `dr.set`, `dr.del` | The default detection rules in `dr-general`. |
| `ikey.list`, `ikey.set`, `ikey.del` | The installation key of its webhook adapter. |
| `cloudsensor.get`, `cloudsensor.set`, `cloudsensor.del` | The adapter's record, and listing your connected cloud sources. |
| `externaladapter.get` | Listing your external adapters, the other half of the connected-sources view. Without it `coverage` fails. |
| `payload.ctrl` | Put, list and delete the placement payloads. |
| `ext.conf.get`, `ext.conf.set` | Add and remove its own `ext-deception-` entries in the `ext-exfil`, `ext-integrity` and `ext-artifact` configurations. This also lets it read your extension subscriptions. |

In other extensions' configurations it changes only entries whose name starts with `ext-deception-`, and refuses any other change. It never writes its own `ext-deception` configuration record (that is yours), and never subscribes your organization to another extension.

## What the extension writes in your organization

| Where | What |
| --- | --- |
| `dr-service` | Plumbing rules, named `ext-deception-connected`, `-daily`, `-task-reply`, `-sweep`, `-helper-start`, `-test-detected`, `-seen-entra`, `-seen-okta` (the sign-in observations behind the [quiet-feed note](decoys.md#log-sources-and-their-limits), at most one request an hour per source), and one `-cand-*` rule per candidate event type your templates need (file reads, FIM hits, process starts, DNS requests, Entra ID, Okta). Customers do not edit these. The extension reinstalls one that goes missing. A candidate signal that is unsafe (empty, a wildcard, too short, a bare common file name) is skipped with a warning and never widened into a firehose. |
| `dr-general` | The `deception-*` [default detection rules](detections.md#default-detection-rules). Yours once installed. |
| `ext-exfil` | Watch rules, one per template and tag set: one per template for the whole organization, plus one more for each distinct tag set the policies use it with. See the [watch-rule budget](decoys.md#watch-rule-budget). |
| `ext-integrity` | FIM wildcards per template, on the generated file name, never per-host paths. |
| `ext-artifact` | Nothing is installed here in this release. Windows event collection for domain controllers is not used. |
| Sensors | The decoy files, and the `deception-hit` tag, only if you call `respond` with `tag`. No sensor is tagged for domain controller collection. |
| Adapters | One webhook adapter, `ext-deception`, with its installation key. |

Plumbing rules contain no generated value. Nothing generated per host or per decoy is written to a rule or to any record you can read.

## Uninstalling before you unsubscribe

Unsubscribing is best-effort cleanup only. The platform deletes the subscription, and every credential the extension holds for your organization, right after the unsubscribe event, whether or not each cleanup step worked, and never retries. Sensors that are offline cannot be reached inside that event. **Run `uninstall` first**, wait for `safe_to_unsubscribe`, then unsubscribe.

```bash
limacharlie extension request --name ext-deception --action uninstall --oid "$OID"
```

1. **The first call starts it.** From that moment nothing new is placed or reinstalled: `deploy`, `rotate` and `test_fire` are refused with a clear message, a new sensor's first connection places nothing, and configuration updates and the daily run do not reconcile. Detection keeps working for decoys still in place.
2. **Every decoy is removed**, with the same hash check as `remove`. Online sensors get the removal immediately. Offline sensors get a queued removal that runs when they connect. The plumbing rules stay until then, because they finish a removal.
3. **Only when no decoy is still waiting** does it delete, in this order: outstanding payloads, the plumbing rules and unmodified shipped detection rules (all but the daily trigger), its entries in other extensions' configurations, the `deception-dc` tags, then the adapter and, last, the daily trigger. A step that fails holds back every step after it, and the daily trigger retries it. Entries the platform refuses to remove, because your organization left that extension, are named in `leftovers`. They hold the uninstall unless you use `force`.
4. **Call it again at any time.** It moves the work along and returns the status.

The status:

| Field | Meaning |
| --- | --- |
| `state` | `removing_decoys`, `removing_rules`, `done`, `cancelled` or `engine_unavailable`. |
| `safe_to_unsubscribe` | True once it is `done`, and the message names any decoys left in place. |
| `decoys` | Counts: `at_start`, `removed`, `in_progress` (online, removal sent), `pending_offline` (queued), `failed`, `sensor_gone`, with sensor ids. Lists are bounded. `more` marks a cut list, `counts_capped` a scan that hit its per-call bound. |
| `rules_kept` | Detection rules you edited, left in place. |
| `leftovers` | Entries in other extensions' configurations the platform would not let it remove. |
| `issues` | Steps that failed this call, retried by the next call and the daily run. |

Parameters:

- `force: true` finishes the uninstall although decoys remain on offline or unconfirmed sensors. Rules, entries and the adapter are removed, but the decoy files stay on those hosts. Once unsubscribed they raise no alert, and the files remain until someone removes them. A forced finish keeps naming `leftovers`.
- `cancel: true` abandons the uninstall. It puts back the plumbing rules, the adapter and the entries, and a later `deploy` places the decoys again. It is refused while the final cleanup is running.

Progress is stored durably, so a crashed request does not lose it, and the final cleanup has one owner at a time. A new subscription never inherits an old uninstall.

If you unsubscribe without uninstalling, the same cleanup runs inside the unsubscribe event as a fallback, with the limits above: offline sensors keep their decoys (inert), and a failed step is not retried. The extension's stored data for your organization (the decoy registry and hit records) is deleted once cleanup completes, or after 30 days at the latest.

## Billing

Pricing is per covered machine per period of time. **The price is not set yet and nothing on this page states one.**

A **covered sensor** is a sensor with at least one verified decoy that has a working alert path. A host whose decoys are all broken or retired is not covered.

Once a day the extension reports two numbers for the last completed UTC day, with an idempotency key per organization and day so a retried run counts once:

| Metric | Meaning |
| --- | --- |
| `covered_sensors` | The day's high-water mark: the most sensors covered at the same time. |
| `covered_sensors_distinct` | Distinct sensors covered at any point that day. For autoscaled fleets the two differ a lot: a 200-node pool replaced four times a day has a peak of 200 and 800 distinct nodes. |

They are recorded as `ext-deception:covered_sensors` and `ext-deception:covered_sensors_distinct` (in the usage API, with the `extension_` prefix). No free allowance is subtracted at report time, a day with nothing covered reports zero, and a failed run reports nothing rather than a false zero. `coverage` returns the same numbers. Reporting a metric bills nothing by itself: it is billed only once a price is attached to it.
