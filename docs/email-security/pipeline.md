# How a Message Is Processed

--8<-- "includes/email-security-beta.md"

This is the page to read first if you are evaluating the product. It follows one
message from the moment your provider says it exists to the moment somebody
decides what to do about it, and it is explicit about which parts happen in one
pass and which parts can happen later.

The short version: **everything that produces the first verdict happens
synchronously, in one pass, per message.** There is no queue of half-judged mail
and no second job that fills in the answer. Anything that changes a verdict
afterwards is recorded as a *revision*, not as a late arrival.

## The stages

| # | Stage | What happens |
|---|---|---|
| 1 | **Notify** | The provider tells us a message exists |
| 2 | **Fetch** | The raw MIME is pulled from the provider |
| 3 | **Parse** | MIME becomes the Message Data Model |
| 4 | **Enrich** | Sender history, lookalike, domain age, link features, attachment explosion |
| 5 | **Score** | The managed pack and your `dr-mail` rules are matched and scored as one set |
| 6 | **Verdict** | One class, one score, and the signals that produced them |
| 7 | **Cluster** | The message is attributed to a campaign, or not |
| 8 | **Persist** | Index row, sealed raw message, sealed judged model |
| 9 | **Emit** | `EMAIL_MESSAGE`, once |
| 10 | **Automate** | Policy automations, `dr-mail` `post_verdict` rules, and ordinary D&R rules |
| 11 | **Triage** | A person or an agent revises the verdict, if it needs revising |
| 12 | **Remediate** | The message is moved at the provider |

Stages 2 through 9 are one function call. If any of them fails, the failure is
emitted as `EMAIL_INGEST_ERROR` rather than swallowed.

### 1. Notify

Email Security connects to the provider's API. **There is no MX change, no mail
routing change, and nothing in the delivery path.** It is post-delivery: the
message has already landed in the mailbox by the time we hear about it.

| Provider | Mechanism |
|---|---|
| Microsoft 365 | A Microsoft Graph change-notification subscription per protected mailbox. Subscriptions are renewed well before Graph's ceiling, and lifecycle notifications are handled on their own endpoint |
| Google Workspace | A Gmail `users.watch` per mailbox publishing to **your own** Pub/Sub topic, which the collector consumes with a pull subscription. Renewed daily. A history-based poll is the fallback for small tenants and for outages |

Both are push. Polling exists as a safety net, not as the normal path. See
[Connecting Providers](providers.md).

### 2-3. Fetch and parse

The raw MIME is fetched and parsed into the **Message Data Model**: headers with
decomposed addresses and domains, sender, recipients, subject, a
thread-segmented body, links, attachments, parsed SPF/DKIM/DMARC/ARC results,
and the `Received` chain. Every later stage reads the model, never the bytes.

### 4. Enrich

Enrichers run in a fixed order so a given message produces the same model every
time: sender and sender-domain history, then static link features, then
lookalike and VIP impersonation distances, then attachment explosion. Sender
domain registration age is resolved from RDAP through a bounded cache.

**Attachment explosion runs here, inline.** Archives are unpacked recursively,
macros extracted, QR codes decoded, files identified by content rather than by
the extension the sender claimed. It carries a per-message time budget; when the
budget is exhausted the verdict is computed without it and the model says so
(`_meta/explode_timeout`) instead of pretending the file was clean.

Everything an enricher resolves is stamped **into** the message, which is why a
rule reads an enrichment as an ordinary path and why re-reading the event later
shows exactly what the engine saw. An enrichment that could not be resolved is
*absent*, never a reassuring default. See
[Detections & Verdicts](detections.md#enrichments).

### 5-6. Score and decide

The managed rule pack and your own `dr-mail` `pre_verdict` rules are matched
separately and then **scored together as one set**. That matters more than it
sounds: a custom rule is evidence in the same verdict rather than a second
opinion sitting beside it, so two 50-weight signals from different sources
compound instead of standing at 50 each.

The score is a weighted compounding model, not a "first rule to fire wins"
model. Each signal removes a fraction of the remaining headroom, so five weak
signals cannot outvote one strong one. The arithmetic, the thresholds, the
graymail lane and the exclusion mechanism are all in
[Detections & Verdicts](detections.md#scoring).

The result is one verdict (`malicious`, `suspicious`, `graymail`, `benign`,
`unknown` or `error`), a score, and the signals that produced it.

### 7-9. Cluster, persist, emit

The message is clustered into a [campaign](campaigns.md) if it belongs to one,
then written: an index row, the sealed raw message, and the sealed **judged
model** (the enrichments as resolved and the verdict as stamped).

Then `EMAIL_MESSAGE` is emitted, once. It is immutable, and it carries the whole
model including the enrichments and the verdict, so a D&R rule never has to call
back for context.

### 10-12. Automate, triage, remediate

From here the message is ordinary work: [policy automations](policy.md#automations)
and `post_verdict` rules can dispatch an action, [D&R rules](automation.md) on
the `EMAIL_*` events get the platform's full response set, an analyst or an
[AI triage agent](ai-triage.md) can revise the verdict, and remediation moves
the message at the provider.

## What is synchronous, and what is not

| | |
|---|---|
| **Synchronous, one pass per message** | Fetch, parse, every enrichment including attachment explosion, matching, scoring, the verdict, campaign clustering, persistence, and the `EMAIL_MESSAGE` emission |
| **Later, and recorded as such** | Verdict revisions, remediation outcomes, campaign membership added when a later message joins the cluster |

A revision does **not** rewrite `EMAIL_MESSAGE`. The original event stands as the
record of what the engine decided at ingest, a revision row is appended with its
sequence number, and an `EMAIL_VERDICT` event is emitted carrying the new
conclusion. Two consumers reading the same stream therefore agree on both what
was decided and what it was changed to, which a mutated event could never give
you.

!!! info "Why the first pass is not allowed to wait"
    Anything the pipeline waits on is a mailbox that stays unjudged while it
    waits. So every enricher is bounded, every one of them can fail toward "not
    resolved", and the verdict is computed from whatever resolved in time with
    the gaps named. A slow enrichment degrades one signal. A blocking one
    degrades coverage, which is the thing you bought.

## Managed detections are optional

The managed rule pack is on by default, and you can turn it off. Some
organizations want to own detection entirely through their own `dr-mail` rules,
and forcing our opinions into their verdicts would make that impossible.

```yaml
# managed-rules.yaml, saved as mailsec_policy record 00-managed-rules
policy_type: managed_rules
enabled: false
```

```bash
limacharlie hive set --hive-name mailsec_policy --key 00-managed-rules \
  --input-file managed-rules.yaml --enabled --oid $OID
```

The extension also exposes `get_managed_rules` and `set_managed_rules` for
reading and flipping this without hand-writing the record.

| | |
|---|---|
| **Default** | Enabled. An organization that has written no policy has the pack |
| **When disabled** | The managed pack is not matched at all. Your own `dr-mail` rules still are, and they are still scored the same way |
| **If nothing matches** | The verdict is `unknown`, never `benign`. "Nobody was looking" and "we looked and it was fine" are different facts and are reported differently |
| **Time to take effect** | On the next policy resolve. A policy change invalidates the cache, and there is a five-minute backstop for a change we did not hear about |

The record must state `enabled` explicitly. A `managed_rules` record that sets
nothing is refused rather than read as "disable", because the failure mode of
guessing wrong here is an organization with no detection that believes it has
some.

You do not need this switch to tune the pack. Disabling one packaged rule, or
changing its weight, is a
[`rule_overrides`](custom-rules.md#tuning-the-managed-pack) entry.

## The state model

A message carries several **independent** dimensions. They are not stages of one
workflow, and reading them as if they were is the most common way to
misinterpret the queue.

| Dimension | Values | Changed by |
|---|---|---|
| **Verdict** | `malicious`, `suspicious`, `graymail`, `benign`, `unknown`, `error` | The scoring pass, then any revision |
| **Decision mode** | `auto`, `analyst`, `ai` | Who last decided. `auto` is the rule pack |
| **Revision history** | An append-only sequence | Each revision, with its rationale |
| **Report status** | `open`, `triaging`, `resolved`, plus a disposition | The [abuse-mailbox queue](user-reports.md) |
| **Remediation state** | `delivered`, `quarantined`, `trashed`, `restored`, `bannered`, `spam` | Actions performed at the provider |
| **Campaign membership** | A campaign id, or none | The [clustering engine](campaigns.md) |

Each has exactly one writer. A quarantined message can still be `benign`
(somebody quarantined it anyway), a `malicious` message can still be `delivered`
(nobody acted, or the organization is in `alert_only`), and a resolved report
can sit on a message whose verdict was never revised. Collapsing these into a
single "status" would lose every one of those distinctions.

## Storage and privacy

A mail security product holds the most sensitive data in the tenant, so it is
worth being precise about what is kept, where, and who can read it.

### The raw message

The full original message is stored, compressed and then encrypted with
**AES-256-GCM**. Keys are **per organization**, derived with HKDF from a root key
that is itself KMS-wrapped, so the deployment's secret is ciphertext and only a
workload with decrypt permission on the KMS key can turn it into key material. A
service that cannot reach KMS fails to start rather than falling back to
plaintext.

The object's own storage path is bound into the encryption as additional
authenticated data, which means a copied object cannot be opened somewhere else.

### Two retention lanes

| Lane | Kept | Holds |
|---|---|---|
| Transient | **35 days** | Every message |
| Retained | up to **400 days** | Flagged messages and the evidence attached to them |

The lane is chosen at ingest from the verdict. A message that becomes evidence
later, because it was reported, re-judged or acted on, is promoted into the
retained lane by re-sealing it there. The retained window is tunable within the
ceiling through [`mailsec_policy/retention`](policy.md#retention); 400 days is
the store's hard limit, and policy can only choose within what the store keeps.

The searchable message index keeps 35 days as well. `EMAIL_*` events go to the
platform's telemetry lake and follow your ordinary retention, which is why
[LCQL](automation.md#querying-mail-with-lcql) reaches further back than the queue
does.

Both lanes can also be emptied outright rather than waited out: a tenant purge
removes everything this product holds for an organization at once, and the same
deletion runs on its own 30 days after an organization unsubscribes. See
[Data retention and deletion](policy.md#data-retention-and-deletion).

### What lands in telemetry

`EMAIL_MESSAGE` carries parsed body content, so mail text is in your normal
telemetry and is subject to your normal Outputs and access controls. Plan for
that deliberately rather than discovering it.

Body parts are capped at roughly **256 KB each**. When a cap is hit the model
sets `body/truncated` and `_meta/truncations` names the exact paths that were
clipped, so a rule author can tell a short message from a clipped one. The
stored raw message always holds the full content regardless.

### Reading a message back

Opening the drawer serves the **sealed judged model** where it exists, labelled
`mdm_source: stored`. That is what the engine actually decided with, enrichments
included. The fallback re-parses the encrypted raw message with today's parser
(`mdm_source: eml_reparse`) and carries no enrichments at all, and the response
always says which one you are reading. Neither needs a justification: the model
is the product's structured view of the message.

The **original bytes** are gated separately. Downloading the EML requires the
`mailsec.get.eml` permission on top of `mailsec.get`, plus a written
justification that is stored verbatim against your authenticated identity. A
failed attempt is recorded too, and the bytes are not served if the audit write
fails. See [Messages & Triage](messages.md#downloading-the-original-message).

## Latency

End-to-end time for a message is three terms:

| Term | Who owns it |
|---|---|
| **Provider notification delay** | Your mail provider. This is normally the dominant term and it is not ours to shorten |
| **Queue** | Time between the notification arriving and a worker picking it up |
| **Processing** | Fetch, parse, enrich, score, persist, emit |

Within processing, fetching from the provider and exploding attachments are the
expensive stages, and only the second of those is bounded by a budget we choose.
Parsing, matching and scoring are not where the time goes.

!!! note "We do not publish a latency figure yet"
    The `coverage` call reports the processing-latency percentile as
    **not recorded** rather than returning an estimate, because the immutable
    timestamps that would make it a measurement are not yet recorded. A number
    that looks like a measurement and is not one is worse than an honest gap, so
    the gap is what you get until it can be computed properly.

    Verdict revisions are a separate clock entirely. A revision arrives when a
    person or an agent gets to the message, which is a queue-depth question
    rather than a pipeline question.

## Where to go next

| | |
|---|---|
| [Getting Started](getting-started.md) | Connect a tenant and see the first judged message |
| [Detections & Verdicts](detections.md) | The scoring model, the managed pack, and what the rules can read |
| [Custom Rules](custom-rules.md) | Writing `dr-mail` rules that compound with the pack |
| [Events & Automation](automation.md) | The `EMAIL_*` events and the D&R seat |
| [Messages & Triage](messages.md) | The queue, the drawer, actions and the audit trail |
| [Policy Reference](policy.md) | Every `mailsec_policy` record type |
