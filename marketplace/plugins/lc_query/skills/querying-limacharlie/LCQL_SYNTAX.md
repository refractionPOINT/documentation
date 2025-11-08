# LCQL Syntax Reference

Complete reference for the LimaCharlie Query Language (LCQL).

## Query Structure

All LCQL queries follow this five-part structure:

```
TIMEFRAME | SENSOR_SELECTOR | EVENT_TYPE | FILTER | PROJECTION
```

Each part is separated by the pipe character `|`. All parts except PROJECTION are required.

## 1. Timeframe

Defines the time range to search. Always the first part of the query.

### Syntax

```
-[NUMBER][UNIT]
```

### Units

| Unit | Description | Example |
|------|-------------|---------|
| `m` | Minutes | `-30m` = Last 30 minutes |
| `h` | Hours | `-24h` = Last 24 hours |
| `d` | Days | `-7d` = Last 7 days |

### Examples

```lcql
-10m    Last 10 minutes
-1h     Last 1 hour
-24h    Last 24 hours (1 day)
-7d     Last 7 days
-30d    Last 30 days
```

### Important Notes

- Timeframe is always **required** and must be the **first element**
- Larger timeframes = longer query times and higher costs
- Free tier queries limited to 30 days maximum
- Consider data volume when choosing timeframe

## 2. Sensor Selector

Filters which sensors/endpoints to query. Uses boolean expressions to match sensor attributes.

### Platform Selectors

Match by operating system or platform type.

```lcql
plat == windows        Windows endpoints
plat == linux          Linux endpoints
plat == macos          macOS endpoints
plat == chrome         Chrome endpoints
plat == github         GitHub telemetry
plat == azure          Azure cloud telemetry
plat == gcp            Google Cloud telemetry
plat == aws            AWS cloud telemetry
```

### Tag Selectors

Match sensors by their assigned tags.

```lcql
tag == production              Sensors tagged "production"
tag == webserver               Sensors tagged "webserver"
tag == critical                Sensors tagged "critical"
```

### Hostname Selectors

Match by hostname patterns.

```lcql
hostname == "server-01"               Exact hostname match
hostname contains "server"            Hostname contains substring
hostname starts with "web-"           Hostname starts with prefix
hostname ends with ".internal"        Hostname ends with suffix
```

### Other Selectors

```lcql
routing/sid == "UUID"                 Specific sensor ID
routing/ext_ip == "1.2.3.4"          Specific external IP
routing/int_ip == "10.0.1.5"         Specific internal IP
```

### Combining Selectors

Use `and` and `or` to combine conditions.

```lcql
plat == windows and tag == production
plat == linux or plat == macos
hostname contains "db" and tag == critical
plat == windows and (tag == dev or tag == test)
```

### Examples

```lcql
plat == windows
plat == linux and tag == production
hostname contains "web-server"
plat == windows and hostname starts with "dc-"
tag == critical or tag == production
```

## 3. Event Type

Specifies which event types to search. Can be one or multiple space-separated types.

### Syntax

```lcql
EVENT_TYPE_1                    Single event type
EVENT_TYPE_1 EVENT_TYPE_2       Multiple event types (space-separated)
*                               All event types (expensive!)
```

### Common Event Types

#### Process Events

```lcql
NEW_PROCESS           Process creation/execution
EXISTING_PROCESS      Running process snapshots
TERMINATE_PROCESS     Process termination
```

#### Network Events

```lcql
DNS_REQUEST               DNS queries
NETWORK_CONNECTIONS       Network connections
NEW_TCP4_CONNECTION       IPv4 TCP connections
NEW_UDP4_CONNECTION       IPv4 UDP connections
```

#### File Events

```lcql
FILE_CREATE           File creation
FILE_DELETE           File deletion
FILE_MODIFIED         File modification
FILE_OPEN             File open operations
```

#### Code & Binary Events

```lcql
CODE_IDENTITY         Binary signatures and metadata
MODULE_LOAD           DLL/module loading
```

#### Windows-Specific Events

```lcql
WEL                   Windows Event Logs
REGISTRY_CREATE       Registry key creation
REGISTRY_WRITE        Registry modification
USER_OBSERVED         User activity
```

#### Cloud & Adapter Events

```lcql
AdvancedHunting-*     Microsoft Defender events
azure-*               Azure events
gcp-*                 Google Cloud events
github-*              GitHub events
```

### Multiple Event Types

```lcql
NEW_PROCESS EXISTING_PROCESS          Both new and running processes
DNS_REQUEST NETWORK_CONNECTIONS       DNS and network activity
FILE_CREATE FILE_DELETE               File create and delete
```

### All Events

```lcql
*                                     Match ALL event types
```

**Warning**: Using `*` is expensive and slow. Only use when necessary or with highly specific filters.

### Discovering Event Types

Use MCP tools to discover available event types:

```
get_platform_names()
get_event_types_with_schemas_for_platform(platform="windows")
get_event_types_with_schemas()
```

## 4. Filter

Boolean expressions to filter events based on field values.

### Operators

#### Equality Operators

```lcql
==                    Equals
!=                    Not equals
is                    Same as ==
is not                Same as !=
```

#### String Operators

```lcql
contains              String contains (case-insensitive by default)
starts with           String starts with
ends with             String ends with
```

#### Numeric Operators

```lcql
>                     Greater than
<                     Less than
>=                    Greater than or equal
<=                    Less than or equal
```

### Logical Operators

```lcql
and                   Boolean AND
or                    Boolean OR
```

**Note**: Use parentheses `()` to group conditions when combining operators.

### Field Paths

All field paths use one of two prefixes:

#### `event/` - Event-Specific Fields

Fields specific to the event type (varies by event type).

```lcql
event/COMMAND_LINE              Process command line
event/FILE_PATH                 File or executable path
event/DOMAIN_NAME               DNS domain name
event/IP_ADDRESS                IP address
event/HASH                      File hash
event/PROCESS_ID                Process ID
event/SIGNATURE/FILE_IS_SIGNED  Binary signature status
event/PARENT/FILE_PATH          Parent process path
event/EVENT/System/EventID      Windows Event Log ID
```

#### `routing/` - Metadata Fields

Consistent across all event types (metadata).

```lcql
routing/hostname                Endpoint hostname
routing/sid                     Sensor ID (UUID)
routing/event_type              Event type
routing/event_time              Unix timestamp (milliseconds)
routing/int_ip                  Internal IP address
routing/ext_ip                  External IP address
routing/plat                    Platform identifier
routing/tags                    Sensor tags
routing/this                    Current process hash
routing/parent                  Parent process hash
routing/target                  Target object hash
```

### Nested Fields

Use `/` to access nested object fields.

```lcql
event/EVENT/System/EventID                    Windows Event Log event ID
event/EVENT/EventData/TargetUserName          Windows Event Log username
event/SIGNATURE/FILE_IS_SIGNED                Signature status
event/PARENT/FILE_PATH                        Parent process executable path
```

### Filter Examples

#### String Matching

```lcql
event/COMMAND_LINE contains "powershell"
event/DOMAIN_NAME contains "google"
event/FILE_PATH starts with "c:\\temp"
event/FILE_PATH ends with ".exe"
routing/hostname == "server-01"
```

#### Numeric Comparisons

```lcql
event/SIGNATURE/FILE_IS_SIGNED != 1
event/PROCESS_ID > 1000
event/EVENT/System/EventID == "4625"
```

#### Complex Filters

```lcql
event/COMMAND_LINE contains "psexec" and event/FILE_PATH not contains "windows"
event/DOMAIN_NAME contains "suspicious" or event/DOMAIN_NAME contains "malware"
(event/FILE_PATH contains "temp" or event/FILE_PATH contains "appdata") and event/SIGNATURE/FILE_IS_SIGNED != 1
```

#### Parent Process Filtering

```lcql
event/PARENT/FILE_PATH contains "cmd.exe"
event/PARENT/FILE_PATH contains "winword.exe" or event/PARENT/FILE_PATH contains "excel.exe"
```

#### Windows Event Log Filtering

```lcql
event/EVENT/System/EventID == "4624"
event/EVENT/EventData/LogonType == "10"
event/EVENT/System/EventID == "7045" and event/EVENT/EventData/ImagePath contains "COMSPEC"
```

## 5. Projection

Controls output formatting, aggregation, and sorting. This component is **optional**.

### Display Columns

Specify which fields to display and alias them.

```lcql
field1 as alias1 field2 as alias2 ...
```

**Examples:**

```lcql
event/DOMAIN_NAME as domain routing/hostname as host
event/FILE_PATH as path event/HASH as hash
event/COMMAND_LINE as cli routing/sid as sensor_id
```

### Aggregation Functions

#### COUNT

Count total number of events.

```lcql
COUNT(event) as count
```

#### COUNT_UNIQUE

Count unique values of a field.

```lcql
COUNT_UNIQUE(routing/sid) as unique_hosts
COUNT_UNIQUE(event/DOMAIN_NAME) as unique_domains
COUNT_UNIQUE(event/HASH) as unique_binaries
```

### Grouping

Group results by one or more fields.

```lcql
GROUP BY(field1)
GROUP BY(field1 field2)
GROUP BY(field1 field2 field3)
```

**Examples:**

```lcql
GROUP BY(domain)
GROUP BY(path hash)
GROUP BY(username logontype)
```

### Combining Aggregation and Grouping

```lcql
event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)
event/FILE_PATH as path event/HASH as hash COUNT_UNIQUE(hash) as count GROUP BY(path hash)
routing/hostname as host COUNT(event) as total GROUP BY(host)
```

### Sorting

Order results by a field.

```lcql
ORDER BY(field)
ORDER BY(field) DESC
```

**Examples:**

```lcql
ORDER BY(count)
ORDER BY(count) DESC
ORDER BY(domain)
```

### Complete Projection Examples

```lcql
event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain) ORDER BY(count) DESC
event/FILE_PATH as path event/HASH as hash routing/hostname as host
COUNT_UNIQUE(routing/sid) as unique_sensors
event/COMMAND_LINE as cli event/FILE_PATH as exe routing/hostname as host
```

## Complete Query Examples

### Example 1: PowerShell Execution

Find all PowerShell execution on Windows in the last 24 hours.

```lcql
-24h | plat == windows | NEW_PROCESS EXISTING_PROCESS | event/COMMAND_LINE contains "powershell" | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

**Breakdown:**
- `-24h` - Last 24 hours
- `plat == windows` - Windows only
- `NEW_PROCESS EXISTING_PROCESS` - Both new and existing processes
- `event/COMMAND_LINE contains "powershell"` - Command line contains powershell
- `event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host` - Display path, command line, and hostname

### Example 2: Domain Resolution Count

Count DNS queries to domains containing "google" in the last 10 minutes.

```lcql
-10m | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "google" | event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)
```

**Breakdown:**
- `-10m` - Last 10 minutes
- `plat == windows` - Windows only
- `DNS_REQUEST` - DNS events only
- `event/DOMAIN_NAME contains "google"` - Domains with "google"
- `event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)` - Count and group by domain

### Example 3: Unsigned Binaries

Find unsigned executables on Windows in the last 24 hours.

```lcql
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as path event/HASH as hash COUNT_UNIQUE(hash) as count GROUP BY(path hash)
```

**Breakdown:**
- `-24h` - Last 24 hours
- `plat == windows` - Windows only
- `CODE_IDENTITY` - Binary signature events
- `event/SIGNATURE/FILE_IS_SIGNED != 1` - Not signed (0 or missing)
- Projection groups by path and hash, counting unique hashes

### Example 4: Failed Logons

Show failed Windows logon attempts in the last hour.

```lcql
-1h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as srcip event/EVENT/EventData/LogonType as logontype event/EVENT/EventData/TargetUserName as username
```

**Breakdown:**
- `-1h` - Last hour
- `plat == windows` - Windows only
- `WEL` - Windows Event Logs
- `event/EVENT/System/EventID == "4625"` - Failed logon event ID
- Display source IP, logon type, and username

### Example 5: Process Tree Analysis

Find processes spawned by cmd.exe in the last 12 hours.

```lcql
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "cmd.exe" | event/PARENT/FILE_PATH as parent event/FILE_PATH as child COUNT(event) as count GROUP BY(parent child)
```

**Breakdown:**
- `-12h` - Last 12 hours
- `plat == windows` - Windows only
- `NEW_PROCESS` - Process creation
- `event/PARENT/FILE_PATH contains "cmd.exe"` - Parent is cmd.exe
- Group children by parent and child path, count occurrences

## Stream Types

LCQL can query different data streams. Specify the stream in the `run_lcql_query` tool call.

### Event Stream (default)

Telemetry from sensors and cloud adapters.

```
stream="event"
```

**Contains:**
- Process events (NEW_PROCESS, EXISTING_PROCESS)
- Network events (DNS_REQUEST, NETWORK_CONNECTIONS)
- File events (FILE_CREATE, FILE_DELETE)
- Windows Event Logs (WEL)
- Cloud adapter events (Azure, GCP, AWS, GitHub, etc.)

### Detection Stream

Detection events from D&R rules.

```
stream="detect"
```

**Contains:**
- Alerts triggered by D&R rules
- Rule match details
- Detection metadata

### Audit Stream

Platform audit logs for API and configuration changes.

```
stream="audit"
```

**Contains:**
- API calls
- Configuration changes
- User actions
- Rule modifications
- Sensor installations/removals

## Query Optimization Tips

### 1. Use Specific Timeframes

**Good:**
```lcql
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "cmd"
```

**Bad:**
```lcql
-90d | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "cmd"
```

Shorter timeframes = faster queries, lower costs.

### 2. Filter by Platform Early

**Good:**
```lcql
-24h | plat == windows | NEW_PROCESS | ...
```

**Bad:**
```lcql
-24h | * | NEW_PROCESS | routing/plat == 268435456 | ...
```

Use sensor selector instead of filters for platform.

### 3. Specify Event Types

**Good:**
```lcql
-24h | plat == windows | NEW_PROCESS DNS_REQUEST | ...
```

**Bad:**
```lcql
-24h | plat == windows | * | ...
```

Avoid `*` unless absolutely necessary.

### 4. Use Narrow Filters

**Good:**
```lcql
-1h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "c:\\temp\\malware.exe"
```

**Bad:**
```lcql
-30d | * | * | event/* contains "malware"
```

Specific filters reduce data churned.

## Common Errors and Solutions

### Error: Invalid field path

**Problem:** Field doesn't exist in event type.

**Solution:** Use `get_event_schema` to verify field names.

```
get_event_schema(name="evt:NEW_PROCESS")
```

### Error: Syntax error near '|'

**Problem:** Missing required query component.

**Solution:** Ensure all required parts are present: TIMEFRAME | SELECTOR | EVENT_TYPE | FILTER

### Error: Unknown event type

**Problem:** Event type doesn't exist or is misspelled.

**Solution:** Use `get_event_types_with_schemas_for_platform` to list available types.

```
get_event_types_with_schemas_for_platform(platform="windows")
```

### Error: Query timeout

**Problem:** Query is too broad or expensive.

**Solution:**
- Reduce timeframe
- Add more specific filters
- Specify event types instead of `*`
- Add a limit to the query

## Case Sensitivity

### String Operators

By default, string operations are **case-insensitive**:

```lcql
event/COMMAND_LINE contains "powershell"    Matches "PowerShell", "POWERSHELL", "powershell"
```

### Exact Matching

For case-sensitive matching, use `==`:

```lcql
event/COMMAND_LINE == "PowerShell.exe"      Exact match only
```

## Special Characters

### Escaping

When searching for special characters, enclose in quotes:

```lcql
event/COMMAND_LINE contains "c:\\windows\\system32"
event/DOMAIN_NAME contains ".exe.txt"
```

### Wildcards

LCQL does not support wildcards (`*` or `?`). Use `contains`, `starts with`, or `ends with` instead.

**Instead of:**
```
event/FILE_PATH == "c:\\temp\\*.exe"        NOT SUPPORTED
```

**Use:**
```lcql
event/FILE_PATH starts with "c:\\temp\\" and event/FILE_PATH ends with ".exe"
```

## Field Type Reference

### String Fields

Most fields are strings. Use string operators.

```lcql
event/COMMAND_LINE contains "value"
event/FILE_PATH starts with "c:\\"
routing/hostname == "server-01"
```

### Integer Fields

Numeric fields use numeric operators.

```lcql
event/PROCESS_ID > 1000
event/SIGNATURE/FILE_IS_SIGNED == 1
routing/event_time >= 1234567890000
```

### Boolean Fields

Use `== 1` for true, `== 0` or `!= 1` for false.

```lcql
event/SIGNATURE/FILE_IS_SIGNED == 1         Signed
event/SIGNATURE/FILE_IS_SIGNED != 1         Not signed
```

### Array Fields

Check for presence using `contains` or `==`.

```lcql
routing/tags contains "production"
```

## Advanced Patterns

### Time-Based Correlation

Use `routing/event_time` for temporal analysis:

```lcql
-24h | plat == windows | NEW_PROCESS | routing/event_time >= 1640000000000 and routing/event_time <= 1640086400000
```

### Process Correlation

Use `routing/this`, `routing/parent`, and `routing/target` for process tracking:

```lcql
-24h | plat == windows | * | routing/this == "a443f9c48bef700740ef27e062c333c6"
```

### Multi-Condition Filters

Complex boolean logic:

```lcql
-24h | plat == windows | NEW_PROCESS | (event/COMMAND_LINE contains "powershell" and event/COMMAND_LINE contains "-enc") or (event/COMMAND_LINE contains "cmd" and event/COMMAND_LINE contains "/c")
```

### Prevalence Analysis

Find rare occurrences:

```lcql
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH as path COUNT_UNIQUE(routing/sid) as hosts GROUP BY(path) ORDER BY(hosts)
```

This finds processes seen on the fewest number of hosts (potential outliers).
