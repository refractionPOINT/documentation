# Detection and Response

Build custom detection logic with automated response actions to protect your infrastructure.

## Overview

LimaCharlie's Detection & Response (D&R) rules enable you to:

- Detect threats in real-time using event-driven logic
- Automate response actions (isolate, terminate, collect artifacts)
- Create custom detections tailored to your environment
- Leverage community-contributed detection rules

## Core Components

### Detection

Detection rules use operators and path selectors to identify suspicious activity:

- Event-based triggers (NEW_PROCESS, NETWORK_CONNECTIONS, etc.)
- Powerful operators (contains, matches, regex, etc.)
- Nested logic with AND/OR conditions
- False positive filtering

### Response

Automated response actions include:

- **report**: Generate a detection alert
- **task**: Execute sensor commands (isolate, terminate, dump memory)
- **add tag**: Apply tags for tracking and targeting
- **remove tag**: Remove tags dynamically
- **service request**: Trigger external integrations

## Documentation

- [Detection & Response Rules](detection-and-response-rules.md) - Complete rule syntax and capabilities
- [Examples](detection-and-response-examples.md) - Real-world detection rule examples
- [Alternate Targets](detection-on-alternate-targets.md) - Detections beyond endpoint events

## Quick Example

```yaml
# Detection
op: ends with
event: NEW_PROCESS
path: event/FILE_PATH
value: .scr
case sensitive: false

# Response
- action: report
  name: suspicious_screensaver
- action: task
  command: history_dump
```

## Getting Started

1. Review [detection rule examples](detection-and-response-examples.md)
2. Understand the [rule syntax](detection-and-response-rules.md)
3. Test rules in your environment
4. Leverage managed rulesets for common threats
