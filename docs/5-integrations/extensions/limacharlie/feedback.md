# Feedback

The Feedback extension enables interactive feedback requests across external channels. It sends approval/denial prompts, acknowledgement requests, or free-form questions to Slack channels or a built-in web UI, collects responses, and dispatches them to LimaCharlie subsystems (case notes via ext-cases, playbook triggers via ext-playbook).

Designed for AI-driven and human-initiated workflows where operator approval or input is required before taking an automated action. For example, a D&R rule or playbook can ask a human "Should we isolate host compromised-01?" and wait for a response before proceeding.

## Enabling the Extension

Navigate to the [Feedback extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-feedback) in the marketplace. Select the organization you wish to enable it for, and select **Subscribe**.

On subscription, the extension automatically:

1. Creates a webhook adapter for the organization
2. Installs a D&R rule that routes feedback responses to the extension for processing

No additional configuration is required. You can immediately start configuring channels and sending feedback requests.

## Concepts

### Channels

A **channel** defines how feedback requests are delivered to respondents. Each channel has a name and a type. Channels are configured through the extension config (see [Channel Configuration](#channel-configuration)).

| Channel Type | Description | Requirements |
|-------------|-------------|--------------|
| `web` | Built-in web UI. Returns a shareable URL that displays the question with response buttons or text input. No external setup needed. | None |
| `slack` | Sends an interactive Block Kit message to a Slack channel with action buttons. For question-type requests, a "Respond" button links to the web UI since Slack does not support inline text input. | A LimaCharlie [Tailored Output](../../../3-detection-response/outputs.md) with `slack_api_token` and `slack_channel` configured |

### Feedback Types

Each feedback type has a dedicated action:

| Feedback Type | Action | UI | Response Values |
|--------------|--------|-----|-----------------|
| `simple_approval` | `request_simple_approval` | **Approve** and **Deny** buttons | `approved` or `denied` |
| `acknowledgement` | `request_acknowledgement` | **Acknowledge** button | `acknowledged` |
| `question` | `request_question` | Free-form text input | `answered` + free-form `text` |

### Feedback Destinations

When a respondent answers, the extension dispatches the response to the configured destination:

| Destination | Behavior |
|-------------|----------|
| `case` | Adds a note to the specified case via ext-cases. Requires a `case_id`. |
| `playbook` | Triggers the specified playbook via ext-playbook with the response data. Requires a `playbook_name`. |

### Response Content

Each feedback request can include optional JSON data per choice. When the respondent selects a choice, the corresponding content is included in the dispatched response. This allows automation to carry structured payloads through the human decision point.

- For `request_simple_approval`, use `approved_content` and `denied_content`.
- For `request_acknowledgement`, use `acknowledged_content`.
- For `request_question`, no content fields are available -- the respondent's free-form text IS the response.

## Channel Configuration

Channels are managed through the extension config, not via extension actions. You can configure channels through the LimaCharlie web UI (extension settings page), via the CLI, or through infrastructure-as-code with git-sync.

=== "CLI"
    ```bash
    echo '{"data":{"channels":[{"name":"ops","channel_type":"web"},{"name":"slack-ops","channel_type":"slack","output_name":"my-slack-output"}]},"usr_mtd":{"enabled":true}}' | \
      limacharlie hive set --hive-name extension_config --key ext-feedback
    ```

=== "Infrastructure as Code"
    Channels can be managed via [git-sync](../../../7-infrastructure-as-code/index.md) by including the extension config in your synced repository:
    ```yaml
    # extension_config/ext-feedback
    channels:
      - name: ops
        channel_type: web
      - name: slack-ops
        channel_type: slack
        output_name: my-slack-output
    ```

## Sending Feedback Requests

### Simple Approval

The `request_simple_approval` action sends a question with Approve/Deny buttons.

=== "CLI"
    ```bash
    limacharlie extension request \
      --name ext-feedback \
      --action request_simple_approval \
      --data '{
        "channel": "ops",
        "question": "Should we isolate host compromised-01?",
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

### Acknowledgement

The `request_acknowledgement` action sends a question with an Acknowledge button.

=== "CLI"
    ```bash
    limacharlie extension request \
      --name ext-feedback \
      --action request_acknowledgement \
      --data '{
        "channel": "ops",
        "question": "Alert: Ransomware detected on file-server-02. Please acknowledge.",
        "feedback_destination": "case",
        "case_id": "92",
        "acknowledged_content": "{\"status\": \"seen\"}"
      }'
    ```

### Question (Free-Form Text)

The `request_question` action sends a question with a text input field. The respondent types a free-form answer.

=== "CLI"
    ```bash
    limacharlie extension request \
      --name ext-feedback \
      --action request_question \
      --data '{
        "channel": "ops",
        "question": "What is the root cause of alert X?",
        "feedback_destination": "playbook",
        "playbook_name": "handle-root-cause"
      }'
    ```

The response event includes `choice: "answered"` and a `text` field with the respondent's answer.

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
  extension action: request_simple_approval
  extension request:
    channel: '{{ "ops-slack" }}'
    question: '{{ "Suspicious process detected on " }}{{ .routing.hostname }}{{ ". Isolate host?" }}'
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
        "request_simple_approval",
        {
            "channel": "ops",
            "question": f"Isolate host {data.get('hostname', 'unknown')}?",
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
3. The respondent clicks a button or submits a text response
4. The response is routed through the organization's webhook adapter (authenticated via `lc-secret` header)
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
5. Add a Slack channel to your extension config referencing the output name (see [Channel Configuration](#channel-configuration)). For example, a channel with `name: "ops"`, `channel_type: "slack"`, and `output_name: "my-slack-output"`.

!!! note
    For `request_question` feedback type, Slack shows a "Respond" button that links to the web UI, since Slack interactive messages do not support inline text input fields.

## Actions Reference

| Action | User-facing | Description |
|--------|:-----------:|-------------|
| `request_simple_approval` | Yes | Send a feedback request with Approve/Deny buttons |
| `request_acknowledgement` | Yes | Send a feedback request with an Acknowledge button |
| `request_question` | Yes | Send a question with a free-form text input |
| `process_response` | No | Internal: processes a response received via webhook |

### request_simple_approval Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `channel` | Yes | Name of the feedback channel |
| `question` | Yes | The question or prompt to present |
| `feedback_destination` | Yes | `case` or `playbook` |
| `case_id` | When destination is `case` | Case to add the response note to |
| `playbook_name` | When destination is `playbook` | Playbook to trigger with the response |
| `approved_content` | No | JSON data included when the respondent approves |
| `denied_content` | No | JSON data included when the respondent denies |

### request_acknowledgement Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `channel` | Yes | Name of the feedback channel |
| `question` | Yes | The question or prompt to present |
| `feedback_destination` | Yes | `case` or `playbook` |
| `case_id` | When destination is `case` | Case to add the response note to |
| `playbook_name` | When destination is `playbook` | Playbook to trigger with the response |
| `acknowledged_content` | No | JSON data included when the respondent acknowledges |

### request_question Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `channel` | Yes | Name of the feedback channel |
| `question` | Yes | The question or prompt to present |
| `feedback_destination` | Yes | `case` or `playbook` |
| `case_id` | When destination is `case` | Case to add the response note to |
| `playbook_name` | When destination is `playbook` | Playbook to trigger with the response |
