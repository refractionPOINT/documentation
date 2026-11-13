# AI Providers

User AI Sessions run on Claude by default, but they are not limited to it. You can connect your own credentials for other AI providers and run sessions on their models instead, with the same tools, permissions, budgets, and session lifecycle.

Supported providers:

| Provider | Key | Authentication options | Default model when none is set |
|----------|-----|------------------------|-------------------------------|
| Anthropic Claude | `anthropic` | Claude subscription (OAuth) or Anthropic API key | Managed Claude default |
| OpenAI | `openai` | OpenAI API key, or an Azure OpenAI resource | `gpt-5.2` |
| Google Gemini | `google` | Google AI Studio API key, or a Vertex AI service account | `gemini-3.7-flash` |
| OpenRouter | `openrouter` | OpenRouter API key | `openai/gpt-5-mini` |

Everything on this page applies to **user sessions** (the AI Terminal and user-owned chats). Organization-owned agents started from D&R rules or `ai_agent` Hive records run on Claude by default; the [`ai start-session`](cli.md#limacharlie-ai-start-session) CLI's `--provider` and `--credential` overrides can launch a record's agent on any of the providers above, while storing the provider choice on the record itself is still rolling out. See [D&R-Driven Sessions](dr-sessions.md), and [Alternative AI Providers](alternative-providers.md) for running Claude through AWS Bedrock or Google Cloud Vertex AI.

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
curl -X POST https://ai.limacharlie.io/v1/credentials/openai \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-xxxxx"}'
```

**Azure OpenAI** (an enterprise-hosted OpenAI variant; sessions are routed to your deployment):

```bash
curl -X POST https://ai.limacharlie.io/v1/credentials/openai/azure \
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
curl -X POST https://ai.limacharlie.io/v1/credentials/google \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "AIzaxxxxx"}'
```

**Vertex AI** (Gemini through your Google Cloud project, using a service account JSON key):

```bash
curl -X POST https://ai.limacharlie.io/v1/credentials/google/vertex \
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
curl -X POST https://ai.limacharlie.io/v1/credentials/openrouter \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "sk-or-xxxxx"}'
```

`GET /v1/credentials` returns a `providers` map with one entry per provider:

```json
{
  "providers": {
    "anthropic":  {"has_credentials": true, "type": "oauth_token", "created_at": "2026-08-01T12:00:00Z"},
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
curl -X POST https://ai.limacharlie.io/v1/profiles \
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

- **Tools**: the terminal, shell, and file tools are available on every provider, with the same approval flow. `allowed_tools` and `denied_tools` patterns such as `Bash(cat:*)` apply identically.
- **MCP servers**: profiles' MCP server configurations work on all providers.
- **Budgets**: `max_budget_usd` is enforced on every provider; a session that reaches its budget stops accepting prompts.
- **Lifecycle**: hibernation, transparent resume, and [session forking](user-sessions.md) work the same everywhere.
- **Usage and cost tracking**: usage rows carry the provider and model, so spend can be broken down per provider and per model. See [Cost Tracking](cost-tracking.md).

- **Reasoning effort**: how long the model thinks before it answers can be set on every provider. See [Reasoning effort](#reasoning-effort) below.

A few capabilities are specific to Claude: plan mode, `bypassPermissions` (on other providers it is treated as `acceptEdits`, so tools outside `allowed_tools` still prompt), `task_budget_tokens`, Task subagents, and showing the model's thinking in the transcript. Sessions on other providers surface a clear notice when one of these is requested instead of silently ignoring it.

## Reasoning effort

Reasoning effort sets how long the model thinks before it answers. Higher levels think longer. They do better on hard investigations, but they are slower and use more tokens on your AI provider's bill. Default lets the model choose.

| Level | Value |
|-------|-------|
| Default | not set (omit the field) |
| Low | `low` |
| Medium | `medium` |
| High | `high` |
| Extra high | `xhigh` |
| Max | `max` |

Leave it unset to keep the model's own default, which is how every session behaved before the setting existed. Any other value is rejected with `400`.

Where to set it:

- On a [session profile](user-sessions.md#profile-options) (`effort`), used by every session started from that profile.
- On a single user session, with `effort` on [`POST /v1/sessions`](api-reference.md#create-session) or `--effort` on [`limacharlie ai chat`](cli.md#limacharlie-ai-chat). This overrides the profile's level for that session.
- On a [SOC bot](soc-bots.md#your-own-bots-and-groups), in its **Advanced configuration**.
- On an API session, as `effort` inside the inline `profile` of `POST /v1/api/sessions`, or with `--effort` on [`limacharlie ai start-session`](cli.md#limacharlie-ai-start-session).

Agent records in the `ai_agent` Hive and the `start ai agent` D&R action do not take a reasoning effort yet.

The level is fixed for the session's life: a session resumed from hibernation keeps it. A [fork](api-reference.md#fork-session) takes its level from the same place as its model, which is the fork's profile for Claude sessions and the source session for other providers.

### How each provider takes it

| Provider | What the session sends | A level the model lacks |
|----------|------------------------|-------------------------|
| Anthropic Claude | The Claude Agent SDK's effort setting | Most current Claude models take all five levels. Some, such as Claude Sonnet 4.6 and Claude Opus 4.6, have no Extra high and use High instead. Models that take no effort setting, such as Claude Haiku 4.5, and model IDs the runner does not recognize, such as Bedrock and Vertex model IDs, get nothing and keep their default. |
| OpenAI and Azure OpenAI | `reasoning_effort` | When the model rejects the level, the session retries one level lower until the model accepts one. When the model takes no reasoning setting at all, or rejects every level, the session sends nothing and keeps the model's default. |
| Google Gemini 3 and later | `thinking_level` | Gemini has no level above High, so Extra high and Max are sent as High. If the model rejects a level, the session steps down. |
| Google Gemini 2.5 | `thinking_budget`, a token budget that grows with the level, with Max at the model's own ceiling | If the model rejects the budget, the session steps down. Other Gemini models get nothing and keep their default. |
| OpenRouter | OpenRouter's `reasoning.effort` | OpenRouter maps the level to the upstream model's own setting, and drops it for models without one. Because OpenRouter accepts the request either way, the session reports the level it sent. |

The rule on every provider is to step down, never fail: when the model does not support the chosen level, the session uses the nearest lower level it supports, and when the model has no reasoning setting at all, the session runs at the model's default. The session does not fail because of the level.

### What the session reports

When a session has a reasoning effort, it posts one note in its activity saying what was applied. A session without one posts nothing.

| `system` subtype | Fields in `data` | When |
|------------------|------------------|------|
| `effort_set` | `effort`, `model` | The level was sent as chosen. The message reads, for example, "Reasoning effort: High". |
| `effort_adjusted` | `requested`, `effort`, `model`, `reason` | The model lacks the chosen level, so a lower one was sent, for example "Extra high reasoning effort isn't available on this model; using High." |
| `effort_skipped` | `requested`, `model`, `reason` | The model takes no reasoning setting, or the provider refused every level, so nothing was sent and the model runs at its default. |

On OpenAI, Azure OpenAI, OpenRouter and Gemini, the note usually arrives with the first answer, once the provider has accepted the request. The web application also shows a **Reasoning effort** line next to the model in the session details.

### Cost

Extra thinking is billed by your own AI provider, not by LimaCharlie: as output tokens on an API key, or against your plan's usage on a Claude subscription. The thinking tokens are counted in the session's token usage and cost, so `max_budget_usd` covers them. On SOC bots running on OpenAI, Azure OpenAI, OpenRouter or Gemini, High and above also raise the per-request output limit, so the model has room to think and still answer.

## Cost notes per provider

- **OpenAI, Google**: cost is computed from token usage at the provider's published rates, including cached-token rates where the provider reports them.
- **OpenRouter**: cost is taken from OpenRouter's own billed cost for each request, so the number you see matches what OpenRouter charges your key.
- **Azure OpenAI**: pricing is specific to your Azure resource and deployment, so LimaCharlie tracks token usage but does not estimate a dollar cost for Azure sessions.
