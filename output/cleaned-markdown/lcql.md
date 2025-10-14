# LimaCharlie Query Language

LimaCharlie Query Language (LCQL) provides a flexible, intuitive and interactive way to explore your data in LimaCharlie. Telemetry ingested via EDR sensors or adapters are searchable via LCQL, and can be searched en masse. Sample use cases for LCQL include:

* Analyze your entire, multi-platform fleet for network connections of interest.
* Search across all Windows Event Logs for unique user activity.
* Look at all Linux systems for specific package installation events.
* Analyze all volume mounts and unmounts on macOS devices
* And many more!!!

The steps below walk you through creating your own LCQL queries. If you're looking for samples or LCQL inspiration, check out our [LCQL Examples](/v2/docs/lcql-examples) page.

> **Beta Feature**: LCQL is currently in Beta, and features may change in the future.

## Building LimaCharlie Queries

LCQL queries contain 4 components with a 5th optional one, each component is separated by a pipe (`|`):

1. **Timeframe**: the time range the query applies to. This can be either a single offset in the past like `-1h` or `-30m`. Or it can be a date time range like `2022-01-22 10:00:00 to 2022-01-25 14:00:00`.

   Note: the time frame is still used in the CLI and API, but no longer exposed in the UI; use the time selector control instead.

2. **Sensor selector**: the set of sensors to query. This can be either `*` for all sensors, or a [Sensor Selector expression](/v2/docs/reference-sensor-selector-expressions), like `plat == windows` or `hostname == foo.com or hostname == bar.com` (Note: a full list of platform types can be found in the [ID Schema Reference](/v2/docs/reference-id-schema))

3. **Event type**: the event types to include in the query. Use `or` to search for multiple events at once, for example `NEW_PROCESS or DNS_REQUEST`, or a `*` to go over all event types.

4. **Filters**: the actual query filters. The filters are a series of statements combined with "and" and "or" that can be associated with parenthesis (`()`). String literals, when used, can be double-quoted to be case insensitive or single-quoted to be case sensitive. Selectors behave like rules, for example: `event/FILE_PATH`.

   The [Query Console UI](/v2/docs/query-console-ui) provides a type-ahead assistance to bring up the available operators and help design the query.

5. **Projection (optional)**: a list of fields you would like to extract from the results with a possible alias, like: `event/FILE_PATH as path event/USER_NAME AS user_name event/COMMAND_LINE`. The Projection can also support a grouping functionality by adding `GROUP BY(field1 field2 ...)` at the end of the projection statement.

   When grouping, all fields being projected must either be in the `GROUP BY` statement, or have an aggregator modifier. An aggregator modifier is, for example, `COUNT( host )` or `COUNT_UNIQUE( host )` instead of just `host`.

   A full example with grouping is:

   `-1h | * | DNS_REQUEST | event/DOMAIN_NAME contains "apple" | event/DOMAIN_NAME as dns COUNT_UNIQUE(routing/hostname) as hostcount GROUP BY(dns host)`

   which would give you the number of hosts having resolved a domain containing `apple`, grouped by domain.

> **Projection Syntax**: Note: There is no space between `BY` and the `(` opening of the parentheses in a projection.
>
> Example: `GROUP BY(dns host)` or `COUNT_UNIQUE(routing/hostname)`

All of this can result in a query like:

`-30m | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell" | event/COMMAND_LINE as cli event/FILE_PATH as path routing/hostname as host`

OR

`-30m | plat == windows | * | event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell"`