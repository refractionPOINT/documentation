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
| **Static analysis (SAST)** | Source code, against a curated rule pack mapped to CWE | `code_weakness` |
| **Container images** | Images your repositories build from, and optionally images your workloads run | `vulnerability` on the image |
| **Licenses** | Dependency licenses with copyleft or unknown terms | `license_risk` |
| **End-of-life runtimes** | Language runtimes and base images past their vendor support date | `eol_runtime` |

See [Supported languages and ecosystems](reference.md#supported-languages-and-ecosystems)
for the full coverage of each engine.

Dependency findings name the package, the installed version and the version
that fixes it. They are ranked with EPSS and CISA KEV, so a known-exploited
advisory sorts above a high CVSS score nobody exploits.

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
  materials and hashes. File contents, diffs and secret values are never stored.
- **Secrets are stored as a salted hash.** No field on a finding can hold the
  credential itself.
- **Nothing is written to your repositories unless you allow it.** Pull-request
  checks, comments and AutoFix pull requests need write permissions you grant to
  the GitHub App, and each write uses a token limited to what that one action
  needs.

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
- [Pull-request checks and push rescans](pull-requests.md): scan every push and gate merges on GitHub.
- [AutoFix pull requests](autofix.md): let LimaCharlie open dependency upgrade pull requests.
- [Bring your own scanner](bring-your-own-scanner.md): scan in your own CI, or push SARIF and CycloneDX results.
- [Reference](reference.md): languages, limits, status codes and API routes.
- [Troubleshooting](troubleshooting.md): common problems and how to fix them.
