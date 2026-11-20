# Troubleshooting

Every refusal and error of the Investigation Engine, and what to do about it. The
other pages link here instead of repeating these tables.

## How an error looks

A refused API call returns an HTTP status and a JSON body:

```json
{"error": "<message for a person>", "error_code": "bad_request", "http_status": 400, "reason_code": "no_template_applies"}
```

| Member | Present | Meaning |
|---|---|---|
| `error` | Always | A message for a person. It can quote values from your request; never parse it. |
| `error_code` | When the engine refused the call | The kind of refusal (table below). A failure of the gateway itself has no `error_code`. |
| `http_status` | When the engine refused the call | The same as the HTTP status. |
| `reason_code` | On a refused start, when there is one specific cause | Why the start was refused (table below). Treat an absent or unknown value as a generic refusal. |
| `path` | On a refused policy field | A JSON Pointer to the field, such as `/autonomy/contain.network/mode`. |
| `errors`, `warnings` | On a refused template or wave | Coded issues, each with `code`, `path`, `message` and often `suggestion`. |

## Why a start was refused: `reason_code`

These apply to every way of starting a run: a person through the API, the console,
the CLI or MCP, and a D&R rule. The console shows a hint and a link to the page that
fixes each one.

| `reason_code` | `error_code` (HTTP) | Cause | What to do |
|---|---|---|---|
| `no_template_applies` | `bad_request` (400) | No **active** template's `applies_to` matches the trigger. | Activate a template whose `applies_to` covers the alert, or name a template. See [How templates are chosen](templates.md#how-templates-are-chosen). |
| `unknown_template` | `bad_request` (400) | The request names a template the organization does not have. | Fix the name, or install the template. |
| `inline_plan_not_allowed` | `bad_request` (400) | A start without a person brought an inline plan. | Name a stored template. |
| `no_policy_identity` | `bad_request` (400) | The policy names no secret identity for a run without a person. | Set `identity.default` (a `hive://secret/<name>`) in the `default` policy, or `identity.templates.<name>.default`. See [Run identity](policies.md#run-identity). |
| `identity_secret_unavailable` | `bad_request` (400) | The secret the policy names is missing, disabled or empty, or holds a key the platform refuses (a user API key, a deleted key). | Store an **organization** API key in that secret and enable it. |
| `case_invalid` | `bad_request` (400) | A case start whose case number is not valid. | Check the rule's `case` value: it must render to a case number. |
| `template_draft` | `forbidden` (403) | The template is a draft. Only a person can start a draft. | A person makes it active (**Make active** in the console). |
| `identity_not_allowed` | `forbidden` (403) | The request named an identity the policy does not allow for this template. | Name the template's default identity, or add it to `identity.allow`. |
| `case_unreadable` | `forbidden` (403) | The policy's identity may not read the case. | Give that identity `investigation.get` (and `investigation.set` to write the case). |
| `case_not_found` | `not_found` (404) | The case does not exist for the policy's identity. | Check the case number and the identity's access. |
| `own_case` | `own_case` (409) | The engine wrote that case itself: a run started without a person never starts in it. | Nothing: this is the loop guard. A person can still investigate the case. |
| `too_many_runs` | `too_many_runs` (429) | The organization is at `budgets.max_concurrent_runs`. | Wait for runs to finish, cancel one, or raise the budget. |

## Error codes

| `error_code` | HTTP | Meaning | What to do |
|---|---|---|---|
| `bad_request` | 400 | Malformed or invalid arguments; the message says which. | Fix the request. |
| `forbidden` | 403 | Refused by the engine: adding inputs to a run another identity started, or deciding an action as someone who is not on the class's `approvers` list (the message names the verb). | Have the starter add inputs, or have an approver decide. Revert is open to anyone with the class permission. |
| `not_found` | 404 | The run, action, test or case document does not exist, or retention removed it. | Check the id. A run's case document is `404` until the run has written one. |
| `conflict` | 409 | The state does not allow it: the run has finished, or the action is not in the right state (for example approving an `expired` action). | Read the run or action and decide again. |
| `own_case` | 409 | See `own_case` above. | Nothing. |
| `too_many_runs` | 429 | The concurrent run cap. | Retry later. |
| `not_implemented` | 501 | The feature is not available. | Nothing to fix on your side. |
| `unavailable` | 503 | Storage, the secret store or another dependency did not answer. | Retry. |
| `policy_unknown_field`, `policy_type`, `policy_range`, `policy_enum`, `policy_duration`, `policy_null`, `policy_duplicate_key`, `policy_alias`, `policy_syntax`, `policy_approver`, `policy_required` | 400 | A policy field (in a record, or in a request's `overrides`) is not valid. `path` names it. | Fix the field. See [Validation](../7-administration/config-hive/investigation-policy.md#permissions-and-safe-edits). |
| `route_control_retired` | 410 | A retired pause/resume or route control was called. | Use the `autonomy-manual-pause` record instead. See [Emergency pause](../7-administration/config-hive/investigation-policy.md#emergency-pause-and-resume). |

Failures of the gateway itself, with no `error_code`:

| Status | When |
|---|---|
| `401` | A permission is missing. The message names it: `unauthorized: missing permission investigation.set`. |
| `403` | The API key has no key id: `this API key has no key id, so it cannot own investigation runs`. Or no permission is mapped for an action class (unknown class). |
| `400` | A malformed id, query string, body or long-poll parameter. |
| `404` | The Investigation Engine is not enabled on this API host: every route is an unknown path. |
| `410` | `route_control_retired`, as above. |
| `413`, `414` | The body is over 8 MiB, or the query string over 8 KiB. |
| `415` | The body is not uncompressed `application/json`. |
| `502` | `investigation engine unavailable`. Retry. |
| `503` | `the investigation engine is not available for this organization`. |
| `504` | `investigation engine timed out`. A write may or may not have happened: read before you repeat it. |

## A D&R rule matched but no investigation started

A rule's `start investigation` never blocks the rule and never reports its outcome to
the rule itself. When the engine refuses a start for a reason you can fix, a record
appears on your organization's **Errors** page, under the rule's name. Each record is
written at most once every 30 minutes per rule and cause, and a refusal never disables
the rule.

| Message on the Errors page | What to do |
|---|---|
| `start investigation: no active investigation template applies to this trigger. Activate a template whose applies_to matches it, or name a template in the rule.` | Activate a template, or add `template: <name>` to the rule. |
| `start investigation: the template named in the rule does not exist. Create it, or fix the name in the rule.` | Fix the name, or install the template. |
| `start investigation: a rule cannot start an inline plan. Name an investigation template instead.` | Name a template. |
| `start investigation: the investigation policy names no identity for runs started by rules. Set identity.default (a hive://secret/<name>) in the investigation policy.` | Add `identity.default` to the `default` policy. |
| `start investigation: the secret the investigation policy names as the identity for runs started by rules is missing, disabled, empty or refused. Check that secret.` | Store an organization API key in that secret. |
| `start investigation: the case number is not valid for this start. Check the case parameter of the rule.` | Check the rule's `case` value. |
| `start investigation: the template is a draft, and a rule can only start an active template. Activate it (set its status to active).` | A person activates the template. |
| `start investigation: the identity requested is not allowed by the investigation policy for this template. Check identity in the policy.` | Check `identity` in the policy. |
| `start investigation: the identity the investigation policy names for runs started by rules may not read the case. Give that identity access to cases.` | Grant the identity `investigation.get` and `investigation.set`. |
| `start investigation: the case was not found, or the identity the investigation policy names for runs started by rules cannot see it.` | Check the case and the identity. |
| `start investigation: the organization is at its limit of concurrent investigations, so this start was dropped (it is not retried).` | Wait, or raise `budgets.max_concurrent_runs`. The dropped start is not retried. |

A refusal with no specific cause shows a generic message that lists what to check:
an active template, the template name and `identity.default`.

These do **not** produce a record:

- The engine refused a case it wrote itself (`own_case`): the loop guard working.
- The rule's `case` value did not render to a case number. The action fails for that
  event with `start investigation: case did not render to a case number`, and nothing
  is sent.
- The organization exceeded the start rate (2 starts per second sustained, bursts of
  20), or too many starts were in flight: the start is dropped.
- The engine did not answer. The start is retried once within 8 seconds, then
  dropped.
- Cases did not deliver the event. Cases delivers its events to rules on a best-effort
  basis; start the run from the case page when you need it.

A rule that uses `start investigation` cannot be saved where the Investigation Engine
is not enabled: saving fails with `start investigation is not enabled in this
environment`.

## A run finished but the verdict means little

| You see | It usually means | Do |
|---|---|---|
| Facts `unknown` with reason `forbidden` | The run's identity may not read that data. | Grant the identity the permission of that data source (see [step 3 of the walkthrough](walkthrough.md#3-the-run-identity-an-api-key-the-policy-names)). |
| Facts `unknown` with reason `llm_agent_not_found` | There is no `investigation-judge` AI agent record. | Create it (see [step 2](walkthrough.md#2-the-ai-agent-record-the-judgements-run-with)). |
| Facts `unknown` with reason `missing_input` | The template reads an input the trigger does not provide. | Derive it from `detection.get`. See [Run inputs](templates.md#run-inputs). |
| Facts `unknown` with reason `policy_denied` | The policy does not allow the operator. | Allow it in `operators.allow`, or accept the unknown. |
| Facts `unknown` with reason `not_found` on the trigger detection | The detection was not stored yet when the run started, and the engine gave up after its wait. | Usually transient. Rerun the investigation. |
| Many `inconclusive` verdicts | The data a proof needs is missing or incomplete. | Read `verdict.unknowns`. Inconclusive is a correct answer when data is missing. |
| `case_error` on the run | The case could not be written: `case write failed`, `case refused: <reasons>`, or `case not written: the run's credentials have expired` (or are unavailable). | Check Cases is subscribed and the identity has `investigation.set`. A run on a person's token cannot write after the token expires: use a secret identity. |
| An action ended `failed` with `is not wired` | The template proposes a class that cannot be executed. | See [Action classes](policies.md#action-classes). |
| An action stays `awaiting_approval` under `auto` | The action has no registered authorization, so a person must decide (reason `no_registered_authorization`). | Approve it, or see [Autonomy modes](policies.md#autonomy-modes). |
| Approve is refused with `this action class is in suggest mode` | The action was proposed in `suggest` mode. | Raise the class in the policy, then start a new run on an active template. |
| Approvals blocked for everyone | The class's `approvers` list matches nobody. | List approvers by the exact email or API key name they act as. |

## Policy warnings

`GET /policy/effective` returns `warnings` about the policy records:

| Warning | Meaning |
|---|---|
| `policy_records_rejected` | An enabled `investigation_policy` record does not parse. The engine keeps the last good set (or suggest-only when it has none), and the answer shows what is enforced. Fix or disable the record. |
| `legacy_policy_fields_ignored` | A stored record still carries a removed field (`spot_check`, `pause_when` or `triggers`). It is ignored; edit the record to remove it. |
| `case_trigger_moved_to_dr_rule` | A stored record still has `triggers.case_created`. New cases start runs only through a D&R rule now: see [D&R rules on a new case](automation.md#dr-rules-on-a-new-case). |
| `legacy_automation_routes_ignored` | A stored record still has `automation_routes`. It grants nothing. |
| `approvers_empty_means_nobody` | A class has `approvers: []`: nobody may approve it. |
