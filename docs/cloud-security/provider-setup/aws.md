# Amazon Web Services

Read-only inventory via an IAM identity that **assumes a read-only role**.
Two topologies:

- **Single account** (below): one IAM user plus one role in that account.
- **AWS Organization:** deploy the same role to every account via a
  service-managed CloudFormation StackSet and set `aws_member_role_name`; the
  **management-account role** named by `aws_role_arn` additionally needs
  `organizations:List*` / `Describe*`. The base IAM user still needs nothing
  beyond `sts:AssumeRole` — member-account discovery is performed with the
  assumed role, not with the user's own credentials.

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

!!! warning "No `aws_` prefix, and no other keys"
    `aws_access_key_id` / `aws_secret_access_key` are silently ignored — the
    SDK then falls back to the default credential chain and the auth check
    fails with `no EC2 IMDS role found`. Use the bare `access_key_id` /
    `secret_access_key` keys. Those two are the only keys read: a
    `session_token` is **not** supported, so temporary/session credentials
    cannot be used here (they are dropped, and the assume then fails with
    `InvalidClientTokenId`). Use the long-lived access key of the dedicated IAM
    user — the role it assumes is where the read permissions live.

```bash
limacharlie secret set --key aws-credentials \
    --value "$(cat aws-secret.json)" --enabled
```

`secret set` wraps the value into the secret record for you — the equivalent of
`limacharlie hive set --hive-name secret` with `{"secret": "<the credential JSON
as a string>"}`.

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

The report opens with the `config` and `credential` checks common to every
provider, [documented once in Provider Setup](index.md#the-two-checks-every-provider-reports-first);
the AWS-specific checks follow.

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | `sts:AssumeRole` failed — wrong external ID, trust policy, or credentials. Nothing else is probed. |
| `ec2` | ✅ | Compute inventory unavailable. |
| `iam` | ✅ | IAM inventory unavailable — the CIEM access graph cannot be built. |
| `s3` | ✅ | Storage inventory unavailable. |
| `regions` | — | Only meaningful when `aws_regions` is **unset** (with it set the check is skipped as unnecessary, and still counts as passing). Enabled-region enumeration was denied, so the sweep falls back to `us-east-1` alone — list the regions you want in `aws_regions`. |
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
