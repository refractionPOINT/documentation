# LimaCharlie Query Language
Beta Feature

LCQL is currently in Beta, and features may change in the future.

LimaCharlie Query Language (LCQL) provides a flexible, intuitive and interactive way to explore your data in LimaCharlie. Telemetry ingested via EDR sensors or adapters are searchable via LCQL, and can be searched en masse. Sample use cases for LCQL include:

* Analyze your entire, multi-platform fleet for network connections of interest.
* Search across all Windows Event Logs for unique user activity.
* Look at all Linux systems for specific package installation events.
* Analyze all volume mounts and unmounts on macOS devices
* And many more!!!

Querying the past 30 days within LimaCharlie is free.

Queries can also be saved by clicking the `Save` button. To save, view, or edit saved queries, users will need to be granted appropriate permissions:

* `query.del` - Delete saved queries
* `query.get` - Get saved queries
* `query.get.mtd` - Get saved queries metadata
* `query.set` - Set saved queries
* `query.set.mtd`- Set saved queries metadata

The steps below walk you through creating your own LCQL queries. If you're looking for samples or LCQL inspiration, check out our [LCQL Examples](/v2/docs/lcql-examples) page.

## Building LimaCharlie Queries

LCQL queries contain 4 components with a 5th optional one, each component is separated by a pipe (`|`):

1. **Timeframe**: the time range the query applies to. This can be either a single offset in the past like `-1h` or `-30m`. Or it can be a date time range like `2022-01-22 10:00:00 to 2022-01-25 14:00:00`.
2. **Sensors**: the set of sensors to query. This can be either `*` for all sensors, a list of space separated SIDs like `111-... 222-... 333-...`, or it can be a [sensor selector](/v2/docs/reference-sensor-selector-expressions) like `plat == windows`.  (Note: a full list of platform types can be found in the [ID Schema Reference](/v2/docs/reference-id-schema))
3. **Events**: the list of events to include in the query, space separated like `NEW_PROCESS DNS_REQUEST`, or a `*` to go over all event types.
4. **Filter**: the actual query filter. The filters are a series of statements combined with " and " and " or " that can be associated with parenthesis (`()`). String literals, when used, can be double-quoted to be case insensitive or single-quoted to be case sensitive. Selectors behave like  rules, for example: `event/FILE_PATH`.

The currently supported filter operators are listed below:

| operator | example |
| --- | --- |
| `is` or `==` | `event/FILE_PATH is "c:\windows\calc.exe"` |
| `is not` or `!=` | `event/FILE_IS_SIGNED != 0` |
| `contains` | `event/FILE_PATH contains 'evil'` |
| `not contains` | `event/FILE_PATH not contains 'system32'` |
| `matches` | `event/FILE_PATH matches ".*system[0-9a-z].*"` |
| `not matches` |  |
| `starts with` | `event/FILE_PATH starts with "c:\windows"` |
| `not starts with` |  |
| `ends with` | `event/FILE_PATH ends with '.eXe'` |
| `not ends with` |  |
| `cidr` | `event/NETWORK_CONNECTIONS/IP_ADDRESS cidr "10.1.0.0/16"` |
| `is lower than` | `event/NETWORK_CONNECTIONS/PORT is lower than 1024` |
| `is greater than` |  |
| `is platform` | `is platform "windows"` |
| `is not platform` | `is not platform "linux"` |
| `is tagged` | `is tagged "vip"` |
| `is not tagged` |  |
| `is public address` | `event/NETWORK_CONNECTIONS/IP_ADDRESS is public address` |
| `is private address` |  |
| `scope` | `event/NETWORK_CONNECTIONS scope (event/IP_ADDRESS is public address and event/PORT is 443)` |
| `with child` / `with descendant` / `with events` | `event/FILE_PATH contains "evil" with child (event/COMMAND_LINE contains "powershell")` |

5. Projection (optional): a list of fields you would like to extract from the results with a possible alias, like: `event/FILE_PATH as path event/USER_NAME AS user_name event/COMMAND_LINE`. The Projection can also support a grouping functionality by adding `GROUP BY(field1 field2 ...)` at the end of the projection statement.

When grouping, all fields being projected must either be in the `GROUP BY` statement, or have an aggregator modifier. An aggregator modifer is, for example, `COUNT( host )` or `COUNT_UNIQUE( host )` instead of just `host`.

A full example with grouping is:

`-1h | * | DNS_REQUEST | event/DOMAIN_NAME contains "apple" | event/DOMAIN_NAME as dns COUNT_UNIQUE(routing/hostname) as hostcount GROUP BY(dns host)`

which would give you the number of hosts having resolved a domain containing `apple`, grouped by domain.

All of this can result in a query like:

`-30m | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell" | event/COMMAND_LINE as cli event/FILE_PATH as path routing/hostname as host`

OR

`-30m | plat == windows | * | event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell"`

Projection Syntax

Note: There is no space between `BY` and the `(` opening of the parentheses in a projection.

Example: `GROUP BY(dns host)` or `COUNT_UNIQUE(routing/hostname)`

## Using the CLI

The command line interface found in the Python CLI/SDK can be invoked like `limacharlie query` once installed (`pip install limacharlie`).

### Context

To streamline day to day usage, the first 3 components of the query are set seperatly and remain between queries.
 These 3 component can be set through the following commands:

1. `set_time` to set the timeframe of the query, like `set_time -3h` based on the [ParseDuration()](https://pkg.go.dev/time#ParseDuration) strings.
2. `set_sensors` to set the sensors who's data is queried, like `set_sensors plat == windows`, based on the [sensor selector](/v2/docs/reference-sensor-selector-expressions) grammar.
3. `set_events` to set the events that should be queried, space separated like `NEW_PROCESS DNS_REQUEST`. This command supports tab completion.

Once set, you can specify the last component(s): the Filter, and the Projection.

Several other commands are avaible to make your job easier:

* `set_limit_event` to set a maximum number of events to scan during the query.
* `set_output` to mirror the queries and their results to a file.
* `set_format` to display results either in `json` or `table`.
* `stats` to display the total costs incurred from the queries during this session.

### Querying

#### Paged Mode

The main method of running a query as described above (in paged mode) is to use the `q` (for "query") command.

Paged mode means that an initial subset of the results will be returned (usually in the 1000s of elements) and if you want to fetch more of the results, you can use the `n` (for "next") command to fetch the next page.

Some queries cannot be done in paged mode, like queries that do aggregation or queries that use a stateful filter (like `with child`). In those cases, all results over the entire timeline are computed.

For example:
`q event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as count GROUP BY(domain)`

This command supports tab completion for elements of the query, like `event/DO` + "tab" will suggest `event/DOMAIN_NAME` or other relevant elements that exist as part of the schema.

#### Non Paged Mode

You can also force a full query over all the data (no paging) by using the "query all" (`qa`) command like:

`qa event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as count GROUP BY(domain)`

#### Dry Run

To simulate running a query, use the `dryrun` command. This will query the LimaCharlie API and return to you an aproximate worst case cost for the query (assuming you fetch all pages over its entire time range).

For example:
`dryrun event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell"`

Endpoint Detection & Response

Command-line Interface