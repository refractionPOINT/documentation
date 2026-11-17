# Investigation Action Policies

An `investigation_policy` Hive record controls whether the Investigation Engine proposes, requests approval for, or automatically performs an action. The `autonomy` section is the action control. Track records show how decisions worked out; they do not enable or disable actions by themselves.

!!! note "Version support"
    This guide describes the policy-controlled actions interface. It requires server support for `pause_when`, `spot_check` and version 1 track-record reports. If the interface reports `upgrade_required`, upgrade support is needed before using these controls. SDK and CLI availability depends on the installed release; the YAML and public API names here do not imply that corresponding SDK methods or CLI commands are available in every released version.

## Choose an action mode

| Mode | Behavior |
|------|----------|
| `off` | Creates no proposal for the action. |
| `suggest` | Records what the engine would do, without changing the product. Use this for a dry run. |
| `approve` | Requires an authorized explicit approval before the approval deadline. |
| `auto` | Runs automatically when the effective policy, confidence, limits, permissions, evidence and target checks allow it. Configured guards and spot checks can hold it for review. |

There is no label-count requirement or separate route graduation, enablement or demotion step. Investigation intake settings decide what to investigate; they do not grant automatic action authority. Draft, shadow and test execution contexts remain read-only.

## Start with a visible policy

The following is the action section of the starter policy. It is the `data` of the `default` record in the `investigation_policy` hive. The record name is supplied separately, not as a YAML field. Merge this section into your existing policy while preserving identity, budgets, triggers, intake and other settings.

```yaml
autonomy:
  close.false_positive:
    mode: suggest
    min_confidence: 0.90
    max_targets_per_run: 3
    max_targets_per_hour: 50
    lease: 2h
    approval_timeout: 15m
    spot_check: "5%"
    pause_when:
      reopened: 3
      within: 7d
      by: people
      max_source_lag: 5m
  eradicate.*:
    mode: approve
  tag.remove:
    mode: approve
```

Starter content does not overwrite an installed policy. The explicit `approve` entries govern eradication and tag removal; check `undo_supported` before approving any action, since some operations have no undo.

To allow automatic false-positive closes, deliberately change the governing `close.false_positive` mode to `auto` after reviewing the proposed actions, permissions and effective policy. Removing `pause_when` removes the history-dependent guard. Omitting `spot_check` means `0%`; the starter's `5%` is an authored value you can change.

### Fields and defaults

Defaults below apply only after all matching policy entries have been combined.

| Field | Accepted value | Default when unresolved |
|-------|----------------|-------------------------|
| `mode` | `off`, `suggest`, `approve`, `auto` | `suggest` |
| `min_confidence` | Number from 0 through 1 | `0.85` |
| `max_targets_per_run` | Positive integer, at most 2147483647 | 3 for containment/eradication; otherwise unlimited |
| `max_targets_per_hour` | Positive integer, at most 2147483647 | 10 for containment/eradication; otherwise unlimited |
| `lease` | Positive duration | `2h` |
| `approval_timeout` | Positive duration | `15m` |
| `approvers` | Distinct principal/group identifiers, such as `group:soc-leads` | Any ordinarily authorized approver |
| `spot_check` | Percentage string from `0%` through `100%`, at most two decimal places | `0%` |
| `pause_when` | Reopening guard, on the literal `close.false_positive` entry only | No history dependency |

Author caps as positive integers; `0` appears only in resolved reports to mean unlimited. `approvers: []` explicitly permits nobody. It does not restore unrestricted approval. Identifiers must be nonempty, contain no whitespace/control characters and fit within 256 UTF-8 bytes.

Supported concrete classes are `close.false_positive`, `contain.network`, `contain.process`, `contain.identity`, `contain.email`, `contain.seal`, `tag`, `tag.add`, `tag.remove`, `eradicate.process`, `eradicate.file`, `collect.memory`, `collect.file` and `collect.artifact`. Patterns such as `*`, `contain.*` and `eradicate.*` match supported classes; matching a pattern does not create a new operation.

### How multiple records combine

Every applicable entry contributes restrictions. The lowest mode wins in the order `off`, `suggest`, `approve`, `auto`; confidence uses the highest minimum; positive target caps, lease and approval timeout use the lowest value. Present approver lists intersect, spot-check percentages use the highest value, and every guard remains applicable. An empty approver intersection limits the effective mode to at most `suggest`, with reason `policy_no_approvers`.

A named record cannot loosen a matching restriction from `default`. For example, adding `mode: auto` to a named record will not override `mode: suggest` in a matching default entry. Review the contributing records and `field_sources` in the track record to find the restriction to edit.

Scope a named record using record-level `match`, as in this fictional `review-mail-triage` record:

```yaml
match:
  run: template == "fictional-mail-triage"
autonomy:
  close.false_positive:
    mode: suggest
```

`template` is the plan's Hive record name. `match.run` and `match.target` belong to the record, never inside an action entry. Missing match attributes do not exempt an action from a potentially applicable restriction. There can be at most 32 potentially applicable guard predicates across an organization's policy set.

## Pause after reopenings

In the starter example, `pause_when` holds automatic false-positive closes after three distinct subjects have been deliberately reopened by people within the last seven days. A subject is a case or a mail message. Three reopenings of one case count as one subject; three cases reopened by one person can count as three.

The guard counts reopenings after confirmed engine closes within the organization, template and concrete action class, across recipe/model versions and the products that scope depends on. A grouped case counts once regardless of its linked detections. Recloses do not erase the earlier reopen history. Deliberate undo, including a preference undo, counts; automatic lease expiry/recovery rollback, failed changes, no-ops and replayed events do not. A dispute label alone is reported separately from a reopening.

| Guard field | Meaning and bounds |
|-------------|--------------------|
| `reopened` | Required integer threshold, 1 through 1000 distinct subjects. |
| `within` | Required rolling window, `1h` through `30d`. |
| `by` | Required `people` or `anyone`. |
| `max_source_lag` | Allowed live source lag, `1m` through `1h`; defaults to `5m`. |

`people` counts authenticated users without declared AI session/client context. `anyone` also includes API keys, AI sessions, services and unknown provenance. An API key reopening does not affect a `people` guard, but can affect an `anyone` guard. Attribution comes from authenticated identity; display names do not establish that someone is a person.

At time `t`, the window excludes exactly `t - within` and includes `t`. The hold is recalculated from policy and history, with reason `policy_reopen_guard`, and clears for new automatic actions when the count falls below the threshold. A held action stays a suggestion: it never automatically executes because the window expires or policy is loosened. An authorized explicit approval can proceed while the guard hold is shown. A hold does not retroactively undo completed actions.

### Live source health and historical coverage

A configured guard holds automatic effects with `policy_history_unavailable` when a required source is unavailable, has not completed its initial scan, or has lag or an unresolved gap older than `max_source_lag`. Lag equal to the limit is allowed. The configured bound describes evaluation against ingested history, not instantaneous knowledge of external changes.

There is **no history warm-up period**. A completed, current initial scan can clear the guard immediately, even if collection began today and no reopenings exist. Reports show `history_from` and `coverage.complete` so you can see the available history. Limited historical coverage alone does not hold actions. With no `pause_when`, reporting/history outages do not introduce a history-based execution hold.

## Hold a sample for review

`spot_check: "5%"` selects a five-percent sample of otherwise automatic actions to hold as suggestions for manual review. It does not execute first and ask for review afterward. Reviewers see the proposed operation and the reason for the hold.

Sampling is deterministic for a run, template, action class and subject within the organization. Retries do not reroll it. `0%` holds none through sampling; `100%` holds all otherwise automatic actions. The percentage is a sampling rate, not a promise that exactly five out of every hundred actions will be held. Sampling percentages combine by maximum across applicable entries.

## Emergency pause and resume

To pause automatic actions organization-wide while continuing to see suggestions, create an enabled, unscoped `investigation_policy` record named `autonomy-manual-pause` with this `data`:

```yaml
autonomy:
  "*":
    mode: suggest
```

The console's manual pause uses this same record. It combines with all other policies; entries already set to `off` remain off. This pauses automatic execution, while authorized explicit approvals remain possible. Use `mode: off` in the applicable policy if you also need to suppress proposals. Existing confirmed effects require their normal undo or remediation procedure.

To resume, delete `autonomy-manual-pause` using normal Hive deletion permissions. The remaining policy determines what new actions may do. Removing the record does not release previously held suggestions into automatic execution.

If Git Sync manages this hive, coordinate the pause with your repository and sync selection. An apply that deletes selected records absent from git could remove a console-created pause; a pause still present in git could be recreated after a console resume. Preserve the pause in the authoritative configuration until you deliberately resume. See [Git Sync](../../5-integrations/extensions/limacharlie/git-sync.md#investigation-policies-and-plans).

## Read the track record and who reopened

Use these public read-only API paths, with the normal authenticated organization context:

| Endpoint | Purpose |
|----------|---------|
| `GET /v1/investigate/{oid}/track-record` | Resolved policy, contributors, guards, history coverage, decisions, assessments and reopening counts. |
| `GET /v1/investigate/{oid}/track-record/reopenings` | Paginated reopening metadata with authenticated principal category and opaque actor/subject references. |

Both return `schema_version: 1`, an `as_of` snapshot and `next_cursor` (empty on the last page). Filters are `product` (`cases` or `mailsec`), `template`, `action_class`, `from`, `to`, `limit` and `cursor`. Aggregate reports also accept `route_id`; reopening details instead accept `by` (`people` or `anyone`, default `anyone`). Time filters use RFC3339 timestamps, default to the last seven days, and must stay within the last 30 days with a positive interval no longer than 30 days. Page size is 1 through 200, default 100.

Continue with the opaque cursor and matching filters; cursors expire after 15 minutes. On `cursor_expired`, restart the report. Unknown, repeated or empty filter values are rejected. Do not infer missing rows from a short page.

Read the report with these distinctions in mind:

- **Policy and guards:** `policy.sources`, `field_sources` and `guards` explain every contributing restriction. A guard spans its template/action and dependent products even when report counts are filtered to one route or product. A guard count marked `count_is_lower_bound` means “at least this many,” since counting can stop at its threshold.
- **Decision quality:** `agreement.numerator` and `agreement.denominator` describe independently labeled observations. A zero denominator means unknown. Unlabeled decisions are not agreements; reopening by an API key is operational history, not a human training label. Missing pricing is unknown, not zero cost.
- **Subjects versus events:** `reopened_subjects` counts distinct subjects in the report interval. `reopen_events_by_principal` counts deduplicated transitions, so event counts can exceed subject counts.
- **Who reopened:** `principal_type` is `user`, `api_key`, `ai_session`, `service` or `unknown`. AI client context is separate, so a `user` event with `ai_client` does not qualify for `people`. `actor_ref` and `on_behalf_of_ref` are opaque, tenant-scoped references, not raw account IDs or names.
- **Coverage:** Healthy live sources can have incomplete historical coverage. Reports can return HTTP 200 with degraded coverage and unknown guards; inspect those fields. If no truthful report snapshot can be served, `source_unavailable` is an error, not an empty success.

Track records do not change policy on their own. The authored `pause_when` rule is what makes reopening history affect automatic execution.

## Permissions and safe edits

| Operation | Required existing permission |
|-----------|------------------------------|
| Read aggregate reports | `investigation.get` |
| Include resolved policy and contributing records | Also `investigation_policy.get` |
| Read Cases reopening details | `investigation.get` |
| Read Mail reopening details | `investigation.get` and `mailsec.get` |
| Read mixed-product reopening details without a product filter | `investigation.get` and `mailsec.get` |
| Read or edit policy records | `investigation_policy.get` / `investigation_policy.set` |
| Delete a policy record, including resume after manual pause | `investigation_policy.del` |
| Close or undo a case | `investigation.set` under the execution credential |
| Close or undo mail disposition | `mailsec.set` under the execution credential |

A report reader without policy-read permission gets `policy_access: denied`, empty `policy_records`, `policy: null` and empty `guards`. This is not evidence that no policy applies. Detail requests without required product access fail rather than silently omitting a product. API keys can manage policy with the same grants; editing policy does not itself grant product execution permissions.

Save through native Hive operations with the version you read (compare-and-swap). Merge only intended changes and preserve unrelated fields. If someone else edited the record, reload and reconcile; do not force-overwrite. Policy changes can tighten an existing action, but loosening policy cannot promote an old held action to automatic execution. Existing receipt-based undo remains available with normal permissions even if policy is now `off`.

Validation rejects duplicate keys, multiple YAML documents, aliases/merge keys, null action fields, unknown action fields, wrong scalar types and out-of-range values. Guard durations use unsigned integer components with units `d`, `h`, `m`, `s`, `ms`, `us`, `ns`; `d` means 24 hours. For example, `7d` and `168h` are equivalent. Use a percentage string such as `"5.25%"`, not a numeric fraction. Validation errors include `error_code`, `error` and a JSON Pointer `path` into record `data`.

Legacy route-decision and autonomy mutation endpoints return `410 route_control_retired`; edit `investigation_policy` instead. Legacy `automation_routes` data grants no action authority. Review existing policy explicitly when changing versions rather than assuming previous route state will preserve the intended mode. If support is missing, controls are read-only with `upgrade_required`; a network outage is a separate error. Policy editing can remain usable during report outages when Hive supports the policy schema.

## Manage policies from Git

Store policy records under `hives.investigation_policy` and plans under `hives.investigation_plan`, each using the native `data` / `usr_mtd` wrapper. Enable and select the hives you intend to synchronize. Keep the complete existing record, including identity, intake and trigger settings, and user metadata. See [Git Sync investigation policies and plans](../../5-integrations/extensions/limacharlie/git-sync.md#investigation-policies-and-plans) for a fictional configuration example and conflict/pause handling.
