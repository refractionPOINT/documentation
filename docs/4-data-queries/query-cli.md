# Query with CLI

The command line interface is part of the Python CLI/SDK. Install it with `pip install limacharlie`. Then start it with `limacharlie search`.

## Context

You set the first 3 components of the query separately, and they stay the same between queries. Use these commands to set them:

1. Use `set_time` to set the time range of the query, for example `set_time -3h`. The value uses the [ParseDuration()](https://pkg.go.dev/time#ParseDuration) strings.
2. Use `set_sensors` to set the sensors that the query reads, for example `set_sensors plat == windows`. The value uses the [sensor selector](../8-reference/sensor-selector-expressions.md) grammar.
3. Use `set_events` to set the events to query, space separated, for example `NEW_PROCESS DNS_REQUEST`. This command supports tab completion.

After you set these components, give the last components: the Filter and the Projection.

Other commands are also available:

- Use `set_limit_event` to set the maximum number of events to scan in the query.
- Use `set_output` to copy the queries and their results to a file.
- Use `set_format` to show the results in `json` or `table` format.
- Use `stats` to show the total cost of the queries in this session.

## Querying

### Paged Mode

To run a query in paged mode, as described above, use the `q` (for "query") command.

In paged mode, the query returns a first subset of the results, usually some thousands of elements. To get more results, use the `n` (for "next") command to fetch the next page.

Some queries cannot run in paged mode: queries that do aggregation, and queries that use a stateful filter such as `with child`. For these queries, all results over the entire timeline are computed.

For example:
`q event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as count GROUP BY(domain)`

This command supports tab completion for elements of the query. For example, `event/DO` + "tab" suggests `event/DOMAIN_NAME` or other elements in the schema.

### Non Paged Mode

To force a full query over all the data, with no paging, use the "query all" (`qa`) command:

`qa event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as count GROUP BY(domain)`

### Dry Run

To simulate a query, use the `dryrun` command. The command queries the LimaCharlie API and returns an approximate worst-case cost for the query. The cost assumes that you fetch all pages over the entire time range.

For example:
`dryrun event/COMMAND_LINE contains "powershell" and event/FILE_PATH not contains "powershell"`
