# Code Scanning

Cloud Security scans the source repositories behind your cloud estate and files
what it finds into the same risk-ranked worklist as everything else. Vulnerable
dependencies, credentials committed to git, misconfigured infrastructure-as-code,
container images and end-of-life runtimes all arrive as ordinary
[findings](findings.md) — same shape, same triage verbs, same automation events.

The point is not to add a second security product next to the first one. It is
that a dependency advisory means something different when the graph can show the
image it is baked into and the workload running that image, and an
infrastructure-as-code check means something different when the bucket it
declares is a bucket you actually own.

!!! info "In the console it's the **Code** page"
    Repositories, their scan status and their findings live under **Cloud
    Security → Code**. The same findings also appear on **Risks**, where the
    **Repository** filter narrows to one repository.

## What it scans

| Lane | What it reads | Finding class |
|---|---|---|
| **Dependencies (SCA)** | lockfiles and manifests, resolved to a software bill of materials, matched against the vulnerability database | `vulnerability` |
| **Malicious packages** | the same dependency set, matched against a malicious-package feed | `malware` |
| **Secrets** | credentials in the working tree, and — as a separate switch — in the full commit history | `secret` |
| **Infrastructure as code** | Terraform, CloudFormation, Kubernetes manifests, Helm charts, Dockerfiles | `misconfig` |
| **Container images** | images the repositories reference, and optionally images your workloads run or your registries hold | `vulnerability` on the image |
| **Licenses** | dependency licenses that carry obligation or compatibility risk | `license_risk` |
| **End-of-life runtimes** | language and base-image runtimes past their published support date | `eol_runtime` |

Dependency findings carry the package, the installed version and the **fixed
version** where one exists, plus EPSS and KEV so the queue is ordered by
exploitability rather than by CVSS alone. Secrets found only in history carry a
different remediation — rotate, because deleting the file does not un-leak the
credential.

## What leaves the sandbox, and what never does

Scanning code means reading code. The invariant is therefore not "we never read
it", it is **we never keep it**:

- Each scan runs in an **ephemeral, sandboxed container** in your data
  region. It shallow-clones the repository into scratch storage, runs the
  engines, writes one normalized report, and is destroyed.
- The container runs with **no cloud identity attached**, a read-only root
  filesystem, restricted egress and a hard 30-minute wall clock.
- The access token it is handed is **scoped to the single repository being
  scanned** and expires in an hour.
- **Only the report leaves.** Findings, the bill of materials and hashes — never
  file contents, never a diff, never a secret's value.
- A discovered secret is stored as a **salted hash**. There is no field on a
  finding capable of holding the credential, which is deliberate: the plaintext
  never reaches storage, a log, or an event.

The connected GitHub App stays **read-only**. Nothing in this lane writes to your
repositories, opens pull requests, or posts comments.

## Turning it on

Two things are required: the App needs to be able to read repository contents,
and you need a `code_scanning` policy that says which repositories to scan.

### 1. Grant `Contents: Read-only`

The connector's baseline permissions inventory repositories but cannot read them.
Add the **Contents → Read-only** *Repository* permission to your GitHub App and
approve the permission change on the organization's installation page — GitHub
requires an owner to accept a permission increase on an existing installation.

See [GitHub provider setup](provider-setup/github.md) for the full permission
table.

!!! warning "Without it, scans fail with a clear error, not silently"
    A repository selected for scanning while the App lacks `Contents` reports
    `github_app_missing_contents_permission` on the code scan status, with the
    remediation attached. Nothing is scanned and no findings are invented.

### 2. Create the policy

Code scanning is **opt-in**. With no `code_scanning` policy the lane never runs
— it does not default to scanning everything you connected.

```yaml
# code-policy.yaml
policy_type: code_scanning
enabled: true
repos:
  include: ["acme/api-*", "acme/payments"]
  exclude: ["acme/api-archive"]
scanners:
  sca: true
  secrets: true
  secrets_history: true
  iac: true
  images: true
  licenses: true
severity_floor: LOW
schedule: daily
image_sources: ["dockerfile"]
```

```bash
limacharlie hive set --hive-name cloudsec_policy --key code-scanning \
    --input-file code-policy.yaml --enabled
```

| Field | Meaning |
|---|---|
| `enabled` | **Required.** `false` parks the policy — kept and editable, but nothing is scanned. |
| `repos.include` | Globs matched case-insensitively against `owner/name` and the bare `name`. **Empty means every repository the provider can see** — write it explicitly unless that is genuinely what you want. |
| `repos.exclude` | Always beats `include`. |
| `scanners` | Each engine is an explicit boolean; **at least one must be true**. There is no implicit "all on", and no engine implies another. |
| `severity_floor` | Drops code findings below this severity. Empty means `LOW`, which keeps informational noise out of the worklist. |
| `schedule` | `daily` (the default), `weekly`, or `manual`. |
| `image_sources` | Where the image lane looks: `dockerfile` (the default), `workloads`, `registries`. The latter two are bounded by the estate rather than by the repositories you selected, so they are opt-in. |

An org may hold **several** `code_scanning` records and they compose, so you can
scan a small set of sensitive repositories daily with every engine on, and the
rest weekly with a narrower set.

!!! note "The glob dialect is the shared Cloud Security one"
    `*`, `?`, `[…]`, `{a,b}`, and a leading `!` for negation *within a list*.
    Write negations in `include`; a `!` in `exclude` reads as "exclude
    everything that is not this", which cancels your include list.

### Force a rescan

Bump the provider record's `sync_now` field to a new value. The next pass picks
up the repositories the policy selects, respecting the per-repository debounce.

## Reading the results

```bash
# Repositories, their scan status and open-finding rollups.
limacharlie cloudsec code repos
limacharlie cloudsec code repos --with-findings --all
limacharlie cloudsec code repos -q payments

# Has the lane run, and what happened last time?
limacharlie cloudsec code status

# The software bill of materials for one repository.
limacharlie cloudsec code sbom --repo acme/payments -o payments-sbom.json.gz
```

`code repos` returns a `repo` key (`<owner>/<name>`) that the other commands and
the `--repo` findings filter take. `code status` is the authoritative answer to
"did it run" — an empty `code` list means the lane has **never** run in this org,
which is not the same as the lane being off.

The findings themselves are ordinary findings:

```bash
limacharlie cloudsec findings list --repo acme/payments --finding-class vulnerability
limacharlie cloudsec findings list --finding-class secret --severity CRITICAL
```

See the [CLI reference](cli.md) and the [API reference](api-reference.md) for the
full surface.

### The bill of materials

Every scanned repository gets a CycloneDX SBOM, produced during the scan and
retrievable on request through a short-lived signed link. It is **not** stored as
inventory rows — a 2,000-package repository must not add 2,000 rows to your
estate — so the graph carries the vulnerability matches while the SBOM stays a
downloadable artifact.

A repository that has not been scanned yet reports `sbom_not_generated_yet`
rather than an empty document.

## The joins that make it worth doing

Code findings are not a separate island. The repository is a node in the
[security graph](graph.md), container images are nodes keyed by digest, and two
edges connect them to the running estate: **`built-from`** (image → the
repository that produced it) and **`runs-image`** (workload → the image it runs).

That gives you questions no repository scanner can answer on its own, shipped in
the [query pack](graph.md):

| Query | Question |
|---|---|
| `vulnerable_packages_on_exposed_workloads` | which advisories are in images that internet-facing workloads actually run |
| `images_with_kev_on_exposed_workloads` | the same, narrowed to known-exploited vulnerabilities |
| `secrets_in_repos_with_cloud_oidc` | which federated pipeline identities can assume a cloud identity — the blast radius of a leaked repository credential |
| `eol_runtimes_in_production_images` | which end-of-life runtimes reach a running workload |

!!! note "Read an empty result carefully"
    Three of the four need the **`runs-image`** link, and that link only covers
    the image sources your policy's `image_sources` enables — `dockerfile` (the
    default) links images a scanned repository declares, `workloads` links the
    digest-pinned images your cloud inventory reports a workload running. So an
    empty result can mean "that link was not collected here" rather than
    "nothing is affected". Each query's `description` says exactly which.

    `secrets_in_repos_with_cloud_oidc` anchors on every **federated** principal,
    not only CI ones, so a directory federation into your cloud appears
    alongside pipeline trusts — read the principal's subject to tell them apart.

## Compliance

Two frameworks are graded off the code lane, alongside the cloud benchmarks:

- **`owasp-top10`** — OWASP Top 10:2021, mapped by CWE. Five of the ten
  categories have a detector today; the rest are evidenced only by static
  analysis and report **NOT_ASSESSED** with their mapping already written down.
- **`cis-supply-chain`** — the CIS Software Supply Chain Security Guide's
  *Source Code* and *Dependencies* sections in full (60 controls), 10 of which
  have a detector. Every other control says in its own words *why* it is not
  assessed.

```bash
limacharlie cloudsec compliance report --framework owasp-top10
limacharlie cloudsec compliance report --framework cis-supply-chain
```

Both apply only when a source-code provider is connected; on an estate without
one they report **NOT_APPLICABLE** rather than a vacuous pass. And every control
that grades an *outcome* ("are there secrets in the source?") additionally waits
for the lane to have **completed a scan pass**: a connected provider is not the
same fact as a scanned repository, so until a scan runs those controls report
**NOT_ASSESSED** rather than passing off an engine that never ran. Because most of
`cis-supply-chain` is not auto-assessable, its report carries the low-coverage
qualifier — read the coverage figure next to the score, never the score alone.
See [Compliance](compliance.md) for how scoring and coverage work.

!!! warning "These controls grade the outcome, not the configuration"
    Several controls in both frameworks ask whether a *scanner is in place*.
    What the finding store can answer is whether there are *findings*. The two
    differ exactly where it matters: a repository your policy **excludes**
    produces no findings and therefore cannot fail those controls. Read the
    score next to the Code page's scan coverage. Each affected control says so
    in its description.

## Limits

| Limit | Value |
|---|---|
| Scan wall clock | 30 minutes per repository |
| Concurrent scans per organization | 4 |
| Per-file size read by static analysis | 1 MiB (larger files are counted, not opened) |
| Clone size | capped; a repository over the cap reports the cap it hit rather than failing silently |
| Report size | capped; a truncated result is reported as truncated |

When a cap truncates a scan, the code scan status carries what was hit. A partial
scan **never closes findings** it did not have the chance to re-observe.

## Not yet available

Named here so their absence is not mistaken for a clean result:

- **Static analysis (SAST)** — the `sast` switch exists in the policy and is off;
  the engine does not ship yet. No `code_weakness` findings are produced, and the
  compliance controls that depend on them report NOT_ASSESSED rather than PASS.
- **Push-triggered rescans**, **pull-request checks and merge gating**, and
  **dependency auto-fix pull requests**. All of these need write access, which the
  read-only connector does not have and will not gain.
- **Bring-your-own scan results** (uploading SARIF or CycloneDX from your own CI).
- **GitLab, Bitbucket and Azure DevOps.** The scanner and the storage model are
  source-control-agnostic by design, but only GitHub is connected today.

## See also

- [GitHub provider setup](provider-setup/github.md) — permissions, the App, and the credentials secret
- [Findings & Triage](findings.md) — the worklist every code finding lands in
- [Security Graph & Queries](graph.md) — the query pack and the graph vocabulary
- [Compliance](compliance.md) — scoring, coverage and evidence
- [Configuration Reference](configuration.md) — every Cloud Security policy record
