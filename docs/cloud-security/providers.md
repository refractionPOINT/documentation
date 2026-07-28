# Connecting Providers

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

A provider connection is one `cloudsec_provider` Hive record. It holds a
`provider_type`, the scope to enumerate, and a read-only credential. All
collection is agentless. The credential itself always lives in the
[secret](../7-administration/config-hive/secrets.md) Hive. The `credentials`
field references it as `hive://secret/<name>`; the provider record never stores
it inline.

Connect a provider in the web app at **Cloud Security → Settings → Providers**
with the **Add provider** button. You can also connect it as code with
`limacharlie hive set --hive-name cloudsec_provider` (see
[Getting Started](getting-started.md#2-connect-a-provider)). In both cases, run
the [credential test](getting-started.md#test-the-credential-before-saving)
first. The test probes every permission that a sweep needs and reports which
permissions are missing.

## The thirteen connectors

| `provider_type` | Surface | Scope field(s) | Credential (JSON stored in the secret) |
|---|---|---|---|
| [`gcp`](provider-setup/gcp.md) | Cloud infra | `gcp_scope` (`projects/{id}`, `folders/{id}`, or `organizations/{id}`) | Service-account key JSON |
| [`aws`](provider-setup/aws.md) | Cloud infra | `aws_role_arn` (+ `aws_external_id`, `aws_regions`, `aws_member_role_name`) | STS AssumeRole (secret optional) |
| [`azure`](provider-setup/azure.md) | Cloud infra | `azure_tenant_id` + `azure_subscription_id` (+ `azure_client_id`) | `{"client_secret": "...", "client_id": "..."}` |
| [`okta`](provider-setup/okta.md) | Identity | `okta_org_url` | `{"api_token": "..."}` (SSWS) or an API Services app |
| [`entra`](provider-setup/entra.md) | Identity | `entra_tenant_id` (+ `entra_client_id`) | `{"client_secret": "..."}` (service principal) |
| [`google_workspace`](provider-setup/google-workspace.md) | Identity | `workspace_customer_id` | SA key with domain-wide delegation + `admin_email` |
| [`1password`](provider-setup/onepassword.md) | Identity | `onepassword_scim_url` | `{"scim_url": "...", "scim_token": "..."}` |
| [`auth0`](provider-setup/auth0.md) | Identity | `auth0_domain` | `{"client_id": "...", "client_secret": "..."}` (M2M) |
| [`cloudflare`](provider-setup/cloudflare.md) | SaaS | `cloudflare_account_id` | `{"api_token": "...", "user_api_token": "..."}` |
| [`github`](provider-setup/github.md) | SaaS | `github_org` + `github_app_id` + `github_installation_id` | `{"private_key": "-----BEGIN..."}` (GitHub App) |
| [`openai`](provider-setup/openai.md) | AI | *(optional `openai_org_id`)* | `{"admin_api_key": "sk-admin-..."}` |
| [`anthropic`](provider-setup/anthropic.md) | AI | *(optional `anthropic_org_uuid`)* | `{"admin_api_key": "sk-ant-admin01-..."}` (+ optional compliance key) |
| [`limacharlie`](provider-setup/limacharlie.md) | LimaCharlie | one of `limacharlie_oid` or `limacharlie_uid` | `{"api_key": "..."}` |

Every record also accepts the fields that all providers share:
`internal_domains`, `sync_now`, `refresh`, and `feed_subscription`.
[Configuration](configuration.md#cloudsec_provider) documents these fields.

## Cloud infrastructure

### Google Cloud (`gcp`)

**Setup guide:** [step-by-step onboarding](provider-setup/gcp.md).

Set `gcp_scope` to a single project (`projects/{id}`), a folder
(`folders/{id}`), or a whole organization (`organizations/{id}`). The collector
enumerates every project in scope. The credential is a service-account key JSON
with read-only roles across the resource surface (compute, storage, IAM,
networking, KMS, BigQuery, Cloud SQL, Secret Manager, Pub/Sub, …). The test
report names any missing role.

### AWS (`aws`)

**Setup guide:** [step-by-step onboarding](provider-setup/aws.md).

The collector assumes a read-only IAM role that you name in `aws_role_arn`. It
uses an `aws_external_id` as the guard against the confused-deputy problem. A
single account needs nothing more.

For an **AWS Organization**, the collector chains from the management role into
each member account. In each member it assumes the role that
`aws_member_role_name` names. The default is the role name parsed from
`aws_role_arn` — the common StackSet pattern, such as
`OrganizationAccountAccessRole`. Use `aws_regions` to restrict enumeration to
specific regions. The secret can carry base credentials for the first assume,
or you can omit it and let the collector use its default chain.

### Azure (`azure`)

**Setup guide:** [step-by-step onboarding](provider-setup/azure.md).

Set `azure_tenant_id` and `azure_subscription_id`. Set the client id of the app
registration (service principal) in `azure_client_id`. The credential secret
carries the client secret: `{"client_secret": "..."}`. If an Entra directory
has **no** Azure infrastructure to enumerate, use the standalone `entra`
provider instead.

## Identity providers

Identity providers ingest a directory into the identity graph — users, groups,
and app assignments — rather than cloud infrastructure. They unify with cloud
IAM principals by email, which makes cross-surface CIEM possible ("this
Workspace user has admin on that GCP bucket").

### Okta (`okta`)

**Setup guide:** [step-by-step onboarding](provider-setup/okta.md).

Set `okta_org_url` to the base URL of the org, such as
`https://acme.okta.com`. The credential is a user-owned SSWS token
(`{"api_token": "..."}`) or an API Services app that uses client credentials
(`{"client_id": "...", "private_key": "..."}` or `client_secret`). The API
Services app is the recommended option, because it is not bound to a user.

### Microsoft Entra ID (`entra`)

**Setup guide:** [step-by-step onboarding](provider-setup/entra.md).

This is a standalone directory-only connection for organizations that have
M365/Entra but no Azure subscription to enumerate. Set `entra_tenant_id` and
set the client id of the app registration in `entra_client_id`. Put the client
secret in the credential secret. It collects users, groups, service principals,
and conditional-access posture. If you also run an `azure` connection for the
same tenant, the Azure connection defers its directory collection to the
standalone `entra` record, so the directory is never collected twice.

### Google Workspace (`google_workspace`)

**Setup guide:** [step-by-step onboarding](provider-setup/google-workspace.md).

Set `workspace_customer_id` to `my_customer` — the delegated super admin's own
account, and the common case — or to an explicit customer id. The credential is
a GCP service-account key with **domain-wide delegation**, plus the super-admin
subject to impersonate. Store it as
`{"service_account_json": "...", "admin_email": "admin@acme.com"}`. It ingests
users, groups, membership, and
managed devices, and it unifies by email with the GCP IAM principals that it
references.

### 1Password (`1password`)

**Setup guide:** [step-by-step onboarding](provider-setup/onepassword.md).

Set `onepassword_scim_url` to the SCIM bridge URL of the account. The
credential is the SCIM bearer token:
`{"scim_url": "...", "scim_token": "..."}`. It collects users and groups into
the identity graph.

### Auth0 (`auth0`)

**Setup guide:** [step-by-step onboarding](provider-setup/auth0.md).

Set `auth0_domain` to the canonical domain of the tenant, such as
`acme.us.auth0.com` or the legacy `acme.auth0.com`. Do not use a custom domain.
The credential is a Machine-to-Machine application that is authorized for the
Management API with read-only scopes:
`{"client_id": "...", "client_secret": "..."}`. It collects users, roles,
applications, and connections.

## SaaS

### Cloudflare (`cloudflare`)

**Setup guide:** [step-by-step onboarding](provider-setup/cloudflare.md).

Set `cloudflare_account_id` to the 32-hex account id from the dashboard. The
credential is a read-only account-scoped API token: `{"api_token": "..."}`. An
optional `user_api_token` covers the user-scoped endpoints: account members and
the enumeration of API tokens. Without it, those surfaces stay unobserved. It
collects zones, DNS posture, R2 buckets, members, API tokens, Access
applications, and Security Center insights.

### GitHub (`github`)

**Setup guide:** [step-by-step onboarding](provider-setup/github.md).

Auth is a **GitHub App installed on the organization** — an App, not a personal
access token. Access is therefore org-scoped and read-only, and it uses
short-lived installation tokens. Set `github_org` (the org login),
`github_app_id`, and `github_installation_id`. Put the private key of the App
in the credential secret:
`{"private_key": "-----BEGIN RSA PRIVATE KEY-----..."}`.

It collects org settings, members, and teams as identities, and repositories as
data stores. It collects installed Apps, webhooks, deploy keys, and Actions
secrets as non-human identities. It also collects the Actions OIDC subject
configuration.

## AI security (AISPM)

AI providers add your model-platform organizations to the estate as full
subjects. They use the same findings and the `nist-ai-rmf` and `owasp-llm`
compliance frameworks.

### OpenAI (`openai`)

**Setup guide:** [step-by-step onboarding](provider-setup/openai.md).

The credential is an **Admin API key** that you create *with* the
`api.management.read` scope at creation time:
`{"admin_api_key": "sk-admin-..."}`. Use a new key — keys that got the scope
later have had missing-scope problems. `openai_org_id` (`org-...`) is optional,
because the
key already implies the org. When you set it, it is checked against the
discovered org, so a mismatch fails the connection early. It collects the
organization, members, projects, and API keys.

### Anthropic (`anthropic`)

**Setup guide:** [step-by-step onboarding](provider-setup/anthropic.md).

Anthropic has two credential planes, and each one can stand alone:

- **Console** — an Admin key in `credentials`: `{"admin_api_key":
  "sk-ant-admin01-..."}`. Anthropic Console Admin keys carry no scopes, because
  every Admin key is full read/write. The collector uses it strictly read-only.
- **Compliance / Analytics** — an optional second secret referenced by
  `compliance_credentials`: `{"compliance_api_key": "sk-ant-api01-..."}` with the
  read-only compliance/analytics scopes. This adds the enforced-settings posture
  and the activity feed.

Set `anthropic_org_uuid` when you connect **only** the compliance plane,
because the Compliance API is addressed by org uuid. With a Console key
present, the org uuid is discovered automatically. The credential secret can
also carry an `org_oauth_token` to reach the Workload Identity Federation admin
plane. Findings degrade gracefully to the plane that is connected.

## LimaCharlie (`limacharlie`)

**Setup guide:** [step-by-step onboarding](provider-setup/limacharlie.md).

Inventory your **own** LimaCharlie tenancy as an estate. This is useful
directly, and also as the CAASM source that unifies your sensors with the rest
of your assets. Set exactly one of:

- `limacharlie_oid` — an **org** API key. Collection covers that one
  organization.
- `limacharlie_uid` — a **user** API key. It enumerates every organization that
  the user reaches. This is the MSSP fleet case: one connection covers the
  fleet.

The API key goes in the credential secret: `{"api_key": "..."}`.

## Refresh and event-driven freshness

Every connection re-enumerates on the `refresh` cadence, a duration such as
`"6h"`. An empty value uses the service default. A connection also
re-enumerates on demand whenever `sync_now` changes. On GCP,
`feed_subscription` names a Pub/Sub subscription that carries a cloud change
feed, so targeted re-sweeps show changes in seconds. The periodic sweep stays
as the safety net. For these shared fields, see
[Configuration](configuration.md#cloudsec_provider).
