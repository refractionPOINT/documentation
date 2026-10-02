# Code Security

Code Security scans the source repositories behind your cloud estate and puts
what it finds into the same risk-ranked worklist as your cloud findings. You
triage a leaked credential or a vulnerable dependency the same way you triage a
public bucket, and the same automation events fire.

It works with **GitHub**, **GitLab.com** and **Bitbucket Cloud**. On GitHub it
can also rescan on every push, check pull requests before they merge, and open
pull requests that upgrade vulnerable dependencies.

!!! tip "Ready to start?"
    [Get started](getting-started.md) takes about ten minutes on GitHub: the
    console creates the GitHub App for you and turns scanning on.

## What it finds

| Engine | What it looks at | Finding class |
|---|---|---|
| **Dependencies (SCA)** | Lockfiles and manifests, matched against the vulnerability database | `vulnerability` |
| **Malicious packages** | The same dependencies, matched against known malicious-package advisories | `malware` |
| **Secrets** | Credentials in the current files and, if you turn it on, in the full git history | `secret` |
| **Infrastructure as code** | Terraform, CloudFormation, Kubernetes manifests, Helm charts, Dockerfiles | `misconfig` |
| **Static analysis (SAST)** | Source code, against your organization's [code rules](code-rules.md): LimaCharlie's CWE-mapped defaults plus your own | `code_weakness` |
| **Container images** | Images your repositories build from, and optionally images your workloads run | `vulnerability` on the image |
| **Licenses** | Dependency licenses with copyleft or unknown terms | `license_risk` |
| **End-of-life runtimes** | Language runtimes and base images past their vendor support date | `eol_runtime` |

See [Supported languages and ecosystems](reference.md#supported-languages-and-ecosystems)
for the full coverage of each engine.

Dependency findings name the package, the installed version and the version
that fixes it. They are ranked with EPSS and CISA KEV, so a known-exploited
advisory sorts above a high CVSS score nobody exploits.

### Image lineage coverage

The image lineage coverage percentage counts **your own distinct running image
digests** that have a source-repository link. Its breakdown separates inferred,
image-declared and verified links. Images identified as third-party are reported
separately and do not enter that percentage.

Connect the cloud project or registry that hosts your images and the source
repositories that build them. On GitHub, grant the App **Attestations: Read-only**
to verify GitHub Actions build signatures; on Google Cloud, grant the collection
service account **Artifact Analysis Occurrences Viewer** on the image project to
verify Cloud Build provenance. See the [GitHub](../provider-setup/github.md#enable-image-attestations-on-an-existing-app)
and [Google Cloud](../provider-setup/gcp.md) setup steps.

When an image's ownership cannot be established, the breakdown reports
`ownership_unknown` and withholds the percentage until the source or registry
connection supplies enough evidence. Ordinary unsigned build metadata can
identify a possible source but does not count as a verified signature.

## How your code is handled

Scanning code means reading it. What LimaCharlie guarantees is that it does not
keep it.

- **Each scan is short-lived and isolated.** A fetch job downloads the commit,
  and a separate sandboxed container scans it and is then destroyed. Both run
  in your organization's data region.
- **The scanner never holds your source-control credential.** Only the fetch
  job uses it. The scan container has no cloud identity, a read-only
  filesystem, and network access only to LimaCharlie's storage and vulnerability
  database mirror.
- **On GitHub, the fetch token covers one repository** and expires within an
  hour. GitLab and Bitbucket cannot narrow a token like that, so those fetch
  jobs use the connection's token. That is why those connections ask for
  read-only scopes.
- **Only the results leave the sandbox:** findings, the software bill of
  materials and hashes. Findings never hold file contents, diffs or secret
  values. The commit package the scan reads, and the files AutoFix edits, are
  deleted when the job ends. See [Data handling and privacy](data-handling.md).
- **Secrets are stored as a salted hash.** No field on a finding can hold the
  credential itself.
- **Nothing is written to your repositories unless you allow it.** Pull-request
  checks, comments and AutoFix pull requests need write permissions you grant to
  the GitHub App, and each write uses a token limited to what that one action
  needs.

These guarantees describe ordinary scans and deterministic dependency AutoFix.
The separate, currently unavailable [AI-proposed fix capability](autofix.md#ai-proposed-fixes)
has an additional opt-in for sending one target file to your model provider;
see [AI data handling](data-handling.md#ai).

## Where to find it

In the console, open **Cloud Security → Code security**. It has four tabs:

| Tab | What it shows |
|---|---|
| **Overview** | Open findings, the repositories to look at first, the **Priority fix queue** (the dependency upgrades that close the most findings), scanner coverage, what each GitHub connection is allowed to do, and the GitHub webhook status. |
| **Repositories** | Every repository with its scan status and open findings. Select one for details, rescan it, download its SBOM, or exclude it from scanning. |
| **Images** | Container images, the repositories that build them and the workloads that run them. |
| **Registries** | Image repositories grouped by registry. |

While something is not set up yet, the page shows a **Set up code security**
button. It opens a checklist of each capability, says what is blocking it, and
links to the right setting.

Code findings also appear on **Risks**, where the **Repository** and **Code
source** filters narrow the list.

## In this section

- [Get started](getting-started.md): connect GitHub, GitLab or Bitbucket and run your first scan.
- [Working with results](results.md): the console, the CLI, SBOMs, and how code findings connect to your cloud.
- [Scan policy](policy.md): which repositories are scanned, which engines run and how often.
- [Code rules](code-rules.md): the static-analysis rules scans run, LimaCharlie's defaults and your own.
- [Pull-request checks and push rescans](pull-requests.md): scan every push and gate merges on GitHub.
- [AutoFix pull requests](autofix.md): let LimaCharlie open dependency upgrade pull requests.
- [Bring your own scanner](bring-your-own-scanner.md): scan in your own CI, or push SARIF and CycloneDX results.
- [What Code Security guarantees](guarantees.md): the rules behind `verified`, image lineage, runtime evidence and remediation.
- [Configure evidence, lineage and remediation](containment-setup.md): permissions, connections, pull-request disclosure, remediation runs and playbooks.
- [Automatic behavior and incident response](incident-response.md): what happens on its own, and how to stop or undo a remediation.
- [Data handling and privacy](data-handling.md): what is read, what is kept, retention and purge.
- [Reference](reference.md): languages, limits, status codes and API routes.
- [Troubleshooting](troubleshooting.md): common problems and how to fix them.
- [Unknown, partial and refusal reasons](reasons.md): every reason code and what to do about it.
