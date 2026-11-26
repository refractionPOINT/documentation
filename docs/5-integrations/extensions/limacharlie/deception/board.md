# Deception: Managing Many Organizations

Deception is built for MSSPs and teams that run many tenants through infrastructure as code. Everything that changes what alerts lives in each organization's `ext-deception` configuration record, so one reviewed file can be pushed to every tenant with Git Sync or your own pipeline, and nothing depends on per-organization clicks or hidden state. This page covers what helps at that scale: the cross-tenant **Deception board**, shared reader allowlists, tokens declared as code, and stable refusal codes.

## The Deception board

The board shows one row per organization, across every organization you can see, with its protection state and what needs attention. Open it from **Deception** in the web app's top navigation.

### Scope and permission

- **Scope**: **All my organizations**, or one organization group you are a member or owner of.
- **Permission**: you need `ext.request` in an organization to see its row. An organization where you lack it is left out silently, never shown as an error.
- **Size**: a scope can hold at most 10,000 organizations. For a larger one, pick an organization group.
- Organizations without Deception are hidden behind a count. **Show organizations without Deception** lists them.

The board loads every page of organizations before it filters or sorts, so a filter is always complete. Until then it shows "Loading N of M organizations" and the filters are off.

**Order.** The board is sorted by live hits in the last 24 hours, most first, then by the worst status, then by hits in 7 days, so an organization that is being hit comes before one whose housekeeping is late. Click a column to sort by it. The sort and the filters are kept in the page's address, so a view can be shared.

### Statuses

Each row has one status: the first of these rules that matches, in this order. A tooltip names every reason that matched.

| Status | Reasons |
| --- | --- |
| Uninstalling | An [uninstall](operations.md#uninstalling-before-you-unsubscribe) is in progress. |
| Broken | Deception is not alerting: at least one alert path is deployed, and the `deception-alert` rule is missing or disabled (no read, modification or use of a decoy raises a detection), no alert path raises an alert, or only Delete paths still do. With nothing deployed the row reads Not tested, never Broken. A path broken by a test that raised no detection counts as not alerting here (the test found that path silent); a path partly covered still alerts on the hosts that hold its decoy. |
| Needs attention | Alerts work, with something to fix: an alert path or token form is broken, a test raised no detection, a shipped detection rule is missing, disabled, edited or has changed tags (the respond and test rules included), the rules could not be checked, or a path is only partly covered. |
| Not tested | Nothing is deployed yet, a testable path has no result yet, a passed test is older than 48 hours, a test passed while its alert rule was off, or a test ran while the test rule was off. |
| Unavailable | Policies select templates the organization cannot run. (A quiet source would count here too, but no source is ever judged quiet in this release: see the `blind` status in [Coverage statuses](decoys.md#coverage-statuses).) |
| Rolling out | A [rollout](operations.md#rollouts) is still running. |
| Hosts missing decoys | A targeted host is not fully protected (partial, pending, failed, skipped, no decoy yet, not reached, or restricted by ACLs), a targeted sensor has not been reached, or the host counts are lower bounds, so whether every host holds its decoys is unknown (never assumed). |
| Observing | A policy is in [observe mode](configuration.md#observe-mode): its unapproved reads and modifications alert at low priority, with no automatic response. |
| Protected | None of the above: every alert path works, every targeted host holds its decoys, and every testable path passed a test in the last 48 hours. |

Observing comes after every problem status, so it never hides a problem, and a healthy organization in observe mode reads Observing, not Protected. An **Observing** badge is also shown next to any other status.

The board adds three states of its own: **Pending first run** (subscribed, but its first summary has not been computed yet, or that computation failed, with the reason), **Datacenter unavailable** (a datacenter did not answer, or runs an older Deception that cannot answer the board), and **No Deception**.

### One verdict

Each row also has a verdict, the same one the organization's **Coverage** tab and **Overview** show: **Working** (no reason in the table above matches: every alert path works, nothing is unavailable, every targeted host holds its decoys, every testable path passed in the last 48 hours), **Working, with gaps** (alerts work, and a reason of Needs attention, Not tested, Unavailable or Hosts missing decoys matches), or **Not alerting** (the Broken status). Only two reasons never change the verdict: observe mode, and the fact that a rollout round is running (`deploy_in_progress`). Hosts the round has not reached yet still count (`rollout_incomplete`). The board reads test results live, but judges them by the test rule's off times as of the row's last computation, so a test that ran while `deception-test` was off can read failing on the board until the row is recomputed (opening the organization's **Coverage** tab does it). `fleet_summary` returns it as `verdict: {state, reasons}` (`working`, `gaps`, `not_alerting`), and an organization-wide [`coverage`](requests.md#coverage) returns the same object.

### Columns and freshness

Columns: Organization, Status, Hits 24h, Hits 7d, Last hit, Alert paths, Hosts with decoys, Mode, Active tokens and Last test. Hits come first. **Alert paths** gives the number broken (split into broken by a rule and broken by a test), unverified and unavailable. A totals strip above the rows adds them up across the scope: organizations by status (click one to filter), hosts with decoys, live and observe hits, active tokens, what needs attention and the oldest summary. **Show only** narrows the board to organizations that are broken, unverified, not tested in 48 hours, with a rollout not complete, observing, or hit in 24 hours or 7 days.

- **Hits and test results are live**: they are read when the board loads.
- **The coverage half of a row** (sensors, paths, rules, rollout, mode) is computed by the organization's daily run, and again whenever someone opens that organization's **Coverage** tab. It can be up to about a day old. **As of** says when it was computed. If a later computation failed, the row keeps the earlier numbers and shows **Last run failed** with the reason.
- **Hosts with decoys** is the number of hosts that hold a placed or verified decoy of an enabled policy, out of the distinct hosts the enabled policies target (`coverage.sensors`, see [`coverage`](requests.md#coverage)). It is not the billing count, and it says how far the rollout got, not how many hosts a decoy has been verified on. The billed covered-sensor count of the last completed UTC day, at its peak, is in the organization's side panel.
- A count shown as `≥N` is a lower bound: the extension stopped counting at a bound, so the real number can be higher.
- **Mode** reads Live, or "Observing N of M" with the earliest end time, or "open-ended" when a policy observes with no `observe_until`.

**Details** on a row opens a side panel next to the table (over it on a narrow window) without leaving the board. It shows why the row has its status, its numbers (hosts with decoys, alert paths with the broken ones split by rule and by test, mode, hits, tokens, last test, covered sensors for billing, and when the coverage was computed and by what), the top reasons, the requirement missing most often (for example "Subscribe ext-exfil"), up to 10 failing test paths, and links to the organization's Deception page and its cases.

If a datacenter does not answer, its organizations are listed with no numbers and the totals are marked partial. The board can be reloaded about once every two minutes at the largest scope; past its rate limit it asks you to wait a minute.

## Shared approved readers

Approved readers (indexers, backup agents, antivirus) are usually the same across your tenants. Keep them in one [Lookup](../../../../7-administration/config-hive/lookups.md) and reference it from every organization's configuration instead of copying entries:

```yaml
reader_allowlist:
  - lookup: mssp-approved-readers
    comment: shared approved readers
```

The Lookup must exist in each organization that references it (sync it with the configuration). See [Reader allowlist](configuration.md#reader-allowlist) for its format, bounds and failure behavior, and for the one-time re-key that organizations subscribed before Lookup support need.

## Tokens as code

Declare tokens in the configuration's `drops` list and they are created, updated and deleted by name in every organization the record goes to. Reverting a commit within 90 days restores the same tokens. See [Declare tokens in the configuration](drops.md#declare-tokens-in-the-configuration).

## Rollouts finish on their own

After a push, every targeted sensor of a large tenant is reached by a paced rollout that runs to its end with no further request. See [Rollouts](operations.md#rollouts).

## Automation and refusal codes

Every refusal carries a stable code next to its English sentence, so a pipeline or an AI agent can react to the code and never has to match text. See [Errors and refusal codes](requests.md#errors-and-refusal-codes).

## Upgrades never change your rules silently

A new release never replaces a detection rule it installed earlier. `plan` shows a shipped rule whose newer version differs as `modified`, and `deploy` with `apply_pack` applies it when you choose. See [Upgrading](operations.md#upgrading).
