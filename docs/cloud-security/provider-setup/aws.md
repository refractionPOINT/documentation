# Amazon Web Services

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and configuration
    formats on this page can change before general availability. Contact us to
    request access.

Read-only inventory with an IAM identity that **assumes a read-only role**.
Two topologies:

- **Single account** (below): one IAM user plus one role in that account.
- **AWS Organization:** deploy the same role to every account with a
  service-managed CloudFormation StackSet, then set `aws_member_role_name`.
  The base user also needs `organizations:List*` / `Describe*`.

## Architecture (least-privilege)

An IAM **user** has one permission only: `sts:AssumeRole` on a read-only
**role** (`SecurityAudit` + `ViewOnlyAccess`). An **external ID** protects
the role. LimaCharlie keeps the access key of the user, assumes the role, and
reads. The user can do nothing but assume that one role.

## Create the identity (CLI, single account)

Run these commands as an IAM admin. Do not use the root user.

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
EXTERNAL_ID=$(openssl rand -hex 16)          # save this

aws iam create-user --user-name lc-cloudsec

cat > trust.json <<EOF
{ "Version": "2012-10-17", "Statement": [{
  "Effect": "Allow",
  "Principal": { "AWS": "arn:aws:iam::${ACCOUNT_ID}:user/lc-cloudsec" },
  "Action": "sts:AssumeRole",
  "Condition": { "StringEquals": { "sts:ExternalId": "${EXTERNAL_ID}" } }
}] }
EOF
aws iam create-role --role-name LimaCharlieCloudSecRO \
  --assume-role-policy-document file://trust.json
aws iam attach-role-policy --role-name LimaCharlieCloudSecRO \
  --policy-arn arn:aws:iam::aws:policy/SecurityAudit
aws iam attach-role-policy --role-name LimaCharlieCloudSecRO \
  --policy-arn arn:aws:iam::aws:policy/job-function/ViewOnlyAccess

cat > assume.json <<EOF
{ "Version": "2012-10-17", "Statement": [{
  "Effect": "Allow", "Action": "sts:AssumeRole",
  "Resource": "arn:aws:iam::${ACCOUNT_ID}:role/LimaCharlieCloudSecRO"
}] }
EOF
aws iam put-user-policy --user-name lc-cloudsec \
  --policy-name lc-assume-ro --policy-document file://assume.json

aws iam create-access-key --user-name lc-cloudsec   # capture AccessKeyId + SecretAccessKey
```

!!! note "In the web app (AWS console)"
    1. Go to IAM → Users and create `lc-cloudsec`.
    2. Go to IAM → Roles and create `LimaCharlieCloudSecRO`. Use a custom
       trust policy with the user and the external-ID condition.
    3. Attach `SecurityAudit` and `ViewOnlyAccess` to the role.
    4. Add an inline policy on the user that allows `sts:AssumeRole` on the
       role.
    5. Create an access key.

## Create the credentials secret

```json
{"access_key_id": "AKIA...", "secret_access_key": "..."}
```

!!! warning "No `aws_` prefix"
    Use the bare `access_key_id` / `secret_access_key` keys. The SDK ignores
    `aws_access_key_id` / `aws_secret_access_key` without a message. It then
    uses the default credential chain, and the auth check fails with
    `no EC2 IMDS role found`. A third key is optional: `session_token` for
    temporary credentials.

```bash
limacharlie hive set --hive-name secret --key aws-credentials \
    --input-file aws-secret.json
```

## Create the provider record

`provider.yaml`:

```yaml
provider_type: aws
aws_role_arn: "arn:aws:iam::<ACCOUNT_ID>:role/LimaCharlieCloudSecRO"
aws_external_id: "<EXTERNAL_ID>"
credentials: hive://secret/aws-credentials
# aws_regions: [us-east-1, ...]                 # optional; omit = all enabled regions
# aws_member_role_name: LimaCharlieCloudSecRO   # ONLY for AWS Organization member accounts
```

## Verify & coverage

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | `sts:AssumeRole` failed. The external ID, the trust policy, or the credentials are wrong. The test probes nothing else. |
| `ec2` | ✅ | Compute inventory unavailable. |
| `iam` | ✅ | IAM inventory unavailable. LimaCharlie cannot build the CIEM access graph. |
| `s3` | ✅ | Storage inventory unavailable. |
| `regions` | — | The list of enabled regions is unavailable. The sweep uses `aws_regions` or the defaults. |
| `organizations` | — | Member-account discovery unavailable. The sweep covers only the connected account. |
| `inspector` | — | Workload vulnerability findings unavailable. |
| `secrets_manager` | — | Secret-store inventory unavailable. |
| `data_stores` | — | RDS / DynamoDB / Redshift inventory unavailable. |
| `ai_services` | — | SageMaker / Bedrock inventory unavailable. |

With `SecurityAudit` + `ViewOnlyAccess`, each optional check above also
passes. No more policies are necessary.

!!! note "Propagation"
    New IAM keys and role trust can need a few seconds to propagate. If the
    test returns a temporary `AccessDenied` / `InvalidClientTokenId`, run it
    again one time.

## Troubleshooting

| `provider test` error | Cause | Fix |
|---|---|---|
| `auth` fails: `… no EC2 IMDS role found` | Secret used the wrong key names → no static creds → default chain → IMDS | Use `access_key_id` / `secret_access_key` (no `aws_` prefix) |
| `AccessDenied` on `sts:AssumeRole` | External ID mismatch, wrong trust-policy principal, or propagation | Check that `aws_external_id` matches the trust condition. Run the test again after a few seconds |
