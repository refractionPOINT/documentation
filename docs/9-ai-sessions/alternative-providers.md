# Alternative AI Providers

By default, AI Sessions connects to Claude through the Anthropic API with your Anthropic API key. You can also send Claude requests through **Amazon Bedrock** or **Google Cloud Vertex AI**.

This is useful when:

- Your organization already has an AWS or GCP agreement that includes Claude access
- You must keep AI traffic in specific regions for compliance
- You want one bill through your existing cloud account

## Two configuration formats

There are two ways to point a session at a non-Anthropic provider:

1. **Structured provider blocks** *(recommended)* — a top-level `bedrock:` or `vertex:` block on the `ai_agent` Hive record, or on a direct `SessionRequest`. The schema validates the fields, the endpoint resolves secrets from Hive, and the runner translates the block into the correct environment variables for the Claude subprocess.
2. **Manual environment variables** — set `CLAUDE_CODE_USE_BEDROCK` / `CLAUDE_CODE_USE_VERTEX` and the related variables of the cloud provider in the `environment:` map of the profile. This is the original mechanism and it still works, but you must assemble the variable names yourself.

Select exactly one credential source for each session: `anthropic_secret`, the `bedrock:` block, or the `vertex:` block. These sources are mutually exclusive. A session cannot use more than one provider.

## Amazon Bedrock

[Amazon Bedrock](https://aws.amazon.com/bedrock/) gives access to Claude models through AWS infrastructure.

### Required AWS setup

#### IAM permissions

The AWS credentials must have permissions to invoke Claude models through Bedrock. The minimum is:

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

Also make sure that the Claude models that you plan to use are [enabled in your Bedrock console](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html) for the selected region.

#### Model IDs

Bedrock model IDs are different from standard Anthropic model IDs. They include a region prefix and a version suffix. Set the `model` field on the profile to one of these values:

- `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- `us.anthropic.claude-haiku-4-5-20251001-v1:0`
- `eu.anthropic.claude-sonnet-4-5-20250929-v1:0`
- `ap.anthropic.claude-sonnet-4-5-20250929-v1:0`

The general format is `<region-prefix>.anthropic.<model-name>-v<version>:<minor>`. The region prefix (`us`, `eu`, `ap`, …) should match your AWS region. The [Bedrock model IDs documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html) lists the available IDs.

### Configuration via the `bedrock:` block (recommended)

The `bedrock` block is at the top of an `ai_agent` Hive record, next to `prompt`. All credential fields end with `_secret`. Each field accepts a literal value or a `hive://secret/<name>` reference. The endpoint resolves the reference before it starts the session.

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
| `access_key_id_secret` | Conditional | AWS access key ID, or a `hive://secret/<name>` reference. Sets `AWS_ACCESS_KEY_ID`. Must be used with `secret_access_key_secret`. |
| `secret_access_key_secret` | Conditional | AWS secret access key, or a `hive://secret/<name>` reference. Sets `AWS_SECRET_ACCESS_KEY`. Must be used with `access_key_id_secret`. |
| `session_token_secret` | No | Temporary session token from STS or SSO, or a `hive://secret/<name>` reference. Sets `AWS_SESSION_TOKEN`. Needs the access-key pair. |
| `bearer_token_secret` | Conditional | Bedrock API bearer token, or a `hive://secret/<name>` reference. Sets `AWS_BEARER_TOKEN_BEDROCK`. Use it as an alternative to the access-key pair. |

You must give **either** `(access_key_id_secret + secret_access_key_secret)` **or** `bearer_token_secret`. The schema rejects a record that sets neither. It also rejects a record that sets only one field of the access-key pair.

When the runner accepts the block, it sets `CLAUDE_CODE_USE_BEDROCK=1` automatically. You do not need to add it yourself.

### Direct `SessionRequest` (API and integrations)

The same provider block is available on the AI Sessions `SessionRequest` type. The org-scoped API uses this type, and so do integrations that build sessions with code. The field names have no `_secret` suffix, because the values are already resolved literals:

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

Validation permits exactly one of `anthropic_key`, `bedrock`, or `vertex` in each request. The rules for each block above also apply.

### Configuration via environment variables (manual mode)

The original mechanism still works: set the AWS variables in the `environment:` map of the profile. The runner sends every entry of `environment:` to the Claude subprocess without change, and the Claude subprocess reads the variables of the cloud provider there.

Use this mode only if you cannot use the structured `bedrock:` block. An example is an older endpoint that does not obey the block.

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
| `AWS_REGION` | AWS region. It must match the region prefix of the model ID. |
| `AWS_SESSION_TOKEN` | *(optional)* STS/SSO temporary session token. |
| `AWS_BEARER_TOKEN_BEDROCK` | *(optional)* Bedrock API bearer token, alternative to access keys. |

> The schema still needs `anthropic_secret` on the record when you use the manual environment-variable form. Point it at a `hive://secret/<name>` that contains any placeholder that is not empty. The runner ignores this value when `CLAUDE_CODE_USE_BEDROCK=1` is in the environment.

## Google Cloud Vertex AI

[Google Cloud Vertex AI](https://cloud.google.com/vertex-ai) gives access to Claude models through GCP. Authentication uses a service-account JSON key that has the necessary Vertex AI permissions.

### Required GCP setup

1. Enable the Vertex AI API in your project.
2. Subscribe to the Claude models that you plan to use in [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden).
3. Create a service account with the `roles/aiplatform.user` role as a minimum, or with a custom role that allows `aiplatform.endpoints.predict`.
4. Generate a JSON key for that service account. Download the key.

### Model IDs and region

Vertex uses the Claude model IDs in the form that Anthropic supplies on the platform. The usual form is `claude-<model>@<version>`, for example `claude-sonnet-4-5@20250929`. Check the IDs that are available in your project against the [Vertex Model Garden listings](https://console.cloud.google.com/vertex-ai/model-garden).

The region that you set must be a region where Anthropic publishes models (usually `global`, `us-east5`, or `europe-west1`). For the current region availability, see the [Anthropic on Vertex AI documentation](https://docs.anthropic.com/en/api/claude-on-vertex-ai).

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
| `project_id` | Yes | GCP project ID that hosts the Vertex AI subscription. Sets `ANTHROPIC_VERTEX_PROJECT_ID`. |
| `region` | Yes | Vertex region (`global`, `us-east5`, `europe-west1`, …). Sets `CLOUD_ML_REGION`. |
| `service_account_json_secret` | Yes | Full service-account JSON key contents, or a `hive://secret/<name>` reference to a secret that holds the JSON. |

The runner writes the resolved service-account JSON to a temporary file for each session (mode `0600`, removed when the process exits). It points `GOOGLE_APPLICATION_CREDENTIALS` at this file. It also sets `CLAUDE_CODE_USE_VERTEX=1` automatically.

> Store the entire service-account JSON in one Hive Secret and refer to it with `hive://secret/<name>`. Never paste the JSON as a literal into a record or a D&R rule, because the JSON contains a private key.

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

`service_account_json` is the literal JSON document of the service-account key. Usually it is the full contents of the file that you downloaded from GCP, as a JSON string.

### Configuration via environment variables (manual mode)

If you must configure Vertex with the `environment:` map of the profile instead of the structured `vertex:` block, set the variables that the runner sets for you. You cannot put the service-account JSON in an environment variable. You must mount it as a file at a known path in the runner image, then point `GOOGLE_APPLICATION_CREDENTIALS` at that path. Most users cannot do this, so the structured `vertex:` block is the supported path.

| Variable | Description |
|---|---|
| `CLAUDE_CODE_USE_VERTEX` | Must be set to `1` to enable Vertex. |
| `ANTHROPIC_VERTEX_PROJECT_ID` | GCP project ID for the Vertex subscription. |
| `CLOUD_ML_REGION` | Vertex region. |
| `GOOGLE_APPLICATION_CREDENTIALS` | Filesystem path to the service-account JSON key. |

## Storing credentials securely

Always store the credentials of the cloud provider in [Hive Secrets](../7-administration/config-hive/secrets.md) and refer to them with `hive://secret/<name>`. Keep the Vertex service-account JSON as one secret. Do not divide it into more than one field. For Bedrock, store the access key, the secret key, and any session token as separate secrets.

The endpoint resolves `hive://secret/<name>` references immediately before it sends the request to AI Sessions. Thus the contents of a secret never appear in D&R rules, `argv`, or session metadata.

## Notes

- When you use Bedrock or Vertex through the structured block, you do **not** need to set `anthropic_secret`. The schema accepts a record that has `bedrock:` or `vertex:` and no `anthropic_secret`. Only the manual environment-variable mode still needs a placeholder `anthropic_secret`.
- The availability of Claude models is different in each AWS region and each Vertex region. Check the [Bedrock model availability page](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) and [Vertex AI Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) before you select a region.
- With these providers, the bill for Claude use goes to your AWS or GCP account, not to Anthropic.
- The provider that you select changes only the path to the Claude API. It does not change LimaCharlie data, MCP servers, the LC CLI, tool execution, or session storage.
