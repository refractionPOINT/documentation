# Cloud Security in your IDE (MCP)

The [LimaCharlie MCP server](https://github.com/refractionPOINT/lc-mcp-server) exposes Cloud
Security to any [Model Context Protocol](https://modelcontextprotocol.io/) client — Claude Code,
Cursor, and others — so an AI assistant can read your cloud posture, triage findings, and, for
[Code Security](code-security/index.md), scan the working copy on your own machine before anything is pushed.

This page covers the setup and the Code Security tools. Tool availability depends
on the MCP server version and backend rollout; check your client's tool list.
Most of the other Cloud Security tools
match a [command line interface](cli.md) command.

## Setup — Claude Code

```bash
git clone https://github.com/refractionPOINT/lc-mcp-server
cd lc-mcp-server
go build -o lc-mcp-server ./cmd/server

claude mcp add \
  --env LC_OID=YOUR_ORGANIZATION_UUID \
  --env LC_API_KEY=YOUR_API_KEY \
  --env MCP_MODE=stdio \
  --env MCP_PROFILE=cloud_security_readonly \
  --transport stdio limacharlie-cloudsec \
  -- /absolute/path/to/lc-mcp-server
```

Build with the Go version required by the server's `go.mod` (currently 1.27.1).
`/mcp` in a session lists the server and its tools. The command follows the
[Claude Code MCP setup](https://code.claude.com/docs/en/mcp).

## Setup — Cursor

Add the server to your personal `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "limacharlie-cloudsec": {
      "command": "/absolute/path/to/lc-mcp-server",
      "args": [],
      "env": {
        "LC_OID": "<your-organization-id>",
        "LC_API_KEY": "<your-api-key>",
        "MCP_MODE": "stdio",
        "MCP_PROFILE": "cloud_security_readonly",
        "LOG_LEVEL": "warn"
      }
    }
  }
}
```

`LOG_LEVEL=warn` matters more than it looks: the server logs to stderr, and in stdio mode a chatty
stderr is noise in the client's transport log.

## Profiles

`MCP_PROFILE` decides which tools the client is offered. For Cloud Security work:

| Profile | What it exposes |
|---|---|
| `cloud_security` | Every Cloud Security tool, including the triage writes |
| `cloud_security_readonly` | CloudSec reads, excluding local scan, ingest, triage and response writes |
| `all` | The whole platform |

Profiles select callable tools; they do not grant API permissions. Generic
provider, secret and policy setup uses `platform_admin` tools or the
[console/CLI setup](setup-cli.md). Keep your key's permissions scoped to the
workflow even when changing profiles. The hosted profile endpoint is
`https://mcp.limacharlie.io/mcp/cloud_security_readonly` when that deployment
supports it; verify the returned tools and any server-wide profile override. An
unrecognized profile endpoint can return 404.

A narrow profile is not just tidiness. An assistant chooses from what it is shown, so a session that
only needs to read posture is both cheaper and safer with `cloud_security_readonly`.

## Permissions

Organization-scoped tools require `ai_agent.operate` by default. Reads need
`cloudsec.get`. Triage writes and code ingest need
`cloudsec.set`; dependency AutoFix, remediation run creation and decisions require the separate
`cloudsec.respond` permission. The whole
surface also requires the organization to be subscribed to the `ext-cloud-security` extension — a
403 may indicate a missing subscription or permission. Check the error before
changing configuration.

For a first review, ask the assistant to use `cloudsec_get_scan_status`,
`cloudsec_get_overview`, then `cloudsec_list_findings` for high-severity open
findings. Read collection and scanner coverage before interpreting an empty list.

## The Code Security tools

| Tool | What it does |
|---|---|
| `cloudsec_code_repos` | The repositories the code lane sees, with scan state and the open-finding rollup |
| `cloudsec_code_findings` | Findings for one or more repositories, or the cross-filtered facet counts |
| `cloudsec_code_fixes` | The dependency upgrades that close the most findings, each with a finding id to pass to `cloudsec_code_autofix` |
| `cloudsec_code_capabilities` | Per-connection scanning and write capabilities; GitLab/Bitbucket workflow support depends on rollout |
| `cloudsec_code_scan_local` | Scans a working copy on your machine with the same scanner the hosted lane runs |
| `cloudsec_code_autofix` | Opens the dependency fix pull request for an SCA finding |

Additional tools read build provenance (`cloudsec_code_provenance`), finding
evidence (`cloudsec_get_finding_evidence_chain`), scanner coverage
(`cloudsec_get_code_coverage`) and change impact (`cloudsec_get_code_impact`).
Their availability depends on the backend capability; missing or stale evidence
does not prove safety. Provenance pushes require `cloudsec.set` and contain
metadata, not source code. Remediation run tools require `cloudsec.respond`.
See the [server's product guide](https://github.com/refractionPOINT/lc-mcp-server/blob/master/docs/SECURITY-PRODUCTS.md)
and the actual tool schema for selectors and confirmation requirements.

### Before they can return anything

Code scanning is opt-in, and two things must be true:

1. A source-control provider is connected (a `cloudsec_provider` record).
2. A `code_scanning` record exists in the `cloudsec_policy` hive, naming the repositories in scope
   and the engines that run.

Both are hive records — see [Get started](code-security/getting-started.md) and
[Scan policy](code-security/policy.md). **An empty answer from a code tool
usually means one of those two is missing, not that your code is clean**, and the tools say so
rather than implying an all-clear.

### Reading findings

`cloudsec_code_findings` will not list without at least one `repo`. That is deliberate: the findings
backend has no "any repository" selector, so dropping the constraint would return your whole
findings worklist — cloud findings included — under a tool named for the code lane. Filtering by
class does not scope it either, because `vulnerability`, `misconfig` and `malware` are shared with
the cloud lane.

The unscoped mode is `facets: true`, which is honest because the `repo` facet counts only findings
that have a repository. So the natural order is:

```text
cloudsec_code_findings { "facets": true }        → which repositories carry what
cloudsec_code_repos    { "has_findings": true }  → the same per repository, with scan state
cloudsec_code_findings { "repo": ["owner/name"], "severity": ["CRITICAL", "HIGH"] }
```

`source` narrows the same read by producer — `hosted` for the scan LimaCharlie ran, `ingest` for a
document your pipeline pushed, `other` for the source control's own detectors, `none` for a finding
with no code provenance, or `both`. It is applied inside the query, so the facet counts describe the
estate rather than the page you happen to be holding.

`repo` is matched **exactly** against a key whose owner and name segments are both ASCII
lower-cased, while a finding's `code.repo_name` is the source-control platform's display casing.
The filter folds what you pass, so a key read straight off a finding now scopes the read rather
than silently matching nothing. A key that is genuinely wrong still returns an empty page, and an
empty page under a single `repo` filter carries a note saying which case you are in: the key is
right and nothing matched, the key is wrong and here is the real one, or no such repository is in
the inventory.

### Scanning your working copy

```text
cloudsec_code_scan_local { "path": "/home/me/src/api" }
```

This runs on the machine hosting your local server: the default container path
needs Docker and a
development [`limacharlie` CLI with CodeSec support](code-security/getting-started.md#cli-installation)
on PATH, and it takes minutes rather than seconds. PyPI 5.6.2 lacks the code scan
command. Verify `limacharlie cloudsec code scan --help` before starting. The default
scanner image also requires registry access; an anonymous pull is not sufficient.
Newer MCP builds let the operator set `LC_CODE_SCANNER_IMAGE` or
`LC_CODE_SCANNER_BINARY` for a compatible authorized image or local executable.
These map to the CLI's `--image` / `--binary`; use a development CLI containing
those flags until release. An MCP caller cannot select the executable. Inspect
the server's [local scan guide](https://github.com/refractionPOINT/lc-mcp-server/blob/master/docs/CLOUD-SECURITY-CODE.md).

Without `ingest`, the findings report is not uploaded to LimaCharlie. Image pulls,
scanner dependency/intelligence lookups and optional rule downloads may still use
the network. A local scan is not visible in the hosted estate until ingested.

Because it runs a container locally, it is available only when the server is running in stdio mode.
A hosted MCP deployment refuses it.

`scanners` defaults to `sca,iac,licenses`; `sast` and `images` also run locally.
By default SAST uses scanner-local rules and does not automatically load
organization rules; the delegated local-only CLI has no organization credentials.
Newer MCP builds let the operator set `LC_CODE_SCANNER_RULES_FILE` to a compatible
exported code-rule JSON file, forwarding the CLI's `--rules-file`. An MCP caller
cannot choose the rules file. A scanner with no usable rules reports `sast_no_rules` (see
[Scan locally or in CI](code-security/bring-your-own-scanner.md#scan-locally-or-in-ci)). **Secret scanning
does not**, and asking for it is an error rather than a silent omission: a credential's identity in
this pipeline is a digest keyed by a value only the hosted lane holds, so locally-found secrets
would neither deduplicate against a hosted scan's nor be accepted by the ingest. Use the hosted lane
for secrets.

With `ingest: true` and a `repo`, the report is pushed to your organization, where it deduplicates
against the hosted scan by identity — the report format is loss-free, so it lands on exactly the
rows a hosted scan of the same repository would write, and re-pushing an identical report writes
nothing. A pushed report can only close findings *it* previously reported, never one the hosted
scanner found.

Pass `output_path` alongside `ingest`. The report otherwise exists only for the duration of the
scan, so a push that fails — not subscribed, no enabled `code_scanning` policy selecting the
repository, a quota, a transient error — costs the whole scan again.

### `cloudsec_code_autofix`

Opens the pull request that raises a vulnerable dependency to its fixed version,
for one finding:

```text
cloudsec_code_autofix { "finding_id": "fnd_..." }
```

`finding_id` is required and is the only input that decides anything: the
backend resolves it against the dependency rows its own scan produced and raises
that package to that advisory's fixed version, so there is no way to name a
package or a version. `repo` and `provider` are optional search hints.

For GitHub it needs **Contents: Read and write** and **Pull requests: Read and write**
App permissions. GitLab.com/Bitbucket use separately configured write credentials
when their workflow is available. `cloudsec_code_capabilities` reports configured
capabilities; a tenant policy cannot enable an unavailable workflow.

The tool creates a governed `open_fix_pr` remediation run and returns its
`run_id` and `state`. It requires `cloudsec.respond`; the caller is recorded as
requester and approver. Follow the run with `cloudsec_get_remediation` before
reporting an outcome. The clone, edit and PR happen asynchronously; `accepted`
does not mean a PR exists or the vulnerability is fixed. Repeating a request
before the PR opens can return the same run with `replayed: true`.

A disabled workflow is refused immediately. Later failures, such as missing
write permissions, policy scope, unsupported edits, an existing PR or exhausted
budgets, appear in the run's `failure_reason` and operational events. `change`
records the PR; `verified` means the fix was observed in every in-scope
deployment. Missing deployment evidence cannot establish a verified fix.

See [AutoFix pull requests](code-security/autofix.md) for the setup and the
lockfile behavior that decides whether the pull request is complete on its own.

## Local IaC attribution

Newer builds provide `cloudsec_code_iac_map_extract` in the full CloudSec profile
for local STDIO sessions. The operator must explicitly set `LC_IAC_MAP_EXTRACTOR`
to an installed extractor's path; there is no implicit executable selection.
The tool reads a local Terraform/OpenTofu show-JSON file and returns sanitized
identity/allowlisted desired metadata. Raw plans, state, source and credentials
are not uploaded. Review the sanitized document before a separate
`cloudsec_code_iac_map_push` call.

Push and receipt status both require `cloudsec.set`, so
`cloudsec_code_iac_map_status` is excluded from the read-only profile despite
being a read. A `processing` receipt is not published evidence; check status
until `published`, or resubmit the same document only for a retryable receipt.
Publication is not proof of deployment or remediation. See
[IaC source mapping](code-security/containment-setup.md#terraform-maps)
and the tool schema for exact receipt fields and capability prerequisites.

## See also

- [Code Security](code-security/index.md) — the product these tools read
- [Command Line Interface](cli.md) — the same surface, without an assistant
