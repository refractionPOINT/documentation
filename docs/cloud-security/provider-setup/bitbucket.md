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

!!! warning "Use a narrow token — a broad one is accepted, but it is yours to justify"
    A token carrying more than the three scopes above still connects, and the credential test
    says so as an **advisory** note (`token_read_only`) rather than refusing it. That includes
    `write:` scopes and it includes **`admin:`** and **`delete:`** scopes.

    It is worth understanding what you are accepting. Bitbucket cannot narrow a token to one
    repository, so the token each scan clones with is the connection's own token, mounted
    into a job that analyses untrusted third-party source. A credential that can administer
    or delete across the workspace carries that reach into the job. Create the token with
    exactly the three read scopes.

    Create the token **with scopes**. If Bitbucket does not report a token's scopes — which
    means it was created without any, and is therefore bounded by none — the credential test
    says they were not verified, neither that the token can read nor that it is limited to
    reading. That is reported, not refused; the first sweep and the first scan are then the
    authoritative check that the token can read.

    A token **missing** one of the three required scopes *is* refused — see below.

!!! info "A missing scope is refused wherever the token is used"
    The credential test is not the only gate, because a token can be rotated after a
    connection is saved. `read:workspace:bitbucket` is re-checked on **every inventory
    sweep**, and `read:repository:bitbucket` before **every scan**. A sweep that refuses
    leaves the inventory **unchanged** — the repositories and their findings stay exactly as
    they were, and the provider's status carries the reason — rather than reporting an empty
    estate.

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
| `token_scopes` | ✅ | The token lacks `read:workspace:bitbucket`. Re-checked on every sweep. Passes with a note when the API reports no scopes at all — a token created without any is bounded by none, so it is not missing anything. |
| `token_read_repository` | ✅ | The token lacks `read:repository:bitbucket`, so scans cannot clone. Re-checked before every scan. |
| `token_read_only` | — | The token is broader than the connection uses — a `write:`, `admin:` or `delete:` scope. Advisory: the connection still saves. |
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
| `token_scopes` reports the scopes as not verified | The API token was created **without** scopes, so Bitbucket reports none — such a token is not bounded by any scope and carries the account's full reach. The connection is not blocked on it | Create a scoped API token with `read:repository:bitbucket`, `read:workspace:bitbucket` and `read:user:bitbucket`, and update the secret |
| The inventory stops refreshing and the provider status says the token "cannot read the workspace" | The connection's secret was rotated to a token without `read:workspace:bitbucket` after the connection was created. The existing repositories and findings are kept, not deleted | Create a token with the three read scopes and update the secret |

## Known limitations

- The API token must keep its three scopes for the lifetime of the connection:
  `read:workspace:bitbucket` is re-checked on every inventory sweep and
  `read:repository:bitbucket` before every scan, so a secret rotated to a narrower token
  stops the connection (without deleting anything) rather than silently reporting a smaller
  estate. A **broader** token is accepted — because Bitbucket has no way to narrow a token
  per repository, each scan clones with the connection's own token, so how much authority
  that token carries is worth a deliberate decision.
- The connection is the **repository estate** of one workspace. Members, groups, access keys,
  repository variables and branch restrictions are not collected, so the branch-protection
  findings GitHub repositories raise do not apply.
- The workspace slug is configuration, not discovery: a second workspace is a second
  connection.
- **Scans run on the schedule** of the `code_scanning` policy. Push-triggered rescans are not
  available for Bitbucket.
- **Nothing is written to Bitbucket.** Pull-request checks, comments and dependency AutoFix
  pull requests are GitHub-only.
