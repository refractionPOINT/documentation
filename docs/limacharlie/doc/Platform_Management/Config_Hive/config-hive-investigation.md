# Config Hive: Investigation

Investigations are records used during cybersecurity incident response to organize events, detections, and entities of interest. They enable analysts to track investigation progress, add annotations, and document findings throughout an incident.

## Format

Investigation records store references to events and detections (by ID), along with entities, notes, and investigation metadata. The maximum record size is 5MB.

### Root Fields

| Field | Type | Required | Max Length | Description |
|-------|------|----------|-----------|-------------|
| `name` | string | Yes | 256 | Human-readable investigation name |
| `description` | string | No | 4096 | Detailed description of the investigation |
| `status` | string | No | - | Investigation status (see enum below) |
| `priority` | string | No | - | Priority level (see enum below) |
| `events` | array | No | - | Event references with annotations |
| `detections` | array | No | - | Detection references with annotations |
| `entities` | array | No | - | Entities of interest (IOCs) |
| `notes` | array | No | - | Investigation notes and findings |
| `summary` | string | No | 16384 | Executive summary |
| `conclusion` | string | No | 16384 | Final investigation conclusion |

### Event Structure

Events reference telemetry by atom and sensor ID.

| Field | Type | Required | Max Length | Description |
|-------|------|----------|-----------|-------------|
| `atom` | string | Yes | - | LimaCharlie event atom identifier |
| `sid` | string | Yes | - | Sensor ID the event originated from |
| `tags` | array | No | - | Tags for categorizing the event |
| `comments` | array | No | - | Analyst comments (see Comment structure) |
| `relevance` | string | No | 1024 | Why this event matters to the investigation |
| `verdict` | string | No | - | Analyst verdict (see Verdict enum) |

### Detection Structure

Detections reference D&R detection records by ID.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `detection_id` | string | Yes | Detection identifier |
| `tags` | array | No | Tags for categorizing the detection |
| `comments` | array | No | Analyst comments (see Comment structure) |
| `false_positive` | object | No | False positive determination (see below) |

**False Positive Object:**

| Field | Type | Description |
|-------|------|-------------|
| `is_fp` | boolean | Whether marked as false positive |
| `reason` | string | Reason for FP determination (max 1024) |
| `determined_by` | string | User who made determination (max 256) |
| `determined_at` | int64 | Timestamp when determined (Unix epoch ms) |

### Entity Structure

Entities represent IOCs and other items of interest.

| Field | Type | Required | Max Length | Description |
|-------|------|----------|-----------|-------------|
| `type` | string | Yes | - | Entity type (see enum below) |
| `value` | string | Yes | 2048 | Entity value |
| `name` | string | No | 256 | Human-readable name/alias |
| `first_seen` | int64 | No | - | First observation timestamp (Unix epoch ms) |
| `last_seen` | int64 | No | - | Last observation timestamp (Unix epoch ms) |
| `context` | string | No | 2048 | Why this entity is of interest |
| `verdict` | string | No | - | Analyst verdict (see Verdict enum) |
| `related_events` | array | No | - | Event atoms this entity relates to |
| `related_detections` | array | No | - | Detection IDs this entity relates to |
| `comments` | array | No | - | Analyst comments (see Comment structure) |

### Note Structure

Notes document observations, findings, and action items.

| Field | Type | Required | Max Length | Description |
|-------|------|----------|-----------|-------------|
| `id` | string | No | 64 | Unique identifier for the note |
| `type` | string | No | - | Note type (see enum below) |
| `content` | string | Yes | 16384 | Note content |
| `author` | string | No | 256 | User who created the note |
| `timestamp` | int64 | No | - | Creation timestamp (Unix epoch ms) |
| `related_events` | array | No | - | Event atoms this note refers to |
| `related_detections` | array | No | - | Detection IDs this note refers to |
| `resolved` | boolean | No | - | For action_items/questions: whether resolved |

### Comment Structure

Comments can be added to events, detections, and entities.

| Field | Type | Required | Max Length | Description |
|-------|------|----------|-----------|-------------|
| `content` | string | Yes | 4096 | Comment text |
| `author` | string | No | 256 | User who wrote the comment |
| `timestamp` | int64 | No | - | When written (Unix epoch ms) |

### Enum Values

**Status:**
`new`, `in_progress`, `pending_review`, `escalated`, `closed_false_positive`, `closed_true_positive`

**Priority:**
`critical`, `high`, `medium`, `low`, `informational`

**Verdict:**
`unknown`, `benign`, `suspicious`, `malicious`

**Entity Type:**
`ip`, `domain`, `hash`, `user`, `host`, `email`, `file_path`, `process`, `url`, `other`

**Note Type:**
`observation`, `hypothesis`, `finding`, `conclusion`, `action_item`, `question`

## Permissions

The investigation hive requires the following permissions:

* `investigation.get` - Read investigation records
* `investigation.set` - Create/update investigation records
* `investigation.del` - Delete investigation records
* `investigation.get.mtd` - Read investigation metadata
* `investigation.set.mtd` - Modify investigation metadata

## Command-Line Usage

```bash
# Create an investigation from a JSON file
limacharlie hive set investigation --key investigation-2024-001 --data investigation.json

# Get an investigation
limacharlie hive get investigation --key investigation-2024-001

# Delete an investigation
limacharlie hive del investigation --key investigation-2024-001

# List all investigations
limacharlie hive list investigation
```

## Usage

### Infrastructure as Code

```yaml
hives:
  investigation:
    ransomware-investigation:
      data:
        name: "Ransomware Investigation 2024-001"
        description: "Investigating ransomware activity on DESKTOP-001"
        status: "in_progress"
        priority: "critical"
        events:
          - atom: "abc123def456"
            sid: "sensor-001-uuid"
            tags:
              - initial_access
            relevance: "First suspicious process execution"
            verdict: "malicious"
        entities:
          - type: "ip"
            value: "203.0.113.50"
            context: "C2 infrastructure"
            verdict: "malicious"
        notes:
          - type: "finding"
            content: "Initial compromise via phishing email"
            author: "analyst@example.com"
      usr_mtd:
        enabled: true
        expiry: 0
        tags:
          - ransomware
          - critical
```

## Example

```json
{
  "name": "Ransomware Investigation 2024-001",
  "description": "Investigating potential ransomware activity on endpoint DESKTOP-001",
  "status": "in_progress",
  "priority": "critical",
  "events": [
    {
      "atom": "abc123def456",
      "sid": "550e8400-e29b-41d4-a716-446655440000",
      "tags": ["initial_access", "suspicious"],
      "relevance": "First suspicious process execution",
      "verdict": "malicious",
      "comments": [
        {
          "content": "This is the initial payload dropper",
          "author": "analyst@example.com",
          "timestamp": 1700000000000
        }
      ]
    }
  ],
  "detections": [
    {
      "detection_id": "det-456-uuid",
      "tags": ["ransomware", "critical"],
      "false_positive": {
        "is_fp": false
      }
    }
  ],
  "entities": [
    {
      "type": "ip",
      "value": "203.0.113.50",
      "name": "C2 Server",
      "first_seen": 1700000000000,
      "last_seen": 1700100000000,
      "context": "Command and control infrastructure",
      "verdict": "malicious",
      "related_events": ["abc123def456"]
    },
    {
      "type": "hash",
      "value": "d41d8cd98f00b204e9800998ecf8427e",
      "context": "Malware payload hash",
      "verdict": "malicious"
    }
  ],
  "notes": [
    {
      "id": "note-1",
      "type": "finding",
      "content": "Initial compromise occurred via phishing email with malicious attachment",
      "author": "analyst@example.com",
      "timestamp": 1700000000000
    },
    {
      "type": "action_item",
      "content": "Isolate affected endpoint and collect forensic image",
      "resolved": true
    }
  ],
  "summary": "Ransomware attack detected on DESKTOP-001. Initial access via phishing.",
  "conclusion": "Attack contained. No data exfiltration observed."
}
```

## Best Practices

For opinionated guidance on tagging events and detections for SOC investigations, including MITRE ATT&CK mapping and attack chain visualization, see the [Investigation Guide](../../Getting_Started/Use_Cases/investigation-guide.md).

## Related

* [Investigation Guide](../../Getting_Started/Use_Cases/investigation-guide.md) - Best practices for tagging and documenting investigations
* [expand_timeline](../../../../marketplace/plugins/lc-essentials/skills/limacharlie-call/functions/expand-timeline.md) - Hydrate investigation with full event/detection data
