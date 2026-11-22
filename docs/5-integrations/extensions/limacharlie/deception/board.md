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

### Statuses

Each row has one status: the first of these rules that matches, in this order. A tooltip names every reason that matched.

| Status | Reasons |
| --- | --- |
| Uninstalling | An [uninstall](operations.md#uninstalling-before-you-unsubscribe) is in progress. |
| Broken | An alert path is broken, a token form is broken, a shipped detection rule is missing or disabled, or a test-fire found a path that raised no detection. |
| Not tested | Nothing is deployed yet, so nothing could be tested, or there is no test-fire result in the last 48 hours. |
| Unavailable | Policies select templates the organization cannot run, or a source the decoys need is quiet. |
| Rolling out | Not every targeted sensor holds a decoy yet, a [rollout](operations.md#rollouts) is still running, or a sensor count is a lower bound, so whether the rollout is complete is unknown (never assumed complete). |
| Observing | A policy is in [observe mode](configuration.md#observe-mode): its reads do not alert yet. |
| Protected | None of the above. |

Observing comes after every problem status, so it never hides a problem, and a healthy organization in observe mode reads Observing, not Protected. An **Observing** badge is also shown next to any other status.

The board adds three states of its own: **Pending first run** (subscribed, but its first summary has not been computed yet, or that computation failed, with the reason), **Datacenter unavailable** (a datacenter did not answer, or runs an older Deception that cannot answer the board), and **No Deception**.

Partial paths, edited shipped rules, unverified token forms and paths not tested yet do not change the status. They are counted in the **Unverified** column instead.

### Columns and freshness

Columns: Organization, Status, Protected / targeted, Rollout, Broken, Unverified, Unavailable, Mode, Hits 24h, Hits 7d, Last hit, Active tokens, Last test and As of. A totals strip above the rows adds them up across the scope.

- **Hits and test results are live**: they are read when the board loads.
- **The coverage half of a row** (sensors, paths, rules, rollout, mode) is computed by the organization's daily run, and again whenever someone opens that organization's **Coverage** tab. It can be up to about a day old. **As of** says when it was computed. If a later computation failed, the row keeps the earlier numbers and shows **Last run failed** with the reason.
- **Protected** is the billed covered-sensor count of the last completed UTC day, at its peak. **Targeted** is the number of distinct sensors the enabled policies target.
- A count shown as `≥N` is a lower bound: the extension stopped counting at a bound, so the real number can be higher.
- **Mode** reads Live, or "Observing N of M" with the earliest end time, or "open-ended" when a policy observes with no `observe_until`.

**Details** on a row shows why it has its status, the top reasons, the requirement missing most often (for example "Subscribe ext-exfil"), up to 10 failing test paths, and links to the organization's Deception page and its cases.

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
