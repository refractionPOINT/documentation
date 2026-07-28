# Query Limits & Performance

This page describes the operational limits for the Query Console and for LCQL searches. The limits control how many queries you can run at the same time and how long a query can run. This page also gives guidance about how large an aggregation can be. It shows how to write efficient queries that stay inside the limits and cost less. It also describes the query types, because the way that a query executes decides how the query behaves against these limits.

## Query Types

The way that a query executes depends on what the query does. This also decides how the query behaves against the limits below. There are four kinds of LCQL query:

| Query type | What it does | Execution |
|------------|--------------|-----------|
| **Stateless** | Evaluates each event on its own against the filter and returns the matching events. This is the default. | Paged: the results come back one page at a time, and you fetch more pages on demand. |
| **Projection** | Adds a projection clause at the end of the query. The query returns only selected or renamed fields, not whole events. | Paged, if it only selects or renames fields. `GROUP BY`, `ORDER BY`, or an aggregation function make it whole-timeline. |
| **Aggregation** | Uses aggregation functions in the projection (`COUNT`, `COUNT_UNIQUE`, `GROUP BY`, and similar) to summarize matching events. | Whole timeline: the query scans the full selected time range before it returns a result. |
| **Stateful** | Uses a filter that correlates across events, such as `with child`, so a match depends on more than one event. | Whole timeline: the query scans the full selected time range before it returns a result. |

**Paged** queries (a stateless filter, or a projection that only selects fields) return the results in increments and seldom run long. **Whole-timeline** queries sort, group, aggregate, or correlate across events. They must scan the full range before they return a result. They use the most resources, and they are the queries that can reach the [query timeout](#query-timeouts).

## Data Sources (Streams)

Every query runs against one data *stream*. Select the stream with the Source dropdown in the Query Console, or with the `stream` parameter in the API, CLI, and SDKs. The stream decides which kind of records the query scans:

| Stream | Console label | Contains |
|--------|---------------|----------|
| `event` | Events | Raw telemetry from endpoints, adapters, and other sensors. This is the default. |
| `detection` | Detections | Detections that your D&R rules produce. |
| `audit` | Platform Audit | Platform audit records, such as configuration changes and user actions. |

A query only sees data from the stream that it targets. A query on the `event` stream does not match detections, and a query on the `detection` stream does not match events. If you do not give the `stream` parameter, the default is `event`. If a query does not return the data that you expect, make sure that you search the correct stream.

## Concurrent Queries

Each organization can run several queries at the same time. Every organization gets a minimum of **10 concurrent queries**. The true limit can be higher, and depends on your region and plan.

Query Console searches and searches from the API, CLI, or SDKs both count against this limit. A paginated query is active for all the time that it fetches pages, not only when it starts.

When you reach the limit, the cloud rejects more queries with an `HTTP 429` (too many concurrent queries) response. This continues until one of the queries in flight finishes. Retry the rejected query after an earlier query completes.

!!! tip
    Contact support to ask for a higher concurrent-query limit for your organization. Do this if you run automation or dashboards that need more capacity.

## Query Timeouts

A single query has a maximum execution time of about **8 to 9 minutes**. If a query goes past this deadline, it returns an error and not partial results.

**Paged queries (a stateless filter or a field-only projection).** Each page fetches a limited number of events and returns quickly. Because of this, a paged query almost never reaches the timeout. When you need more results, fetch the next page. Do not make one request wider.

**Whole-timeline queries (sorting, aggregation, and stateful).** Sorting (`ORDER BY`), aggregations (`COUNT`, `COUNT_UNIQUE`, `GROUP BY`), and stateful filters (such as `with child`) must scan the full selected time range before they return results. The result is complete only after the query evaluates every matching event. On a very large time range, or with a high volume of data, the scan can go past the timeout and the query returns an error. See [Query Types](#query-types) for the difference between the query types.

!!! note "Working around whole-timeline timeouts"
    If a large aggregation times out, make the time range smaller. Split the work into several smaller queries. Each query covers one slice of the range. Then combine the results yourself.

    For example, do not run one 24-hour aggregation. Run the same aggregation over 24 one-hour windows, then add the counts of the windows together to get the total for the full range. Keep the query the same and change only the time range for each run:

    ```lcql
    plat == windows | WEL | event/EVENT/System/EventID == "4625" | COUNT(event) as FailedAttempts
    ```

    Each one-hour window stays well below the timeout. Set the time range for each run with the Console time picker (absolute from/to), the CLI `set_time`, or the API `startTime` / `endTime` parameters.

    You can split and add additive aggregations such as `COUNT`. But you cannot add a `COUNT_UNIQUE` result across windows. For stateful queries (`with child`), make the scope smaller instead, because a split can miss correlations that cross a window boundary.

## Aggregation Limits

An aggregation builds groups in memory as it scans. Thus an aggregation with very high cardinality becomes slow and unreliable. Use these values as guardrails for dependable results:

- `GROUP BY` distinct groups: keep well under **~1,000,000** distinct groups.
- `COUNT_UNIQUE` distinct values per field per group: keep well under **~5,000,000** distinct values.

The usual cause of a value above these numbers is a query that groups by a near-unique field (see [Anti-patterns](#anti-patterns) below). Group by a coarser field, or make the scope smaller, to keep the number of groups limited.

!!! tip
    Add `ORDER BY(...) LIMIT N` to limit the output. Project only the fields that you need, to make each row smaller. See [Writing Efficient and Performant Queries](#writing-efficient-and-performant-queries) below.

## Query Progress and Cost Reporting

A query can scan a large amount of data. Because of this, the API reports an estimate before you run the query, and the true progress and cost while the results come back. A query scans stored telemetry in separate units that are called *batches*. The batch counts below drive a progress bar.

### Pre-flight estimate (validate)

The [validate endpoint](index.md#validate-query-syntax) returns an estimate of the work of a query before you run it:

- `batchesInScope` - the total number of batches that the query scans. This is the denominator for a progress bar.
- `eventsInScope` / `bytesInScope` - the estimated number of events and bytes in scope.
- `estimatedPrice` - the estimated cost, from the events in scope.

### Progress while paging

While a search runs, each page reports how much of the query is complete in its `cumulativeStats`:

- `batchesInScope` - the total batches in scope (denominator). This value is the same for every page of the search.
- `batchesCompleted` - the batches that the query processed so far across all pages (numerator).

Show the progress as `batchesCompleted / batchesInScope`, clamped to 0-100%. The Query Console computes its progress bar in this way. The per-page `batchesProcessed` field reports the batches of that one page. Byte and event ratios (`bytesScanned / bytesInScope`, `eventsScanned / eventsInScope`) are also available and give a smoother signal. But the batch ratio is the reliable one. Guard against a denominator of zero.

### Actual cost per page

Every page also returns the true billing for the data that it processed. Thus you do not have to trust the estimate for the cost:

- `billedEvents` / `freeEvents` - the events on this page that are billed, compared to the events that a free-tier window covers (`billedEvents + freeEvents == eventsScanned`).
- `estimatedPrice` - the price for this page, from the true `billedEvents`. The `cumulativeStats` field carries the running totals across all pages.

!!! warning "Estimates are approximate - rely on the per-page billing for cost"
    The pre-flight `estimatedPrice`, `eventsInScope`, and the related validate estimates are approximations. Their accuracy changes with the query type and with internal optimizations that decrease how much data the query must scan. The estimate does not always include these optimizations. Use the estimate only to plan, and never as the exact cost. The authoritative cost is the true billing (`billedEvents` and the `estimatedPrice` from it). Each page returns this billing, and `cumulativeStats` accumulates it.

### Building a Progress Bar

The Query Console draws its progress bar with this formula:

```text
progress = clamp(batchesCompleted / batchesInScope, 0, 100%)
```

Use `batchesInScope` as the denominator. Get this value from the [validate response](#pre-flight-estimate-validate) before the search starts, or from the `cumulativeStats` of each page after the search starts. Use the per-page `cumulativeStats.batchesCompleted` as the numerator. Two rules keep the bar correct:

- **Guard the denominator.** `batchesInScope` is `0` (or absent) until the scope is known. Show the progress as unavailable. Do not divide by zero.
- **Clamp the ratio.** `batchesCompleted` can be more than `batchesInScope` for a short time when a batch is re-opened across page boundaries. Clamp the value to 100%. The `completed` flag of a page is the authoritative "done" signal.

The examples below take one Search API page response (a parsed `SearchResponse`). They return a percentage in the range 0-100.

=== "Python"

    ```python
    --8<-- "snippets/python/progress_bar.py"
    ```

=== "Go"

    ```go
    --8<-- "snippets/golang/progress_bar/main.go"
    ```

=== "Bash (curl + jq)"

    ```bash
    # Denominator only, from the pre-flight validate response (before running):
    curl -s -X POST "https://$SEARCH_HOST/v1/search/validate" \
      -H "Authorization: Bearer $LC_JWT" -H "Content-Type: application/json" \
      -d '{"oid":"YOUR_OID","query":"...","startTime":"'"$START"'","endTime":"'"$END"'"}' \
      | jq '.stats.batchesInScope'

    # Progress from a running search page: clamp batchesCompleted/batchesInScope
    # to 0-100%, and treat a completed page as 100%.
    curl -s -X POST "https://$SEARCH_HOST/v1/search" \
      -H "Authorization: Bearer $LC_JWT" -H "Content-Type: application/json" \
      -d '{"oid":"YOUR_OID","query":"...","startTime":"'"$START"'","endTime":"'"$END"'","stream":"event"}' \
      | jq '
        ([.results[].stats.cumulativeStats | select(. != null)] | first) as $c
        | if .completed then 100
          elif ($c.batchesInScope // 0) > 0
          then ([100 * $c.batchesCompleted / $c.batchesInScope, 100] | min)
          else 0
          end'
    ```

See [Run an LCQL Query](index.md#run-an-lcql-query) to find `$SEARCH_HOST` and get a JWT.

## Writing Efficient and Performant Queries

The cost of a query depends on the amount of data churned (billed for each 200,000 events evaluated). The speed depends on the same factor. A query that scans fewer events and returns less data is faster and costs less. The patterns below improve both the speed and the cost.

### Prefer Projections (Select Only the Fields You Need)

By default, a query returns whole events. A projection clause (the segment after the last `|`) returns only the fields that you name. This decreases the data transferred, makes the query faster, and lowers the cost.

Non-aggregation query. This query returns every field of each matching event:

```lcql
-1h | * | NETWORK_CONNECTIONS | event/PORT > 1000
```

Project only the two fields that you need:

```lcql
-1h | * | NETWORK_CONNECTIONS | event/PORT > 1000 | event/IP_ADDRESS as IP event/PORT as Port
```

Aggregation query. A projection also defines what an aggregation returns. This query returns only the source IP and its count of failed logons, sorted and capped:

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as SourceIP COUNT(event) as FailedAttempts GROUP BY(SourceIP) ORDER BY(FailedAttempts desc) LIMIT 50
```

### Narrow the Scope Early

Limit the data that the query scans before it reaches the filter:

- Use the [Sensor Selector](../8-reference/sensor-selector-expressions.md) and not `*`, so that the query searches only the applicable sensors (see below).
- Set the Event Type to the specific events that you need. Do not search all event types.
- Use the smallest time range that answers your question.

Each of these decreases the number of events churned. This makes the query faster and cheaper.

**Targeting sensors by ID.** A match on `sid` is the most efficient selector. Use it when you know the exact sensors that you want. It limits the scan to specific sensors before the query reads any events:

- A single sensor: `sid == "<sensor-id>"`.
- A specific set of sensors: combine terms with `or`, as in `sid == "<sid1>" or sid == "<sid2>" or sid == "<sid3>"`.

When you do not know the IDs, select by attribute - for example `plat == windows`, `"prod" in tags`, or `hostname`. Sensor IDs are UUIDs. You must put backticks around a selector value that starts with a number. See the [Sensor Selector reference](../8-reference/sensor-selector-expressions.md) for the full list of operators and the rules for quotes.

### Bound Output with ORDER BY and LIMIT

For "top N" questions, always add `ORDER BY(...) LIMIT N`. This caps the result set, and the query does not return every matching row. See [Sorting and Limiting Results](lcql-examples.md#sorting-and-limiting-results) for the full syntax.

### Aggregate Instead of Pulling Raw Events

When you need only counts or summaries, use `COUNT`, `COUNT_UNIQUE`, and `GROUP BY`. Do not download raw events and count them yourself. An aggregation in the query returns a small summary and not a large stream of events.

### Split Large Aggregations

If an aggregation over a wide time range is slow or times out, divide it into smaller time windows and combine the results. [Working around whole-timeline timeouts](#query-timeouts) above describes this method.

### Anti-patterns

!!! warning "Avoid these patterns"
    - Do not use the `*` sensor selector with no Event Type filter over a wide time range. This query scans everything, and it is the slowest and most expensive query.
    - Do not return whole events when you need only a few fields. Add a projection.
    - Do not group by a near-unique field such as a full command line, a raw timestamp, or a per-event identifier. This makes millions of groups and goes past the aggregation guardrails. Group by a coarser field.
    - Do not run an aggregation with no `LIMIT`. Cap the output with `ORDER BY(...) LIMIT N`.

## Troubleshooting

### The query is rejected before it runs

[Validate the query](index.md#validate-query-syntax) first. The validate endpoint reports syntax errors and does not scan any data. Common causes:

- **Field paths use `/`, not dots.** Write `event/FILE_PATH`, not `event.FILE_PATH`. Nested fields join with slashes, as in `event/PARENT/FILE_PATH`.
- **A selector value that starts with a number must be backtick-quoted**, for example `` plat == `1password` ``.
- **Projection and aggregation go in the final clause**, after the last `|`. See [LCQL Examples](lcql-examples.md).

### The query returns no results

- **Wrong stream.** A query only sees the stream that it targets. If you want detections, query the `detection` stream and not the `event` stream. See [Data Sources (Streams)](#data-sources-streams).
- **Time range.** Make sure that the range covers the data. In the Query Console, times use the timezone from your User Settings. API, CLI, and SDK times are Unix epoch seconds.
- **Selector too narrow.** A Sensor Selector or Event Type that is too specific can exclude the data that you want. Make it wider and run the query again.
- **Field name.** A field name with a spelling error, or a field that does not exist, never matches. Use the Available Fields panel or the [event schema](../8-reference/event-schemas.md) to check field names.

### The query is rejected as too busy or times out

- **`HTTP 429` (too many concurrent queries).** You reached the [concurrent-query limit](#concurrent-queries). Wait for a query in flight to finish, then retry.
- **Timeout.** A long aggregation over a large range can reach the [query timeout](#query-timeouts). Make the range smaller, or divide the query into smaller windows.

## See Also

- [LCQL Examples](lcql-examples.md)
- [Query Console UI](query-console-ui.md)
- [Query with CLI](query-cli.md)
