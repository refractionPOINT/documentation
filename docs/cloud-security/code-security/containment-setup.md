# Configure evidence, lineage and remediation

This page covers the settings behind the evidence chain, image lineage, live
pull-request impact, runtime checks and remediation runs. It lists the
permissions each one needs, what to grant on each connection, and which
policies control them. For what these features promise, see
[What Code Security guarantees](guarantees.md).

!!! note "Availability"
    These capabilities are enabled region by region. Until yours is on, the
    routes below answer `feature_disabled`, `disabled` or `codesec_disabled`.
    Scanning, pull-request checks and the rest of Code Security are unaffected.

## Permissions

| Permission | Allows |
|---|---|
| `cloudsec.get` | Reading findings, the evidence chain, coverage, live impact, image lineage and remediation runs. Running a runtime check, which starts collecting package evidence on the finding's sensors and changes nothing else. |
| `cloudsec.set` | Writing policies, pushing Terraform maps and build provenance, rescans. |
| `cloudsec.respond` | Requesting, approving, rejecting and cancelling remediation runs, pressing **Open AutoFix PR**, and writing a `response` policy. |

`cloudsec.respond` is separate on purpose. `cloudsec.set` does not include it,
because it lets a person change your repositories, detection rules and
endpoints. The **Owner** and **Administrator** roles include it. Operator,
Viewer and Basic do not. A user or API key that got its permissions before
`cloudsec.respond` existed does not receive it automatically: grant it
explicitly, or assign the role again.

Writing a `cloudsec_policy` record of type `response` needs both
`cloudsec.set` and `cloudsec.respond`, because that record decides what a
remediation may do.

## Connections and permissions

All of these are read-only unless the row says otherwise.

| Connection | Grant | Needed for |
|---|---|---|
| GitHub App | **Contents: Read-only** | Scanning. See [GitHub setup](../provider-setup/github.md). |
| GitHub App | **Attestations: Read-only** | Verifying GitHub Actions artifact attestations, so an image's link to its repository can be `verified`. After adding it to an existing App, an organization owner must approve the new permission on the installation page. Without it, scanning continues and lineage stays inferred or asserted. |
| GitHub App | **Contents** and **Pull requests: Read and write** | AutoFix and fix pull requests. Write access, granted only if you want it. |
| Google Cloud | `roles/artifactregistry.reader` on the project that hosts the image | Pulling private images to scan them. See [Container image scanning](../provider-setup/gcp.md#container-image-scanning-by-code-security). |
| Google Cloud | `roles/containeranalysis.occurrences.viewer` (Artifact Analysis Occurrences Viewer) on the project that stores the image | Reading Cloud Build provenance so the build can be verified. A grant on the project where the workload runs is not enough if the image lives elsewhere. |
| Cloud accounts that run your workloads | The standard Cloud Security collection roles | Seeing which digest each Cloud Run service and GKE workload runs. Only Cloud Run and GKE digests are observed today. |
| LimaCharlie sensors | A sensor on the host or node | Runtime checks. Without one the answer is `unknown` with `no_sensors`. |

GitLab and Bitbucket connections are scanned with their read tokens. Pull-request
checks, fixes and other writes on GitLab and Bitbucket are not available yet.

### Webhooks

Push rescans and pull-request checks on GitHub arrive through the App's webhook.
Set it up as described in [Pull-request checks and push
rescans](pull-requests.md#set-up-webhook). LimaCharlie checks the
HMAC-SHA256 signature on every delivery, refuses a delivery without a valid one
with `401`, and refuses a repeated delivery for 24 hours.

## Image lineage

Code Security tries to link each running image digest to the source it was built
from, without any change to your build pipeline. Every link carries a `status`:

| Status | How it is established |
|---|---|
| `inferred` | The image's build steps and file paths match a Dockerfile in a repository you connected. It names the repository and the scanned commit whose Dockerfile matched. It does not identify the build commit. |
| `asserted` | The image carries OCI `org.opencontainers.image.source` and `revision` labels, or an unsigned build record, pointing at a connected repository. Anyone who can build the image can write these. |
| `verified` | A signature checks out for that exact digest and a repository in your connections. It comes from Google Cloud Build, from GitHub Actions artifact attestations, or from a statement you pushed that matches a trusted signing identity in your `provenance_trust` policy. |
| `ambiguous` | More than one source matches, or two sources disagree. Neither is used. |
| `unknown` | No usable evidence, or the evidence is past its window. |

Among the evidence Code Security collects itself, only Google Cloud Build and
GitHub Actions signatures make a link `verified`. A label or an unsigned build
claim stays `asserted` however it is written.

The lineage coverage line counts only your own images: images in your own
registries or cloud projects, or matched to your repositories. Public images
from well-known vendor registries that match none of your connections are
counted separately as `third_party`. Images whose ownership cannot be settled
are `ownership_unknown`, and the percentage is withheld until your
connections settle it.

### Build provenance

You can also push signed build statements yourself. This is optional.

- `POST /code/provenance` accepts `lc-build-provenance/v1`, SLSA provenance v1
  and Sigstore bundles, up to 1 MiB, for full sha256 digests and full commits.
  It needs `cloudsec.set`.
- A `provenance_trust` policy names the builders you trust, per repository.
  A statement verified against a Sigstore identity or GitHub's Sigstore
  instance is `verified`. A statement signed with a public key you uploaded is
  `asserted`.
- LimaCharlie sets `trust`, `verified`, `signer` and similar fields itself and
  refuses a statement that tries to set them. It never fetches a URL found in a
  statement.
- Two statements that disagree about the source give `ambiguous` and a coverage
  note. The later one does not win.

## Terraform maps

Code-to-cloud attribution matches a Terraform declaration to a live resource by
exact identity. When a name is computed at apply time, the scan alone cannot
resolve it, and the finding's attribution reason is `unresolved_name`. A map
fills the gap.

LimaCharlie never accepts a state or plan file. You extract a map on your own
machine or CI runner and push only the map:

```bash
terraform show -json > terraform.json

limacharlie cloudsec code iac-map extract --input terraform.json \
    --source-kind state_identity --repository acme/infra \
    --commit 3f1c2a9e0b7d4c5a6e8f9a0b1c2d3e4f5a6b7c8d --workspace default > map.json

limacharlie cloudsec code iac-map push --input map.json
```

- `extract` runs offline. It does not run Terraform, read your environment,
  contact a server or authenticate. It needs the `iac-map-extract` binary on
  your `PATH`.
- `--source-kind state_identity` keeps resource identities only.
  `plan_desired` adds allowlisted desired settings (yes/no values) so drift can
  be checked.
- Every value Terraform marks sensitive or unknown is dropped. On push, a map
  with a secret-looking key or a value over 4 KiB is refused.
- `push` needs `cloudsec.set`, is limited to 20 MiB and 30 pushes a minute, and
  waits until the map is published. Pushing the same map again writes nothing.
  A partial map only adds; it never deletes earlier mappings.

## Pull-request disclosure

Pull-request checks can show what a change touches in production. The
`pr_live_context` field of the [code-scanning policy](policy.md) decides how
much:

| Value | The check shows |
|---|---|
| `off` (default) | Nothing about live resources. The check is exactly what it was without this feature. |
| `risk_summary` | Counts, the environment, yes/no exposure, privilege and sensitivity facts, the highest severity, and a link that needs a LimaCharlie login. No resource names, account IDs, IP addresses or sensor IDs. |
| `resource_details` | The above plus per-declaration impact details. Resource names are still left out of the pull request. The authenticated impact view can show them. |

When several policies select one repository, the one that discloses least wins.
The impact lookup has a 2-second budget. If it fails or runs out of time, the
check still publishes its normal scan verdict, unchanged, with a note that the
live context is missing.

## Remediation runs

Every change Code Security makes to your systems is a remediation run. A run
states its target, which the server derives from the finding. You cannot point
a run at another target. It waits for a person with `cloudsec.respond` to
approve it, and its outcome comes back through an authenticated callback that
the run records. Pre-approval is not available: every run needs a human
approval.

| Action | What it does | Needs |
|---|---|---|
| `open_fix_pr` | Opens a pull request that upgrades a vulnerable dependency or base image. | The GitHub write permissions above. |
| `notify_ticket` | Sends a notification or opens a ticket. | A `code-notify-ticket-v1` playbook. |
| `temporary_detection` | Installs a detection rule that expires on its own. | A `code-temporary-detection-v1` playbook. |
| `isolate_endpoint` | Network-isolates a sensor for a limited time. | A `code-isolate-endpoint-v1` playbook that lists the sensors it may act on. |

Requesting a run and deciding it are separate calls:

```bash
limacharlie cloudsec remediation create fnd_0123abcd --action open_fix_pr
limacharlie cloudsec remediation approve rem_0123abcd                 # prints what you are approving
limacharlie cloudsec remediation approve rem_0123abcd --confirm <token>
```

The approval binds to the run's current target and generation. If either
changes after you reviewed it, the approval is refused and you review again.

Limits: 100 active runs per organization and 10 per finding. A run waits at
most 72 hours for approval and is monitored for up to 7 days after it acts.

### AutoFix is a remediation run

Pressing **Open AutoFix PR** creates an `open_fix_pr` run. The person who
presses is recorded as both requester and approver, so the button needs
`cloudsec.respond`. The pull request and its outcome come back through the same
callback as any other run. See [AutoFix pull requests](autofix.md).

### Response playbooks

Notify, ticket, temporary detection and isolation run LimaCharlie-managed
templates that you install with a `response` policy. You cannot write a rule
body, command or target through it.

```yaml
policy_type: response
response:
  playbooks:
    - template: code-temporary-detection-v1
      version: 1
      mode: live
      approval: human
      max_duration_seconds: 86400
    - template: code-notify-ticket-v1
      version: 1
      channels: [notify, ticket]
```

| Field | Meaning |
|---|---|
| `template`, `version` | The managed template and its version (`1`). A run is bound to the installation it was approved under. If the installation changes before the run acts, the run stops with `installation_changed`. |
| `mode` | `dry_run` (the default) records exactly what would happen and does nothing. `live` acts. |
| `approval` | `human`, the only mode. |
| `max_duration_seconds` | For temporary controls. 5 minutes to 7 days, default 24 hours. Isolation is capped at 4 hours. |
| `channels` | For `code-notify-ticket-v1`: `notify`, `ticket`, or both. |
| `sensors` | For `code-isolate-endpoint-v1`, required: 1 to 10 sensor IDs. The target still comes from the finding. This list only narrows it. |

At most 8 playbooks, one per template. Isolation also needs an approval less
than 10 minutes old at the moment it acts.

LimaCharlie never merges, deploys, rolls back or revokes credentials for you.
There is no template for those.

## Exclusions

Several settings keep things out of Code Security. They do different things:

| Setting | Effect |
|---|---|
| `repos.exclude` in the [code-scanning policy](policy.md#fields) | The repository is not scanned. The console's **Exclude from scanning** writes it. Exclude always wins over include. |
| `paths` on a [code rule](code-rules.md) | That rule does not run on those paths. |
| A [`suppression` policy](../configuration.md#suppression-finding-disposition-policy) or a VEX statement | Matching findings get a disposition. They stay recorded. |
| A [`collection` exclusion](../configuration.md#exclusions-the-escape-hatch) | The cloud resources it matches are removed from inventory. |

A collection exclusion also removes those resources from Code Security's view of
your cloud. Evidence that needs them then reads `resource_not_collected` or
`workload_not_resolved`. It never reads as "not exposed" or "not running".
