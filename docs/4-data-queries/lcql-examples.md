# LCQL Examples

LimaCharlie Query Language (LCQL) lets you write structured queries against the telemetry in LimaCharlie. The examples below help you do targeted searches or hunts across your telemetry. You can also change them to build your own queries. The examples are sorted by *source*, but you can adjust them for your environment.

Share your unique queries.

If you wrote a unique query, or you want to share one with the community, join the [LimaCharlie Community](https://community.limacharlie.com/).

## Time Range

Every LCQL query has a time range. The source of that range depends on the interface that you use:

| Interface | How the time range is set |
|-----------|---------------------------|
| Replay API and raw LCQL query strings | The **first component of the query string**, before the first `\|` (for example `-24h \| ...`). |
| Query Console (web UI) | The **time picker** above the query editor, not the query text. |
| Search API | The **`startTime` and `endTime`** body parameters, in Unix epoch seconds. |
| CLI (`limacharlie search run`) | The **`--start` and `--end`** flags, in Unix epoch seconds. |

!!! note
    In the Search API, the CLI, and the Query Console, the explicit range has priority. The explicit range is the picker, `startTime` / `endTime`, or `--start` / `--end`. Any time prefix in the query string is removed and replaced. The examples on this page include the leading time component (`-24h |`) because they are raw LCQL. In raw LCQL, the time range is the first component of the query string.

### Time Formats in the Query String

When the time range is part of the query (raw LCQL and the Replay API), the first component accepts relative durations, absolute date/times, or a bounded range.

**Relative durations** count backwards from now with the Go [duration syntax](https://pkg.go.dev/time#ParseDuration). The units are `h`, `m`, and `s`. There is no unit for days or weeks, so give longer windows in hours (`-168h` is 7 days).

| Value | Meaning |
|-------|---------|
| `-24h` | Last 24 hours |
| `-90m` | Last 90 minutes |
| `-1h30m` | Last 1 hour and 30 minutes |

**Absolute date/times** accept common formats such as `2025-01-16 08:52:54` or `2025-01-16`. For precise control, include a timezone offset, for example a trailing `Z` or `+02:00`. A time without an offset is interpreted as UTC.

**Bounded ranges** join two values with `to`. Each side can be relative or absolute, and you can mix the two. A single value with no `to` means "from that time until now".

```lcql
-24h to -12h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with ".exe"
```

## General Queries

Search *all* event types on *all* Windows systems for a string in *any* field. The `event/*` selector is a subtree wildcard. It tests the value against every field in the event.

```lcql
-24h | plat == windows | * | event/* contains 'psexec'
```

!!! warning "`event/*` is powerful but slow"
    A subtree wildcard must test every field of every event. With the `*` event-type selector, the query also scans every event type. This is the most expensive shape of query. Use it for broad hunts. When you know which field holds the value, narrow the query to a specific event type and field, for example `NEW_PROCESS | event/COMMAND_LINE contains 'psexec'`. See [Query Limits & Performance](query-limits-and-performance.md#writing-efficient-and-performant-queries).

You can also apply the wildcard to a specific *subtree* instead of the whole event. A subtree is much cheaper than `event/*`. Windows Event Log records keep many fields under `event/EVENT/EventData`. This query matches a username in any of those fields, and it does not read the rest of the event:

```lcql
-24h | plat == windows | WEL | event/EVENT/EventData/* contains "administrator"
```

## GitHub Telemetry

GitHub logs are a good source of telemetry to find abuse or misuse of a repository or an account. When LimaCharlie ingests the logs correctly, you can see the GitHub log data with `plat == github`.

### GitHub Protected Branch Override

Show all GitHub branch protection overrides (a force push to a repository without all approvals) in the last 12h that came from a user outside the United States. Show the repository, the user, and the number of infractions.

```lcql
-12h | plat == github | protected_branch.policy_override | event/public_repo is false and event/actor_location/country_code is not "us" | event/repo as repo event/actor as actor COUNT(event) as count GROUP BY(repo actor)
```

which could result in:

| actor    |   count | repo                               |
|----------|---------|------------------------------------|
| alice    |      11 | example-org/frontend               |
| bob      |      11 | example-org/analytics              |
| carol    |       3 | example-org/devops                 |

## Network Telemetry

Endpoints record network details such as new connections and DNS requests. These details give combined information. You can also query this data for aggregate details and show the results in a readable form.

### Domain Count

Show all domains that contain "google" and that Windows hosts resolved in the last 10 minutes. Also show how many times each domain was resolved.

```lcql
-10m | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)
```

which could result in:

|   count | domain                     |
|---------|----------------------------|
|      14 | logging.googleapis.com     |
|      36 | logging-alv.googleapis.com |

### Domain Prevalence

Show all domains that contain "google" and that Windows hosts resolved in the last 10 minutes. Also show the number of unique Sensors that resolved each domain.

```lcql
-10m | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains 'google' | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as count GROUP BY(domain)
```

which could result in:

|   count | domain                     |
|---------|----------------------------|
|       4 | logging.googleapis.com     |
|       3 | logging-alv.googleapis.com |

## Process Activity

### Unsigned Binaries

Grouped and counted.

```lcql
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as Path event/HASH as Hash event/ORIGINAL_FILE_NAME as OriginalFileName COUNT(event) as Count GROUP BY(Path Hash OriginalFileName)
```

### Process Command Line Args

```lcql
-1h | plat == windows | NEW_PROCESS EXISTING_PROCESS | event/COMMAND_LINE contains "psexec" | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

### Stack Children by Parent

```lcql
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "cmd.exe" | event/PARENT/FILE_PATH as parent event/FILE_PATH as child COUNT_UNIQUE(event) as count GROUP BY(parent child)
```

## Windows Event Log (WEL)

You can query `WEL` type events in LimaCharlie when you ingest them with EDR telemetry or with a separate Adapter. The sample queries are in alphabetical order. Details of the threat or the technique are given where they apply.

### %COMSPEC% in Service Path

```lcql
-12h | plat == windows | WEL | event/EVENT/System/EventID == "7045" and event/EVENT/EventData/ImagePath contains "COMSPEC" | event/EVENT/EventData/ImagePath as ImagePath routing/hostname as Host
```

### Overpass-the-Hash

```lcql
-12h | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "9" and event/EVENT/EventData/AuthenticationPackageName == "Negotiate" and event/EVENT/EventData/LogonProcess == "seclogo" | event/EVENT/EventData/TargetUserName as User event/EVENT/EventData/IpAddress as SrcIP routing/hostname as Host
```

### Taskkill from a Non-System Account

#### Requires process auditing to be enabled

```lcql
-12h | plat == windows | WEL | event/EVENT/System/EventID == "4688" and event/EVENT/EventData/NewProcessName contains "taskkill" and event/EVENT/EventData/SubjectUserName not ends with "!" | event/EVENT/EventData/NewProcessName as Process event/EVENT/EventData/SubjectUserName as User routing/hostname as Host
```

### Logons by Specific LogonType

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" AND event/EVENT/EventData/LogonType == "10" | event/EVENT/EventData/TargetUserName as User event/EVENT/EventData/IpAddress as SrcIP routing/hostname as Host
```

### Stack/Count All LogonTypes by User

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" | event/EVENT/EventData/LogonType AS LogonType event/EVENT/EventData/TargetUserName as UserName COUNT_UNIQUE(event) as Count GROUP BY(UserName LogonType)
```

### Failed Logons

```lcql
-1h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as SrcIP event/EVENT/EventData/LogonType as LogonType event/EVENT/EventData/TargetUserName as Username event/EVENT/EventData/WorkstationName as SrcHostname
```

---

## Common Operators and Patterns

The filter (the clause before the projection) is a full detection-style expression. These examples show the most common operators and patterns. Combine them with the projection, aggregation, sorting, and limiting clauses in other sections of this page. For the broad `event/*` subtree wildcard, see [General Queries](#general-queries) above.

### String matching

Double-quoted values are case-insensitive. Single-quoted values are case-sensitive.

- Contains (case-insensitive): `event/FILE_PATH contains "temp"`
- Contains (case-sensitive): `event/FILE_PATH contains 'Temp'`
- Prefix / suffix: `event/FILE_PATH starts with "c:\\windows"` and `event/FILE_PATH ends with ".exe"`
- Regular expression: `event/COMMAND_LINE matches "(?i)invoke-\\w+"`
- Negation: `event/FILE_PATH not contains "system32"`

Combined example - executables that start from outside `system32`:

```lcql
-1h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with ".exe" and event/FILE_PATH not contains "system32" | event/FILE_PATH as Path event/COMMAND_LINE as CommandLine routing/hostname as Host
```

### Numeric comparison

Use `>` / `<` (or the words `is greater than` / `is lower than`):

```lcql
-1h | * | NETWORK_CONNECTIONS | event/PORT > 1024
```

### IP address and CIDR

- Match a CIDR range: `event/IP_ADDRESS cidr "10.0.0.0/8"`
- Public vs private address: `event/IP_ADDRESS is public address` (also `is private address`)

Example - outbound connections to public IPs on high ports:

```lcql
-1h | * | NETWORK_CONNECTIONS | event/IP_ADDRESS is public address and event/PORT > 1024 | event/IP_ADDRESS as IP event/PORT as Port routing/hostname as Host
```

### Field existence

`exists` matches events that contain the field, with any value:

```lcql
-1h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH exists
```

### Boolean logic and grouping

Combine terms with `and`, `or`, and `not`, and use parentheses to control precedence:

```lcql
-1h | plat == windows | NEW_PROCESS | (event/FILE_PATH ends with "cmd.exe" or event/FILE_PATH ends with "powershell.exe") and event/COMMAND_LINE contains "-enc"
```

### Stateful correlation (with child / with descendant / with events)

Stateful operators match an event only when a *related* event also matches a nested filter. You give the nested filter in parentheses after the operator. These operators scan the whole time range, so keep their scope small (see [Query Types](query-limits-and-performance.md#query-types)).

**`with child`** matches when the event has a **direct child** that matches the nested filter. For process events, "child" means a process that the event spawned directly. This query finds `cmd.exe` that directly spawns `calc.exe`:

```lcql
-6h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with "cmd.exe" with child (event/FILE_PATH ends with "calc.exe")
```

In the process trees below, the query matches the first tree but not the second. In the second tree, `calc.exe` is a grandchild, not a direct child:

```text
cmd.exe --> calc.exe                    (match)
cmd.exe --> firefox.exe --> calc.exe    (no match)
```

**`with descendant`** works like `with child`, but it matches at **any depth**: child, grandchild, and deeper. If you change the operator, the query matches both trees above:

```lcql
-6h | plat == windows | NEW_PROCESS | event/FILE_PATH ends with "cmd.exe" with descendant (event/FILE_PATH ends with "calc.exe")
```

**`with events`** correlates **proximal events on the same sensor**. The events do not need a parent/child relation. Another event that matches the nested filter must also occur. This example finds a host that ran a credential-dumping command line and, separately, a lateral-movement tool:

```lcql
-6h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "sekurlsa" with events (event/COMMAND_LINE contains "psexec")
```

!!! tip "Repetition thresholds (count / within)"
    To match *repeated* events, for example 5 failed logons in 60 seconds, use the `count` and `within` modifiers. These modifiers are available in [D&R stateful rules](../3-detection-response/stateful-rules.md) (YAML). Those rules use the same `with child` / `with descendant` / `with events` model, and they give more sample data.

### Target specific sensors

The sensor field accepts `*` (the whole organization), a [Sensor Selector](../8-reference/sensor-selector-expressions.md) expression, or a space-separated list of sensor IDs:

```lcql
-1h | 1a2b3c4d-1111-2222-3333-444455556666 5f6e7d8c-9999-8888-7777-666655554444 | NEW_PROCESS | event/FILE_PATH ends with ".exe"
```

!!! note "Aggregation functions"
    LCQL has two aggregation functions. `COUNT(...)` gives the number of matching rows. `COUNT_UNIQUE(...)` gives the number of distinct values of a field. There is no `SUM`, `AVG`, `MIN`, or `MAX`.

    - Do not use `COUNT_UNIQUE` on a field that is also a `GROUP BY` key. The result is always 1.
    - Do not use `GROUP BY` on high-cardinality fields, for example a full command line, a file hash, or a raw timestamp. Such a field makes a very large number of groups, is inefficient, and rarely gives useful information. Group by a coarser field instead.

---

## Sorting and Limiting Results

The projection clause supports `ORDER BY(...)` to sort the results and `LIMIT N` to cap the result set. They are evaluated after aggregation, so they apply to raw projections and to `GROUP BY` summaries.

### ORDER BY Syntax

```text
ORDER BY(<field> [asc|desc])
ORDER BY(<field>)                       # direction omitted; defaults to ascending
```

The parentheses are mandatory. They delimit the arguments of the operator inside the space-delimited projection clause. Direction keywords are case-insensitive, but the canonical form is lowercase `asc` / `desc`. A sort key can be a raw selector (for example `event/PORT`) or a projection alias (for example `Port`).

!!! note
    `ORDER BY` currently sorts on a single key. The backend does not support multi-key sort expressions at this time.

### LIMIT Syntax

```text
LIMIT <N>
```

`LIMIT` caps the number of rows that the query returns. Put it at the end of the projection clause, after any `ORDER BY`.

### Top N Noisiest Destination Ports

Sort raw events by a numeric field, no aggregation:

```lcql
-1h | * | NETWORK_CONNECTIONS | event/PORT > 1000 | event/IP_ADDRESS as IP event/PORT as Port ORDER BY(Port desc) LIMIT 100
```

### Top 50 Failed-Logon Source IPs

Sort an aggregated count, descending:

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as SourceIP COUNT(event) as FailedAttempts GROUP BY(SourceIP) ORDER BY(FailedAttempts desc) LIMIT 50
```

---

## See Also

- [LCQL Overview](index.md)
- [Query Console](query-console-ui.md)
- [Query Limits & Performance](query-limits-and-performance.md)
- [EDR Events](../8-reference/edr-events.md)
