# Slack Audit Logs

[Slack audit logs](https://api.slack.com/admins/audit-logs) supply the audit events of a Slack Enterprise Grid organization. You can ingest these events directly from the Slack API with a cloud-to-cloud Adapter or with a CLI Adapter.

Use the `slack` platform to address Slack telemetry.

**Note**: Audit Logs through the API are available only to Slack workspaces on the Enterprise Grid plan.

## Adapter Deployment

You can collect Slack Audit Logs directly from the Slack API, with a cloud-to-cloud Adapter or with the CLI Adapter. You need a Slack App OAuth token before you deploy this Adapter. For more information about how to generate Slack OAuth tokens, see [Slack token types](https://api.slack.com/authentication/token-types).

### Cloud-to-Cloud Adapter

Configure Slack API telemetry in the LimaCharlie web application. Under `Sensors List`, select `+ Add Sensor > Slack Audit Logs`. After you give an Installation Key, the web app asks for an Adapter Name and a Slack App OAuth Token.

### Deploying via the CLI Adapter

You can also use the LimaCharlie CLI Adapter to ingest Slack events if you do not want to create a cloud-to-cloud Adapter. Use the sample configuration below to create a Slack CLI Adapter:

```yaml
slack:
  client_options:
    hostname: slack-audit
    identity:
      installation_key: <INSTALLATION_KEY>
      oid: <OID>
    platform: slack
    sensor_seed_key: super-special-seed-key
  token: <SLACK OAUTH TOKEN>
```
