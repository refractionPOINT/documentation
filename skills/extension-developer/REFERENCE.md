# Extension Developer Reference

This document provides complete technical reference for LimaCharlie extensions, including all data types, field options, schema structures, and API details.

## Table of Contents

- [Complete Data Types Reference](#complete-data-types-reference)
- [Field Options and Filters](#field-options-and-filters)
- [Schema Structure Details](#schema-structure-details)
- [Request/Response Formats](#requestresponse-formats)
- [SDK Usage Reference](#sdk-usage-reference)
- [UI Layout Reference](#ui-layout-reference)

## Complete Data Types Reference

### Primitive Types

| Type | Description | Special Filters | Default UI |
|------|-------------|----------------|------------|
| `string` | Text value | `whitelist`, `blacklist`, `valid_re`, `invalid_re` | Text input |
| `integer` | Number | `min`, `max` | Number input |
| `bool` | Boolean | - | Toggle/Checkbox |
| `enum` | Selection from list | Requires `enum_values` field | Dropdown |
| `complex_enum` | Enum with categories/descriptions | Requires `complex_enum_values` field | Categorized dropdown |
| `sid` | Sensor ID | `platforms` filter | Sensor selector |
| `oid` | Organization ID | - | Organization selector |
| `platform` | Platform type | - | Platform dropdown |
| `architecture` | CPU architecture | - | Architecture dropdown |
| `sensor_selector` | Sensor selection criteria | - | Advanced selector |
| `tag` | Sensor tag | - | Tag input |
| `duration` | Time duration | - | Duration input |
| `time` | Timestamp | `min`, `max` | Date/time picker |
| `url` | URL value | - | URL input with validation |
| `domain` | Domain name | - | Domain input with validation |
| `yara_rule_name` | YARA rule name | - | YARA rule selector |
| `event_name` | Event type | `whitelist`, `blacklist` | Event type selector |
| `secret` | Secret from secrets manager | - | Secret selector |

### Code Block Types

Code blocks provide syntax highlighting and validation:

| Type | Description | Validation | UI Support |
|------|-------------|------------|------------|
| `json` | JSON editor | JSON syntax validation | Full editor |
| `yaml` | YAML editor | YAML syntax validation | Full editor |
| `yara_rule` | YARA rule editor | Limited validation | Limited UI support |

**Important**: Code blocks do NOT support `is_list`. Use `record` data type for multiple code blocks.

#### Code Block Example

```json
{
  "configuration": {
    "data_type": "yaml",
    "description": "YAML configuration",
    "label": "Configuration",
    "placeholder": "key: value"
  },
  "detection_rules": {
    "data_type": "json",
    "description": "Detection rules in JSON format",
    "label": "Rules",
    "default_value": "{}"
  }
}
```

### Object Types

Objects allow nested fields and complex structures.

#### Single Object

Used for grouped configuration or parameters:

```json
{
  "settings": {
    "data_type": "object",
    "is_list": false,
    "description": "Extension settings",
    "label": "Settings",
    "object": {
      "fields": {
        "enabled": {
          "data_type": "bool",
          "description": "Enable feature",
          "label": "Enabled",
          "default_value": true
        },
        "threshold": {
          "data_type": "integer",
          "description": "Alert threshold",
          "label": "Threshold",
          "filter": {
            "min": 1,
            "max": 100
          },
          "default_value": 10
        },
        "mode": {
          "data_type": "enum",
          "description": "Operation mode",
          "enum_values": ["passive", "active", "aggressive"],
          "default_value": "passive"
        }
      },
      "requirements": [["enabled"], ["threshold"]]
    }
  }
}
```

#### List of Objects (Table UI)

Used for multiple records displayed as a table:

```json
{
  "rules": {
    "data_type": "object",
    "is_list": true,
    "description": "Detection rules",
    "label": "Rules",
    "object": {
      "fields": {
        "name": {
          "data_type": "string",
          "description": "Rule name",
          "label": "Name",
          "display_index": 1
        },
        "pattern": {
          "data_type": "string",
          "description": "Detection pattern",
          "label": "Pattern",
          "display_index": 2,
          "placeholder": "regex:.*malware.*"
        },
        "severity": {
          "data_type": "enum",
          "description": "Rule severity",
          "label": "Severity",
          "enum_values": ["low", "medium", "high", "critical"],
          "default_value": "medium",
          "display_index": 3
        },
        "enabled": {
          "data_type": "bool",
          "description": "Enable this rule",
          "label": "Enabled",
          "default_value": true,
          "display_index": 4
        }
      },
      "requirements": [["name"], ["pattern"], ["severity"]]
    }
  }
}
```

#### Record Type (Key-Value Pairs)

Used for dynamic key-value mappings:

```json
{
  "tags": {
    "data_type": "record",
    "is_list": true,
    "description": "Custom tags",
    "label": "Tags",
    "object": {
      "key": {
        "name": "tag_key",
        "data_type": "string",
        "description": "Tag key"
      },
      "element_name": "tag",
      "element_desc": "A custom tag key-value pair",
      "fields": {
        "value": {
          "data_type": "string",
          "description": "Tag value",
          "label": "Value"
        },
        "description": {
          "data_type": "string",
          "description": "Tag description",
          "label": "Description"
        },
        "category": {
          "data_type": "enum",
          "description": "Tag category",
          "enum_values": ["system", "user", "automatic"],
          "default_value": "user"
        }
      },
      "requirements": [["value"]]
    }
  }
}
```

### Enum Types

#### Simple Enum

```json
{
  "severity": {
    "data_type": "enum",
    "description": "Alert severity level",
    "label": "Severity",
    "enum_values": ["low", "medium", "high", "critical"],
    "default_value": "medium",
    "placeholder": "Select severity"
  }
}
```

#### Complex Enum

Provides categorized options with descriptions:

```json
{
  "scan_profile": {
    "data_type": "complex_enum",
    "description": "Scanning profile",
    "label": "Profile",
    "complex_enum_values": {
      "categories": {
        "Basic": {
          "quick": {
            "label": "Quick Scan",
            "description": "Fast scan of critical areas only",
            "reference": "https://docs.example.com/quick-scan"
          },
          "standard": {
            "label": "Standard Scan",
            "description": "Balanced scan covering common threats"
          }
        },
        "Advanced": {
          "deep": {
            "label": "Deep Scan",
            "description": "Comprehensive system scan with thorough analysis",
            "reference": "https://docs.example.com/deep-scan"
          },
          "custom": {
            "label": "Custom Scan",
            "description": "User-defined scan parameters"
          }
        },
        "Specialized": {
          "memory": {
            "label": "Memory Scan",
            "description": "Focus on memory-resident threats"
          },
          "network": {
            "label": "Network Scan",
            "description": "Scan network connections and traffic"
          }
        }
      }
    }
  }
}
```

### Sensor Selection Types

#### SID (Sensor ID)

```json
{
  "target_sensor": {
    "data_type": "sid",
    "description": "Target sensor for operation",
    "label": "Sensor",
    "filter": {
      "platforms": ["windows", "linux"]
    }
  }
}
```

#### Sensor Selector

Advanced sensor selection with multiple criteria:

```json
{
  "targets": {
    "data_type": "sensor_selector",
    "description": "Sensors matching criteria",
    "label": "Target Sensors"
  }
}
```

## Field Options and Filters

### Universal Field Options

All fields support these optional parameters:

```json
{
  "field_name": {
    "data_type": "string",
    "description": "Tooltip description shown to users",
    "label": "Human Readable Label",
    "placeholder": "Example text shown in empty field",
    "display_index": 1,
    "default_value": "default_value_here",
    "filter": { /* Type-specific filters */ }
  }
}
```

### String Filters

```json
{
  "username": {
    "data_type": "string",
    "filter": {
      "whitelist": ["admin", "user", "guest"],
      "blacklist": ["root", "system"],
      "valid_re": "^[a-zA-Z0-9_]+$",
      "invalid_re": "^test.*"
    }
  }
}
```

### Integer Filters

```json
{
  "port": {
    "data_type": "integer",
    "filter": {
      "min": 1,
      "max": 65535
    },
    "default_value": 8080
  }
}
```

### Time Filters

```json
{
  "start_time": {
    "data_type": "time",
    "filter": {
      "min": 0,
      "max": 2147483647
    }
  }
}
```

### Platform Filters (for SID)

```json
{
  "windows_sensor": {
    "data_type": "sid",
    "filter": {
      "platforms": ["windows"]
    }
  },
  "unix_sensors": {
    "data_type": "sid",
    "filter": {
      "platforms": ["linux", "macos"]
    }
  }
}
```

### Event Name Filters

```json
{
  "event_type": {
    "data_type": "event_name",
    "filter": {
      "whitelist": ["NEW_PROCESS", "DNS_REQUEST", "NETWORK_CONNECTIONS"],
      "blacklist": ["STARTING_UP", "SHUTTING_DOWN"]
    }
  }
}
```

## Schema Structure Details

### Complete Schema Example

```json
{
  "layout": "auto",
  "views": [
    {
      "name": "Main",
      "layout": "action",
      "default_action": "primary_action"
    }
  ],
  "config_schema": {
    "fields": {
      "api_endpoint": {
        "data_type": "url",
        "description": "API endpoint URL",
        "label": "API Endpoint",
        "placeholder": "https://api.example.com",
        "display_index": 1
      },
      "api_key": {
        "data_type": "secret",
        "description": "API authentication key",
        "label": "API Key",
        "display_index": 2
      },
      "timeout": {
        "data_type": "integer",
        "description": "Request timeout in seconds",
        "label": "Timeout",
        "default_value": 30,
        "filter": {
          "min": 5,
          "max": 300
        },
        "display_index": 3
      },
      "retry_count": {
        "data_type": "integer",
        "description": "Number of retry attempts",
        "label": "Retries",
        "default_value": 3,
        "filter": {
          "min": 0,
          "max": 10
        },
        "display_index": 4
      },
      "enabled": {
        "data_type": "bool",
        "description": "Enable extension",
        "label": "Enabled",
        "default_value": true,
        "display_index": 5
      }
    },
    "requirements": [["api_endpoint"], ["api_key"]]
  },
  "request_schema": {
    "scan": {
      "is_impersonated": false,
      "is_user_facing": true,
      "short_description": "Scan a sensor for threats",
      "long_description": "Performs a comprehensive security scan on the specified sensor, checking for malware, suspicious processes, and configuration issues.",
      "messages": {
        "in_progress": "Scanning sensor...",
        "success": "Scan completed successfully",
        "error": "Scan failed"
      },
      "parameters": {
        "fields": {
          "sid": {
            "data_type": "sid",
            "description": "Sensor ID to scan",
            "label": "Sensor",
            "display_index": 1
          },
          "scan_type": {
            "data_type": "enum",
            "description": "Type of scan to perform",
            "label": "Scan Type",
            "enum_values": ["quick", "full", "custom"],
            "default_value": "quick",
            "display_index": 2
          },
          "deep_analysis": {
            "data_type": "bool",
            "description": "Enable deep analysis",
            "label": "Deep Analysis",
            "default_value": false,
            "display_index": 3
          }
        },
        "requirements": [["sid"], ["scan_type"]]
      },
      "response": {
        "fields": {
          "findings": {
            "data_type": "json",
            "description": "Scan findings and detections"
          },
          "duration": {
            "data_type": "integer",
            "description": "Scan duration in seconds"
          },
          "status": {
            "data_type": "enum",
            "enum_values": ["clean", "threats_found", "error"],
            "description": "Overall scan status"
          }
        },
        "supported_actions": ["remediate"]
      }
    },
    "remediate": {
      "is_impersonated": false,
      "is_user_facing": true,
      "short_description": "Remediate detected threats",
      "long_description": "Takes action to remediate threats detected during scanning.",
      "parameters": {
        "fields": {
          "findings": {
            "data_type": "json",
            "description": "Findings to remediate"
          },
          "action": {
            "data_type": "enum",
            "enum_values": ["quarantine", "delete", "monitor"],
            "description": "Remediation action"
          }
        },
        "requirements": [["findings"], ["action"]]
      }
    }
  },
  "required_events": ["subscribe", "unsubscribe", "update"]
}
```

### Config Schema

The `config_schema` defines extension-wide configuration stored in Hive under the `extension_configuration` namespace.

**Key Points**:
- Configuration is shared across all actions
- Validated when updated via validation callback
- Accessible in all callbacks via SDK
- Supports all data types except code blocks in some contexts

### Request Schema

The `request_schema` defines actions that users and D&R rules can invoke.

**Action Parameters**:
- `is_impersonated`: Uses user's authentication context
- `is_user_facing`: Shows in UI (false = API/D&R only)
- `short_description`: Brief UI description
- `long_description`: Detailed explanation
- `messages`: UI feedback for states (`in_progress`, `success`, `error`)
- `parameters`: Action input fields
- `response`: Expected response structure

### Response Schema

Defines the structure of action responses.

**Benefits**:
- Clarifies expected outputs for users
- Enables UI to properly display results
- Supports action chaining via `supported_actions`
- Documents API response format

```json
{
  "response": {
    "fields": {
      "status": {
        "data_type": "string",
        "description": "Operation status"
      },
      "results": {
        "data_type": "object",
        "is_list": true,
        "description": "Result records",
        "object": {
          "fields": {
            "id": {
              "data_type": "string",
              "description": "Result ID"
            },
            "severity": {
              "data_type": "enum",
              "enum_values": ["low", "medium", "high"],
              "description": "Severity level"
            }
          }
        }
      }
    },
    "supported_actions": ["follow_up_action"]
  }
}
```

## Request/Response Formats

### Webhook Request Format

LimaCharlie sends webhooks in this format:

```json
{
  "oid": "organization-id",
  "action": "scan",
  "params": {
    "sid": "sensor-id",
    "scan_type": "quick"
  },
  "user_email": "user@example.com",
  "is_impersonated": false,
  "lc_api_key": "temporary-api-key-with-permissions",
  "lc_url": "https://api.limacharlie.io"
}
```

**Headers**:
```
Content-Type: application/json
X-LC-Signature: hmac-sha256-signature
```

### Response Format

Extensions must return JSON responses:

**Success Response**:
```json
{
  "status": "success",
  "data": {
    "findings": [...],
    "duration": 45
  }
}
```

**Error Response**:
```json
{
  "error": "Error message describing what went wrong"
}
```

Or return HTTP error status with message in body.

### Event Request Format

For subscribe/unsubscribe/update events:

```json
{
  "oid": "organization-id",
  "event": "subscribe",
  "lc_api_key": "temporary-api-key-with-permissions",
  "lc_url": "https://api.limacharlie.io"
}
```

### Configuration Validation Request

When configuration changes:

```json
{
  "oid": "organization-id",
  "action": "validate_config",
  "config": {
    "api_key": "new-api-key",
    "timeout": 60
  }
}
```

**Response**: Return 200 OK for valid config, or error for invalid.

## SDK Usage Reference

### Provided SDK

Every callback receives an authenticated LimaCharlie SDK with requested permissions.

**SDK Access**:
```go
// In Golang
ctx.SDK // Pre-authenticated SDK instance

// In Python
ctx.sdk # Pre-authenticated SDK instance
```

### Common SDK Operations

#### Sensor Operations

```go
// Get sensor information
sensor, err := ctx.SDK.Sensor(sid).Get()

// Task a sensor
err = ctx.SDK.Sensor(sid).Task("history_dump", map[string]interface{}{
    "file_pattern": "*.exe",
})

// Get sensor tags
tags, err := ctx.SDK.Sensor(sid).Tags()
```

#### Hive Operations

```go
// Get configuration
config, err := ctx.SDK.Hive().Get("extension_configuration", "my-ext")

// Set configuration
err = ctx.SDK.Hive().Set("extension_configuration", "my-ext", map[string]interface{}{
    "enabled": true,
})

// Delete configuration
err = ctx.SDK.Hive().Delete("extension_configuration", "my-ext")
```

#### D&R Rule Operations

```go
// List rules
rules, err := ctx.SDK.Rules().List()

// Add rule
rule := `
detect:
  event: NEW_PROCESS
  op: is
  path: event/FILE_PATH
  value: /usr/bin/malware
respond:
  - action: report
    name: Malware Detected
`
err = ctx.SDK.Rules().Add("my-rule", rule)

// Delete rule
err = ctx.SDK.Rules().Delete("my-rule")
```

#### Output Operations

```go
// Get outputs
outputs, err := ctx.SDK.Outputs().List()

// Add output
err = ctx.SDK.Outputs().Add("my-output", map[string]interface{}{
    "type": "syslog",
    "host": "syslog.example.com",
    "port": 514,
})
```

#### Artifact Operations

```go
// Get artifact
artifact, err := ctx.SDK.Artifact().Get(artifactID)

// List artifacts
artifacts, err := ctx.SDK.Artifact().List()
```

### Permission Requirements

Extensions only have permissions specified in their definition:

```json
"permissions": [
  "sensor.get",
  "sensor.task",
  "dr.get",
  "dr.set",
  "hive.get",
  "hive.set"
]
```

**Common Permissions**:
- `sensor.get`: Read sensor information
- `sensor.task`: Task sensors
- `sensor.tag`: Manage sensor tags
- `dr.get`: Read D&R rules
- `dr.set`: Create/update/delete D&R rules
- `hive.get`: Read Hive data
- `hive.set`: Write Hive data
- `artifact.get`: Access artifacts
- `outputs.get`: Read outputs
- `outputs.set`: Manage outputs
- `fp.ctrl`: Manage false positives
- `user.get`: Read user information
- `billing.ctrl`: Billing operations

## UI Layout Reference

### Layout Types

#### Auto Layout

Default layout that adapts based on schema:

```json
{
  "layout": "auto"
}
```

#### Config Layout

Prioritizes configuration display:

```json
{
  "layout": "config"
}
```

Best for: Extensions with complex configuration and few actions.

#### Editor Layout

Large code editor for YAML/JSON:

```json
{
  "layout": "editor",
  "default_action": "validate_yaml"
}
```

Best for: Extensions focused on editing YAML/JSON content.

#### Action Layout

Prioritizes specific actions with in-page forms:

```json
{
  "layout": "action",
  "default_action": "scan"
}
```

Best for: Extensions with primary action workflows.

#### Description Layout

Description-focused layout:

```json
{
  "layout": "description"
}
```

Best for: Extensions with extensive documentation or guidance.

### Multiple Views (Tabs)

Create tabbed interface with multiple layouts:

```json
{
  "views": [
    {
      "name": "Configuration",
      "layout": "config"
    },
    {
      "name": "Scan",
      "layout": "action",
      "default_action": "scan"
    },
    {
      "name": "History",
      "layout": "description"
    },
    {
      "name": "Editor",
      "layout": "editor",
      "default_action": "validate_rules"
    }
  ]
}
```

### Supported Actions (Action Chaining)

Link actions in workflows:

```json
{
  "detect": {
    "response": {
      "fields": {
        "threats": {
          "data_type": "json",
          "description": "Detected threats"
        }
      },
      "supported_actions": ["remediate", "report"]
    }
  },
  "remediate": {
    "parameters": {
      "fields": {
        "threats": {
          "data_type": "json",
          "description": "Threats to remediate"
        }
      }
    }
  }
}
```

This creates a workflow where "detect" results can flow directly to "remediate" or "report" actions.

### Display Index

Control field order with `display_index`:

```json
{
  "fields": {
    "name": {
      "data_type": "string",
      "display_index": 1
    },
    "description": {
      "data_type": "string",
      "display_index": 3
    },
    "enabled": {
      "data_type": "bool",
      "display_index": 2
    }
  }
}
```

Fields are displayed in order: name (1), enabled (2), description (3).

### UI Messages

Customize UI feedback for actions:

```json
{
  "scan": {
    "messages": {
      "in_progress": "Scanning sensor for threats...",
      "success": "Scan completed - {findings_count} findings",
      "error": "Scan failed: {error_message}"
    }
  }
}
```

Messages support variable interpolation from response data.
