# Sample Submission

--8<-- "includes/email-security-beta.md"

Sample submission lets your analysts send LimaCharlie a copy of a message the
engine got wrong, so detection can improve. It is **off by default**, it is
**never automatic**, and it works **one message at a time**.

!!! warning "Submitting sends the message to LimaCharlie"
    When an analyst submits a message, LimaCharlie keeps a copy of the original
    message, including its attachments. The sections below state exactly what is
    kept, where, for how long and who can open it. You can withdraw any submission
    at any time, which deletes the copy.

## Why it exists

Two kinds of mistakes are worth telling us about:

- a threat the engine called benign or unknown (a missed threat), and
- a legitimate message the engine flagged (a false positive).

Sample submission is the way to hand us one of those, with a short reason,
without turning on anything broader. It copies the message to LimaCharlie. It does
not change the verdict on your message.

## Turning it on

Sample submission is opt-in per organization. Until you opt in, submit requests
are refused and nothing is ever copied.

Opt in with a `mailsec_policy` record of type `sample_sharing`:

```yaml
policy_type: sample_sharing
enabled: true
```

```bash
echo '{"policy_type": "sample_sharing", "enabled": true}' > opt-in.json
limacharlie hive set --hive-name mailsec_policy --key sample-sharing \
  --input-file opt-in.json --enabled
```

| Field | Default | |
|---|---|---|
| `enabled` | `false` | Without a record the feature is off. Set it to `false`, or delete the record, to turn it off again |

The record has only that one field. Unknown fields are refused, and a record that
sets nothing is refused. When several records set `enabled`, the last one in
record-name order wins, as with [`reporter_reply`](policy.md#reporter_reply).
See [Policy Reference](policy.md#sample_sharing). Writing the record needs the
same permission as any other `mailsec_policy` record.

## Who can submit

Only a person. Submitting and withdrawing need `mailsec.act`, and the request
must come from an analyst in the console or from an API key.
**D&R rules, automations and the AI agent cannot submit or withdraw.** The backend
refuses them, records the refusal as a `failed` action, and returns:

```text
submit_sample is an analyst action: automation, D&R rules and the AI agent may not send mail to LimaCharlie
```

Listing and reading submissions needs `mailsec.get`.

## Alert-only mode does not apply

[Alert-only mode](messages.md#enforcement) governs actions that write to a
mailbox, and submitting or withdrawing a sample touches none. So an organization in
alert-only mode can still submit and withdraw samples, and `--force` is not needed
or used. What governs these two actions is the opt-in and the rule that only a
person can run them.

## What you choose when you submit

Every submission needs a **category** and a **reason**.

| Category | Use it when |
|---|---|
| `missed_threat` | We called the message benign or unknown, and it is a threat |
| `false_positive` | We flagged the message, and it is legitimate |
| `other` | Anything else you want us to look at |

The reason is free text, 1 to 1024 characters after trimming, and is kept with the
submission. Unlike the other message actions, it is required.

## What is kept

For each submission, LimaCharlie keeps:

- **The message itself**: the original raw bytes (RFC 822, including
  attachments), compressed and encrypted with AES-256-GCM. The encryption key is
  derived per organization from a dedicated LimaCharlie key that is separate from
  the key protecting your own stored mail.
- **A metadata row**: the message id, the category, the reason your analyst typed,
  your analyst's identity, the time, the verdict, score and matched detection
  rule ids at that time, the sender, the subject, the mailbox address and the
  size.

Only the one message you chose is copied.

## Where it is kept and for how long

- **Where**: in a LimaCharlie-owned bucket in the **same datacenter and region**
  as your organization's Email Security data. It is a separate bucket from the
  one that holds your raw messages.
- **How long**: a fixed 400 days from the submission, then deleted
  automatically. Your organization's mail retention settings (`message_days` and
  `flagged_days` in the [`retention`](policy.md#retention) record) do not apply to
  submissions: they neither shorten nor extend that period.
- **Earlier**: any time you withdraw it, or when your organization's Email
  Security data is deleted (see below).

## Who can open it, and how you can tell

Only LimaCharlie staff working on detection quality can open a submission, through
an internal tool that records every access. No other customer can see it.

You can see that record. Each submission carries a `review_count` and a
`last_reviewed_at`, and [`GET /submissions/{submission_id}`](#routes) returns the
timestamp of every time the stored copy was opened. The record is a count and
timestamps only: it never names the person who opened it.

## Withdrawing

You can withdraw at any time, from the console, the CLI or the API. Withdrawing
**deletes the stored copy and its metadata** (a hard delete), then writes the
withdrawal to the audit trail. It cannot be undone; to share the message again,
submit it again.

- Withdrawing by message: `withdraw_sample` on the message, or
  `limacharlie mailsec message withdraw-sample <msg_uuid>`.
- Withdrawing by submission id: `DELETE /submissions/{submission_id}`, or
  `limacharlie mailsec submission withdraw <submission_id>`.

Withdrawing a submission that was already withdrawn or has expired is harmless: the
submission routes answer `withdrawn: false` and nothing is deleted a second time.

## If the organization is deleted

Deleting the organization (the Email Security tenant purge) deletes all of its
submissions too. The automatic deletion that follows an unsubscribe or a trial
lapse is the same tenant purge, so it deletes submissions as well. See
[Data retention and deletion](policy.md#data-retention-and-deletion).

## From the command line

```bash
# Submit one message. Both --category and --reason are required.
limacharlie mailsec message submit-sample <MSG_UUID> \
  --category missed_threat --reason "credential phish we did not flag"

# Withdraw by message, or by submission id
limacharlie mailsec message withdraw-sample <MSG_UUID>
limacharlie mailsec submission withdraw <SUBMISSION_ID>

# See what you have sent
limacharlie mailsec submission list
limacharlie mailsec submission list --category false_positive --since 2026-09-01T00:00:00Z --limit 100

# One submission, including when LimaCharlie staff opened it
limacharlie mailsec submission get <SUBMISSION_ID>
```

The CLI checks the category and the reason before sending anything. A refused
submission exits non-zero and prints the reason. See
[Command Line Interface](cli.md).

## Routes

All routes are under `/v1/mailsec/{oid}`. See [API Reference](api-reference.md)
for the shared conventions.

| Route | Does |
|---|---|
| `POST /messages/{msg_uuid}/actions` with `{"action": "submit_sample", "category": ..., "reason": ...}` | Submit one message. `category` and `reason` are required; `attempt` is an optional idempotency token. Requires `mailsec.act` |
| `POST /messages/{msg_uuid}/actions` with `{"action": "withdraw_sample"}` | Withdraw the submission made from this message. `reason` (up to 1024 characters) and `attempt` are optional. Requires `mailsec.act` |
| `GET /submissions` | `{enabled, available, submissions, next_cursor}`. Filters: `category`, `since`, `until` (RFC 3339), `limit` (1-200, default 50), `cursor`. Requires `mailsec.get` |
| `GET /submissions/{submission_id}` | `{submission, reviews}`, where `reviews` is `[{ts}]`, one per time LimaCharlie staff opened the copy. An unknown id is not an error: it returns `{"submission": null, "reviews": []}`, so branch on `null`. Requires `mailsec.get` |
| `DELETE /submissions/{submission_id}` | `{withdrawn: true, submission_id, action_id}`. Hard-deletes the stored copy and its metadata. An unknown, already-withdrawn or expired id is not an error: it returns `{withdrawn: false, submission_id}` with no `action_id`, and nothing is deleted. Requires `mailsec.act` |

`GET /submissions` always returns two flags, so an empty list is never ambiguous:
`enabled` says your organization has opted in, and `available` says your
datacenter has a submissions store. Pagination works as for the other lists: pass
`next_cursor` back as `cursor`, verbatim, until it is empty.

A submission looks like this:

```json
{
  "submission_id": "3f1c9b7e5a2d4c8e9a0b1c2d3e4f5a6b",
  "msg_uuid": "0057db2b-0000-4000-8000-000000000001",
  "category": "missed_threat",
  "reason": "credential phish we did not flag",
  "actor": "analyst@corp.example",
  "ts": "2026-09-30T12:00:00Z",
  "expires_at": "2027-11-04T12:00:00Z",
  "provider": "m365",
  "mailbox_address": "user@corp.example",
  "sender_email": "sender@example.net",
  "subject": "Invoice overdue",
  "verdict": "benign",
  "score": 0,
  "matched_rules": [],
  "size_bytes": 12345,
  "review_count": 0
}
```

`last_reviewed_at` is present once LimaCharlie staff have opened the copy and
omitted before that.

### Action results and refusals

A submission goes through the same action route as other message actions and
returns the same result shape. `ok` and `skipped` carry a `submission_id`;
`skipped` means the message already has an active submission, so submitting twice
is safe. A refusal is reported like any other failed action, with one of these
texts in `error`:

| Error | Meaning |
|---|---|
| `sample submission is not enabled for this organization` | You have not opted in |
| `sample submission is not available in this datacenter` | Your datacenter has no submissions store |
| `the message's raw copy is no longer stored, so it cannot be submitted` | The raw copy aged out or was never stored |
| `submit_sample is an analyst action: automation, D&R rules and the AI agent may not send mail to LimaCharlie` | The request came from automation, a D&R rule or the AI agent |

A missing or unknown `category`, or a missing or over-long `reason`, is refused
with an HTTP 400 before anything is sent.

Every outcome is written to the action audit trail and emitted as an
`EMAIL_ACTION` event, which carries `category` and `submission_id`. Submitting and
withdrawing also write `mailsec_sample_submitted` and `mailsec_sample_withdrawn`
platform audit events.

## FAQ

**Does submitting change my verdicts?** No. It copies the message to LimaCharlie;
it does not revise the verdict or move the message.

**Is anything submitted automatically?** No. Nothing is submitted unless a person
runs the action on a message, and only after your organization has opted in.

**Is it per message?** Yes. Each submission is one message. There is no bulk or
campaign form.

**Can I see who at LimaCharlie looked at it?** You can see whether and when: the
review count and timestamps are shown on every submission. The reviewer's identity
is not shown.

**Can I take it back?** Yes, at any time. Withdrawing deletes LimaCharlie's copy
and its metadata.

**Can another customer see it?** No.
