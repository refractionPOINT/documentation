# AutoFix pull requests

For a vulnerable dependency with a published fixed version, Code Security can
open the GitHub pull request that upgrades it. You review and merge it like any
other pull request.

AutoFix is GitHub-only and supports **npm** (including yarn and pnpm projects),
**pip**, **Go modules** and **Maven**.

## Turn it on

AutoFix needs:

- a GitHub connection whose App has **Contents: Read and write** and **Pull
  requests: Read and write**. With **Create a GitHub App for me**, tick **Allow
  AutoFix to open fix pull requests**. For any other App, add the permissions
  under the App's **Permissions & events** on GitHub, then have an organization
  owner approve the change on the installation page;
- an enabled code-scanning policy that selects the repository.

There is no separate policy switch. Once the permissions are granted, the
**Code security** Overview tab stops showing **Automated fixes** as needing
setup, and `limacharlie cloudsec code capabilities` reports `fix_pull_requests`
as `available`.

## Open a fix

- **Console:** open a dependency finding and choose **Open AutoFix PR**.
- **Fix queue:** the **Priority fix queue** on the Overview tab lists the
  upgrades that close the most findings.
- **CLI:**

    ```bash
    # The upgrades that close the most findings, with a representative finding id.
    limacharlie cloudsec code fixes

    limacharlie cloudsec code autofix fnd_2290bab86c1b4d0374d1e2666f64aeca
    ```

The request is accepted immediately. The pull request appears a few minutes
later, on a branch named `limacharlie/autofix/<ecosystem>-<package>` (for
example `limacharlie/autofix/npm-babel-core` for `@babel/core`). There is at most
one open AutoFix pull request per repository and package.

You can only ask for a fix by finding: the package and target version come from
LimaCharlie's own scan, never from the request.

The finding closes once the pull request is merged and the next scan of the
default branch no longer sees the vulnerable version.

## What gets edited

| Ecosystem | Edited | Lockfile |
|---|---|---|
| **npm** | The version in `package.json`, keeping its range operator (`^`, `~`) | `package-lock.json` or `npm-shrinkwrap.json` is updated too. A `yarn.lock` or `pnpm-lock.yaml` is not, and the pull request says so. |
| **pip** | The pin in `requirements.txt` | None to update. Requirements pinned with `--hash`, compound specifiers such as `>=2.0,<3.0`, and projects locked with Poetry, Pipenv or PDM are refused. |
| **Go** | The `require` line in `go.mod` | `go.sum` is never edited, so every Go pull request says to run `go mod tidy`. |
| **Maven** | The `<version>` in `pom.xml`, or the property it references | None to update. |

## Lockfiles

When a lockfile could not be updated, the pull request carries a clear
stale-lockfile warning and the command to run on the branch before merging:

| Lockfile | Command |
|---|---|
| `package-lock.json` | `npm install --package-lock-only --ignore-scripts` |
| `yarn.lock` | `yarn install --mode update-lockfile` |
| `pnpm-lock.yaml` | `pnpm install --lockfile-only` |
| `go.sum` | `go mod tidy` |

AutoFix never runs a package manager, because that would run code from the very
dependencies under suspicion. To update `package-lock.json`, it makes one
read-only request to the npm registry for the new version's download URL and
integrity hash, and writes those into the lockfile.

To forbid that registry request, set `autofix_registry_access: false` in the
policy. npm pull requests then change `package.json` only and carry the
stale-lockfile warning. If any policy selecting a repository sets it to `false`,
that wins.

Separately, LimaCharlie always confirms the fixed version exists on the public
registry (npm, PyPI, Maven Central or the Go module proxy) before opening a pull
request. Packages published only to a private registry cannot be fixed
automatically.

AutoFix also refuses changes it cannot make safely, and says why: transitive
dependencies, Go upgrades across a major version, complex npm version ranges,
Maven versions inherited from a parent POM, and pip pins other than `==`, `===`,
`~=` or `>=`.

## When no pull request appears

The request is accepted before the work runs, so a refusal is not returned by
the CLI or the console. It is reported as a `cloudsec.code_autofix_refused`
operational event in the organization's event stream, with the reason in its
`error` field. Operational events are off by default: turn them on with
`ops_events: true` in the [`emission` policy](../configuration.md#emission-the-event-feed).

Common reasons:

| Reason | Meaning |
|---|---|
| `write_app_not_configured` | The App is not installed on that repository. |
| `write_app_lacks_contents` | The App lacks **Contents** or **Pull requests: Read and write**, its installation is suspended, or GitHub could not be reached to check. |
| `finding_not_found`, `repo_not_in_inventory`, `repo_out_of_policy_scope` | The finding or its repository could not be found, or no enabled policy selects the repository. |
| `finding_not_autofixable` | The package is flagged malicious (remove it and rotate credentials instead), has no published fixed version, cannot be raised to that version automatically, or its ecosystem is not supported. |
| `autofix_not_applicable` | The manifest could not be edited safely, for example a `--hash`-pinned requirement or a Poetry lock file. |
| `autofix_fix_version_unverified` | The fixed version could not be confirmed on the public registry. |
| `autofix_pr_already_open` | A pull request for that package is already open. |
| `autofix_budget_exhausted` | The daily limit of 20 AutoFix requests was reached. Requests count when they start, even if they later fail. The limit resets at midnight UTC. |
| `autofix_job_failed`, `autofix_pr_failed` | The job or the pull request creation failed. Try again later. |
