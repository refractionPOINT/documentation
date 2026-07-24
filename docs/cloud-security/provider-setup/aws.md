# Amazon Web Services

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Read-only inventory via an IAM identity that **assumes a read-only role**.
Two topologies:

- **Single account** (below): one IAM user plus one role in that account.
- **AWS Organization:** deploy the same role to every account via a
  service-managed CloudFormation StackSet and set `aws_member_role_name`; the
  base user additionally needs `organizations:List*` / `Describe*`.

## Architecture (least-privilege)

An IAM **user** whose only permission is `sts:AssumeRole` on a read-only
**role** (`SecurityAudit` + `ViewOnlyAccess`), gated by an **external ID**.
LimaCharlie stores the user's access key, assumes the role, and reads. The
user itself can do nothing but assume that one role.

## Create the identity (CLI, single account)

Run as an IAM admin (never the root user):

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
    IAM → Users → create `lc-cloudsec`; IAM → Roles → create
    `LimaCharlieCloudSecRO` (custom trust policy → the user plus the
    external-ID condition; attach `SecurityAudit` + `ViewOnlyAccess`); add an
    inline policy on the user allowing `sts:AssumeRole` on the role; then
    create an access key.

## Create the credentials secret

```json
{"access_key_id": "AKIA...", "secret_access_key": "..."}
```

!!! warning "No `aws_` prefix"
    `aws_access_key_id` / `aws_secret_access_key` are silently ignored — the
    SDK then falls back to the default credential chain and the auth check
    fails with `no EC2 IMDS role found`. Use the bare `access_key_id` /
    `secret_access_key` keys. (Optional third key: `session_token` for
    temporary credentials.)

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
| `auth` | ✅ | `sts:AssumeRole` failed — wrong external ID, trust policy, or credentials. Nothing else is probed. |
| `ec2` | ✅ | Compute inventory unavailable. |
| `iam` | ✅ | IAM inventory unavailable — the CIEM access graph cannot be built. |
| `s3` | ✅ | Storage inventory unavailable. |
| `regions` | — | Enabled-region enumeration unavailable; the sweep falls back to `aws_regions` or defaults. |
| `organizations` | — | Member-account discovery unavailable; only the connected account is swept. |
| `inspector` | — | Workload vulnerability findings unavailable. |
| `secrets_manager` | — | Secret-store inventory unavailable. |
| `data_stores` | — | RDS / DynamoDB / Redshift inventory unavailable. |
| `ai_services` | — | SageMaker / Bedrock inventory unavailable. |

With `SecurityAudit` + `ViewOnlyAccess`, every optional surface above also
passes — no extra policies needed.

!!! note "Propagation"
    Fresh IAM keys and role trust can take a few seconds to propagate; retry
    once on a transient `AccessDenied` / `InvalidClientTokenId`.

## Troubleshooting

| `provider test` error | Cause | Fix |
|---|---|---|
| `auth` fails: `… no EC2 IMDS role found` | Secret used the wrong key names → no static creds → default chain → IMDS | Use `access_key_id` / `secret_access_key` (no `aws_` prefix) |
| `AccessDenied` on `sts:AssumeRole` | External ID mismatch, wrong trust-policy principal, or propagation | Confirm `aws_external_id` matches the trust condition; retry after a few seconds |
