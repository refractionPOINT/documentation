# Microsoft Teams

Output detections and audit (only) to a Microsoft Teams channel via webhook.

Messages are delivered as [Adaptive Cards](https://learn.microsoft.com/en-us/adaptive-cards/).

* `webhook_url`: the Microsoft Teams webhook URL (Incoming Webhook or Power Automate Workflow).
* `message`: (optional) a template string for custom message formatting.

Example:

```
webhook_url: https://xxxxx.webhook.office.com/webhookb2/...
```

## Provisioning

You can connect LimaCharlie to a Teams channel using either an Incoming Webhook or a Power Automate Workflow.

### Option A: Incoming Webhook

1. In Microsoft Teams, navigate to the target channel
2. Click the channel name, then **Connectors** (or **Manage channel** > **Connectors**)
3. Find **Incoming Webhook** and click **Configure**
4. Give the webhook a name (e.g. "LimaCharlie") and optionally upload an icon
5. Click **Create** and copy the webhook URL — this is the `webhook_url` you need in LimaCharlie

For details, see [Create Incoming Webhooks](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook) in the Microsoft documentation.

### Option B: Power Automate Workflow (recommended)

Microsoft is transitioning from Office 365 Connectors to Power Automate Workflows for incoming webhooks.

1. In the Teams channel, click **+** or go to channel settings
2. Select **Workflows** and choose the **Post to a channel when a webhook request is received** template
3. Follow the setup wizard to create the workflow
4. Copy the workflow webhook URL — this is the `webhook_url` you need in LimaCharlie

For details, see [Create incoming webhooks with Workflows](https://support.microsoft.com/en-us/office/create-incoming-webhooks-with-workflows-for-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498).
