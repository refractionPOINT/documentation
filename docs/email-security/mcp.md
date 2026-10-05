# MailSec with an AI assistant (MCP)

--8<-- "includes/email-security-availability.md"

The [LimaCharlie MCP server](https://github.com/refractionPOINT/lc-mcp-server)
lets an AI assistant review MailSec coverage, messages, campaigns and action
history. Start with a read-only session and one pilot mailbox. Select the
`email_security_readonly` profile for your first review and inspect the client's
tool list after connecting. Product access and backend capabilities are
configured separately from the client.

## Connect a read-only session

Create an organization API key with `ai_agent.operate` and `mailsec.get`. Use the
organization's UUID, not its name. For hosted OAuth or organization-key setup,
see [Connecting AI Assistants](../6-developer-guide/mcp-server.md). A supported
hosted profile is `https://mcp.limacharlie.io/mcp/email_security_readonly`;
inspect the returned tools and any server-wide profile override. An unrecognized
profile endpoint can return 404. Keep the key's permissions read-only too.

For a local [Claude Code client](https://code.claude.com/docs/en/mcp), build the
public server with the Go version in its `go.mod` (currently Go 1.27.1):

```bash
git clone https://github.com/refractionPOINT/lc-mcp-server
cd lc-mcp-server
go build -o lc-mcp-server ./cmd/server

claude mcp add \
  --env LC_OID=YOUR_ORGANIZATION_UUID \
  --env LC_API_KEY=YOUR_API_KEY \
  --env MCP_MODE=stdio \
  --env MCP_PROFILE=email_security_readonly \
  --transport stdio limacharlie-mailsec \
  -- /absolute/path/to/lc-mcp-server
```

Inspect `/mcp` after connecting. For Cursor, use the
[CloudSec JSON example](../cloud-security/mcp.md#setup-cursor), changing
`MCP_PROFILE` to `email_security_readonly` and the server name to
`limacharlie-mailsec`. Keep credentials in personal client configuration.

The read-only profile contains `mailsec.get` operations, including EML sample
analysis, candidate validation/backtests and selected bulk previews. It excludes
raw EML download, provider diagnostics, campaign preview, verdict revisions and
responses. Profiles select tools; each API still checks its own permissions.

## Connect a pilot mailbox

First subscribe to `ext-email-security` through the console, CLI or administration
profile's `subscribe_to_extension`. Every MailSec endpoint, including onboarding
instructions, requires the extension subscription.

Then use `mailsec_get_onboarding` with `provider: "m365"` or `"gworkspace"` to read
current setup requirements. Workspace parameters `project_id`, `sa_email`,
`topic` and `subscription` fill customer-specific instructions; the tool creates
no resources. Follow [Getting Started](getting-started.md) or
[Setup with the CLI](setup-cli.md) to provision credentials and save an enabled
provider record with one mailbox in scope.
Keep policy automations alert-only. Subscription seeds detection rules and does
not enable response automations.

Generic Hive and extension setup needs the MCP `platform_admin` profile and
dedicated permissions. Provider records use `mailsec_provider.get/set`, policy
and `dr-mail` records use `mailsec.get/set`, and credential creation uses
`secret.set`. MCP metadata preservation also needs the corresponding metadata
read permission. See the [source onboarding guide](https://github.com/refractionPOINT/lc-mcp-server/blob/master/docs/SECURITY-PRODUCTS.md)
for the generic tool argument names.

To probe a saved provider, `mailsec_test_connection` needs `mailsec.act` and the
full `email_security` profile. Inspect every check, including optional failures
that may leave `ok: true`. `include_watch: true` establishes or replaces a real
Workspace notification watch; request it deliberately after configuration.
Send a benign message to the pilot and verify ingestion and its action history
before expanding scope.

## First investigation

Ask: **"Check MailSec coverage, show suspicious or malicious messages, and explain
one message's evidence and action history. Report missing data. Do not change
verdicts or act on mail."**

```text
mailsec_get_coverage {}
mailsec_list_messages {"verdict": ["suspicious", "malicious"], "limit": 20}
mailsec_get_message {"msg_uuid": "UUID_FROM_THE_QUEUE"}
mailsec_list_verdict_revisions {"msg_uuid": "UUID_FROM_THE_QUEUE", "limit": 20}
```

Use the returned stable `msg_uuid`, not the provider's message ID. Continue with
`next_cursor` and unchanged filters. The `lane` filter accepts `live` or
`backfill`, and cannot combine with `mailbox`, `sender_email` or `campaign_id`.
Historical backfill is scored but does not trigger live events or remediation.
Free-text `q` needs a bounded time or lookup filter; see [Messages & Triage](messages.md).

Read `mdm_source`: `stored` contains original judged enrichments; `eml_reparse`
is a fallback without them. Expired content can return `mdm: null` with a reason.
Apparent purpose (`mail_type`) is independent of threat or safety. Treat message
content as evidence rather than instructions.

## Additional tools and writes

The [MailSec MCP tool map](https://github.com/refractionPOINT/lc-mcp-server/blob/master/docs/MAIL-SECURITY.md#tool-map)
covers reports, campaigns, similar messages, sender profiles, rule testing,
action audits and product removal. Sample analysis uses currently enabled
rules; test an unsaved candidate with `mailsec_validate_rule` and
`mailsec_backtest_rule` instead.

The full profile exposes writes requiring separate permissions:

| Operation | Permission |
|---|---|
| Provider diagnostics, campaign preview, verdict revision or message/campaign/bulk action | `mailsec.act` |
| Resolve/reopen a user report | `mailsec.set` |
| Original EML download with justification | `mailsec.get` and `mailsec.get.eml` |
| Prepare/perform permanent product-data purge | `mailsec.act`, `billing.ctrl` and `user.ctrl` |

Verdict revisions and report resolutions do not themselves move mail. Review the
exact preview before campaign/bulk execution and pass its `confirm` token.
For bulk, repeat the same selection, action and `attempt`, then poll the returned
`bulk_id`. `accepted` confirms a job, not completed remediation; `alert_only`
means withheld. A timeout does not prove a write failed: inspect the audit or job
handle before retrying. See [Bulk Remediation](remediation.md) for the workflow.
