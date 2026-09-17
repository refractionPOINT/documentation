# Scan policy

A `code_scanning` policy decides which repositories are scanned, which engines
run, how often, and what happens on pull requests. With no enabled policy,
nothing is scanned.

Edit it in the console under **Cloud Security → Policies → Code scanning**, or
store it as a record in the `cloudsec_policy` hive.

## Example

```yaml
policy_type: code_scanning
enabled: true
repos:
  include: ["acme/api-*", "acme/payments"]
  exclude: ["acme/api-archive"]
scanners:
  sca: true
  secrets: true
  secrets_history: true
  iac: true
  images: true
  licenses: true
  # sast runs unless set to false
schedule: daily
severity_floor: ""
image_sources: ["dockerfile", "workloads"]
pr_checks: true
pr_comments: false
gating:
  fail_on: HIGH
```

```bash
limacharlie hive set --hive-name cloudsec_policy --key code-scanning \
    --input-file code-policy.yaml --enabled
```

## Fields

| Field | Meaning |
|---|---|
| `enabled` | **Required.** `false` keeps the policy but scans nothing. |
| `repos.include` | Repositories to scan, as globs matched case-insensitively against `owner/name` and the bare name. **Empty means every repository the connections can see.** |
| `repos.exclude` | Repositories to skip. Always wins over `include`. |
| `scanners` | Which engines run. See [Engines](#engines). |
| `schedule` | `daily` (the default), `weekly`, or `manual` (only when you ask for a rescan). |
| `severity_floor` | Drop findings below this severity. See [Severity floor](#severity-floor). |
| `sast_ruleset` | The static-analysis rule pack. Leave empty for the default pack. |
| `image_sources` | Where the image engine finds images. See [Container images](#container-images). |
| `pr_checks`, `pr_comments`, `gating.fail_on` | Pull-request checks on GitHub. See [Pull-request checks](pull-requests.md#turn-on-pull-request-checks). |
| `autofix_registry_access` | Whether AutoFix may look up package registry metadata to update lockfiles. Default `true`. See [AutoFix](autofix.md#lockfiles). |

Globs support `*`, `?`, `[…]` and `{a,b}`. A leading `!` negates within a list.
Write negations in `include`. A `!` pattern in `exclude` means "exclude
everything that does not match", which cancels your include list.

## Engines

| Key | Engine | Default |
|---|---|---|
| `sca` | Dependencies and malicious packages | off |
| `secrets` | Secrets in the current files | off |
| `secrets_history` | Secrets in the full git history | off |
| `iac` | Infrastructure as code | off |
| `sast` | Static analysis | **on** |
| `images` | Container images | off |
| `licenses` | Dependency licenses | off |

Every engine except `sast` runs only when set to `true`. Static analysis runs
unless a policy sets `sast: false`. The console's policy form starts with
dependencies, secrets, infrastructure as code, static analysis and licenses
turned on.

An enabled policy needs at least one engine running.

`secrets_history` is a separate switch because it needs the full history
instead of the latest commit. On a large repository that makes the scan much
slower. Secrets found only in history need rotating: deleting the file does not
un-leak the credential.

End-of-life runtime findings come with the dependency engine (`sca`) and the
image engine (`images`).

## Severity floor

`severity_floor` drops findings below a severity: `MEDIUM`, `HIGH` or `CRITICAL`.
`LOW`, `INFO` and an empty value all mean no floor.

The floor **drops** findings rather than hiding them. A finding under the floor
is never recorded. Raising the floor closes the findings that fall under it, with
`closed_reason: below_severity_floor`. Lowering it again brings them back as new
occurrences: their age restarts and their triage state is gone.

If you only want a narrower view, leave the floor empty and filter the worklist
by severity.

## Container images

`image_sources` is a list:

| Value | Scans |
|---|---|
| `dockerfile` | Images your repositories reference, such as a Dockerfile's base image. The default. |
| `workloads` | Images your connected cloud accounts report running, when pinned by digest. |
| `registries` | Accepted, but not built yet. It currently adds nothing. |

Only digest-pinned image references are scanned. A reference by tag alone is
counted and skipped, because a tag can point at a different image tomorrow.

Image sources also decide what the [code-to-runtime queries](results.md#how-code-connects-to-your-cloud)
can see.

## Several policies

An organization can have several `code_scanning` policies. For example, scan
sensitive repositories daily with every engine, and everything else weekly with
fewer engines. When more than one enabled policy selects a repository:

- the engines are combined, so any policy can add one;
- the lowest severity floor applies;
- the most frequent schedule applies;
- pull-request checks and comments are on if any policy turns them on, and the
  strictest `gating.fail_on` applies;
- the image sources are combined;
- `autofix_registry_access: false` in **any** policy wins, so a broad policy
  cannot restore network access a narrower policy removed.

## Rescan now

To scan one repository without waiting for its schedule, choose **Rescan now** on
the **Repositories** tab, or:

```bash
limacharlie cloudsec code rescan acme/payments
```

The rescan is accepted immediately and runs within minutes. Requests for the
same repository in a short window are combined into one scan. Check the result
on the repository's row, not in the rescan response.
