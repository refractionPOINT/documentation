# Detections & Verdicts

--8<-- "includes/email-security-beta.md"

Every message gets exactly one verdict, and the verdict always carries its
reasons. This page explains how the reasons are produced, what the rules can see,
and how to tune it.

## The verdict

| Verdict | Meaning |
|---|---|
| `malicious` | Score at or above the malicious threshold |
| `suspicious` | Score at or above the suspicious threshold |
| `graymail` | Bulk or marketing mail: neither an attack nor wanted |
| `benign` | Below the suspicious threshold, and nothing said "graymail" |
| `unknown` | No judgement was reached |
| `error` | Judging failed |

The verdict object on a message carries:

| Field | Meaning |
|---|---|
| `verdict` | The class above |
| `score` | 0–100 |
| `top_signals` | Up to five contributing rules, heaviest first, each with `rule_id`, `name` and `weight`. This is the "why this verdict" block |
| `matched_signals` | Every rule id that matched, including suppressed ones — the hunting surface |
| `tags` | The deduplicated, sorted tags of the rules that actually contributed |
| `engine_version` | The rule-pack version that decided it |
| `decided_at` | When |
| `mode` | `auto` (the rule pack), `analyst` (a human override) or `ai` |
| `campaign_id` | The campaign this message was clustered into, if any |

!!! info "A number alone is never the answer"
    A non-benign verdict always populates `top_signals`. The console renders it
    as **Why this verdict** in the message drawer, and the API returns it on both
    the index row (the single heaviest signal) and the detail response (the full
    list). A score with no explanation would not be actionable and is not
    offered.

### The verdict is also an event

Every verdict this product reaches is emitted as an `EMAIL_VERDICT` event, so a
rule that acts on verdicts is written **once**:

| `revision/seq` | `revision/mode` | What it is |
|---|---|---|
| `0` | `auto` | What the rule pack decided, emitted at ingest immediately after the message's `EMAIL_MESSAGE` |
| `1`, `2`, … | `analyst` | A human overrode it |
| | `ai` | The AI triage agent overrode it |
| | `detonation` | Link detonation found something at the other end and overrode it |

The `seq 0` event repeats a verdict that is already inside `EMAIL_MESSAGE`, and
that duplication is deliberate: without it, "tell me when a message is judged
malicious" would be two rules against two paths on two event types — one for the
engine's opinion and one for everything that happened after it — that you would
have to keep in agreement forever.

`EMAIL_MESSAGE` is still emitted once per message and is still immutable. The
verdict *history* is the sequence of `EMAIL_VERDICT` events, which is what lets a
hunt reconstruct what was known at any point in time.

The `seq 0` event is an event and nothing else. It is not an entry in the
message's revision history, and a message nobody has overridden reports zero
revisions in the API and the console.

See [Events & Automation](automation.md) for the payload and
[Custom Rules](custom-rules.md#acting-on-a-verdict) for a rule that uses it.

## Scoring

Each matching rule carries a **weight** (0–100, how much this evidence is worth)
and a **confidence** (0–100, how often it is right when it fires). The score
combines them with diminishing returns rather than a sum:

```text
score = 100 × ( 1 − Π (1 − wᵢ/100 × cᵢ/100) )
```

Each signal removes a fraction of the *remaining* headroom. A sum would let five
weak signals outscore one strong one and would need clamping at 100, which makes
every heavily-signalled message look identical. One rule at weight *N* and
confidence 100 scores exactly *N*, which is the identity every threshold is
reasoned about against.

| Threshold | Default | Where to change it |
|---|---|---|
| `malicious_min` | 85 | [`mailsec_policy/thresholds`](policy.md#thresholds) |
| `suspicious_min` | 45 | [`mailsec_policy/thresholds`](policy.md#thresholds) |

`malicious_min` must stay above `suspicious_min`. Composed policy that inverts
the pair is refused, and an inverted pair reaching the scorer any other way falls
back to the defaults rather than making every suspicious message malicious.

### The graymail lane

Graymail is a **lane, not a score band**. Rules classed `graymail` contribute no
score at all; they set the verdict to `graymail` only when the score did not
reach `suspicious_min` **and** no `detection`-class rule fired.

That last clause is the point: a newsletter that also carries a credential-phish
link is a phish that happens to look like a newsletter, and filing it under
"marketing" is filing it where nobody looks.

### Exclusions

Exclusions are applied **before** scoring, so a suppressed rule contributes
nothing to the score and never appears in `top_signals`. It still appears in
`matched_signals`, so a suppression is auditable rather than invisible.

Exclusions can be scoped by rule id, sender address, sender domain or mailbox,
require a written reason, and can carry an expiry — after which they become inert
without anyone deleting them. See
[Policy Reference → Exclusions](policy.md#exclusions).

## What the rules can read

Rules are standard D&R detect blocks evaluated against the **Message Data
Model** — the parsed message — plus the enrichments the pipeline stamped onto it.
Because the enrichments are *in the message*, a rule reads them as ordinary paths
and a re-evaluation later sees exactly what the pipeline saw.

### The parsed message

`headers` (including the raw header list, decomposed sender and recipient
addresses, and every domain and IP found), `sender` (with `reply_to_mismatch`,
free-mail and disposable flags), `recipients`, `subject`, `body` (HTML and plain,
extracted display text, thread segmentation into the current reply and previous
quoted threads, hidden-text detection), `links`, `attachments`, `auth` (parsed
SPF / DKIM / DMARC / ARC results with alignment) and `hops` (the parsed `Received`
chain).

### Enrichments

| Path | What it carries |
|---|---|
| `enrichments/sender_profile` | This organization's history with the sender **address**: `first_seen_ts`, `days_known`, `msg_count_30d`, `flagged_count_180d`, `prevalence` (`none` / `new` / `rare` / `common`) |
| `enrichments/domain_profile` | The same, keyed on the sender's registrable **domain** |
| `enrichments/sender_domain` | The sender domain's registration age, from RDAP with a bounded global cache |
| `enrichments/link_features[]` | Per link, aligned with `links[]`: `domain`, `domain_age_days`, `popularity_bucket` (`top1k` / `top100k` / `top1m` / `unranked`), `in_urlhaus`, `mixed_script` (a homograph label mixing writing systems), `credentials_in_url` (the `https://apple.com@evil.example/` trick) |
| `enrichments/lookalike` | `vip_hit` (`display_name:<name>` when the display name matches a VIP whose address does not, `email:<addr>` when the sender *is* the VIP), `org_domain_distance` and `brand_domain_distance` — edit distances against your own domains and known brands |
| `attachments[].explode` | Attachment explosion: recursive `children` with their own names, hashes, magic types and depth; `archive` (`encrypted`, `file_count`, `max_depth_hit`); `vba` (`auto_exec`, `suspicious`, `hex_strings`); `qr[].url`; `ocr_excerpt`; `yara_matches`; the `scanners` that ran |

Attachment explosion is bounded — a per-message time budget and size and event
caps — and can only ever fail toward "not scanned". `explode.scanners` names what
actually ran for that attachment, so a rule that depends on a particular kind of
evidence can tell "the scanner found nothing" from "that scanner did not run".

!!! warning "Absent is not benign"
    An enrichment that could not be resolved is **absent**, never a reassuring
    value. `domain_age_days` is missing when the registry lookup was unavailable,
    rate-limited or a cache miss — which is common — and a
    newly-registered-domain rule must therefore test *presence* as well as a
    threshold. Likewise `popularity_bucket` is empty when the lookup did not run,
    which is a different fact from `unranked`, a positive finding that the domain
    really is not in the list. A missing lookup must never become a suspicion.

### The sender-history feedback loop, and why it is closed

Sender profiles are read **before** the message is counted, so the stamp answers
"what did this organization know about this sender *before* this message
arrived". Counting first would make `msg_count_30d` never zero and first contact
indistinguishable from second contact.

More importantly, the profile's `flagged_count_180d` counter is only incremented
for verdicts that flag **independently of prevalence signals**. Rules whose
evidence *is* the accumulated history carry a `prevalence` tag, and the counter
is computed with those rules removed.

The reason is a loop observed live before the contract existed: the sender-history
rule alone can cross the suspicious threshold, and if a flagged verdict fed the
counter, one false positive would re-flag that sender forever — each flag
re-incrementing the counter that caused it, never decaying, and in enforce mode
quarantining a legitimate sender silently. Counting only the independent lane
makes a history rule an amplifier of *other* evidence and never of itself.

## The managed rule pack

A packaged, versioned set of rules ships with the product and its version is
stamped into every verdict as `engine_version`. The current pack:

| Rule id | Class | Weight | What it says |
|---|---|:--:|---|
| `ms-sender-first-contact` | signal | 30 | First message ever from this sender (`prevalence: none`) |
| `ms-sender-known-bad-history` | signal | 65 | This sender has been independently flagged before |
| `ms-sender-domain-newly-registered` | signal | 45 | The sender's domain was registered in the last week |
| `ms-auth-dmarc-fail` | signal | 50 | DMARC failed |
| `ms-auth-spf-fail-inbound` | signal | 40 | SPF failed on inbound mail |
| `ms-impersonation-vip-display-name` | signal | 55 | Display name matches a VIP but the address does not |
| `ms-impersonation-org-domain-lookalike` | signal | 70 | Sender domain is one or two edits from one of your domains |
| `ms-impersonation-exact-org-domain-external` | **detection** | 85 | Claims one of your domains but arrived from outside |
| `ms-impersonation-reply-to-mismatch` | signal | 35 | `Reply-To` points at a different organization than `From` |
| `ms-link-display-href-mismatch` | signal | 60 | A link's visible text names a different site than its destination |
| `ms-link-credentials-in-url` | signal | 75 | A link embeds credentials before the host |
| `ms-link-mixed-script-domain` | **detection** | 80 | A link's domain mixes writing systems within one label |
| `ms-link-unranked-domain` | signal | 30 | A link points at a domain absent from the top-1M list |
| `ms-link-known-malicious-url` | **detection** | 95 | A link matches the managed malicious-URL feed |
| `ms-graymail-list-unsubscribe` | graymail | — | Bulk mail carrying `List-Unsubscribe` |
| `ms-graymail-precedence-bulk` | graymail | — | The message declares itself bulk |

Rule ids are stable and are never renamed — that is the only reason an exclusion
or a per-rule override can be persisted at all.

You can disable a packaged rule or replace its weight for your organization
without forking anything, through
[`mailsec_policy/thresholds` → `rule_overrides`](policy.md#thresholds).

!!! tip "Judge a message without ingesting it"
    `POST /mailsec/{oid}/analyze` (`limacharlie mailsec analyze --file
    suspect.eml`) parses a raw message you supply and runs the enrichers and the
    packaged rules against default policy. **Nothing is ingested or stored**: no
    index row is written, no raw copy is kept, and the organization's mail
    history is unchanged. It is how you test a rule change, or analyze a sample
    that was never in the tenant. The tenant-specific context it cannot have —
    your sender history, your VIP list — is named explicitly in the response
    rather than silently missing.

## Two seats for rules

Signal rules run in the collector, before the verdict is emitted. Platform D&R
rules run afterwards, on the emitted events, with the whole response arsenal.
Same syntax, different seat. See [Custom Rules](custom-rules.md) and
[Events & Automation](automation.md).
