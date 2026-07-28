# Microsoft Teams

Output detections and audit (only) to a Microsoft Teams channel through a webhook.

Messages are delivered as [Adaptive Cards](https://learn.microsoft.com/en-us/adaptive-cards/).

- `webhook_url`: the Microsoft Teams Workflow webhook URL.
- `message`: (optional) a template string for custom message formatting.

Example:

```text
webhook_url: https://<environment-id>.<region>.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/...
```

## Provisioning

LimaCharlie connects to a Teams channel with a **Power Automate Workflow** webhook.

!!! warning "Incoming Webhooks retired"
    Microsoft retired Office 365 Connectors (including Incoming Webhooks) from Teams. The old `webhook.office.com` URLs no longer work. You must use a Power Automate Workflow as described below.

### Create a Workflow webhook

1. In Microsoft Teams, go to the target channel
2. Click **...** (More options) next to the channel name
3. Select **Workflows**
4. Search for the **Send webhook alerts to a channel** template
5. Select the template
6. Give the workflow a name (e.g. "LimaCharlie")
7. Authenticate your account
8. Click **Next**
9. Confirm the Team and the Channel
10. Click **Add workflow**
11. Copy the webhook URL from the confirmation dialog. This is the `webhook_url` that you need in LimaCharlie

For details, see [Create incoming webhooks with Workflows](https://support.microsoft.com/en-us/office/create-incoming-webhooks-with-workflows-for-microsoft-teams-8ae491c7-0394-4861-ba59-055e33f75498).

!!! note "Workflow limitations"
    - Workflows post through **Flow bot**. Flow bot works only in **public channels**. For shared channels, open the workflow in Power Automate. Then change "Post As" from Flow bot to User.
    - Each workflow is linked to the user that created it. If that user leaves the organization, the workflow stops. To prevent this, add co-owners in Power Automate.
