# Slack

Output detections and audit (only) to a Slack community and channel.

* `slack_api_token`: the Slack provided API token used to authenticate.
* `slack_channel`: the channel to output to within the community.

Example:

```
slack_api_token: sample_api_token
slack_channel: #detections
```

## Provisioning

To use this Output, you need to create a Slack App and Bot. This is very simple:

1. Head over to https://api.slack.com/apps
2. Click on "Create App" and select the workspace where it should go
3. From the sidebar, click on OAuth & Permissions
4. Go to the section "Bot Token Scope" and click "Add an OAuth Scope"
5. Select the scope `chat:write`
6. From the sidebar, click "Install App" and then "Install to Workspace"
7. Copy token shown, this is the `slack_api_token` you need in LimaCharlie
8. In your Slack workspace, go to the channel you want to receive messages in, and type the slash command: `/invite @limacharlie` (assuming the app name is `limacharlie`)
