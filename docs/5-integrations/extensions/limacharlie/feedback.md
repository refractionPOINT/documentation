# Feedback

The Feedback extension sends interactive feedback requests to external channels. It can send an approve-or-deny prompt, an acknowledgement request, or a free-form question. The channel can be Slack, Telegram, Microsoft Teams, email, or a built-in web UI. The extension collects the responses and sends them to LimaCharlie subsystems: case notes through ext-cases, playbook triggers through ext-playbook, or AI agent sessions through the AI Sessions API.

Use the extension in AI-driven and human-initiated workflows that need operator approval or input before an automated action. For example, a D&R rule or a playbook can ask a person "Should we isolate host compromised-01?". The rule then waits for a response before it continues.

## Enabling the Extension

Open the [Feedback extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-feedback) in the marketplace. Select the organization that you want to enable the extension for. Select **Subscribe**.

When you subscribe, the extension automatically:

1. Creates a webhook adapter for the organization
2. Installs a D&R rule that sends feedback responses to the extension for processing

No more configuration is necessary. You can configure channels and send feedback requests immediately.

## Concepts

### Channels

A **channel** defines how the extension delivers feedback requests to respondents. Each channel has a name and a type. You configure channels in the extension config. For more information, see [Channel Configuration](#channel-configuration).

| Channel Type | Description | In-Chat Buttons | Requirements |
|-------------|-------------|:---------------:|--------------|
| `web` | Built-in web UI. Returns a URL that you can share. The page shows the question with response buttons or a text input. | N/A | None |
| `slack` | Sends an interactive Block Kit message with action buttons to a Slack channel. | Yes | A [Slack Tailored Output](../../outputs/destinations/slack.md) with `slack_api_token` and `slack_channel`. See [Slack Setup](#slack-setup). |
| `telegram` | Sends a message with inline keyboard buttons to a Telegram chat through the Bot API. | Yes | A [Telegram Tailored Output](../../outputs/destinations/telegram.md) with `bot_token` and `chat_id`. See [Telegram Setup](#telegram-setup). |
| `ms_teams` | Sends an Adaptive Card to a Microsoft Teams channel through a webhook. A button links to the web UI, where the respondent answers. | No (link to web UI) | A [Microsoft Teams Tailored Output](../../outputs/destinations/ms-teams.md) with `webhook_url`. See [Microsoft Teams Setup](#microsoft-teams-setup). |
| `email` | Sends an HTML email with the question and a link to the web approval page. | No (link to web UI) | An [SMTP Tailored Output](../../outputs/destinations/smtp.md) with `dest_host`, `dest_email`, `from_email`, and SMTP credentials. See [Email Setup](#email-setup). |

### Feedback Types

Each feedback type has a dedicated action:

| Feedback Type | Action | UI | Response Values |
|--------------|--------|-----|-----------------|
| `simple_approval` | `request_simple_approval` | **Approve** and **Deny** buttons | `approved` or `denied` |
| `acknowledgement` | `request_acknowledgement` | **Acknowledge** button | `acknowledged` |
| `question` | `request_question` | Free-form text input | `answered` + free-form `text` |

### Feedback Destinations

When a respondent answers, the extension sends the response to the configured destination:

| Destination | Behavior |
|-------------|----------|
| `case` | Adds a note to the specified case through ext-cases. Needs a `case_id`. |
| `playbook` | Triggers the specified playbook through ext-playbook with the response data. Needs a `playbook_name`. |
| `ai_agent` | Starts an AI agent session. The extension adds the response data to the prompt of the agent. Needs an `ai_agent_name` that refers to an `ai_agent` hive record. |

### Response Content

Each feedback request can include optional JSON data for each choice. When the respondent selects a choice, the extension includes the related content in the response that it sends. Automation can then carry structured payloads through the human decision point.

- For `request_simple_approval`, use `approved_content` and `denied_content`.
- For `request_acknowledgement`, use `acknowledged_content`.
- For `request_question`, there are no content fields. The free-form text from the respondent is the response.

### Timeouts

All feedback actions accept an optional timeout. If you set `timeout_seconds` (minimum 60) and no person responds before the deadline, the extension responds with a default choice. The timeout response uses the same webhook, D&R, and dispatch path as a normal response. In a timeout response, `responder` is `"timeout"`.

| Parameter | Applies To | Description |
|-----------|-----------|-------------|
| `timeout_seconds` | All actions | Number of seconds to wait before an automatic response (minimum 60) |
| `timeout_choice` | `request_simple_approval` | The choice to select automatically: `approved` or `denied`. Necessary when you set `timeout_seconds`. |
| `timeout_content` | All actions | JSON data to include in the timeout response. It replaces the content of the choice. Necessary for `request_question` when you set `timeout_seconds`. |

For `request_acknowledgement`, the timeout choice is always `acknowledged`. For `request_question`, the timeout choice is always `answered`, and `timeout_content` gives the automatic answer.

If you configure a timeout, the channel message includes a note such as "(Auto-denied in 5 minutes if no response)". The note shows the deadline to the respondent.

## Channel Configuration

You manage channels in the extension config, not with extension actions. You can configure channels in the LimaCharlie web app (the extension settings page), with the CLI, or as infrastructure-as-code with git-sync.

=== "CLI"
    ```bash
    # Add channels individually
    limacharlie feedback channel add --name ops --type web
    limacharlie feedback channel add --name slack-ops --type slack --output-name my-slack-output
    limacharlie feedback channel add --name tg-ops --type telegram --output-name my-telegram-output
    limacharlie feedback channel add --name teams-ops --type ms_teams --output-name my-teams-output
    limacharlie feedback channel add --name email-ops --type email --output-name my-smtp-output

    # List configured channels
    limacharlie feedback channel list

    # Remove a channel
    limacharlie feedback channel remove --name old-channel
    ```

=== "Hive (bulk)"
    ```bash
    echo '{"data":{"channels":[{"name":"ops","channel_type":"web"},{"name":"slack-ops","channel_type":"slack","output_name":"my-slack-output"},{"name":"tg-ops","channel_type":"telegram","output_name":"my-telegram-output"},{"name":"teams-ops","channel_type":"ms_teams","output_name":"my-teams-output"},{"name":"email-ops","channel_type":"email","output_name":"my-smtp-output"}]},"usr_mtd":{"enabled":true}}' | \
      limacharlie hive set --hive-name extension_config --key ext-feedback
    ```

=== "Infrastructure as Code"
    You can manage channels with [git-sync](git-sync.md). Add the extension config to your synced repository:
    ```yaml
    # extension_config/ext-feedback
    channels:
      - name: ops
        channel_type: web
      - name: slack-ops
        channel_type: slack
        output_name: my-slack-output
      - name: tg-ops
        channel_type: telegram
        output_name: my-telegram-output
      - name: teams-ops
        channel_type: ms_teams
        output_name: my-teams-output
      - name: email-ops
        channel_type: email
        output_name: my-smtp-output
    ```

For all channel types except `web`, the `output_name` field refers to a LimaCharlie [Tailored Output](../../outputs/index.md) that holds the credentials for the channel.

## Sending Feedback Requests

### Simple Approval

The `request_simple_approval` action sends a question with Approve/Deny buttons.

=== "CLI"
    ```bash
    limacharlie feedback request-approval \
      --channel ops \
      --question "Should we isolate host compromised-01?" \
      --destination case --case-id 78 \
      --approved-content '{"action": "isolate", "sid": "sensor-abc"}' \
      --denied-content '{"action": "skip"}'
    ```

=== "CLI (with timeout)"
    ```bash
    # Auto-deny after 5 minutes if no human responds
    limacharlie feedback request-approval \
      --channel ops \
      --question "Should we isolate host compromised-01?" \
      --destination case --case-id 78 \
      --approved-content '{"action": "isolate", "sid": "sensor-abc"}' \
      --denied-content '{"action": "skip"}' \
      --timeout 300 --timeout-choice denied
    ```

=== "Extension Request (generic)"
    ```bash
    limacharlie extension request \
      --name ext-feedback \
      --action request_simple_approval \
      --data '{
        "channel": "ops",
        "question": "Should we isolate host compromised-01?",
        "feedback_destination": "case",
        "case_id": "78",
        "approved_content": {"action": "isolate", "sid": "sensor-abc"},
        "denied_content": {"action": "skip"}
      }'
    ```

The response includes:

```json
{
  "request_id": "a1b2c3d4-...",
  "url": "https://feedback-system.limacharlie.io/r/a1b2c3d4-..."
}
```

The `url` is the link to the web UI where the respondent answers. You can share this link. For Slack, Telegram, Microsoft Teams, and email channels, the response contains no URL. The extension sends the message directly to the configured channel.

### Acknowledgement

The `request_acknowledgement` action sends a question with an Acknowledge button.

=== "CLI"
    ```bash
    limacharlie feedback request-ack \
      --channel ops \
      --question "Alert: Ransomware detected on file-server-02. Please acknowledge." \
      --destination case --case-id 92 \
      --acknowledged-content '{"status": "seen"}'
    ```

=== "CLI (with timeout)"
    ```bash
    # Auto-acknowledge after 10 minutes
    limacharlie feedback request-ack \
      --channel ops \
      --question "Alert: Ransomware detected on file-server-02. Please acknowledge." \
      --destination case --case-id 92 \
      --timeout 600
    ```

=== "Extension Request (generic)"
    ```bash
    limacharlie extension request \
      --name ext-feedback \
      --action request_acknowledgement \
      --data '{
        "channel": "ops",
        "question": "Alert: Ransomware detected on file-server-02. Please acknowledge.",
        "feedback_destination": "case",
        "case_id": "92",
        "acknowledged_content": {"status": "seen"}
      }'
    ```

### Question (Free-Form Text)

The `request_question` action sends a question with a text input field. The respondent types a free-form answer.

=== "CLI"
    ```bash
    limacharlie feedback request-question \
      --channel ops \
      --question "What is the root cause of alert X?" \
      --destination playbook --playbook handle-root-cause
    ```

=== "CLI (with timeout)"
    ```bash
    # Auto-answer after 5 minutes with a default response
    limacharlie feedback request-question \
      --channel ops \
      --question "What is the root cause of alert X?" \
      --destination playbook --playbook handle-root-cause \
      --timeout 300 --timeout-content '{"answer": "no response"}'
    ```

=== "Extension Request (generic)"
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

A D&R rule can request human approval before an automated action. The extension sends the response to a playbook that does the action.

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
    timeout_seconds: 300
    timeout_choice: '{{ "denied" }}'
```

The `timeout_seconds: 300` and `timeout_choice: "denied"` values make sure that the rule denies automatically if no person responds in 5 minutes. The workflow does not wait forever.

### Playbook Example

A playbook can request approval while it runs:

```python
def playbook(sdk, data):
    # Request human approval with a 5-minute timeout.
    # sdk is a limacharlie.Manager instance.
    response = sdk.extensionRequest(
        "ext-feedback",
        "request_simple_approval",
        {
            "channel": "ops",
            "question": f"Isolate host {data.get('hostname', 'unknown')}?",
            "feedback_destination": "playbook",
            "playbook_name": "handle-isolation-response",
            "approved_content": {"action": "isolate", "sid": data.get("sid")},
            "denied_content": {"action": "skip"},
            "timeout_seconds": 300,
            "timeout_choice": "denied",
        },
    )

    # The response will trigger the handle-isolation-response playbook
    # when the human responds (or after 5 minutes with choice="denied"
    # and responder="timeout").
    return {"request_id": response.get("request_id")}
```

## Response Flow

1. The extension creates the feedback request and stores it with a 7-day TTL
2. The extension delivers the question through the configured channel (a Slack message or a web URL)
3. The respondent clicks a button or sends a text response (or the timeout occurs, if you configured one)
4. The response goes through the webhook adapter of the organization (the `lc-secret` header authenticates it)
5. A D&R rule matches the response event and triggers the `process_response` action of the extension
6. The extension claims the request atomically (this stops duplicate processing) and sends the response to the configured destination

If you configure a timeout and no person responds before the deadline, the extension sends a response with the configured default choice. The timeout response includes `responder: "timeout"`. Downstream automation can use this value to tell a timeout response from a human response.

Feedback requests expire after **7 days**. An expired request shows an error in the web UI, and the extension rejects it.

The extension protects responses against replay. After it processes a response, it rejects duplicate deliveries from webhook retries or replay. This also stops a race between a human response and a timeout that occur at the same time. The first response that the extension processes claims the request.

## Slack Setup

To use Slack channels:

1. Create a Slack App and enable "Interactivity & Shortcuts"
2. Set the Request URL to the Slack callback endpoint: `https://feedback-system.limacharlie.io/callback/slack`
3. Install the app in your Slack workspace and record the Bot User OAuth Token
4. In LimaCharlie, create a [Slack Tailored Output](../../outputs/destinations/slack.md) with:
    - `slack_api_token`: the Bot User OAuth Token
    - `slack_channel`: the target channel (e.g. `#security-ops`)
5. Add a Slack channel to your extension config that refers to the output name. For more information, see [Channel Configuration](#channel-configuration). For example, use a channel with `name: "ops"`, `channel_type: "slack"`, and `output_name: "my-slack-output"`.

!!! note
    For the `request_question` feedback type, Slack shows a "Respond" button that links to the web UI. Slack interactive messages do not support inline text input fields.

## Telegram Setup

To use Telegram channels, you need a Telegram bot and a LimaCharlie Tailored Output with its credentials.

### Step 1: Create a Telegram Bot

1. Open Telegram and start a conversation with [**@BotFather**](https://t.me/BotFather) ([Telegram Bot API documentation](https://core.telegram.org/bots#botfather))
2. Send `/newbot`. Obey the prompts to choose a name and a username.
3. BotFather responds with a **bot token** (e.g. `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`). Save this token.
4. Add the bot to the Telegram group or channel that receives the feedback messages
5. Get the **chat ID** of the group or channel:
    - Add the bot to the group, send a message, then look for the `chat.id` field at `https://api.telegram.org/bot<TOKEN>/getUpdates`
    - For channels, the chat ID is usually a negative number such as `-1001234567890`

For more information, see the [Telegram Bot API documentation](https://core.telegram.org/bots/api).

### Step 2: Create a Tailored Output

In LimaCharlie, create a Telegram [Tailored Output](../../outputs/index.md) with:

- `bot_token`: the bot token from BotFather
- `chat_id`: the target chat, group, or channel ID

### Step 3: Add a Telegram Channel

Add a channel to your extension config that refers to the output name:

```yaml
channels:
  - name: tg-ops
    channel_type: telegram
    output_name: my-telegram-output
```

### How Telegram Responses Work

For the `simple_approval` and `acknowledgement` feedback types, Telegram messages include **inline keyboard buttons** (Approve/Deny or Acknowledge). The respondent taps a button in the chat. The extension processes the response immediately, and the respondent stays in Telegram.

For `request_question`, a "Respond" button links to the web UI. Telegram inline keyboards do not support text input.

When the extension receives a response, it updates the original Telegram message. The message then shows the choice and the respondent.

!!! note
    The extension automatically registers a webhook with the Telegram bot to receive the callbacks from button clicks. It uses [`setWebhook`](https://core.telegram.org/bots/api#setwebhook) for this registration. If you also use the bot for other webhook integrations, the ext-feedback registration replaces the existing webhook. Use a dedicated bot for ext-feedback if this is a problem.

## Microsoft Teams Setup

To use Microsoft Teams channels, you need a Teams Workflow webhook URL and a LimaCharlie Tailored Output.

!!! warning "Incoming Webhooks retired"
    You must use a Power Automate Workflow, as described in the next steps. Microsoft retired Office 365 Connectors (including Incoming Webhooks) from Teams.

### Create a Workflow Webhook

1. In Microsoft Teams, open the channel that receives the feedback messages
2. Click **...** (More options) next to the channel name
3. Select **Workflows**
4. Find and select the **Send webhook alerts to a channel** template
5. Give the workflow a name (e.g. "LimaCharlie Feedback") and authenticate your account
6. Click **Next**, confirm the Team and the Channel, then click **Add workflow**
7. Copy the webhook URL from the confirmation dialog

For more information, see [Create incoming webhooks with Workflows](https://support.microsoft.com/en-us/office/create-incoming-webhooks-with-workflows-for-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498).

### Create the Tailored Output

In LimaCharlie, create a Microsoft Teams [Tailored Output](../../outputs/index.md) with:

- `webhook_url`: the Teams webhook URL (from either option above)

### Add a Teams Channel

Add a channel to your extension config that refers to the output name:

```yaml
channels:
  - name: teams-ops
    channel_type: ms_teams
    output_name: my-teams-output
```

### How Teams Responses Work

The extension delivers feedback requests as [Adaptive Cards](https://learn.microsoft.com/en-us/adaptive-cards/) in the Teams channel. The card shows the question and a button that opens the web approval page in a browser. The extension collects the responses through the web UI.

## Email Setup

To use email channels, you need an SMTP server and a LimaCharlie Tailored Output with its credentials.

### Create a Tailored Output

In LimaCharlie, create an SMTP [Tailored Output](../../outputs/index.md) with:

- `dest_host`: the SMTP server address, with an optional port (e.g. `smtp.example.com:587`). If you do not give a port, the default is 587.
- `dest_email`: the recipient email address (e.g. `soc@example.com`)
- `from_email`: the sender email address (e.g. `limacharlie@example.com`)
- `username` (optional): the username for SMTP authentication
- `password` (optional): the password for SMTP authentication

### Add an Email Channel

Add a channel to your extension config that refers to the output name:

```yaml
channels:
  - name: email-ops
    channel_type: email
    output_name: my-smtp-output
```

### How Email Responses Work

The extension sends an HTML email with the feedback question and a **Respond** button. The button links to the web approval page. The extension collects the responses through the web UI.

## Actions Reference

| Action | User-facing | Description |
|--------|:-----------:|-------------|
| `request_simple_approval` | Yes | Send a feedback request with Approve/Deny buttons |
| `request_acknowledgement` | Yes | Send a feedback request with an Acknowledge button |
| `request_question` | Yes | Send a question with a free-form text input |
| `process_response` | No | Internal: processes a response that comes through the webhook |

### request_simple_approval Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `channel` | Yes | Name of the feedback channel |
| `question` | Yes | The question or prompt to present |
| `feedback_destination` | Yes | `case`, `playbook`, or `ai_agent` |
| `case_id` | When destination is `case` | Case to add the response note to |
| `playbook_name` | When destination is `playbook` | Playbook to trigger with the response |
| `ai_agent_name` | When destination is `ai_agent` | Name of the `ai_agent` hive record to start a session with |
| `approved_content` | No | JSON data included when the respondent approves |
| `denied_content` | No | JSON data included when the respondent denies |
| `timeout_seconds` | No | Respond automatically after this many seconds if there is no response (minimum 60) |
| `timeout_choice` | When `timeout_seconds` is set | Choice to select automatically on timeout: `approved` or `denied` |
| `timeout_content` | No | JSON data for the timeout response. It replaces the content of the choice. |

### request_acknowledgement Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `channel` | Yes | Name of the feedback channel |
| `question` | Yes | The question or prompt to present |
| `feedback_destination` | Yes | `case`, `playbook`, or `ai_agent` |
| `case_id` | When destination is `case` | Case to add the response note to |
| `playbook_name` | When destination is `playbook` | Playbook to trigger with the response |
| `ai_agent_name` | When destination is `ai_agent` | Name of the `ai_agent` hive record to start a session with |
| `acknowledged_content` | No | JSON data included when the respondent acknowledges |
| `timeout_seconds` | No | Acknowledge automatically after this many seconds if there is no response (minimum 60) |
| `timeout_content` | No | JSON data for the timeout response. It replaces `acknowledged_content`. |

### request_question Parameters

| Parameter | Required | Description |
|-----------|:--------:|-------------|
| `channel` | Yes | Name of the feedback channel |
| `question` | Yes | The question or prompt to present |
| `feedback_destination` | Yes | `case`, `playbook`, or `ai_agent` |
| `case_id` | When destination is `case` | Case to add the response note to |
| `playbook_name` | When destination is `playbook` | Playbook to trigger with the response |
| `ai_agent_name` | When destination is `ai_agent` | Name of the `ai_agent` hive record to start a session with |
| `timeout_seconds` | No | Answer automatically after this many seconds if there is no response (minimum 60) |
| `timeout_content` | When `timeout_seconds` is set | JSON data for the automatic answer on timeout. Necessary for the question type. |
