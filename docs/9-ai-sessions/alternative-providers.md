# Alternative AI Providers

By default, AI Sessions connects to Claude through Anthropic's API using your Anthropic API key. However, you can configure sessions to route Claude requests through alternative providers such as **Amazon Bedrock** or **Google Cloud Vertex AI**.

This is useful when:

- Your organization already has an AWS or GCP agreement that includes Claude access
- You need to keep AI traffic within specific cloud regions for compliance
- You want to consolidate billing through your existing cloud account

For Hive `ai_agent` records, both providers are supported as **first-class** alternatives via dedicated `bedrock` and `vertex` configuration blocks. When set, the consumer automatically configures the underlying environment variables (`CLAUDE_CODE_USE_BEDROCK`, `CLAUDE_CODE_USE_VERTEX`, etc.) on the Claude subprocess. The two blocks are mutually exclusive.

For interactive Profiles and inline D&R `profile:` blocks, the same behaviour can be achieved by setting the `model` and `environment` variables directly, as shown below.

## Amazon Bedrock

[Amazon Bedrock](https://aws.amazon.com/bedrock/) provides access to Claude models through AWS infrastructure.

### Model

You must set the `model` field to a Bedrock model ID. Bedrock model IDs differ from standard Anthropic model IDs — they include a region prefix and version suffix:

| Profile field | Example value |
|---------------|---------------|
| `model` | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |

The general format is `<region-prefix>.anthropic.<model-name>-v<version>:<minor>`. Available model IDs can be found in the [Bedrock model IDs documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html). Common examples:

- `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- `us.anthropic.claude-haiku-4-5-20251001-v1:0`
- `eu.anthropic.claude-sonnet-4-5-20250929-v1:0`
- `ap.anthropic.claude-sonnet-4-5-20250929-v1:0`

The region prefix in the model ID (e.g., `us`, `eu`, `ap`) should correspond to the AWS region you are calling.

### AWS IAM Permissions

The AWS credentials must have permissions to invoke Claude models via Bedrock. At minimum, the IAM policy should include:

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

### Configuration — AI Agent Hive Record (recommended)

When using definition mode with a Hive `ai_agent` record, set the `bedrock` block. The consumer resolves the secrets and injects `CLAUDE_CODE_USE_BEDROCK=1`, `AWS_REGION`, and the AWS credential variables on your behalf:

```yaml
ai_agent:
  bedrock-investigator:
    data:
      prompt: "Investigate this detection..."
      lc_api_key_secret: hive://secret/lc-api-key
      model: us.anthropic.claude-sonnet-4-5-20250929-v1:0
      bedrock:
        region: us-east-1
        access_key_id_secret: hive://secret/aws-access-key
        secret_access_key_secret: hive://secret/aws-secret-key
        # session_token_secret: hive://secret/aws-session-token   # optional, STS/SSO
    usr_mtd:
      enabled: true
```

A Bedrock API key may be used instead of an IAM key pair:

```yaml
ai_agent:
  bedrock-investigator:
    data:
      prompt: "Investigate this detection..."
      model: us.anthropic.claude-sonnet-4-5-20250929-v1:0
      bedrock:
        region: us-east-1
        bearer_token_secret: hive://secret/bedrock-api-key
```

Validation rules:

- `region` is required.
- Either `access_key_id_secret` + `secret_access_key_secret` **or** `bearer_token_secret` must be set.
- `session_token_secret` may be combined with the access-key pair only.
- `bedrock` and `vertex` are mutually exclusive.
- When `bedrock` is set, `anthropic_secret` is not required.

### Configuration — Interactive Profile

Profiles can be configured through the LimaCharlie web app (under AI Sessions > Profiles) or via the API. Profiles use the generic `environment` map directly:

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/profiles \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bedrock Investigation",
    "description": "Investigation profile using AWS Bedrock",
    "model": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "environment": {
      "CLAUDE_CODE_USE_BEDROCK": "1",
      "AWS_ACCESS_KEY_ID": "hive://secret/aws-access-key",
      "AWS_SECRET_ACCESS_KEY": "hive://secret/aws-secret-key",
      "AWS_REGION": "us-east-1"
    },
    "allowed_tools": ["Bash", "Read", "Grep", "Glob", "WebFetch"],
    "max_turns": 100
  }'
```

### Configuration — Inline D&R Profile

```yaml
respond:
  - action: start ai agent
    prompt: "Investigate this detection..."
    anthropic_secret: hive://secret/anthropic-key
    profile:
      model: us.anthropic.claude-sonnet-4-5-20250929-v1:0
      environment:
        CLAUDE_CODE_USE_BEDROCK: "1"
        AWS_ACCESS_KEY_ID: hive://secret/aws-access-key
        AWS_SECRET_ACCESS_KEY: hive://secret/aws-secret-key
        AWS_REGION: us-east-1
```

### Notes

- Claude model availability varies by AWS region. Check the [Bedrock model availability page](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) to confirm your desired model is available in your selected region.
- Billing for Claude usage goes through your AWS account when using Bedrock, not through Anthropic directly.
- For inline D&R profiles, the `anthropic_secret` field is still required by the schema even when routing through Bedrock — set it to a placeholder value in your Hive secret. AI Agent Hive records do not have this requirement when the `bedrock` block is set.

## Google Cloud Vertex AI

[Vertex AI](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude) provides access to Claude models through Google Cloud infrastructure.

### Model

Vertex model IDs use the plain Anthropic naming convention (no provider prefix), with an optional dated revision suffix:

| Profile field | Example value |
|---------------|---------------|
| `model` | `claude-sonnet-4-5@20250929` |

Common examples:

- `claude-sonnet-4-5@20250929`
- `claude-haiku-4-5@20251001`
- `claude-opus-4-7`

Append `[1m]` (e.g., `claude-sonnet-4-6[1m]`) on supported models to enable the 1M-token context window.

### GCP IAM Permissions

The service account used to invoke Vertex AI must hold a role granting `aiplatform.endpoints.predict`. The pre-defined `roles/aiplatform.user` role is sufficient. You must also:

1. Enable the **Vertex AI API** (`aiplatform.googleapis.com`) on the project.
2. Request access to each Claude model you intend to use through the Vertex AI **Model Garden** (approval can take 24–48 hours).

### Region

`region` corresponds to `CLOUD_ML_REGION`. Valid values include the multi-region endpoints (`global`, `us`, `eu`) and specific regions (`us-east5`, `europe-west1`, etc.). Not every model is available on every endpoint type — check the **Supported features** column in Model Garden. A `404` response usually indicates a region/model mismatch.

### Configuration — AI Agent Hive Record (recommended)

When using definition mode with a Hive `ai_agent` record, set the `vertex` block. The consumer resolves the service-account JSON, writes it to a temp file referenced by `GOOGLE_APPLICATION_CREDENTIALS`, and injects `CLAUDE_CODE_USE_VERTEX=1`, `ANTHROPIC_VERTEX_PROJECT_ID`, and `CLOUD_ML_REGION` on your behalf:

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
        service_account_json_secret: hive://secret/vertex-sa-json
    usr_mtd:
      enabled: true
```

The secret referenced by `service_account_json_secret` must hold the **full JSON contents** of a Google Cloud service account key (not a path). Generate one with:

```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=claude-vertex@my-gcp-project.iam.gserviceaccount.com
```

…then store the contents of `key.json` in a Hive secret.

Validation rules:

- `project_id`, `region`, and `service_account_json_secret` are all required.
- `bedrock` and `vertex` are mutually exclusive.
- When `vertex` is set, `anthropic_secret` is not required.

### Configuration — Interactive Profile

Profiles use the generic `environment` map directly. Because Vertex requires a JSON key file on disk, store the JSON contents in a Hive secret and reference it via the `GOOGLE_APPLICATION_CREDENTIALS_JSON` variable that the runner unpacks for you:

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/profiles \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vertex Investigation",
    "description": "Investigation profile using GCP Vertex AI",
    "model": "claude-sonnet-4-5@20250929",
    "environment": {
      "CLAUDE_CODE_USE_VERTEX": "1",
      "ANTHROPIC_VERTEX_PROJECT_ID": "my-gcp-project",
      "CLOUD_ML_REGION": "us-east5",
      "GOOGLE_APPLICATION_CREDENTIALS_JSON": "hive://secret/vertex-sa-json"
    },
    "allowed_tools": ["Bash", "Read", "Grep", "Glob", "WebFetch"],
    "max_turns": 100
  }'
```

### Configuration — Inline D&R Profile

```yaml
respond:
  - action: start ai agent
    prompt: "Investigate this detection..."
    anthropic_secret: hive://secret/anthropic-key
    profile:
      model: claude-sonnet-4-5@20250929
      environment:
        CLAUDE_CODE_USE_VERTEX: "1"
        ANTHROPIC_VERTEX_PROJECT_ID: my-gcp-project
        CLOUD_ML_REGION: us-east5
        GOOGLE_APPLICATION_CREDENTIALS_JSON: hive://secret/vertex-sa-json
```

### Notes

- Claude model availability varies by Vertex AI region. Refer to the [Vertex AI Claude model documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/partner-models/use-claude) for current availability.
- Billing for Claude usage goes through your GCP project when using Vertex, not through Anthropic directly.
- For inline D&R profiles, the `anthropic_secret` field is still required by the schema even when routing through Vertex — set it to a placeholder value in your Hive secret. AI Agent Hive records do not have this requirement when the `vertex` block is set.

## Storing Credentials Securely

Always store provider credentials in [Hive Secrets](../7-administration/config-hive/secrets.md) rather than hardcoding them in profiles or D&R rules. The `_secret` suffix on each field indicates that a `hive://secret/<name>` reference is accepted (and recommended) in addition to literal values.
