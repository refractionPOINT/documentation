# Bitbucket Cloud

Connects one **Bitbucket Cloud workspace**. Its repositories become repositories in the
inventory, and the workspace itself becomes the account they belong to.

The connection exists to drive [Code Scanning](../code-scanning.md): once a `code_scanning`
policy selects its repositories, they are scanned exactly like GitHub repositories and their
findings land in the same worklist.

**Auth model:** an Atlassian **API token with scopes**, read-only. The connector only ever
reads: every API call is a `GET`, and a scan's clone is a fetch.

!!! note "Bitbucket Data Center is not supported"
    Bitbucket Data Center (self-hosted) is a different product with a different API. This
    connector is for Bitbucket Cloud (`bitbucket.org`) only.

## Prerequisites

- An Atlassian account that is a **member of the workspace** and can read its repositories.
- The workspace **slug** — the first path segment of a repository URL: the `acme` in
  `https://bitbucket.org/acme/api`.

## Required token scopes

| Scope | Why | Preflight check |
|---|---|---|
| `read:workspace:bitbucket` | Resolve the workspace and confirm membership | `token_scopes`, `workspace`, `workspace_membership` |
| `read:repository:bitbucket` | List repositories and let the scan clone them | `token_read_repository`, `repositories` |
| `read:user:bitbucket` | Identify the token's account | `auth` |

!!! warning "Admin and delete scopes are refused"
    A token carrying any **`admin:`** or **`delete:`** scope fails the credential test
    (`token_not_workspace_admin`). Bitbucket cannot narrow a token to one repository, so the
    token each scan clones with is the connection's own token, and a credential that can
    administer or delete across the workspace does not belong in a job that analyses
    untrusted source. A token with a narrower `write:` scope still connects, with an advisory
    note.

    Create the token **with scopes**. If Bitbucket does not report a token's scopes, the
    credential test says they were not verified — neither that the token can read nor that it
    is limited to reading.

## Membership is required, and checked on every sweep

The token's account must be a **member of the workspace**. This is not a formality: Bitbucket
answers a caller who cannot see a workspace's private repositories with a successful listing
of only its public ones. Without membership that listing is not the whole estate, so the
connection refuses to trust it — the sweep leaves the inventory unchanged and reports the
failure, rather than removing private repositories it merely cannot see.

## Create the token

1. Sign in to your Atlassian account settings: **Security → Create and manage API tokens**.
2. **Create API token with scopes**, give it a name and an expiry.
3. Select the **Bitbucket** app and only these scopes: `read:repository:bitbucket`,
   `read:workspace:bitbucket`, `read:user:bitbucket`.
4. Copy the token — it is shown once.

## Create the credentials secret

The secret holds the token, either bare or as a JSON document:

```json
{"token": "ATATT3xFfGF0..."}
```

```bash
limacharlie secret set --key bitbucket-token --value '{"token": "ATATT3..."}' --enabled
```

## Create the provider record

`provider.yaml`:

```yaml
provider_type: bitbucket
bitbucket_workspace: "acme"
credentials: hive://secret/bitbucket-token
refresh: 6h
```

`bitbucket_workspace` is the bare slug: letters, digits, `_` and `-`, up to 100 characters. No
URL, no `/`.

In the web app: **Add provider → Bitbucket Cloud**, then set **Workspace** and
**Credentials**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The token was rejected (wrong, revoked or expired). Nothing else is probed. |
| `token_scopes` | ✅ | The token lacks `read:workspace:bitbucket`. |
| `token_read_repository` | ✅ | The token lacks `read:repository:bitbucket`, so scans cannot clone. |
| `token_not_workspace_admin` | ✅ | The token carries an `admin:` or `delete:` scope. Replace it with a read-only token. |
| `token_read_only` | — | The token carries write scopes the connection never uses. |
| `workspace` | ✅ | The slug does not exist, or the token cannot see it. |
| `workspace_membership` | ✅ | The token's account is not a member of the workspace. |
| `repositories` | ✅ | The repository listing is not readable. |
| `repositories_visible` | — | The listing works but no repository is visible to the token. |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `workspace` fails as not found | A display name or URL instead of the slug | Use the first path segment of a repository URL |
| `workspace` fails as refused | The token lacks `read:workspace:bitbucket`, or the account is not a member | Add the scope, or add the account to the workspace |
| `workspace_membership` fails | The account can see the workspace but is not a member | Add the account to the workspace |
| `token_not_workspace_admin` fails | A token created with broad scopes | Create a token with only the three read scopes and update the secret |

## Known limitations

- The connection is the **repository estate** of one workspace. Members, groups, access keys,
  repository variables and branch restrictions are not collected, so the branch-protection
  findings GitHub repositories raise do not apply.
- The workspace slug is configuration, not discovery: a second workspace is a second
  connection.
- **Scans run on the schedule** of the `code_scanning` policy. Push-triggered rescans are not
  available for Bitbucket.
- **Nothing is written to Bitbucket.** Pull-request checks, comments and dependency AutoFix
  pull requests are GitHub-only.
