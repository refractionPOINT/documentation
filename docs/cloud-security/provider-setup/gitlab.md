# GitLab

Connects one **GitLab namespace** — a group with every subgroup below it, or a user
namespace — on GitLab.com or a self-managed GitLab instance. Its projects become repositories
in the inventory, and the namespace itself becomes the account they belong to.

The connection exists to drive [Code Scanning](../code-scanning.md): once a `code_scanning`
policy selects its projects, they are scanned exactly like GitHub repositories and their
findings land in the same worklist.

**Auth model:** a GitLab **access token** (group, project or personal) with two read scopes.
The connector only ever reads: every API call is a `GET`, and a scan's clone is a fetch.

## Prerequisites

- A token owner that is a **member of the group** (Reporter or above) — or of each project to
  scan. A group or project access token is the cleanest choice: it belongs to the group, not
  to a person.
- The group's **full path**, e.g. `acme`, or `acme/platform` for a subgroup. For a personal
  namespace it is the username.
- For self-managed GitLab only: the instance's https root URL, e.g.
  `https://gitlab.example.com`.

## Required token scopes

| Scope | Why | Preflight check |
|---|---|---|
| `read_api` | Resolve the namespace and list its projects, subgroups included | `token_scopes`, `namespace`, `projects` |
| `read_repository` | Let the scan clone repository contents | `token_read_repository` |

Nothing else is needed.

!!! warning "Broad tokens are refused"
    A token carrying **`api`**, **`admin_mode`** or **`sudo`** fails the credential test
    (`token_not_tenant_wide`). It is not about what the connector does — it only reads — but
    about where the token goes: GitLab cannot narrow an access token to one repository, so
    the token each scan clones with is the connection's own token. A credential that can
    write everywhere the account reaches does not belong in a job that analyses untrusted
    source. Create a token with exactly `read_api` and `read_repository`.

    A token with a narrower extra write scope (`write_repository`, `write_registry`,
    `create_runner`, …) still connects, with an advisory note recommending the two read
    scopes.

## Create the token

**Group access token** (recommended): **Group → Settings → Access tokens → Add new token**.
Give it a name, an expiry, the **Reporter** role, and select only **`read_api`** and
**`read_repository`**. Copy the token — it is shown once.

A project access token (**Project → Settings → Access tokens**) connects the same way, scoped
to one project. A personal access token (**User settings → Access tokens**) also works, with
the same two scopes, but ties the connection to a person.

## Create the credentials secret

The secret holds the token, either bare or as a JSON document:

```json
{"token": "glpat-xxxxxxxxxxxxxxxxxxxx"}
```

```bash
limacharlie secret set --key gitlab-token --value '{"token": "glpat-..."}' --enabled
```

## Create the provider record

`provider.yaml`:

```yaml
provider_type: gitlab
gitlab_namespace: "acme/platform"
credentials: hive://secret/gitlab-token
refresh: 6h
```

For self-managed GitLab add the instance root:

```yaml
gitlab_base_url: "https://gitlab.example.com"
```

- `gitlab_namespace` is the full path: letters, digits, `_`, `.` and `-` per segment,
  segments joined by `/`. No URL, no leading or trailing slash.
- `gitlab_base_url` must be `https`, a bare instance root (no credentials, query or fragment)
  and must not be a private or loopback address. Leave it empty for GitLab.com.

In the web app: **Add provider → GitLab**, then set **Namespace**, optionally **Instance
URL**, and **Credentials**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The token was rejected (wrong, revoked or expired), or the instance URL is wrong. Nothing else is probed. |
| `token_scopes` | ✅ | The token lacks `read_api`, so the namespace cannot be listed. |
| `token_read_repository` | ✅ | The token lacks `read_repository`, so scans cannot clone. |
| `token_not_tenant_wide` | ✅ | The token carries `api`, `admin_mode` or `sudo`. Replace it with a read-only token. |
| `token_read_only` | — | The token carries write scopes the connection never uses. |
| `token_expiry` | — | The token is inactive or close to expiry. |
| `namespace` | ✅ | The namespace path does not exist, or the token cannot see it. |
| `projects` | ✅ | The project listing is not readable. |
| `projects_visible` | — | The listing works but no project is visible to the token — usually a membership gap. |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `token_not_tenant_wide` fails | The token has `api` (common for personal tokens) | Create a token with only `read_api` and `read_repository` and update the secret |
| `namespace` fails | A group name instead of its full path, or a subgroup path missing its parent | Use the path from the group's URL, e.g. `acme/platform` |
| `projects_visible` fails | The token's owner is not a member of the projects | Grant the token Reporter on the group, or on each project |
| Projects shared into the group are missing | Shared projects belong to their own namespace | Connect that namespace as well |
| `token_scopes` reports scopes as unverified on self-managed | Older GitLab versions do not expose token introspection | Expected; the first scan's clone is the authoritative check |

## Known limitations

- The connection is the **repository estate** of one namespace. Group members, service
  accounts, deploy tokens, CI/CD variables and group settings posture are not collected.
- Protected-branch and push-rule posture is not collected, so the branch-protection findings
  GitHub repositories raise do not apply.
- **Scans run on the schedule** of the `code_scanning` policy. Push-triggered rescans are not
  available for GitLab.
- **Nothing is written to GitLab.** Merge-request checks, comments and dependency AutoFix pull
  requests are GitHub-only.
- GitLab's own security scan reports (SAST, dependency and secret detection) are not
  ingested.
- A second namespace is a second connection.
