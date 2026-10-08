# Connecting AI Assistants

LimaCharlie can be accessed by AI assistants in three ways:

- **Claude Code Plugin** — Uses the `limacharlie` CLI for all operations, with pre-built skills and workflows (recommended)
- **CLI with other Frontier Models** — The same `limacharlie` CLI driven by Gemini CLI, OpenAI Codex, or any shell-capable agent; the recommended path when you're not using Claude Code. See [Using the CLI with other Frontier Models](frontier-models.md)
- **MCP Server** — A [Model Context Protocol](https://modelcontextprotocol.io/) endpoint for any MCP-compatible AI client

## Setup Options

Choose the setup method based on your AI client:

| Method | Auth Type | Multi-Org |
|--------|-----------|-----------|
| **Option 1:** Claude Code Plugin | OAuth via CLI (browser login) | Yes |
| **Option 2:** HTTP MCP with OAuth | OAuth (browser login) | Yes |
| **Option 3:** HTTP MCP with JWT | User API Key → JWT | Yes |
| **Option 3:** HTTP MCP with API Key | Org API Key | No |

**Recommendation:** Use Option 1 if you're using Claude Code — it provides the richest experience with pre-built skills and workflows, and uses the `limacharlie` CLI for all operations. If not using Claude Code, check whether your MCP client supports OAuth and use Option 2. Fall back to Option 3 (JWT or API key) only if OAuth isn't available in your client.

---

## Option 1: Claude Code Plugin (Recommended)

The LimaCharlie plugin provides the richest experience with pre-built skills, workflows, and multi-org support. Unlike Options 2–3, this plugin does **not** use an MCP server—it uses the `limacharlie` CLI for all API operations, which is automatically installed on session start.

### Installation

Run these commands in Claude Code:

```bash
/plugin marketplace add https://github.com/refractionPOINT/lc-ai
/plugin install lc-essentials@lc-marketplace
```

The plugin automatically installs the `limacharlie` CLI when a session starts. If auto-installation fails, install it manually:

```bash
pipx install limacharlie   # preferred (isolated environment)
uv tool install limacharlie # alternative
pip install --user limacharlie # fallback
```

### Authentication

Authenticate the CLI via OAuth:

```bash
limacharlie auth login
```

This opens your browser for LimaCharlie OAuth. Credentials persist across sessions automatically.

### Verify Setup

Run the following to confirm authentication and list your organizations:

```bash
limacharlie org list --output yaml
```

Or ask Claude: *"List my LimaCharlie organizations"*

---

## Option 2: HTTP MCP with OAuth

If your MCP client supports OAuth authentication, configure it to use the LimaCharlie MCP endpoint:

```text
https://mcp.limacharlie.io/mcp
```

The client will handle the OAuth flow automatically, prompting you to authenticate via browser. This provides the same multi-org access as the Claude Code plugin.

Consult your MCP client's documentation to determine if OAuth is supported.

---

## Option 3: HTTP MCP with Keys

Use this method when your MCP client doesn't support OAuth.

### Multi-Org Access (JWT)

To access all organizations associated with your user account, authenticate using a JWT generated from your **User API Key**.

#### Step 1: Get your User API Key

1. Go to [app.limacharlie.io](https://app.limacharlie.io) → **User Profile** (top-right menu)
2. Navigate to **API Keys**
3. Generate a User API Key

#### Step 2: Generate a JWT

```bash
curl -X POST "https://jwt.limacharlie.io" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "uid=YOUR_USER_ID&secret=YOUR_USER_API_KEY"
```

This returns a JWT valid for 1 hour. See [API Keys](../7-administration/access/api-keys.md) for details.

#### Step 3: Configure your MCP client

```json
{
  "mcpServers": {
    "limacharlie": {
      "type": "http",
      "url": "https://mcp.limacharlie.io/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_JWT"
      }
    }
  }
}
```

> **Note:** JWTs expire after 1 hour. You'll need to regenerate and update your configuration periodically.

---

### Single-Org Access (API Key)

For simpler single-organization access, use an Organization API Key directly.

**Get your credentials:**

1. Go to your organization in [app.limacharlie.io](https://app.limacharlie.io) → **Access Management** → **REST API**
2. Generate an API key with appropriate permissions
3. Note your Organization ID (OID) from the URL or org settings

**Claude Code:**

```bash
claude mcp add limacharlie https://mcp.limacharlie.io/mcp \
  --transport http \
  --header "Authorization: Bearer YOUR_API_KEY:YOUR_ORG_ID"
```

**Cursor / Other Clients:**

```json
{
  "mcpServers": {
    "limacharlie": {
      "type": "http",
      "url": "https://mcp.limacharlie.io/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_API_KEY:YOUR_ORG_ID"
      }
    }
  }
}
```

---

### Verify Setup

Ask your AI assistant: *"List my online sensors"*

---

## Permission Requirements

The MCP server enforces the same permission model as the LimaCharlie REST API. The operations available to the AI assistant depend on the permissions granted to the authenticated user or API key.

### How Permissions Work by Auth Method

| Auth Method | Permission Source |
|-------------|------------------|
| **OAuth / JWT** | Inherits your user permissions for each organization. You can only perform actions your user account is authorized for. |
| **Org API Key** | Uses the permissions assigned to the API key at creation time. Scoped to a single organization. |

### Permission Enforcement

Organization-scoped MCP operations require `ai_agent.operate` by default, in
addition to the API permission for the requested operation. The server or API
reports missing privileges; an authentication failure and a permission denial
are different problems. Read the returned error before changing credentials.

Profiles select the tools offered and callable on an endpoint; they do not grant
permissions. Prefer a product's read-only profile with a read-only key for a first
review. An unknown profile endpoint can return 404. Inspect the tool list because a server-wide
configured profile can override the URL profile.

`ai_agent.operate` must be granted to the API key or user authenticated to MCP,
even for read-only investigation. Add it to each permission set below. It does
not grant the operation-specific permissions by itself. `ai_agent.exec` is a
separate permission for launching configured agent UI actions; it is not required
merely to call MCP investigation tools. See the
[AI agent permissions reference](../8-reference/permissions.md#ai_agentexec-launch-a-configured-agent)
for examples and troubleshooting.

### Recommended Permissions by Use Case

The MCP server organizes its tools into capability profiles. Grant permissions based on the operations you need:

#### Read-Only Investigation

For querying telemetry and reviewing configurations without making changes:

| Permission | Purpose |
|------------|---------|
| `sensor.list` | List sensors in the organization |
| `sensor.get` | View detailed sensor information |
| `insight.evt.get` | Query historical telemetry events (LCQL) |
| `insight.det.get` | View detection alerts |
| `insight.stat` | Access telemetry statistics |
| `dr.list` | View D&R rules |
| `fp.ctrl` | View false positive rules |
| `yara.get` | View YARA rules |
| `lookup.get` | Read lookup tables |
| `audit.get` | Access audit logs |

#### Threat Response

For investigating and responding to incidents (includes all read-only permissions above, plus):

| Permission | Purpose |
|------------|---------|
| `sensor.task` | Send commands to sensors (process listing, network connections, file inspection) |
| `sensor.tag` | Apply or remove sensor tags (e.g., for isolation groups) |
| `sensor.del` | Remove compromised or decommissioned sensors |

#### Detection Engineering

For creating and managing detection rules (includes read-only permissions above, plus):

| Permission | Purpose |
|------------|---------|
| `dr.set` | Create and modify D&R rules |
| `dr.del` | Delete D&R rules |
| `fp.ctrl` | Create and manage false positive rules |
| `yara.set` | Create and modify YARA rules |
| `yara.del` | Delete YARA rules |
| `lookup.set` | Create and modify lookup tables |
| `lookup.del` | Delete lookup tables |

#### Platform Administration

For full platform management (includes all of the above, plus):

| Permission | Purpose |
|------------|---------|
| `output.list`, `output.set`, `output.del` | Manage output configurations |
| `secret.get`, `secret.set`, `secret.del` | Manage secrets |
| `ikey.list`, `ikey.set`, `ikey.del` | Manage installation keys |
| `org.conf.get`, `org.conf.set` | View and modify organization configuration |
| `ext.request`, `ext.conf.get`, `ext.conf.set` | Manage extensions |
| `playbook.get`, `playbook.set`, `playbook.del` | Manage playbooks |
| `cloudsensor.get`, `cloudsensor.set`, `cloudsensor.del` | Manage cloud sensor adapters |
| `externaladapter.get`, `externaladapter.set`, `externaladapter.del` | Manage external adapters |

#### CloudSec, CodeSec and MailSec

Start with a small, read-only product review, then grant the particular write
permission only when the workflow needs it:

| Workflow | Profile | Permissions beyond `ai_agent.operate` |
|---|---|---|
| CloudSec posture and CodeSec findings | `cloud_security_readonly` | `cloudsec.get` |
| CloudSec triage and code ingest | `cloud_security` | `cloudsec.get`, `cloudsec.set` |
| Dependency AutoFix and remediation run creation/decision | `cloud_security` | `cloudsec.respond` (separate from `cloudsec.set`) |
| Entity Pivot: resolve an email, hostname, IP or sensor ID to Users and Hosts | `cloud_security_readonly`, or the `historical_data_readonly` and `email_security_readonly` investigation profiles | `cloudsec.get`; activity and sightings also need the permission of each product they read, such as `insight.evt.get`, `insight.det.get` or `mailsec.get` |
| MailSec coverage, messages, campaigns and histories | `email_security_readonly` | `mailsec.get` |
| Raw email download | `email_security` | `mailsec.get` and `mailsec.get.eml` |
| MailSec EML analysis, rule validation/backtest and selected bulk preview | `email_security_readonly` | `mailsec.get` |
| MailSec provider diagnostics, campaign preview, verdict revision or remediation | `email_security` | `mailsec.act` |
| MailSec report resolution/reopening | `email_security` | `mailsec.set` |
| Product provider/policy/secret setup | `platform_admin` | Dedicated provider `.get/set`, product `.get/set` for policy, `secret.set` and required metadata-read access |

CloudSec requires the `ext-cloud-security` subscription; MailSec requires
`ext-email-security`. Setup uses generic Hive and
extension tools, the console or CLI; product read-only profiles exclude those
writes. MailSec's read-only profile excludes raw EML and privileged diagnostics.
Backend capability rollout remains independent of the client version.

Use `https://mcp.limacharlie.io/mcp/cloud_security_readonly` or
`https://mcp.limacharlie.io/mcp/email_security_readonly` for a supported hosted
profile. With a local server, select the same name using `MCP_PROFILE`.
Follow [CloudSec in your IDE](../cloud-security/mcp.md),
[MailSec with an AI assistant](../email-security/mcp.md), or the
[MCP source onboarding guide](https://github.com/refractionPOINT/lc-mcp-server/blob/master/docs/SECURITY-PRODUCTS.md)
for pilot setup and first tools.

### Assigning Permissions

**For users (OAuth/JWT):**

1. Go to your organization in [app.limacharlie.io](https://app.limacharlie.io) → **Access Management** → **Users**
2. Click the Edit icon next to the user
3. Assign permissions individually or select a pre-set permission scheme

Newly added users start with **Unset** privileges (basic org information only). Always configure appropriate permissions after adding a user. See [User Access](../7-administration/access/user-access.md) for details.

**For Organization API keys:**

1. Go to **Access Management** → **REST API**
2. Create a new API key and select the required permissions
3. Use the tables above to determine which permissions to grant based on your intended use case

> **Tip:** Follow the principle of least privilege — grant only the permissions needed for your use case. For read-only investigation workflows, avoid granting write permissions like `dr.set` or `sensor.task`.
>
> **Note:** Permissions granted through [Organization Groups](../7-administration/access/user-access.md#access-via-organization-groups) are additive on top of per-organization permissions and cannot reduce existing access.

For the full list of available permissions, see the [Permissions Reference](../8-reference/permissions.md).

---

## Capabilities

Once connected, AI assistants can:

- **Query telemetry** — Search historical sensor data using LCQL
- **Investigate endpoints** — Inspect processes, network connections, files, and more
- **Manage detections** — Create and modify D&R rules, YARA rules, and false positive rules
- **Take response actions** — Isolate endpoints, kill processes, manage tags
- **Search threat intelligence** — Query IOCs and map to MITRE ATT&CK
- **Configure the platform** — Manage outputs, adapters, secrets, and playbooks
- **Review CloudSec and CodeSec** — Inspect posture, repositories, findings and coverage
- **Pivot on an identifier** — Resolve an email address, hostname, IP address or sensor ID to Users and Hosts, then read their [activity](../cloud-security/entity-pivot.md)
- **Triage MailSec** — Review coverage, messages, campaigns and action history

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Unauthorized" error | Verify your API key and OID are correct. Ensure the API key has the required permissions for the operation — the error message will specify the missing privilege. |
| Plugin not appearing | Restart Claude Code after installation. |
| OAuth login fails | Clear browser cookies for limacharlie.io and try again. |
| CLI not found (plugin) | The plugin auto-installs the `limacharlie` CLI on session start. If it fails, install manually: `pipx install limacharlie` |
| CLI not authenticated | Run `limacharlie auth login` to authenticate via browser OAuth. |
| MCP tools not loading (Options 2–3) | Verify the MCP server URL and authentication headers are correct. |
| "Missing privilege" on specific operations | The authenticated user or API key lacks the required permission. See [Permission Requirements](#permission-requirements) to identify which permissions to grant. |

---

## Resources

- [lc-ai Plugin Repository](https://github.com/refractionPOINT/lc-ai)
- [MCP Server Source](https://github.com/refractionPOINT/lc-mcp-server)
- [API Keys & JWT Authentication](../7-administration/access/api-keys.md)
- [User Access & Permissions](../7-administration/access/user-access.md)
- [Permissions Reference](../8-reference/permissions.md)
