# Feedback

The Feedback extension enables interactive feedback requests across external channels. It sends approval/denial prompts or questions to Slack channels or a built-in web UI, collects responses, and dispatches them to LimaCharlie subsystems (case notes via ext-cases, playbook triggers via ext-playbook).

Designed for AI-driven and human-initiated workflows where operator approval or input is required before taking an automated action. For example, a D&R rule or playbook can ask a human "Should we isolate host compromised-01?" and wait for a response before proceeding.

## Enabling the Extension

Navigate to the [Feedback extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-feedback) in the marketplace. Select the organization you wish to enable it for, and select **Subscribe**.

On subscription, the extension automatically:

1. Creates a webhook adapter for the organization
2. Installs a D&R rule that routes feedback responses to the extension for processing

No additional configuration is required. You can immediately start creating channels and sending feedback requests.

## Concepts

### Channels

A **channel** defines how feedback requests are delivered to respondents. Each channel has a name and a type.

| Channel Type | Description | Requirements |
|-------------|-------------|--------------|
| `default` | Built-in web UI. Returns a shareable URL that displays the question with response buttons. No external setup needed. | None |
| `slack` | Sends an interactive Block Kit message to a Slack channel with Approve/Deny or Acknowledge buttons. | A LimaCharlie [Tailored Output](../../../3-detection-response/outputs.md) with `slack_api_token` and `slack_channel` configured |

### Feedback Types

| Feedback Type | Buttons | Response Values |
|--------------|---------|-----------------|
| `simple_approval` | **Approve** and **Deny** | `approved` or `denied` |
| `question` | **Acknowledge** | `acknowledged` |

### Feedback Destinations

When a respondent clicks a button, the extension dispatches the response to the configured destination:

| Destination | Behavior |
|-------------|----------|
| `case` | Adds a note to the specified case via ext-cases. Requires a `case_id`. |
| `playbook` | Triggers the specified playbook via ext-playbook with the response data. Requires a `playbook_name`. |

### Response Content

Each feedback request can include optional JSON data per choice. When the respondent selects a choice, the corresponding content is included in the dispatched response. This allows automation to carry structured payloads through the human decision point.

For `simple_approval`, use `approved_content` and `denied_content`. For `question`, use `acknowledged_content`.

## Channel Management

### Create a Channel

=== "CLI"
    ```bash
    # Default channel (web UI)
    limacharlie extension request \
      --name ext-feedback \
      --action set_channel \
      --data '{"name":"approvals","channel_type":"default"}'

    # Slack channel (requires a Tailored Output with Slack credentials)
    limacharlie extension request \
      --name ext-feedback \
      --action set_channel \
      --data '{"name":"ops-slack","channel_type":"slack","output_name":"slack-ops"}'
    ```

=== "D&R Rule"
    ```yaml
    - action: extension request
      extension name: ext-feedback
      extension action: set_channel
      extension request:
        name: '{{ "approvals" }}'
        channel_type: '{{ "default" }}'
    ```

### List Channels

=== "CLI"
    ```bash
    limacharlie extension request \
      --name ext-feedback \
      --action list_channels
    ```

### Delete a Channel

=== "CLI"
    ```bash
    limacharlie extension request \
      --name ext-feedback \
      --action delete_channel \
      --data '{"name":"approvals"}'
    ```

## Sending Feedback Requests

The `request_feedback` action sends a question to a channel and returns a `request_id`. When a respondent answers, the response is dispatched to the configured destination.

### Simple Approval via Default Channel

=== "CLI"
    ```bash
    limacharlie extension request \
      --name ext-feedback \
      --action request_feedback \
      --data '{
        "channel": "approvals",
        "question": "Should we isolate host compromised-01?",
        "feedback_type": "simple_approval",
        "feedback_destination": "case",
        "case_id": "78",
        "approved_content": "{\"action\": \"isolate\", \"sid\": \"sensor-abc\"}",
        "denied_content": "{\"action\": \"skip\"}"
      }'
    ```

The response includes:

```json
{
  "request_id": "a1b2c3d4-...",
  "url": "https://feedback-system.limacharlie.io/r/a1b2c3d4-..."
}
```

The `url` is the shareable link to the web UI where the respondent can answer. For Slack channels, no URL is returned -- the message is sent directly to the Slack channel.

### D&R Rule Example

A D&R rule can request human approval before taking automated action. The response is dispatched to a playbook that performs the action.

**Detection:**
```yaml
op: is
event: NEW_PROCESS
path: event/FILE_PATH
value: /usr/bin/suspicious-tool
```

**Response:**
```yaml
- action: extension request
  extension name: ext-feedback
  extension action: request_feedback
  extension request:
    channel: '{{ "ops-slack" }}'
    question: '{{ "Suspicious process detected on " }}{{ .routing.hostname }}{{ ". Isolate host?" }}'
    feedback_type: '{{ "simple_approval" }}'
    feedback_destination: '{{ "playbook" }}'
    playbook_name: '{{ "isolate-host" }}'
    approved_content:
      action: '{{ "isolate" }}'
      sid: routing.sid
    denied_content:
      action: '{{ "monitor" }}'
      sid: routing.sid
```

### Playbook Example

A playbook can request approval during execution:

```python
def main(lc, data):
    import json

    # Request human approval
    response = lc.extension_request(
        "ext-feedback",
        "request_feedback",
        {
            "channel": "approvals",
            "question": f"Isolate host {data.get('hostname', 'unknown')}?",
            "feedback_type": "simple_approval",
            "feedback_destination": "playbook",
            "playbook_name": "handle-isolation-response",
            "approved_content": json.dumps({"action": "isolate", "sid": data.get("sid")}),
            "denied_content": json.dumps({"action": "skip"}),
        },
    )

    # The response will trigger the handle-isolation-response playbook
    # when the human responds.
    return {"request_id": response.get("request_id")}
```

## Response Flow

1. A feedback request is created and stored with a 7-day TTL
2. The question is delivered via the configured channel (Slack message or web URL)
3. The respondent clicks a button
4. The response is routed through the organization's webhook adapter
5. A D&R rule matches the response event and triggers the extension's `process_response` action
6. The extension atomically claims the request (preventing duplicate processing) and dispatches the response to the configured destination

Feedback requests expire after **7 days**. Expired requests show an error in the web UI and are rejected by the extension.

Responses are protected against replay: once a response is processed, any duplicate deliveries (from webhook retries or replay) are rejected.

## Slack Setup

To use Slack channels:

1. Create a Slack App with "Interactivity & Shortcuts" enabled
2. Set the Request URL to the Slack callback endpoint: `https://feedback-system.limacharlie.io/callback/slack`
3. Install the app to your Slack workspace and note the Bot User OAuth Token
4. In LimaCharlie, create a [Tailored Output](../../../3-detection-response/outputs.md) with:
    - `slack_api_token`: the Bot User OAuth Token
    - `slack_channel`: the target channel (e.g. `#security-ops`)
5. Create a feedback channel referencing the output name:
    ```bash
    limacharlie extension request \
      --name ext-feedback \
      --action set_channel \
      --data '{"name":"ops","channel_type":"slack","output_name":"my-slack-output"}'
    ```

## Actions Reference

| Action | User-facing | Description |
|--------|:-----------:|-------------|
| `set_channel` | Yes | Create or update a feedback channel |
| `delete_channel` | Yes | Delete a feedback channel |
| `list_channels` | Yes | List all feedback channels for the organization |
| `request_feedback` | Yes | Send a feedback request to a channel |
| `process_response` | No | Internal: processes a response received via webhook |

### request_feedback Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `channel` | Yes | Name of the feedback channel |
| `question` | Yes | The question or prompt to present |
| `feedback_type` | Yes | `simple_approval` or `question` |
| `feedback_destination` | Yes | `case` or `playbook` |
| `case_id` | When destination is `case` | Case to add the response note to |
| `playbook_name` | When destination is `playbook` | Playbook to trigger with the response |
| `approved_content` | No | JSON data included when the respondent approves (simple_approval) |
| `denied_content` | No | JSON data included when the respondent denies (simple_approval) |
| `acknowledged_content` | No | JSON data included when the respondent acknowledges (question) |
