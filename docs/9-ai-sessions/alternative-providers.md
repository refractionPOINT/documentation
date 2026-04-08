# Alternative AI Providers

By default, AI Sessions connects to Claude through Anthropic's API using your Anthropic API key. However, you can configure sessions to route Claude requests through alternative providers such as **Amazon Bedrock**.

This is useful when:

- Your organization already has an AWS agreement that includes Claude access
- You need to keep AI traffic within specific AWS regions for compliance
- You want to consolidate billing through your existing AWS account

## Amazon Bedrock

[Amazon Bedrock](https://aws.amazon.com/bedrock/) provides access to Claude models through AWS infrastructure. To use Bedrock as the AI provider for your sessions, you configure AWS credentials and a feature flag via environment variables.

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_CODE_USE_BEDROCK` | Set to `1` to enable Bedrock as the AI provider. |
| `AWS_ACCESS_KEY_ID` | Your AWS access key ID with Bedrock permissions. |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret access key. |
| `AWS_REGION` | The AWS region where Bedrock is available (e.g., `us-east-1`, `us-west-2`, `ap-southeast-2`). |

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

Set the environment variables in your session profile. These can be configured in both interactive (user) and headless (D&R-driven) sessions.

#### Interactive Sessions (Profile)

When creating or updating a profile, include the Bedrock environment variables:

```bash
curl -X POST https://ai-sessions.limacharlie.io/v1/profiles \
  -H "Authorization: Bearer $LC_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bedrock Investigation",
    "description": "Investigation profile using AWS Bedrock",
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
      environment:
        CLAUDE_CODE_USE_BEDROCK: "1"
        AWS_ACCESS_KEY_ID: hive://secret/aws-access-key
        AWS_SECRET_ACCESS_KEY: hive://secret/aws-secret-key
        AWS_REGION: us-east-1
```

#### D&R-Driven Sessions (AI Agent Hive Record)

When using definition mode with a Hive AI agent record, set the environment variables in the record:

```yaml
ai_agent:
  bedrock-investigator:
    data:
      prompt: "Investigate this detection..."
      anthropic_secret: hive://secret/anthropic-key
      lc_api_key_secret: hive://secret/lc-api-key
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
