# Microsoft Provider Quarantine

--8<-- "includes/email-security-availability.md"

**Provider quarantine** shows Microsoft delivery observations and hosted-quarantine
release activity. Messages blocked before reaching a mailbox may never enter
LimaCharlie's message analysis pipeline. These observations therefore have no
LimaCharlie engine verdict, disposition or remediation result.

The console has two views:

- **Delivery observations**: `quarantined`, `filteredAsSpam`, and `failed` from
  Microsoft's message trace. A failed delivery is **not** a quarantined message.
- **Release activity**: end-user requests and later release or denial audit
  observations. Reading this view does not approve or perform a release.

Each view shows its own connection coverage. Optional application permissions
are configured in [Microsoft 365 setup](provider-setup/microsoft-365.md).

## Read coverage before interpreting an empty list

| State | Meaning |
|---|---|
| `ok` | The last bounded provider window was fully stored and the polling result is current |
| `pending` | A walk is still in progress; there may be more provider pages |
| `not_granted` | The optional permission is absent or the provider refused access |
| `not_evaluated` | This connection/feed has not produced a polling result yet |
| `error` | The provider read or durable write failed; this is not evidence of zero blocked mail |
| `stale` | The last complete poll is older than ten minutes |

`watermark` is the end of the last fully stored provider window. `last_success`
is the last complete poll; `as_of` is when the API fetched this response.
An empty list with unavailable or incomplete coverage cannot establish that
Microsoft blocked nothing. Microsoft may publish traces and audit records late.
The poller checks overlapping windows and suppresses repeated observations;
provider timestamps remain separate from the time LimaCharlie observed them.

Visibility starts with the previous 24 hours. Recovery resumes stored progress
rather than skipping unfinished pages. A gap beyond the provider's retention
window is reported as an error. Indexed observation metadata is retained in the
organization's evidence lane, up to 400 days; no message body, attachment or raw
audit blob is retained by these feeds. Unsent telemetry expires with the organization’s
configured evidence retention; a long emission outage does not extend that retention.
An invalid persisted event is marked `emission_rejected` and kept as provider history
without blocking later valid events or claiming the rejected event was delivered.

## CLI and API

These commands require a CLI build that includes provider visibility; confirm
availability with `limacharlie mailsec --help`. They require `mailsec.get` and an
Email Security subscription.

```bash
limacharlie mailsec provider-quarantine list --connection m365-prod --output yaml
limacharlie mailsec provider-quarantine list --status failed --limit 100 --output yaml
limacharlie mailsec release-request list --status requested --output yaml
```

Both support `--connection`, `--status`, `--since`, `--until`, `--cursor` and
`--limit` (1–1000). Times are RFC3339 or Unix seconds. Pass the returned
`next_cursor` unchanged and keep all filters unchanged while paging.

The corresponding read routes are `GET /mailsec/{oid}/provider-quarantine` and
`GET /mailsec/{oid}/release-requests`. Responses contain `provider_quarantine` or
`release_requests`, `next_cursor`, `coverage` and `as_of`. Each history row has
`id`, `connection`, `feed`, `source_id`, `status`, `ts`, `observed_at` and typed
`metadata`; the recipient is included when the provider supplies one.

## Events and identity

`EMAIL_PROVIDER_QUARANTINE` carries `provider_status`, `trace_id`,
`recipient_address`, `received_at`, `observed_at`, `connection` and `event_id`.
Sender, subject and Internet Message-ID are included when available within fixed
metadata limits; long subjects are clipped and oversized optional fields omitted.
`EMAIL_RELEASE_REQUEST` carries `audit_id`, `requested_at`, `observed_at`,
`connection` and `event_id`, plus provider-supplied recipient, actor and
`network_message_id` when available. Actual releases and denials stay in the
activity history; they do not produce new request events.

A resolved recipient carries `mailbox: {id, address, upn?}`, using the stable
provider handle and normalized primary SMTP address. An ambiguous known recipient or
an audit record without a recipient uses the connection sensor. External or unknown
recipients without a tenant mailbox record are omitted. The audit actor
can be an administrator and is never guessed to be the recipient.

Microsoft audit NetworkMessageId and message trace Internet Message-ID are
separate identifiers. A `quarantine_id` appears only with a proven correlation;
the current feeds do not supply a reliable bridge, so it is absent. Keep request,
release and denial observations as provider history rather than assuming they
identify a message in the LimaCharlie message index.

Events may be retried after interrupted delivery. Deduplicate automated work
using `event_id`. Use ordinary D&R event matching for alerts and reporting; these
feeds describe provider activity. To restore mail held by the optional Microsoft target, use the indexed message’s restore action described below.

## Mailbox scope limits

Recipient-bearing observations follow the connection's mailbox scope and exclusions.
For a restricted scope, an audit record without a recipient is omitted until it can be
linked to an in-scope mailbox; the administrative actor is never used as that link.
Only an unrestricted tenant connection can include recipient-less audit history.
Catch-up across historical polling windows stays pending until it reaches the current
polling interval; a finished old window does not claim current coverage.

Visibility requires a resolved mailbox scope. An unresolved `include_groups` scope
reports `error` instead of claiming coverage from the organization-wide mailbox index.
Use explicit `include_addresses` until group membership has been resolved. Ambiguous
provider handles preserve the recipient observation without inventing a mailbox ID.

## Optional Microsoft quarantine target (beta)

**Beta — requires Defender for Office 365 Plan 2; validated with early customers.**
The default remains the LC hidden folder. Opt in through **Email Security → Policy →
Quarantine target**, or save this flat `mailsec_policy` record:

```json
{"policy_type": "quarantine", "target": "microsoft"}
```

Set `target` to `lc_folder` to return to the default. This selects the destination;
it does not enable enforcement or override the organization’s alert-only mode.
Google Workspace continues using its existing provider-specific quarantine.

Microsoft requires the optional Graph application permission
`SecurityAnalyzedMessage.ReadWrite.All` and admin consent. Consent alone does not
prove a Plan 2 licence. Coverage has an independent `microsoft_quarantine` capability:
`not_granted`, `not_evaluated` (write capability not established), `not_licensed`,
`unsupported`, `available` (a writer request was accepted), or `stale`.
Successful reads of analyzed email records never establish licensed write capability.

The same `quarantine_message` action now returns `result: pending` when queued for
Microsoft. The collector resolves the exact Internet Message-ID and recipient to a
unique analyzed-email/network-message identity. Missing or ambiguous identities are
never guessed. The message drawer and `mailsec message get` include up to twenty
`provider_remediations`; `EMAIL_ACTION` includes `provider_remediation` with:

| Status | Meaning |
|---|---|
| `pending` | The durable request is queued or its placement is still being checked |
| `succeeded` | Microsoft’s documented latest delivery reports the requested placement |
| `unsupported` | Microsoft permission, licensing, identity or operation support prevented this request; inspect the separately recorded LC fallback |
| `failed` | Placement or fallback failed, or completion could not be confirmed before its bounded stage deadline |

Requests that wait more than thirty minutes expire before submission. The
execution budget is twenty minutes from the first owner claim; a known provider
refusal starts a separate twenty-minute LC fallback budget. Neither budget renews
on retry. A restore waiting behind quarantine gets its own execution budget.

A Microsoft `202` acknowledges acceptance. It does **not** prove completion.
Its `tracking_url` is a human Action Center portal link, never a Graph status API.
LimaCharlie polls the documented analyzed-email placement instead of inventing an
operation-status endpoint. `succeeded` means **requested placement observed**, not
proof that a particular Microsoft bulk operation caused that placement. See the
[Microsoft remediation API](https://learn.microsoft.com/en-us/graph/api/security-analyzedemail-remediate?view=graph-rest-1.0).

A definitive permission/licence/unsupported refusal falls back automatically to the
LC hidden folder. The outcome records both the Microsoft reason and
`fallback: {target: lc_folder, result: ok|skipped|failed}`. An LC success does not turn
the Microsoft status into success. Unknown submission failures and accepted requests
whose completion remains unconfirmed do not trigger another competing placement.

Restore follows the recorded quarantine target. Microsoft-held mail uses
`moveToInbox` and waits for observed `inbox_folder`; LC fallback restores the original
folder. A restore queues behind an outstanding Microsoft quarantine; other placement
changes are refused while it is pending. Jobs survive collector restarts, use
per-message replica guards, and never resubmit an uncertain accepted request.
Microsoft exposes no documented cancellation API: after an unconfirmed deadline,
check the Action Center before another manual placement change. A later observed
quarantine can still be restored through the indexed message.

Terminal and pending action events have stable `event_id` values for deduplicating
at-least-once delivery. Bulk jobs keep pending members open rather than treating
acceptance as completion. Provider remediation audit metadata follows the evidence
retention policy; it contains identities and outcomes, not message bodies.
