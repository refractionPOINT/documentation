# API Rate Limits

The LimaCharlie REST API limits how many requests a caller can make. Authenticated requests count against one general limit, and a few expensive endpoints have tighter limits on top of it. A request over a limit gets an `HTTP 429` response.

## General limit

Authenticated REST API requests count against a limit measured over a rolling 60-second window.

| Caller | Limit |
|--------|-------|
| Regular API key or user | 500 requests per 60 seconds |
| Bulk key | 1,000 requests per 60 seconds |

### Bulk keys

An [API key](../7-administration/access/api-keys.md#flair) gets the bulk limit in either of two ways:

- Its name ends in `_bulk`. This works for Organization API keys only.
- Its name carries the `[bulk]` flair, such as `orchestration-key[bulk]`. This works for Organization API keys and for user API keys.

A user API key needs the flair because its identity ends with the user's email address, so a `_bulk` suffix never matches.

### Who shares a budget

The budget follows the identity that makes the call:

- An Organization API key has a budget in the organization that issued it. Two differently named keys never share a budget.
- A web login uses the user's own budget, keyed on their email address.
- A user API key has its own budget, separate from the user's web login and from the user's differently named keys. Two user API keys with the same name, held by the same user, share one budget.
- User budgets, for a web login or a user API key, cover all organizations together.
- The limit is not per IP address.

### When you go over

The API answers with `HTTP 429` and a JSON body that has the fields `error`, `used`, `quota` and `period`. Two headers come with it:

| Header | Meaning |
|--------|---------|
| `X-RateLimit-Quota` | The limit that applied to the request. |
| `X-RateLimit-Period` | The window length in seconds (`60`). |

The response has no `Retry-After` header. Back off and retry. Starting with a 10-second wait and doubling it on each further `429` works well. Spreading calls over the window helps more than retrying in a burst, and a job that regularly needs more than 500 requests per minute should use a bulk key.

## Endpoint limits

These limits apply on top of the general limit. They protect endpoints that scan a lot of data on every call. The table lists common examples, not every endpoint with a limit.

Paths are relative to `https://api.limacharlie.io/v1`.

| Endpoint | Limit | Counted per |
|----------|-------|-------------|
| `/insight/{oid}/traffic/breakdown`<br>`/insight/{oid}/traffic/stats`<br>`/insight/{oid}/detections/breakdown`<br>`/insight/{oid}/detections/stats`<br>`/insight/{oid}/online/stats`<br>`/usage/{oid}` | 120 per hour for each endpoint | Credential, per organization. Each endpoint has its own budget. |
| `/insight/event_count/{oid}/{sid}` | 60 per hour | Credential, per organization |
| `/orgs/{oid}/name` (rename an organization) | 3 per hour | Credential, per organization |

Going over one of these returns `HTTP 429` with a JSON body like this, with no `Retry-After` header:

```json
{"error": "api quota for \"<path>\" (120 in 1h0m0s) exceeded"}
```

### AI generation

The `limacharlie ai generate-*` commands share one budget of 10 requests per minute. The budget follows the same identity as the [general limit](#who-shares-a-budget). Going over returns `HTTP 429` with `{"error": "rate limit exceeded"}`.

### IOC and object searches

The object search endpoints `/insight/{oid}/objects/{objType}`, `/insight/{oid}/objects` and `/insight/{oid}/objects-details` limit only the searches that are costly to run. The budget belongs to the organization, so every key and user in it draws from the same pool.

| Search | Limit |
|--------|-------|
| Exact match, or a single leading or trailing `%`, with the default history | No extra limit |
| Any other wildcard, such as `%foo%`, `fo%o` or `_` | 20 per hour per organization |
| An otherwise efficient `/objects-details` lookup with a non-default `time_range` | 50 per hour per organization |

A search that is both a wildcard scan and a custom time range counts against the 20-per-hour budget only. Going over returns `HTTP 429` with an `api quota for ... exceeded` error that names the search budget instead of the path.

## Limits documented elsewhere

Some features have their own limits, described on their pages:

- Search and LCQL queries have a [concurrent query limit](../4-data-queries/query-limits-and-performance.md#concurrent-queries).
- See the [AI Sessions rate limits](../9-ai-sessions/api-reference.md#rate-limits) for registration, interactive session creation and per-connection WebSocket limits. Organization API session creation has a separate organization-level limit.
- Email Security limits the number of raw message downloads. See the [Email Security API reference](../email-security/api-reference.md).

## SDK behavior

The SDKs can retry a `429` for you.

- **Python.** Retrying is off by default and the SDK raises `RateLimitError`. Create the client with `is_retry_quota_errors=True` to retry. A request then gets 3 attempts. After consecutive `429`s it waits 10 seconds before the second attempt and 20 seconds before the third, then waits 40 seconds before raising `RateLimitError`. See [Built-in Retry Logic](../6-developer-guide/sdks/python-sdk.md#built-in-retry-logic).
- **Go.** The SDK retries on its own. A request gets 4 attempts in total. It waits 10 seconds after a `429` and normally 5 seconds after a retryable `504`. After an eligible `401` it can refresh the JWT once and retry, which uses an attempt from the same budget.

## Related

- [API Keys](../7-administration/access/api-keys.md)
- [Reliable Tasking](../5-integrations/extensions/limacharlie/reliable-tasking.md), which keeps the number of API calls low for large fleets
