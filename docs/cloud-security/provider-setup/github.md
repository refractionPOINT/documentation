# GitHub

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Collects a GitHub organization: org settings, members and teams (identities),
repositories and their branch protection (data stores), installed GitHub Apps,
webhooks, deploy keys and Actions secrets (machine identities), and the Actions
OIDC subject configuration that lets workflows assume cloud roles.

**Auth model:** a **GitHub App installed on the organization**, with a
read-only permission set. The App's private key is used to mint short-lived
installation tokens — no personal access token, no user account in the loop.

## Prerequisites

- **Organization owner** access (creating and installing an org-owned App).
- The org **slug** (its login, e.g. `example-org`).

## Required permissions

Create the App with **read-only** access on the following. All are
*Repository* or *Organization* permissions set to **Read**:

| Permission | Scope | Why | Preflight check |
|---|---|---|---|
| **Members** | Organization | Org members and teams — the identity inventory | `members`, `teams` |
| **Metadata** | Repository | Repository inventory | `repos` |

## Optional permissions

| Permission | Scope | Unlocks | Preflight check |
|---|---|---|---|
| **Administration** | Organization | Installed-App inventory → over-privileged-app findings | `installed_apps` |
| **Secrets** | Organization | Organization Actions-secret inventory (**names only**, never values) | `org_secrets` |
| **Administration** | Repository | Branch-protection posture | *(collected during the sweep)* |
| **Secrets** | Repository | Repository Actions-secret inventory (names only) | *(collected during the sweep)* |
| **Webhooks** | Organization + Repository | Webhook inventory (data-egress surface) | *(collected during the sweep)* |

## Create the GitHub App

1. **Organization → Settings → Developer settings → GitHub Apps → New GitHub
   App.**
2. Name it (e.g. `LimaCharlie Cloud Security`), set a homepage URL, and
   **uncheck Webhook → Active** (the collector polls; it needs no callback).
3. Under **Permissions**, set each permission above to **Read-only**.
4. Under **Where can this GitHub App be installed?**, choose **Only on this
   account**.
5. **Create GitHub App**, then note the **App ID** at the top of the page.
6. Scroll to **Private keys → Generate a private key**. A `.pem` file
   downloads — this is shown once.
7. Click **Install App**, install it on your organization, and choose **All
   repositories** (or a subset, accepting reduced coverage).

### Get the installation ID

After installing, the browser URL of the installation settings page ends in the
installation ID:
`https://github.com/organizations/<org>/settings/installations/<INSTALLATION_ID>`.

With the `gh` CLI, as an org owner:

```bash
gh api /orgs/<org>/installations --jq '.installations[] | {id, app_slug}'
```

## Create the credentials secret

The secret carries **only** the private key; the App ID and installation ID
live on the provider record.

```json
{"private_key": "-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----\n"}
```

```bash
python3 -c 'import json;print(json.dumps({"secret":json.dumps({"private_key":open("app.private-key.pem").read()})}))' \
  > gh-secret.json

limacharlie hive set --hive-name secret --key github-app-key \
    --input-file gh-secret.json --enabled
```

## Create the provider record

`provider.yaml`:

```yaml
provider_type: github
github_org: "example-org"
github_app_id: "1234567"
github_installation_id: "89012345"
credentials: hive://secret/github-app-key
internal_domains: [example.com]
refresh: 6h
```

Both IDs are the **numeric** values, as strings. `github_org` is the bare org
slug — no URL, no owner prefix.

In the web app: **Add provider → GitHub**, then set **Organization**, **App
ID**, **Installation ID**, **Credentials**, and **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The App could not mint an installation token, or the installation cannot see the org. Nothing else is probed. |
| `members` | ✅ | Organization members unreadable — no identity inventory. |
| `repos` | ✅ | Repository inventory unavailable. |
| `teams` | — | Team and team-membership edges unavailable. |
| `installed_apps` | — | Installed-App inventory (over-privileged-app findings) unavailable. |
| `org_secrets` | — | Organization Actions-secret inventory unavailable. |
| `sso_identities` | — | SAML/SCIM external identities unavailable; identity unification falls back to verified-domain and public-profile emails. Passes with a note when the org has no SAML SSO. |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails: `Bad credentials` / JWT rejected | Wrong App ID, or the private key does not belong to that App | Confirm the App ID on the App settings page and regenerate the key if unsure |
| `auth` fails: `Not Found` on the org | The installation ID belongs to a different account, or the App is not installed on this org | Re-read the installation ID from the installation settings URL |
| `repos` passes but repositories are missing | The installation was scoped to selected repositories | Re-install with **All repositories**, or accept partial coverage |
| First sweep takes many minutes | Large orgs need per-repository calls for branch protection, deploy keys, secrets, and webhooks | Expected; subsequent sweeps are incremental |
| A permission was added after installing | GitHub requires the installation to accept new permissions | Approve the permission request on the org's installation page |

## Known limitations

- **Activity data** is limited to deploy-key last-used timestamps. GitHub App
  installation tokens expose no per-permission last-use, so used-vs-granted
  analysis is unavailable.
- **Fine-grained personal access tokens** cannot be enumerated org-wide by an
  App, so they are not inventoried.
- An **Actions OIDC trust** with no corresponding cloud-side role is reported
  as a dangling trust rather than a fabricated "can assume" edge.
