# Scan private container images

Code Security scans digest-pinned images found in your cloud inventory. Public images need no registry credential. For private images, connect the registry as described below. An image that the registry will not let LimaCharlie pull stays **unscanned** with an access reason; findings for that image are incomplete. Other images continue scanning.

Registry credentials are used by the short-lived image fetch job. The scan container receives the downloaded image, without a registry credential.

| Registry | Grant or credential | Where to configure it |
|---|---|---|
| Google Artifact Registry / GCR | `roles/artifactregistry.reader` on the image's project for the connected service account. Legacy Container Registry may also need `roles/storage.objectViewer` on its image bucket. | [Google Cloud provider](../provider-setup/gcp.md#container-image-scanning-by-code-security) |
| Amazon ECR | `ecr:GetAuthorizationToken` on the connected assume-role, and `ecr:BatchGetImage` and `ecr:GetDownloadUrlForLayer` for each repository to scan. For member accounts, `organizations:DescribeAccount` on the connected role. | [AWS provider](../provider-setup/aws.md#private-ecr-images) |
| Azure Container Registry | `AcrPull` on the registry for the connected app registration. | [Azure provider](../provider-setup/azure.md#private-azure-container-registry-images) |
| Docker Hub | A token with read access to the exact private repository. | **Cloud Security → Settings → Registries** |
| Quay.io | A read-only robot account with access to the exact repository. | **Cloud Security → Settings → Registries** |
| GitHub Container Registry (`ghcr.io`) | A classic personal access token with `read:packages`, from a user allowed to read the package. If your GitHub organization requires SSO, authorize the token for it. | **Cloud Security → Settings → Registries** |

For Docker Hub, Quay.io, and GHCR, store the token in a LimaCharlie secret and create one registry credential setting **per repository**. Enter the registry, repository name (for example, `team/app`), username, and the secret reference. The setting cannot contain a literal token. Use a read-only account or token, and grant it access only to repositories that must be scanned. A credential for `team/app` is never used to pull `team/other`.

To manage the same setting as code, create an enabled secret with the registry
token as its value, then save `registry-credential.yaml`:

```yaml
policy_type: registry_credential
registry_credential:
  registry: ghcr
  repository: team/app
  username: registry-reader
  secret_ref: hive://secret/ghcr-team-app
```

```bash
limacharlie hive set --hive-name cloudsec_policy --key ghcr-team-app \
  --input-file registry-credential.yaml --enabled --oid "$OID"
```

`registry` is `dockerhub`, `quay` or `ghcr`, not a registry URL. Repository
paths are exact, lowercase and contain no tag or digest. Docker Hub and Quay
accept `namespace/image`; GHCR also accepts nested paths. Saving the policy
needs `cloudsec.set` **and read access to the referenced secret**, including
any record ACL. Create the secret before saving the policy; a misspelled or
unreadable reference is refused.

For ECR and ACR, LimaCharlie uses your existing cloud connection. It exchanges that connection for a short-lived registry pull credential; no second long-lived credential is needed. Each pull credential can read only the one repository being scanned: ACR tokens request `repository:<name>:pull`, and ECR tokens come from a session whose policy allows reads on that single repository.

ECR images are pulled only from the connected AWS account, or from member accounts that AWS Organizations confirms belong to the connected organization. Images in other AWS accounts are reported as not scanned; LimaCharlie does not request credentials for them. Likewise, ACR images are pulled only from registries that LimaCharlie has inventoried through your connected Azure subscriptions.

If one image cannot be pulled, the pass is **partial**, not a clean result. Open the image to see the registry and reason. `image_registry_credential` means a usable credential is missing; `image_registry_permission` means the registry refused the supplied credential. After fixing access, use **Sync now** on the source connection to retry immediately, or wait for the next scheduled attempt.

See [Troubleshooting](troubleshooting.md#scanning) for other image failures.
