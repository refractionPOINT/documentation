# Amazon Web Services

!!! tip "Connecting from the web app?"
    Follow the prerequisites and credential creation instructions below, then
    return to **Cloud Security → Settings → Providers → Add provider**. Enter
    the provider IDs under **Configuration** and save the credential using
    **New secret** under **Permissions**. Run **Test Provider**, fix required
    failures, and save. The LimaCharlie CLI examples below are an alternative.
    [First-time setup and verification](../getting-started.md) explains the full journey.

Read-only inventory via an IAM identity that **assumes a read-only role**.
Two topologies:

- **Single account** (below): one IAM user plus one role in that account.
- **AWS Organization:** deploy the same role to every account via a
  service-managed CloudFormation StackSet and set `aws_member_role_name`; the
  **management-account role** named by `aws_role_arn` additionally needs
  `organizations:List*` / `Describe*`. The base IAM user still needs nothing
  beyond `sts:AssumeRole` — member-account discovery is performed with the
  assumed role, not with the user's own credentials.

## What we check

- **Root and IAM.** Root user without MFA, with access keys, or used recently.
  Weak password policy. Credentials unused for 45 days. Full-administrator
  policies. No IAM Access Analyzer. Accounts covered by no guardrail SCP.
- **Logging and threat detection.** CloudTrail trails that are stopped, lack log
  validation or KMS encryption, or miss data events. AWS Config, GuardDuty and
  Security Hub not enabled in every region. Missing CIS metric filters and alarms.
- **Network.** VPC flow logs off, default security groups with rules, NACLs and
  security groups open to the internet on SSH, RDP, SMB and other high-risk ports,
  over-broad peering routes, transit gateways that auto-accept attachments, Client
  VPN without logging.
- **Compute.** EC2 instances that accept IMDSv1, unencrypted or public EBS volumes,
  snapshots and AMIs, ECS tasks that run privileged or as root, credentials in
  CodeBuild and Lambda environments, unauthenticated Lambda URLs, cross-account
  Lambda layers.
- **Data.** S3 public access, missing TLS enforcement, MFA delete, ACLs, logging
  and cross-account access. Unencrypted or public EFS, KMS keys without rotation or
  with a public policy, Secrets Manager rotation, and public resource policies on
  DynamoDB, SQS, SNS, Glue and Backup.
- **Databases and managed data services.** RDS and Aurora, DocumentDB, Neptune,
  Redshift, ElastiCache, OpenSearch, MSK, DMS and similar: encryption at rest and
  in transit, public access, public snapshots, authentication and audit logs.
- **EKS clusters.** Public API endpoint, private nodes, local accounts, workload
  identity, audit logging, Secrets encryption, network policy enforcement,
  supported versions and cluster-admin access entries. See [Kubernetes](../index.md#what-we-look-for).

Not checked: workloads and RBAC inside EKS clusters.

## Architecture (least-privilege)

An IAM **user** whose only permission is `sts:AssumeRole` on a read-only
**role** (`SecurityAudit` + `ViewOnlyAccess`), gated by an **external ID**.
LimaCharlie stores the user's access key, assumes the role, and reads. The
user itself can do nothing but assume that one role.

<span id="create-the-identity-cli-single-account"></span>

## Create the identity (single account)

Use a dedicated test account for your first connection if you have one. Ask an
AWS administrator who can create IAM users, roles, policies, and access keys
to run the steps below. The created user is the application's identity, not a
human login. The role grants the read permissions, and the external ID is a
value that must match between the role's trust policy and LimaCharlie.

Choose one tab; both create the same user, role, and access key.

=== "Web console"

    1. Sign in to the AWS console as an administrator, open **IAM → Users → Create user**,
       and name the user `lc-cloudsec`. Leave console access off. Create the user
       without attaching policies; its permission is added below.
    2. Copy your 12-digit account ID from the account menu. Generate and save a unique
       alphanumeric external ID (for example, using a password manager). Replace
       `<ACCOUNT_ID>` and `<EXTERNAL_ID>` in the following policy with those values.
    3. Open **IAM → Roles → Create role → Custom trust policy** and paste:

        ```json
        {
          "Version": "2012-10-17",
          "Statement": [{
            "Effect": "Allow",
            "Principal": {"AWS": "arn:aws:iam::<ACCOUNT_ID>:user/lc-cloudsec"},
            "Action": "sts:AssumeRole",
            "Condition": {"StringEquals": {"sts:ExternalId": "<EXTERNAL_ID>"}}
          }]
        }
        ```

    4. Continue to permissions and select both `SecurityAudit` and `ViewOnlyAccess`.
       Name the role `LimaCharlieCloudSecRO`, create it, and copy its **ARN** from
       the role details. Keep the external ID for the LimaCharlie wizard.
    5. Open **IAM → Users → lc-cloudsec → Permissions → Add permissions → Create
       inline policy**. Select the **JSON** editor and paste this policy, replacing
       `<ACCOUNT_ID>` with the same account ID:

        ```json
        {
          "Version": "2012-10-17",
          "Statement": [{
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::<ACCOUNT_ID>:role/LimaCharlieCloudSecRO"
          }]
        }
        ```

    6. Name the policy `lc-assume-ro` and create it. The user now has permission to
       assume this role; the read permissions belong to the role.
    7. On the user's **Security credentials** tab, choose **Create access key**.
       Review the use-case guidance, select **Other**, continue through the prompts,
       and save the **Access key ID** and **Secret access key**. AWS shows the
       secret only at creation; keep it for the credential step below.

    AWS documents [custom trust policies](https://aws.amazon.com/blogs/security/iam-access-analyzer-makes-it-simpler-to-author-and-validate-role-trust-policies/)
    and [access key creation](https://docs.aws.amazon.com/IAM/latest/UserGuide/access-keys-admin-managed.html).

=== "Cloud Shell / CLI"

    1. Sign in to the AWS console with that administrator identity (not root).
    2. Open **CloudShell** from the console toolbar and use its Bash shell. The AWS
       CLI is already installed and uses your console identity. See
       [AWS CloudShell setup](https://docs.aws.amazon.com/cloudshell/latest/userguide/getting-started.html).
    3. Run `aws sts get-caller-identity` and confirm the **Account** is the one you
       intend to connect.
    4. Run the commands below in that same shell. Stop if a command fails rather
       than continuing with an incomplete role.
    5. Keep the generated external ID and the access key's **AccessKeyId** and
       **SecretAccessKey**. They are used in different fields, as shown below.

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

## Compliance metadata permissions

The assumed role, including every organization member-account role, needs these
read permissions for configuration compliance. Keep the base IAM user's grant
limited to `sts:AssumeRole`.

| Permission | Resource scope | Read surface |
|---|---|---|
| `iam:ListUsers`, `iam:ListAccessKeys` | `*` for user enumeration; IAM user resources for key metadata where applicable | Active human IAM user key creation dates; uses the existing IAM user inventory reads |
| `cloudtrail:DescribeTrails`, `cloudtrail:GetTrailStatus`, `cloudtrail:GetEventSelectors` | `*` | Trail configuration, logging status and management-event selectors |
| `ec2:DescribeRegions` | `*` | Complete region enumeration for absence decisions |
| `s3:GetEncryptionConfiguration` | `arn:aws:s3:::*` (or the intended bucket ARNs) | Bucket default encryption configuration |

Verify these permissions on your role even if its managed policies already include
them. IAM user normalization also needs the existing MFA, key-last-used and
attached/inline policy read permissions. Key metadata never exposes the key value.
Only active keys participate in the 90-day age check; inactive keys and a proven
empty active-key population are excluded. Unknown creation dates or incomplete
user enumeration cannot establish a clean result.

CloudTrail checks use each trail's home-region status and selectors, including
organization/shadow trails. A qualifying multi-region trail must log read and
write management events. Unsupported or unread selectors stay unknown. An
explicitly configured region subset can prove a qualifying multi-region trail,
but cannot prove its absence across the account. Provider tests probe only a
representative trail and bucket; per-resource reads decide sweep coverage.

S3 default encryption describes **new uploads**, not historical objects. AWS
[automatically encrypts new uploads with SSE-S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html),
so an absent stored bucket encryption configuration is not evidence of unencrypted
storage. Historical object encryption remains a manual part of the CIS encryption
assessment. Configuration reads never authorize a claim about all existing objects.

## Create the credentials secret

In the LimaCharlie wizard's **Permissions** step, select **New secret**. Choose
a name such as `aws-credentials`, then paste this JSON with the two values
from AWS: the access key ID and secret access key. If you used the CLI, do not
paste the entire command output.

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

For CLI setup, save the credential JSON above as `aws-secret.json` and install `jq`.

```bash
jq -Rs '{secret: .}' aws-secret.json \
  | limacharlie secret set --key aws-credentials --enabled \
  && rm -f aws-secret.json
```

`jq -Rs` wraps the file contents into the secret record for stdin — the equivalent of
`limacharlie hive set --hive-name secret` with `{"secret": "<the credential JSON
as a string>"}`.

## Create the provider record

In the wizard's **Configuration** step, enter the role ARN from IAM → Roles →
`LimaCharlieCloudSecRO` and the external ID you generated. An ARN is AWS's full
identifier for a resource. Leave the member role field empty for a single-account
setup; it is for collecting across an AWS Organization. Then test and save.

The equivalent CLI configuration is below.

`provider.yaml`:

```yaml
provider_type: aws
aws_role_arn: "arn:aws:iam::<ACCOUNT_ID>:role/LimaCharlieCloudSecRO"
aws_external_id: "<EXTERNAL_ID>"
credentials: hive://secret/aws-credentials
# aws_regions: [us-east-1, ...]                 # optional; omit = all enabled regions. Optional with region locks; see below.
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
| `iam_boundaries` | — | IAM permission boundaries unreadable (`iam:GetAccountAuthorizationDetails`). A principal whose boundary caps it below its policies is scored on the uncapped policies, so it can be reported as an administrator when it is not. |
| `s3` | ✅ | Storage inventory unavailable. |
| `regions` | — | Only meaningful when `aws_regions` is **unset** (with it set the check is skipped as unnecessary, and still counts as passing). The role was refused `ec2:DescribeRegions` for a missing permission, so the sweep cannot list the enabled regions and falls back to `us-east-1` alone. Grant `ec2:DescribeRegions` (see [Compliance metadata permissions](#compliance-metadata-permissions)), or list the regions you want in `aws_regions`. A refusal that names an organization policy is not this failure: the request is retried through a region the policy allows. See [Organization policies that block reads](#organization-policies-that-block-reads). |
| `organizations` | — | Member-account discovery unavailable; only the connected account is swept. |
| `org_policies` | — | The organization's **service control policies** (SCPs) and **resource control policies** (RCPs) are unreadable, so they are not collected. Passes when the account is not in an organization, or no policy type is enabled on the organization root — in both cases there is nothing to read. |
| `inspector` | — | Workload vulnerability findings unavailable. |
| `secrets_manager` | — | Secret-store inventory unavailable. |
| `data_stores` | — | RDS / DynamoDB / Redshift inventory unavailable. |
| `front_doors` | — | Lambda / API Gateway / load-balancer inventory unavailable — a public function URL, API stage or internet-facing load balancer stays invisible to the exposure model. |
| `ai_services` | — | SageMaker / Bedrock inventory unavailable. |

With `SecurityAudit` + `ViewOnlyAccess`, every optional surface above also
passes — no extra policies needed.

!!! note "Why `front_doors` probes more than one call"
    Lambda's exposure verdict needs three separate grants —
    `lambda:ListFunctions`, `lambda:ListFunctionUrlConfigs` and
    `lambda:GetPolicy` — and a role missing any one of them still passes a
    single representative list call. The check therefore exercises the real
    per-function reads against one existing function, so a hand-rolled
    least-privilege policy is caught at connect time instead of leaving the
    Lambda inventory unreadable on every sweep.

    The two managed policies grant these BETWEEN them, not each on its own:
    `SecurityAudit` supplies `lambda:List*` and `lambda:GetPolicy`,
    `ViewOnlyAccess` the ELBv2 describes, and both supply `apigateway:GET`.
    Attach both, as the setup above does.

## Organization guardrails (SCPs and RCPs)

For an account in an AWS Organization, LimaCharlie records where the account
sits in the organization tree and every **service control policy** and
**resource control policy** that applies to it — those attached to the account
itself, plus each organizational unit above it, plus the root. The policy
documents are stored verbatim, each labelled with the level it is attached at.

!!! warning "Collected, not yet applied"
    These policies are **inventory today, not part of the access calculation**.
    Permission and attack-path answers are still the union of the permissions
    that were *granted*, without subtracting what an SCP forbids — so they can
    over-state access. If the collection role cannot read the policies at all,
    that is reported as a finding ("effective-permission analysis is
    unconstrained") rather than left implicit. The one place the policies are
    used today is deciding which regions and services to skip, described in
    [Organization policies that block reads](#organization-policies-that-block-reads).

Collecting them uses these read-only actions on the role named by
`aws_role_arn`, all of which `SecurityAudit` already grants:

```text
organizations:DescribeOrganization    organizations:ListPolicies
organizations:DescribePolicy          organizations:ListTargetsForPolicy
organizations:ListRoots               organizations:ListAccounts
organizations:ListOrganizationalUnitsForParent
organizations:ListAccountsForParent
```

If you attached a hand-written least-privilege policy instead of
`SecurityAudit`, add the actions above — the `org_policies` check tells you
whether they are in place. A standalone account (not in an organization) needs
none of this and reports no finding: with no organization there are no
guardrails to account for.

!!! note "Which account the role must live in"
    AWS only allows these reads from the organization's **management account**,
    or from an account you have registered as a **delegated administrator** for
    AWS Organizations. From any other member account they are refused with the
    same `AccessDenied` you would get from a missing permission, and adding IAM
    permissions will not change that. If `org_policies` keeps failing with a
    fully-granted role, check which account `aws_role_arn` points at.

!!! note "Propagation"
    Fresh IAM keys and role trust can take a few seconds to propagate; retry
    once on a transient `AccessDenied` / `InvalidClientTokenId`.

## Organization policies that block reads

Many organizations use SCPs as guardrails: a region lock that denies every
region except one or two (for example the Control Tower region deny), or a deny
on whole services such as DynamoDB or EKS. Cloud Security works within these
policies. There is no setting to turn on, and you do not need to loosen a
policy or exempt the LimaCharlie role.

### What Cloud Security does

Cloud Security already reads your organization's SCPs (see above). It
recognizes two standard shapes:

- **Region lock:** a deny on every action outside a list of allowed regions,
  including the Control Tower region deny and its exemptions for specific
  actions and principals.
- **Whole-service deny:** a deny on all actions of a service, such as
  `dynamodb:*`.

If the policy exempts the LimaCharlie role, nothing is blocked for that role.

For these collectors, Cloud Security does not call a region or service the
policy denies:

- EC2 instances
- EC2 security groups
- DynamoDB
- Redshift
- Secrets Manager
- EKS clusters
- Bedrock models
- ECR repositories
- Lambda functions
- RDS instances and clusters
- Elastic Load Balancing (v2) load balancers
- API Gateway REST, HTTP and WebSocket APIs
- SageMaker endpoints
- Bedrock agents, AgentCore runtimes and Q Business applications

Some of these also read a related service for detail, such as the security
groups and WAF associations of a load balancer, or the IAM role of a Lambda
function. Such a collector skips blocked scopes only in accounts where your
SCPs allow those detail reads wherever it uses them. Otherwise it behaves as
before in that account.

So in an account locked to `eu-north-1`, these are read in `eu-north-1`. Before,
a refused first region could stop the whole service, and the allowed region was
never read.

Everything else behaves as before. Other collectors and checks (ECS and
Inspector findings, for example) still try every region. A refusal there still shows as
a failed check under **Needs attention**, even when an SCP you recognize is the
cause. Adding a permission to the role only fixes a refusal that is a real
permission gap.

A policy shape Cloud Security cannot interpret blocks nothing. The scan then
behaves as it did without this feature. The organization's management account
is never subject to SCPs, so nothing is blocked there.

### What you see

Under the connection, **Blocked by your organization policy** lists, for each
account:

- **Services** the policy denies (for example `dynamodb`).
- **Service-in-region pairs**, written `service@region` (for example
  `ec2@ap-south-1`), where the policy denies a service in one region.
- **Policy IDs** (`p-...`) of the policies behind them.

Only scopes that were actually skipped are listed. A blocked scope is not a
failed check and does not count as an error. A refusal from a collector that
was not skipped is a different thing. It stays under **Needs attention**
whether the cause is a gap in the role's permissions, a policy shape Cloud
Security does not interpret, a recognized policy that denies a collector
outside the list above, or a recognized policy that denies one of a listed
collector's detail reads (so that collector behaves as before in that account).
Only the first is fixed by adding a permission.

### What happens to blocked scopes

- **No calls, no data.** A blocked region or service is not requested, so no
  inventory or findings come from it.
- **Not reported as empty.** An SCP can exempt other principals, and resources
  can predate the policy, so a block says nothing about what exists. The scope
  is recorded as not read, never as "nothing there".
- **Earlier data is kept.** Inventory collected from a scope before it was
  blocked is not deleted.
- **Other regions are unaffected.** A service denied in one region is still
  read in every allowed region.

**Current limitation.** In an account locked to some regions, a resource
deleted in an allowed region is not removed from the inventory yet. It stays as
last seen while the lock is in place. Removal works as before once the lock is
lifted.

### Account-wide reads

Some reads are not tied to a region: listing S3 buckets, finding a bucket's
region, reading the account-level S3 public access block, and listing the
enabled regions. AWS answers these from any enabled region. If your policy
refuses the default region (`us-east-1`), Cloud Security repeats the request
through another region. It tries the regions in `aws_regions` first, then the
standard regions that AWS enables on every account, and keeps the first one
your policy lets through. A real permission gap (a plain `AccessDenied` that
names no organization policy) is not retried.

**Limitation.** The standard regions do not include regions you have to opt in
to (for example `ap-east-1` or `me-south-1`). If the only region your policy
allows is an opt-in region, these reads can still be refused, and the
enabled-region list falls back to `us-east-1` alone. Listing that region in
`aws_regions` makes it a candidate.

### `aws_regions`

`aws_regions` stays optional. Use it when you want to limit scanning on
purpose, for example to cover only the regions you operate in. The collectors
listed above work with a region lock without it, as long as your SCPs allow
their detail reads (see above). For the other collectors,
setting `aws_regions` to the allowed regions also removes the **Needs
attention** entries from refused regions.

### CloudTrail

AWS logs each refused call as an `AccessDenied` event in the affected
account's CloudTrail. For the collectors listed above, in accounts where they
skip blocked scopes, Cloud Security no longer calls denied regions and
services, so these events are far fewer. Other
checks can still produce them. Limiting `aws_regions` to the regions you use
reduces them further.

## Troubleshooting

| `provider test` error | Cause | Fix |
|---|---|---|
| `auth` fails: `… no EC2 IMDS role found` | Secret used the wrong key names → no static creds → default chain → IMDS | Use `access_key_id` / `secret_access_key` (no `aws_` prefix) |
| `AccessDenied` on `sts:AssumeRole` | External ID mismatch, wrong trust-policy principal, or propagation | Confirm `aws_external_id` matches the trust condition; retry after a few seconds |
| A region or service appears under **Blocked by your organization policy** | An SCP in your organization denies it | Nothing to fix. See [Organization policies that block reads](#organization-policies-that-block-reads) |
| **Needs attention** shows a permission to add | The role lacks a read permission, or an SCP denies a collector that does not skip blocked scopes yet | Add the permission to the role (and to member-account roles) only if no SCP denies the call. For a region lock, set `aws_regions` to the allowed regions |

## Private ECR images

To scan private images in Amazon ECR, add these permissions to the **assumed role** used by this connection:

- `ecr:GetAuthorizationToken` (this action uses `Resource: "*"`).
- `ecr:BatchGetImage` and `ecr:GetDownloadUrlForLayer` on each ECR repository you want scanned.

For an AWS Organization connection, grant the same permissions to the member-account role in the account that owns each image, and allow the connected role `organizations:DescribeAccount` so LimaCharlie can confirm that the image's account is a member. Keep the base IAM user's permission limited to `sts:AssumeRole`. Each pull credential is limited by a session policy to the one repository being scanned. Images in AWS accounts outside the connected account and its organization are not pulled. See [AWS's ECR pull permission reference](https://docs.aws.amazon.com/AmazonECR/latest/userguide/ECR_on_ECS.html) and [private image scanning](../code-security/container-registries.md).
