# Troubleshooting

--8<-- "includes/email-security-beta.md"

Most Email Security problems are one of a small number of shapes, and the product
is built so that each of them says so somewhere rather than looking like silence.
This page is the map from a symptom to the thing that reports it.

`coverage` is the first place to look for almost all of them:

```bash
limacharlie mailsec coverage --oid $OID --output yaml
```

It leads with `connections`, deliberately — a screen reporting 1,400 protected
mailboxes next to a connection that has not completed a pass since Tuesday is
lying with true numbers.

## Nothing is being ingested at all

### 1. Check the subscription

Email Security is gated on the `ext-email-security` subscription, and the gate is
enforced where mail is actually read rather than only at the API. An organization
that unsubscribes stops being ingested.

```bash
limacharlie extension list --oid $OID
```

What "gated" means, precisely:

| | |
|---|---|
| **No new mail is read** | Every arriving notification is discarded |
| **No discovery, no subscription creation, no watch renewal** | The provider's own watches then expire on their own schedule, and the provider stops sending |
| **Existing data is untouched** | A gate is not a deletion. The [retention lanes](policy.md#data-retention-and-deletion) still govern expiry |
| **Reading and remediating still work** | An analyst must still be able to act on mail already ingested |

!!! danger "Mail that arrives while you are unsubscribed is never read, and is never backfilled"
    This is a design decision, not a gap waiting to be filled. Resubscribing
    resumes ingestion of mail that arrives **after** it. It does not replay the
    window the product was off for, and there is no way to ask it to.

    If you are turning the subscription off to stop billing or to test something,
    that window is a permanent hole in your mail history. The
    [`enabled` flag on a `mailsec_provider` record](providers.md) is the
    reversible way to stop one connection.

Timings, both directions:

| | |
|---|---|
| Ingestion stops after unsubscribing | Within **5 minutes** |
| Discovery, watch renewal and polling stop | Within **10 minutes** of that |
| Resubscribing recovers | On the same bounds, with no restart and no support ticket |

### 2. Check the entitlement block

`coverage` carries an `entitlement` block reporting what the platform believes
about this organization:

```bash
limacharlie mailsec coverage --oid $OID --output yaml --filter 'entitlement'
```

| Field | |
|---|---|
| `resolved` | **Read this first.** `false` means the tier could not be resolved, and every other field is then absent rather than guessed. It is not a claim that you have no limits |
| `subscribed` | Whether the extension subscription was found |
| `gate_reason` | `""` when mail may be worked; otherwise `not_subscribed` or `trial_expired` |
| `plan` | `paid` or `trial` |
| `trial_started_at`, `trial_ends_at`, `trial_expired`, `trial_days_remaining` | The clock, when one applies. Days remaining rounds **up** — a trial with four hours to run has not had its last day yet |
| `mailbox_cap`, `mailbox_cap_enforced` | The protected-mailbox ceiling, and whether it is actually being enforced |
| `purge_schedule_available` | `false` means the schedule could not be **read**. The block is then absent rather than rendered as "nothing scheduled" |
| `purge_scheduled_at`, `purge_reason`, `purge_days_remaining`, `purge_cancellable` | A pending deletion, why, when, and whether undoing the condition withdraws it |

Where a mailbox ceiling applies, mailboxes past it stay in state `discovered` —
found, and not being watched. Not `excluded` (which is your own scope decision)
and not `error` (which would be a fault to fix). A cap **bounds activation and
never deactivation**: nothing un-protects a mailbox that is already protected.

!!! note "Trial limits are reported before they are enforced"
    During the private beta the trial clock and the mailbox ceiling are resolved
    and reported — so `entitlement` tells you what *would* apply — while nothing
    is refused on their account. `mailbox_cap_enforced` is the field that says
    which of the two you are looking at. Do not read a populated `trial_ends_at`
    as an announcement about pricing.

### 3. Check the connection itself

```bash
limacharlie mailsec connection test <record> --oid $OID --output yaml
```

Every requirement is probed independently and a failure names the step to fix.
`connections.state` in `coverage` summarizes to the **worst** connection, and an
organization with no connection at all reads `unconfigured`, never `ok`.

A first connection that appears to do nothing is very often a `mailsec_provider`
record that was created without `--enabled`. A disabled record is not a
connection — see [Getting Started](getting-started.md#4-connect-the-mail-tenant).

## One mailbox went quiet and the rest are fine

This is the failure with the fewest natural symptoms, so it is worth knowing by
name.

A mailbox is identified in several places that never see each other: your
provider's directory, the notification subscription built from it, the resource
path the provider echoes back on every notification, and the row the product
stored. If any two of those fold the address differently — a difference of case
is enough — notifications keep arriving and nothing claims them. There is no
error, because each attempt fails *retryably*: the item is retried rather than
reported, for days, and then dead-lettered.

**What you see:** one mailbox produces no `EMAIL_MESSAGE` events while its
neighbours on the same connection do, and `coverage` still reports it
`protected`. Nothing is in `error`.

Internally this is counted, and the **shape** of the count is the signal rather
than the value:

- a burst that decays is a connection's ownership moving between workers during a
  platform update — the new owner's discovery pass repopulates the inventory and
  every one of those retries into success;
- a trickle that never decays is a spelling mismatch, which is the fault.

If a single mailbox has gone silent while the rest of its connection is healthy,
open a support ticket naming the mailbox. It is fixable in place and it is not
something you can resolve from the console.

## Some messages never appear

A message that could not be fetched or processed is reported, not swallowed.

```yaml
op: is
path: routing/event_type
value: EMAIL_INGEST_ERROR
```

| Field | |
|---|---|
| `provider` | Which mail tenant |
| `stage` | Where it failed |
| `error` | Why |
| `external/provider_message_id` | The provider's own id for the message |
| `mailbox/id` | The mailbox, when it is known |
| `subscription_id` | The notification subscription, when set |

Three things about it are deliberate and worth knowing:

- **It carries no message content.** A fetch that failed has none, and a parse
  that failed must not put a hostile subject line into your telemetry as a side
  effect of reporting that it was hostile. Identifiers and a reason, nothing else.
- **It means the message will never be ingested** — it is a fact about the
  message, not about one delivery attempt. Transient failures are retried and
  produce no event.
- **It is emitted once per message**, not once per attempt.

Work that could not even be attributed to an organization — an undecodable
payload — is retired to an internal sink and produces **no** event in anyone's
telemetry, because an unattributable payload must not let a caller write into
some tenant's error feed.

Alert on it. Pair it with `coverage`'s mailboxes-in-`error` count, its
parse-degradation rate and its emission backlog. See
[Events & Automation](automation.md#watching-your-own-coverage).

## A short gap right after a platform update

Each mail connection is owned by exactly one worker at a time, and that ownership
is what holds the provider credentials, the compiled rules and the resolved
policy. On a rolling update the outgoing worker **releases** its connections
before it stops rather than letting them lapse, so another worker picks them up
in the time it takes to notice — seconds, not minutes.

The failure mode this replaced is worth knowing because it is what a gap looks
like: a lapsed ownership is only re-acquirable after a grace period, so a worker
that is killed rather than drained leaves that connection dark for the length of
it. Mail arriving in that window is not lost — the provider's notification is
retried and ingested by the new owner — but it is judged late, and that lateness
is deliberately **not** counted in the
[time-to-verdict number](pipeline.md#time-to-verdict), which measures live
ingests only.

If you see a burst of retries that decays after an update, that is this and it is
expected. A burst that does not decay is not.

## "Why does my organization have a `mailsec` installation key?"

Email Security ships its telemetry the same way every other LimaCharlie data
source does, so each connection appears as one cloud sensor on platform `email`
and authenticates with an installation key tagged `mailsec`.

**One key per connection**, and it is *ensured* rather than minted: the id is
derived, so the same connection reconnecting — after an update, a failover or a
restart — reuses the key it already has instead of creating another. An
organization with two mail connections has two such keys and stays at two.

If you are looking at a large number of `mailsec`-tagged installation keys, that
is the signature of an older build that minted one per connection attempt, and
it is fixed. The surplus keys are safe to delete; keep the ones the live
connections are using. Deleting a key a connection is using costs an ingestion
gap until it is ensured again, so prune deliberately rather than in bulk.

## We unsubscribed — what happens to our data?

Unsubscribing deletes nothing immediately. It stops ingestion (above) and starts
a clock.

| | |
|---|---|
| **30 days** after unsubscribing | Everything Email Security holds for the organization is permanently deleted |
| **Resubscribing inside those 30 days** | Cancels the scheduled deletion, and ingestion resumes |
| **Deleting the organization** | Deletes it immediately |

The 30 days exist so that an accidental unsubscribe, a lapsed card or a
reorganization of who pays for what is recoverable. Nothing can reconstruct last
month's mail once it is gone.

**You are told twice.** A notice is delivered to the organization's error stream
when the deletion is first scheduled, and again in the final seven days. Both
name the exact date and say plainly that resubscribing before it cancels the
deletion and that nothing has been deleted yet. They arrive on the same rail the
subscription gate speaks on, so there is one place to look for "Email Security is
telling me something".

`coverage`'s `entitlement` block carries the same facts as data —
`purge_scheduled_at`, `purge_reason`, `purge_days_remaining` and
`purge_cancellable` — so you can check without waiting for a notice.

What a deletion removes, and how it differs from the retention clocks that run on
their own, is in
[Data retention and deletion](policy.md#data-retention-and-deletion). Asking for
one immediately is a [tenant purge](cli.md#the-tenant-purge-is-irreversible).

## Quick reference

| Symptom | Where it is reported |
|---|---|
| No mail at all | `coverage.connections`, `coverage.entitlement.gate_reason`, `extension list` |
| A connection in error | `mailsec connection test <record>` — each requirement, independently |
| Mailboxes found but not watched | `coverage.mailboxes.discovered`, plus `mailbox_cap` where one applies |
| Individual messages missing | `EMAIL_INGEST_ERROR`, `coverage` parse-degradation rate |
| Judged but not emitted | `coverage` emission backlog |
| Slow verdicts | `coverage.overview.processing_latency_p95` — and its `basis`, which includes your provider's own notification delay |
| Automations decided but nothing moved | Action `result: alert_only` — see [`automations`](policy.md#automations) |
| A verdict you disagree with | [`message revisions`](detections.md#revising-a-verdict), and the `top_signals` on the message |
| Data scheduled for deletion | `coverage.entitlement.purge_scheduled_at` |
