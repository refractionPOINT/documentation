# Troubleshooting Code Security

Start with the **Set up code security** checklist on the **Code security** page,
if it is shown. It names what is not set up and links to the fix. From the CLI,
`limacharlie cloudsec code status` shows whether scans run and what failed.

## Scanning

| Problem | What to check |
|---|---|
| Nothing is scanned | An enabled code-scanning policy exists and selects the repository. Connecting a provider alone scans nothing. |
| A repository shows `unknown` with `repo_not_scanned` | It has not been reached yet. Confirm it matches the policy's `include` list and not its `exclude` list, then wait for the next pass or use **Rescan now**. |
| A repository shows `free_tier_code_repos_cap` | The free tier covers the first 10 repositories per source-control organization. Narrow the policy to the repositories you care about, or upgrade. A code ending in `_report` means the limit is not enforced: everything was scanned. |
| `github_app_missing_contents_permission` | The GitHub App cannot read code. Add **Repository → Contents: Read-only** to the App, then have a GitHub organization owner **approve the permission request** on the installation page. Editing the App alone is not enough. |
| A repository shows `partial` | A limit cut the scan short, and the limit is listed on the repository. Its findings are incomplete, not clean. |
| `sast_ruleset_unresolved` | The policy names a static-analysis rule pack that is not available. Clear `sast_ruleset`. Other engines are unaffected. |
| GitLab projects are listed but never scanned | The connection is to a self-managed GitLab instance. Only GitLab.com projects can be scanned. The connection test reports `code_scanning_reachable`. |
| The repository drawer says it is outside the App's installation | The GitHub App is installed on selected repositories only. Add the repository on GitHub's installation page. |
| A finding you expected is missing entirely | Check `severity_floor`. Findings below it are never recorded, so there is nothing to filter for. |
| No findings, and you expected some | Check the repository's engine states in its **Details** drawer. An engine that is off, partial or has no result has not proven the repository clean. |

## Push rescans and pull-request checks

| Problem | What to check |
|---|---|
| Pushes are not rescanned, or pull requests get no check | Work through [Is it firing?](pull-requests.md#is-it-firing). |
| The webhook shows **Not connected** | No active webhook: use **Set up webhook** and finish on GitHub. Points elsewhere: use **Fix webhook**. |
| The webhook shows **Missing events** | A GitHub organization owner ticks **Push** and **Pull request** under the App's **Permissions & events**. GitHub has no API for this. |
| The webhook shows **Not verified** | GitHub could not be read. It is checked again automatically. If it persists, check that the App and its private key still exist. |
| GitHub's **Recent Deliveries** show `401` | The App signs with a different secret. Use **Re-sync webhook secret**. |
| The webhook shows **Name conflict** | Two connection names differ only by letter case. Delete one and add it again with a different name. |
| **Fix webhook** fails with `webhook_in_use_by_other_org` | The App already sends to another LimaCharlie organization. Create a separate App for this organization. |
| **Fix webhook** fails with `github_credential_rejected` or `credential_unavailable` | Generate a new private key for the App on GitHub and update the connection's credentials secret. |
| **Fix webhook** fails with `webhook_not_active` | The webhook was turned off on GitHub. Follow [Set up webhook](pull-requests.md#set-up-webhook). |
| **Fix webhook** times out | The change may have been applied. Choose **Check again** before retrying. |
| Checks stopped appearing after editing a rule | The `pr` field must stay a bare path, not a `{{ }}` template. See [If you fork these rules](pull-requests.md#3-install-the-rules). |
| A pull-request check reports `write_app_not_configured` | The App lacks **Checks** or **Pull requests: Read and write**, or is not installed on the repository. Grant them and approve on the installation page. |

## GitHub App setup

| Problem | What to check |
|---|---|
| The wizard opens on **I already have a GitHub App** | Your user or API key is missing permissions the automatic setup needs. The wizard names them. |
| "The installation was requested" | The installer is not a GitHub organization owner. After an owner approves, add the connection with **I already have a GitHub App**. |
| The setup expired | GitHub allows an hour to create the App. Start again from Settings. If the App was created anyway, delete it or connect it with a new private key. |
| The page closed before the private key was saved | The App may exist on GitHub. Generate a new private key and connect it with **I already have a GitHub App**, or delete the App and start again. |
| **Secret not synced** | The setup could not confirm the webhook secret. Use **Sync webhook secret**. |

## AutoFix

| Problem | What to check |
|---|---|
| No pull request appears | Refusals are reported as `cloudsec.code_autofix_refused` events, once `ops_events` is on. See [When no pull request appears](autofix.md#when-no-pull-request-appears). |
| `write_app_lacks_contents` | Grant **Contents: Read and write** to the App and approve on the installation page. |
| The pull request warns that the lockfile is stale | Run the command in the pull request on its branch before merging. See [Lockfiles](autofix.md#lockfiles). |

## Pushed results and local scans

| Problem | What to check |
|---|---|
| `No such command` for `cloudsec code` | Upgrade the `limacharlie` CLI. |
| The CLI cannot identify the repository | Pass `--repo <owner>/<repository>`. |
| Docker is not found | Install and start Docker, or use `--binary`, or push results from your own scanner with `code ingest`. |
| A pushed repository is not recorded | It must match an enabled code-scanning policy and fit within the repository limits. |
| Fixed findings from a SARIF push never close | Pass `--scanner-succeeded`. Many tools do not record whether the run succeeded. |
| Secret findings from a push do not appear | Secrets are only accepted from the hosted scan. |
| The document is too large | Keep it under 20 MiB, or split it. |
