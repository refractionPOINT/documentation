# Google Cloud

!!! warning "Private Beta"
    Cloud Security is currently in **Private Beta**. Features, APIs, and
    configuration formats described here may change before general
    availability. Contact us if you would like access.

Collects the Google Cloud estate across every project in scope — compute,
storage, networking, IAM, KMS, databases, secrets, Pub/Sub — plus CIEM (who can
reach what), Vertex AI inventory, and agentless workload vulnerabilities from
VM Manager.

**Auth model:** a **service-account key** (JSON) granted read-only roles at the
**organization**, **folder**, or **project** you want enumerated. The collector
discovers every active project underneath that node by itself.

## Prerequisites

1. A GCP **project** to own the service account (any project you control — it
   does not have to be one being scanned).
2. Permission to grant IAM roles at the scope you intend to connect
   (Organization Admin / Folder Admin / Project IAM Admin).
3. The **APIs enabled** on the service account's own project — these are the
   client APIs the collector calls:

    ```bash
    gcloud services enable \
      cloudresourcemanager.googleapis.com \
      iam.googleapis.com \
      compute.googleapis.com \
      storage.googleapis.com \
      secretmanager.googleapis.com \
      osconfig.googleapis.com \
      aiplatform.googleapis.com \
      recommender.googleapis.com \
      policyanalyzer.googleapis.com \
      cloudidentity.googleapis.com \
      --project "$SA_PROJECT"
    ```

!!! info "APIs must also be on in the projects being scanned"
    A scanned project with a service API disabled is **skipped for that
    service** — treated as *covered, empty*, never as a permission failure.
    That is usually what you want. `provider test` reports a disabled API as a
    passing check with an explanatory note, precisely so you do not mistake it
    for a missing grant.

## Required roles

Grant at the **scope node** (organization, folder, or project). Roles are
inherited down the hierarchy, so an org-level grant covers every project.

| Role | Why | Preflight check |
|---|---|---|
| `roles/viewer` | The read surface for every resource type (compute, storage, networking, databases, Pub/Sub, KMS, …) | `compute`, `storage`, `projects` |
| `roles/iam.securityReviewer` | `*.getIamPolicy` across services — the CIEM graph (who can access what) | `iam` |

!!! tip "Prefer a tighter grant?"
    `roles/viewer` is the simple, well-understood baseline. A least-privilege
    alternative is `roles/browser` (hierarchy traversal) plus the per-service
    viewer roles you care about, still with `roles/iam.securityReviewer`. Use
    `provider test` to confirm the result — it names every surface that is
    still denied.

## Optional roles

Each adds one inventory or analysis surface. Skipping one leaves that surface
*unobserved*; the sweep still succeeds.

| Role | Unlocks | Preflight check |
|---|---|---|
| `roles/secretmanager.viewer` | Secret **metadata** inventory (names/rotation posture — never secret values) | `secret_manager` |
| `roles/osconfig.vulnerabilityReportViewer` | Agentless workload vulnerabilities from VM Manager | `osconfig_vuln` |
| `roles/osconfig.inventoryViewer` | The OS-inventory join that attaches package name + installed/fixed version to each CVE | `osconfig_vuln` |
| `roles/recommender.iamViewer` | Unused-privilege findings (activity-based CIEM) | `activity_ciem` |
| `roles/policyanalyzer.activityAnalysisViewer` | Dormant-identity / last-authentication findings | `activity_ciem` |
| `roles/aiplatform.viewer` | Vertex AI endpoint, model, and notebook inventory *(already covered by `roles/viewer`)* | `vertex_ai` |
| `roles/cloudidentity.groups.readonly` | Google-group **membership expansion**, so `group:` IAM bindings resolve to real people | `cloud_identity` |

!!! note "Cloud Identity groups are granted elsewhere"
    `roles/cloudidentity.groups.readonly` (or the **Groups Reader** role) is
    granted at the **Cloud Identity account/customer** level in the Google
    Admin console, not on a GCP project. Without it, IAM bindings to groups
    remain visible but their membership is not expanded, so
    "which humans can reach this bucket" stops at the group.

## Create the service account

```bash
SA_PROJECT=my-security-project
ORG_ID=123456789                     # or use --folder / --project instead

gcloud iam service-accounts create lc-cloudsec \
  --display-name "LimaCharlie Cloud Security" \
  --project "$SA_PROJECT"

SA="lc-cloudsec@${SA_PROJECT}.iam.gserviceaccount.com"

# Required
for ROLE in roles/viewer roles/iam.securityReviewer; do
  gcloud organizations add-iam-policy-binding "$ORG_ID" \
    --member "serviceAccount:${SA}" --role "$ROLE"
done

# Optional surfaces
for ROLE in roles/secretmanager.viewer \
            roles/osconfig.vulnerabilityReportViewer \
            roles/osconfig.inventoryViewer \
            roles/recommender.iamViewer \
            roles/policyanalyzer.activityAnalysisViewer; do
  gcloud organizations add-iam-policy-binding "$ORG_ID" \
    --member "serviceAccount:${SA}" --role "$ROLE"
done

gcloud iam service-accounts keys create sa-key.json \
  --iam-account "$SA" --project "$SA_PROJECT"
```

For a folder scope use `gcloud resource-manager folders add-iam-policy-binding
<FOLDER_ID>`; for a single project use `gcloud projects add-iam-policy-binding
<PROJECT_ID>`.

!!! note "In the console"
    **IAM & Admin → Service Accounts → Create service account**, then
    **IAM & Admin → IAM → Grant access** at the organization/folder/project and
    add the roles above. Create the key under the service account's **Keys →
    Add key → Create new key → JSON**.

## Create the credentials secret

The secret value is the **service-account key JSON itself** — no wrapper.

```bash
python3 -c 'import json,sys;print(json.dumps({"secret":open("sa-key.json").read()}))' \
  > gcp-secret.json

limacharlie hive set --hive-name secret --key gcp-collector-sa \
    --input-file gcp-secret.json --enabled
```

Or in the web app: **Organization Settings → Secrets Manager → Add**, name it
`gcp-collector-sa`, and paste the key JSON.

## Create the provider record

`provider.yaml`:

```yaml
provider_type: gcp
gcp_scope: organizations/123456789      # or folders/456 or projects/my-project
credentials: hive://secret/gcp-collector-sa
internal_domains: [example.com]
refresh: 6h
```

| Field | Meaning |
|---|---|
| `gcp_scope` | The node to enumerate: `organizations/{id}`, `folders/{id}`, or `projects/{id}`. Every **active** project underneath is swept. |
| `gcp_project` | Alternative to `gcp_scope` for a single project. Supply one or the other. |

In the web app: **Add provider → Google Cloud**, then set the **scope**,
**Credentials**, and **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The key could not mint a token, or the scope node is unreachable. Nothing else can be probed. |
| `projects` | ✅ | `resourcemanager.projects.list` denied — no project can be discovered under the scope. |
| `compute` | ✅ | `compute.instances.list` denied — no compute inventory. |
| `storage` | ✅ | `storage.buckets.list` denied — no storage inventory. |
| `iam` | ✅ | `getIamPolicy` and/or `serviceAccounts.list` denied — the CIEM access graph cannot be built. |
| `secret_manager` | — | Secret-store inventory unavailable. |
| `activity_ciem` | — | Unused-privilege and dormant-identity findings unavailable. |
| `osconfig_vuln` | — | Workload vulnerability findings unavailable. |
| `vertex_ai` | — | Vertex AI endpoint inventory unavailable. |
| `cloud_identity` | — | Group membership is not expanded; `group:` bindings do not resolve to people. |

!!! tip "Org-scope tests probe one representative project"
    For a folder/organization scope the preflight picks the first active
    project under the node and probes there — IAM grants are inherited, so one
    project answers "is this granted". If that project happens to have a
    service API disabled, the check passes with a note saying the grant was
    neither proven nor disproven.

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails: `PERMISSION_DENIED` on the scope | The service account has no binding at that org/folder/project | Grant `roles/viewer` at the scope node (not just on the SA's own project) |
| `projects` fails | Missing `resourcemanager.projects.list` | `roles/viewer` or `roles/browser` at the scope node |
| `iam` fails on `getIamPolicy` | `roles/viewer` alone does not cover every `getIamPolicy` | Add `roles/iam.securityReviewer` |
| A check passes with *"API not enabled on the probed project"* | Benign — the sweep skips API-disabled projects | Enable the named API if you want that surface; otherwise ignore |
| `activity_ciem` fails with *Recommender API not enabled* | Recommender / Policy Analyzer not enabled on the probed project | Enable `recommender.googleapis.com` and `policyanalyzer.googleapis.com` |
| Inventory is missing whole projects | Those projects are not `ACTIVE`, or the grant is on a narrower node | Confirm project state, and that the binding is at the scope you configured |
