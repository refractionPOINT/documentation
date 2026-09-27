# Data handling and privacy

This page lists what Code Security reads, what it keeps, how long it keeps it,
and what happens to it when your organization leaves. It covers the scan lane
described in [Code Security](index.md) and the evidence, lineage and remediation
features described in [What Code Security guarantees](guarantees.md).

## What it reads

| Source | What is read | How |
|---|---|---|
| Your repositories | The commit being scanned | A short-lived fetch job downloads the commit and packs it. A separate sandboxed scan job reads the package and is then destroyed. See [How your code is handled](index.md#how-your-code-is-handled). |
| Container images | Image layers and metadata, by digest | The fetch job pulls the image with a registry credential. The scan sandbox never holds that credential. Only images referenced by digest are scanned. |
| Image build records | OCI labels, build attestations, and on Google Cloud the Artifact Analysis occurrences for an image | Read-only, with the permissions listed in [Configure connections and permissions](containment-setup.md#connections-and-permissions). Used to link a running image to the repository and commit that built it. |
| Your cloud accounts | Inventory and configuration | The existing Cloud Security collectors, with read-only credentials. Collection credentials are never used to change anything. |
| LimaCharlie sensors | Process and module activity on hosts that run an affected package | Summarized per sensor into short-lived package evidence (15 minutes). Asking for a runtime check tells the finding's sensors which packages to watch. It never changes the finding. |
| Terraform | A map you produce and push yourself | See [Terraform state and plans](#terraform-state-and-plans). LimaCharlie never receives a state or plan file. |
| Build provenance | Statements you push | Normalized and stored without the raw envelope. LimaCharlie never fetches a URL found inside a statement. |

## What it keeps

| Data | Kept | Not kept |
|---|---|---|
| Findings | Rule, severity, file path and line numbers, package and version, a fingerprint, and a hash of the matched text | The matched source lines. Code rules you write keep their own title text, with every captured value replaced by `[code]`. |
| Secret findings | Rule, file, line, a salted hash, and whether the secret is also in history | The secret value. No field on a finding can hold it. Results pushed in SARIF or other foreign formats have their secret findings dropped, because those formats carry the value. |
| Infrastructure-as-code findings | Check, file, lines, the resource address, and the resource name as it is written in the code (for example a bucket name) | The source line. |
| SBOM | One CycloneDX document per repository, as a downloadable file | |
| Terraform map | Resource addresses, identities and allowlisted settings | Any sensitive, unknown or secret-looking value. |
| Build provenance | Repository, commit, builder, workflow, digest and the evidence level | The raw signed envelope. |
| Remediation runs | Who requested and approved, the resolved targets, the state, bounded structured evidence and the callback result | Command output. |

Source bytes do pass through storage while a scan runs. The fetch job uploads
the commit package for the scan job to read. LimaCharlie deletes it when that
scan ends, and a storage rule deletes anything left after one day. AutoFix
works the same way with the manifest and lockfile it edits. Deleted objects are
not recoverable: the bucket has no soft delete and no versioning.

## Secrets and credentials

- **Secrets found in code** are stored only as a salted SHA-256. The salt is
  derived for your organization, and the scan sandbox receives only that
  derived value.
- **Liveness** comes from the provider's own verdict. LimaCharlie never
  presents a found credential to its issuer to test it.
- **Your connection credentials** (GitHub App private keys, GitLab and
  Bitbucket tokens, webhook secrets) live in your organization's
  [secrets](../../7-administration/config-hive/secrets.md) and are referenced
  by name. They never reach the scan sandbox or the browser.
- **The GitHub fetch token** covers one repository and expires within an hour.

### Terraform state and plans

State and plan files contain secrets, so LimaCharlie refuses them. The API
recognizes raw Terraform JSON and answers `400 iac_map_raw_terraform` with the
command to run instead.

You run the extractor yourself, on your own machine or CI runner. It does not
run Terraform, read your environment, contact a server or upload anything. It
reads `terraform show -json` output and writes a map with resource identities
and allowlisted settings. It drops every value Terraform marks sensitive or
unknown. Pushing the map is a separate command. On push, LimaCharlie rejects any
map that carries a key such as `password`, `secret`, `token`, `private_key` or
`connection_string`, or a value over 4 KiB.

## Pull-request output

Pull-request checks show the live consequence of a change only if you turn it
on with `pr_live_context`. It is `off` by default. In `risk_summary` mode the
check shows counts, the environment, yes/no exposure facts and the highest
severity, with a link that requires a LimaCharlie login. It shows no resource
names, account IDs, IP addresses or sensor IDs. `resource_details` adds
per-declaration detail, still without resource names. See
[Configure connections and permissions](containment-setup.md#pull-request-disclosure).

## AI

AutoFix does not send your code to a language model. It is deterministic. It
raises one dependency to one version and never runs a package manager. No
AI-generated fix feature is available.

## Retention

| Data | Retention |
|---|---|
| Source packages and AutoFix working files | Deleted when the job ends. Anything left is deleted after 1 day. |
| Scan reports, SBOMs and other scan result files | 30 days from creation. |
| Findings | While open. A closed finding is removed and a `cloud_finding.closed` event is emitted. |
| Superseded provenance events, and finished remediation runs with their steps and events | 90 days by default. Runs that are still active or `verified` are kept. |
| Runtime package evidence | 15 minutes. |
| Pull-request check bookkeeping | 24 hours. |
| Temporary detections and isolation created by a remediation | Until their expiry: at most 7 days, isolation at most 4 hours. |

## When your organization leaves

When an organization is deleted or unsubscribes, Code Security data is removed
from the live databases after a 7-day grace period, and remaining backup copies
expire within 7 days after that. Scan result files expire within 30 days of their
creation.

Some things are yours and stay with you: tickets, webhook deliveries and pull
requests already created in your systems. An unsubscribed organization also
keeps its own configuration, such as policies and response settings, until the
organization is deleted.

To ask for your organization's Code Security data to be removed, or to confirm
that removal finished, contact LimaCharlie support.

## Isolation between organizations

Every record that holds your data is keyed to your organization. Every API route checks that
the caller belongs to the organization in the path, and the server stamps the
organization itself. Download links for stored files are signed for a single
object and expire, after 15 minutes for SBOMs. Scan jobs run on a network with
no route to the rest of the platform.
