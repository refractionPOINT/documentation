# Investigation Action Policies

An `investigation_policy` Hive record controls whether the Investigation Engine proposes, requests approval for, or automatically performs an action. The `autonomy` section is the action control.

The policy record is the only thing that decides what the engine may do. Each action class has a mode (`off`, `suggest`, `approve` or `auto`) and limits, and the engine follows them. Nothing pauses, samples or promotes an action behind your back, and no history or score changes a decision. To pause everything, save the [`autonomy-manual-pause` record](#emergency-pause-and-resume). Every action keeps its undo and its audit trail.

!!! note "Version support"
    This guide describes the policy-controlled actions interface. If the interface reports `upgrade_required`, upgrade support is needed before using these controls. SDK and CLI availability depends on the installed release; the YAML and public API names here do not imply that corresponding SDK methods or CLI commands are available in every released version.

## Choose an action mode

| Mode | Behavior |
|------|----------|
| `off` | Creates no proposal for the action. |
| `suggest` | Records what the engine would do, without changing the product. Use this for a dry run. |
| `approve` | Requires an authorized explicit approval before the approval deadline. |
| `auto` | Runs automatically when the effective policy, confidence, limits, permissions, evidence and target checks allow it. The engine holds an action as a suggestion when a limit, permission, evidence or target check does not pass. |

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
  eradicate.*:
    mode: approve
  tag.remove:
    mode: approve
```

Starter content does not overwrite an installed policy. The explicit `approve` entries govern eradication and tag removal; check `undo_supported` before approving any action, since some operations have no undo.

To allow automatic false-positive closes, deliberately change the governing `close.false_positive` mode to `auto` after reviewing the proposed actions, permissions and effective policy.

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

Author caps as positive integers; `0` appears only in resolved reports to mean unlimited. `approvers: []` explicitly permits nobody. It does not restore unrestricted approval. Identifiers must be nonempty, contain no whitespace/control characters and fit within 256 UTF-8 bytes.

Supported concrete classes are `close.false_positive`, `contain.network`, `contain.process`, `contain.identity`, `contain.email`, `contain.seal`, `tag`, `tag.add`, `tag.remove`, `eradicate.process`, `eradicate.file`, `collect.memory`, `collect.file` and `collect.artifact`. Patterns such as `*`, `contain.*` and `eradicate.*` match supported classes; matching a pattern does not create a new operation.

### How multiple records combine

Every applicable entry contributes restrictions. The lowest mode wins in the order `off`, `suggest`, `approve`, `auto`; confidence uses the highest minimum; positive target caps, lease and approval timeout use the lowest value. Present approver lists intersect. An empty approver intersection limits the effective mode to at most `suggest`, with reason `policy_no_approvers`.

A named record cannot loosen a matching restriction from `default`. For example, adding `mode: auto` to a named record will not override `mode: suggest` in a matching default entry. Review the `investigation_policy` records that match the run to find the restriction to edit.

Scope a named record using record-level `match`, as in this fictional `review-mail-triage` record:

```yaml
match:
  run: template == "fictional-mail-triage"
autonomy:
  close.false_positive:
    mode: suggest
```

`template` is the plan's Hive record name. `match.run` and `match.target` belong to the record, never inside an action entry. Missing match attributes do not exempt an action from a potentially applicable restriction.

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

## Engine performance

The engine reports how it performed from its own records of runs and actions:

```
GET /v1/investigate/{oid}/stats
```

Query parameters, all optional: `template` (a template name), `since` and `until` (RFC 3339 timestamps, applied to when each run was created). It needs `investigation.get`. The report covers a capped number of the most recent matching runs; `window.truncated` is `true` when more matched, so narrow the window or the template for a complete picture.

It reports:

- Runs by state and by verdict, and time to verdict.
- AI cost and tokens, and search volume.
- Per-operator call counts, timings and errors.
- For each template and action type, how many actions were suggested, approved, denied, expired, executed automatically, failed, undone or held, and why they were held (`actions.by_template_class`).

An abridged example, with only the action section filled in beyond the headline counts:

```json
{
  "window": {"template": "phishing-triage", "runs_considered": 41, "truncated": false},
  "runs": {"total": 41, "by_state": {"completed": 30, "decided": 8, "cancelled": 3},
           "by_verdict": {"true_positive": 9, "false_positive": 28, "inconclusive": 2, "undecided": 2}},
  "time_to_verdict_ms": {"p50": 410, "p95": 2300, "samples": 39},
  "llm": {"usd": 0.31, "tokens": 91000},
  "actions": {
    "by_class_state": {"close.false_positive": {"executed": 7, "proposed": 2}},
    "by_template_class": [
      {
        "template": "phishing-triage",
        "action_class": "close.false_positive",
        "total": 12,
        "suggested": 3,
        "approved": 4,
        "denied": 1,
        "expired": 1,
        "auto_executed": 5,
        "failed": 0,
        "undone": 1,
        "held": 2,
        "held_by_reason": {"policy_no_approvers": 2},
        "by_state": {"executed": 8, "proposed": 2, "denied": 1, "expired": 1}
      }
    ]
  }
}
```

The counters in each `by_template_class` row are not a partition of `total`: an approved action can later be undone, so it counts under both. `held` counts an action once however many reasons held it, and `held_by_reason` counts it once under each reason, using the hold reason as recorded (for example `policy_no_approvers`). `by_state` always adds up to `total`.

From the command line:

```bash
limacharlie investigate stats --template phishing-triage --since 2026-11-01T00:00:00Z --until 2026-11-08T00:00:00Z --oid <OID> --output yaml
```

This is a report on how the engine performed: how much it ran, how fast, at what cost, and what became of the actions it proposed. It does not score whether its verdicts were right, and it does not change policy. Policy changes only when you edit the record.

## Permissions and safe edits

| Operation | Required existing permission |
|-----------|------------------------------|
| Read the engine performance report | `investigation.get` |
| Read or edit policy records | `investigation_policy.get` / `investigation_policy.set` |
| Delete a policy record, including resume after manual pause | `investigation_policy.del` |
| Close or undo a case | `investigation.set` under the execution credential |
| Close or undo mail disposition | `mailsec.set` under the execution credential |

API keys can manage policy with the same grants; editing policy does not itself grant product execution permissions.

Save through native Hive operations with the version you read (compare-and-swap). Merge only intended changes and preserve unrelated fields. If someone else edited the record, reload and reconcile; do not force-overwrite. Policy changes can tighten an existing action, but loosening policy cannot promote an old held action to automatic execution. Existing receipt-based undo remains available with normal permissions even if policy is now `off`.

Validation rejects duplicate keys, multiple YAML documents, aliases/merge keys, null action fields, unknown action fields, wrong scalar types and out-of-range values. Durations use unsigned integer components with units `d`, `h`, `m`, `s`, `ms`, `us`, `ns`; `d` means 24 hours, so `2h` and `120m` are equivalent. Validation errors include `error_code`, `error` and a JSON Pointer `path` into record `data`.

Legacy route-decision and autonomy mutation endpoints return `410 route_control_retired`; edit `investigation_policy` instead. Legacy `automation_routes` data grants no action authority. Review existing policy explicitly when changing versions rather than assuming previous route state will preserve the intended mode. If support is missing, controls are read-only with `upgrade_required`; a network outage is a separate error.

## Manage policies from Git

Store policy records under `hives.investigation_policy` and plans under `hives.investigation_plan`, each using the native `data` / `usr_mtd` wrapper. Enable and select the hives you intend to synchronize. Keep the complete existing record, including identity, intake and trigger settings, and user metadata. See [Git Sync investigation policies and plans](../../5-integrations/extensions/limacharlie/git-sync.md#investigation-policies-and-plans) for a fictional configuration example and conflict/pause handling.
