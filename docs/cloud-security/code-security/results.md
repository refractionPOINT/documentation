# Working with results

Code findings are ordinary [Cloud Security findings](../findings.md). They share
the worklist, the triage actions (mitigated, accepted, false positive), owners,
tickets, [remediation SLAs](../remediation-sla.md) and the `cloud_finding.*`
automation events. Each one also carries a `repo` key and a `code` block with the
file, line range, package and fixed version where they apply.

## In the console

### Overview tab

**Cloud Security → Code security → Overview** is the place to start:

- **Open findings**, **Priority repositories**, **Scanner coverage** and
  **Container images** at a glance. **Open risk worklist** jumps to Risks.
- **Priority repositories** lists the repositories with the most severe open
  findings first.
- **Priority fix queue** groups open dependency findings by the one upgrade
  that closes them, such as "Upgrade lodash", with how many findings and
  repositories each upgrade clears. Start here to close the most findings with
  the fewest changes.
- **Scanner coverage** counts repositories that are partial, not scanned, held
  back by a plan limit, unknown or archived. A repository that was not fully
  scanned has not been proven clean.
- **Protection capabilities** shows, per capability (repository scanning,
  pull-request checks, automated fixes, container image scanning), whether it is
  set up, needs attention, or could not be verified.
- **Code to runtime evidence** follows an image from the repositories that build
  it to the workloads running it.
- **GitHub webhooks** and **Webhook automation** show whether push rescans and
  pull-request checks can fire. See
  [Pull-request checks and push rescans](pull-requests.md#webhook-status).

### Repositories tab

Every repository the connections can see, with its scan status and open
findings. Filter by name or finding class, or narrow to **Critical or high**,
**Partial coverage**, **Not scanned** or **Public**.

Each row offers **Rescan now**, **Download SBOM**, **View findings**,
**Details**, **Exclude from scanning** and **Open on** the provider. Select
several rows to rescan, exclude or download SBOMs in bulk.

**Exclude from scanning** adds the repository to the exclude list of every
enabled code-scanning policy. The next pass stops scanning it and resolves its
open findings.

**Details** opens a drawer with the repository's coverage, the state of each
engine (**On**, **Off**, **Partial**, **Unknown** or **No result**), the severity
floor and the top open findings. If the repository is outside the GitHub App's
installation, the drawer says so and links to the installation page.

### Images and Registries tabs

**Images** lists container images by digest, with the repositories they are
**Built from**, the workloads they are **Running on**, and their open findings.
Select an image to open its findings in Risks. **Registries** groups images by
image repository.

### Risks

Code findings appear in the main worklist on **Risks**. Use the **Repository**
filter for one repository, and **Code source** to separate **Hosted** scans
from **Pushed** results (see [Bring your own scanner](bring-your-own-scanner.md)).

A dependency finding's detail page has an **Open AutoFix PR** button. See
[AutoFix pull requests](autofix.md).

## From the CLI

```bash
# Repositories with scan status and open-finding counts.
limacharlie cloudsec code repos
limacharlie cloudsec code repos --with-findings --all
limacharlie cloudsec code repos -q payments

# Has the lane run, and what happened last time?
limacharlie cloudsec code status

# The dependency upgrades that close the most findings.
limacharlie cloudsec code fixes

# What each GitHub connection is allowed to do.
limacharlie cloudsec code capabilities

# Findings for one repository.
limacharlie cloudsec finding list --repo acme/payments --class vulnerability
limacharlie cloudsec finding list --class secret --severity CRITICAL
```

`code repos` returns a `repo` key (`<owner>/<name>`) that the other commands
accept. `code status` is the authoritative answer to "did the scan run". An empty
`code` list there means the lane has never run in this organization.

### Filter by where a finding came from

```bash
limacharlie cloudsec finding list --repo acme/payments --source hosted
limacharlie cloudsec finding list --repo acme/payments --source ingest
```

| `--source` | Findings from |
|---|---|
| `hosted` | Scans LimaCharlie ran |
| `ingest` | Results you pushed |
| `other` | The source-control platform's own detectors, such as GitHub's Dependabot, code-scanning and secret-scanning alerts |
| `none` | Findings with no code origin, which is most cloud findings |
| `both` | No filter (the default) |

Each finding also records the producer in `code.detected_via`:
`lc-code-scanner` (hosted scan), `lc-code-scanner-byo` (a local scan you
pushed), `sarif-ingest` or `cyclonedx-ingest`.

## Scan status

Each repository has a `scan_status`:

| Status | Meaning |
|---|---|
| `scanned` | The last scan completed. |
| `partial` | A limit or an unavailable engine cut the scan short. The findings are a **lower bound**, not a clean result. The limits that were hit are listed on the repository. |
| `unknown` | No scan state yet. `scan_status_reason` says why, for example `repo_not_scanned`. |

See [Status and reason codes](reference.md#status-and-reason-codes) for every
reason.

## Software bill of materials

Every scanned repository gets a CycloneDX SBOM. Download it from the
Repositories tab, or:

```bash
limacharlie cloudsec code sbom --repo acme/payments -o payments-sbom.json.gz
```

The SBOM is kept as a downloadable file, not as inventory rows, so a repository
with thousands of packages does not add thousands of rows to your estate. A
repository that has not finished a scan yet reports `sbom_not_generated_yet`.
One with no dependency manifest, such as a documentation repository, reports
`no_sbom_for_this_repository`.

## How code connects to your cloud

Repositories and container images are nodes in the
[security graph](../graph.md). Two edges connect them to what is running:
**`built-from`** (image to the repository that produced it) and **`runs-image`**
(workload to the image it runs).

That makes it possible to ask questions a repository scanner cannot answer on its
own. These queries ship in the [query pack](../graph.md):

| Query | Question |
|---|---|
| `vulnerable_packages_on_exposed_workloads` | Which advisories are in images that internet-facing workloads run? |
| `images_with_kev_on_exposed_workloads` | The same, limited to known-exploited vulnerabilities |
| `secrets_in_repos_with_cloud_oidc` | Which federated identities can assume a cloud identity? This is the blast radius of a leaked repository credential. |
| `eol_runtimes_in_production_images` | Which end-of-life runtimes reach a running workload? |

!!! note "An empty result is not always good news"
    The image queries need the `runs-image` link, and it only exists for the
    image sources the policy enables. `dockerfile` (the default) links images
    your repositories declare. `workloads` links digest-pinned images your cloud
    inventory reports running. An empty result can mean the link was not
    collected. See [`image_sources`](policy.md#container-images).

## Compliance

Two frameworks are graded from code findings. Both apply only when a
source-control provider is connected.

- **`owasp-top10`**: OWASP Top 10:2021, mapped by CWE. Five categories depend on
  static analysis and report **NOT_ASSESSED** until a static-analysis scan has
  run.
- **`cis-supply-chain`**: the *Source Code* and *Dependencies* sections of the CIS
  Software Supply Chain Security Guide, 60 controls. 10 can be assessed
  automatically. The others report **NOT_ASSESSED** with a reason, so read the
  coverage figure next to the score.

```bash
limacharlie cloudsec compliance report --framework owasp-top10
limacharlie cloudsec compliance report --framework cis-supply-chain
```

Controls that grade outcomes, such as "no secrets in source", wait until a scan
has completed. They grade what was scanned. A repository your policy excludes
produces no findings and cannot fail them, so compare the score with scanner
coverage. See [Compliance](../compliance.md) for how scoring works.

## In your IDE

The LimaCharlie MCP server gives AI assistants in your editor the same view:
repository findings, the fix queue, local scans and AutoFix. See
[Cloud Security in your IDE](../mcp.md).
