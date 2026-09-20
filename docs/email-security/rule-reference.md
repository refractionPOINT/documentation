# Mail Rule Reference

--8<-- "includes/email-security-beta.md"

Use this reference with [Mail Rules](custom-rules.md). It describes
`dr-mail` rules and the Message Data Model (MDM) they read. Platform D&R rules on
`EMAIL_*` events and [cloud posture rules](../cloud-security/mail-posture-rules.md)
have different wrappers and validation rules.

## Paths and phases

| Context | Example path |
|---|---|
| `dr-mail`, either phase | `sender/email/domain/root` |
| `dr-mail`, `post_verdict` only | `verdict/verdict` |
| `dr-general` on `EMAIL_MESSAGE` | `event/sender/email/domain/root` |
| `dr-general` on `EMAIL_VERDICT` | `event/revision/verdict` |
| Inside `scope` with `path: links` | `href_url/domain/root` |

The MDM is the root of a mail rule. Do not add `mdm/` or `event/`. The Hive
rejects `mdm/` paths and pre-verdict reads of `verdict`. Use `scope` to iterate
arrays of objects; `dr-mail` paths containing `?` or `*` are rejected.

## Operators

The complete `dr-mail` operator allowlist is:

`and`, `or`, `scope`, `exists`, `is`, `contains`, `starts with`, `ends with`,
`matches`, `is greater than`, `is lower than`, `is older than`, `cidr`,
`string distance`, `lookup`.

Use `not: true` on a condition to negate it; `is not` is not an operator.
`and` and `or` take `rules`; `scope` takes a single `rule`. See the platform's
[Detection Operators](../8-reference/detection-logic-operators.md) for operand syntax;
only the operators listed above are available in `dr-mail`.

`lookup` accepts only `hive://lookup/<name>` and reads the organization's lookup
Hive. Sensor-variable values (`[[name]]`) and template values (`{{ … }}`) are
rejected inside `detect`. Response templates are separate: the
[post-verdict example](custom-rules.md#what-a-post_verdict-rule-may-respond-with)
uses `{{ .msg_uuid }}` to bind an action to its message.

## Limits

| Per-rule limit | Maximum |
|---|---:|
| Record name (no prefix is reserved) | 64 bytes |
| Human-readable `name` | 256 bytes |
| Serialized `detect` JSON | 8 KiB |
| Detection nesting | 32 levels |
| `scope` operators | 2; nesting a scope inside another is rejected |
| `lookup` operators | 4 |
| Compiled regex instructions, one expression | 1,000 |
| Compiled regex instructions, all expressions | 5,000 |
| `respond` actions | 16 |
| Serialized `respond` JSON | 8 KiB |

Regex limits measure compiled instructions, not pattern characters. Validate
rules after changing regexes. Both `name` and `fp_notes` must be non-empty.
Scoring classes require `weight` from 1 to 100; graymail records must omit it.

## Choosing fields

| Question | Field or array scope |
|---|---|
| Who sent it? | `sender/email/local`, `sender/email/domain/root`, `sender/display_name` |
| Where would a reply go? | `headers/reply_to` (array of addresses), `sender/reply_to_mismatch` |
| Did authentication fail? | `auth/spf/result`, `auth/dmarc/result`; scope `auth/dkim` for individual signatures |
| What does the newest reply say? | `body/current_thread/text` or `body/current_thread/visible_text` |
| Does one link disguise its destination? | Scope `links`; compare `href_url/domain/root` and `mismatched` |
| Is a link's domain new or suspicious? | Scope `enrichments/link_features`; read `domain`, `domain_age_days`, `popularity_bucket` |
| Does an attachment match an IOC? | Scope `attachments`; read `sha256` or another hash |
| What did attachment analysis actually inspect? | Scope `attachments`; inspect `explode/scanners` before interpreting scanner-specific results |
| Is this a known sender? | `enrichments/sender_profile/prevalence` (`none`, `new`, `rare`, `common`) |
| Is the sender impersonating an organization? | `enrichments/lookalike/org_domain_distance`, `enrichments/lookalike/vip_hit` |
| What happened after a link was fetched? | `enrichments/detonation`; see [Link detonation](detections.md#link-detonation) |
| Was parsing or analysis incomplete? | `_meta/truncations`, `_meta/errors`, `_meta/explode_timeout`, `body/truncated` |

`scope` processes objects, not scalar strings. A scalar equality test on a whole
string array is not a membership test. For wildcard traversal of string arrays,
use a platform D&R rule on the emitted event, such as
`event/headers/domains/?`; that wildcard path is not accepted in `dr-mail`.

An email address is decomposed into `local` and `domain`; `sender/email` is an
object, not a string containing `user@example.com`. A domain's `raw` is the full
host, while `root` is its registrable domain. Use an exact comparison on `root`
for an ownership test; a substring search can also match `example.com.evil.test`.
An IP literal has no registrable root domain.

`links` and `enrichments/link_features` are separate arrays. A scope on one does
not bind an element of the other. Match related features in a single
`link_features` scope using its own `domain` field.

## Presence and missing evidence

Optional fields are omitted when empty; pointer fields are omitted when unset.
A pointer to a number can preserve zero, such as domain age zero or an exact
lookalike distance of zero. Many boolean fields omit `false`, so `op: is` with
`value: false` is not a general test for a negative result. A missing enrichment
can mean that the work never ran or could not finish.

For example, this condition requires a measured sender-domain age:

```yaml
op: and
rules:
  - op: exists
    path: enrichments/sender_domain/age_days
  - op: is lower than
    path: enrichments/sender_domain/age_days
    value: 7
```

A presence check distinguishes missing data from a measured zero. It does not
turn an omitted boolean into proof of a negative result. Use the parent result
and its scanner or completion indicators when that distinction matters.

Profiles and external enrichments are available only when the pipeline stamps
them. Detonation arrives after the first verdict. A rule referencing it will not
match during the initial pass. The [backtest](custom-rules.md#what-a-backtest-can-evaluate)
does not reconstruct the original enrichment stamps.

## Message fields

The tables below describe the JSON objects reachable from an MDM. Each field
name is **relative to the object in that table**, not a complete detection path.
Follow the linked object types to build a path; use `scope` for arrays of objects.
For example, MDM → sender → email → domain → root becomes
`sender/email/domain/root`.

**Presence** describes JSON serialization, not whether collection succeeded:

- **Always**: emitted whenever its containing object exists; may still be empty.
- **Non-empty**: omitted for an empty string/list, zero number, or false boolean.
- **When set**: optional object or pointer; a set numeric pointer can contain zero.

Timestamps are RFC 3339 strings. `direction` is `inbound`, `outbound`, or
`internal`; `provider` is `m365` or `gworkspace`. The verdict object is available
only after scoring. Recursive attachment children and attached messages remain
subject to parser and analysis depth limits.

<!-- Field tables checked against go-mailsec v0.1.78, the
legion_mailsec dependency at review time. Update from model JSON tags when that
wire contract changes; do not infer presence from Go field names or comments. -->

### MDM

| Field | Type | Presence |
|---|---|---|
| `mdm_version` | integer | Always |
| `direction` | string | Always |
| `provider` | string | Always |
| `msg_uuid` | string | Non-empty |
| `mailbox` | [Mailbox](#mailbox) | Always |
| `external` | [External](#external) | Always |
| `timestamps` | [Timestamps](#timestamps) | Always |
| `headers` | [Headers](#headers) | Always |
| `sender` | [Sender](#sender) | Always |
| `recipients` | [Recipients](#recipients) | Always |
| `subject` | string | Always |
| `body` | [Body](#body) | Always |
| `links` | array of [Link object](#link) | Non-empty |
| `attachments` | array of [Attachment](#attachment) | Non-empty |
| `auth` | [Auth](#auth) | Always |
| `hops` | array of [Hop](#hop) | Non-empty |
| `enrichments` | [Enrichments](#enrichments) | When set |
| `verdict` | [VerdictInfo](#verdictinfo) | When set |
| `_meta` | [Meta](#meta) | When set |

### Mailbox

| Field | Type | Presence |
|---|---|---|
| `id` | string | Non-empty |
| `address` | string | Always |
| `display_name` | string | Non-empty |

### External

| Field | Type | Presence |
|---|---|---|
| `provider_message_id` | string | Always |
| `thread_id` | string | Non-empty |
| `folder` | string | Non-empty |
| `spam_folder` | boolean | Non-empty |

### Timestamps

| Field | Type | Presence |
|---|---|---|
| `sent` | timestamp | When set |
| `received` | timestamp | Always |
| `ingested` | timestamp | Always |

### Headers

| Field | Type | Presence |
|---|---|---|
| `from` | [Address](#address) | Always |
| `reply_to` | array of [Address](#address) | Non-empty |
| `return_path` | [Address](#address) | When set |
| `null_return_path` | boolean | Non-empty |
| `message_id` | string | Non-empty |
| `in_reply_to` | string | Non-empty |
| `references` | array of string | Non-empty |
| `mailer` | string | Non-empty |
| `delivered_to` | string | Non-empty |
| `x_originating_ip` | string | Non-empty |
| `all` | array of [Header](#header) | Non-empty |
| `domains` | array of string | Non-empty |
| `ips` | array of string | Non-empty |

### Address

| Field | Type | Presence |
|---|---|---|
| `display_name` | string | Non-empty |
| `email` | [EmailAddress](#emailaddress) | Always |

### EmailAddress

| Field | Type | Presence |
|---|---|---|
| `local` | string | Non-empty |
| `domain` | [DomainInfo](#domaininfo) | Always |

### DomainInfo

| Field | Type | Presence |
|---|---|---|
| `raw` | string | Non-empty |
| `root` | string | Non-empty |
| `sld` | string | Non-empty |
| `tld` | string | Non-empty |
| `subdomain` | string | Non-empty |
| `punycode` | string | Non-empty |
| `is_idn` | boolean | Non-empty |

### Header

| Field | Type | Presence |
|---|---|---|
| `name` | string | Always |
| `value` | string | Always |

### Sender

| Field | Type | Presence |
|---|---|---|
| `display_name` | string | Non-empty |
| `email` | [EmailAddress](#emailaddress) | When set |
| `reply_to_mismatch` | boolean | Non-empty |
| `display_name_email` | string | Non-empty |
| `free_mail` | boolean | Non-empty |
| `disposable` | boolean | Non-empty |

### Recipients

| Field | Type | Presence |
|---|---|---|
| `to` | array of [Address](#address) | Non-empty |
| `cc` | array of [Address](#address) | Non-empty |
| `bcc` | array of [Address](#address) | Non-empty |
| `count` | integer | Non-empty |
| `undisclosed` | boolean | Non-empty |

### Body

| Field | Type | Presence |
|---|---|---|
| `html` | [HTMLBody](#htmlbody) | When set |
| `plain` | [PlainBody](#plainbody) | When set |
| `current_thread` | [ThreadSegment](#threadsegment) | When set |
| `previous_threads` | array of [PreviousThread](#previousthread) | Non-empty |
| `ips` | array of string | Non-empty |
| `has_remote_images` | boolean | Non-empty |
| `hidden_text_present` | boolean | Non-empty |
| `language` | string | Non-empty |
| `truncated` | boolean | Non-empty |

### HTMLBody

| Field | Type | Presence |
|---|---|---|
| `raw` | string | Non-empty |
| `inner_text` | string | Non-empty |
| `display_text` | string | Non-empty |
| `charset` | string | Non-empty |

### PlainBody

| Field | Type | Presence |
|---|---|---|
| `raw` | string | Non-empty |

### ThreadSegment

| Field | Type | Presence |
|---|---|---|
| `text` | string | Non-empty |
| `renderings` | array of [ThreadRendering](#threadrendering) | Non-empty |
| `visible_text` | string | Non-empty |
| `links` | array of [Link object](#link) | Non-empty |

### ThreadRendering

| Field | Type | Presence |
|---|---|---|
| `kind` | string | Always |
| `text` | string | Non-empty |
| `links` | array of [Link object](#link) | Non-empty |

### Link

| Field | Type | Presence |
|---|---|---|
| `href_url` | [URLInfo](#urlinfo) | Always |
| `display_text` | string | Non-empty |
| `display_url` | string | Non-empty |
| `mismatched` | boolean | Non-empty |
| `visible` | boolean | Non-empty |
| `source` | string | Non-empty |
| `from_form` | boolean | Non-empty |
| `form_password_input` | boolean | Non-empty |
| `rewritten_by` | string | Non-empty |
| `rewritten_url` | string | Non-empty |
| `redirects_resolved` | array of string | Non-empty |

### URLInfo

| Field | Type | Presence |
|---|---|---|
| `raw` | string | Non-empty |
| `scheme` | string | Non-empty |
| `domain` | [DomainInfo](#domaininfo) | Always |
| `path` | string | Non-empty |
| `query` | string | Non-empty |
| `fragment` | string | Non-empty |
| `is_ip` | boolean | Non-empty |
| `port` | integer | Non-empty |

### PreviousThread

| Field | Type | Presence |
|---|---|---|
| `sender` | string | Non-empty |
| `ts` | timestamp | When set |
| `text_excerpt` | string | Non-empty |

### Attachment

| Field | Type | Presence |
|---|---|---|
| `file_name` | string | Non-empty |
| `file_extension` | string | Non-empty |
| `content_type` | string | Non-empty |
| `content_disposition` | string | Non-empty |
| `content_id` | string | Non-empty |
| `size` | integer | Non-empty |
| `md5` | string | Non-empty |
| `sha1` | string | Non-empty |
| `sha256` | string | Non-empty |
| `tlsh` | string | Non-empty |
| `magic_type` | string | Non-empty |
| `is_inline` | boolean | Non-empty |
| `explode` | [Explode](#explode) | When set |

### Explode

| Field | Type | Presence |
|---|---|---|
| `depth` | integer | Non-empty |
| `children` | array of [Attachment](#attachment) | Non-empty |
| `message` | [MDM](#mdm) | When set |
| `vba` | [VBAInfo](#vbainfo) | When set |
| `qr` | array of [QRCode](#qrcode) | Non-empty |
| `ocr_excerpt` | string | Non-empty |
| `yara_matches` | array of string | Non-empty |
| `archive` | [ArchiveInfo](#archiveinfo) | When set |
| `flavors` | array of string | Non-empty |
| `scanners` | array of string | Non-empty |
| `file_count` | integer | Non-empty |
| `truncated` | boolean | Non-empty |
| `truncation_reasons` | array of string | Non-empty |

### VBAInfo

| Field | Type | Presence |
|---|---|---|
| `auto_exec` | array of string | Non-empty |
| `suspicious` | array of string | Non-empty |
| `hex_strings` | array of string | Non-empty |

### QRCode

| Field | Type | Presence |
|---|---|---|
| `url` | string | Non-empty |

### ArchiveInfo

| Field | Type | Presence |
|---|---|---|
| `encrypted` | boolean | Non-empty |
| `file_count` | integer | Non-empty |
| `max_depth_hit` | boolean | Non-empty |

### Auth

| Field | Type | Presence |
|---|---|---|
| `spf` | [SPFResult](#spfresult) | When set |
| `dkim` | array of [DKIMResult](#dkimresult) | Non-empty |
| `dmarc` | [DMARCResult](#dmarcresult) | When set |
| `arc` | [ARCResult](#arcresult) | When set |
| `compauth` | [CompAuthResult](#compauthresult) | When set |

### SPFResult

| Field | Type | Presence |
|---|---|---|
| `result` | string | Non-empty |
| `domain` | string | Non-empty |

### DKIMResult

| Field | Type | Presence |
|---|---|---|
| `result` | string | Non-empty |
| `domain` | string | Non-empty |
| `selector` | string | Non-empty |

### DMARCResult

| Field | Type | Presence |
|---|---|---|
| `result` | string | Non-empty |
| `policy` | string | Non-empty |
| `alignment` | boolean | Non-empty |

### ARCResult

| Field | Type | Presence |
|---|---|---|
| `result` | string | Non-empty |

### CompAuthResult

| Field | Type | Presence |
|---|---|---|
| `result` | string | Non-empty |
| `reason` | string | Non-empty |

### Hop

| Field | Type | Presence |
|---|---|---|
| `by` | string | Non-empty |
| `from` | string | Non-empty |
| `ip` | string | Non-empty |
| `protocol` | string | Non-empty |
| `ts` | timestamp | When set |
| `delay_s` | integer | Non-empty |

### Enrichments

| Field | Type | Presence |
|---|---|---|
| `sender_profile` | [SenderProfile](#senderprofile) | When set |
| `domain_profile` | [SenderProfile](#senderprofile) | When set |
| `sender_domain` | [SenderDomain](#senderdomain) | When set |
| `link_features` | array of [LinkFeature](#linkfeature) | Non-empty |
| `lookalike` | [Lookalike](#lookalike) | When set |
| `password_in_body` | boolean | Non-empty |
| `detonation` | [Detonation](#detonation) | When set |

### SenderProfile

| Field | Type | Presence |
|---|---|---|
| `first_seen_ts` | timestamp | When set |
| `days_known` | integer | Non-empty |
| `msg_count_30d` | integer | Non-empty |
| `flagged_count_180d` | integer | Non-empty |
| `flagged_count_other_addresses_180d` | integer | Non-empty |
| `prevalence` | string | Non-empty |
| `profile_key` | string | Non-empty |

### SenderDomain

| Field | Type | Presence |
|---|---|---|
| `domain` | string | Non-empty |
| `age_days` | integer | When set |
| `registered_ts` | timestamp | When set |

### LinkFeature

| Field | Type | Presence |
|---|---|---|
| `domain` | string | Non-empty |
| `domain_age_days` | integer | When set |
| `popularity_bucket` | string | Non-empty |
| `in_urlhaus` | boolean | Non-empty |
| `mixed_script` | boolean | Non-empty |
| `credentials_in_url` | boolean | Non-empty |

### Lookalike

| Field | Type | Presence |
|---|---|---|
| `vip_hit` | string | Non-empty |
| `org_domain_distance` | integer | When set |
| `brand_domain_distance` | integer | When set |

### Detonation

| Field | Type | Presence |
|---|---|---|
| `url` | string | Always |
| `hops` | array of [DetonationHop](#detonationhop) | Non-empty |
| `landing` | [DetonationLanding](#detonationlanding) | When set |
| `refusal` | [DetonationRefusal](#detonationrefusal) | When set |
| `elapsed_ms` | integer | Non-empty |
| `detonated_at` | timestamp | Always |

### DetonationHop

| Field | Type | Presence |
|---|---|---|
| `requested_url` | string | Non-empty |
| `host` | string | Non-empty |
| `resolved_ips` | array of string | Non-empty |
| `blocked_ips` | array of [DetonationBlockedIP](#detonationblockedip) | Non-empty |
| `connected_addr` | string | Non-empty |
| `status` | integer | Non-empty |
| `next_url` | string | Non-empty |
| `tls` | [DetonationTLS](#detonationtls) | When set |
| `duration_ms` | integer | Non-empty |
| `refusal` | [DetonationRefusal](#detonationrefusal) | When set |

### DetonationBlockedIP

| Field | Type | Presence |
|---|---|---|
| `ip` | string | Always |
| `reason` | string | Always |

### DetonationTLS

| Field | Type | Presence |
|---|---|---|
| `sni` | string | Non-empty |
| `version` | string | Non-empty |
| `cipher_suite` | string | Non-empty |
| `subject` | string | Non-empty |
| `issuer` | string | Non-empty |
| `sans` | array of string | Non-empty |
| `not_before` | timestamp | When set |
| `not_after` | timestamp | When set |
| `san_matches_host` | boolean | Always |
| `verified` | boolean | Always |
| `verify_error` | string | Non-empty |

### DetonationRefusal

| Field | Type | Presence |
|---|---|---|
| `reason` | string | Always |
| `kind` | string | Non-empty |

### DetonationLanding

| Field | Type | Presence |
|---|---|---|
| `effective_url` | string | Non-empty |
| `status` | integer | Non-empty |
| `body_sha256` | string | Non-empty |
| `body_bytes` | integer | Always |
| `body_complete` | boolean | Always |
| `title` | string | Non-empty |
| `text_excerpt` | string | Non-empty |
| `has_password_input` | boolean | Non-empty |
| `form_count` | integer | Non-empty |
| `form_action_hosts` | array of string | Non-empty |
| `signals_truncated` | boolean | Non-empty |

### VerdictInfo

| Field | Type | Presence |
|---|---|---|
| `verdict` | string | Always |
| `score` | integer | Always |
| `top_signals` | array of [TopSignal](#topsignal) | Non-empty |
| `matched_signals` | array of string | Non-empty |
| `tags` | array of string | Non-empty |
| `engine_version` | string | Non-empty |
| `decided_at` | timestamp | Always |
| `mode` | string | Non-empty |
| `campaign_id` | string | Non-empty |

### TopSignal

| Field | Type | Presence |
|---|---|---|
| `rule_id` | string | Always |
| `name` | string | Non-empty |
| `weight` | integer | Non-empty |
| `renderings` | array of string | Non-empty |

### Meta

| Field | Type | Presence |
|---|---|---|
| `truncations` | array of string | Non-empty |
| `errors` | array of [ParseError](#parseerror) | Non-empty |
| `explode_timeout` | boolean | Non-empty |

### ParseError

| Field | Type | Presence |
|---|---|---|
| `stage` | string | Always |
| `message` | string | Always |
