# Investigation Action Policies

An `investigation_policy` Hive record controls whether the Investigation Engine proposes, requests approval for, or automatically performs an action. The `autonomy` section is the action control.

The policy record is the only thing that decides what the engine may do. Each action class has a mode (`off`, `suggest`, `approve` or `auto`) and limits, and the engine follows them. Nothing pauses, samples or promotes an action behind your back, and no history or score changes a decision. To pause everything, save the [`autonomy-manual-pause` record](#emergency-pause-and-resume). Actions that support undo (`undo_supported`) keep it, and every action keeps its audit trail.

!!! note "Version support"
    This guide describes the policy-controlled actions interface. If the interface reports `upgrade_required`, upgrade support is needed before using these controls. SDK and CLI availability depends on the installed release; the YAML and public API names here do not imply that corresponding SDK methods or CLI commands are available in every released version.

## Choose an action mode

| Mode | Behavior |
|------|----------|
| `off` | Creates no proposal for the action. |
| `suggest` | Records what the engine would do, without changing the product. Use this for a dry run. |
| `approve` | Requires an authorized explicit approval before the approval deadline. |
| `auto` | Runs automatically, once the rule the action fires on decided, when the effective policy, limits, permissions, evidence and target checks allow it, and the action has a registered authorization; an action without one waits for a person (`no_registered_authorization`, see [Autonomy modes](../../investigation-engine/policies.md#autonomy-modes)). The engine holds an action as a suggestion when a limit, permission, evidence or target check does not pass, or when the approver lists leave nobody (`policy_no_approvers`). |

There is no label-count requirement or separate route graduation, enablement or demotion step. Investigation intake settings decide what to investigate; they do not grant automatic action authority. Draft, shadow and test execution contexts remain read-only.

## Start with a visible policy

The following is the action section of the starter policy. It is the `data` of the `default` record in the `investigation_policy` hive. The record name is supplied separately, not as a YAML field. Merge this section into your existing policy while preserving identity, budgets, intake and other settings.

<!-- validate: policy -->
```yaml
ai_may_decide:
  "*": "off"
autonomy:
  close.false_positive:
    mode: suggest
    max_targets_per_run: 3
    max_targets_per_hour: 50
    lease: 2h
    approval_timeout: 15m
  eradicate.*:
    mode: approve
  tag.remove:
    mode: approve
```

Starter content does not overwrite an installed policy. The explicit `approve` entries govern eradication and tag removal; check `undo_supported` before approving any action, since some operations have no undo.

To allow automatic false-positive closes, deliberately change the governing `close.false_positive` mode to `auto` after reviewing the proposed actions, permissions and the matching policy records. A close then runs by itself after `closed_by_rule`, and after `closed_by_ai` only for the templates where `ai_may_decide` lets the AI close. `ai_may_decide: {"*": "off"}` keeps every AI answer a recommendation (quote `"off"`: some YAML readers, including the one in current `limacharlie hive set` releases, turn a bare `off` into false, and the record is refused); see [What the AI may decide](../../investigation-engine/policies.md#what-the-ai-may-decide).

### Fields and defaults

Defaults below apply only after all matching policy entries have been combined.

| Field | Accepted value | Default when unresolved |
|-------|----------------|-------------------------|
| `mode` | `off`, `suggest`, `approve`, `auto` | `suggest` |
| `max_targets_per_run` | Positive integer, at most 2147483647 | 3 for containment/eradication; otherwise unlimited |
| `max_targets_per_hour` | Positive integer, at most 2147483647 | 10 for containment/eradication; otherwise unlimited |
| `lease` | Positive duration | `2h` |
| `approval_timeout` | Positive duration | `15m` |
| `approvers` | Distinct identities, each compared exactly with the person deciding: a user's email or an API key's name, such as `alice@example.com` | Any ordinarily authorized approver |

Author caps as positive integers. An approver list restricts approve, deny, extend and confirm; revert stays open to anyone with the action class permission. Groups are not expanded: list each person. `approvers: []` explicitly permits nobody. It does not restore unrestricted approval. Identifiers must be nonempty, contain no whitespace/control characters and fit within 256 UTF-8 bytes.

Supported concrete classes are `close.false_positive`, `contain.network`, `contain.process`, `contain.identity`, `contain.email`, `contain.seal`, `tag`, `tag.add`, `tag.remove`, `eradicate.process`, `eradicate.file`, `collect.memory`, `collect.file` and `collect.artifact`. Patterns such as `*`, `contain.*` and `eradicate.*` match supported classes; matching a pattern does not create a new operation.

### How multiple records combine

Every applicable entry contributes restrictions. The lowest mode wins in the order `off`, `suggest`, `approve`, `auto`; positive target caps, lease and approval timeout use the lowest value. Present approver lists intersect. An empty approver intersection limits the effective mode to at most `suggest`, with reason `policy_no_approvers`.

A named record cannot loosen a matching restriction from `default`. For example, adding `mode: auto` to a named record will not override `mode: suggest` in a matching default entry. Review the `investigation_policy` records that match the run to find the restriction to edit.

Scope a named record using record-level `match`, as in this fictional `review-mail-triage` record:

<!-- validate: policy -->
```yaml
match:
  run: template == "fictional-mail-triage"
autonomy:
  close.false_positive:
    mode: suggest
```

`template` is the plan's Hive record name. `match.run` and `match.target` belong to the record, never inside an action entry. Missing match attributes do not exempt an action from a potentially applicable restriction.

## Starting investigations

The policy has no setting that starts an investigation. A person, an API client or a D&R rule starts each run; a new case starts one through a D&R rule on the `case_created` event. A `triggers` block left in an older record is ignored, and saving it is refused (`policy_unknown_field`). See [Automatic Starts](../../investigation-engine/automation.md).

## Emergency pause and resume

To pause automatic actions organization-wide while continuing to see suggestions, create an enabled, unscoped `investigation_policy` record named `autonomy-manual-pause` with this `data`:

<!-- validate: policy -->
```yaml
autonomy:
  "*":
    mode: suggest
```

The console's manual pause uses this same record. It combines with all other policies; entries already set to `off` remain off. This pauses automatic execution, while authorized explicit approvals remain possible. Use `mode: off` in the applicable policy if you also need to suppress proposals. Existing confirmed effects require their normal undo or remediation procedure.

To resume, delete `autonomy-manual-pause` using normal Hive deletion permissions. The remaining policy determines what new actions may do. Removing the record does not release previously held suggestions into automatic execution.

If Git Sync manages this hive, coordinate the pause with your repository and sync selection. An apply that deletes selected records absent from git could remove a console-created pause; a pause still present in git could be recreated after a console resume. Preserve the pause in the authoritative configuration until you deliberately resume. See [Git Sync](../../5-integrations/extensions/limacharlie/git-sync.md#investigation-policies-and-plans).

## Engine performance

`GET /v1/investigate/{oid}/stats` reports, from the engine's own records, what it did with the actions this policy allowed: per template and action class, how many were suggested, approved, denied, expired, executed automatically, failed, undone or held, and why they were held. It needs `investigation.get`, `insight.evt.get` and `investigation_policy.set`. It does not score whether outcomes were right, and it does not change policy. See [Stats](../../investigation-engine/api-reference.md#stats).

## Permissions and safe edits

| Operation | Required existing permission |
|-----------|------------------------------|
| Read the engine performance report | `investigation.get`, `insight.evt.get` and `investigation_policy.set` |
| Read or edit policy records | `investigation_policy.get` / `investigation_policy.set` |
| Delete a policy record, including resume after manual pause | `investigation_policy.del` |
| Close or undo a case | `investigation.set` under the execution credential |
| Close or undo mail disposition | `mailsec.set` under the execution credential |

API keys can manage policy with the same grants; editing policy does not itself grant product execution permissions.

Save through native Hive operations with the version you read (compare-and-swap). Merge only intended changes and preserve unrelated fields. If someone else edited the record, reload and reconcile; do not force-overwrite. Policy changes can tighten an existing action, but loosening policy cannot promote an old held action to automatic execution. Existing receipt-based undo remains available with normal permissions even if policy is now `off`.

Validation rejects the removed fields (`min_confidence` on an action entry, the whole `decision` section with its thresholds and mandatory checks) with `policy_unknown_field`. A record that is already stored with them keeps loading: the engine ignores them and reports `legacy_policy_fields_ignored`. Validation also rejects duplicate keys, multiple YAML documents, aliases/merge keys, null action fields, unknown action fields, wrong scalar types and out-of-range values. Durations use unsigned integer components with units `d`, `h`, `m`, `s`, `ms`, `us`, `ns`; `d` means 24 hours, so `7d` and `168h` are equivalent. Validation errors include `error_code`, `error` and a JSON Pointer `path` into record `data`.

Legacy route-decision and autonomy mutation endpoints return `410 route_control_retired`; edit `investigation_policy` instead. Legacy `automation_routes` data grants no action authority. Review existing policy explicitly when changing versions rather than assuming previous route state will preserve the intended mode. If support is missing, controls are read-only with `upgrade_required`; a network outage is a separate error.

## Manage policies from Git

Store policy records under `hives.investigation_policy` and plans under `hives.investigation_plan`, each using the native `data` / `usr_mtd` wrapper. Enable and select the hives you intend to synchronize. Keep the complete existing record, including identity, intake and other settings, and user metadata. See [Git Sync investigation policies and plans](../../5-integrations/extensions/limacharlie/git-sync.md#investigation-policies-and-plans) for a fictional configuration example and conflict/pause handling.
