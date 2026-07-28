# Human-in-the-Loop Response Automation

This tutorial builds a workflow that detects a credential dumping tool. The workflow asks a SOC analyst for approval before it isolates the host, then does the response with a Python playbook. It shows how D&R rules, the [Feedback extension](../extensions/limacharlie/feedback.md), and [Playbooks](../extensions/limacharlie/playbook.md) work together for human-in-the-loop security automation.

## What You Will Build

```text
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

**Reason for human-in-the-loop:** Automated isolation works, but it interrupts users. A sysadmin who runs a legitimate tool on a server, or a red team engagement, can trigger credential-tool detections. A question to a human before the isolation stops costly interruptions from false positives. The response is still fast when the threat is real.

## Prerequisites

Subscribe to these extensions in the [LimaCharlie marketplace](https://app.limacharlie.io/add-ons):

- **Feedback** (`ext-feedback`) -- delivers approval requests and collects responses
- **Playbook** (`ext-playbook`) -- runs Python playbooks

You also need a [Slack Tailored Output](../outputs/destinations/slack.md) that has a `slack_api_token` and a `slack_channel`. To create a Slack App with interactivity enabled, see [Feedback Slack Setup](../extensions/limacharlie/feedback.md#slack-setup).

!!! tip "No Slack?"
    You can use any channel type ([Telegram](../extensions/limacharlie/feedback.md#telegram-setup), [Microsoft Teams](../extensions/limacharlie/feedback.md#microsoft-teams-setup), [email](../extensions/limacharlie/feedback.md#email-setup), or `web`). Replace the channel type in Step 1. The D&R rule, the playbook, and the response flow are the same for each channel.

## Step 1: Create a Feedback Channel

Add a Slack channel to the Feedback extension config. The channel tells ext-feedback where to deliver approval requests.

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

Check that the channel exists:

```bash
limacharlie feedback channel list
```

## Step 2: Write the D&R Rule

This rule detects credential dumping tools and asks a human for approval before it acts. The response goes to a playbook that isolates the host or monitors it.

### Detection

The detection matches a process with a file path that ends with the name of a known credential dumping tool:

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
    This detection is simplified for the example. A production rule includes more context, such as command-line arguments that target `lsass`, hash lookups, or behavioral patterns.

### Response

The response has two actions: it reports the detection, and it requests approval through ext-feedback.

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
    timeout_seconds: 600
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

- **Suppression** stops the same host from sending too many messages to the Slack channel. The key is the hostname, so each host sends a maximum of one approval request each hour. Without suppression, a noisy process that restarts many times creates dozens of Slack messages.
- **Timeout** denies the request automatically after 10 minutes. The playbook still runs at the timeout (with `responder: "timeout"`), so the host is tagged for monitoring even if nobody watches Slack.
- **`approved_content` / `denied_content`** carry the sensor ID and the hostname through the human decision. The playbook then has all the data that it needs to act, and it makes no more API calls to look up the sensor.

## Step 3: Create the Playbook

Create a playbook named `handle-isolation-decision` in the Playbooks section (Automation > Playbooks in the web app), or with Infrastructure as Code.

The playbook receives the feedback response. It isolates the host or tags it for monitoring.

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

When ext-feedback sends the response to a playbook, the `data` parameter contains:

| Field | Description |
|-------|-------------|
| `request_id` | UUID of the feedback request |
| `question` | The original question text |
| `choice` | `approved` or `denied` |
| `responder` | Username of the person who responded, or `"timeout"` |
| `content` | The JSON from `approved_content` or `denied_content` (whichever matches the choice) |

The `content` field holds the context from the D&R rule: the sensor ID, the hostname, and the file path. For this reason, `approved_content` and `denied_content` in the D&R rule include `sid` and `hostname`. These values move through the feedback system and arrive intact in the playbook.

### Infrastructure as Code

To manage the playbook with [git-sync](../extensions/limacharlie/git-sync.md):

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
    The playbook needs an API key with `sensor.set` permissions for isolation and tagging. When you trigger the playbook from a D&R rule, give the credentials in the `credentials` field. You can also configure the playbook extension with a default API key.

## Step 4: Test the Workflow

To test the full flow without a real detection, send a feedback request from the CLI:

```bash
limacharlie feedback request-approval \
  --channel soc-approvals \
  --question "TEST: Credential dumping tool detected on workstation-42. Isolate this host?" \
  --destination playbook --playbook handle-isolation-decision \
  --approved-content '{"sid": "YOUR_SENSOR_SID", "hostname": "workstation-42", "file_path": "C:\\tools\\mimikatz.exe", "action": "isolate"}' \
  --denied-content '{"sid": "YOUR_SENSOR_SID", "hostname": "workstation-42", "file_path": "C:\\tools\\mimikatz.exe", "action": "monitor"}' \
  --timeout 120 --timeout-choice denied
```

Replace `YOUR_SENSOR_SID` with a real sensor ID from your organization. After you run this command:

1. A message appears in your Slack channel with **Approve** and **Deny** buttons
2. Click **Approve** -- the `handle-isolation-decision` playbook runs and isolates the sensor
3. Click **Deny** -- the playbook tags the sensor with `cred-tool-monitor` for 24 hours

To test without a change to a real sensor, use the `web` channel. It gives you a URL that you can open in a browser:

```bash
limacharlie feedback channel add --name test-web --type web

limacharlie feedback request-approval \
  --channel test-web \
  --question "TEST: Isolate workstation-42?" \
  --destination playbook --playbook handle-isolation-decision \
  --approved-content '{"sid": "test-sid", "hostname": "workstation-42", "file_path": "mimikatz.exe", "action": "isolate"}' \
  --denied-content '{"sid": "test-sid", "hostname": "workstation-42", "file_path": "mimikatz.exe", "action": "monitor"}'
```

The CLI returns a `url` that you can open in your browser to respond.

## How It All Fits Together

1. A `NEW_PROCESS` event fires when mimikatz.exe runs on an endpoint
2. The D&R rule matches and sends a `request_simple_approval` to ext-feedback
3. Suppression checks if this host already has a pending request (keyed on hostname, 1-hour window) -- if it does, the action is skipped
4. ext-feedback delivers the question to Slack with Approve/Deny buttons
5. A SOC analyst clicks **Approve** (or the 10-minute timeout fires and auto-denies)
6. ext-feedback routes the response through the webhook adapter and D&R pipeline
7. The `handle-isolation-decision` playbook runs with the analyst's choice and the event context
8. The playbook isolates the host (if approved) or tags it for monitoring (if denied/timed out)

## Extending the Pattern

**Escalation chain:** When the timeout occurs, let the playbook send a second feedback request to a different channel, such as `management-approvals`. Give this second request a shorter timeout before the automatic isolation.

**Multi-step workflow:** Chain many feedback requests. For example, after the approval of the isolation, ask "Run memory forensics on this host?". Send the response to a second playbook that starts a [Velociraptor](../extensions/third-party/velociraptor.md) or [Dumper](../extensions/limacharlie/dumper.md) collection.

**Audit trail:** Set the feedback destination to `case` instead of `playbook`. Each approval decision becomes a case note, which gives you an audit trail that you can review.

**AI agent follow-up:** Set the feedback destination to `ai_agent` to start an AI agent session when the human responds. The agent gets the feedback response at the end of its prompt. The agent can then take automated action that uses the context of the human decision.
