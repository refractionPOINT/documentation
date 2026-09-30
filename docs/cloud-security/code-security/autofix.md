# AutoFix pull requests

--8<-- "includes/code-security-cli-version.md"

For a vulnerable dependency with a published fixed version, Code Security can
open the GitHub pull request that upgrades it. You review and merge it like any
other pull request.

The walkthrough below uses GitHub. AutoFix supports **npm** (including yarn and
pnpm projects), **pip**, **Go modules** and **Maven**. GitLab.com and Bitbucket
Cloud workflow support is deployment-dependent: confirm workflow availability
with LimaCharlie, configure the provider's separate write token, then use
`code capabilities` to verify the connection can open fix pull requests. A
connection missing from that workflow response may still support
ordinary scheduled repository scanning.

## Turn it on

AutoFix needs:

- a GitHub connection whose App has **Contents: Read and write** and **Pull
  requests: Read and write**. With **Create a GitHub App for me**, tick **Allow
  AutoFix to open fix pull requests**. For any other App, add the permissions
  under the App's **Permissions & events** on GitHub, then have an organization
  owner approve the change on the installation page;
- an enabled code-scanning policy that selects the repository;
- the `cloudsec.respond` permission for whoever asks for the fix. `cloudsec.set`
  does not include it. See [Permissions](containment-setup.md#permissions).

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

Each request creates a remediation run of type `open_fix_pr`. A person or API key
with `cloudsec.respond` can request it. The same identity is recorded as both
requester and approver, and the pull request comes back to the run through an
authenticated callback. Asking again before the pull
request is open returns the same run. See
[Remediation runs](containment-setup.md#remediation-runs).

The pull request appears a few minutes later, on a branch named `limacharlie/autofix/<ecosystem>-<package>` (for
example `limacharlie/autofix/npm-babel-core` for `@babel/core`). There is at most
one open AutoFix pull request per repository and package.

You can only ask for a fix by finding: the package and target version come from
LimaCharlie's own scan, never from the request.

The finding closes once the pull request is merged and the next scan of the
default branch no longer sees the vulnerable version. A merged pull request
alone is not a fix. The run becomes `verified` only when every in-scope
deployment also runs the fixed build. When no deployment is in scope, it ends
`expired` with `pr_merged_unverifiable`.

## What gets edited

| Ecosystem | Edited | Lockfile |
|---|---|---|
| **npm** | The version in `package.json`, keeping its range operator (`^`, `~`) | The lockfile beside the manifest is updated too: `package-lock.json`, `npm-shrinkwrap.json`, `yarn.lock` or `pnpm-lock.yaml`. A yarn or pnpm lockfile that cannot be rewritten safely is refused before any job runs (`autofix_not_applicable`, with the reason). |
| **pip** | The pin in `requirements.txt` | None to update. Requirements pinned with `--hash`, compound specifiers such as `>=2.0,<3.0`, and projects locked with Poetry, Pipenv or PDM are refused. |
| **Go** | The `require` line in `go.mod` | `go.sum` is written from the Go checksum database. A Go fix whose `go.sum` cannot be completed this way, or a repository with no `go.sum`, is refused before any job runs (`autofix_not_applicable`) instead of opening a pull request that does not build. |
| **Maven** | The `<version>` in `pom.xml`, or the property it references | None to update. |

## Lockfiles

When a `package-lock.json` could not be regenerated (for example with
`autofix_registry_access: false`), the pull request carries a clear
stale-lockfile warning and the command to run on the branch before merging:

| Lockfile | Command |
|---|---|
| `package-lock.json` | `npm install --package-lock-only --ignore-scripts` |
| `npm-shrinkwrap.json` | `npm install --package-lock-only --ignore-scripts` |

This warning applies to npm's JSON lockfiles. A yarn, pnpm or Go lockfile the
service cannot complete safely is refused before the job runs, rather than
opened with a stale-lockfile warning.

AutoFix never runs a package manager, because that would run code from the very
dependencies under suspicion. To update `package-lock.json`, it makes one
read-only request to the npm registry for the new version's download URL and
integrity hash, and writes those into the lockfile.

To forbid that registry request, set `autofix_registry_access: false` in the
policy. Projects using npm JSON lockfiles then change `package.json` only and
carry the stale-lockfile warning. Other lockfile formats can instead be refused
if safe completion needs registry metadata. If any policy selecting a repository sets it to `false`,
that wins.

Separately, LimaCharlie always confirms the fixed version exists on the public
registry (npm, PyPI, Maven Central or the Go module proxy) before opening a pull
request. Packages published only to a private registry cannot be fixed
automatically.

AutoFix also refuses changes it cannot make safely, and says why: transitive
dependencies, Go upgrades that require a module-path change for major versions
above v1 (v0-to-v1 is allowed), complex npm version ranges,
Maven versions inherited from a parent POM, and pip pins other than `==`, `===`,
`~=` or `>=`.

## When no pull request appears

The request is accepted before the work runs, so most refusals are not
returned by the CLI or the console. The run records the reason in its
`failure_reason` (`limacharlie cloudsec remediation get <run_id>`). It is also
reported as a `cloudsec.code_autofix_refused` operational event in the
organization's event stream, with a sentence in `error`, a reason code in
`reason`, and the run in `remediation_id`. The table below lists the codes that
appear in `error`. The `reason` field and the run's `failure_reason` use the
[fix pull request codes](reasons.md#fix-pull-requests-and-autofix). Operational events are off by default: turn them on with
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

Some requests are refused immediately, with an HTTP error:

| Error | Meaning |
|---|---|
| `403 missing_permission` | You lack `cloudsec.respond`. |
| `422 action_unavailable` | The finding is not a dependency finding AutoFix can raise, or fix pull requests are not enabled for your organization. |
| `429 capacity` | Your organization already has 100 active remediation runs, or this finding has 10. |
| `503 disabled` | Remediation is not enabled for your organization yet. |

See [Unknown, partial and refusal reasons](reasons.md#remediation-runs) for
every code.

## AI-proposed fixes

!!! warning "Not currently available"
    AI-proposed fix pull requests are a separate capability from dependency
    AutoFix. They are not currently enabled as an available service. The
    configuration below describes the opt-in contract for organizations that
    LimaCharlie enables in a future preview; saving it does not grant access.

The `ai_fix_pr` action proposes a change to the single file named by a hosted
static-analysis or infrastructure-as-code finding. It uses **your Anthropic
API key**, sends that file and the finding context to Anthropic, and charges
usage to your Anthropic account. Review [AI data handling](data-handling.md#ai)
before opting in. Dependency upgrades continue to use deterministic AutoFix.

When this capability is available, it needs the GitHub write grants above,
`cloudsec.respond` for requesting and approving each run, and an `ai_fix` block
on an enabled code-scanning policy that selects the repository:

```yaml
# Add this block INSIDE the code_scanning object in your existing policy.
ai_fix:
  enabled: true
  model_secret: hive://secret/code-fix-anthropic-key
  job_cap_usd: 2
  jobs_per_day: 10
  checks: [syntax]
```

Create the referenced enabled secret first, with your Anthropic API key as the
secret value. The optional `model` selects a supported model; omit it to use the
service default and confirm the available models with LimaCharlie during setup.

| Field | Contract |
|---|---|
| `enabled` | Required inside the block. `false` denies AI fixes for every repository the policy selects. Absent `ai_fix` leaves AI fixes off unless another selecting policy enables them. |
| `model_secret` | Required when enabled; a `hive://secret/<name>` reference, never an inline API key. |
| `job_cap_usd` | Per-model-call budget, USD 0.10–10; default 2. A job that cannot fit its input and output budget makes no model call. |
| `jobs_per_day` | Per-organization daily job cap, 1–50; default 10. Failed jobs count when they start. |
| `checks` | `syntax` (default) or `none`. The service never accepts a command to execute. `none` skips only the optional syntax check; rescanning and the impact gate remain mandatory. |

Across selecting policies, an explicit denial wins, caps take the lowest value,
and required checks combine. Conflicting model or secret choices refuse the
job. The default syntax check supports Go, JSON, YAML, Terraform and HCL files;
unsupported file types are refused rather than treated as having passed.

The model cannot choose a repository, target file, branch, commit or command.
A proposed patch must remove the target finding in a sandboxed rescan, pass the
configured checks, and pass the live-impact gate before a pull request opens.
Missing or partial evidence refuses the job. Each run still needs explicit
approval, and its pull request needs your normal review and merge process.

To disable this opt-in, set `ai_fix.enabled: false` in a policy selecting the
repository. Cancel any active run separately; changing a policy does not close
pull requests already opened.
