---
name: extension-developer
description: Use this skill when the user needs help building, testing, or deploying custom LimaCharlie extensions.
---

# LimaCharlie Extension Developer

This skill helps you build custom LimaCharlie extensions. Use this when users ask for help creating extensions, understanding the extension architecture, building UI components, or debugging extension issues.

## What are LimaCharlie Extensions?

LimaCharlie Extensions are small HTTPS services that receive webhooks from the LimaCharlie cloud, enabling you to expand and customize security environments by integrating third-party tools, automating workflows, and adding new capabilities.

### Key Benefits

- **Multi-tenancy**: LC organizations can subscribe to your extension and replicate features across tenants
- **Credentials handling**: No need to store credentials - every callback includes an authenticated LimaCharlie SDK with requested permissions
- **Configuration**: LC provides a configuration JSON object stored in Hive with validation callbacks
- **Auto-generated UI**: Extensions define a schema that LimaCharlie interprets to generate custom user interfaces

### Public vs Private Extensions

- **Private Extensions**: Require `billing.ctrl` and `user.ctrl` permissions to subscribe an organization
- **Public Extensions**: Visible and subscribable by everyone (contact answers@limacharlie.io to make an extension public)

## Extension Architecture

### High-Level Structure

Extensions are HTTPS services that:
1. Receive webhooks from LimaCharlie cloud
2. Process requests using the LimaCharlie SDK (provided in callbacks)
3. Return responses in JSON format
4. Can be hosted on Google Cloud Run, AWS Lambda, or custom infrastructure

### Request/Response Model

```
User/D&R Rule → LimaCharlie Cloud → Extension (via webhook)
                                   ↓
                        Process with LC SDK
                                   ↓
                        Return JSON Response
```

Each webhook includes:
- **Request data**: Action name and parameters
- **Authenticated SDK**: Pre-configured with org-specific permissions
- **Organization context**: Relevant to the callback
- **Signature**: Shared secret for authenticity verification

## Getting Started

### Framework Options

**Golang** (recommended for stricter typing):
```
https://github.com/refractionPOINT/lc-extension
```

**Python**:
```
https://github.com/refractionPOINT/lc-extension/tree/master/python
```

### Creating an Extension Definition

Navigate to: https://app.limacharlie.io/add-ons/published

Required fields:
- **Destination URL**: HTTPS endpoint for your extension
- **Required Extensions**: List of other extensions your extension depends on
- **Shared Secret**: Random string (32+ characters) for webhook signature verification
- **Extension Flairs**:
  - `segment`: Isolates resources (extension can only see/modify what it created)
  - `bulk`: Increases API quota for extensions making many API calls
- **Permissions**: List of required permissions (use least privilege)

## Extension Schema

The schema describes what your extension can do and defines the auto-generated UI.

### Schema Structure

```json
{
  "config_schema": {
    "fields": { ... },
    "requirements": null
  },
  "request_schema": {
    "action_name": {
      "is_impersonated": false,
      "is_user_facing": true,
      "short_description": "Brief description",
      "long_description": "Detailed description",
      "parameters": {
        "fields": { ... },
        "requirements": null
      },
      "response": {
        "fields": { ... },
        "requirements": null
      }
    }
  },
  "required_events": [
    "subscribe",
    "unsubscribe",
    "update"
  ]
}
```

### Field Structure

Every field follows this minimal structure:

```json
{
  "field_name": {
    "data_type": "string",
    "description": "Field description",
    "label": "Human Readable Label",
    "placeholder": "Example value",
    "display_index": 1,
    "default_value": "default"
  }
}
```

### Requirements Array

The `requirements` field defines which fields are required:

```json
// Both fields required
"requirements": [["denominator"], ["numerator"]]

// denominator AND (numerator OR default) required
"requirements": [["denominator"], ["numerator", "default"]]
```

- First array joins with AND
- Nested arrays join with OR

### Config Schema

Defines extension configuration stored in Hive (`extension_configuration` namespace).

```json
{
  "config_schema": {
    "fields": {
      "api_key": {
        "data_type": "secret",
        "description": "API key for external service",
        "label": "API Key"
      },
      "timeout": {
        "data_type": "integer",
        "description": "Request timeout in seconds",
        "default_value": 30
      }
    },
    "requirements": [["api_key"]]
  }
}
```

### Request Schema

Defines actions users and D&R rules can invoke.

#### Request Parameters

- **is_impersonated**: If true, request impersonates the user's authentication
- **is_user_facing**: If true, action appears in UI (false hides from UI but allows API/D&R usage)
- **short_description**: Brief description for UI
- **long_description**: Detailed description
- **messages**: Optional UI messages for `in_progress`, `success`, `error` states
- **parameters**: Fields for this action
- **response**: Optional response schema (defines expected return structure)

#### Example Request Schema

```json
{
  "scan": {
    "is_impersonated": false,
    "is_user_facing": true,
    "short_description": "Scan a sensor",
    "long_description": "Perform a security scan on the specified sensor",
    "parameters": {
      "fields": {
        "sid": {
          "data_type": "sid",
          "description": "Sensor ID to scan",
          "label": "Sensor"
        },
        "scan_type": {
          "data_type": "enum",
          "description": "Type of scan to perform",
          "enum_values": ["full", "quick", "custom"]
        }
      },
      "requirements": [["sid"], ["scan_type"]]
    },
    "response": {
      "fields": {
        "findings": {
          "data_type": "json",
          "description": "Scan findings"
        },
        "duration": {
          "data_type": "integer",
          "description": "Scan duration in seconds"
        }
      }
    }
  }
}
```

### Response Schema (Optional)

Defines the structure of data returned by an action. Useful for:
- Clarifying expected responses for users
- Enabling UI to properly display results
- Supporting `supported_action` chaining

```json
{
  "response": {
    "fields": {
      "status": {
        "data_type": "string",
        "description": "Operation status"
      },
      "data": {
        "data_type": "json",
        "description": "Response data"
      }
    }
  }
}
```

## Data Types

### Primitive Types

| Type | Description | Special Filters |
|------|-------------|----------------|
| `string` | Text value | `whitelist`, `blacklist`, `valid_re`, `invalid_re` |
| `integer` | Number | `min`, `max` |
| `bool` | Boolean | - |
| `enum` | Selection from list | Requires `enum_values` field |
| `complex_enum` | Enum with categories/descriptions | Requires `complex_enum_values` field |
| `sid` | Sensor ID | `platforms` filter |
| `oid` | Organization ID | - |
| `platform` | Platform type | - |
| `architecture` | CPU architecture | - |
| `sensor_selector` | Sensor selection criteria | - |
| `tag` | Sensor tag | - |
| `duration` | Time duration | - |
| `time` | Timestamp | `min`, `max` |
| `url` | URL value | - |
| `domain` | Domain name | - |
| `yara_rule_name` | YARA rule name | - |
| `event_name` | Event type | `whitelist`, `blacklist` |
| `secret` | Secret from secrets manager | - |

#### Enum Example

```json
{
  "severity": {
    "data_type": "enum",
    "description": "Alert severity level",
    "enum_values": ["low", "medium", "high", "critical"],
    "default_value": "medium"
  }
}
```

#### Complex Enum Example

```json
{
  "scan_profile": {
    "data_type": "complex_enum",
    "description": "Scanning profile",
    "complex_enum_values": {
      "categories": {
        "Basic": {
          "quick": {
            "label": "Quick Scan",
            "description": "Fast scan of critical areas",
            "reference": "https://docs.example.com/quick"
          }
        },
        "Advanced": {
          "deep": {
            "label": "Deep Scan",
            "description": "Comprehensive system scan"
          }
        }
      }
    }
  }
}
```

### Code Block Types

Code blocks provide syntax highlighting and validation:

1. **json**: JSON editor with validation
2. **yaml**: YAML editor with validation
3. **yara_rule**: YARA rule editor (limited UI support)

**Important**: Code blocks do NOT support `is_list`. Use `record` data type for multiple code blocks.

#### Code Block Example

```json
{
  "configuration": {
    "data_type": "yaml",
    "description": "YAML configuration",
    "label": "Configuration"
  }
}
```

### Object Types

Objects allow nested fields and can be displayed as tables with `is_list: true`.

#### Single Object

```json
{
  "settings": {
    "data_type": "object",
    "is_list": false,
    "description": "Extension settings",
    "object": {
      "fields": {
        "enabled": {
          "data_type": "bool",
          "description": "Enable feature"
        },
        "threshold": {
          "data_type": "integer",
          "description": "Alert threshold"
        }
      },
      "requirements": [["enabled"]]
    }
  }
}
```

#### List of Objects (Table UI)

```json
{
  "rules": {
    "data_type": "object",
    "is_list": true,
    "description": "Detection rules",
    "object": {
      "fields": {
        "name": {
          "data_type": "string",
          "description": "Rule name"
        },
        "pattern": {
          "data_type": "string",
          "description": "Detection pattern"
        },
        "severity": {
          "data_type": "enum",
          "enum_values": ["low", "medium", "high"]
        }
      },
      "requirements": [["name"], ["pattern"]]
    }
  }
}
```

#### Record Type (Key-Value Pairs)

```json
{
  "tags": {
    "data_type": "record",
    "is_list": true,
    "description": "Custom tags",
    "object": {
      "key": {
        "name": "tag_key",
        "data_type": "string"
      },
      "element_name": "tag",
      "element_desc": "A custom tag key-value pair",
      "fields": {
        "value": {
          "data_type": "string",
          "description": "Tag value"
        },
        "description": {
          "data_type": "string",
          "description": "Tag description"
        }
      }
    }
  }
}
```

### Field Options

All fields support these optional parameters:

- **label**: Human-readable field label
- **placeholder**: Example text in input field
- **description**: Tooltip description
- **display_index**: Display order (starts at 1)
- **default_value**: Default field value
- **filter**: Conditional filters (min/max for numbers, whitelist/blacklist for strings)

## Callbacks

Extensions implement callbacks to handle different event types.

### Configuration Validation Callback

Called when configuration changes in Hive. Validate and return success or error.

```go
func validateConfig(config map[string]interface{}) error {
    apiKey, ok := config["api_key"].(string)
    if !ok || apiKey == "" {
        return fmt.Errorf("api_key is required")
    }
    // Validate API key format
    if len(apiKey) < 32 {
        return fmt.Errorf("api_key must be at least 32 characters")
    }
    return nil
}
```

### Event Callback

Handle platform events. Specify interested events in schema's `required_events`.

#### Available Events

- **subscribe**: Organization subscribes to extension
- **unsubscribe**: Organization unsubscribes from extension
- **update**: Daily update trigger (useful for updating D&R rules, lookups, etc.)

#### Subscribe Event Example

```go
func handleSubscribe(ctx ExtensionContext) error {
    // Initialize resources for new organization
    err := ctx.SDK.Rules().Add("my-rule", ruleContent)
    if err != nil {
        return fmt.Errorf("failed to add rule: %w", err)
    }

    // Create initial configuration
    config := map[string]interface{}{
        "enabled": true,
        "initialized_at": time.Now().Unix(),
    }
    return ctx.SDK.Hive().Set("extension_configuration", "my-ext", config)
}
```

#### Update Event Example

```go
func handleUpdate(ctx ExtensionContext) error {
    // Update D&R rules daily
    latestRules := fetchLatestRules()
    for name, content := range latestRules {
        err := ctx.SDK.Rules().Add(name, content)
        if err != nil {
            log.Printf("Failed to update rule %s: %v", name, err)
        }
    }
    return nil
}
```

### Request Callback

Handle user-initiated or D&R-triggered requests.

#### Request Context

Callbacks receive:
- **Action name**: Which action was invoked
- **Parameters**: User-provided parameters
- **SDK**: Authenticated LimaCharlie SDK
- **Organization info**: OID, sensor details, etc.

#### Request Example

```go
func handleScan(ctx ExtensionContext, params map[string]interface{}) (interface{}, error) {
    sid, ok := params["sid"].(string)
    if !ok {
        return nil, fmt.Errorf("sid parameter required")
    }

    scanType, _ := params["scan_type"].(string)
    if scanType == "" {
        scanType = "quick"
    }

    // Perform scan
    results := performScan(ctx.SDK, sid, scanType)

    // Return response matching schema
    return map[string]interface{}{
        "findings": results.Findings,
        "duration": results.Duration,
        "status": "completed",
    }, nil
}
```

## User Interface Development

### Auto-Generated UI

LimaCharlie automatically generates UI from your schema. The UI adapts based on data types and layout configuration.

### UI Page Structure

1. **Header**: Extension label and short description
2. **Associated Sensor Button**: Quick access if extension has associated sensor
3. **Action Dropdown**: Actions marked `is_user_facing: true`
4. **Main Content**: Determined by layout type

### Layout Types

Specify layout in schema's top-level `layout` field:

- **auto** (default): Automatically selects appropriate layout
- **config**: Prioritizes configuration display
- **editor**: For large code blocks (YAML/JSON editing)
- **action**: Prioritizes specific actions with in-page forms
- **description**: Description-focused layout
- **key**: Variation of description layout

#### Editor Layout Example

```json
{
  "layout": "editor",
  "default_action": "validate_yaml",
  "request_schema": {
    "validate_yaml": {
      "is_user_facing": true,
      "parameters": {
        "fields": {
          "yaml_content": {
            "data_type": "yaml",
            "description": "YAML to validate"
          }
        }
      }
    }
  }
}
```

### Multiple Layouts (Tabs)

Define multiple views as tabs:

```json
{
  "views": [
    {
      "name": "Configuration",
      "layout": "config"
    },
    {
      "name": "Actions",
      "layout": "action",
      "default_action": "scan"
    },
    {
      "name": "Documentation",
      "layout": "description"
    }
  ]
}
```

### Supported Actions

Link actions in workflows by defining `supported_actions` in response schema. This allows chaining actions where response data flows to the next action.

```json
{
  "detect": {
    "is_user_facing": true,
    "short_description": "Detect threats",
    "parameters": { ... },
    "response": {
      "fields": {
        "threats": {
          "data_type": "json",
          "description": "Detected threats"
        }
      },
      "supported_actions": ["remediate"]
    }
  },
  "remediate": {
    "is_user_facing": true,
    "short_description": "Remediate threats",
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

## Testing and Debugging

### Local Testing

1. **Set up local HTTPS server**:
   ```bash
   # Using Go
   go run main.go --port 8080

   # Using Python
   python extension.py --port 8080
   ```

2. **Use ngrok for webhook testing**:
   ```bash
   ngrok http 8080
   # Use ngrok URL as Destination URL
   ```

3. **Test webhook signatures**:
   ```go
   func verifySignature(body []byte, signature string, secret string) bool {
       mac := hmac.New(sha256.New, []byte(secret))
       mac.Write(body)
       expected := hex.EncodeToString(mac.Sum(nil))
       return hmac.Equal([]byte(expected), []byte(signature))
   }
   ```

### Testing Configuration Validation

```bash
# Update config via CLI to test validation
limacharlie hive set extension_configuration my-ext '{"api_key": "test123"}'
```

### Testing Requests

```bash
# Test extension request via CLI
limacharlie extension request --name my-ext --action scan --data '{"sid": "12345"}'
```

### Testing from D&R Rules

```yaml
detect:
  event: NEW_PROCESS
  op: is
  path: event/FILE_PATH
  value: /usr/bin/test
respond:
  - action: extension request
    extension name: my-ext
    extension action: scan
    extension request:
      sid: '{{ .routing.sid }}'
```

### Logging and Debugging

```go
import "log"

func handleRequest(ctx ExtensionContext, params map[string]interface{}) (interface{}, error) {
    log.Printf("Received request: action=%s, params=%v", ctx.Action, params)

    // Your logic here

    log.Printf("Sending response: %v", response)
    return response, nil
}
```

## Deployment

### Hosting Options

#### Google Cloud Run (Recommended)

```bash
# Build container
docker build -t gcr.io/PROJECT/my-extension .

# Push to GCR
docker push gcr.io/PROJECT/my-extension

# Deploy
gcloud run deploy my-extension \
  --image gcr.io/PROJECT/my-extension \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### AWS Lambda

Use AWS API Gateway + Lambda for serverless deployment:

```python
def lambda_handler(event, context):
    # Extract webhook data
    body = json.loads(event['body'])
    signature = event['headers'].get('x-lc-signature')

    # Verify signature
    if not verify_signature(body, signature):
        return {'statusCode': 403, 'body': 'Invalid signature'}

    # Process request
    response = handle_extension_request(body)

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
```

### Publishing

1. **Test thoroughly**: Verify all actions and edge cases
2. **Set up monitoring**: Track errors and performance
3. **Document usage**: Provide clear descriptions in schema
4. **Contact LimaCharlie**: Email answers@limacharlie.io to make extension public
5. **Set pricing** (optional): Work with LC team for monetization

### Updating Extensions

When updating schema or code:

1. **Update schema**: Modify via web interface or API
2. **Deploy new code**: Update HTTPS endpoint
3. **Test changes**: Verify with test organization
4. **Notify users**: If breaking changes, communicate with subscribers

## Best Practices

### Security

1. **Verify signatures**: Always verify webhook signatures using shared secret
   ```go
   if !verifySignature(body, signature, sharedSecret) {
       return fmt.Errorf("invalid signature")
   }
   ```

2. **Validate input**: Sanitize and validate all user input
   ```go
   func validateSID(sid string) error {
       if !regexp.MustCompile(`^[a-f0-9-]+$`).MatchString(sid) {
           return fmt.Errorf("invalid sid format")
       }
       return nil
   }
   ```

3. **Use least privilege**: Request minimum required permissions
   ```json
   "permissions": ["sensor.get", "sensor.task"]
   ```

4. **Handle secrets securely**: Use environment variables, never hardcode
   ```go
   sharedSecret := os.Getenv("LC_SHARED_SECRET")
   ```

5. **Use segment flair**: Isolate extension resources when possible
   ```
   Extension Flairs: ["segment"]
   ```

### Performance

1. **Async operations**: Use background processing for long tasks
   ```go
   go func() {
       performLongScan(ctx, params)
   }()
   return map[string]interface{}{"status": "started"}, nil
   ```

2. **Cache configurations**: Avoid repeated Hive reads
   ```go
   var configCache sync.Map

   func getConfig(oid string, sdk *limacharlie.SDK) (map[string]interface{}, error) {
       if cached, ok := configCache.Load(oid); ok {
           return cached.(map[string]interface{}), nil
       }
       config, err := sdk.Hive().Get("extension_configuration", "my-ext")
       if err == nil {
           configCache.Store(oid, config)
       }
       return config, err
   }
   ```

3. **Use bulk flair**: For extensions making many API calls
   ```
   Extension Flairs: ["bulk"]
   ```

4. **Implement timeouts**: Prevent hanging requests
   ```go
   ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
   defer cancel()
   ```

### Error Handling

1. **Return meaningful errors**: Help users understand issues
   ```go
   return nil, fmt.Errorf("failed to scan sensor %s: %w", sid, err)
   ```

2. **Handle partial failures**: Continue processing when possible
   ```go
   var errors []string
   for _, sid := range sids {
       if err := scanSensor(sid); err != nil {
           errors = append(errors, fmt.Sprintf("sensor %s: %v", sid, err))
       }
   }
   if len(errors) > 0 {
       return map[string]interface{}{
           "status": "partial_failure",
           "errors": errors,
       }, nil
   }
   ```

3. **Log errors**: Maintain logs for debugging
   ```go
   log.Printf("ERROR: %v", err)
   ```

### Configuration Management

1. **Provide defaults**: Make configuration optional when possible
   ```go
   timeout := 30
   if config["timeout"] != nil {
       timeout = int(config["timeout"].(float64))
   }
   ```

2. **Validate configuration**: Check values on update
   ```go
   func validateConfig(config map[string]interface{}) error {
       if timeout, ok := config["timeout"].(float64); ok {
           if timeout < 1 || timeout > 300 {
               return fmt.Errorf("timeout must be between 1 and 300 seconds")
           }
       }
       return nil
   }
   ```

3. **Use update events**: Keep configurations synchronized
   ```go
   func handleUpdate(ctx ExtensionContext) error {
       config, err := ctx.SDK.Hive().Get("extension_configuration", "my-ext")
       if err != nil {
           return err
       }
       // Apply configuration updates
       return applyConfig(config)
   }
   ```

## Simplified Frameworks

The Golang implementation provides specialized frameworks for common use cases:

### D&R Framework

Package D&R rules as an extension for easy distribution and updates.

```go
import "github.com/refractionPOINT/lc-extension/simplified/dr"

func GetRules() map[string]map[string]string {
    return map[string]map[string]string{
        "my-namespace": {
            "rule-1": `
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: malware.exe
respond:
  - action: report
    name: Malware Detected
`,
            "rule-2": `...`,
        },
    }
}

func main() {
    dr.Serve(dr.Config{
        GetRules: GetRules,
    })
}
```

### Lookup Framework

Package Lookups for distribution.

```go
import "github.com/refractionPOINT/lc-extension/simplified/lookup"

func GetLookups() map[string][]string {
    return map[string][]string{
        "malware-domains": {
            "evil.com",
            "malicious.net",
            // ...
        },
        "threat-ips": {
            "1.2.3.4",
            "5.6.7.8",
        },
    }
}

func main() {
    lookup.Serve(lookup.Config{
        GetLookups: GetLookups,
    })
}
```

### CLI Framework

Integrate third-party CLI tools with LimaCharlie.

```go
import "github.com/refractionPOINT/lc-extension/simplified/cli"

func main() {
    cli.Serve(cli.Config{
        CommandPath: "/usr/bin/nmap",
        CommandArgs: []string{"-sV", "{{.target}}"},
        OutputParser: func(output string) (map[string]interface{}, error) {
            // Parse CLI output
            return parseNmapOutput(output)
        },
    })
}
```

## Complete Extension Examples

### Example 1: Simple Alerting Extension

```go
package main

import (
    "fmt"
    "log"
    ext "github.com/refractionPOINT/lc-extension"
)

func main() {
    e := ext.NewExtension(ext.Config{
        SharedSecret: os.Getenv("SHARED_SECRET"),
        Schema: &ext.Schema{
            ConfigSchema: &ext.ObjectSchema{
                Fields: map[string]*ext.Field{
                    "webhook_url": {
                        DataType:    "url",
                        Description: "Webhook URL for alerts",
                    },
                    "severity_filter": {
                        DataType:    "enum",
                        EnumValues:  []string{"low", "medium", "high", "critical"},
                        Description: "Minimum severity to alert",
                    },
                },
                Requirements: [][]string{{"webhook_url"}},
            },
            RequestSchema: map[string]*ext.RequestSchema{
                "alert": {
                    IsUserFacing:     true,
                    ShortDescription: "Send alert",
                    Parameters: &ext.ObjectSchema{
                        Fields: map[string]*ext.Field{
                            "message": {
                                DataType:    "string",
                                Description: "Alert message",
                            },
                            "severity": {
                                DataType:    "enum",
                                EnumValues:  []string{"low", "medium", "high", "critical"},
                                Description: "Alert severity",
                            },
                        },
                        Requirements: [][]string{{"message"}, {"severity"}},
                    },
                },
            },
            RequiredEvents: []string{"subscribe"},
        },
    })

    e.OnRequest("alert", func(ctx *ext.Context) (interface{}, error) {
        config, err := ctx.SDK.Hive().Get("extension_configuration", "alerter")
        if err != nil {
            return nil, fmt.Errorf("failed to get config: %w", err)
        }

        webhookURL := config["webhook_url"].(string)
        message := ctx.Params["message"].(string)
        severity := ctx.Params["severity"].(string)

        // Send webhook
        err = sendWebhook(webhookURL, message, severity)
        if err != nil {
            return nil, fmt.Errorf("failed to send webhook: %w", err)
        }

        return map[string]interface{}{
            "status": "sent",
            "timestamp": time.Now().Unix(),
        }, nil
    })

    e.OnEvent("subscribe", func(ctx *ext.Context) error {
        log.Printf("New subscription: %s", ctx.OID)
        return nil
    })

    log.Fatal(e.Serve(":8080"))
}
```

### Example 2: Scanning Extension with Tables

```json
{
  "config_schema": {
    "fields": {
      "scan_timeout": {
        "data_type": "integer",
        "description": "Scan timeout in seconds",
        "default_value": 60,
        "label": "Scan Timeout"
      },
      "auto_remediate": {
        "data_type": "bool",
        "description": "Automatically remediate threats",
        "default_value": false,
        "label": "Auto Remediate"
      }
    }
  },
  "request_schema": {
    "scan": {
      "is_impersonated": false,
      "is_user_facing": true,
      "short_description": "Scan for threats",
      "parameters": {
        "fields": {
          "targets": {
            "data_type": "object",
            "is_list": true,
            "description": "Scan targets",
            "label": "Targets",
            "object": {
              "fields": {
                "sid": {
                  "data_type": "sid",
                  "description": "Sensor ID",
                  "display_index": 1
                },
                "path": {
                  "data_type": "string",
                  "description": "Path to scan",
                  "display_index": 2
                },
                "depth": {
                  "data_type": "integer",
                  "description": "Scan depth",
                  "default_value": 3,
                  "display_index": 3
                }
              },
              "requirements": [["sid"], ["path"]]
            }
          }
        },
        "requirements": [["targets"]]
      },
      "response": {
        "fields": {
          "results": {
            "data_type": "object",
            "is_list": true,
            "description": "Scan results",
            "object": {
              "fields": {
                "sid": {
                  "data_type": "string",
                  "description": "Sensor ID"
                },
                "threats_found": {
                  "data_type": "integer",
                  "description": "Number of threats"
                },
                "status": {
                  "data_type": "enum",
                  "enum_values": ["clean", "infected", "error"],
                  "description": "Scan status"
                }
              }
            }
          }
        }
      }
    }
  }
}
```

## Using Extensions

### From Web UI

1. Navigate to extension page in LimaCharlie web app
2. Select action from dropdown
3. Fill in parameters
4. Click execute

### From D&R Rules

```yaml
detect:
  event: CODE_IDENTITY
  op: lookup
  path: event/HASH
  resource: hive://lookup/malware-hashes
respond:
  - action: extension request
    extension name: my-scanner
    extension action: scan
    extension request:
      sid: '{{ .routing.sid }}'
      path: '{{ .event.FILE_PATH }}'
      depth: 5
```

### From API

```bash
curl -X POST "https://api.limacharlie.io/v1/ext/my-scanner/request" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "oid": "organization-id",
    "action": "scan",
    "params": {
      "sid": "sensor-id",
      "path": "/usr/bin",
      "depth": 3
    }
  }'
```

### From CLI

```bash
limacharlie extension request \
  --name my-scanner \
  --action scan \
  --data '{"sid": "sensor-id", "path": "/usr/bin", "depth": 3}'
```

## Interacting with Organizations

### Using the Provided SDK

Every callback receives an authenticated SDK:

```go
func handleRequest(ctx *ext.Context) (interface{}, error) {
    // Get sensor info
    sensor, err := ctx.SDK.Sensor(ctx.Params["sid"].(string)).Get()
    if err != nil {
        return nil, err
    }

    // Task sensor
    err = ctx.SDK.Sensor(sensor.SID).Task("history_dump", nil)
    if err != nil {
        return nil, err
    }

    // Access Hive
    config, err := ctx.SDK.Hive().Get("extension_configuration", "my-ext")
    if err != nil {
        return nil, err
    }

    // Add D&R rule
    rule := `...`
    err = ctx.SDK.Rules().Add("my-rule", rule)
    if err != nil {
        return nil, err
    }

    return map[string]interface{}{"status": "success"}, nil
}
```

### Checking Permissions

Extensions receive only the permissions specified in their definition:

```go
// Extension definition specifies:
// "permissions": ["sensor.get", "sensor.task", "dr.get", "dr.set"]

// These will work:
ctx.SDK.Sensor(sid).Get()
ctx.SDK.Sensor(sid).Task("history_dump", nil)
ctx.SDK.Rules().List()
ctx.SDK.Rules().Add("rule", content)

// This will fail (missing permission):
ctx.SDK.User().List() // Error: missing user.get permission
```

## Troubleshooting

### Extension Not Receiving Webhooks

1. **Verify URL is accessible**: Test with curl
   ```bash
   curl -X POST https://your-extension.com/webhook
   ```

2. **Check signature verification**: Ensure shared secret matches
   ```go
   log.Printf("Received signature: %s", signature)
   log.Printf("Expected signature: %s", computeSignature(body))
   ```

3. **Review extension logs**: Check for errors in your service logs

4. **Test with ngrok**: Use ngrok to debug locally
   ```bash
   ngrok http 8080
   # Update extension URL to ngrok URL
   ```

### Schema Not Updating in UI

1. **Clear browser cache**: Hard refresh (Ctrl+Shift+R)
2. **Verify schema format**: Check for JSON syntax errors
3. **Check schema via API**:
   ```bash
   limacharlie extension get_schema --name my-ext
   ```

### Configuration Validation Failing

1. **Check validation callback**: Add logging to validation function
   ```go
   func validateConfig(config map[string]interface{}) error {
       log.Printf("Validating config: %v", config)
       // validation logic
   }
   ```

2. **Test configuration format**: Ensure JSON structure matches schema
3. **Review requirements**: Verify all required fields are present

### SDK Permissions Errors

1. **Check extension definition**: Verify required permissions are listed
2. **Test with minimal permissions**: Start with basic permissions and add as needed
3. **Review error messages**: LC API returns specific permission errors

## Additional Resources

### Code References

- **Golang Extension Framework**: https://github.com/refractionPOINT/lc-extension
- **Python Extension Framework**: https://github.com/refractionPOINT/lc-extension/tree/master/python
- **Schema Types Definition**: https://github.com/refractionPOINT/lc-extension/blob/master/common/config_schema.go

### Example Extensions

- **YARA Extension**: Automated YARA scanning
- **Artifact Extension**: Low-level collection capabilities
- **Dumper Extension**: Process memory dumping
- **Infrastructure Extension**: Cloud infrastructure management

### Documentation

- **Extension API**: https://api.limacharlie.io/static/swagger/#/Extension-Request
- **Schema API**: https://api.limacharlie.io/static/swagger/#/Extension-Schema
- **Hive Documentation**: Reference for configuration storage
- **D&R Documentation**: For extension integration with detection rules

### Community

- **Community Slack**: Get help from LC team and community
- **Email Support**: answers@limacharlie.io
- **GitHub Issues**: Report framework bugs

## Key Reminders

1. Always verify webhook signatures for security
2. Use least privilege permissions
3. Validate all user input in callbacks
4. Provide clear, descriptive schema definitions
5. Test with test organizations before production
6. Use segment flair to isolate resources
7. Implement proper error handling and logging
8. Cache configurations to reduce API calls
9. Use simplified frameworks for common patterns (D&R, Lookups, CLI)
10. Add response schemas to clarify expected outputs
11. Use suppression in D&R rules that call extensions
12. Document actions with short and long descriptions
13. Test locally with ngrok before deploying
14. Monitor extension performance and errors
15. Keep shared secret secure (use environment variables)

This skill provides comprehensive guidance for building LimaCharlie extensions. When helping users, always encourage testing with a test organization before production deployment and emphasize security best practices.
