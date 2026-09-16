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

!!! warning "Use a narrow token — a broad one is accepted, but it is yours to justify"
    A token carrying more than the two scopes above still connects, and the credential test
    says so as an **advisory** note (`token_read_only`) rather than refusing it. That
    includes `write_repository` and the like, and it includes **`api`**, **`admin_mode`** and
    **`sudo`**.

    It is worth understanding what you are accepting. GitLab cannot narrow an access token to
    one repository, so the token each scan clones with is the connection's own token,
    mounted into a job that analyses untrusted third-party source. `api` is read-write across
    everything the account can reach, and `admin_mode`/`sudo` are the instance
    administrator's reach. Create a token with exactly `read_api` and `read_repository`.

    A token **missing** one of the two required scopes *is* refused — see below.

!!! info "A missing scope is refused wherever the token is used"
    The credential test is not the only gate, because a token can be rotated after a
    connection is saved. `read_api` is re-checked on **every inventory sweep**, and
    `read_repository` before **every scan**. A sweep that refuses leaves the inventory
    **unchanged** — the repositories and their findings stay exactly as they were, and the
    provider's status carries the reason — rather than reporting an empty estate.

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
| `token_scopes` | ✅ | The token lacks `read_api`, so the namespace cannot be listed. Re-checked on every sweep. |
| `token_read_repository` | ✅ | The token lacks `read_repository`, so scans cannot clone. Re-checked before every scan. |
| `token_read_only` | — | The token is broader than the connection uses — a write scope, or `api`/`admin_mode`/`sudo`. Advisory: the connection still saves. |
| `token_expiry` | — | The token is inactive or close to expiry. Advisory here, but a revoked or expired token is refused before every scan. |
| `namespace` | ✅ | The namespace path does not exist, or the token cannot see it. |
| `namespace_membership` | ✅ | The token's account is not confirmed as able to see the whole namespace (Reporter or above). A public or internal group answers a non-member with its **public** projects only, so an unconfirmed listing cannot be trusted as the estate. Checked again on every sweep. |
| `projects` | ✅ | The project listing is not readable. |
| `projects_visible` | — | The listing works but no project is visible to the token — usually a membership gap. |
| `code_scanning_reachable` | — | The connection points at a self-managed instance, which code scanning cannot reach. The inventory and its posture are unaffected. |

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `namespace` fails | A group name instead of its full path, or a subgroup path missing its parent | Use the path from the group's URL, e.g. `acme/platform` |
| `namespace_membership` fails | The token's account holds no role on the group, or it was removed from it. A group access token's bot user is a member by construction; a personal token's owner is not | Grant the account at least **Reporter** on the group. For a *user* namespace, connect the namespace belonging to that account, or use a group instead |
| `projects_visible` fails | The token's owner is not a member of the projects | Grant the token Reporter on the group, or on each project |
| Projects shared into the group are missing | Shared projects belong to their own namespace | Connect that namespace as well |
| `token_scopes` reports scopes as unverified on self-managed | Older GitLab versions do not expose token introspection | Expected; the first scan's clone is the authoritative check |
| The connection was saved, the inventory appears, but scans never produce findings | The instance is self-managed — see `code_scanning_reachable` and the limitation below | Connect a GitLab.com namespace for code scanning, or use the inventory and posture only |
| The inventory stops refreshing and the provider status says the token "cannot enumerate the namespace" | The connection's secret was rotated to a token without `read_api` after the connection was created. The existing repositories and findings are kept, not deleted | Create a token with `read_api` and `read_repository` and update the secret |

## Known limitations

- The access token must keep its two scopes for the lifetime of the connection: `read_api` is
  re-checked on every inventory sweep and `read_repository` before every scan, so a secret
  rotated to a narrower token stops the connection (without deleting anything) rather than
  silently reporting a smaller estate. A **broader** token is accepted — because GitLab has
  no way to narrow a token per repository, each scan clones with the connection's own token,
  so how much authority that token carries is worth a deliberate decision.
- The connection is the **repository estate** of one namespace. Group members, service
  accounts, deploy tokens, CI/CD variables and group settings posture are not collected.
- Protected-branch and push-rule posture is not collected, so the branch-protection findings
  GitHub repositories raise do not apply.
- **Code scanning is available for GitLab.com only.** A self-managed instance can be
  connected and its projects are inventoried and assessed normally, but repository cloning
  runs in an isolated, egress-restricted environment that reaches GitLab.com and does not
  reach customer-run instances, so scans of those projects cannot complete. The connection
  test reports this as `code_scanning_reachable`.
- **Scans run on the schedule** of the `code_scanning` policy. Push-triggered rescans are not
  available for GitLab.
- **Nothing is written to GitLab.** Merge-request checks, comments and dependency AutoFix pull
  requests are GitHub-only.
- GitLab's own security scan reports (SAST, dependency and secret detection) are not
  ingested.
- A second namespace is a second connection.
