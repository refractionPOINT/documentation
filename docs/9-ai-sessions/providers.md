# AI Providers

User AI Sessions run on Claude by default, but they are not limited to it. You can connect your own credentials for other AI providers and run sessions on their models instead, with the same tools, permissions, budgets, and session lifecycle.

Supported providers:

| Provider | Key | Authentication options | Default model when none is set |
|----------|-----|------------------------|-------------------------------|
| Anthropic Claude | `anthropic` | Claude subscription (OAuth) or Anthropic API key | Managed Claude default |
| OpenAI | `openai` | OpenAI API key, or an Azure OpenAI resource | `gpt-5.2` |
| Google Gemini | `google` | Google AI Studio API key, or a Vertex AI service account | `gemini-3.7-flash` |
| OpenRouter | `openrouter` | OpenRouter API key | `openai/gpt-5-mini` |

Everything on this page applies to **user sessions** (the AI Terminal and user-owned chats). Organization-owned agents started from D&R rules or `ai_agent` Hive records currently run on Claude; see [D&R-Driven Sessions](dr-sessions.md) and [Alternative AI Providers](alternative-providers.md) for running Claude through AWS Bedrock or Google Cloud Vertex AI.

Credentials are bring-your-own-key: LimaCharlie stores them encrypted, bound to your user identity, and uses them only to run your sessions. You are billed directly by the provider. You can connect several providers at the same time and pick one per session profile.

## Connecting a provider

### In the web application

Go to **User Settings → AI Terminal**. Each supported provider has a row with its connection status and a **Connect** button that opens a form for that provider's credentials. Connected providers can be disconnected from the same place at any time.

### Via the API

Each provider has its own credential endpoint. All requests use your LimaCharlie JWT, the same as every other AI Sessions API call.

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/v1/credentials` | GET | Status of all connected providers |
| `/v1/credentials/openai` | POST / DELETE | Store or delete an OpenAI API key |
| `/v1/credentials/openai/azure` | POST | Store an Azure OpenAI configuration |
| `/v1/credentials/google` | POST / DELETE | Store or delete a Google AI Studio API key |
| `/v1/credentials/google/vertex` | POST | Store a Vertex AI service account for Gemini |
| `/v1/credentials/openrouter` | POST / DELETE | Store or delete an OpenRouter API key |

Claude credentials keep their existing endpoints under `/v1/auth/claude/*`; see [User Sessions](user-sessions.md#getting-started).

**OpenAI** (keys start with `sk-`; `org_id` and `project_id` are optional):

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/credentials/openai \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-xxxxx"}'
```

**Azure OpenAI** (an enterprise-hosted OpenAI variant; sessions are routed to your deployment):

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/credentials/openai/azure \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "https://my-resource.openai.azure.com",
    "deployment_name": "gpt-5-deploy",
    "api_version": "2024-10-21",
    "api_key": "xxxxx"
  }'
```

**Google AI Studio** (both the classic `AIza...` keys and the newer `AQ.`-prefixed keys are accepted):

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/credentials/google \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "AIzaxxxxx"}'
```

**Vertex AI** (Gemini through your Google Cloud project, using a service account JSON key):

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/credentials/google/vertex \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "my-gcp-project",
    "region": "us-central1",
    "service_account_json": "{...service account key JSON...}"
  }'
```

**OpenRouter** (keys start with `sk-or-`; one key gives access to OpenRouter's whole model catalog, with models named by vendor prefix such as `openai/gpt-5-mini` or `anthropic/claude-sonnet-4-6`):

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/credentials/openrouter \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-or-xxxxx"}'
```

`GET /v1/credentials` returns a `providers` map with one entry per provider:

```json
{
  "providers": {
    "anthropic":  {"has_credentials": true, "type": "oauth", "created_at": "2026-08-01T12:00:00Z"},
    "openai":     {"has_credentials": true, "type": "api_key", "created_at": "2026-08-10T09:30:00Z"},
    "google":     {"has_credentials": false},
    "openrouter": {"has_credentials": false}
  }
}
```

`DELETE` on a provider's endpoint removes the stored credential immediately. Storing a new credential for a provider replaces the previous one.

## Choosing a provider for a session

Provider selection rides on [session profiles](user-sessions.md#session-profiles). A profile can set:

- `provider`: one of `anthropic`, `openai`, `google`, `openrouter`. When omitted, the profile uses Claude.
- `model`: a model identifier valid for that provider. When omitted, the provider's default model from the table above is used. Azure OpenAI is the exception: the model is whatever your configured deployment serves, so `model` is not used for routing.

A `provider` passed directly on a session creation request overrides the profile's value. Creating a session on a provider you have not connected fails with an explicit error rather than falling back to another provider.

For example, a profile that runs sessions on Gemini:

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/profiles \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gemini triage",
    "provider": "google",
    "model": "gemini-3.7-flash",
    "max_budget_usd": 2.0
  }'
```

## What works on every provider

Sessions behave the same regardless of provider:

- **Tools**: the terminal, shell, and file tools are available on every provider, with the same permission and approval model. `allowed_tools` patterns such as `Bash(cat:*)` apply identically.
- **MCP servers**: profiles' MCP server configurations work on all providers.
- **Budgets**: `max_budget_usd` is enforced on every provider; a session that reaches its budget stops accepting prompts.
- **Lifecycle**: hibernation, transparent resume, and [session forking](user-sessions.md) work the same everywhere.
- **Usage and cost tracking**: usage rows carry the provider and model, so spend can be broken down per provider and per model. See [Cost Tracking](cost-tracking.md).

A few capabilities are specific to Claude: plan mode, Task subagents, and extended thinking. Sessions on other providers surface a clear notice when one of these is requested instead of silently ignoring it.

## Cost notes per provider

- **OpenAI, Google**: cost is computed from token usage at the provider's published rates, including cached-token rates where the provider reports them.
- **OpenRouter**: cost is taken from OpenRouter's own billed cost for each request, so the number you see matches what OpenRouter charges your key.
- **Azure OpenAI**: pricing is specific to your Azure resource and deployment, so LimaCharlie tracks token usage but does not estimate a dollar cost for Azure sessions.
