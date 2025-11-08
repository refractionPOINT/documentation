# Event Types Reference

Comprehensive guide to LimaCharlie event types, their fields, and usage patterns.

## Table of Contents

- [Event Structure Overview](#event-structure-overview)
- [Platform-Specific Events](#platform-specific-events)
  - [Windows Events](#windows-events)
  - [Linux Events](#linux-events)
  - [macOS Events](#macos-events)
  - [Chrome Events](#chrome-events)
- [Cross-Platform Events](#cross-platform-events)
- [Windows Event Logs (WEL)](#windows-event-logs-wel)
- [Cloud Adapter Events](#cloud-adapter-events)
- [Discovering Event Types](#discovering-event-types)

---

## Event Structure Overview

Every LimaCharlie event has two top-level objects:

```json
{
  "routing": { /* metadata - consistent across all events */ },
  "event": { /* event-specific data - varies by type */ }
}
```

### Routing Object (Metadata)

Consistent across **all** event types:

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `routing/oid` | UUID | Organization ID | `8cbe27f4-...` |
| `routing/sid` | UUID | Sensor ID (unique endpoint) | `bb4b30af-...` |
| `routing/event_type` | string | Event type | `NEW_PROCESS` |
| `routing/event_time` | integer | Unix timestamp (milliseconds) | `1656959942437` |
| `routing/event_id` | UUID | Unique event ID | `8cec565d-...` |
| `routing/hostname` | string | Endpoint hostname | `server-01` |
| `routing/iid` | UUID | Installation Key ID | `7d23bee6-...` |
| `routing/did` | UUID | Device ID | `b97e9d00-...` |
| `routing/ext_ip` | string | External IP address | `35.1.1.1` |
| `routing/int_ip` | string | Internal IP address | `10.1.1.1` |
| `routing/plat` | integer | Platform identifier | `268435456` (Windows) |
| `routing/arch` | integer | Architecture | `2` (x64) |
| `routing/moduleid` | integer | Sensor module ID | `2` |
| `routing/tags` | array | Sensor tags | `["production", "edr"]` |
| `routing/this` | hash | Current process hash | `a443f9c4...` |
| `routing/parent` | hash | Parent process hash | `42217cb0...` |
| `routing/target` | hash | Target object hash | `6f8a3d21...` |

### Event Object (Event-Specific Data)

Varies by event type. Contains fields specific to the event.

---

## Platform-Specific Events

### Windows Events

#### NEW_PROCESS

Process creation/execution events.

**Common Fields:**
- `event/FILE_PATH` - Executable path
- `event/COMMAND_LINE` - Process command line
- `event/PROCESS_ID` - Process ID (PID)
- `event/PARENT` - Full parent process information
- `event/PARENT/FILE_PATH` - Parent executable path
- `event/PARENT/COMMAND_LINE` - Parent command line
- `event/USER` - Username
- `event/DOMAIN` - User domain

**Example Query:**
```lcql
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH contains "powershell" | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

**Use Cases:**
- Process execution monitoring
- Malware detection
- Process tree analysis
- User activity tracking

---

#### EXISTING_PROCESS

Running process snapshots (periodic process enumeration).

**Common Fields:**
- `event/FILE_PATH` - Executable path
- `event/COMMAND_LINE` - Process command line
- `event/PROCESS_ID` - Process ID
- `event/PARENT_PROCESS_ID` - Parent PID
- `event/MEMORY_USAGE` - Memory consumption
- `event/THREADS` - Thread count

**Example Query:**
```lcql
-1h | plat == windows | EXISTING_PROCESS | event/FILE_PATH as process COUNT_UNIQUE(routing/sid) as hosts GROUP BY(process)
```

**Use Cases:**
- Software inventory
- Long-running process detection
- Resource usage analysis

---

#### DNS_REQUEST

DNS query events.

**Common Fields:**
- `event/DOMAIN_NAME` - Queried domain
- `event/IP_ADDRESS` - Resolved IP
- `event/DNS_TYPE` - DNS record type
- `event/DNS_FLAGS` - DNS flags
- `event/CNAME` - CNAME if present
- `event/PROCESS_ID` - Requesting process ID
- `event/MESSAGE_ID` - DNS message ID

**Example Query:**
```lcql
-10m | plat == windows | DNS_REQUEST | event/DOMAIN_NAME contains "google" | event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)
```

**Use Cases:**
- C2 detection
- DNS tunneling detection
- Domain reputation checks
- Network behavior analysis

---

#### NETWORK_CONNECTIONS

Network connection events.

**Common Fields:**
- `event/NETWORK_ACTIVITY` - Array of connection objects
- `event/IP_ADDRESS` - Remote IP
- `event/PORT` - Remote port
- `event/PROTOCOL` - Protocol (TCP/UDP)
- `event/PROCESS_ID` - Process making connection
- `event/STATE` - Connection state

**Example Query:**
```lcql
-24h | plat == windows | NETWORK_CONNECTIONS | event/IP_ADDRESS == "1.2.3.4" | event/PORT as port routing/hostname as host
```

**Use Cases:**
- C2 detection
- Lateral movement detection
- Network traffic analysis
- Beaconing detection

---

#### CODE_IDENTITY

Binary signature and metadata events.

**Common Fields:**
- `event/FILE_PATH` - Binary path
- `event/HASH` - File hash (SHA-256)
- `event/SIGNATURE/FILE_IS_SIGNED` - 1 if signed, 0 if not
- `event/SIGNATURE/CERT_ISSUER` - Certificate issuer
- `event/SIGNATURE/CERT_CHAIN_STATUS` - Cert validation status
- `event/ORIGINAL_FILE_NAME` - Original filename
- `event/FILE_DESCRIPTION` - File description
- `event/COMPANY_NAME` - Company name

**Example Query:**
```lcql
-24h | plat == windows | CODE_IDENTITY | event/SIGNATURE/FILE_IS_SIGNED != 1 | event/FILE_PATH as path event/HASH as hash COUNT_UNIQUE(hash) as count GROUP BY(path hash)
```

**Use Cases:**
- Unsigned binary detection
- Software inventory
- Malware identification
- Certificate validation

---

#### MODULE_LOAD

DLL/module loading events.

**Common Fields:**
- `event/FILE_PATH` - Module path
- `event/HASH` - Module hash
- `event/BASE_ADDRESS` - Load address
- `event/MEMORY_SIZE` - Module size

**Example Query:**
```lcql
-12h | plat == windows | MODULE_LOAD | event/FILE_PATH contains "injected" | event/FILE_PATH as module routing/hostname as host
```

**Use Cases:**
- DLL injection detection
- Module tampering detection
- Software behavior analysis

---

#### FILE_CREATE

File creation events.

**Common Fields:**
- `event/FILE_PATH` - Created file path
- `event/PROCESS_ID` - Creating process ID
- `event/HASH` - File hash (if available)

**Example Query:**
```lcql
-6h | plat == windows | FILE_CREATE | event/FILE_PATH contains "\\temp\\" | event/FILE_PATH as path routing/hostname as host
```

**Use Cases:**
- Malware dropper detection
- Ransomware detection
- File system monitoring

---

#### FILE_DELETE

File deletion events.

**Common Fields:**
- `event/FILE_PATH` - Deleted file path
- `event/PROCESS_ID` - Deleting process ID

**Example Query:**
```lcql
-24h | plat == windows | FILE_DELETE | event/FILE_PATH as deleted_file routing/hostname as host routing/event_time as time
```

**Use Cases:**
- Evidence destruction detection
- Ransomware detection
- Data loss prevention

---

#### REGISTRY_CREATE / REGISTRY_WRITE

Registry modification events.

**Common Fields:**
- `event/REGISTRY_PATH` - Registry key path
- `event/VALUE_NAME` - Value name
- `event/VALUE_DATA` - Value data
- `event/VALUE_TYPE` - Value type
- `event/PROCESS_ID` - Modifying process ID

**Example Query:**
```lcql
-3h | plat == windows | REGISTRY_CREATE REGISTRY_WRITE | event/REGISTRY_PATH contains "\\Run" | event/REGISTRY_PATH as path event/VALUE_NAME as name routing/hostname as host
```

**Use Cases:**
- Persistence detection
- Configuration change monitoring
- Malware behavior analysis

---

#### USER_OBSERVED

User activity observation events.

**Common Fields:**
- `event/USER_NAME` - Username
- `event/DOMAIN` - User domain

**Example Query:**
```lcql
-24h | plat == windows | USER_OBSERVED | event/USER_NAME as user COUNT_UNIQUE(routing/sid) as hosts GROUP BY(user)
```

**Use Cases:**
- User activity tracking
- Lateral movement detection

---

### Linux Events

#### NEW_PROCESS (Linux)

Process execution on Linux.

**Common Fields:**
- `event/FILE_PATH` - Executable path
- `event/COMMAND_LINE` - Command line
- `event/PROCESS_ID` - PID
- `event/PARENT` - Parent process info
- `event/USER_ID` - UID
- `event/USER_NAME` - Username

**Example Query:**
```lcql
-24h | plat == linux | NEW_PROCESS | event/COMMAND_LINE contains "bash" | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

**Use Cases:**
- Command execution monitoring
- Privilege escalation detection
- Suspicious script execution

---

#### DNS_REQUEST (Linux)

DNS queries on Linux.

**Common Fields:**
(Same as Windows DNS_REQUEST)

**Example Query:**
```lcql
-1h | plat == linux | DNS_REQUEST | event/DOMAIN_NAME as domain COUNT(event) as count GROUP BY(domain)
```

---

#### NETWORK_CONNECTIONS (Linux)

Network connections on Linux.

**Common Fields:**
(Similar to Windows NETWORK_CONNECTIONS)

**Example Query:**
```lcql
-24h | plat == linux | NETWORK_CONNECTIONS | event/PORT == 22 | event/IP_ADDRESS as remote_ip routing/hostname as host
```

**Use Cases:**
- SSH connection monitoring
- C2 detection
- Network behavior analysis

---

### macOS Events

#### NEW_PROCESS (macOS)

Process execution on macOS.

**Common Fields:**
(Similar to Windows/Linux NEW_PROCESS)

**Example Query:**
```lcql
-24h | plat == macos | NEW_PROCESS | event/FILE_PATH contains ".app" | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

---

#### DNS_REQUEST (macOS)

DNS queries on macOS.

**Common Fields:**
(Same as Windows/Linux DNS_REQUEST)

---

### Chrome Events

#### CHROME_EXTENSION

Chrome extension activity.

**Common Fields:**
- `event/EXTENSION_ID` - Extension ID
- `event/EXTENSION_NAME` - Extension name
- `event/VERSION` - Extension version
- `event/ENABLED` - Enabled status

**Example Query:**
```lcql
-7d | plat == chrome | CHROME_EXTENSION | event/EXTENSION_NAME as extension COUNT_UNIQUE(routing/sid) as users GROUP BY(extension)
```

**Use Cases:**
- Extension inventory
- Malicious extension detection

---

## Cross-Platform Events

Some event types are available across multiple platforms.

### DNS_REQUEST

Available on: Windows, Linux, macOS

**Fields:** (See platform-specific sections above)

---

### NETWORK_CONNECTIONS

Available on: Windows, Linux, macOS

**Fields:** (See platform-specific sections above)

---

### NEW_PROCESS

Available on: Windows, Linux, macOS

**Fields:** (See platform-specific sections above)

---

## Windows Event Logs (WEL)

Windows Event Logs ingested as telemetry.

### Event Structure

WEL events have a nested structure:

```
event/EVENT/System/...        System information
event/EVENT/EventData/...     Event-specific data
```

### Common Event IDs

#### Security Events

| Event ID | Description | Use Case |
|----------|-------------|----------|
| 4624 | Successful logon | Logon monitoring |
| 4625 | Failed logon | Brute-force detection |
| 4672 | Special privileges assigned | Privilege escalation |
| 4688 | Process creation | Process monitoring |
| 4698 | Scheduled task created | Persistence detection |
| 4740 | Account lockout | Brute-force detection |
| 4768 | Kerberos TGT requested | Authentication monitoring |
| 4769 | Kerberos service ticket | Service access monitoring |

#### System Events

| Event ID | Description | Use Case |
|----------|-------------|----------|
| 7045 | Service installed | Persistence detection |
| 7036 | Service state change | Service monitoring |

### WEL Query Patterns

#### Event ID Filter

```lcql
event/EVENT/System/EventID == "4624"
```

#### EventData Filter

```lcql
event/EVENT/EventData/LogonType == "10"
event/EVENT/EventData/TargetUserName == "admin"
event/EVENT/EventData/IpAddress == "1.2.3.4"
```

### Example Queries

#### Failed Logons

```lcql
-1h | plat == windows | WEL | event/EVENT/System/EventID == "4625" | event/EVENT/EventData/IpAddress as srcip event/EVENT/EventData/TargetUserName as username
```

#### Service Installation

```lcql
-24h | plat == windows | WEL | event/EVENT/System/EventID == "7045" | event/EVENT/EventData/ServiceName as service event/EVENT/EventData/ImagePath as path routing/hostname as host
```

#### RDP Logons

```lcql
-7d | plat == windows | WEL | event/EVENT/System/EventID == "4624" and event/EVENT/EventData/LogonType == "10" | event/EVENT/EventData/TargetUserName as user routing/hostname as host
```

---

## Cloud Adapter Events

### GitHub Events

#### protected_branch.policy_override

Branch protection bypass events.

**Common Fields:**
- `event/repo` - Repository name
- `event/actor` - User who performed action
- `event/public_repo` - Public/private status
- `event/actor_location/country_code` - Actor location

**Example Query:**
```lcql
-12h | plat == github | protected_branch.policy_override | event/repo as repo event/actor as actor COUNT(event) as count GROUP BY(repo actor)
```

---

### Azure Events

Azure cloud telemetry via adapters.

**Event Types:**
- `azure-activitylog` - Azure Activity Log events
- `azure-signinlogs` - Sign-in events
- `azure-auditlogs` - Audit log events

**Example Query:**
```lcql
-24h | plat == azure | azure-signinlogs | event/* as data routing/event_type as type
```

---

### GCP Events

Google Cloud Platform telemetry.

**Event Types:**
- `gcp-auditlog` - GCP Audit logs
- `gcp-cloudaudit` - Cloud Audit logs

**Example Query:**
```lcql
-24h | plat == gcp | gcp-auditlog | event/* as data routing/event_type as type
```

---

### AWS Events

Amazon Web Services telemetry.

**Event Types:**
- `aws-cloudtrail` - CloudTrail events

**Example Query:**
```lcql
-24h | plat == aws | aws-cloudtrail | event/* as data routing/event_type as type
```

---

### Microsoft Defender Advanced Hunting

Microsoft Defender telemetry ingested via adapter.

**Event Types:**
- `AdvancedHunting-DeviceEvents`
- `AdvancedHunting-DeviceProcessEvents`
- `AdvancedHunting-DeviceNetworkEvents`
- `AdvancedHunting-DeviceFileEvents`

**Example Query:**
```lcql
-24h | plat == windows | AdvancedHunting-DeviceProcessEvents | event/* as data routing/hostname as host
```

---

## Discovering Event Types

### Using MCP Tools

#### List All Platforms

```
get_platform_names()
```

**Returns:** Available platform names (windows, linux, macos, github, azure, etc.)

---

#### Get Event Types for Platform

```
get_event_types_with_schemas_for_platform(platform="windows")
```

**Returns:** All event types available for Windows platform.

**Example Response:**
```json
{
  "event_types": [
    "evt:NEW_PROCESS",
    "evt:EXISTING_PROCESS",
    "evt:DNS_REQUEST",
    "evt:NETWORK_CONNECTIONS",
    "evt:CODE_IDENTITY",
    "evt:WEL",
    ...
  ],
  "count": 45
}
```

---

#### Get Schema for Event Type

```
get_event_schema(name="evt:NEW_PROCESS")
```

**Returns:** Field definitions and types for the event.

**Example Response:**
```json
{
  "schema": {
    "event_type": "evt:NEW_PROCESS",
    "elements": [
      "s:event/FILE_PATH",
      "s:event/COMMAND_LINE",
      "i:event/PROCESS_ID",
      "s:routing/hostname",
      "i:routing/event_time",
      ...
    ]
  }
}
```

**Field Prefixes:**
- `s:` - String
- `i:` - Integer
- `b:` - Boolean

---

#### List All Event Types

```
get_event_types_with_schemas()
```

**Returns:** All event types across all platforms.

---

## Schema Discovery Workflow

When working with unfamiliar event types:

**Step 1:** List available platforms
```
get_platform_names()
```

**Step 2:** Get event types for your platform
```
get_event_types_with_schemas_for_platform(platform="windows")
```

**Step 3:** Get schema for specific event type
```
get_event_schema(name="evt:NEW_PROCESS")
```

**Step 4:** Build query using discovered fields
```lcql
-24h | plat == windows | NEW_PROCESS | event/FILE_PATH as path event/COMMAND_LINE as cli routing/hostname as host
```

---

## Event Type Selection Guide

### Choose Event Type Based On:

**Process Activity:**
- `NEW_PROCESS` - Process starts
- `EXISTING_PROCESS` - Running processes
- `TERMINATE_PROCESS` - Process exits

**Network Activity:**
- `DNS_REQUEST` - DNS queries
- `NETWORK_CONNECTIONS` - TCP/UDP connections
- `NEW_TCP4_CONNECTION` - IPv4 TCP connections

**File Activity:**
- `FILE_CREATE` - File creation
- `FILE_DELETE` - File deletion
- `FILE_MODIFIED` - File changes

**Binary/Code:**
- `CODE_IDENTITY` - Binary signatures
- `MODULE_LOAD` - DLL/library loading

**Windows Specifics:**
- `WEL` - Windows Event Logs
- `REGISTRY_CREATE` / `REGISTRY_WRITE` - Registry changes
- `USER_OBSERVED` - User activity

**Cloud:**
- `github-*` - GitHub events
- `azure-*` - Azure events
- `gcp-*` - GCP events
- `AdvancedHunting-*` - Microsoft Defender events

---

## Best Practices

### 1. Use Specific Event Types

**Good:**
```lcql
-24h | plat == windows | NEW_PROCESS DNS_REQUEST | ...
```

**Bad:**
```lcql
-24h | plat == windows | * | ...
```

### 2. Understand Field Availability

Not all fields are present in all events. Use schema discovery to verify.

### 3. Combine Related Event Types

```lcql
NEW_PROCESS EXISTING_PROCESS           Process activity
FILE_CREATE FILE_DELETE FILE_MODIFIED  File operations
REGISTRY_CREATE REGISTRY_WRITE         Registry changes
```

### 4. Use Routing Fields for Correlation

```lcql
routing/this       Current process hash
routing/parent     Parent process hash
routing/target     Target object hash
routing/sid        Sensor ID (endpoint)
```

These enable cross-event correlation.

### 5. Platform-Specific Filtering

Use appropriate event types for each platform:

```lcql
-24h | plat == windows | WEL | ...          Windows Event Logs (Windows only)
-24h | plat == github | protected_branch... GitHub events (GitHub only)
-24h | plat == linux | NEW_PROCESS | ...    Linux processes
```

---

## Common Mistakes

### 1. Using Wrong Event Type Prefix in Schema Calls

**Wrong:**
```
get_event_schema(name="NEW_PROCESS")
```

**Correct:**
```
get_event_schema(name="evt:NEW_PROCESS")
```

Schema calls require the `evt:` prefix.

### 2. Assuming All Platforms Have All Events

Not all event types are available on all platforms. Use discovery tools.

### 3. Querying Nonexistent Fields

Always verify fields exist using `get_event_schema` before querying.

### 4. Using `*` for Event Type

Avoid `*` unless necessary - it's expensive and slow.

**Better:**
```lcql
-24h | plat == windows | NEW_PROCESS DNS_REQUEST NETWORK_CONNECTIONS | ...
```

---

## Summary

- **Routing fields** are consistent across all events
- **Event fields** vary by event type
- Use **schema discovery tools** to understand available fields
- Choose **specific event types** to optimize query performance
- **Platform-specific events** like WEL and cloud events have unique structures
- Always **verify field availability** before building complex queries
