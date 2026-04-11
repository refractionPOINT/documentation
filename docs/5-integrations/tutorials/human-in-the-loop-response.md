# Human-in-the-Loop Response Automation

This tutorial walks through building an end-to-end workflow that detects a credential dumping tool, asks a SOC analyst for approval before isolating the host, and executes the response via a Python playbook. It demonstrates how D&R rules, the [Feedback extension](../extensions/limacharlie/feedback.md), and [Playbooks](../extensions/labs/playbook.md) work together to implement human-in-the-loop security automation.

## What You Will Build

```
NEW_PROCESS event (mimikatz.exe)
        |
        v
  D&R rule detects it
        |
        v
  ext-feedback sends approval
  request to Slack channel
  (suppressed per-host per-hour)
        |
        v
  Analyst clicks Approve or Deny
  (auto-denied after 10 minutes)
        |
        v
  Playbook receives the response
        |
    +---+---+
    |       |
 Approved  Denied
    |       |
 Isolate   Tag host
 the host  for monitoring
```

**Why human-in-the-loop?** Automated isolation is effective but disruptive. A sysadmin running a legitimate tool on a server, or a red team engagement, can trigger credential-tool detections. Asking a human before isolating avoids costly false-positive disruptions while still ensuring fast response when the threat is real.

## Prerequisites

Subscribe to the following extensions in the [LimaCharlie marketplace](https://app.limacharlie.io/add-ons):

- **Feedback** (`ext-feedback`) -- delivers approval requests and collects responses
- **Playbook** (`ext-playbook`) -- executes Python playbooks

You also need a [Slack Tailored Output](../outputs/destinations/slack.md) configured with a `slack_api_token` and `slack_channel`. See [Feedback Slack Setup](../extensions/limacharlie/feedback.md#slack-setup) for details on creating a Slack App with interactivity enabled.

!!! tip "No Slack?"
    You can use any channel type ([Telegram](../extensions/limacharlie/feedback.md#telegram-setup), [Microsoft Teams](../extensions/limacharlie/feedback.md#microsoft-teams-setup), [email](../extensions/limacharlie/feedback.md#email-setup), or `web`). Replace the channel type in Step 1 accordingly. The D&R rule, playbook, and response flow are identical regardless of channel.

## Step 1: Create a Feedback Channel

Add a Slack channel to the Feedback extension config. This tells ext-feedback where to deliver approval requests.

=== "CLI"
    ```bash
    limacharlie feedback channel add \
      --name soc-approvals \
      --type slack \
      --output-name my-slack-output
    ```

=== "Infrastructure as Code"
    ```yaml
    version: 3
    hives:
      extension_config:
        ext-feedback:
          data:
            channels:
              - name: soc-approvals
                channel_type: slack
                output_name: my-slack-output
          usr_mtd:
            enabled: true
            expiry: 0
            tags: []
            comment: ""
    ```

Verify the channel was created:

```bash
limacharlie feedback channel list
```

## Step 2: Write the D&R Rule

This rule detects credential dumping tools and asks for human approval before taking action. The response is routed to a playbook that handles isolation or monitoring.

### Detection

The detection matches processes whose file path ends with known credential dumping tool names:

```yaml
op: or
rules:
  - op: ends with
    event: NEW_PROCESS
    path: event/FILE_PATH
    value: mimikatz.exe
    case sensitive: false
  - op: ends with
    event: NEW_PROCESS
    path: event/FILE_PATH
    value: procdump.exe
    case sensitive: false
  - op: ends with
    event: NEW_PROCESS
    path: event/FILE_PATH
    value: pypykatz.exe
    case sensitive: false
```

!!! note
    This is a simplified detection for illustration. Production rules would include additional context (e.g., command-line arguments targeting `lsass`, hash lookups, or behavioral patterns).

### Response

The response has two actions: report the detection, and request approval via ext-feedback.

```yaml
- action: report
  name: cred-tool-detected - {{ .routing.hostname }}

- action: extension request
  extension name: ext-feedback
  extension action: request_simple_approval
  extension request:
    channel: '{{ "soc-approvals" }}'
    question: '{{ "Credential dumping tool detected on " }}{{ .routing.hostname }}{{ " (process: " }}{{ base .event.FILE_PATH }}{{ "). Isolate this host?" }}'
    feedback_destination: '{{ "playbook" }}'
    playbook_name: '{{ "handle-isolation-decision" }}'
    approved_content:
      sid: routing.sid
      hostname: routing.hostname
      file_path: event.FILE_PATH
      action: '{{ "isolate" }}'
    denied_content:
      sid: routing.sid
      hostname: routing.hostname
      file_path: event.FILE_PATH
      action: '{{ "monitor" }}'
    timeout_seconds: '{{ 600 }}'
    timeout_choice: '{{ "denied" }}'
  suppression:
    max_count: 1
    period: 1h
    is_global: false
    keys:
      - 'cred-tool-isolation'
      - '{{ .routing.hostname }}'
```

**Key design decisions:**

- **Suppression** prevents the same host from flooding the Slack channel. Keyed on hostname, it ensures at most one approval request per host per hour. Without this, a noisy process restarting repeatedly would generate dozens of Slack messages.
- **Timeout** auto-denies after 10 minutes. The playbook still runs on timeout (with `responder: "timeout"`), so the host gets tagged for monitoring even if no one is watching Slack.
- **`approved_content` / `denied_content`** carry the sensor ID and hostname through the human decision point, so the playbook has everything it needs to act without additional API calls to look up the sensor.

## Step 3: Create the Playbook

Create a playbook named `handle-isolation-decision` in the Playbooks section (Automation > Playbooks in the web UI), or via Infrastructure as Code.

This playbook receives the feedback response and either isolates the host or tags it for monitoring.

### Playbook Code

```python
from limacharlie.Sensor import Sensor

def playbook(sdk, data):
    if not sdk:
        return {"error": "credentials required"}

    content = data.get("content", {})
    choice = data.get("choice")
    responder = data.get("responder")
    action = content.get("action")
    sid = content.get("sid")
    hostname = content.get("hostname", "unknown")
    file_path = content.get("file_path", "unknown")

    if not sid:
        return {"error": "no sensor ID in response content"}

    sensor = Sensor(sdk, sid)

    if action == "isolate":
        # Isolate the host from the network.
        sensor.isolateNetwork()

        # Generate a detection so this shows up in the Detections view.
        return {
            "data": {
                "action": "isolated",
                "hostname": hostname,
                "approved_by": responder,
            },
            "detection": {
                "summary": f"Host {hostname} isolated after cred-tool detection (approved by {responder})",
                "sid": sid,
                "hostname": hostname,
                "file_path": file_path,
            },
            "cat": "Credential-Tool-Host-Isolated",
        }
    else:
        # Tag the host for enhanced monitoring instead of isolating.
        sensor.tag("cred-tool-monitor", ttl=86400)

        return {
            "data": {
                "action": "monitoring",
                "hostname": hostname,
                "decided_by": responder,
                "reason": "denied" if choice == "denied" else "timeout",
            },
        }
```

### What the Playbook Receives

When ext-feedback dispatches to a playbook, the `data` parameter contains:

| Field | Description |
|-------|-------------|
| `request_id` | UUID of the feedback request |
| `question` | The original question text |
| `choice` | `approved` or `denied` |
| `responder` | Username of the person who responded, or `"timeout"` |
| `content` | The JSON from `approved_content` or `denied_content` (whichever matches the choice) |

The `content` field is where the D&R rule's context (sensor ID, hostname, file path) arrives. This is why the `approved_content` and `denied_content` in the D&R rule include `sid` and `hostname` -- they travel through the feedback system and arrive intact in the playbook.

### Infrastructure as Code

To manage the playbook via [git-sync](../extensions/limacharlie/git-sync.md):

```yaml
hives:
  playbook:
    handle-isolation-decision:
      data:
        python: |-
          from limacharlie.Sensor import Sensor

          def playbook(sdk, data):
              if not sdk:
                  return {"error": "credentials required"}

              content = data.get("content", {})
              choice = data.get("choice")
              responder = data.get("responder")
              action = content.get("action")
              sid = content.get("sid")
              hostname = content.get("hostname", "unknown")
              file_path = content.get("file_path", "unknown")

              if not sid:
                  return {"error": "no sensor ID in response content"}

              sensor = Sensor(sdk, sid)

              if action == "isolate":
                  sensor.isolateNetwork()
                  return {
                      "data": {
                          "action": "isolated",
                          "hostname": hostname,
                          "approved_by": responder,
                      },
                      "detection": {
                          "summary": f"Host {hostname} isolated after cred-tool detection (approved by {responder})",
                          "sid": sid,
                          "hostname": hostname,
                          "file_path": file_path,
                      },
                      "cat": "Credential-Tool-Host-Isolated",
                  }
              else:
                  sensor.tag("cred-tool-monitor", ttl=86400)
                  return {
                      "data": {
                          "action": "monitoring",
                          "hostname": hostname,
                          "decided_by": responder,
                          "reason": "denied" if choice == "denied" else "timeout",
                      },
                  }
      usr_mtd:
        enabled: true
        expiry: 0
        tags: []
        comment: "Handles isolation decisions from ext-feedback approval requests"
```

!!! warning
    The playbook needs an API key with `sensor.set` permissions (for isolation and tagging). When triggering the playbook from a D&R rule, pass credentials via the `credentials` field, or configure the playbook extension with a default API key.

## Step 4: Test the Workflow

You can test the full flow without waiting for a real detection by sending a feedback request directly from the CLI:

```bash
limacharlie feedback request-approval \
  --channel soc-approvals \
  --question "TEST: Credential dumping tool detected on workstation-42. Isolate this host?" \
  --destination playbook --playbook handle-isolation-decision \
  --approved-content '{"sid": "YOUR_SENSOR_SID", "hostname": "workstation-42", "file_path": "C:\\tools\\mimikatz.exe", "action": "isolate"}' \
  --denied-content '{"sid": "YOUR_SENSOR_SID", "hostname": "workstation-42", "file_path": "C:\\tools\\mimikatz.exe", "action": "monitor"}' \
  --timeout 120 --timeout-choice denied
```

Replace `YOUR_SENSOR_SID` with a real sensor ID from your organization. After running this command:

1. A message appears in your Slack channel with **Approve** and **Deny** buttons
2. Click **Approve** -- the `handle-isolation-decision` playbook runs and isolates the sensor
3. Click **Deny** -- the playbook tags the sensor with `cred-tool-monitor` for 24 hours

If you want to test without affecting a real sensor, use the `web` channel instead to get a URL you can open in a browser:

```bash
limacharlie feedback channel add --name test-web --type web

limacharlie feedback request-approval \
  --channel test-web \
  --question "TEST: Isolate workstation-42?" \
  --destination playbook --playbook handle-isolation-decision \
  --approved-content '{"sid": "test-sid", "hostname": "workstation-42", "file_path": "mimikatz.exe", "action": "isolate"}' \
  --denied-content '{"sid": "test-sid", "hostname": "workstation-42", "file_path": "mimikatz.exe", "action": "monitor"}'
```

The CLI returns a `url` you can open in your browser to respond.

## How It All Fits Together

1. A `NEW_PROCESS` event fires when mimikatz.exe runs on an endpoint
2. The D&R rule matches and sends a `request_simple_approval` to ext-feedback
3. Suppression checks whether this host already has a pending request (keyed on hostname, 1-hour window) -- if so, the action is skipped
4. ext-feedback delivers the question to Slack with Approve/Deny buttons
5. A SOC analyst clicks **Approve** (or the 10-minute timeout fires and auto-denies)
6. ext-feedback routes the response through the webhook adapter and D&R pipeline
7. The `handle-isolation-decision` playbook runs with the analyst's choice and the event context
8. The playbook isolates the host (if approved) or tags it for monitoring (if denied/timed out)

## Extending the Pattern

**Escalation chain:** If the timeout fires, have the playbook send a second feedback request to a different channel (e.g., `management-approvals`) with a shorter timeout before auto-isolating.

**Multi-step workflow:** Chain multiple feedback requests. For example, after isolation approval, ask "Run memory forensics on this host?" with the response going to a second playbook that triggers [Velociraptor](../extensions/third-party/velociraptor.md) or a [Dumper](../extensions/limacharlie/dumper.md) collection.

**Audit trail:** Set the feedback destination to `case` instead of `playbook` to log every approval decision as a case note, creating a reviewable audit trail.

**AI agent follow-up:** Set the feedback destination to `ai_agent` to start an AI agent session when the human responds. The agent receives the feedback response appended to its prompt, allowing it to take context-aware automated action based on the human's decision.
