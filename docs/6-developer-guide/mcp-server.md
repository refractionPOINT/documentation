# Connecting AI Assistants

AI assistants can access LimaCharlie in three ways:

- **Claude Code Plugin** — Uses the `limacharlie` CLI for all operations, with pre-built skills and workflows (recommended)
- **CLI with other Frontier Models** — The same `limacharlie` CLI, driven by Gemini CLI, OpenAI Codex, or another agent that can run shell commands. Use this method if you do not use Claude Code. See [Using the CLI with other Frontier Models](frontier-models.md)
- **MCP Server** — A [Model Context Protocol](https://modelcontextprotocol.io/) endpoint for any MCP-compatible AI client

## Setup Options

Choose the setup method based on your AI client:

| Method | Auth Type | Multi-Org |
|--------|-----------|-----------|
| **Option 1:** Claude Code Plugin | OAuth through the CLI (browser login) | Yes |
| **Option 2:** HTTP MCP with OAuth | OAuth (browser login) | Yes |
| **Option 3:** HTTP MCP with JWT | User API Key → JWT | Yes |
| **Option 3:** HTTP MCP with API Key | Org API Key | No |

**Recommendation:** Use Option 1 if you use Claude Code. Option 1 supplies pre-built skills and workflows, and uses the `limacharlie` CLI for all operations. If you do not use Claude Code, check if your MCP client supports OAuth, then use Option 2. Use Option 3 (JWT or API key) only if your client does not support OAuth.

---

## Option 1: Claude Code Plugin (Recommended)

The LimaCharlie plugin supplies pre-built skills, workflows, and multi-org support. Unlike Options 2–3, this plugin does **not** use an MCP server. It uses the `limacharlie` CLI for all API operations, and it installs the CLI automatically when a session starts.

### Installation

Run these commands in Claude Code:

```bash
/plugin marketplace add https://github.com/refractionPOINT/lc-ai
/plugin install lc-essentials@lc-marketplace
```

The plugin installs the `limacharlie` CLI automatically when a session starts. If the automatic installation fails, install the CLI manually:

```bash
pipx install limacharlie   # preferred (isolated environment)
uv tool install limacharlie # alternative
pip install --user limacharlie # fallback
```

### Authentication

Authenticate the CLI with OAuth:

```bash
limacharlie auth login
```

The command opens your browser for LimaCharlie OAuth. The CLI keeps the credentials for later sessions automatically.

### Verify Setup

Run this command to confirm the authentication and to list your organizations:

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

The client does the OAuth flow automatically and asks you to authenticate in a browser. This method gives the same multi-org access as the Claude Code plugin.

Read the documentation of your MCP client to find if it supports OAuth.

---

## Option 3: HTTP MCP with Keys

Use this method when your MCP client does not support OAuth.

### Multi-Org Access (JWT)

To access all organizations of your user account, authenticate with a JWT that you generate from your **User API Key**.

#### Step 1: Get your User API Key

1. Go to [app.limacharlie.io](https://app.limacharlie.io) → **User Profile** (top-right menu)
2. Go to **API Keys**
3. Generate a User API Key

#### Step 2: Generate a JWT

```bash
curl -X POST "https://jwt.limacharlie.io" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "uid=YOUR_USER_ID&secret=YOUR_USER_API_KEY"
```

The command returns a JWT that is valid for 1 hour. See [API Keys](../7-administration/access/api-keys.md) for details.

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

> **Note:** JWTs expire after 1 hour. Generate a new JWT and update your configuration at regular intervals.

---

### Single-Org Access (API Key)

For single-organization access, use an Organization API Key directly.

**Get your credentials:**

1. Go to your organization in [app.limacharlie.io](https://app.limacharlie.io) → **Access Management** → **REST API**
2. Generate an API key with the necessary permissions
3. Get your Organization ID (OID) from the URL or from the org settings

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

The MCP server enforces the same permission model as the LimaCharlie REST API. The permissions of the authenticated user or API key control which operations the AI assistant can do.

### How Permissions Work by Auth Method

| Auth Method | Permission Source |
|-------------|------------------|
| **OAuth / JWT** | Inherits your user permissions for each organization. You can do only the actions that your user account is authorized to do. |
| **Org API Key** | Uses the permissions that you assign to the API key when you create it. Scoped to one organization. |

### Permission Enforcement

The API enforces permissions strictly. An operation without the necessary permission fails with a `401` error that specifies the missing privilege. The AI assistant shows these errors and tells you which permission is necessary.

### Recommended Permissions by Use Case

The MCP server organizes its tools into capability profiles. Grant permissions based on the operations you need:

#### Read-Only Investigation

To query telemetry and review configurations without changes:

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

To investigate and respond to incidents (includes all the read-only permissions above, plus):

| Permission | Purpose |
|------------|---------|
| `sensor.task` | Send commands to sensors (process listing, network connections, file inspection) |
| `sensor.tag` | Apply or remove sensor tags (e.g., for isolation groups) |
| `sensor.del` | Remove compromised or decommissioned sensors |

#### Detection Engineering

To create and manage detection rules (includes the read-only permissions above, plus):

| Permission | Purpose |
|------------|---------|
| `dr.set` | Create and change D&R rules |
| `dr.del` | Delete D&R rules |
| `fp.ctrl` | Create and manage false positive rules |
| `yara.set` | Create and change YARA rules |
| `yara.del` | Delete YARA rules |
| `lookup.set` | Create and change lookup tables |
| `lookup.del` | Delete lookup tables |

#### Platform Administration

To manage the full platform (includes all of the above, plus):

| Permission | Purpose |
|------------|---------|
| `output.list`, `output.set`, `output.del` | Manage output configurations |
| `secret.get`, `secret.set`, `secret.del` | Manage secrets |
| `ikey.list`, `ikey.set`, `ikey.del` | Manage installation keys |
| `org.conf.get`, `org.conf.set` | View and change organization configuration |
| `ext.request`, `ext.conf.get`, `ext.conf.set` | Manage extensions |
| `playbook.get`, `playbook.set`, `playbook.del` | Manage playbooks |
| `cloudsensor.get`, `cloudsensor.set`, `cloudsensor.del` | Manage cloud sensor adapters |
| `externaladapter.get`, `externaladapter.set`, `externaladapter.del` | Manage external adapters |

### Assigning Permissions

**For users (OAuth/JWT):**

1. Go to your organization in [app.limacharlie.io](https://app.limacharlie.io) → **Access Management** → **Users**
2. Click the Edit icon next to the user
3. Assign permissions individually or select a pre-set permission scheme

A new user starts with **Unset** privileges and sees only basic org information. Always configure the necessary permissions after you add a user. See [User Access](../7-administration/access/user-access.md) for details.

**For Organization API keys:**

1. Go to **Access Management** → **REST API**
2. Create a new API key and select the required permissions
3. Use the tables above to find which permissions to grant for your use case

> **Tip:** Obey the principle of least privilege. Grant only the permissions that your use case needs. For read-only investigation workflows, do not grant write permissions such as `dr.set` or `sensor.task`.
>
> **Note:** Permissions from [Organization Groups](../7-administration/access/user-access.md#access-via-organization-groups) add to the per-organization permissions. They cannot reduce existing access.

For the full list of available permissions, see the [Permissions Reference](../8-reference/permissions.md).

---

## Capabilities

After you connect an AI assistant, it can do these operations:

- **Query telemetry** — Search historical sensor data with LCQL
- **Investigate endpoints** — Inspect processes, network connections, files, and more
- **Manage detections** — Create and change D&R rules, YARA rules, and false positive rules
- **Take response actions** — Isolate endpoints, kill processes, manage tags
- **Search threat intelligence** — Query IOCs and map to MITRE ATT&CK
- **Configure the platform** — Manage outputs, adapters, secrets, and playbooks

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Unauthorized" error | Check that your API key and OID are correct. Make sure that the API key has the necessary permissions for the operation. The error message specifies the missing privilege. |
| Plugin not appearing | Restart Claude Code after installation. |
| OAuth login fails | Clear browser cookies for limacharlie.io and try again. |
| CLI not found (plugin) | The plugin auto-installs the `limacharlie` CLI on session start. If it fails, install manually: `pipx install limacharlie` |
| CLI not authenticated | Run `limacharlie auth login` to authenticate with browser OAuth. |
| MCP tools not loading (Options 2–3) | Check that the MCP server URL and the authentication headers are correct. |
| "Missing privilege" on specific operations | The authenticated user or API key does not have the necessary permission. See [Permission Requirements](#permission-requirements) to find which permissions to grant. |

---

## Resources

- [lc-ai Plugin Repository](https://github.com/refractionPOINT/lc-ai)
- [MCP Server Source](https://github.com/refractionPOINT/lc-mcp-server)
- [API Keys & JWT Authentication](../7-administration/access/api-keys.md)
- [User Access & Permissions](../7-administration/access/user-access.md)
- [Permissions Reference](../8-reference/permissions.md)
