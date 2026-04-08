# Alternative AI Providers

By default, AI Sessions connects to Claude through Anthropic's API using your Anthropic API key. However, you can configure sessions to route Claude requests through alternative providers such as **Amazon Bedrock**.

This is useful when:

- Your organization already has an AWS agreement that includes Claude access
- You need to keep AI traffic within specific AWS regions for compliance
- You want to consolidate billing through your existing AWS account

## Amazon Bedrock

[Amazon Bedrock](https://aws.amazon.com/bedrock/) provides access to Claude models through AWS infrastructure. To use Bedrock as the AI provider for your sessions, you configure AWS credentials and a feature flag via environment variables.

### Requirements

You need to configure both environment variables and a profile-level `model` setting.

#### Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_CODE_USE_BEDROCK` | Set to `1` to enable Bedrock as the AI provider. |
| `AWS_ACCESS_KEY_ID` | Your AWS access key ID with Bedrock permissions. |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret access key. |
| `AWS_REGION` | The AWS region where Bedrock is available (e.g., `us-east-1`, `us-west-2`, `ap-southeast-2`). |

#### Model

You must also set the `model` field in the profile to a Bedrock model ID. Bedrock model IDs differ from standard Anthropic model IDs — they include a region prefix and version suffix:

| Profile field | Example value |
|---------------|---------------|
| `model` | `us.anthropic.claude-sonnet-4-5-20250929-v1:0` |

The general format is `<region-prefix>.anthropic.<model-name>-v<version>:<minor>`. Available model IDs can be found in the [Bedrock model IDs documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html). Common examples:

- `us.anthropic.claude-sonnet-4-5-20250929-v1:0`
- `us.anthropic.claude-haiku-4-5-20251001-v1:0`
- `eu.anthropic.claude-sonnet-4-5-20250929-v1:0`
- `ap.anthropic.claude-sonnet-4-5-20250929-v1:0`

The region prefix in the model ID (e.g., `us`, `eu`, `ap`) should correspond to your `AWS_REGION`.

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

### Configuration

Set the model and environment variables in your session profile. These can be configured in both interactive (user) and headless (D&R-driven) sessions.

#### Interactive Sessions (Profile)

Profiles can be configured through the LimaCharlie web app (under AI Sessions > Profiles) or via the API. When creating or updating a profile, set the Bedrock model and environment variables:

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
      "AWS_ACCESS_KEY_ID": "AKIAIOSFODNN7EXAMPLE",
      "AWS_SECRET_ACCESS_KEY": "hive://secret/aws-secret-key",
      "AWS_REGION": "us-east-1"
    },
    "allowed_tools": ["Bash", "Read", "Grep", "Glob", "WebFetch"],
    "max_turns": 100
  }'
```

#### D&R-Driven Sessions (Inline Profile)

Include the environment variables in the inline profile of your D&R rule:

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

#### D&R-Driven Sessions (AI Agent Hive Record)

When using definition mode with a Hive AI agent record, set the model and environment variables in the record:

```yaml
ai_agent:
  bedrock-investigator:
    data:
      prompt: "Investigate this detection..."
      anthropic_secret: hive://secret/anthropic-key
      lc_api_key_secret: hive://secret/lc-api-key
      model: us.anthropic.claude-sonnet-4-5-20250929-v1:0
      environment:
        CLAUDE_CODE_USE_BEDROCK: "1"
        AWS_ACCESS_KEY_ID: hive://secret/aws-access-key
        AWS_SECRET_ACCESS_KEY: hive://secret/aws-secret-key
        AWS_REGION: us-east-1
    usr_mtd:
      enabled: true
```

### Storing Credentials Securely

Always store AWS credentials in [Hive Secrets](../7-administration/config-hive/secrets.md) rather than hardcoding them in profiles or D&R rules:

```yaml
environment:
  CLAUDE_CODE_USE_BEDROCK: "1"
  AWS_ACCESS_KEY_ID: hive://secret/aws-access-key-id
  AWS_SECRET_ACCESS_KEY: hive://secret/aws-secret-access-key
  AWS_REGION: us-east-1
```

### Notes

- When using Bedrock, you do **not** need to store an Anthropic API key for user sessions. However, for D&R-driven sessions the `anthropic_secret` field is still required by the schema — you can set it to a placeholder value in your Hive secret.
- Claude model availability varies by AWS region. Check the [Bedrock model availability page](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) to confirm your desired model is available in your selected region.
- Billing for Claude usage goes through your AWS account when using Bedrock, not through Anthropic directly.
