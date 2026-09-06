# API Reference

--8<-- "includes/email-security-beta.md"

All Email Security routes live under
`https://api.limacharlie.io/v1/mailsec/{oid}/…` and appear in the public OpenAPI
spec at [`/openapi`](https://api.limacharlie.io/openapi). Authentication is the
standard `Authorization: Bearer <JWT>` header.

!!! info "Permissions & enable gate"
    Every route requires the organization to be subscribed to
    `ext-email-security` — a `403` on any route means subscribe first. The `oid`
    is always taken from the authorized path.

    Reads and the read-only `POST`s (`analyze`, `rules/validate`,
    `rules/backtest`) require `mailsec.get`. Resolving a report requires
    `mailsec.set`. Anything that touches live mail — the action routes and the
    connection test — requires `mailsec.act`. Downloading raw message bytes
    requires `mailsec.get` **and** `mailsec.get.eml`.

    Connections, policy and custom rules are **not** `/mailsec` routes: their CRUD
    goes through Hive (`mailsec_provider`, `mailsec_policy`, `dr-mail`).

Shared behaviours:

- **Repeatable filters** are passed as repeated query keys —
  `?verdict=malicious&verdict=suspicious`. OR within a key, AND across keys.
- **Boolean selectors are tri-state.** An absent parameter means "not filtered",
  which is *not* the same as passing `false`.
- **Keyset pagination.** Pages carry `next_cursor`; pass it back as `?cursor=`.
  An empty `next_cursor` is the last page. A cursor is **bound to the filter set
  that minted it** — changing a filter mid-walk fails the next page rather than
  resuming at a position that means something else. Restart the walk.
- **Times** are RFC3339 or unix seconds on input.
- **A miss is not an error.** An unknown or expired message, campaign or report
  id returns a null object rather than a `404`: the index has a 35-day retention
  and a miss is a normal outcome.

## Reads

| Route | Returns |
|---|---|
| `GET /coverage` | Mailboxes discovered / protected / excluded / in error, message volume and the verdict funnel over the window, the parse-degradation rate, backfill progress, the emission backlog, per-connection health, and the `overview` block (open reports, active campaigns, resolved automation mode). Params: `since`, `until`. With no window the default period is served from a short-lived server-side memo; naming an explicit range always computes that exact range |
| `GET /messages` | `{messages, next_cursor}` — the message index. Filters: `mailbox`, `sender_email`, `sender_root_domain`, `campaign_id`, `link_domain`, `attachment_sha256`, `verdict[]`, `state[]`, `direction[]`, `user_reported`, `min_score`, `q`, `since`, `until`, `cursor`, `limit` |
| `GET /messages/{msg_uuid}` | `{message, mdm, mdm_source}` — the index row, the full signal rationale, the action timeline, and the Message Data Model. `mdm_source` is `stored` (the model the collector judged with, enrichments included) or `eml_reparse` (a fresh parse of the original bytes, no enrichments). `mdm_unavailable_reason` replaces the model when neither is available |
| `GET /messages/{msg_uuid}/similar` | `{messages, since}` — recent messages sharing at least one clustering key, each with the `matched_keys` that matched, plus the lookback window that was searched. Candidates, not a cluster |
| `GET /campaigns` | `{campaigns, next_cursor}`. Filters: `state[]`, `verdict[]`, `min_members`, `since`, `until`, `cursor`, `limit` |
| `GET /campaigns/{campaign_id}` | `{campaign}` — span, membership, verdict, and the keys that bound the messages together |
| `GET /reports` | The user-report queue. Params: `status[]` (`open`, `triaging`, `resolved`), `oldest_first`, `cursor`, `limit` |
| `GET /reports/{report_id}` | One report: who reported it, the message they reported, the original once located across the tenant's mailboxes, and its triage state |
| `GET /senders/{key}` | The accumulated profile for one correspondent. `key` is qualified (`email:someone@corp.example` or `domain:corp.example`) or a bare address or domain. A key with no profile says so explicitly rather than returning a zeroed profile |
| `GET /actions/{action_id}` | `{action}` — one audit entry expanded, **including the JSON request payload the message timeline omits**. For a raw-message download that payload carries the access justification. Gated on `mailsec.get`: reading who did what to a message is part of reading the product |
| `GET /onboarding` | `{scopes, steps, script}` — the setup steps, OAuth scopes and `gcloud` commands for connecting a tenant, for rendering in a setup flow. Each step carries a `console` and, where verifiable, a `verified_by` naming the connection-test check that proves it. Params: `provider` (`gworkspace` default, or `m365`), `project_id`, `sa_email`, `topic`, `subscription` — supply them and the commands come back ready to run rather than templated |

### `GET /messages/{msg_uuid}/eml`

The justified raw download. Requires `mailsec.get` **and** `mailsec.get.eml`, and
the `justification` query parameter is **required**.

| Param | |
|---|---|
| `justification` | Why these bytes are being accessed. Recorded against your authenticated identity in the organization's action audit and retained for 400 days — a failed attempt is recorded too. Stored verbatim; the backend enforces a minimum and a maximum length and refuses an over-long reason rather than truncating |

Raw copies expire 35 days after delivery (longer for flagged messages), after
which this returns a typed expiry error while the index row stays readable.

## Writes

| Route | Does |
|---|---|
| `POST /messages/{msg_uuid}/actions` | Perform a typed action on one message. Body: `action` (`quarantine_message`, `trash_message`, `move_to_spam`, `restore_message`, `banner_message`, `unbanner_message`), optional `reason`, optional `attempt` (idempotency token — omit to collapse onto the existing attempt). `banner_message` uses the organization's own banner, rendered from its `mailsec_policy` record of type `banners`; the body's `banner` field is **deprecated and ignored** and will be removed. Requires `mailsec.act` |
| `POST /campaigns/{campaign_id}/actions` | Sweep a campaign. Same body plus `confirm`. **Without `confirm` this previews** and changes nothing, returning the member ids, the distinct mailboxes, the counts and a `confirm` token derived from that exact member set. With `confirm` it executes exactly that set; a campaign that grew since the preview is refused. Capped at 500 members. Requires `mailsec.act` |
| `POST /reports/{report_id}/resolve` | Record a triage outcome. Body: `disposition` — one of `true_positive`, `false_positive`, `benign`. Resolving an already-resolved report succeeds and reports `already_resolved`, so two analysts clicking at once is not an error. Requires `mailsec.set` |
| `POST /connections/{record}/test` | Probe a configured connection and report each requirement independently: the credential, each scope, a real directory read, and — for Google Workspace — the notification subscription and topic. Every check carries `id`, `name`, `required`, `status`, and on failure `detail` and `remediation`. A failed **optional** check leaves `ok` true. Body: `include_watch` (Workspace only; the one probe with a side effect — it establishes an idempotent, self-expiring push watch). Takes a **record name, not a credential**. Requires `mailsec.act` |

### Read-only `POST`s

| Route | Does |
|---|---|
| `POST /analyze` | Parse a raw message into the Message Data Model and judge it with the packaged rules against default policy. **Nothing is ingested or stored**: no index row is written, no raw copy kept, and the organization's mail history is unchanged. Body: `eml_b64` (preferred) or `eml`, plus optional `org_domains` and `direction`. Tenant context it cannot have — your sender history, your VIP list — is named explicitly in the payload rather than silently missing. Requires `mailsec.get` |
| `POST /rules/validate` | Compile a candidate `dr-mail` rule and report its errors without saving it. Body: `rule` (object), optional `rule_id`. Runs the **same** validation the `dr-mail` Hive applies on save, so a rule this accepts is a rule that will save. An invalid rule is a `200` carrying `valid: false` and the reason, not an error response. Requires `mailsec.get` |
| `POST /rules/backtest` | Replay a candidate rule over the organization's indexed message window and report what it would have matched. Body: `rule`, optional `rule_id`, `since`, `until`. Every response carries a `coverage_note` and counts what it could not examine (`skipped_no_raw`, `skipped_unparse`, `truncated`). `precision` is `null` — not `0` — when nothing it matched has an analyst disposition yet. Requires `mailsec.get` |

## Action results

Action routes report the outcome honestly rather than flattening it into
success/failure:

| `result` | Meaning |
|---|---|
| `ok` | The provider was changed |
| `skipped` | The desired state already held; no provider write happened |
| `alert_only` | Decided and deliberately not performed, because the organization is not in enforce mode. **Not an error** |
| `failed` | The provider refused or errored; `error` carries the reason |
| `pending` | In flight |

A campaign sweep returns `attempted`, `succeeded`, `alert_only` and a per-member
`failed` map. It does not abort on the first error.

## Attribution

`actor` and `source` on every audit row are stamped by the server from the
caller's verified claims — a user token keeps its stable user id, and an
authorized organization API key is attributed as `api-key:<key-id>`. A request
body **cannot** supply `by`, `actor` or `source`: an audit trail is only worth
having if it names who really asked.

## SDK and CLI

The Python SDK exposes the same surface, and the CLI wraps it — see
[Command Line Interface](cli.md). Both are generated against these routes, so
anything documented here is reachable from either.
