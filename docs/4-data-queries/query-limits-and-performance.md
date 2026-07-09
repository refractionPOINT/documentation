# Query Limits & Performance

This page describes the operational limits that apply to Query Console and LCQL searches - how many queries you can run at once and how long a query may run - along with guidance on how large an aggregation can reasonably get and how to write efficient queries that stay within those limits and cost less. It also covers the different query types, since how a query executes determines how it behaves against these limits.

## Query Types

How a query executes - and therefore how it behaves against the limits below - depends on what it does. LCQL queries fall into four kinds:

| Query type | What it does | Execution |
|------------|--------------|-----------|
| **Stateless** | Evaluates each event independently against the filter and returns the matching events. This is the default. | Paged: results come back a page at a time, and you fetch more on demand. |
| **Projection** | Adds a projection clause at the end of the query to return only selected or renamed fields instead of whole events. | Paged, as long as it only selects or renames fields; `GROUP BY`, `ORDER BY`, or an aggregation function make it whole-timeline. |
| **Aggregation** | Uses aggregation functions in the projection (`COUNT`, `COUNT_UNIQUE`, `GROUP BY`, and similar) to summarize matching events. | Whole timeline: the entire selected time range is scanned before any result is returned. |
| **Stateful** | Uses a filter that correlates across events, such as `with child`, so a match depends on more than one event. | Whole timeline: the entire selected time range is scanned before any result is returned. |

**Paged** queries (a stateless filter, or a projection that only selects fields) stream results incrementally and rarely run long. **Whole-timeline** queries (anything that sorts, groups, aggregates, or correlates across events) must scan the full range before returning, so they consume the most resources and are the ones that can reach the [query timeout](#query-timeouts).

## Data Sources (Streams)

Every query runs against one data *stream*, chosen with the Source dropdown in the Query Console or the `stream` parameter in the API, CLI, and SDKs. The stream determines which kind of records the query scans:

| Stream | Console label | Contains |
|--------|---------------|----------|
| `event` | Events | Raw telemetry collected from endpoints, adapters, and other sensors. This is the default. |
| `detection` | Detections | Detections produced by your D&R rules. |
| `audit` | Platform Audit | Platform audit records, such as configuration changes and user actions. |

A query only sees data from the stream it targets - a query on the `event` stream will not match detections, and vice versa. When the `stream` parameter is omitted it defaults to `event`. If a query returns nothing you expected to see, confirm you are searching the intended stream.

## Concurrent Queries

Each organization can run several queries at the same time. Every organization is guaranteed a minimum of **10 concurrent queries**, and the effective limit may be higher depending on your region and plan.

Both interactive Query Console searches and searches issued through the API, CLI, or SDKs count toward this limit. A paginated query counts as active for the entire time it is fetching pages, not only at the moment it starts.

When the limit is reached, additional queries are rejected with an `HTTP 429` (too many concurrent queries) response until one of the in-flight queries finishes. Retry the rejected query once an earlier one completes.

!!! tip
    If you regularly run automation or dashboards that need more headroom, contact support to request a higher concurrent-query limit for your organization.

## Query Timeouts

A single query has a maximum execution time of roughly **8 to 9 minutes**. If a query exceeds this deadline it returns an error rather than partial results.

**Paged queries (a stateless filter or a field-only projection).** Each page fetches a bounded number of events and returns quickly, so paged queries should effectively never reach the timeout. When you need more results, fetch the next page rather than trying to widen a single request.

**Whole-timeline queries (sorting, aggregation, and stateful).** Sorting (`ORDER BY`), aggregations (`COUNT`, `COUNT_UNIQUE`, `GROUP BY`), and stateful filters (such as `with child`) must scan the entire selected time range before they can return results, because the outcome is only complete once every matching event has been evaluated. Over a very large time range or a high volume of data, the scan can exceed the timeout and the query returns an error. See [Query Types](#query-types) for the distinction.

!!! note "Working around whole-timeline timeouts"
    If a large aggregation times out, narrow the time range and split the work into several smaller queries that each cover an incremental slice of the range, then combine the results yourself.

    For example, instead of a single 24-hour aggregation, run the same aggregation over 24 consecutive one-hour windows and add the per-window counts together for the full-range total. Keep the query identical and only change the time range for each run:

    ```lcql
    plat == windows | WEL | event/EVENT/System/EventID == "4625" | COUNT(event) as FailedAttempts
    ```

    Each one-hour window stays well under the timeout. Set the time range per run using the Console time picker (absolute from/to), the CLI `set_time`, or the API `startTime` / `endTime` parameters.

    Splitting and summing works for additive aggregations like `COUNT`; a `COUNT_UNIQUE` result cannot simply be added across windows. For stateful queries (`with child`), narrow the scope instead, since splitting can miss correlations that span a window boundary.

## Aggregation Limits

Aggregations build in-memory groupings as they scan, so very high-cardinality aggregations become slow and unreliable. Treat the following as recommended guardrails for dependable results:

- `GROUP BY` distinct groups: keep well under **~1,000,000** distinct groups.
- `COUNT_UNIQUE` distinct values per field per group: keep well under **~5,000,000** distinct values.

The usual cause of blowing past these numbers is grouping by a near-unique field (see [Anti-patterns](#anti-patterns) below). Group by a coarser field, or narrow the scope, so the number of groups stays bounded.

!!! tip
    Add `ORDER BY(...) LIMIT N` to bound the output, and project only the fields you need to shrink each row. See [Writing Efficient and Performant Queries](#writing-efficient-and-performant-queries) below.

## Query Progress and Cost Reporting

Because a query can scan a large amount of data, the API reports both a pre-flight estimate before you run it and the actual progress and cost as results stream back. A query scans stored telemetry in discrete units called *batches*; the batch counts below are what drive a progress bar.

### Pre-flight estimate (validate)

The [validate endpoint](index.md#validate-query-syntax) returns an estimate of how much work a query represents before you run it:

- `batchesInScope` - the total number of batches the query will scan. This is the denominator for a progress bar.
- `eventsInScope` / `bytesInScope` - the estimated number of events and bytes in scope.
- `estimatedPrice` - the estimated cost, derived from the events in scope.

### Progress while paging

Each page of a running search reports how much of the query is complete so far in its `cumulativeStats`:

- `batchesInScope` - the total batches in scope (denominator); the same value for every page of the search.
- `batchesCompleted` - the batches processed so far across all pages (numerator).

Render progress as `batchesCompleted / batchesInScope`, clamped to 0-100%. This is exactly how the Query Console progress bar is computed. The per-page `batchesProcessed` field reports the batches handled by that single page. Byte- and event-weighted ratios (`bytesScanned / bytesInScope`, `eventsScanned / eventsInScope`) are also available as a smoother signal, but the batch ratio is the reliable one; guard against a zero denominator.

### Actual cost per page

Every page also returns the actual billing for the data it processed, so you do not have to trust the estimate for cost:

- `billedEvents` / `freeEvents` - the events on this page that were billed versus covered by a free-tier window (`billedEvents + freeEvents == eventsScanned`).
- `estimatedPrice` - the price for this page, derived from the actual `billedEvents`. The running totals across all pages are carried in `cumulativeStats`.

!!! warning "Estimates are approximate - rely on the per-page billing for cost"
    The pre-flight `estimatedPrice`, `eventsInScope`, and related validate estimates are approximations. Their accuracy varies with the query type and with internal optimizations that reduce how much data actually has to be scanned, which are not always reflected in the estimate. Treat the estimate as a planning aid only and never rely on it as the exact cost. The authoritative cost is the actual billing (`billedEvents` and the `estimatedPrice` derived from it) returned with each page and accumulated in `cumulativeStats`.

## Writing Efficient and Performant Queries

Query cost is measured by the amount of data churned (billed per 200,000 events evaluated), and speed tracks the same factor: the fewer events a query has to scan and the less data it has to return, the faster and cheaper it is. The patterns below reduce both.

### Prefer Projections (Select Only the Fields You Need)

By default a query returns whole events. Adding a projection clause (the segment after the final `|`) returns only the fields you name, which reduces the data transferred, speeds up the query, and lowers cost.

Non-aggregation query. Instead of returning every field of each matching event:

```lcql
-1h | * | NETWORK_CONNECTIONS | event/PORT > 1000
```

project just the two fields you actually care about:

```lcql
-1h | * | NETWORK_CONNECTIONS | event/PORT > 1000 | event/IP_ADDRESS as IP event/PORT as Port
```

Aggregation query. Projections also define what an aggregation emits. This returns only the source IP and its failed-logon count, sorted and capped:

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as SourceIP COUNT(event) as FailedAttempts GROUP BY(SourceIP) ORDER BY(FailedAttempts desc) LIMIT 50
```

### Narrow the Scope Early

Restrict what the query has to scan before it reaches the filter:

- Use the [Sensor Selector](../8-reference/sensor-selector-expressions.md) instead of `*` so only relevant sensors are searched (see below).
- Set the Event Type to the specific events you need rather than searching all event types.
- Use the tightest time range that answers your question.

Each of these lowers the number of events churned, which makes the query both faster and cheaper.

**Targeting sensors by ID.** When you know exactly which sensors you care about, matching on `sid` is the most efficient selector of all, because it narrows the scan to specific sensors before any events are read:

- A single sensor: `sid == "<sensor-id>"`.
- A specific set of sensors: combine terms with `or`, as in `sid == "<sid1>" or sid == "<sid2>" or sid == "<sid3>"`.

When you do not know the IDs, select by attribute instead - for example `plat == windows`, `"prod" in tags`, or by `hostname`. Sensor IDs are UUIDs, and a selector value that starts with a number must be backtick-quoted; see the [Sensor Selector reference](../8-reference/sensor-selector-expressions.md) for the full operator list and quoting rules.

### Bound Output with ORDER BY and LIMIT

For "top N" style questions, always add `ORDER BY(...) LIMIT N` so the result set is capped instead of returning every matching row. See [Sorting and Limiting Results](lcql-examples.md#sorting-and-limiting-results) for the full syntax.

### Aggregate Instead of Pulling Raw Events

When you only need counts or summaries, use `COUNT`, `COUNT_UNIQUE`, and `GROUP BY` rather than downloading raw events and counting them yourself. Aggregating in the query returns a small summary instead of a large event stream.

### Split Large Aggregations

If an aggregation over a wide time range is slow or times out, break it into smaller incremental time windows and combine the results, as described in [Working around whole-timeline timeouts](#query-timeouts) above.

### Anti-patterns

!!! warning "Avoid these patterns"
    - `*` sensor selector with no Event Type filter over a wide time range - this scans everything and is the slowest, most expensive shape of query.
    - Returning whole events when you only need a few fields - add a projection instead.
    - Grouping by a near-unique field such as a full command line, a raw timestamp, or a per-event identifier - this produces millions of groups and blows past the aggregation guardrails. Group by a coarser field.
    - Unbounded aggregations with no `LIMIT` - cap the output with `ORDER BY(...) LIMIT N`.

## Troubleshooting

### The query is rejected before it runs

[Validate the query](index.md#validate-query-syntax) first - the validate endpoint reports syntax errors without scanning any data. Common causes:

- **Field paths use `/`, not dots.** Write `event/FILE_PATH`, not `event.FILE_PATH`. Nested fields chain with slashes, as in `event/PARENT/FILE_PATH`.
- **A selector value that starts with a number must be backtick-quoted**, for example `` plat == `1password` ``.
- **Projection and aggregation go in the final clause**, after the last `|`. See [LCQL Examples](lcql-examples.md).

### The query returns no results

- **Wrong stream.** A query only sees the stream it targets. If you expected detections, query the `detection` stream rather than `event`. See [Data Sources (Streams)](#data-sources-streams).
- **Time range.** Confirm the range actually covers the data. In the Query Console, times use the timezone from your User Settings; API, CLI, and SDK times are Unix epoch seconds.
- **Selector too narrow.** An overly specific Sensor Selector or Event Type can exclude the data you want - widen it and re-run.
- **Field name.** A misspelled or non-existent field simply never matches. Use the Available Fields panel or the [event schema](../8-reference/event-schemas.md) to confirm field names.

### The query is rejected as too busy or times out

- **`HTTP 429` (too many concurrent queries).** You have reached the [concurrent-query limit](#concurrent-queries). Wait for an in-flight query to finish, then retry.
- **Timeout.** Long-running aggregations over large ranges can hit the [query timeout](#query-timeouts). Narrow the range or split the query into smaller windows.

## See Also

- [LCQL Examples](lcql-examples.md)
- [Query Console UI](query-console-ui.md)
- [Query with CLI](query-cli.md)
