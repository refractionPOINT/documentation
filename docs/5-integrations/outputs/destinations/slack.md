# Slack

Output detections and audit (only) to a Slack community and channel.

- `slack_api_token`: the Bot User OAuth Token from your Slack App.
- `slack_channel`: the channel to output to within the community (e.g. `#detections`).

Example:

```text
slack_api_token: xoxb-your-bot-token
slack_channel: #detections
```

## Provisioning

To use this Output, you must create a Slack App and a Bot:

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App**
3. Select **From scratch**
4. Choose the workspace
5. From the sidebar, click **OAuth & Permissions**
6. Under **Bot Token Scopes**, click **Add an OAuth Scope**
7. Add the `chat:write` scope
8. From the sidebar, click **Install App**
9. Click **Install to Workspace**
10. Copy the **Bot User OAuth Token**. This is the `slack_api_token` that you need in LimaCharlie
11. In your Slack workspace, go to the target channel
12. Invite the bot with the slash command: `/invite @your-app-name`

### Interactivity Setup (for ext-feedback)

If you use this output with the [Feedback extension](../../extensions/limacharlie/feedback.md) for interactive Slack messages (approval buttons, acknowledgements):

1. In your Slack App settings ([api.slack.com/apps](https://api.slack.com/apps)), click **Interactivity & Shortcuts** in the sidebar
2. Toggle **Interactivity** to **On**
3. Set the **Request URL** to `https://feedback-system.limacharlie.io/callback/slack`
4. Click **Save Changes**

These settings let Slack send button-click interactions back to the feedback extension for processing. You do not need more LimaCharlie output parameters. The extension registers the callback automatically.
