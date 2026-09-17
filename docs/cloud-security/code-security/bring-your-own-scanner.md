# Bring your own scanner

You don't have to rely only on the hosted scan. You can:

- **push results from a scanner you already run**, as SARIF or CycloneDX;
- **run the LimaCharlie scanner in your own CI** or on your machine, and push the
  report;
- **cover repositories LimaCharlie is not connected to**.

Pushed findings land in the same worklist as hosted ones, marked with their
source. Filter them with **Code source → Pushed** on Risks, or
`--source ingest` in the CLI.

All pushes need an API key with `cloudsec.set`.

## Push existing results

```bash
limacharlie cloudsec code ingest --repo acme/payments --source sarif \
    -f results.sarif --scanner-succeeded
```

| `--source` | Format |
|---|---|
| `sarif` | SARIF 2.1.0, which most scanners can produce |
| `cyclonedx` | A CycloneDX bill of materials, with or without a `vulnerabilities` section |
| `report` | The LimaCharlie scanner's own report, as produced by [`code scan`](#scan-locally-or-in-ci) |

Pass `--commit` with the commit that was scanned. Documents can be up to
**20 MiB** as sent, and may be gzip-compressed. Each API key can push up to 600
documents an hour.

!!! warning "Pass `--scanner-succeeded` for SARIF"
    A SARIF push only closes findings when the document says the scanner run
    succeeded, and many tools (Trivy, for example) do not write that field.
    Without `--scanner-succeeded`, fixed findings from those tools never close.
    Pass it when your scan step succeeded.

### How pushed findings merge

- **Duplicates collapse.** A pushed finding is matched to a hosted one by
  identity, not line number. For a dependency, that is the advisory, the package
  and the manifest. When both see the same issue there is one finding, and its
  age and triage state are kept. Pushing the same document twice changes
  nothing.
- **A push only closes what the same tool reported.** Fix a dependency, push
  again from the same tool, and that finding closes. A push never closes a hosted
  finding, and one SARIF tool never closes another tool's findings. If the hosted
  scan later finds the same issue, the hosted scan takes it over and closes it
  when it is fixed.
- **A push closes findings only when it is complete:** a SARIF document must say
  its run succeeded (see above), and a CycloneDX document needs a
  `vulnerabilities` section.
- **Secrets are refused from third-party documents**
  (`secrets_not_ingestable`). LimaCharlie identifies a secret by a keyed hash
  that foreign formats cannot carry, and those documents often contain the
  credential itself. Use the hosted scan for secrets.
- **What a format cannot express is reported.** The response's `notes` explain
  it. For example, `iac_resource_ref_absent` means SARIF could only identify an
  infrastructure finding by file, so it will not merge with the hosted scan's
  finding for the same resource.

### Repositories LimaCharlie does not collect

A push for a repository no connection covers creates the repository in your
inventory. Add `--default-branch`, since no connection can supply it:

```bash
limacharlie cloudsec code ingest \
  --repo acme/private-api \
  --source sarif \
  --file results.sarif \
  --default-branch main \
  --commit "$COMMIT_SHA" \
  --scanner-succeeded
```

The repository must still match an enabled code-scanning policy, and it counts
toward the same repository limits. Pushes can create up to 500 repositories per
provider. A repository created this way is removed with its findings after 30
days without a push for a new commit.

## Scan locally or in CI

`code scan` runs the LimaCharlie scanner on a checkout. Your code never leaves
the machine, only the report does.

```bash
# Scan and keep the report, without sending anything.
limacharlie cloudsec code scan ~/src/payments -o report.json.gz

# Scan and push.
limacharlie cloudsec code scan ~/src/payments --repo acme/payments --ingest
```

- It needs **Docker**, since the scanner runs in a container with its engines and
  databases. `--binary` runs an installed scanner instead.
- `--scanners` defaults to `sca,iac,licenses`. `sast` and `images` can also run
  locally. Locally, `images` lists the images your Dockerfiles use but does not
  scan them.
- Local static analysis **never applies your organization's
  [code rules](code-rules.md)**. With the CLI's default container image, it runs
  the default rules built into that scanner image. Scanner releases that support
  code rules have no built-in rules. They run static analysis only when started
  with their `--default-rules` flag (LimaCharlie's default set) or `--rules-file`,
  and the CLI does not pass either one. So pointing `--image` or `--binary` at one
  of those releases gives a report with `sast_no_rules` and no code weaknesses.
- A scan must use `--ingest`, `-o`, or both, so the report is never thrown away.
- `--repo` is read from the checkout's git remote when possible. Pass it
  explicitly in CI.

**Secret scanning does not run locally.** `--scanners sca,iac,secrets` fails
rather than skipping secrets quietly. Local findings could not be matched to the
hosted scan's secret findings, so use the hosted scan for secrets.

### GitHub Actions

This workflow scans every push to `main` and pushes the report. The scan runs on
your runner.

```yaml
name: LimaCharlie code scan

on:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install the LimaCharlie CLI
        run: pipx install limacharlie

      - name: Scan and push
        env:
          # An API key with cloudsec.set, stored as repository secrets.
          LC_OID: ${{ secrets.LC_OID }}
          LC_API_KEY: ${{ secrets.LC_API_KEY }}
        run: |
          limacharlie cloudsec code scan . \
            --repo "$GITHUB_REPOSITORY" \
            --commit "$GITHUB_SHA" \
            --ingest
```

`$GITHUB_REPOSITORY` is already `<owner>/<name>`, the key LimaCharlie uses.

To push results from a scanner you already run instead, replace the last step:

```yaml
      - name: Push existing results
        env:
          LC_OID: ${{ secrets.LC_OID }}
          LC_API_KEY: ${{ secrets.LC_API_KEY }}
        run: |
          limacharlie cloudsec code ingest \
            --repo "$GITHUB_REPOSITORY" \
            --source sarif \
            --commit "$GITHUB_SHA" \
            --scanner-succeeded \
            -f results.sarif
```

**Cloud Security → Settings → Integrations** also shows ready-to-copy CLI and
`curl` examples for pushing results.

## In your IDE

The LimaCharlie MCP server can scan your working copy from an AI assistant in
your editor, before anything is pushed. See
[Cloud Security in your IDE](../mcp.md).
