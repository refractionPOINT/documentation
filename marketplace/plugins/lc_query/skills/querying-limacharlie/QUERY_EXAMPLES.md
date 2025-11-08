# LCQL Query Examples

Practical LCQL query examples organized by use case. All examples can be executed using `run_lcql_query(query="...", stream="event")`.

## Table of Contents

- [Threat Hunting](#threat-hunting)
- [Incident Investigation](#incident-investigation)
- [Compliance & Reporting](#compliance--reporting)
- [Network Analysis](#network-analysis)
- [Process Analysis](#process-analysis)
- [File Operations](#file-operations)
- [Windows Event Logs](#windows-event-logs)
- [Cloud Telemetry](#cloud-telemetry)
- [Detection Analysis](#detection-analysis)

---

## Threat Hunting

### Suspicious PowerShell Execution

Find PowerShell with encoded commands (common malware technique).

```lcql
-24h | plat == windows | NEW_PROCESS EXISTING_PROCESS | event/COMMAND_LINE contains "-encodedcommand" or event/COMMAND_LINE contains "-enc" or event/COMMAND_LINE contains "downloadstring" | event/COMMAND_LINE as command event/FILE_PATH as path routing/hostname as host
```

**Use case:** Detect obfuscated PowerShell commonly used in malware delivery.

### Unsigned Executables

Find unsigned binaries running on Windows endpoints.

```lcql
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 and event/FILE_PATH not contains "windows" | event/FILE_PATH as path event/HASH as hash COUNT_UNIQUE(hash) as count GROUP BY(path hash)
```

**Use case:** Identify potentially malicious unsigned executables (excluding Windows system files).

### Unusual Parent-Child Process Relationships

Detect Office applications spawning suspicious processes.

```lcql
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH contains "winword.exe" or event/PARENT/FILE_PATH contains "excel.exe" or event/PARENT/FILE_PATH contains "powerpnt.exe" | event/PARENT/FILE_PATH as parent event/FILE_PATH as child event/COMMAND_LINE as command routing/hostname as host
```

**Use case:** Detect macro-based malware or document exploits.

### PsExec Execution

Find PsExec usage across the environment.

```lcql
-24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "psexec" or event/FILE_PATH contains "psexec" | event/FILE_PATH as path event/COMMAND_LINE as command routing/hostname as host routing/ext_ip as ip
```

**Use case:** Detect lateral movement attempts using PsExec.

### Temp Directory Execution

Find executables running from temp directories.

```lcql
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "\\temp\\" or event/FILE_PATH contains "\\tmp\\" or event/FILE_PATH contains "appdata\\local\\temp" | event/FILE_PATH as path event/COMMAND_LINE as command routing/hostname as host
```

**Use case:** Detect malware commonly executed from temporary directories.

### Credential Dumping Tools

Search for known credential dumping tools.

```lcql
-7d | plat == windows | NEW_PROCESS EXISTING_PROCESS | event/FILE_PATH contains "mimikatz" or event/COMMAND_LINE contains "procdump" or event/COMMAND_LINE contains "lsass" | event/FILE_PATH as path event/COMMAND_LINE as command routing/hostname as host
```

**Use case:** Detect credential theft attempts.

### Suspicious Service Creation

Find services with suspicious paths or names.

```lcql
-12h | plat == windows | WEL | event/EVENT/System/EventID == "7045" and (event/EVENT/EventData/ImagePath contains "COMSPEC" or event/EVENT/EventData/ImagePath contains "powershell" or event/EVENT/EventData/ImagePath contains "cmd.exe") | event/EVENT/EventData/ServiceName as service event/EVENT/EventData/ImagePath as path routing/hostname as host
```

**Use case:** Detect persistence mechanisms via malicious services.

### Rare Process Execution (Prevalence Analysis)

Find processes seen on the fewest hosts (potential outliers).

```lcql
-7d | plat == windows | NEW_PROCESS | event/FILE_PATH as path COUNT_UNIQUE(routing/sid) as unique_hosts COUNT(event) as total_executions GROUP BY(path) ORDER BY(unique_hosts)
```

**Use case:** Identify rare or unique processes that may be malicious.

### Living Off The Land Binaries (LOLBins)

Find potentially abused Windows utilities.

```lcql
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "certutil" or event/FILE_PATH contains "bitsadmin" or event/FILE_PATH contains "mshta" or event/FILE_PATH contains "regsvr32" | event/FILE_PATH as binary event/COMMAND_LINE as command routing/hostname as host
```

**Use case:** Detect abuse of legitimate Windows binaries for malicious purposes.

---

## Incident Investigation

### Host Activity Timeline

Get all events from a specific host in chronological order.

```lcql
-24h | routing/hostname == "compromised-host" | * | routing/event_time as time routing/event_type as type event/* as data
```

**Use case:** Build a timeline of activity on a potentially compromised host.

### Specific Sensor Activity

Query all activity from a specific sensor ID.

```lcql
-24h | routing/sid == "bb4b30af-1234-5678-90ab-f014ada33345" | * | routing/event_time as time routing/event_type as type
```

**Use case:** Investigate activity from a specific endpoint.

### Network Connections from Process

Find network connections made by a specific process.

```lcql
-6h | plat == windows | NETWORK_CONNECTIONS | event/PROCESS_ID == 1234 | event/IP_ADDRESS as remote_ip event/PORT as port routing/hostname as host
```

**Use case:** Investigate network communications from a suspicious process.

### File Operations During Timeframe

View all file activity within a specific timeframe.

```lcql
-2h | plat == windows | FILE_CREATE FILE_DELETE FILE_MODIFIED | event/FILE_PATH as path routing/event_type as operation routing/hostname as host routing/event_time as time
```

**Use case:** Investigate file system changes during incident window.

### User Logon History

Track logon activity for a specific user.

```lcql
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/TargetUserName == "john.doe" | event/EVENT/EventData/LogonType as type event/EVENT/EventData/IpAddress as srcip routing/hostname as host routing/event_time as time
```

**Use case:** Investigate user account activity during incident.

### Process Execution by Hash

Find all executions of a specific binary hash.

```lcql
-30d | plat == windows | NEW_PROCESS CODE_IDENTITY | event/HASH == "a1b2c3d4e5f6..." | event/FILE_PATH as path event/COMMAND_LINE as command routing/hostname as host routing/event_time as time
```

**Use case:** Track execution of known malicious binaries.

### Parent Process Investigation

Find all child processes spawned by a specific parent.

```lcql
-12h | plat == windows | NEW_PROCESS | routing/parent == "a443f9c48bef700740ef27e062c333c6" | event/FILE_PATH as child event/COMMAND_LINE as command routing/hostname as host
```

**Use case:** Investigate process tree for suspicious parent process.

### Registry Modifications

Find registry changes during incident timeframe.

```lcql
-3h | plat == windows | REGISTRY_CREATE REGISTRY_WRITE | event/REGISTRY_PATH as path event/VALUE_NAME as value routing/hostname as host routing/event_time as time
```

**Use case:** Detect persistence mechanisms via registry modifications.

---

## Compliance & Reporting

### Logon Activity by Type

Count Windows logons by logon type.

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" | event/EVENT/EventData/LogonType as type event/EVENT/EventData/TargetUserName as user COUNT(event) as count GROUP BY(user type)
```

**Use case:** Compliance reporting for authentication activity.

### Failed Logon Summary

Track failed authentication attempts.

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as srcip event/EVENT/EventData/TargetUserName as user COUNT(event) as attempts GROUP BY(srcip user) ORDER BY(attempts) DESC
```

**Use case:** Detect brute-force attacks or account compromises.

### DNS Resolution Patterns

Analyze DNS query patterns and volume.

```lcql
-7d | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as unique_hosts COUNT(event) as total_queries GROUP BY(domain) ORDER BY(unique_hosts) DESC
```

**Use case:** Identify most queried domains and prevalence.

### Software Inventory

List unique processes executed across the environment.

```lcql
-30d | plat == windows | NEW_PROCESS | event/FILE_PATH as executable COUNT_UNIQUE(routing/sid) as deployed_hosts COUNT(event) as executions GROUP BY(executable) ORDER BY(deployed_hosts) DESC
```

**Use case:** Software inventory and deployment verification.

### Network Traffic Summary

Summarize outbound network connections.

```lcql
-24h | plat == windows | NETWORK_CONNECTIONS | event/IP_ADDRESS as remote_ip event/PORT as port COUNT(event) as connections COUNT_UNIQUE(routing/sid) as hosts GROUP BY(remote_ip port) ORDER BY(connections) DESC
```

**Use case:** Network traffic analysis for compliance.

### User Activity Report

Count user sessions by username.

```lcql
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4624" | event/EVENT/EventData/TargetUserName as username COUNT_UNIQUE(routing/sid) as hosts_accessed COUNT(event) as total_logons GROUP BY(username) ORDER BY(total_logons) DESC
```

**Use case:** User activity monitoring for compliance.

### Endpoint Agent Version Report

List sensor versions across the fleet.

```lcql
-1h | plat == windows | EXISTING_PROCESS | routing/sid as sensor_id routing/hostname as hostname COUNT(event) as sample_size
```

**Use case:** Verify agent deployment and versions. (Note: Combine with `get_sensor_info` for version details)

---

## Network Analysis

### DNS Queries to Domain

Find all DNS queries for a specific domain pattern.

```lcql
-24h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "suspicious-domain.com" | event/DOMAIN_NAME as domain event/IP_ADDRESS as resolved_ip routing/hostname as host routing/event_time as time
```

**Use case:** Track DNS queries to known malicious domains.

### Domain Count by Host

Count unique domains queried per host.

```lcql
-24h | plat == windows | DNS_REQUEST | routing/hostname as host COUNT_UNIQUE(event/DOMAIN_NAME) as unique_domains GROUP BY(host) ORDER BY(unique_domains) DESC
```

**Use case:** Identify hosts with unusual DNS activity (potential C2 beaconing).

### DNS Query Volume

Find domains with highest query volume.

```lcql
-1h | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT(event) as query_count GROUP BY(domain) ORDER BY(query_count) DESC
```

**Use case:** Identify DNS tunneling or beaconing activity.

### Connections to IP

Find all connections to a specific IP address.

```lcql
-7d | plat == windows | NETWORK_CONNECTIONS | event/IP_ADDRESS == "1.2.3.4" | event/PORT as port routing/hostname as host routing/event_time as time
```

**Use case:** Investigate connections to known malicious IPs.

### Outbound Connections by Port

Summarize network connections by destination port.

```lcql
-24h | plat == windows | NETWORK_CONNECTIONS | event/PORT as port COUNT(event) as connections COUNT_UNIQUE(event/IP_ADDRESS) as unique_ips GROUP BY(port) ORDER BY(connections) DESC
```

**Use case:** Identify unusual network protocols or ports.

### DNS Queries for Rare Domains

Find domains queried by only one or two hosts.

```lcql
-7d | plat == windows | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT_UNIQUE(routing/sid) as host_count GROUP BY(domain) ORDER BY(host_count)
```

**Use case:** Detect targeted C2 domains or unique threats.

---

## Process Analysis

### Process Command Line Search

Search for specific command line patterns.

```lcql
-24h | plat == windows | NEW_PROCESS EXISTING_PROCESS | event/COMMAND_LINE contains "target-string" | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

**Use case:** Find processes with specific arguments or commands.

### Process Tree - Children by Parent

Group child processes by parent executable.

```lcql
-12h | plat == windows | NEW_PROCESS | event/PARENT/FILE_PATH as parent event/FILE_PATH as child COUNT(event) as count GROUP BY(parent child) ORDER BY(count) DESC
```

**Use case:** Analyze common process parent-child relationships.

### Process Count by Executable

Count executions of each unique executable.

```lcql
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH as executable COUNT(event) as executions COUNT_UNIQUE(routing/sid) as hosts GROUP BY(executable) ORDER BY(executions) DESC
```

**Use case:** Identify most commonly executed processes.

### Long-Running Processes

Find processes running across the entire query timeframe (using EXISTING_PROCESS).

```lcql
-24h | plat == windows | EXISTING_PROCESS | event/FILE_PATH as process COUNT_UNIQUE(routing/sid) as hosts GROUP BY(process) ORDER BY(hosts) DESC
```

**Use case:** Identify persistent processes across the environment.

### Process Spawned from Specific Path

Find processes executed from unusual locations.

```lcql
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH starts with "c:\\users\\" and event/FILE_PATH ends with ".exe" | event/FILE_PATH as path event/COMMAND_LINE as command routing/hostname as host
```

**Use case:** Detect execution from user directories (potential malware).

---

## File Operations

### File Created in Directory

Monitor file creation in specific directories.

```lcql
-6h | plat == windows | FILE_CREATE | event/FILE_PATH contains "c:\\windows\\temp" | event/FILE_PATH as path routing/hostname as host routing/event_time as time
```

**Use case:** Monitor sensitive directories for unauthorized file creation.

### File Deletion Events

Track file deletions (potential evidence destruction).

```lcql
-24h | plat == windows | FILE_DELETE | event/FILE_PATH as deleted_file routing/hostname as host routing/event_time as time
```

**Use case:** Detect evidence destruction or ransomware activity.

### File Operations by Extension

Find operations on specific file types.

```lcql
-24h | plat == windows | FILE_CREATE FILE_MODIFIED | event/FILE_PATH ends with ".exe" or event/FILE_PATH ends with ".dll" | event/FILE_PATH as path routing/event_type as operation routing/hostname as host
```

**Use case:** Monitor creation or modification of executable files.

### File Modification in System Directories

Detect modifications to system directories.

```lcql
-12h | plat == windows | FILE_MODIFIED | event/FILE_PATH starts with "c:\\windows\\system32" | event/FILE_PATH as path routing/hostname as host routing/event_time as time
```

**Use case:** Detect tampering with system files.

---

## Windows Event Logs

### Failed Logons by User

Track failed authentication attempts per user.

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as srcip COUNT(event) as failed_attempts GROUP BY(user srcip) ORDER BY(failed_attempts) DESC
```

**Use case:** Detect brute-force attacks on specific accounts.

### Successful Logons (Event ID 4624)

Track successful Windows logons.

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4624" | event/EVENT/EventData/LogonType as type event/EVENT/EventData/TargetUserName as user routing/hostname as host event/EVENT/EventData/IpAddress as srcip
```

**Use case:** Audit successful authentication events.

### RDP Logons (LogonType 10)

Find Remote Desktop Protocol logons.

```lcql
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "10" | event/EVENT/EventData/TargetUserName as user event/EVENT/EventData/IpAddress as srcip routing/hostname as host routing/event_time as time
```

**Use case:** Monitor RDP access to servers.

### Service Installation

Detect new service installations.

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "7045" | event/EVENT/EventData/ServiceName as service event/EVENT/EventData/ImagePath as path routing/hostname as host
```

**Use case:** Detect malware persistence via service installation.

### Overpass-the-Hash Detection

Detect Overpass-the-Hash authentication attacks.

```lcql
-12h | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "9" and event/EVENT/EventData/AuthenticationPackageName == "Negotiate" and event/EVENT/EventData/LogonProcess == "seclogo" | event/EVENT/EventData/TargetUserName as user routing/hostname as host
```

**Use case:** Detect Kerberos-based credential attacks.

### Account Lockout Events

Track account lockouts (Event ID 4740).

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4740" | event/EVENT/EventData/TargetUserName as user routing/hostname as host COUNT(event) as lockouts GROUP BY(user host)
```

**Use case:** Investigate account lockouts from brute-force attacks.

### Scheduled Task Creation

Monitor scheduled task creation for persistence.

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "4698" | event/EVENT/EventData/TaskName as task routing/hostname as host
```

**Use case:** Detect persistence mechanisms via scheduled tasks.

### Taskkill from Non-System Account

Detect taskkill execution from non-system accounts (potential defense evasion).

```lcql
-12h | plat == windows | WEL | event/EVENT/System/EventID == "4688" and event/EVENT/EventData/NewProcessName contains "taskkill" and event/EVENT/EventData/SubjectUserName not ends with "$" | event/EVENT/EventData/SubjectUserName as user event/EVENT/EventData/CommandLine as command routing/hostname as host
```

**Use case:** Detect attempts to kill security tools or processes.

---

## Cloud Telemetry

### GitHub Branch Protection Override

Detect GitHub branch protection bypasses.

```lcql
-12h | plat == github | protected_branch.policy_override | event/public_repo is false | event/repo as repo event/actor as actor event/actor_location/country_code as country COUNT(event) as count GROUP BY(repo actor country)
```

**Use case:** Detect unauthorized force pushes to protected branches.

### Azure Activity

Query Azure cloud telemetry.

```lcql
-24h | plat == azure | * | event/* as data routing/event_type as type
```

**Use case:** Investigate Azure cloud activity.

### GCP Events

Query Google Cloud Platform events.

```lcql
-24h | plat == gcp | * | event/* as data routing/event_type as type
```

**Use case:** Investigate GCP activity.

### Microsoft Defender Advanced Hunting

Query Microsoft Defender telemetry ingested via adapter.

```lcql
-24h | plat == windows | AdvancedHunting-DeviceEvents | event/* as data routing/hostname as host
```

**Use case:** Analyze Microsoft Defender telemetry.

---

## Detection Analysis

To query the **detection stream** (alerts from D&R rules), use `stream="detect"` in the tool call.

### All Detections in Timeframe

```lcql
-24h | * | * | routing/event_type as detection routing/hostname as host routing/event_time as time
```

**Tool call:**
```
run_lcql_query(query="...", stream="detect")
```

**Use case:** Review all alerts triggered in the last 24 hours.

### Detections by Category

Group detections by detection name/category.

```lcql
-7d | * | * | routing/event_type as detection COUNT(event) as count GROUP BY(detection) ORDER BY(count) DESC
```

**Tool call:**
```
run_lcql_query(query="...", stream="detect")
```

**Use case:** Identify most frequently triggered detections.

### Detections on Specific Host

```lcql
-24h | routing/hostname == "server-01" | * | routing/event_type as detection routing/event_time as time
```

**Tool call:**
```
run_lcql_query(query="...", stream="detect")
```

**Use case:** Investigate alerts on a specific host.

### High Severity Detections

Filter detections by severity (if included in detection metadata).

```lcql
-24h | * | * | event/severity == "high" | routing/event_type as detection routing/hostname as host routing/event_time as time
```

**Tool call:**
```
run_lcql_query(query="...", stream="detect")
```

**Use case:** Prioritize investigation of high-severity alerts.

---

## Combining Multiple Tools

### IOC Search Then Query Details

**Step 1:** Search for IOC
```
search_iocs(indicator="malicious.com", indicator_type="domain", days=7)
```

**Step 2:** If matches found, query for details
```lcql
-7d | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "malicious.com" | event/DOMAIN_NAME as domain routing/hostname as host routing/event_time as time
```

### Schema Discovery Then Query

**Step 1:** Discover event types
```
get_event_types_with_schemas_for_platform(platform="windows")
```

**Step 2:** Get schema
```
get_event_schema(name="evt:NEW_PROCESS")
```

**Step 3:** Build and execute query
```lcql
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

### Host Investigation Workflow

**Step 1:** Get host info
```
get_sensor_info(sid="bb4b30af-1234-5678-90ab-f014ada33345")
```

**Step 2:** Query host activity
```lcql
-24h | routing/sid == "bb4b30af-1234-5678-90ab-f014ada33345" | * | routing/event_type as type routing/event_time as time
```

**Step 3:** Focus on specific activity
```lcql
-24h | routing/sid == "bb4b30af-1234-5678-90ab-f014ada33345" | NEW_PROCESS | event/FILE_PATH as path event/COMMAND_LINE as cli
```

---

## Tips for Building Effective Queries

1. **Start simple, refine iteratively** - Begin with basic query, add filters progressively
2. **Use schema tools** - Verify event types and fields before building complex queries
3. **Leverage AI generation** - For complex requests, use `generate_lcql_query`
4. **Add limits for exploration** - Use `limit=100` when exploring data
5. **Group and aggregate** - Use `GROUP BY` and `COUNT` for summaries
6. **Sort results** - Use `ORDER BY` to prioritize findings
7. **Filter early** - Apply platform and event type filters to reduce query cost
8. **Test incrementally** - Run queries in small timeframes first, then expand

---

## Query Performance Guidelines

**Fast Queries:**
- Short timeframes (-1h, -24h)
- Specific platforms and event types
- Narrow filters
- Limited projections

**Slow Queries:**
- Long timeframes (-30d, -90d)
- `*` for platform or event type
- Broad filters or no filters
- Large aggregations

**Optimization:**
```
Bad:  -30d | * | * | event/* contains "malware"
Good: -24h | plat == windows | NEW_PROCESS | event/COMMAND_LINE contains "malware.exe"
```
