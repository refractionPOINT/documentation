# Automatic behavior and incident response

This page describes what Code Security does on its own when something goes
wrong, what it never does on its own, and what you can do during an incident
that involves a remediation.

## What happens automatically

| Situation | What Code Security does |
|---|---|
| The security graph is slow or down during a pull-request check | The check publishes its normal scan verdict, unchanged, with a note that the live context is missing. Impact reads give `graph_unavailable` or `deadline`. |
| A sensor stops reporting | A lapse never turns into `not_observed`. The answer becomes `present` or `unknown`, with a reason. A package already seen loaded or running stays so. |
| Deployment or scan evidence goes stale | The affected stage or coverage line reads `stale` or `coverage_stale`. Verification waits. |
| A fix is merged but not deployed everywhere | The run stays in `monitoring` with `old_digest_running` or `deployment_partial`. It is not `verified`. |
| The fixed image has no completed scan | The run stays in `monitoring` with `fix_digest_unscanned`. |
| A fix run's deadline passes without proof | If the old digest is still running, the run ends `persists`. Otherwise it ends `expired` with `deadline`. The finding is not marked fixed. |
| A repository fix is merged but nothing in scope runs it | The run ends `expired` with `pr_merged_unverifiable`. It is never marked `verified`. |
| The vulnerable digest runs again after verification | Within 30 days of verification, the run becomes `regressed` and the evidence chain says so. |
| A temporary control reaches its expiry | It is removed. Detection rules also carry their own expiry, so they are deleted even if Code Security is unavailable. Isolation expires at most 4 hours after it is applied, and cleanup then releases it. |
| A temporary control cannot be removed on time | After three failed removals, or 15 minutes past expiry, a HIGH `code-response-cleanup-failed` finding opens. It closes once the control is confirmed gone. |
| An executor never reports back | The run retries, then fails with `dispatch_exhausted` or `deadline`. A late or repeated callback has no second effect. |
| The playbook installation or the target changes after approval | The run stops before acting, with `installation_changed` or `target_changed`. |
| Someone else isolated the sensor first | The run does not act (`target_already_isolated`), so there is no isolation of its own to release. |

## What never happens automatically

- Nothing is merged, deployed or rolled back.
- No credential is revoked.
- No run acts without a human approval. There is no pre-approval.
- No target is taken from a request. The server derives it from the finding.
- Runtime and exposure evidence never lower a finding's risk score.

## During an incident

### A remediation is doing something you did not expect

1. Find the run: `limacharlie cloudsec remediation list --finding-id <finding>`,
   or the finding's evidence chain in the console.
2. Cancel it if it has not finished:
   `limacharlie cloudsec remediation cancel <run_id>`, then repeat with the
   `--confirm` token it prints. Cancel works even when remediation is disabled
   for your organization.
3. A temporary detection it installed expires on its own. To remove it now,
   delete its D&R rule, named `cloudsec-rem-*`.
4. An isolation it applied expires after at most 4 hours and cleanup releases
   it. If release fails, cleanup keeps retrying and a HIGH finding opens. To
   release it earlier, rejoin the sensor to the network as you would any
   isolated sensor.
5. A pull request it opened stays open for you to close. The run keeps
   monitoring until its deadline and then ends `expired`.

### Stop all Code Security actions in your organization

- Set every playbook in your `response` policy to `mode: dry_run`, or delete
  the policy. Notify, ticket, detection and isolation runs then record their
  plan and act on nothing. A run approved under the old installation stops
  with `installation_changed` before it acts.
- Remove `cloudsec.respond` from the users and API keys that hold it. Nobody can
  then request or approve a run, or press **Open AutoFix PR**.
- Remove the GitHub App's write permissions to stop fix pull requests at the
  source.

Runs that already acted keep their cleanup: temporary controls are still
removed at expiry.

### A HIGH `code-response-cleanup-failed` finding opened

The finding names the control. Check whether its effect is still in place: the
`cloudsec-rem-*` detection rule, or the sensor's isolation state. Remove it by
hand if it is. The finding closes on its own once the control is confirmed gone.
If it does not, contact LimaCharlie support with the finding ID.

### A fix shows `regressed`

The vulnerable digest is running again. The run's verification step lists which
workloads run which digests. Find the deployment that reintroduced it,
typically a rollback or a pipeline that still builds from the old commit, and
redeploy the fixed image.

### Results look wrong

Check the reason codes first ([Unknown, partial and refusal
reasons](reasons.md)). A stale or partial answer is expected while collection
catches up. If a finding is attributed to the wrong resource, or a stage is
`proven` when you believe it should not be, contact LimaCharlie support with
the finding ID and the evidence chain.

## Getting help

Contact LimaCharlie support with the organization ID, the finding or run ID,
and the reason codes shown. Support can check the state of a run, a purge, or a
feature's rollout in your region.
