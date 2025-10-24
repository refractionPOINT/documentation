# Extension Examples

This document provides complete, working examples of LimaCharlie extensions for common use cases.

## Table of Contents

- [Simple Alerting Extension](#simple-alerting-extension)
- [Scanning Extension with Tables](#scanning-extension-with-tables)
- [Multi-Action Extension](#multi-action-extension)
- [D&R Rule Distribution](#dr-rule-distribution)
- [Lookup Distribution](#lookup-distribution)
- [CLI Integration](#cli-integration)
- [Complex Configuration Extension](#complex-configuration-extension)

## Simple Alerting Extension

A basic extension that sends alerts to external webhooks.

### Schema

```json
{
  "layout": "action",
  "default_action": "alert",
  "config_schema": {
    "fields": {
      "webhook_url": {
        "data_type": "url",
        "description": "Webhook URL for alerts",
        "label": "Webhook URL",
        "placeholder": "https://hooks.example.com/alerts",
        "display_index": 1
      },
      "severity_filter": {
        "data_type": "enum",
        "description": "Minimum severity to alert",
        "label": "Severity Filter",
        "enum_values": ["low", "medium", "high", "critical"],
        "default_value": "medium",
        "display_index": 2
      },
      "enabled": {
        "data_type": "bool",
        "description": "Enable alerting",
        "label": "Enabled",
        "default_value": true,
        "display_index": 3
      }
    },
    "requirements": [["webhook_url"]]
  },
  "request_schema": {
    "alert": {
      "is_impersonated": false,
      "is_user_facing": true,
      "short_description": "Send alert to webhook",
      "long_description": "Sends an alert message to the configured webhook URL with the specified severity level.",
      "messages": {
        "in_progress": "Sending alert...",
        "success": "Alert sent successfully",
        "error": "Failed to send alert"
      },
      "parameters": {
        "fields": {
          "message": {
            "data_type": "string",
            "description": "Alert message",
            "label": "Message",
            "display_index": 1
          },
          "severity": {
            "data_type": "enum",
            "description": "Alert severity",
            "label": "Severity",
            "enum_values": ["low", "medium", "high", "critical"],
            "default_value": "medium",
            "display_index": 2
          },
          "metadata": {
            "data_type": "json",
            "description": "Additional metadata",
            "label": "Metadata",
            "default_value": "{}",
            "display_index": 3
          }
        },
        "requirements": [["message"], ["severity"]]
      },
      "response": {
        "fields": {
          "status": {
            "data_type": "string",
            "description": "Send status"
          },
          "timestamp": {
            "data_type": "integer",
            "description": "Unix timestamp"
          }
        }
      }
    }
  },
  "required_events": ["subscribe", "unsubscribe"]
}
```

### Implementation (Golang)

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "log"
    "net/http"
    "os"
    "time"

    ext "github.com/refractionPOINT/lc-extension"
)

func sendWebhook(url, message, severity string, metadata map[string]interface{}) error {
    payload := map[string]interface{}{
        "message":   message,
        "severity":  severity,
        "metadata":  metadata,
        "timestamp": time.Now().Unix(),
    }

    data, err := json.Marshal(payload)
    if err != nil {
        return fmt.Errorf("failed to marshal payload: %w", err)
    }

    resp, err := http.Post(url, "application/json", bytes.NewReader(data))
    if err != nil {
        return fmt.Errorf("failed to send webhook: %w", err)
    }
    defer resp.Body.Close()

    if resp.StatusCode != 200 {
        return fmt.Errorf("webhook returned status %d", resp.StatusCode)
    }

    return nil
}

func main() {
    e := ext.NewExtension(ext.Config{
        SharedSecret: os.Getenv("SHARED_SECRET"),
        Schema: &ext.Schema{
            // Schema defined above
        },
    })

    e.OnRequest("alert", func(ctx *ext.Context) (interface{}, error) {
        // Get configuration
        config, err := ctx.SDK.Hive().Get("extension_configuration", "alerter")
        if err != nil {
            return nil, fmt.Errorf("failed to get config: %w", err)
        }

        // Check if enabled
        enabled, _ := config["enabled"].(bool)
        if !enabled {
            return map[string]interface{}{
                "status": "disabled",
            }, nil
        }

        webhookURL := config["webhook_url"].(string)
        message := ctx.Params["message"].(string)
        severity := ctx.Params["severity"].(string)

        var metadata map[string]interface{}
        if m, ok := ctx.Params["metadata"]; ok {
            metadata, _ = m.(map[string]interface{})
        }

        // Send webhook
        err = sendWebhook(webhookURL, message, severity, metadata)
        if err != nil {
            return nil, fmt.Errorf("failed to send webhook: %w", err)
        }

        return map[string]interface{}{
            "status":    "sent",
            "timestamp": time.Now().Unix(),
        }, nil
    })

    e.OnEvent("subscribe", func(ctx *ext.Context) error {
        log.Printf("New subscription: %s", ctx.OID)
        return nil
    })

    e.OnEvent("unsubscribe", func(ctx *ext.Context) error {
        log.Printf("Unsubscribed: %s", ctx.OID)
        return nil
    })

    log.Fatal(e.Serve(":8080"))
}
```

### D&R Integration

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: malware.exe
respond:
  - action: extension request
    extension name: alerter
    extension action: alert
    extension request:
      message: 'Malware detected: {{ .event.FILE_PATH }}'
      severity: critical
      metadata:
        sid: '{{ .routing.sid }}'
        hostname: '{{ .routing.hostname }}'
```

## Scanning Extension with Tables

Extension that scans multiple sensors and displays results in a table.

### Schema

```json
{
  "layout": "action",
  "default_action": "scan",
  "config_schema": {
    "fields": {
      "scan_timeout": {
        "data_type": "integer",
        "description": "Scan timeout in seconds",
        "label": "Scan Timeout",
        "default_value": 60,
        "filter": {
          "min": 10,
          "max": 300
        }
      },
      "auto_remediate": {
        "data_type": "bool",
        "description": "Automatically remediate threats",
        "label": "Auto Remediate",
        "default_value": false
      }
    }
  },
  "request_schema": {
    "scan": {
      "is_impersonated": false,
      "is_user_facing": true,
      "short_description": "Scan sensors for threats",
      "long_description": "Performs security scans on specified sensors and returns findings in a structured format.",
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
                  "label": "Sensor",
                  "display_index": 1
                },
                "path": {
                  "data_type": "string",
                  "description": "Path to scan",
                  "label": "Path",
                  "placeholder": "/usr/bin",
                  "display_index": 2
                },
                "depth": {
                  "data_type": "integer",
                  "description": "Scan depth",
                  "label": "Depth",
                  "default_value": 3,
                  "filter": {
                    "min": 1,
                    "max": 10
                  },
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
                "path": {
                  "data_type": "string",
                  "description": "Scanned path"
                },
                "threats_found": {
                  "data_type": "integer",
                  "description": "Number of threats"
                },
                "status": {
                  "data_type": "enum",
                  "enum_values": ["clean", "infected", "error"],
                  "description": "Scan status"
                },
                "duration": {
                  "data_type": "integer",
                  "description": "Scan duration (seconds)"
                }
              }
            }
          },
          "summary": {
            "data_type": "object",
            "description": "Overall summary",
            "object": {
              "fields": {
                "total_scans": {
                  "data_type": "integer",
                  "description": "Total scans performed"
                },
                "threats_found": {
                  "data_type": "integer",
                  "description": "Total threats found"
                },
                "total_duration": {
                  "data_type": "integer",
                  "description": "Total duration (seconds)"
                }
              }
            }
          }
        },
        "supported_actions": ["remediate"]
      }
    },
    "remediate": {
      "is_impersonated": false,
      "is_user_facing": true,
      "short_description": "Remediate threats",
      "parameters": {
        "fields": {
          "results": {
            "data_type": "json",
            "description": "Scan results to remediate"
          }
        }
      }
    }
  },
  "required_events": ["subscribe"]
}
```

### Implementation (Golang)

```go
package main

import (
    "fmt"
    "log"
    "os"
    "sync"
    "time"

    ext "github.com/refractionPOINT/lc-extension"
)

type ScanTarget struct {
    SID   string `json:"sid"`
    Path  string `json:"path"`
    Depth int    `json:"depth"`
}

type ScanResult struct {
    SID          string `json:"sid"`
    Path         string `json:"path"`
    ThreatsFound int    `json:"threats_found"`
    Status       string `json:"status"`
    Duration     int    `json:"duration"`
}

func scanSensor(sdk interface{}, target ScanTarget) ScanResult {
    start := time.Now()

    // Simulate scanning logic
    time.Sleep(2 * time.Second)

    result := ScanResult{
        SID:          target.SID,
        Path:         target.Path,
        ThreatsFound: 0,
        Status:       "clean",
        Duration:     int(time.Since(start).Seconds()),
    }

    return result
}

func main() {
    e := ext.NewExtension(ext.Config{
        SharedSecret: os.Getenv("SHARED_SECRET"),
    })

    e.OnRequest("scan", func(ctx *ext.Context) (interface{}, error) {
        targets := ctx.Params["targets"].([]interface{})

        var wg sync.WaitGroup
        results := make([]ScanResult, len(targets))

        for i, t := range targets {
            wg.Add(1)
            go func(idx int, targetData interface{}) {
                defer wg.Done()

                targetMap := targetData.(map[string]interface{})
                target := ScanTarget{
                    SID:   targetMap["sid"].(string),
                    Path:  targetMap["path"].(string),
                    Depth: int(targetMap["depth"].(float64)),
                }

                results[idx] = scanSensor(ctx.SDK, target)
            }(i, t)
        }

        wg.Wait()

        // Calculate summary
        totalThreats := 0
        totalDuration := 0
        for _, r := range results {
            totalThreats += r.ThreatsFound
            totalDuration += r.Duration
        }

        return map[string]interface{}{
            "results": results,
            "summary": map[string]interface{}{
                "total_scans":    len(results),
                "threats_found":  totalThreats,
                "total_duration": totalDuration,
            },
        }, nil
    })

    e.OnRequest("remediate", func(ctx *ext.Context) (interface{}, error) {
        results := ctx.Params["results"]

        // Remediation logic
        log.Printf("Remediating threats from results: %v", results)

        return map[string]interface{}{
            "status": "remediated",
        }, nil
    })

    e.OnEvent("subscribe", func(ctx *ext.Context) error {
        log.Printf("New subscription: %s", ctx.OID)
        return nil
    })

    log.Fatal(e.Serve(":8080"))
}
```

## Multi-Action Extension

Extension with multiple related actions and complex workflows.

### Schema

```json
{
  "views": [
    {
      "name": "Detection",
      "layout": "action",
      "default_action": "detect"
    },
    {
      "name": "Response",
      "layout": "action",
      "default_action": "isolate"
    },
    {
      "name": "Configuration",
      "layout": "config"
    }
  ],
  "config_schema": {
    "fields": {
      "detection_threshold": {
        "data_type": "integer",
        "description": "Detection sensitivity threshold",
        "default_value": 5,
        "filter": {
          "min": 1,
          "max": 10
        }
      },
      "auto_respond": {
        "data_type": "bool",
        "description": "Automatically respond to threats",
        "default_value": false
      }
    }
  },
  "request_schema": {
    "detect": {
      "is_user_facing": true,
      "short_description": "Detect threats on sensor",
      "parameters": {
        "fields": {
          "sid": {
            "data_type": "sid",
            "description": "Target sensor"
          }
        },
        "requirements": [["sid"]]
      },
      "response": {
        "fields": {
          "threats": {
            "data_type": "json",
            "description": "Detected threats"
          },
          "severity": {
            "data_type": "enum",
            "enum_values": ["low", "medium", "high", "critical"]
          }
        },
        "supported_actions": ["isolate", "investigate"]
      }
    },
    "isolate": {
      "is_user_facing": true,
      "short_description": "Isolate sensor from network",
      "parameters": {
        "fields": {
          "sid": {
            "data_type": "sid",
            "description": "Sensor to isolate"
          },
          "reason": {
            "data_type": "string",
            "description": "Isolation reason"
          }
        },
        "requirements": [["sid"]]
      }
    },
    "investigate": {
      "is_user_facing": true,
      "short_description": "Launch investigation",
      "parameters": {
        "fields": {
          "threats": {
            "data_type": "json",
            "description": "Threats to investigate"
          },
          "scope": {
            "data_type": "enum",
            "enum_values": ["sensor", "organization", "global"],
            "default_value": "sensor"
          }
        }
      }
    }
  },
  "required_events": ["subscribe", "update"]
}
```

## D&R Rule Distribution

Use the simplified D&R framework to distribute detection rules.

### Implementation

```go
package main

import (
    "log"

    "github.com/refractionPOINT/lc-extension/simplified/dr"
)

func GetRules() map[string]map[string]string {
    return map[string]map[string]string{
        "malware-detection": {
            "ransomware-indicator": `
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: ends with
      path: event/FILE_PATH
      value: .exe
    - op: contains
      path: event/COMMAND_LINE
      value: encrypt
respond:
  - action: report
    name: Potential Ransomware Activity
  - action: task
    command: deny_tree
    investigation: ransomware-{{ .event.PROCESS_ID }}
`,
            "suspicious-powershell": `
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is
      path: event/FILE_PATH
      value: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
    - op: contains
      path: event/COMMAND_LINE
      case sensitive: false
      value: -encodedcommand
respond:
  - action: report
    name: Suspicious PowerShell Execution
  - action: add tag
    tag: suspicious-powershell
    ttl: 86400
`,
            "credential-dumping": `
detect:
  event: CODE_IDENTITY
  op: and
  rules:
    - op: is
      path: event/FILE_PATH
      case sensitive: false
      value: C:\Windows\System32\lsass.exe
    - op: exists
      path: event/MEMORY_ACCESS
respond:
  - action: report
    name: Potential Credential Dumping
    metadata:
      tactic: Credential Access
      technique: LSASS Memory
  - action: task
    command: mem_map
    process_id: <<routing/parent>>
`,
        },
        "network-monitoring": {
            "c2-beacon": `
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is
      path: event/STATE
      value: ESTABLISHED
    - op: lookup
      path: event/IP_ADDRESS
      resource: hive://lookup/threat-ips
respond:
  - action: report
    name: C2 Beacon Detected
  - action: extension request
    extension name: network-monitor
    extension action: block_ip
    extension request:
      ip: '{{ .event.IP_ADDRESS }}'
`,
            "dns-tunneling": `
detect:
  event: DNS_REQUEST
  op: and
  rules:
    - op: is
      path: event/DNS_TYPE
      value: TXT
    - op: length of
      path: event/DOMAIN_NAME
      length: 100
respond:
  - action: report
    name: Potential DNS Tunneling
`,
        },
    }
}

func main() {
    dr.Serve(dr.Config{
        GetRules: GetRules,
    })
}
```

## Lookup Distribution

Distribute threat intelligence lookups.

### Implementation

```go
package main

import (
    "log"

    "github.com/refractionPOINT/lc-extension/simplified/lookup"
)

func GetLookups() map[string][]string {
    return map[string][]string{
        "malware-domains": {
            "evil.com",
            "malicious.net",
            "badactor.org",
            "ransomware.biz",
            "phishing-site.info",
        },
        "threat-ips": {
            "1.2.3.4",
            "5.6.7.8",
            "10.20.30.40",
            "192.168.100.100",
        },
        "malware-hashes": {
            "44d88612fea8a8f36de82e1278abb02f",
            "d41d8cd98f00b204e9800998ecf8427e",
            "098f6bcd4621d373cade4e832627b4f6",
        },
        "known-good-hashes": {
            "aec070645fe53ee3b3763059376134f0",
            "c4ca4238a0b923820dcc509a6f75849b",
        },
    }
}

func main() {
    lookup.Serve(lookup.Config{
        GetLookups: GetLookups,
    })
}
```

### D&R Integration

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malware-domains
respond:
  - action: report
    name: Malicious Domain Accessed
```

## CLI Integration

Integrate external CLI tools with LimaCharlie.

### Nmap Integration Example

```go
package main

import (
    "encoding/json"
    "log"
    "regexp"
    "strings"

    "github.com/refractionPOINT/lc-extension/simplified/cli"
)

func parseNmapOutput(output string) (map[string]interface{}, error) {
    result := map[string]interface{}{
        "raw_output": output,
        "open_ports": []map[string]string{},
    }

    // Parse open ports
    portRegex := regexp.MustCompile(`(\d+)/(\w+)\s+open\s+(\w+)`)
    matches := portRegex.FindAllStringSubmatch(output, -1)

    for _, match := range matches {
        port := map[string]string{
            "port":     match[1],
            "protocol": match[2],
            "service":  match[3],
        }
        ports := result["open_ports"].([]map[string]string)
        result["open_ports"] = append(ports, port)
    }

    return result, nil
}

func main() {
    cli.Serve(cli.Config{
        CommandPath: "/usr/bin/nmap",
        CommandArgs: []string{
            "-sV",
            "-p", "{{.ports}}",
            "{{.target}}",
        },
        OutputParser: parseNmapOutput,
    })
}
```

### Schema for CLI Extension

```json
{
  "request_schema": {
    "scan_network": {
      "is_user_facing": true,
      "short_description": "Scan network target with Nmap",
      "parameters": {
        "fields": {
          "target": {
            "data_type": "string",
            "description": "Target IP or hostname",
            "label": "Target"
          },
          "ports": {
            "data_type": "string",
            "description": "Port range to scan",
            "label": "Ports",
            "default_value": "1-1000",
            "placeholder": "1-1000 or 22,80,443"
          }
        },
        "requirements": [["target"]]
      }
    }
  }
}
```

## Complex Configuration Extension

Extension with advanced configuration including nested objects and records.

### Schema

```json
{
  "layout": "config",
  "config_schema": {
    "fields": {
      "general": {
        "data_type": "object",
        "is_list": false,
        "description": "General settings",
        "label": "General",
        "object": {
          "fields": {
            "enabled": {
              "data_type": "bool",
              "description": "Enable extension",
              "default_value": true
            },
            "log_level": {
              "data_type": "enum",
              "enum_values": ["debug", "info", "warning", "error"],
              "default_value": "info"
            }
          }
        }
      },
      "api_endpoints": {
        "data_type": "object",
        "is_list": true,
        "description": "API endpoints for integrations",
        "label": "API Endpoints",
        "object": {
          "fields": {
            "name": {
              "data_type": "string",
              "description": "Endpoint name",
              "display_index": 1
            },
            "url": {
              "data_type": "url",
              "description": "Endpoint URL",
              "display_index": 2
            },
            "api_key": {
              "data_type": "secret",
              "description": "API key",
              "display_index": 3
            },
            "timeout": {
              "data_type": "integer",
              "description": "Request timeout (seconds)",
              "default_value": 30,
              "filter": {
                "min": 5,
                "max": 300
              },
              "display_index": 4
            }
          },
          "requirements": [["name"], ["url"], ["api_key"]]
        }
      },
      "filters": {
        "data_type": "record",
        "is_list": true,
        "description": "Custom filters",
        "label": "Filters",
        "object": {
          "key": {
            "name": "filter_name",
            "data_type": "string"
          },
          "element_name": "filter",
          "element_desc": "A custom filter rule",
          "fields": {
            "pattern": {
              "data_type": "string",
              "description": "Filter pattern (regex)"
            },
            "action": {
              "data_type": "enum",
              "enum_values": ["allow", "block", "alert"],
              "default_value": "alert"
            },
            "enabled": {
              "data_type": "bool",
              "default_value": true
            }
          },
          "requirements": [["pattern"], ["action"]]
        }
      },
      "advanced_config": {
        "data_type": "yaml",
        "description": "Advanced YAML configuration",
        "label": "Advanced Config",
        "default_value": "# Add custom configuration here\n"
      }
    },
    "requirements": [["general"]]
  },
  "request_schema": {
    "test_config": {
      "is_user_facing": true,
      "short_description": "Test configuration",
      "parameters": {
        "fields": {}
      }
    }
  },
  "required_events": ["subscribe"]
}
```

### Implementation

```go
package main

import (
    "fmt"
    "log"
    "os"

    ext "github.com/refractionPOINT/lc-extension"
)

func main() {
    e := ext.NewExtension(ext.Config{
        SharedSecret: os.Getenv("SHARED_SECRET"),
    })

    e.OnConfigValidation(func(config map[string]interface{}) error {
        // Validate general settings
        general, ok := config["general"].(map[string]interface{})
        if !ok {
            return fmt.Errorf("general settings required")
        }

        // Validate API endpoints
        if endpoints, ok := config["api_endpoints"].([]interface{}); ok {
            for i, ep := range endpoints {
                endpoint := ep.(map[string]interface{})

                name, _ := endpoint["name"].(string)
                if name == "" {
                    return fmt.Errorf("endpoint %d: name required", i)
                }

                url, _ := endpoint["url"].(string)
                if url == "" {
                    return fmt.Errorf("endpoint %s: url required", name)
                }
            }
        }

        return nil
    })

    e.OnRequest("test_config", func(ctx *ext.Context) (interface{}, error) {
        config, err := ctx.SDK.Hive().Get("extension_configuration", "my-ext")
        if err != nil {
            return nil, err
        }

        return map[string]interface{}{
            "status": "valid",
            "config": config,
        }, nil
    })

    e.OnEvent("subscribe", func(ctx *ext.Context) error {
        // Initialize default configuration
        defaultConfig := map[string]interface{}{
            "general": map[string]interface{}{
                "enabled":   true,
                "log_level": "info",
            },
            "api_endpoints": []interface{}{},
            "filters":       map[string]interface{}{},
        }

        return ctx.SDK.Hive().Set("extension_configuration", "my-ext", defaultConfig)
    })

    log.Fatal(e.Serve(":8080"))
}
```

## Best Practices Demonstrated

All examples above demonstrate:

1. **Security**: Signature verification, input validation, secrets management
2. **Error Handling**: Meaningful error messages, graceful degradation
3. **Performance**: Async operations for long tasks, efficient data structures
4. **User Experience**: Clear descriptions, sensible defaults, helpful UI
5. **Configuration**: Validation callbacks, default values, requirements
6. **SDK Usage**: Proper authentication, permission scoping, resource management

Use these examples as templates for your own extensions, adapting them to your specific use cases.
