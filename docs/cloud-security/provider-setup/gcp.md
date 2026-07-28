# Google Cloud

!!! warning "Private Beta"
    Cloud Security is in **Private Beta**. Features, APIs, and configuration
    formats on this page can change before general availability. Contact us to
    request access.

This provider collects the Google Cloud estate in each project in scope:
compute, storage, networking, IAM, KMS, databases, secrets, and Pub/Sub. It
also collects CIEM data (who can reach what), Vertex AI inventory, and
agentless workload vulnerabilities from VM Manager.

**Auth model:** a **service-account key** (JSON) with read-only roles at the
**organization**, **folder**, or **project** that you want to enumerate. The
collector finds every active project below that node.

## Prerequisites

1. A GCP **project** to own the service account (any project that you control;
   it does not need to be a scanned project).
2. Permission to grant IAM roles at the scope that you connect
   (Organization Admin / Folder Admin / Project IAM Admin).
3. The **APIs enabled** on the project of the service account. The collector
   calls these client APIs:

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
    If a scanned project has a service API disabled, the sweep **skips that
    service** for the project. The sweep records the service as *covered,
    empty*, never as a permission failure. `provider test` reports a disabled
    API as a check that passes, with a note. The note stops confusion with a
    missing grant.

## Required roles

Grant the roles at the **scope node** (organization, folder, or project). The
hierarchy inherits roles downward, so a grant at the organization covers every
project.

| Role | Why | Preflight check |
|---|---|---|
| `roles/viewer` | The read surface for every resource type (compute, storage, networking, databases, Pub/Sub, KMS, …) | `compute`, `storage`, `projects` |
| `roles/iam.securityReviewer` | `*.getIamPolicy` in all services. This builds the CIEM graph (who can access what) | `iam` |

!!! tip "Prefer a tighter grant?"
    `roles/viewer` is the simple baseline. For least privilege, use
    `roles/browser` (hierarchy traversal), the viewer role for each service
    that you need, and `roles/iam.securityReviewer`. Run `provider test` to
    check the result. It names each surface that is still denied.

## Optional roles

Each role adds one inventory or analysis surface. If you omit a role, that
surface stays *unobserved*, but the sweep still succeeds.

| Role | Unlocks | Preflight check |
|---|---|---|
| `roles/secretmanager.viewer` | Secret **metadata** inventory (names/rotation posture — never secret values) | `secret_manager` |
| `roles/osconfig.vulnerabilityReportViewer` | Agentless workload vulnerabilities from VM Manager | `osconfig_vuln` |
| `roles/osconfig.inventoryViewer` | The OS-inventory join that attaches package name + installed/fixed version to each CVE | `osconfig_vuln` |
| `roles/recommender.iamViewer` | Unused-privilege findings (activity-based CIEM) | `activity_ciem` |
| `roles/policyanalyzer.activityAnalysisViewer` | Dormant-identity / last-authentication findings | `activity_ciem` |
| `roles/aiplatform.viewer` | Vertex AI endpoint, model, and notebook inventory | `vertex_ai` |
| `roles/cloudidentity.groups.readonly` | Google-group **membership expansion**, so `group:` IAM bindings resolve to real people | `cloud_identity` |

!!! note "Recommender needs only the list permission"
    The Google walkthrough to *review* role recommendations in the console
    also asks for `roles/iam.roleViewer` and a resource IAM-admin role. Those
    roles are for interactive application of recommendations. This collector
    only **lists** the recommendations, and the `roles/viewer` baseline covers
    the reads of role metadata.

!!! note "Cloud Identity groups are granted elsewhere"
    Grant `roles/cloudidentity.groups.readonly` (or the **Groups Reader**
    role) at the **Cloud Identity account/customer** level in the Google Admin
    console, not on a GCP project. Without this role, IAM bindings to groups
    stay visible, but the collector does not expand their membership. The
    answer to "which humans can reach this bucket" then stops at the group.

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

For a folder scope, use `gcloud resource-manager folders add-iam-policy-binding
<FOLDER_ID>`. For a single project, use `gcloud projects add-iam-policy-binding
<PROJECT_ID>`.

!!! note "In the console"
    1. Go to **IAM & Admin → Service Accounts → Create service account**.
    2. Go to **IAM & Admin → IAM → Grant access** at the
       organization/folder/project and add the roles above.
    3. Create the key under **Keys → Add key → Create new key → JSON** of the
       service account.

## Create the credentials secret

The secret value is the **service-account key JSON itself**, with no wrapper.

```bash
python3 -c 'import json,sys;print(json.dumps({"secret":open("sa-key.json").read()}))' \
  > gcp-secret.json

limacharlie hive set --hive-name secret --key gcp-collector-sa \
    --input-file gcp-secret.json --enabled
```

Or, in the web app, select **Organization Settings → Secrets Manager → Add**.
Name the secret `gcp-collector-sa` and paste the key JSON.

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
| `gcp_scope` | The node to enumerate: `organizations/{id}`, `folders/{id}`, or `projects/{id}`. The sweep covers each **active** project below the node. |
| `gcp_project` | An alternative to `gcp_scope` for a single project. Set one field or the other. |

In the web app, select **Add provider → Google Cloud**. Then set the
**scope**, **Credentials**, and **Refresh interval**.

## Verify

```bash
limacharlie cloudsec provider test --input-file provider.yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `auth` | ✅ | The key cannot get a token, or the scope node is unreachable. The test probes nothing else. |
| `projects` | ✅ | `resourcemanager.projects.list` is denied. The collector cannot discover projects under the scope. |
| `compute` | ✅ | `compute.instances.list` is denied. There is no compute inventory. |
| `storage` | ✅ | `storage.buckets.list` is denied. There is no storage inventory. |
| `iam` | ✅ | `getIamPolicy` and/or `serviceAccounts.list` is denied. LimaCharlie cannot build the CIEM access graph. |
| `secret_manager` | — | Secret-store inventory unavailable. |
| `activity_ciem` | — | Unused-privilege and dormant-identity findings unavailable. |
| `osconfig_vuln` | — | Workload vulnerability findings unavailable. |
| `vertex_ai` | — | Vertex AI endpoint inventory unavailable. |
| `cloud_identity` | — | The collector does not expand group membership. `group:` bindings do not resolve to people. |

!!! tip "Org-scope tests probe one representative project"
    For a folder scope or an organization scope, the preflight selects the
    first active project under the node and probes that project. The
    hierarchy inherits IAM grants, so one project shows if a grant exists. If
    that project has a service API disabled, the check passes with a note. The
    note says that the test neither proved nor disproved the grant.

## Troubleshooting

| `provider test` result | Cause | Fix |
|---|---|---|
| `auth` fails: `PERMISSION_DENIED` on the scope | The service account has no binding at that org/folder/project | Grant `roles/viewer` at the scope node, not only on the own project of the service account |
| `projects` fails | Missing `resourcemanager.projects.list` | `roles/viewer` or `roles/browser` at the scope node |
| `iam` fails on `getIamPolicy` | `roles/viewer` alone does not cover every `getIamPolicy` | Add `roles/iam.securityReviewer` |
| A check passes with *"API not enabled on the probed project"* | This is not an error. The sweep skips projects that have the API disabled | Enable the named API if you want that surface. If not, ignore the note |
| `activity_ciem` fails with *Recommender API not enabled* | Recommender / Policy Analyzer not enabled on the probed project | Enable `recommender.googleapis.com` and `policyanalyzer.googleapis.com` |
| Inventory is missing whole projects | Those projects are not `ACTIVE`, or the grant is on a narrower node | Check the project state. Check that the binding is at the scope that you configured |
