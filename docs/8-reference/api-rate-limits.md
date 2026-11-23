# API Rate Limits

The LimaCharlie REST API limits how many requests a caller can make. There is one general limit that applies to every request, plus tighter limits on a few expensive endpoints. A request over a limit gets an `HTTP 429` response.

## General limit

Every request to the API counts against a limit measured over a rolling 60-second window.

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

- An Organization API key has its own budget for each organization it is used in. Two keys never share a budget, and one key used in two organizations has two budgets.
- A user has a single budget across all organizations, whether the user calls the API through a web login or with a user API key.
- The limit is not per IP address.

### When you go over

The API answers with `HTTP 429` and a JSON body that has the fields `error`, `used`, `quota` and `period`. Two headers come with it:

| Header | Meaning |
|--------|---------|
| `X-RateLimit-Quota` | The limit that applied to the request. |
| `X-RateLimit-Period` | The window length in seconds (`60`). |

The response has no `Retry-After` header. Back off and retry. Starting with a 10-second wait and doubling it on each further `429` works well. Spreading calls over the window helps more than retrying in a burst, and a job that regularly needs more than 500 requests per minute should use a bulk key.

## Endpoint limits

These limits apply on top of the general limit. They protect endpoints that scan a lot of data on every call.

An endpoint limit that is hit returns `HTTP 429` with a JSON body like this, with no `Retry-After` header:

```json
{"error": "api quota for \"<path>\" (120 in 1h0m0s) exceeded"}
```

Paths are relative to `https://api.limacharlie.io/v1`.

| Endpoint | Limit | Counted per |
|----------|-------|-------------|
| `/insight/{oid}/traffic/breakdown`<br>`/insight/{oid}/traffic/stats`<br>`/insight/{oid}/detections/breakdown`<br>`/insight/{oid}/detections/stats`<br>`/insight/{oid}/online/stats`<br>`/usage/{oid}` | 120 per hour | Key or user, per organization |
| `/insight/event_count/{oid}/{sid}` | 60 per hour | Key or user, per organization |
| `/orgs/{oid}/name` (rename an organization) | 3 per hour | Key or user, per organization |
| `/ai/*` (AI generation, used by the `limacharlie ai generate-*` commands) | 10 per minute | Key per organization, or user |

The AI endpoints answer an over-limit call with `{"error": "rate limit exceeded"}`.

### IOC and object searches

The object search endpoints `/insight/{oid}/objects/{objType}`, `/insight/{oid}/objects` and `/insight/{oid}/objects-details` limit only the searches that are costly to run. The budget belongs to the organization, so every key and user in it draws from the same pool.

| Search | Limit |
|--------|-------|
| Exact, prefix or suffix lookup | No extra limit |
| Substring or wildcard match | 20 per hour per organization |
| `/objects-details` with a non-default `time_range` | 50 per hour per organization |

A search that is both a substring match and a custom time range counts against the 20-per-hour budget only.

## Limits documented elsewhere

Some features have their own limits, described on their pages:

- Search and LCQL queries have a [concurrent query limit](../4-data-queries/query-limits-and-performance.md#concurrent-queries).
- AI Sessions have [per-user limits](../9-ai-sessions/api-reference.md#rate-limits) on registration, session creation and WebSocket messages.
- Email Security limits the number of raw message downloads. See the [Email Security API reference](../email-security/api-reference.md).

## SDK behavior

The SDKs can retry a `429` for you.

- **Python.** Retrying is off by default and the SDK raises `RateLimitError`. Create the client with `is_retry_quota_errors=True` to retry. See [Built-in Retry Logic](../6-developer-guide/sdks/python-sdk.md#built-in-retry-logic).
- **Go.** The SDK retries a `429` on its own, waiting 10 seconds between attempts. A request gets 4 attempts in total, and a `401` or `504` retry uses up one of them too.

## Related

- [API Keys](../7-administration/access/api-keys.md)
- [Reliable Tasking](../5-integrations/extensions/limacharlie/reliable-tasking.md), which keeps the number of API calls low for large fleets
