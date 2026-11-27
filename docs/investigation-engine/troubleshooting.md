# Troubleshooting

Every refusal and error of the Investigation Engine, and what to do about it.

## How an error looks

```json
{"error": "<message for a person>", "error_code": "bad_request", "http_status": 400, "reason_code": "no_template_applies"}
```

| Member | Meaning |
|---|---|
| `error` | A message for a person. It can quote your request; never parse it. |
| `error_code` | The kind of refusal (below). A failure of the gateway itself has none. |
| `http_status` | The same as the HTTP status. |
| `reason_code` | On a refused start, the specific cause (below). Treat an absent or unknown one as a generic refusal. |
| `path` | On a refused settings field, a JSON Pointer to it. |
| `errors`, `warnings` | On a refused template or wave: coded issues with `code`, `path`, `message` and often `suggestion`. |
| `details` | Extra structured fields of a refusal (for example the `fields` of an invalid agent answer, or the `candidates` of an ambiguous flush). |

## Why a start was refused: `reason_code`

| `reason_code` | `error_code` (HTTP) | Cause | What to do |
|---|---|---|---|
| `no_template_applies` | `bad_request` (400) | No **active** template's `applies_to` matches the trigger. | Activate one whose `applies_to` covers the alert, or name a template. See [How templates are chosen](templates.md#how-templates-are-chosen). |
| `unknown_template` | `bad_request` (400) | The named template does not exist, or its record does not load. | Fix the name, or the record (`templates list --oid ...` with the API's `stored=true` shows `load_error`). |
| `check_missing`, `check_not_callable`, `check_invalid`, `check_cycle`, `check_depth_limit`, `check_size_limit`, `check_not_startable` | `bad_request` (400) | A check the template calls is gone or does not validate, or a check was named as the template. | Fix the check, then validate the caller. |
| `inline_plan_not_allowed` | `bad_request` (400) | A start without a person brought an inline plan. | Name a stored template. |
| `no_policy_identity` | `bad_request` (400) | The settings name no secret identity for a run without a person. | Set `identity.default` in the [settings](settings.md#identity). |
| `identity_secret_unavailable` | `bad_request` (400) | The secret is missing, disabled or empty, or holds a key the platform refuses (a user API key, a deleted key). | Store an **organization** API key in it and enable it. |
| `case_invalid` | `bad_request` (400) | A case start whose case number is not valid. | Check the rule's `case` value. |
| `template_draft` | `forbidden` (403) | The template is a draft. | A person promotes it. |
| `identity_not_allowed` | `forbidden` (403) | The request named an identity the settings do not allow for this template. | Use the template's default identity, or add it to `identity.allow`. |
| `case_unreadable` | `forbidden` (403) | The run identity may not read the case. | Grant it `investigation.get` and `investigation.set`. |
| `case_not_found` | `not_found` (404) | The case does not exist for that identity. | Check the number and the identity's access. |
| `own_case` | `own_case` (409) | The engine wrote that case: a run without a person never starts in it. | Nothing: this is the loop guard. A person can still investigate the case. |

A start is never refused for the organization's load: above `limits.max_parallel_runs` it
waits in the [run queue](run-queue.md). Only an hourly cap you set (`limits.runs_per_hour`)
records starts above it as `capped`, not investigated.

## Error codes

| `error_code` | HTTP | Meaning | What to do |
|---|---|---|---|
| `bad_request` | 400 | Malformed or invalid arguments; the message says which. | Fix the request. |
| `forbidden` | 403 | Adding inputs to a run another identity started; an agent answer with the wrong token. | Have the starter add inputs. |
| `not_found` | 404 | The run, action, test, case document or agent request does not exist, or retention removed it. | Check the id. |
| `conflict` | 409 | The state does not allow it: the run has finished, or the action is not in a state that takes that verb (the message names it). | Read the run or action and decide again. |
| `already_answered`, `deadline_passed`, `not_waiting` | 409 | An AI agent answer that comes too late or twice. | Nothing to retry. |
| `invalid_answer` | 400 | An AI agent answer that does not match the step's `returns`; `fields` says which. | Fix and send again before the deadline. |
| `too_many_runs` | 429 | A wave or a test above the organization's parallel limit. | Retry later. |
| `not_implemented` | 501 | The feature is not available on this deployment (for example the run queue or agent answers on an engine that predates them). | Nothing to fix on your side. |
| `unavailable` | 503 | Storage or a dependency did not answer. | Retry. |
| `policy_unknown_field`, `policy_type`, `policy_range`, `policy_enum`, `policy_null`, `policy_record_name`, ... | 400 | A settings field (in the record, or a run's `overrides`) is not valid; `path` names it. A removed field's message names what replaced it. | Fix the field. See the [settings record](../7-administration/config-hive/investigation-policy.md). |

Failures of the gateway itself, with no `error_code`:

| Status | When |
|---|---|
| `401` | A permission is missing; the message names it. |
| `403` | The API key has no key id, or the action has no permission mapping. |
| `404` | The Investigation Engine is not enabled on this API host. |
| `413`, `414` | The body is over 8 MiB, or the query string over 8 KiB. |
| `502`, `504` | The engine did not answer, or timed out. A write may or may not have happened: read before you repeat it. |
| `503` | The Investigation Engine is not available for this organization. |

## A D&R rule matched but no investigation started

A rule's `start investigation` never blocks the rule. When a start is refused for a reason
you can fix, or could not be delivered, a record appears on the organization's **Errors**
page under the rule's name, at most once every 30 minutes per rule and cause. A refusal
never disables the rule.

| Message on the Errors page | What to do |
|---|---|
| `start investigation: no active investigation template applies to this trigger. ...` | Activate a template, or add `template: <name>` to the rule. |
| `start investigation: the template named in the rule does not exist. ...` | Fix the name, or install the template. |
| `start investigation: a rule cannot start an inline plan. ...` | Name a template. |
| `start investigation: the investigation policy names no identity for runs started by rules. ...` | Set `identity.default` in `investigation_policy/default`. |
| `start investigation: the secret the investigation policy names as the identity ... is missing, disabled, empty or refused. ...` | Store an organization API key in that secret. |
| `start investigation: the case number is not valid for this start. ...` | Check the rule's `case` value. |
| `start investigation: the template is a draft, and a rule can only start an active template. ...` | A person promotes the template. |
| `start investigation: the identity requested is not allowed ... for this template. ...` | Check `identity` in the settings. |
| `start investigation: the identity ... may not read the case. ...` or `the case was not found ...` | Grant the identity `investigation.get` and `investigation.set`; check the case. |
| `start investigation: the Investigation Engine did not confirm the start (unreachable or busy for 15 minutes, this host's retry buffer was full, or the host was shutting down), ...` | The alert may not have been investigated. Start it by hand if it matters, and check the engine's status. |
| `start investigation: an attempt to start an investigation ... was refused before it reached the Investigation Engine ...` | The request was malformed or too large: check the rule's `inputs` (at most 64 KiB) and `coalesce_key` (at most 256 bytes). |

(The messages still say "investigation policy": that is the `investigation_policy/default`
settings record.)

The rule's own restrictions also apply: an event from a sensor with an `acl:` tag the
rule's `acl_scopes` does not cover is refused before the start (see
[Automatic Starts](automation.md#sensors-with-resource-acl-tags)).

These produce no record:

- The engine refused a case it wrote itself (`own_case`): the loop guard working.
- The rule's `case` value did not render to a case number: the action fails for that
  event (`start investigation: case did not render to a case number`).
- Cases did not deliver the event. Cases delivers its events on a best-effort basis; start
  the run from the case page when you need it.

A rule that uses `start investigation` cannot be saved where the engine is not enabled
(`start investigation is not enabled in this environment`).

## Queued, flushed and capped starts

| You see | It means | Do |
|---|---|---|
| Runs in `queued` for a long time | The organization is at `limits.max_parallel_runs`. | Read `limacharlie investigate queue`: which rule or template is filling it. Flush a noisy rule, or raise the limit. |
| Runs in `capped` | The hourly cap (`limits.runs_per_hour`) was reached; those alerts were not investigated. | Raise or remove the cap, or fix the rule that fired so often. |
| Runs in `flushed` | Someone flushed them (`flushed.by_actor`, `note`). | Nothing; the audit log has the flush. |
| A flush answered `flushed: 0` with `rule_not_queued: true` | Nothing of that name was queued. | Use a name from `queued_rules`. |
| A flush refused with `rule_ambiguous` | The bare rule name is queued under several namespaces. | Name one of the `candidates`. |
| A run `failed` with `template_gone` or `template_draft` | The template was deleted, stopped matching, or became a draft while the start waited. | Fix the template; start again if needed. |

## Outcomes at a glance

| `verdict.outcome` | A person... |
|---|---|
| `closed_by_rule`, `escalated_by_rule` | ...reads the rule's sentence (`decided_by.say`). The actions did what their entries say. |
| `closed_by_ai`, `escalated_by_ai` | ...knows the AI decided, because the template's `ai_may_decide` allows it. Each action followed its own `approval`. |
| `ai_recommends_benign`, `ai_recommends_malicious` | ...decides: the entries that name the recommending rule wait for a person (`ai_recommendation`). |
| `couldnt_tell` | ...reads `verdict.missing` and answers its `ask`, or fixes the cause. |
| `conflict` | ...decides, and fixes the rules. |

## A run finished but the outcome means little

| You see | It usually means | Do |
|---|---|---|
| Steps `unknown` with reason `forbidden` | The run identity may not read that data. | Grant its key the permission (`settings get` lists `missing_grants` per template). |
| Steps `unknown` with reason `acl_restricted` or `not_found_or_restricted` | The sensor has an `acl:` tag the run key is outside of. | Add the key to the scope. See [ACL-scoped sensors](permissions.md#acl-scoped-sensors). |
| A `lookup.get` step `unknown(not_found)` | The Lookup does not exist yet. | Create it. |
| `ask_ai` steps or the review `unknown(llm_agent_not_found)` | No AI agent: the settings' `llm.agent` names none and the deployment has no default. | Create an `ai_agent` record and set `llm.agent`. |
| A Playbook step `unknown(playbook_identity_disabled)` or `unknown(playbook_unsupported)` | The Playbook extension on this deployment does not run Playbooks as the engine's identity yet. Nothing ran. | Nothing in the template to fix. |
| A Playbook step `unknown(not_read_only)` | The record no longer says `read_only: true`, or changed. | Fix the record, or move the Playbook to `act`. |
| An AI agent step `unknown(agent_unavailable)` | The session could not start: no record, the run key lacks `ai_agent.get`, no credentials. | Grant `ai_agent.get`; check the record. |
| An AI agent step `unknown(timeout)` | No answer by the step's deadline. | Check that the session can answer (`investigate_answer` MCP tool, or a CLI with `investigate answer`). |
| An AI agent step `unknown(agent_depth)` | The run was started from an agent's session or with an agent's key: such a run asks no agent. | Nothing: this is the loop guard. |
| Steps `skipped` (`only_if_false`, `condition_unknown`, `dependency_skipped`) | A step's `only_if` was false, or a step it reads failed. | Fix the first step that failed; its `reason` says why. |
| Many `couldnt_tell` | The rules miss the fact that decides, or the data is often incomplete. | Test on past alerts and read `unknown_reasons`. |
| A check call `unknown` with `check_couldnt_tell`, `check_conflict` | The check did not decide. | Read what it was missing. A rule that reads it is unknown, never false. |
| `case_error` on the run | The case could not be written. `case_error_code` says why (`cases_access_denied`: grant `ext.request`; `credentials_unavailable`; `cases_unavailable`: usually passes). | Fix the cause the code names. |

## An action did not do what you expected

| You see | It means | Do |
|---|---|---|
| `awaiting_approval`, `approval_reason: approval_required` or `approval_condition` | The entry says so. | Approve or deny it, or change the entry. |
| `awaiting_approval`, `approval_reason: paused` | The organization is paused. | Decide it; resuming does not wake it. |
| `awaiting_approval`, `approval_reason: circuit_breaker` | The organization's or the run's cap of automatic containments was reached; the history note names it. | Decide it. If the cap is too low for your templates, raise `circuit_breaker`. |
| `awaiting_approval`, `approval_reason: ai_recommendation` | The AI recommended it and the template does not let the AI decide. | Decide it, or set `ai_may_decide` in the template. |
| `awaiting_approval`, `approval_reason: settings_unavailable` | The settings could not be read at that moment. | Decide it. |
| `suggested` | A draft template, an inline plan, or the template changed since the run started. Never executed, never approvable. | Promote the template; later runs act. |
| `failed` with `not sent: ...` | The platform proved the request was refused before delivery. Nothing ran. | Fix what the sentence names (permissions, the record, the extension). |
| `failed` with `permission_denied: ...` | The run key lacks the action's permission. | Grant it (the note names it). |
| `uncertain` | The outcome is not known. With an undo it is undone to be safe; without, a person decides. | Check the target yourself before retrying. |
| `held`, `held_reason: on_lease_end_hold` or `lease_check_max` | The lease ended and the entry keeps it for a person. | Confirm, extend or undo it. |
| `held`, `held_reason: close_unconfirmed` | The product did not confirm the close. | Undo it, or leave it. |
| `withheld`, `already_decided` | A person already decided the case or message. Nothing changed. | Nothing: a person's decision wins. |
| A tag stayed on the sensor | A tag holds no lease; it lasts its `ttl`, or until removed. | Set `attrs.ttl`, or undo the action. |
| `extend` or `confirm` answers `409` on a tag | A tag holds no lease. | `revert` removes it. |
| An undo `failed` with `acl_restricted` | The target sensor is outside the run key's ACL scopes. | Add the key to the scope, then retry the undo. |
| A "check again" never releases | An argument was read from incomplete evidence (`on_lease_end.args_incomplete`), or the check never closes. | Read `lease_checks` for each outcome; fix the check or its arguments. |

## A template is refused when you save or validate it

| Code | Cause | Do |
|---|---|---|
| `missing_approval` | An `act` entry has no `approval`. | Add `approval: none`, `required` or `{when: ...}`. |
| `act_class_renamed` | An `act` entry says `class`. | Rename it `do` and add `approval`. |
| `missing_lease`, `missing_on_lease_end`, `lease_not_allowed` | A leased action without its lease, or a lease on an action that holds none. | See [Leases](actions.md#leases-and-what-happens-when-they-end). |
| `bad_on_lease_end`, `bad_lease_max`, `lease_check_not_check` | A malformed "check again". | `check`, `max` and `at_max` are required; `check` names a `kind: check` template. |
| `bad_undo`, `action_not_supported`, `unknown_action_class` | An `undo` on a built-in action, or an action that does not exist. | See [What an action can do](actions.md#what-an-action-can-do). |
| `playbook_not_read_only`, `playbook_sdk_version`, `agent_not_read_only` | A step's Playbook or agent record is not marked read-only, or the Playbook is not SDK v5. | Fix the record, or call it from `act`. |
| `extension_request_removed` | A step uses `extension.request`. | Call the extension from `act`, or read through a Playbook step. |
| `legacy_template_format` | An earlier format (`facts`, `proofs`, `respond`, ...). | Rewrite it. |
| `unknown_reference`, `bad_reference` | A step reads `$name` the starting point does not provide, or a rule or `act` entry reads `$?name`. | Derive the value with a step. |
| `close_rests_on_no_answer` | A close rule rests on `not is_ok(step)`. | Escalate on it, or close on what answered. |
| `no_verdict_path` | No rule and no `ai_review`. | Add one. |
| `agent_budget_exceeded`, `agent_wait_exceeds_budget` | AI agent budgets or deadlines do not fit the settings. | Lower them, or raise `budgets.max_agent_usd_per_run` / `max_wall_seconds`. |

The full list, with the fix for each code, is in the kit:
`limacharlie investigate kit --section codes`.

## Settings warnings

`limacharlie investigate settings get` returns `warnings`:

| Warning | Meaning |
|---|---|
| `settings_rejected` | The stored record does not parse. The engine keeps its last good copy (or runs the organization paused with no identity); `rejection` names the field. |
| `settings_field_ignored` | The record still carries `budgets.max_concurrent_runs`; it is not read. Remove it and set `limits.max_parallel_runs`. |
| `settings_record_ignored` | The hive holds an enabled record other than `default`; it is ignored. |
| `settings_unavailable` | The record could not be read now; automatic actions wait. |
