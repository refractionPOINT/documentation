# Alternative AI Providers

By default, AI Sessions connects to Claude through Anthropic's API using your Anthropic API key. You can also route Claude requests through **Amazon Bedrock** or **Google Cloud Vertex AI**.

This is useful when:

- Your organization already has an AWS or GCP agreement that includes Claude access
- You need to keep AI traffic within specific regions for compliance
- You want to consolidate billing through your existing cloud account

## Where to configure

Both providers can be configured at two scopes:

- **Org-scoped (D&R rules and integrations)** — the `bedrock:` / `vertex:` blocks on an `ai_agent` Hive record, or directly on a `SessionRequest`. This page is primarily about that path.
- **User-scoped (per-user BYOK sessions)** — the same provider blocks, posted to `POST /v1/auth/claude/bedrock` and `POST /v1/auth/claude/vertex`. See [User AI Sessions — Step 2: Store Claude Credentials](user-sessions.md#step-2-store-claude-credentials) for the user-side flow. The IAM, region, and model ID guidance in the rest of this page applies to that path as well — only the credential entry mechanism differs.

## Two configuration formats

There are two ways to point a session at a non-Anthropic provider:

1. **Structured provider blocks** *(recommended)* — a top-level `bedrock:` or `vertex:` block on the `ai_agent` Hive record (or on a direct `SessionRequest`). The fields are validated by the schema, secrets are resolved from Hive, and the runner translates the block into the correct environment variables for the Claude subprocess.
2. **Manual environment variables** — set `CLAUDE_CODE_USE_BEDROCK` / `CLAUDE_CODE_USE_VERTEX` and the corresponding cloud-provider variables under the profile's `environment:` map. This is the original mechanism and still works, but you have to assemble the variable names yourself.

Pick exactly one credential source per session: `anthropic_secret`, the `bedrock:` block, or the `vertex:` block. They are mutually exclusive — a session cannot mix providers.

## Amazon Bedrock

[Amazon Bedrock](https://aws.amazon.com/bedrock/) provides access to Claude models through AWS infrastructure.

### Required AWS setup

#### IAM permissions

The AWS credentials must have permissions to invoke Claude models via Bedrock. At minimum:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.*"
    }
  ]
}
```

You must also ensure that the Claude models you intend to use are [enabled in your Bedrock console](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) for the selected region.

#### Model IDs

Bedrock model IDs differ from standard Anthropic model IDs — they include a region prefix and version suffix. Set the `model` field on the profile to one of:

- `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- `us.anthropic.claude-haiku-4-5-20251001-v1:0`
- `eu.anthropic.claude-sonnet-4-5-20250929-v1:0`
- `ap.anthropic.claude-sonnet-4-5-20250929-v1:0`

The general format is `<region-prefix>.anthropic.<model-name>-v<version>:<minor>`. The region prefix (`us`, `eu`, `ap`, …) should correspond to your AWS region. Available IDs are listed in the [Bedrock model IDs documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html).

### Configuration via the `bedrock:` block (recommended)

The `bedrock` block lives at the top of an `ai_agent` Hive record, alongside `prompt`. All credential fields end with `_secret` and accept either a literal value or a `hive://secret/<name>` reference; the endpoint resolves the reference before launching the session.

```yaml
ai_agent:
  bedrock-investigator:
    data:
      prompt: "Investigate this detection..."
      lc_api_key_secret: hive://secret/lc-api-key
      model: us.anthropic.claude-sonnet-4-5-20250929-v1:0

      bedrock:
        region: us-east-1
        access_key_id_secret: hive://secret/aws-access-key-id
        secret_access_key_secret: hive://secret/aws-secret-access-key
        # Optional — only when using STS / SSO temporary credentials:
        session_token_secret: hive://secret/aws-session-token
    usr_mtd:
      enabled: true
```

#### `bedrock` field reference

| Field | Required | Description |
|---|---|---|
| `region` | Yes | AWS region where Bedrock is available (for example `us-east-1`, `us-west-2`, `eu-central-1`, `ap-southeast-2`). Sets `AWS_REGION` on the runner. |
| `access_key_id_secret` | Conditional | AWS access key ID, or a `hive://secret/<name>` reference. Sets `AWS_ACCESS_KEY_ID`. Must be paired with `secret_access_key_secret`. |
| `secret_access_key_secret` | Conditional | AWS secret access key, or a `hive://secret/<name>` reference. Sets `AWS_SECRET_ACCESS_KEY`. Must be paired with `access_key_id_secret`. |
| `session_token_secret` | No | Temporary session token from STS or SSO, or a `hive://secret/<name>` reference. Sets `AWS_SESSION_TOKEN`. Requires the access-key pair. |
| `bearer_token_secret` | Conditional | Bedrock API bearer token, or a `hive://secret/<name>` reference. Sets `AWS_BEARER_TOKEN_BEDROCK`. Used as an alternative to the access-key pair. |

You must supply **either** `(access_key_id_secret + secret_access_key_secret)` **or** `bearer_token_secret`. The schema rejects records that set neither, and rejects setting only one of the access-key pair.

When the runner accepts the block, it sets `CLAUDE_CODE_USE_BEDROCK=1` automatically — you do not need to add it yourself.

### Direct `SessionRequest` (API and integrations)

The same provider block is exposed on the AI Sessions `SessionRequest` type used by the org-scoped API and by integrations that build sessions programmatically. The field names drop the `_secret` suffix because the values are already-resolved literals at that point:

```json
{
  "prompt": "Investigate this detection...",
  "bedrock": {
    "region": "us-east-1",
    "access_key_id": "AKIA…",
    "secret_access_key": "…",
    "session_token": "…",
    "bearer_token": "…"
  },
  "profile": {
    "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "allowed_tools": ["Bash", "Read", "Grep", "Glob", "WebFetch"]
  }
}
```

Validation enforces exactly one of `anthropic_key`, `bedrock`, or `vertex` per request, plus the same per-block rules listed above.

### Configuration via environment variables (manual mode)

The original mechanism — setting AWS variables under the profile's `environment:` map — still works. The runner forwards every entry of `environment:` to the Claude subprocess as-is, so the cloud-provider variables get picked up there.

Use this only if you cannot use the structured `bedrock:` block (for example, an older endpoint that does not yet honour the block).

```yaml
ai_agent:
  bedrock-investigator:
    data:
      prompt: "Investigate this detection..."
      anthropic_secret: hive://secret/anthropic-key  # placeholder, see note below
      lc_api_key_secret: hive://secret/lc-api-key
      model: us.anthropic.claude-sonnet-4-5-20250929-v1:0
      environment:
        CLAUDE_CODE_USE_BEDROCK: "1"
        AWS_ACCESS_KEY_ID: hive://secret/aws-access-key-id
        AWS_SECRET_ACCESS_KEY: hive://secret/aws-secret-access-key
        AWS_REGION: us-east-1
    usr_mtd:
      enabled: true
```

| Variable | Description |
|---|---|
| `CLAUDE_CODE_USE_BEDROCK` | Must be set to `1` to enable Bedrock. |
| `AWS_ACCESS_KEY_ID` | AWS access key ID with Bedrock permissions. |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key. |
| `AWS_REGION` | AWS region, matching the model ID's region prefix. |
| `AWS_SESSION_TOKEN` | *(optional)* STS/SSO temporary session token. |
| `AWS_BEARER_TOKEN_BEDROCK` | *(optional)* Bedrock API bearer token, alternative to access keys. |

> When using the manual environment-variable form, the schema still requires `anthropic_secret` to be set on the record. Point it at a `hive://secret/<name>` containing any non-empty placeholder — the runner ignores it once `CLAUDE_CODE_USE_BEDROCK=1` is in the environment.

## Google Cloud Vertex AI

[Google Cloud Vertex AI](https://cloud.google.com/vertex-ai) provides access to Claude models through GCP. Authentication uses a service-account JSON key with the appropriate Vertex AI permissions.

### Required GCP setup

1. Enable the Vertex AI API in your project.
2. Subscribe to the Claude models you intend to use in [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden).
3. Create a service account with at least the `roles/aiplatform.user` role (or a custom role permitting `aiplatform.endpoints.predict`).
4. Generate and download a JSON key for that service account.

### Model IDs and region

Vertex uses Claude model IDs in the form Anthropic ships them on the platform — typically `claude-<model>@<version>`, for example `claude-sonnet-4-5@20250929`. Confirm the IDs available in your project against the [Vertex Model Garden listings](https://console.cloud.google.com/vertex-ai/model-garden).

The region you set must be one that Anthropic publishes models to (commonly `global`, `us-east5`, or `europe-west1`). Cross-check with the [Anthropic on Vertex AI documentation](https://docs.anthropic.com/en/api/claude-on-vertex-ai) for current region availability.

### Configuration via the `vertex:` block (recommended)

```yaml
ai_agent:
  vertex-investigator:
    data:
      prompt: "Investigate this detection..."
      lc_api_key_secret: hive://secret/lc-api-key
      model: claude-sonnet-4-5@20250929

      vertex:
        project_id: my-gcp-project
        region: us-east5
        service_account_json_secret: hive://secret/vertex-service-account
    usr_mtd:
      enabled: true
```

#### `vertex` field reference

| Field | Required | Description |
|---|---|---|
| `project_id` | Yes | GCP project ID hosting the Vertex AI subscription. Sets `ANTHROPIC_VERTEX_PROJECT_ID`. |
| `region` | Yes | Vertex region (`global`, `us-east5`, `europe-west1`, …). Sets `CLOUD_ML_REGION`. |
| `service_account_json_secret` | Yes | Full service-account JSON key contents, or a `hive://secret/<name>` reference to a secret holding the JSON. |

The runner writes the resolved service-account JSON to a per-session temporary file (mode `0600`, removed when the process exits) and points `GOOGLE_APPLICATION_CREDENTIALS` at it. It also sets `CLAUDE_CODE_USE_VERTEX=1` automatically.

> Store the entire service-account JSON in a single Hive Secret and reference it via `hive://secret/<name>`. The JSON contains a private key — never paste it as a literal into a record or D&R rule.

### Direct `SessionRequest` (API and integrations)

```json
{
  "prompt": "Investigate this detection...",
  "vertex": {
    "project_id": "my-gcp-project",
    "region": "us-east5",
    "service_account_json": "{\"type\":\"service_account\",\"project_id\":\"…\",\"private_key\":\"…\"}"
  },
  "profile": {
    "model": "claude-sonnet-4-5@20250929"
  }
}
```

`service_account_json` is the literal JSON document for the service-account key — typically the entire contents of the file you downloaded from GCP, embedded as a JSON string.

### Configuration via environment variables (manual mode)

If you must configure Vertex through the profile `environment:` map instead of the structured `vertex:` block, set the variables the runner would otherwise set on your behalf. Note that you cannot inline the service-account JSON as an environment variable — you have to mount it as a file at a known path inside the runner image and point `GOOGLE_APPLICATION_CREDENTIALS` at that path. Most users do not have a way to do that, which is why the structured `vertex:` block is the supported path.

| Variable | Description |
|---|---|
| `CLAUDE_CODE_USE_VERTEX` | Must be set to `1` to enable Vertex. |
| `ANTHROPIC_VERTEX_PROJECT_ID` | GCP project ID for the Vertex subscription. |
| `CLOUD_ML_REGION` | Vertex region. |
| `GOOGLE_APPLICATION_CREDENTIALS` | Filesystem path to the service-account JSON key. |

## Storing credentials securely

Always store cloud-provider credentials in [Hive Secrets](../7-administration/config-hive/secrets.md) and reference them via `hive://secret/<name>`. Treat the Vertex service-account JSON as a single secret (don't try to split it into multiple fields). For Bedrock, store the access key, secret key, and any session token as separate secrets.

The endpoint resolves `hive://secret/<name>` references just before sending the request to AI Sessions, so secret contents never appear in D&R rules, `argv`, or session metadata.

## Notes

- When using Bedrock or Vertex through the structured block, you do **not** need to set `anthropic_secret`. The schema accepts a record with `bedrock:` or `vertex:` and no `anthropic_secret`. Only the manual environment-variable mode still requires a placeholder `anthropic_secret`.
- Claude model availability varies by AWS region and Vertex region. Check the [Bedrock model availability page](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) and [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) before picking a region.
- Billing for Claude usage goes through your AWS or GCP account when using these providers, not through Anthropic directly.
- The provider you choose only affects the Claude API path. LimaCharlie data, MCP servers, the LC CLI, tool execution, and session storage are unaffected.
