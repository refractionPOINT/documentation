# Bulk Remediation

--8<-- "includes/email-security-beta.md"

A campaign sweep acts on a cluster the engine decided. **Bulk remediation** acts
on a set *you* named — a filtered page of the queue, the result of an LCQL hunt,
a list of ids in a file. It is what turns a search result into provider-side
action.

It is deliberately the same preview-then-confirm discipline the
[campaign sweep](campaigns.md#sweeping-a-campaign) uses, over a caller-supplied
selection rather than a cluster, with one structural difference: **the execute
cannot finish inside a request.** Up to 500 provider writes paced against
Microsoft 365 and Google throttling do not fit in one call, so execute returns a
handle and the work proceeds in the background.

## The four steps

| Step | Route | Permission | |
|---|---|---|---|
| **Preview** | `POST /actions/bulk/preview` | `mailsec.get` | Reads the index, reports each message's current state, and mints the `confirm` token |
| **Confirm** | — | — | A human reads the preview. This is the step the design exists for |
| **Execute** | `POST /actions/bulk/execute` | `mailsec.act` | Takes the token *and* the same request back. Returns a `bulk_id` immediately |
| **Status** | `GET /actions/bulk/{bulk_id}` | `mailsec.get` | The running truth of the job, polled to completion |

The actions are the same frozen names every other remediation path uses:
`quarantine_message`, `trash_message`, `move_to_spam`, `restore_message`,
`banner_message`, `unbanner_message`. An unrecognized action is refused with the
whole supported set named, rather than with a bare error.

`submit_to_triage` is deliberately **not** among them. Submitting 500 messages to
an AI triage agent is a bulk *spend*, not a bulk remediation, and it does not
belong behind a dialog whose whole subject is where mail ends up.

!!! warning "Capped at 500, and a larger selection is refused rather than truncated"
    Acting on the first 500 of 900 leaves the rest in inboxes nobody will look
    at. Narrow your filters, or split the selection yourself.

## Preview

```json
{
  "action": "quarantine_message",
  "msg_uuids": ["0057db2b-…", "…"],
  "attempt": "optional idempotency token"
}
```

Nothing is changed and **no job is created**. The preview reads the index and
answers, per message:

| Field | |
|---|---|
| `msg_uuid` | The message |
| `exists` | `false` when the index no longer resolves the id — expired past retention, or never real |
| `verdict`, `state`, `mailbox`, `provider`, `subject` | Enough to recognize what you are about to act on |
| `already_in_target_state` | Advisory, from the index — see below |

and, in `summary`:

| Count | |
|---|---|
| `total` | The selection you sent |
| `found` / `missing` | How many the index resolved |
| `already_in_target_state` | How many the index already places where the action would put them |
| `mailbox_count` | **The blast radius.** "38 messages" and "38 people's inboxes" feel very different, and only one of them is the real exposure |
| `actionable` | An **upper bound**, not a prediction: how many are not already in the target state *according to the index* |
| `by_provider` | The selection split by mail tenant |

`target_state` is the placement the action would produce. It is present and empty
for an action with no target placement (`unbanner_message` modifies a message
without moving it), which is what `has_target_state` distinguishes from "the
backend forgot to say".

!!! note "Expired ids and already-done messages are reported, not dropped"
    They stay in the confirmed set. `already_in_target_state` is read off the
    *index*, which records where remediation last put a message — its owner may
    have moved it since. The executor re-checks at the provider and answers
    `skipped`, which is a truer answer than a client-side filter could give.

## The confirmation is a derivation, not a nonce

The `confirm` token is derived from `(action, attempt, the normalized member
list)`. It is not a random handle the server remembers, so the execute must send
the **whole previewed request** back beside it — the same `action`, the same
`attempt`, and the same `msg_uuids`.

Change any of the three and the backend re-derives a different token, does not
match, and refuses the run rather than acting on a set nobody approved. A client
that re-ran its search between previewing and executing is stopped by this.

The selection is deduplicated, trimmed and sorted before the token is derived, so
re-ordering your own list is not a change.

`attempt` participates in the derivation on purpose. A **new** `attempt` over the
same selection is a new token, a new `bulk_id` and a deliberate second run —
which is the escape hatch for acting on the same messages again after a provider
outage. Omit it and a repeat collapses onto the job you already have.

**`reason` is deliberately outside the derivation.** It is your justification,
recorded on the job's audit row *and* on every message's, and rewording it
between previewing and executing neither invalidates the token nor starts a
second job over the same messages.

## Execute

```json
{
  "action": "quarantine_message",
  "msg_uuids": ["0057db2b-…", "…"],
  "confirm": "3f31ed…",
  "attempt": "optional",
  "reason": "INC-4471, confirmed credential phish"
}
```

The response is an acceptance, not a completion:

| Field | |
|---|---|
| `bulk_id` | The handle. Poll it |
| `accepted`, `started` | Whether the job was taken, and whether this call started it |
| `already_running` / `already_complete` | The idempotent answers — the confirmation re-derives to a fixed `bulk_id`, so re-sending the same request **adopts the same job rather than acting twice** |
| `member_count`, `state`, `counts` | The job as it stands at acceptance |
| `force` | Whether this execute was [forced](#forcing-an-action-in-alert-only-mode) |

Partial failure is a normal, honestly-reported outcome, **never a rollback**.
Provider actions are not transactional and there is no undo.

## Status

`GET /actions/bulk/{bulk_id}` is the running truth.

| `state` | Terminal | |
|---|:--:|---|
| `running` | | Members are still being attempted |
| `complete` | ✅ | Every member settled |
| `interrupted` | ✅ | The job was finalized before every member settled — a worker went away and the record was closed out |

!!! warning "`interrupted` is a terminal state, not a synonym for failure"
    The job stopped moving. The outcomes recorded against each member are real
    and are the authority on what actually happened — read `items[]`, do not
    infer that nothing was done.

`stalled` is a different fact and is **not** a state: it is `true` when a
*running* job's record has not been touched for **two minutes**, which means the
worker that accepted it is gone. Re-send the same execute request with the same confirmation
to finish it; every message already acted on collapses onto its existing action
row rather than being acted on twice.

Each member appears in `items[]`:

| `items[].result` | |
|---|---|
| `ok` | A provider write that happened |
| `skipped` | The provider found the message already where the action would put it |
| `failed` | `items[].reason` carries the executor's bounded explanation |
| `alert_only` | The organization's policy declined to act — see [`automations`](policy.md#automations), and [forcing](#forcing-an-action-in-alert-only-mode) to act anyway |
| `not_found` | No row in the index for that member |
| `pending` | Not attempted yet |

`items[].action_id` is the authoritative audit row for that member, expandable
through `GET /actions/{action_id}` like any other action.

`counts` carries the same vocabulary as running totals — `total`, `pending`,
`ok`, `skipped`, `failed`, `alert_only`, `not_found`. `alert_only` is counted
separately from `ok` on purpose: one is a provider write and the other is a
decision the organization's policy withheld.

The status also carries `force` — the job was
[forced](#forcing-an-action-in-alert-only-mode) — and `force_required`, which is
`true` when `counts.alert_only` is above zero.

**Read `state` to know whether to keep polling, and `counts` to know what
happened.** They answer different questions and can disagree in the one way that
matters: a job that ends `interrupted` is terminal with members still `pending`,
because nothing will attempt them now. `counts.pending` at zero means every
member settled; it is not the definition of "stop polling".

!!! note "Two `reason` fields, two authors"
    `reason` at the top level is the **operator's** justification for the whole
    job. `items[].reason` is the **executor's** explanation of one member's
    outcome. They are never the same sentence.

## From the CLI

Two calls, exactly like a campaign sweep:

```bash
# 1. Preview. Prints the per-message report and the confirm token; changes nothing.
PREVIEW=$(limacharlie mailsec message bulk-action \
  --action quarantine_message --input-file uuids.txt \
  --oid $OID --output json)

echo "$PREVIEW" | jq '.summary'

# 2. Execute the exact selection that was previewed.
limacharlie mailsec message bulk-action \
  --action quarantine_message --input-file uuids.txt \
  --confirm "$(echo "$PREVIEW" | jq -r .confirm)" \
  --reason "INC-4471, confirmed credential phish" \
  --oid $OID
```

The selection can come from `--msg-uuids` (repeatable and comma-separated),
`--input-file` (a JSON/YAML list or one id per line), or standard input — which
is what makes the queue pipe into it:

```bash
limacharlie mailsec message list --verdict malicious --output json --oid $OID \
  | jq -r '.messages[].msg_uuid' \
  | limacharlie mailsec message bulk-action \
      --action quarantine_message --input-file - --oid $OID
```

Ids must be message UUIDs. A selection carrying anything else — the header row
and second column of a pasted CSV are the usual way this happens — is refused
**by name**, because a phantom id comes back from the preview as "not in index",
identical to a legitimately expired one, and the counts you would be consenting
over would be wrong.

`--reason` **is** supported on the execute and reaches the audit trail: it is
recorded on the job's own row and on every message's, so an analyst reading one
message's timeline sees why it was acted on without having to discover that the
row belongs to a bulk job. It is not part of the confirmation token, so
rewording it between previewing and executing neither invalidates a token you
hold nor starts a second job over the same messages.

Passing `--reason` to a *preview* does nothing, and the CLI says so rather than
accepting it quietly: the preview mints the confirmation and takes no `reason`
by design, precisely so that rewording a justification can never invalidate a
selection somebody already approved.

!!! note "Older builds on either side of the wire"
    `limacharlie mailsec message bulk-action --ai-help` used to end with a stale
    paragraph claiming "there is no `--reason`", contradicting an earlier
    paragraph in the same text that described the flag correctly. That paragraph
    has been removed; if your installed CLI still prints it, trust this page and
    `--help`.

    The flag itself has always been registered, but it did not always reach the
    audit trail: the API used to drop `reason` from this one route before it got
    to the backend, which is why the Python SDK's `bulk_action_execute()`
    docstring still carries a note about it. Current deployments forward and
    record it, so the caveat is history rather than a contradiction.

### The exit code carries the outcome

`bulk-action` waits for the job by default (`--wait`, with `--timeout`
seconds — 300 by default — and `--poll-interval`), so `&&` means what it looks
like in a runbook:

| Exit | |
|---|---|
| `0` | The job reached `complete` without the "nothing worked" case below — or you passed `--no-wait`, or you ran a preview and it produced a token |
| non-zero | The execute was not accepted; the job completed with **zero successes and at least one failure**; it ended `interrupted`; it is `stalled`; it was still running at the timeout; or a poll errored |

The non-zero rule is narrower than "nothing was remediated", deliberately.
Per-member failures inside an otherwise successful batch are your data, not an
error. Zero successes **with at least one failure** is an error: nothing was
remediated and something broke, so a chained command must not run as though it
had worked.

A batch that completes with no failures and no successes — every member
`skipped` because the provider already had them where you wanted them, every
member `alert_only` because the organization is not in enforce mode, or every
member `not_found` — exits **`0`**. Nothing broke. If "at least one provider
write actually happened" is what your runbook needs, read `counts.ok` rather
than relying on the exit code. A batch withheld by alert-only mode is re-run
with `--force` to act — see
[Forcing an action](#forcing-an-action-in-alert-only-mode).

The `bulk_id` is announced on stderr *before* the first poll, so a poll that
fails still leaves you holding the handle. With `--quiet`, the exit code and
`limacharlie mailsec message bulk-status <bulk_id>` are how you read the result.

```bash
limacharlie mailsec message bulk-status <bulk_id> --oid $OID --output yaml
```

## From the console

The **Messages** queue and the **Hunt** screen both carry row selection and a
bulk action bar. Selecting rows and choosing an action runs exactly the flow
above: the dialog is the preview, with the blast radius and the per-message
report, and the confirm button is the execute. The console then polls the status
route and renders each member's outcome by name.

The console's bulk action list is a deliberate subset: `banner_message` is
offered (a bulk banner still uses the organization's own
[banner policy](policy.md#banners); no client supplies HTML), and
`unbanner_message` is not — un-bannering is a per-message follow-up taken from a
bannered row's timeline, not a sweep. The API accepts all six.

## When to use which

| | |
|---|---|
| One message | [`POST /messages/{msg_uuid}/actions`](api-reference.md#writes) — see [Messages & Triage](messages.md#actions) |
| Everything the engine attributed to one attack | [Campaign sweep](campaigns.md#sweeping-a-campaign) — the member set is the engine's, and the token is derived from it |
| A set you chose | Bulk remediation, this page |

All three end in the same executor, so `alert_only` / `enforce`, `force`, the audit row,
the `EMAIL_ACTION` event and idempotency apply identically. There is exactly one
remediation path in this product.

## Forcing an action in alert-only mode

An organization with no [automation](policy.md#automations) in `enforce` mode is
in **alert-only mode**, and that applies to **every** remediation, not only
automated ones. An action a person starts from the console, the CLI or the API,
or one an AI agent asks for, is decided, audited and withheld exactly like a
rule's: `result: alert_only`, and no mail moves.

A withheld action says so. Its response carries `force_required: true`. To
perform it, repeat the **same** request with `force: true`. That is an explicit
consent for that one action: it does not change the organization's mode, and the
next action without it is withheld again.

| Caller | How to force |
|---|---|
| Console | A withheld action asks *"Quarantine anyway?"* (or the action's own name); confirming re-sends it forced |
| CLI | `--force` on `mailsec message action`, and on the **execute** (with `--confirm`) of `mailsec message bulk-action` and `mailsec campaign action` |
| Python SDK | `force=True` on `act_on_message()`, `act_on_campaign()` and `bulk_action_execute()` |
| REST API | `force` (boolean) on `POST /messages/{msg_uuid}/actions`, `POST /campaigns/{campaign_id}/actions` and `POST /actions/bulk/execute` — see [Writes](api-reference.md#writes) |
| AI agents | Through the CLI, like any other caller |
| D&R rules | `force: true` in the `extension request` — in a `dr-mail` [`post_verdict` rule](custom-rules.md#what-a-post_verdict-rule-may-respond-with) or an ordinary [D&R rule](automation.md#acting-on-mail-from-a-dr-rule) |

```bash
limacharlie mailsec message action <msg_uuid> \
  --action quarantine_message --reason "confirmed credential phish" \
  --force --oid $OID
```

- **Only a real boolean `true` forces.** Anything else — `false`, the string
  `"true"`, `1`, or no field at all — does not.
- **`force` is not part of any confirmation token, and previews do not take
  it.** Preview as usual, then send `force` on the execute with the token you
  already hold.
- **A forced bulk execute is a new job.** Re-sending a confirmation that was
  withheld, now with `force`, starts a job with a **new `bulk_id`** rather than
  adopting the withheld one. The bulk status reports `force` (this job was forced)
  and `force_required` (`counts.alert_only` is above zero).
- **A campaign sweep** reports `force_required: true` when any member came back
  `alert_only`.
- **The override is audited beside the refusal, not over it.** A forced action
  is its own action row, next to the withheld one; its `request` carries
  `force: true`, and its `EMAIL_ACTION` event carries `forced: true`. The field
  is absent on every action that was not forced, so a rule can alert on
  overrides alone:

```yaml
# Detect
op: and
rules:
  - op: is
    path: routing/event_type
    value: EMAIL_ACTION
  - op: is
    path: event/forced
    value: true
```

`force` needs a `limacharlie` release that includes it; an older CLI refuses
`--force` as unknown, and the field can be sent directly to the API in the
meantime.
