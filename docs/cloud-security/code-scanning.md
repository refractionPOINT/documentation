# Code Scanning and Pushed Results

Cloud Security can analyze source code in two ways:

- **Hosted scanning** checks repositories selected by your source-control
  connection and code-scanning policy.
- **Pushed results** let a developer or CI pipeline scan a checkout locally, or
  upload an existing SARIF or CycloneDX document.

Both paths write to the same findings worklist. Use pushed results when source
code must stay in your environment, when you already run another scanner, or
when you want scan feedback on every push instead of waiting for a scheduled
hosted scan.

!!! note "CLI version"
    The `cloudsec code` commands used on this page were added after CLI 5.6.2.
    They require the first `limacharlie` release newer than 5.6.2. Check your
    installation before using the examples:

    ```bash
    limacharlie --version
    limacharlie cloudsec code scan --help
    ```

## Before you begin

You need:

- a LimaCharlie organization subscribed to `ext-cloud-security`;
- an enabled code-scanning policy that selects the repository;
- an API key with `cloudsec.get` and `cloudsec.set`;
- the current [LimaCharlie CLI](cli.md); and
- Docker for local scans. Uploading an existing document does not require
  Docker.

Authenticate interactively with `limacharlie auth login`, or set `LC_OID` and
`LC_API_KEY` in CI. Create and scope organization API keys as described in
[API Keys](../7-administration/access/api-keys.md).

To configure the required policy in the console, open **Cloud Security →
Policies → Code scanning**, turn on **Enable code scanning**, and add the
repository's `<owner>/<repository>` name under **Include**. Select at least one
hosted scanning engine, then save the policy. The policy can select a repository
even when it does not come from a connected source-control organization.

Repository names use the `<owner>/<repository>` form, for example `acme/api`.
If a checkout has a hosted Git remote, the local scan command can infer this
name and the current commit. Pass `--repo` and `--commit` explicitly when the
remote does not identify them unambiguously.

## Scan a local checkout

From the repository root, scan and send the result to Cloud Security:

```bash
limacharlie --output yaml cloudsec code scan . \
  --repo acme/api \
  --commit "$(git rev-parse HEAD)" \
  --ingest
```

The default scan covers software dependencies, infrastructure as code, and
licenses. To select supported scanners explicitly, pass a comma-separated
list:

```bash
limacharlie --output yaml cloudsec code scan . \
  --repo acme/api \
  --scanners sca,iac,sast,licenses,images \
  --ingest
```

The CLI runs the published LimaCharlie scanner container. The checkout is
mounted read-only. Nothing from the checkout is sent to LimaCharlie unless you
add `--ingest`; in that case, only the generated report is uploaded.

To inspect or archive a report without uploading it, write it to a file:

```bash
limacharlie cloudsec code scan . \
  --repo acme/api \
  -o lc-code-report.json.gz
```

The output is a gzipped LimaCharlie `report/v1` document. A scan must use either
`--ingest`, `-o`, or both, so a completed scan never discards its only copy of
the report.

!!! info "Secret scanning uses the hosted lane"
    Local scans do not accept the `secrets` or `secrets_history` scanners.
    Secret findings require identity data held by the hosted service to merge
    safely. Use hosted scanning for credentials and secret history.

## Push an existing scanner result

Use `code ingest` when another tool already produced the result. The command
accepts:

- `sarif` for a SARIF results document;
- `cyclonedx` for a CycloneDX bill of materials; or
- `report` for a LimaCharlie `report/v1` document produced by `code scan`.

For example, push a SARIF file from the current commit:

```bash
limacharlie --output yaml cloudsec code ingest \
  --repo acme/api \
  --source sarif \
  --file trivy.sarif \
  --commit "$(git rev-parse HEAD)" \
  --ref "$(git branch --show-current)"
```

Or push an existing CycloneDX SBOM:

```bash
limacharlie --output yaml cloudsec code ingest \
  --repo acme/api \
  --source cyclonedx \
  --file sbom.cdx.json \
  --commit "$(git rev-parse HEAD)"
```

Files ending in `.gz` stay compressed in transit. A document can be up to 20
MiB; narrow the scan or split it into separate documents if it exceeds that
limit.

A pushed repository does not need to come from a connected source-control
organization. The push creates the repository entry with only the facts the
document supplies. In that case, also pass `--default-branch` because no
provider connection can supply it:

```bash
limacharlie --output yaml cloudsec code ingest \
  --repo acme/private-api \
  --source sarif \
  --file results.sarif \
  --default-branch main \
  --commit "$COMMIT_SHA"
```

The repository must still match an enabled code-scanning policy and counts
toward the same repository quota as a connected repository.

## Run on every GitHub push

Store the organization UUID as the `LC_OID` Actions secret and a least-privilege
organization API key as `LC_API_KEY`. Then add
`.github/workflows/limacharlie-code-scan.yml` to the repository:

```yaml
name: LimaCharlie code scan

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - name: Check out repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install LimaCharlie CLI
        run: pip install --upgrade limacharlie

      - name: Scan and push results
        env:
          LC_API_KEY: ${{ secrets.LC_API_KEY }}
          LC_OID: ${{ secrets.LC_OID }}
        run: |
          limacharlie --output yaml cloudsec code scan . \
            --repo "$GITHUB_REPOSITORY" \
            --commit "$GITHUB_SHA" \
            --ref "$GITHUB_REF" \
            --ingest
```

The workflow grants GitHub only read access to repository contents. The
LimaCharlie key controls the upload and should contain only the permissions
listed in [Before you begin](#before-you-begin).

If your existing scanner produces SARIF, replace the final step with that
scanner followed by `cloudsec code ingest`. For example:

```yaml
      - name: Push SARIF results
        env:
          LC_API_KEY: ${{ secrets.LC_API_KEY }}
          LC_OID: ${{ secrets.LC_OID }}
        run: |
          limacharlie --output yaml cloudsec code ingest \
            --repo "$GITHUB_REPOSITORY" \
            --source sarif \
            --file results.sarif \
            --commit "$GITHUB_SHA" \
            --ref "$GITHUB_REF"
```

## Review the result

Confirm that Cloud Security recorded the repository:

```bash
limacharlie --output yaml cloudsec code repos -q acme/api
```

Then list its open pushed findings:

```bash
limacharlie --output yaml cloudsec finding list \
  --repo acme/api \
  --source ingest \
  --status open
```

Repository rows identify their source as `ingest`, `hosted`, or `both`.
Pushed findings use the same triage, ownership, Cases, Outputs, and automation
as hosted findings.

Pushing the same document again is idempotent. When a newer document omits a
finding previously reported by that pushed source, Cloud Security closes that
finding. A pushed document never closes a finding owned by the hosted scanner.
The ingest response also contains `notes` for results it could not safely
import; for example, credential findings from third-party documents are
deliberately skipped.

## Troubleshooting

| Problem | What to check |
|---|---|
| A `cloudsec code` command is missing | Upgrade to a CLI release newer than 5.6.2. |
| The CLI cannot identify the repository | Pass `--repo <owner>/<repository>` explicitly. |
| Docker is not found | Install and start Docker, or upload a document produced by an existing scanner with `code ingest`. |
| The repository is not recorded | Confirm that the repository matches an enabled code-scanning policy and is within the organization's repository quota. |
| The document is rejected as too large | Keep it below 20 MiB by narrowing the scan or splitting independent results into separate documents. |
| Secret results do not appear | Use hosted secret scanning; local and third-party secret findings are intentionally not ingested. |
| Hosted scanning reports `github_app_missing_contents_permission` | The connected GitHub App cannot read repository contents, so nothing could be cloned. Add **Repository → Contents: Read-only** to the App, then approve the permission request on the organization's installation page: GitHub requires an owner to accept a permission increase on an existing installation, so editing the App alone is not enough. Nothing was scanned and no existing finding changed. |
| A repository reports `scan_status: partial` with `sast_ruleset_unresolved` | The code-scanning policy names a static-analysis rule pack that is not available, so static analysis did not run on that repository. Clear the custom `sast_ruleset` value to use the built-in pack. Nothing else about the repository is affected: its dependency, infrastructure, license and secret findings are complete and still close normally. |
| A repository reports `scan_status: unknown` with `repo_not_scanned` | Nothing has scanned it yet. Confirm it is inside an enabled code-scanning policy's include list, then allow the next scheduled pass to reach it. `limacharlie cloudsec code status` is the authoritative answer about the scan run itself; follow it when the two disagree. |
| A repository or image reports `free_tier_code_repos_cap` or `free_tier_code_images_cap` | The organization is on the free tier, which covers the first 10 repositories per connected source-control organization and the 5 most-referenced container images per organization. The covered set is stable rather than rotating, so findings do not appear and disappear between passes. Narrow the policy to the repositories you care about, or move off the free tier. A `_report` suffix means the limit is not being applied: everything was scanned, and the message reports what the limit would have done. |
| A pull-request check or fix pull request reports `write_app_not_configured` or `write_app_lacks_contents` | Writing to a repository uses a separate, opt-in GitHub App that you create and install; the read-only scanning connection is never used to write. `write_app_not_configured` means no such App is recorded on the connection. `write_app_lacks_contents` means the App is installed but still needs **Contents: Read and write**, which is a different page in GitHub's settings. Scanning and existing findings are unaffected either way. |
| A fix pull request is marked `lockfile_stale` | The manifest was updated and the lockfile beside it was not, so the change does not take effect until the lock is regenerated. Run the command given in the pull-request body before merging, then review the result: `npm install --package-lock-only --ignore-scripts`, `yarn install --mode update-lockfile`, `pnpm install --lockfile-only`, or `go mod tidy`. Maven and `requirements.txt` have no lockfile and are complete as opened. |
