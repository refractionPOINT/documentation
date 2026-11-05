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

Dependency findings are known vulnerabilities in the packages your manifests and
lockfiles declare, including transitive ones. Each names the package, the
installed version and the fixed version when one exists.

Two checks decide how much a finding matters in your code:

- **Development-only dependencies.** A vulnerability in a package declared for
  build or test only is capped at `LOW`, because the package does not ship in
  what you deploy.
- **Reachability.** For most language ecosystems (JavaScript and TypeScript,
  Python, Go, Java and other JVM languages, Rust, Ruby, PHP, .NET and Swift),
  the scan looks for an import of the vulnerable package anywhere in the
  repository. A package that nothing imports is lowered one step. When the scan
  cannot tell, for example because the repository has no source in that
  language, the result is `unknown` and nothing is lowered. For Go and Rust, a
  finding can also say whether the repository names any function that the
  advisory lists as affected. If it names none, the finding is lowered one step.
  Both checks are heuristics that read your own source, not your dependencies'
  source. They lower severity and never drop a finding. See
  [Default severity adjustments](results.md#default-severity-adjustments).

#### Malicious packages

The same dependencies are matched against malicious-package advisories (the
`MAL-` entries in the OSV database). A match is filed as class `malware`, not
`vulnerability`.

There is no fixed version. Remove the package, and rotate any credential the
build or the machines that installed it could reach. The severity of a
malicious-package finding is never lowered because the package is
development-only or unreachable: install-time code runs either way.

### Static analysis (SAST)

LimaCharlie's [default code rules](code-rules.md#the-default-rules) cover
JavaScript and TypeScript, Python, Go, Java, C#, Ruby and Rust, and are mapped to
CWE. [What the default rules look for](code-rules.md#what-the-default-rules-look-for)
lists the classes of weakness and the languages for each. The defaults have no
rules for C and C++, PHP, Kotlin, Scala or Swift; rules you write can target any
language the engine supports.

Static analysis runs exactly the organization's enabled
[code rules](code-rules.md). The policy's `sast_ruleset` is deprecated and ignored.

Static analysis does not read files under directories named `vendor`,
`node_modules`, `testdata` or `__tests__`, or files that match `*.min.js`. It also
skips what the engine ignores by default, such as `tests/` directories and Go
`*_test.go` files.

A low-confidence static-analysis finding is recorded as `INFO`. Many of the
default rules are low-confidence, so many of their matches arrive as `INFO`.
`INFO` findings never fail a [pull-request check](pull-requests.md#what-the-check-says).

### Infrastructure as code

Terraform, CloudFormation, Kubernetes manifests, Helm charts and Dockerfiles.
The checks fall into these categories:

| Category | What the checks look for |
|---|---|
| Public exposure and network access | Storage buckets and objects that allow public access through ACLs or policies, security groups and firewalls that allow SSH, RDP or other traffic from any address, and databases with a public endpoint. |
| Encryption and data protection | Encryption at rest missing, or not using a customer-managed key. Versioning, access logging, backup retention and deletion protection turned off. |
| Identity and access | Weak access settings on cloud resources, for example database IAM authentication turned off. |
| Container and Kubernetes hardening | Privileged containers, containers that run as root or can escalate privileges, access to the host network or process namespace, default or unneeded Linux capabilities, a writable root filesystem, no seccomp profile, missing CPU and memory limits, and workloads in the `default` namespace. |
| Dockerfile hygiene | Images that run as root, no `HEALTHCHECK`, and package installs without the usual size and safety flags. |

Which checks apply depends on the resource types in your files; this table
describes the kinds of problem, not a fixed list.

A finding on an AWS, Google Cloud or Azure Terraform resource is linked to the
live resource when that resource exists in a connected cloud account, so you can
see which file to change. The match is by exact name. A name computed at apply
time needs a [Terraform map](containment-setup.md#terraform-maps).

### Secrets

Credentials in the working tree, and in the full git history when
`secrets_history` is on. The detectors recognize hundreds of credential formats,
in these groups:

| Group | Examples |
|---|---|
| Cloud provider keys | AWS access keys, Google Cloud API keys, Azure AD client secrets, and keys for other cloud and hosting providers |
| Source control and CI/CD tokens | GitHub, GitLab and Bitbucket tokens, npm and PyPI publish tokens, and CI service tokens |
| SaaS and payment API keys | Slack, Stripe, Twilio, SendGrid, Sentry, Shopify and many others |
| AI provider keys | OpenAI, Anthropic, Cohere, Hugging Face and others |
| Private keys and certificates | PEM private keys and PKCS#12 files |
| JSON Web Tokens | Signed JWTs committed in code or configuration |
| Generic high-entropy API keys | Values assigned to names such as `api_key` or `secret` that look like a credential but match no specific provider |

On GitHub, a secret finding also carries GitHub's own verdict on whether the
credential is still live, when GitHub has one. A credential GitHub reports as
inactive is lowered to `LOW`. Only GitHub supplies this; GitLab and Bitbucket
findings carry no live verdict. Secrets under vendored or test paths are lowered
to `INFO` unless GitHub reports them live. See
[Default severity adjustments](results.md#default-severity-adjustments).

Deleting a file does not remove its credentials from git history. Rotate any
credential found only in history.

### Licenses

When `licenses` is on, every license the scan identifies on a dependency becomes
a `license_risk` finding, one per package and license. Permissive licenses are
reported too, as `LOW`.

The severity follows the license's risk category: forbidden is `CRITICAL`,
restricted is `HIGH`, reciprocal is `MEDIUM`, and notice, permissive and
unencumbered are `LOW`. A license the scan cannot classify is also filed as
`LOW`.

Each finding also carries the license's obligation class in its evidence, as
`risk_class`. The class is separate from the severity, and the two can differ.

| `risk_class` | Meaning |
|---|---|
| `copyleft` | Strong copyleft, such as the GPL and AGPL families. Obligations reach the whole combined work. |
| `weak-copyleft` | Weak copyleft, such as the LGPL, MPL and EPL. Obligations reach the modified files of the component. |
| `permissive` | Permissive, such as MIT, BSD and Apache-2.0. |
| `unknown` | Not recognized. This includes any license the scan could not identify, which a person should review. |

For a dual-licensed package (`A OR B`) the class is the least restrictive
choice. For `A AND B`, it is the most restrictive. To focus on copyleft and
unknown licenses, look at `risk_class` rather than severity alone.

### Container images

Image scans report known vulnerabilities in the operating system packages and
the application packages inside an image, and flag base images that are past
their end-of-life date. They do not scan the image's contents for secrets,
misconfigurations or licenses. A Dockerfile in a repository is checked by the
infrastructure-as-code engine, not by the image scan.

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
`cloudsec.get` and writes need `cloudsec.set`. The exceptions: AutoFix and
remediation requests and decisions need `cloudsec.respond`, a runtime check
(`POST`) needs only `cloudsec.get`, and the map status read
(`GET /code/iac-map/status`) needs `cloudsec.set`. See the table below. The organization must be subscribed to
`ext-cloud-security`.

| Route | CLI | Purpose |
|---|---|---|
| `GET /code/repos` | `code repos` | Repositories with scan status and open-finding counts. Params: `q`, `has_findings`, `provider`, `cursor`, `limit`. |
| `GET /code/status` | `code status` | Run status per connection. |
| `GET /code/capabilities` | `code capabilities` | What enabled source-control workflow connections can do, and their webhook status. Optional `repo`. |
| `GET /code/fixes` | `code fixes` | Open dependency findings grouped by the upgrade that fixes them. |
| `GET /code/sbom` | `code sbom` | A short-lived download link for one repository's SBOM. Params: `repo` (required, `<owner>/<name>` as `/code/repos` returns it), `provider`. |
| `GET /code/images`, `GET /code/images/{digest}` | `image list`, `image get` | Container images and one image's detail. |
| `GET /code/image-repos`, `GET /code/image-repos/facets` | `image repos`, `image repo-facets` | Image repositories and their filter counts. |
| `POST /code/scan` | `code rescan` | Rescan one repository. Body: `{repo, ref?, provider?}`. |
| `POST /code/autofix` | `code autofix` | Open an AutoFix pull request as a remediation run. Needs `cloudsec.respond`. Body: `{finding_id, repo?}`. |
| `POST /code/ingest` | `code ingest` | Push SARIF, CycloneDX or a scanner report. |
| `POST /code/pr_check` | `code pr-check` | Check a pull request. Used by the webhook rules. |
| `POST /code/webhook` | `code webhook` | Point a GitHub App's webhook at LimaCharlie. See [the webhook API](pull-requests.md#the-webhook-api). |

Image reads accept repeatable `lineage_status` values: `verified`, `asserted`,
`inferred`, `ambiguous`, `unknown`. Filtering is server-side; a stale lineage
decision counts as `unknown` immediately. Image-repository facets can request
`lineage_facet=true` for digest-level counts under `lineage_statuses`; repository
placement filters do not narrow those lineage counts. An older server that
cannot apply the filter refuses it instead of returning an unfiltered page.
See [image lineage](containment-setup.md#image-lineage) for what each status
proves.

Findings are read with the standard [findings routes](../api-reference.md),
filtered by `repo`.

Evidence, lineage and remediation routes. See
[Configure evidence, lineage and remediation](containment-setup.md) for the
setup, and [Unknown, partial and refusal reasons](reasons.md) for the codes
they return.

| Route | Permission | Purpose |
|---|---|---|
| `GET /findings/{finding_id}/evidence-chain` | `cloudsec.get` | The finding's evidence chain. Optional `runtime=true`. |
| `POST /findings/{finding_id}/runtime-check` | `cloudsec.get` | Check whether the finding's package was seen running. Reads only. |
| `GET /code/coverage` | `cloudsec.get` | Coverage lines with their denominators. |
| `GET /code/impact` | `cloudsec.get` | Live impact of a commit (`repo_urn`, `commit`) or a finding (`finding_id`). |
| `GET /code/provenance`, `POST /code/provenance` | `cloudsec.get`, `cloudsec.set` | List or push build provenance. |
| `POST /code/iac-map`, `GET /code/iac-map/status` | `cloudsec.set` | Push a Terraform map, and read its publication status. |
| `POST /findings/{finding_id}/remediations` | `cloudsec.respond` | Request a remediation run. Body: `{action, idempotency_key}`. |
| `GET /remediations`, `GET /remediations/{run_id}` | `cloudsec.get` | List runs, or read one run with its steps. |
| `POST /remediations/{run_id}/approve`, `reject`, `cancel` | `cloudsec.respond` | Decide a run. |

## Not available yet

- **Scanning images from container registries.** `image_sources: ["registries"]`
  is accepted but does nothing yet.
- **GitLab and Bitbucket workflows without the corresponding server capability.**
  Support depends on rollout in your data region. Read `code capabilities`;
  scheduled repository scans do not imply webhook, check or AutoFix support.
- **Scanning self-managed GitLab instances.** They can be connected for inventory.
- **Bitbucket Data Center** (self-hosted).
