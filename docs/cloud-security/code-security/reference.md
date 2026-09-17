# Code Security reference

## Supported languages and ecosystems

### Dependencies (SCA)

| Language | Ecosystems and files |
|---|---|
| JavaScript / TypeScript | npm, yarn, pnpm, bun |
| Python | pip, Poetry, Pipenv, uv, Conda |
| Go | Go modules, Go binaries |
| Rust | Cargo, Rust binaries |
| Java / JVM | Maven, Gradle, JAR files, sbt |
| Ruby | Bundler, gemspec |
| PHP | Composer |
| .NET | NuGet, `packages.props`, .NET Core deps |
| Swift / Objective-C | Swift Package Manager, CocoaPods |
| Containers | OS packages in container images |

Development dependencies are included and marked as such. The SBOM is CycloneDX.
Maven parent POMs are not resolved, because scans run without access to package
registries.

For Go and Rust, dependency findings also say whether the vulnerable code is
imported, and for some advisories whether the vulnerable function is called.

### Static analysis (SAST)

LimaCharlie's [default code rules](code-rules.md#the-default-rules) cover
JavaScript and TypeScript, Python, Go, Java, C#, Ruby and Rust, and are mapped to
CWE. Rules you write can target any language the engine supports.

Static analysis runs exactly the organization's enabled
[code rules](code-rules.md). The policy's `sast_ruleset` is deprecated and ignored.

A low-confidence static-analysis finding is recorded as `INFO`.

### Infrastructure as code

Terraform, CloudFormation, Kubernetes manifests, Helm charts and Dockerfiles.

### Secrets

Credentials in the working tree, and in the full git history when
`secrets_history` is on. On GitHub, a secret finding also carries GitHub's own
verdict on whether the credential is still live, when GitHub has one.

### End-of-life runtimes

Python, Node.js, Go, Java, Ruby, PHP and .NET, read from files such as
`.nvmrc`, `.python-version`, `.ruby-version`, `go.mod`, `pom.xml`,
`build.gradle` and `global.json`. Also nginx, Debian, Ubuntu and Alpine base
images.

### AutoFix

npm (including yarn and pnpm projects), pip, Go modules and Maven. See
[AutoFix pull requests](autofix.md).

## Limits

### Free tier

| Limit | Value |
|---|---|
| Repositories scanned | The first **10** by name, per connected source-control organization |
| Container images scanned | The **5** most referenced, per organization |

Repositories and images held back by these limits report
`free_tier_code_repos_cap` or `free_tier_code_images_cap`. The covered set does
not rotate, so findings do not appear and disappear between passes.

### All plans

| Limit | Value |
|---|---|
| Scan duration | 30 minutes per repository, including about 20 minutes of scanning |
| Repository download | 4 GiB. A larger repository fails with `source_too_large` |
| Container image size | 1 GiB compressed |
| File size read by static analysis | 1 MiB (larger files are counted, not read) |
| Enabled [code rules](code-rules.md#limits-on-the-rule-set) per organization | 5,000 rules and 20 MB |
| Report size | 20 MiB compressed |
| Container images per pass | 50 |
| Triggered scans (pushes and rescans) per repository | 50 per day |
| Pull-request writes per connection | 500 per day |
| AutoFix pull requests per connection | 20 per day |
| Pushed document size | 20 MiB |

When a limit cuts a scan short, the repository reports `scan_status: partial`
and lists the limit in `scan_limits`. A partial scan **never closes** findings it
did not get to check again. Files skipped by the static-analysis size limit are
counted, but do not make the scan partial.

## Status and reason codes

### Repository `scan_status`

| `scan_status` | `scan_status_reason` | Meaning |
|---|---|---|
| `scanned` | | The last scan completed. |
| `partial` | | A limit or unavailable engine cut the scan short. The limits are listed in `scan_limits`, for example `sast_no_rules` when no code rule is enabled. See [When rules cannot run](code-rules.md#when-rules-cannot-run) for the static-analysis reasons. |
| `unknown` | `repo_not_scanned` | Not scanned yet. |
| `unknown` | `repo_archived` | Archived repositories are not scanned. |
| `unknown` | `free_tier_code_repos_cap` | Outside the free-tier repository limit. |

`repo_archived` and `free_tier_code_repos_cap` can also appear on a `scanned`
repository that was scanned before it was archived or held back. Its last
results are kept.

### SBOM

| Reason | Meaning |
|---|---|
| `sbom_not_generated_yet` | No scan has completed yet. Try again later. |
| `no_sbom_for_this_repository` | The scan found no dependency manifest. This is permanent for repositories without dependencies. |
| `code_lane_not_enabled_in_datacenter` | Code Security is not available in this data region. |

### Scan errors on `code status`

| Code | Meaning |
|---|---|
| `github_app_missing_contents_permission` | The GitHub App lacks **Contents: Read-only**, so nothing could be downloaded. |
| `gitlab_token_missing_read_repository`, `bitbucket_token_missing_read_repository` | The connection's token cannot clone repositories. |
| `gitlab_token_inactive` | The GitLab token is revoked or expired. |
| `source_too_large` | The repository is over the 4 GiB download limit. |
| `job_timeout` | The scan ran past its time limit. |
| `fetch_failed` | The repository could not be downloaded. |
| `mirror_stale` | The vulnerability database mirror was out of date, so the scan did not run. |

## Events

Code Security emits these operational events into the organization's event
stream. They are off by default. Turn them on with `ops_events: true` in the
[`emission` policy](../configuration.md#emission-the-event-feed).

| Event | When |
|---|---|
| `cloudsec.code_scan_completed` | A repository or image scan finished. |
| `cloudsec.code_scan_failed` | A repository or image scan failed. |
| `cloudsec.code_pr_check_completed` | A pull-request check was published. |
| `cloudsec.code_pr_check_failed` | A pull-request check could not be completed. |
| `cloudsec.code_autofix_opened` | An AutoFix pull request was opened. |
| `cloudsec.code_autofix_refused` | An AutoFix request did not produce a pull request. |
| `cloudsec.code_scan_closure_held` | A scan would have closed a large share of a repository's findings, so closing waits for a second scan. |
| `cloudsec.code_scan_claim_refused` | One engine's result could not be trusted, so that engine's findings were left unchanged. |

Code findings themselves emit the standard `cloud_finding.*` events, which are
on by default. See [Events](../api-reference.md#events).

## API routes

All routes are under `https://api.limacharlie.io/v1/cloudsec/{oid}`. Reads need
`cloudsec.get`, writes need `cloudsec.set`, and the organization must be
subscribed to `ext-cloud-security`.

| Route | CLI | Purpose |
|---|---|---|
| `GET /code/repos` | `code repos` | Repositories with scan status and open-finding counts. Params: `q`, `has_findings`, `provider`, `cursor`, `limit`. |
| `GET /code/status` | `code status` | Run status per connection. |
| `GET /code/capabilities` | `code capabilities` | What each GitHub connection can do, and its webhook status. Optional `repo`. |
| `GET /code/fixes` | `code fixes` | Open dependency findings grouped by the upgrade that fixes them. |
| `GET /code/repos/{repo}/sbom` | `code sbom` | A short-lived download link for the repository's SBOM. |
| `GET /code/images`, `GET /code/images/{digest}` | | Container images and one image's detail. |
| `GET /code/image-repos`, `GET /code/image-repos/facets` | | Image repositories and their filter counts. |
| `POST /code/scan` | `code rescan` | Rescan one repository. Body: `{repo, ref?, provider?}`. |
| `POST /code/autofix` | `code autofix` | Open an AutoFix pull request. Body: `{finding_id, repo?}`. |
| `POST /code/ingest` | `code ingest` | Push SARIF, CycloneDX or a scanner report. |
| `POST /code/pr_check` | | Check a pull request. Used by the webhook rules. |
| `POST /code/webhook` | | Point a GitHub App's webhook at LimaCharlie. See [the webhook API](pull-requests.md#the-webhook-api). |

Findings are read with the standard [findings routes](../api-reference.md),
filtered by `repo`.

## Not available yet

- **Scanning images from container registries.** `image_sources: ["registries"]`
  is accepted but does nothing yet.
- **Pull-request checks, push rescans and AutoFix on GitLab and Bitbucket.**
- **Scanning self-managed GitLab instances.** They can be connected for inventory.
- **Bitbucket Data Center** (self-hosted).
