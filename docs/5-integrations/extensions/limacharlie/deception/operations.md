# Deception: Operations

## The daily run

Once a day per organization, and on every configuration update, the extension converges its rules and entries so a deleted plumbing rule or a missing adapter heals without anyone asking. The daily run also:

- verifies the decoys of the sensors it reconciles, drops sensors that no longer exist, and times out stale operations,
- retires the decoys of a template that no enabled policy selects any more, for example because you removed the policy or the template (a decoy that another enabled policy still selects stays, and so does a decoy on a sensor that merely stopped matching a policy's targeting). When any record was skipped as invalid on read, nothing is retired for configuration reasons, so a typo cannot remove decoys,
- first, retries the placements that failed: it deploys again the sensors whose last placement of a wanted decoy failed, three times 6 hours apart and then weekly (see [Failed decoys](decoys.md#failed-decoys)). A decoy skipped on purpose because its folder is missing is checked again the same way, with the same back-off, and is not a fault,
- runs a pass of the organization's [rollout](#rollouts), starts a new round once a week to catch sensors that started matching a policy, and restarts a round whose passes stopped,
- applies your [declared tokens](drops.md#declare-tokens-in-the-configuration) again and fires the hidden test tokens,
- puts back missing [template tags](decoys.md#per-host-watch-rules) and removes the ones no decoy accounts for,
- recovers decoys stranded in the `planned` state: a decoy that was chosen more than 10 minutes ago but never moved on is settled: if its placement operation already ended it is treated as placed and waits for verification, and if no placement ever started it is marked failed (with a stable reason) so its target is free for the next pass. A bounded number is looked at per run,
- removes a `deception-dc` tag that an earlier build may have left on a domain controller (this release tags none),
- starts the next test-fire runs, and recomputes coverage,
- reports the covered-sensor numbers for [billing](#billing).

Each step is bounded and continues from a stored cursor. A failed step does not stop the others and is retried. Placing decoys on a large organization is not left to the daily run: a [rollout](#rollouts) reaches every targeted sensor within hours.

## Rollouts

A **rollout round** visits every sensor your enabled policies target, once, and deploys to it: it puts on the missing template tags, collects the day's inventory and places the decoys that are missing. A round runs to its end on its own, in passes the platform schedules about 10 seconds apart, so nobody needs to click **Deploy** again, whatever the size of the organization.

- **What starts a round**: a `deploy` (with or without a `policy`: the round covers every enabled policy), a change to your enabled policies or templates (a configuration push starts the first pass within seconds and restarts a running round from the first sensor), a change in what the organization sends (a newly subscribed extension or sign-in source), the organization's first deploy, and once a week the daily run's recheck.
- **Pace**: about 120 sensors a minute per organization, 8 at a time, so a tenant of 20,000 sensors is covered in about three to four hours. Each organization's rollout runs on its own and never holds back another's.
- **Offline sensors** are not waited on. They are counted `offline` and get their decoys when they next connect (for policies with `setup_on_new_sensors`) or in the next round.
- **Failures**: a sensor whose deploy fails is counted `failed` and retried by the next round. Between rounds, the daily run retries a failed placement on its own, with a back-off (see [Failed decoys](decoys.md#failed-decoys)). A long run of failures in a row (an outage) pauses the round for a minute instead of failing every sensor, and no sensor can hold a round open.
- **If the chain of passes breaks** (a redeploy, a failed request), a rule that runs every 30 minutes resumes the round, and the daily run is the backstop.
- **What a round records.** For each sensor it visits, the round keeps what it did there (offline, blocked and why, inventory started, decoys planned, nothing could be placed, or the deploy failed) and when, for 30 days. That is the **Last rollout visit** of the Hosts view and of `list_hosts`, which lists every targeted host, decoy or not (see [Host status](decoys.md#host-status)).
- **No round runs** while the organization is not subscribed, an uninstall is in progress, or the configuration record is disabled, unreadable or invalid. An uninstall that starts during a round stops it.

Progress is in `plan` (`plan.deploy.rollout`), in the answer of `deploy` (`ops.rollout`, with `ops.more` true while the round runs) and on the [Deception board](board.md#the-deception-board):

| Field | Meaning |
| --- | --- |
| `state` | `running` or `done`. |
| `trigger` | What started the round: `deploy`, `config`, `sources`, `first` or `recheck`. |
| `done`, `total`, `remaining` | Sensors handled so far, sensors targeted, and the difference. When the platform could not resolve the targets, the round walks the sensor list instead: `total` is then what it has seen (`total_exact` false) and `remaining` is `-1` (unknown). |
| `started`, `offline`, `skipped`, `failed` | What happened to the sensors handled: work started, offline, nothing to do, failed. They need not add up to `done` when targeting changes mid-round. |
| `round_started`, `passes`, `last_pass`, `finished` | When the round began, how many passes it took, the latest pass, and when it finished. |
| `next_pass_by` | A pass is scheduled and expected by then. A running round with none is resumed by the 30-minute rule. |

A sensor that starts matching after the round passed its position waits for the next round, or gets its decoys when it next connects. LimaCharlie can lower the pace for a deployment.

## Permissions

### For you

| To | You need |
| --- | --- |
| Send requests (`plan`, `deploy`, `uninstall` and the rest) | `ext.request` |
| Read or write the extension's configuration record | `ext.conf.get`, `ext.conf.set` |
| Subscribe to the extension from the web app | `billing.ctrl` and `user.ctrl` |
| Place, verify, rotate, remove or test decoys, or isolate a host, from the web app | `ext.request` and `sensor.task`, with the configuration record enabled |
| Start an uninstall from the web app | `ext.request` and `sensor.task`, with the configuration record enabled. From the CLI or API, `uninstall` works even when the record is disabled. |
| Tag a host from the web app | `ext.request` and `sensor.tag` |
| Read hits, test runs, readers and the uninstall status | `ext.request` |
| Create, edit, rotate, delete or test tokens | `ext.request` |
| Place decoys on one host now (**Place on this host now**) | `ext.request` and `sensor.task` |
| See an organization on the [Deception board](board.md#the-deception-board) | `ext.request` in that organization |
| Re-key the extension's subscription (`limacharlie extension rekey`) | `billing.ctrl` and `user.ctrl` |

### For the extension

The extension acts in your organization through an API key that needs these 22 permissions. It uses them only for what this page describes.

| Permission | Why |
| --- | --- |
| `sensor.list`, `sensor.get` | List sensors and their liveness, read one sensor and its tags. |
| `sensor.task` | Task sensors (placement, verification, removal, inventory) and isolate a sensor for `respond`. |
| `sensor.tag` | Add and remove the [template tags](decoys.md#per-host-watch-rules) (`deception-t-*`), tag hit sensors `deception-hit`, and remove a leftover `deception-dc` tag. |
| `dr.list.service`, `dr.set.service`, `dr.del.service` | Its plumbing rules in `dr-service`. |
| `dr.list`, `dr.set`, `dr.del` | The default detection rules in `dr-general`. |
| `ikey.list`, `ikey.set`, `ikey.del` | The installation key of its webhook adapter. |
| `cloudsensor.get`, `cloudsensor.set`, `cloudsensor.del` | The adapter's record, and listing your connected cloud sources. |
| `externaladapter.get` | Listing your external adapters, the other half of the connected-sources view. Without it `coverage` fails. |
| `payload.ctrl` | Put, list and delete the placement payloads. |
| `payload.use` | Run the placement helper on the sensor. Without it the platform refuses the placement task, the decoy shows as failed with a reason naming the missing `payload.use` permission, and nothing is placed. |
| `ext.conf.get`, `ext.conf.set` | Add and remove its own `ext-deception-` entries in the `ext-exfil`, `ext-integrity` and `ext-artifact` configurations. This also lets it read your extension subscriptions. |
| `lookup.get` | Read the [Lookups](configuration.md#share-one-list-across-organizations-lookups) your reader allowlists reference. |

The platform copies these permissions into an organization's key when it subscribes. A subscription made before the extension asked for `lookup.get` keeps its old key, so its referenced Lookups read as `unreadable` and approve nothing until you re-key it once: `limacharlie extension rekey --name ext-deception --oid "$OID"`.

In other extensions' configurations it changes only entries whose name starts with `ext-deception-`, and refuses any other change. It never writes its own `ext-deception` configuration record (that is yours), and never subscribes your organization to another extension.

## What the extension writes in your organization

| Where | What |
| --- | --- |
| `dr-service` | Plumbing rules, named `ext-deception-connected`, `-daily`, `-task-reply`, `-sweep`, `-rollout` (resumes a [rollout](#rollouts) every 30 minutes when its passes stopped), `-helper-start`, `-test-detected`, `-seen-entra`, `-seen-okta` (the sign-in observations behind the [quiet-feed note](decoys.md#log-sources-and-their-limits), at most one request an hour per source), and one `-cand-*` rule per candidate event type your templates need (file reads, FIM hits, process starts, DNS requests, Entra ID, Okta). Customers do not edit these. The extension reinstalls one that goes missing. A candidate signal that is unsafe (empty, a wildcard, too short, a bare common file name) is skipped with a warning and never widened into a firehose. |
| `dr-general` | The `deception-*` [default detection rules](detections.md#default-detection-rules). Yours once installed. |
| `ext-exfil` | Watch rules, one per file-name pattern of each template, filtered by the template's tag, so they reach only the sensors holding a decoy of it. See [Per-host watch rules](decoys.md#per-host-watch-rules) and the [watch-rule budget](decoys.md#watch-rule-budget). |
| `ext-integrity` | One FIM rule per template, on the generated file name (never per-host paths), filtered the same way. |
| `ext-artifact` | Nothing is installed here in this release. Windows event collection for domain controllers is not used. |
| Sensors | The decoy files, the folders it made for templates with a generated folder name (removed again with the last decoy in them), one `deception-t-*` tag per template the sensor holds a decoy of, and the `deception-hit` tag, only if you call `respond` with `tag`. No sensor is tagged for domain controller collection. |
| Adapters | One webhook adapter, `ext-deception`, with its installation key. |

Plumbing rules contain no secret, token or per-host or per-decoy value. They do carry organization-level match values: the generated file and folder names (from your organization's own vocabulary) that your templates use, because the rules watch for them. Those names are the same on every host of the organization. Nothing generated per host or per decoy is written to a rule or to any record you can read.

## Uninstalling before you unsubscribe

Unsubscribing is best-effort cleanup only. The platform deletes the subscription, and every credential the extension holds for your organization, right after the unsubscribe event, whether or not each cleanup step worked, and never retries. Sensors that are offline cannot be reached inside that event. **Run `uninstall` first**, wait for `safe_to_unsubscribe`, then unsubscribe.

```bash
limacharlie extension request --name ext-deception --action uninstall --oid "$OID"
```

1. **The first call starts it.** From that moment nothing new is placed or reinstalled: `deploy`, `rotate` and `test_fire` are refused with a clear message, a new sensor's first connection places nothing, and configuration updates and the daily run do not reconcile. Detection keeps working for decoys still in place.
2. **Every decoy is removed**, with the same hash check as `remove`, and so is every folder the extension made for a decoy, once nothing else is in it. Online sensors get the removal immediately. Offline sensors get a queued removal that runs when they connect. The plumbing rules stay until then, because they finish a removal.
3. **Only when no decoy is still waiting** does it delete, in this order: outstanding payloads, the plumbing rules and unmodified shipped detection rules (all but the daily trigger), its entries in other extensions' configurations, the `deception-dc` tags and the template tags (`deception-t-*`), then the adapter and, last, the daily trigger. At most 200 template tags are removed per call. Any left once the rules are gone are inert, never hold the uninstall back, and are listed in `tags_left` with the command that removes them in bulk, for example:

    ```bash
    limacharlie tag mass-remove --selector '`deception-t-0123456789abcdef` in tags' --tag deception-t-0123456789abcdef --oid "$OID"
    ```

    A step that fails holds back every step after it, and the daily trigger retries it. Entries the platform refuses to remove, because your organization left that extension, are named in `leftovers`. They hold the uninstall unless you use `force`.
4. **Call it again at any time.** It moves the work along and returns the status. To only look, without starting or advancing anything, send `uninstall_status`: it never starts an uninstall, removes a decoy, deletes a rule, renews a lease or cancels anything, and answers `not_started` when there is none. The web app shows the same status under **Uninstall Deception** and a banner while one is running.

The status:

| Field | Meaning |
| --- | --- |
| `state` | `removing_decoys`, `removing_rules`, `done`, `cancelled` or `engine_unavailable`. |
| `safe_to_unsubscribe` | True once it is `done`, and the message names any decoys left in place. |
| `decoys` | Counts: `at_start`, `removed`, `in_progress` (online, removal sent), `pending_offline` (queued), `failed`, `sensor_gone`, with sensor ids. Lists are bounded. `more` marks a cut list, `counts_capped` a scan that hit its per-call bound. |
| `rules_kept` | Detection rules you edited, left in place. |
| `leftovers` | Entries in other extensions' configurations the platform would not let it remove. |
| `tags_left` | Template tags still on some sensors once it finished. Inert; remove them in bulk with the command the message names. |
| `issues` | Steps that failed this call, retried by the next call and the daily run. |

Parameters:

- `force: true` finishes the uninstall although decoys remain on offline or unconfirmed sensors. Rules, entries and the adapter are removed, but the decoy files stay on those hosts. Once unsubscribed they raise no alert, and the files remain until someone removes them. A forced finish keeps naming `leftovers`.
- `cancel: true` abandons the uninstall. It puts back the plumbing rules, the adapter and the entries, and a later `deploy` places the decoys again. It is refused while the final cleanup is running.

Progress is stored durably, so a crashed request does not lose it, and the final cleanup has one owner at a time. A new subscription never inherits an old uninstall.

**Tokens are not removed.** They are on no sensor: the uninstall removes the rules and the adapter, so they go silent, but each one stays wherever you put it (a wiki page, a ticket, a file share) until you take it out there. See [Tokens](drops.md#uninstall-and-billing).

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

[Tokens](drops.md) are included with the subscription. The same daily report carries `active_drops` (`ext-deception:active_drops`), the number of active tokens, test tokens excluded, with no price attached.

## Upgrading

A new release of the extension takes effect for every subscribed organization at once. What it never does on its own:

- **It never replaces a detection rule it installed earlier.** Rules in `dr-general` are yours once installed. A shipped rule that is missing (for example a rule new in this release) is installed automatically, but an existing one stays as it is, whether you edited it or it is simply the older shipped version. `plan` lists each shipped rule as `missing`, `current` or `modified`, with the current shipped copy, and `coverage` reads an older or edited rule as `unverified (rule edited: <rule>)`. Review the difference, then apply the shipped version when you choose:

    ```bash
    limacharlie extension request --name ext-deception --action deploy       --data '{"apply_pack":["deception-alert","deception-alert-sanctioned-agent","deception-respond"]}' --oid "$OID"
    ```

    Some behavior depends on the current rules. Observe mode, for example, needs the current `deception-alert`, `deception-alert-sanctioned-agent` and `deception-respond`, which leave observe-mode hits out: with older copies, an observe-mode read alerts at priority 10, and `plan` warns about it while a policy observes.
- **It never rewrites your configuration record.** A field a new release adds is off until you set it.
- **It never re-keys a subscription.** A new permission the extension asks for (such as `lookup.get`) reaches an existing organization only when you run `limacharlie extension rekey`.

What it does on its own: it rewrites its own plumbing rules and its entries in other extensions' configurations at the next `deploy`, configuration update or daily run, and decoys keep their contents (a decoy is never rewritten; `rotate` replaces one).
