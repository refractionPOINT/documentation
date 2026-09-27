# Unknown, partial and refusal reasons

Code Security never turns missing evidence into a reassuring answer. When it
cannot prove something, it says `unknown` or `partial` and returns a closed
reason code. Evidence-chain stages and coverage lines also give an `action` code
that names the next step. This page lists the codes for the generally available
workflows and what to do about each.

For scan-lane problems (repositories not scanned, webhooks, the GitHub App), see
[Troubleshooting](troubleshooting.md). For what the guarantees behind these codes
are, see [What Code Security guarantees](guarantees.md).

## Reading a reason

Evidence-chain stages and coverage lines carry these fields. Runtime checks
return `status`, `reason`, `level`, `observed_at` and `stale_at`. Remediation
runs carry `state`, `failure`, `failure_reason` and `playbook_reason` instead.
The action for those codes is listed in each table below.

| Field | Meaning |
|---|---|
| `status` | `proven`, `partial`, `unknown` or `not_applicable`. `proven` says the stage is evidenced, not that the news is good. Read `outcome` for that. |
| `level` | How strong the evidence is: `verified` (cryptographically checked), `asserted` (a claim from you or a tool), `observed` (LimaCharlie saw it), `derived` (a join of the above), or `unknown`. |
| `reason_domain`, `reason` | The feature the reason belongs to, and the closed reason code. |
| `reason_recognised` | `false` when the code is not in the server's catalog. The code is shown as is, with the action `review_reason`. Report it to LimaCharlie support. |
| `action` | The suggested next step, from the table below. |
| `observed_at`, `stale_at` | When the evidence was observed, and when it stops counting. |

## Actions

| `action` | What to do |
|---|---|
| `connect_repository` | Connect the repository in Code Security so its code can be scanned and linked. |
| `rescan_repository` | Rescan the repository so its latest commit is recorded. |
| `push_iac_map` | Push an infrastructure-as-code map so declarations can be matched to live resources. See [Terraform maps](containment-setup.md#terraform-maps). |
| `narrow_iac_scope` | Narrow the infrastructure-as-code scope so each declaration matches one live resource. |
| `push_build_provenance` | Push build provenance so each image digest names the commit it was built from. See [Build provenance](containment-setup.md#build-provenance). |
| `resolve_provenance_conflict` | Two builds claim different sources for this artifact. Check your build records and push the correct one. |
| `deploy_by_digest` | Deploy by immutable image digest instead of a tag. |
| `check_provider_access` | Check that the cloud connection can read this resource's deployments. |
| `connect_cloud_provider` | Connect the cloud account that holds this resource. |
| `wait_for_collection` | Wait for the next collection pass, then reload. |
| `open_impact_view` | Open the live impact view for this commit to see the full answer. |
| `retry_later` | A backend read failed or ran out of time. Try again in a few minutes. |
| `run_runtime_check` | Run a runtime check. |
| `deploy_sensor` | Deploy a LimaCharlie sensor on this resource. |
| `check_sensor_health` | The sensor's telemetry was interrupted or incomplete. Check the sensor. |
| `request_remediation` | Request a remediation run. |
| `approve_remediation` | A run waits for someone with `cloudsec.respond` to approve it. |
| `wait_for_remediation` | A run is in progress. Wait for it to report back. |
| `wait_for_rollout` | Wait for the fix to reach every in-scope deployment. |
| `investigate_regression` | The old artifact came back after the fix was verified. Find the deployment that reintroduced it. |
| `configure_write_access` | Configure write access for the repository. |
| `review_finding` | The evidence does not fit together. A person needs to decide. |
| `review_manually` | LimaCharlie has no evidence for this. Check the cloud provider or the repository directly. |
| `review_reason` | The reason is not one this version knows. Read the raw code. |
| `enable_feature` | The capability is not enabled for your organization. Ask your administrator or LimaCharlie support. |
| `contact_support` | Contact LimaCharlie support with the finding ID. |

## Evidence chain

`GET /findings/{finding_id}/evidence-chain` returns eight stages: `declared`,
`committed`, `built`, `running`, `exposed`, `observed`, `responded`, `verified`.
If `chain` is null, the top-level `reason` is `feature_disabled` or
`finding_not_found`.

| `reason` | Action | Meaning |
|---|---|---|
| `iac_origin_partial` | `push_iac_map` | A declaration inventory was capped or incomplete, so these may not be all the declarations. |
| `no_iac_origin` | `push_iac_map` | No declaration is attributed. That does not prove none exists. |
| `iac_origin_unverified` | `rescan_repository` | The listed declarations carry no fresh, complete evidence. |
| `commit_unknown` | `rescan_repository` | The scan recorded no exact commit. |
| `not_a_workload` | none | The resource is not a workload, so build and deployment stages do not apply. |
| `runtime_not_applicable` | none | The finding names no package, so runtime evidence does not apply. |
| `workload_not_resolved` | `check_provider_access` | No deployment was resolved for this workload. |
| `deployment_not_observed` | `review_manually` | No container deployment was observed. Only Cloud Run and GKE digests are observed today. |
| `deployment_trace_unavailable` | `review_manually` | Which deployments run code from this repository is not traced per finding in this version. |
| `workloads_truncated` | `review_finding` | More workloads run this than one chain lists. |
| `observation_time_unknown` | `wait_for_collection` | The fact has no observation time, so its freshness cannot be stated. |
| `chain_read_failed` | `retry_later` | A read the chain depends on failed. |
| `evidence_contradictory` | `review_finding` | The evidence contradicts itself, so neither side is shown as the answer. |
| `lineage_candidate` | `push_build_provenance` | A source repository is linked, but the exact build commit is not proven. |
| `lineage_ambiguous` | `resolve_provenance_conflict` | Several sources match. |
| `lineage_stale` | `retry_later` | The image lineage expired. It is refreshed on the next image scan. |
| `exposure_not_established` | `review_manually` | Nothing establishes exposure. That does not prove the resource is unexposed. |
| `finding_not_open` | `review_finding` | The finding is not open, so its exposure facts are not current. |
| `runtime_not_checked` | `run_runtime_check` | No runtime check was part of this read. Add `runtime=true` or run a check. |
| `no_remediation_requested` | `request_remediation` | No remediation run exists. |
| `awaiting_approval` | `approve_remediation` | A run waits for approval. |
| `remediation_in_progress` | `wait_for_remediation` | A run is in progress. |
| `remediation_rejected`, `remediation_cancelled`, `remediation_expired` | `request_remediation` | The latest run was rejected, cancelled, or expired without a conclusive result. |
| `remediation_failed` | `contact_support` | The latest run failed. |
| `verification_pending` | `wait_for_rollout` | The rollout is being monitored. No verdict yet. |
| `remediation_persists` | `wait_for_rollout` | The old artifact is still running after the monitoring window. |
| `remediation_regressed` | `investigate_regression` | The old artifact came back after verification. |
| `remediation_state_unrecognised` | `review_reason` | The run's state is not one this server version knows. |

Stages that are proven carry a positive reason instead: `code_location`,
`iac_origin`, `exposure_established`, `response_executed`,
`remediation_verified`.

### Code-to-cloud attribution

A finding's `iac_attribution` is `attributed`, `ambiguous` or `none`. When it is
`none`, the reason says why:

| `reason` | Action | Meaning |
|---|---|---|
| `unresolved_name` | `push_iac_map` | The declaration's name could not be resolved, so no live resource was matched. A map with the resolved identity fixes this. |
| `unsupported_resource_type` | `review_manually` | This resource type is not supported for attribution. |
| `not_collected` | `connect_cloud_provider` | This resource type is not collected by name, so no live match could be checked. |
| `no_match` | `review_manually` | No matching live resource exists. |

### Build provenance

| `reason` | Action | Meaning |
|---|---|---|
| `missing` | `push_build_provenance` | No build provenance is recorded for this artifact. |
| `conflict` | `resolve_provenance_conflict` | Build provenance records disagree about the source. Neither is used. |
| `incomplete` | `push_build_provenance` | The build provenance is incomplete. |
| `declared` | `push_build_provenance` | The source is declared, for example by an image label, but not proven by build provenance. |

## Deployment coverage and image lineage

`GET /code/coverage` returns one line per metric, each with a `numerator`, a
`denominator` and a `breakdown`. A percentage is shown only when the line is
complete and fresh. If `coverage` is null, the reason is `feature_disabled`.

| Line `reason` | Action | Meaning |
|---|---|---|
| `coverage_incomplete` | `check_provider_access` | A collection pass did not read its whole scope, so the denominator is a lower bound. |
| `coverage_stale` | `wait_for_collection` | Part of the count is past its evidence window. |
| `coverage_truncated` | `review_manually` | More rows existed than one report reads. |
| `no_denominator` | `connect_cloud_provider` | There is nothing to count yet. |
| `coverage_read_failed` | `retry_later` | The read for this line failed. |
| `metric_not_materialized` | `review_manually` | This metric is not counted in this version. |

### Why a workload has no digest

These codes appear in the workload coverage breakdown and on the `running`
stage of the evidence chain.

| Code | Action | Meaning |
|---|---|---|
| `tag_only` | `deploy_by_digest` | The deployment names an image tag, not an immutable digest. |
| `revision_unavailable` | `check_provider_access` | The deployment's current revision could not be read. |
| `provider_unreachable` | `check_provider_access` | The cloud provider could not be reached. |
| `not_running` | `wait_for_collection` | Nothing runs for this deployment right now (scaled to zero, or no pods). Reported beside the percentage, not inside it. |
| `malformed_digest` | `contact_support` | The provider reported a malformed digest. |
| `stale` | `wait_for_collection` | The deployment evidence is past its window. |
| `partial` | `check_provider_access` | Only part of the deployment could be resolved. |
| `missing` | `check_provider_access` | No deployment evidence was found. |
| `unattributed` | `push_build_provenance` | The running artifact has no recorded source. |
| `build_unstated` | `push_build_provenance` | The build that produced the artifact is not recorded. |
| `deployment_unknown` | `check_provider_access` | What is deployed could not be determined. |

`provider_digest`, `resolved` and `rolling` (a rollout in progress, more than
one artifact running) are resolved states.

### Image lineage breakdown

The `digests_with_source` line counts your own running image digests that have a
source link. Its breakdown keys:

| Key | Counted as |
|---|---|
| `inferred` | Covered. Matched from the image's build steps and files. |
| `tool_emitted_asserted`, `signed_push_asserted` | Covered. A label or pushed statement without a trusted signature. |
| `tool_emitted_verified`, `signed_push_verified` | Covered. A trusted signature checked for that digest. |
| `ambiguous` | Not covered. Several sources match. |
| `unknown` | Not covered. No usable evidence, or the evidence is stale. |
| `third_party` | Outside the percentage. A public image that matches none of your registries or repositories. |
| `ownership_unknown` | Withholds the percentage until your registry or source connections show whose images these are. |

On one image (`GET /code/images/{digest}`), `lineage.reason` explains the
decision. The common ones:

| `reason` | Meaning |
|---|---|
| `insufficient_evidence`, `lineage_evidence_unavailable` | No candidate matched well enough. |
| `partial_image_evidence` | The image's own metadata is incomplete. |
| `unique_fingerprint_match` | One repository matches (inferred). |
| `competing_candidates` | More than one repository matches (ambiguous). |
| `oci_source_revision_label` | Asserted from the image's OCI source and revision labels. |
| `source_label_unresolved` | The image has no usable source or revision label. |
| `source_label_fingerprint_conflict` | The label and the build-step match name different repositories (ambiguous). |
| `google_cloud_build_signature`, `github_actions_signature` | Verified from a Google Cloud Build or GitHub Actions signature. |
| `native_lineage_conflict`, `signed_claim_conflict`, `producer_claim_conflict`, `lineage_source_conflict` | Two sources of lineage disagree. Neither is used. |
| `signed_push_verified`, `signed_push_asserted` | From a statement you pushed, with or without a trusted signature. |
| `signed_claim_stale`, `signed_claim_incomplete` | A signed claim is out of date or incomplete. |
| `base_candidate_cap`, `build_candidate_cap`, `producer_row_cap`, `signed_claim_bounds` | Too many candidates to decide within limits. |
| `lineage_read_failed` | The read failed. Try again. |

## Live impact and pull-request consequence

`GET /code/impact` and the pull-request consequence section return a
`summary.status` of `complete`, `partial` or `unavailable`. A partial answer
never says "no impact". Each impact lists the reasons it is partial:

| `reason` | Action | Meaning |
|---|---|---|
| `graph_unavailable` | `retry_later` | The security graph did not answer. The pull-request verdict is unaffected. |
| `deadline` | `retry_later` | The impact read ran past its 2-second budget. The pull-request verdict is unaffected. |
| `declarations_truncated` | `open_impact_view` | More than 100 declarations changed, so not all were considered. |
| `graph_truncated` | `open_impact_view` | The graph answered only in part, within its 500-row limit. |
| `mapping_stale` | `push_iac_map` | The code-to-cloud map describes a different revision. |
| `mapping_ambiguous` | `narrow_iac_scope` | A declaration matches more than one live resource. |
| `resource_not_collected` | `connect_cloud_provider` | A matched resource is not collected. |
| `deployment_unknown` | `check_provider_access` | What runs on a workload could not be determined. |
| `runtime_unavailable` | `run_runtime_check` | Runtime information was not available. |
| `disclosure_redacted` | `open_impact_view` | Detail was withheld by the pull-request disclosure setting. |
| `facet_not_collected` | `review_manually` | This fact is not recorded for this kind of resource. |

If `impact` is null, the reason is `feature_disabled` or `subject_not_found`
(the repository or commit was not found).

`exposure`, `privilege` and `sensitivity` are `established`,
`not_established` or `unknown`. `not_established` means nothing positive was
found. It never means "not exposed". An impact with status `no_live_match` names
a resource that does not exist yet, typically one the change will create.

## Runtime checks

`POST /findings/{finding_id}/runtime-check` returns a `status`:

| `status` | Meaning |
|---|---|
| `executing` | The package is the running executable. |
| `loaded` | The package is loaded into a running process. |
| `not_observed` | A complete telemetry window never saw the package loaded. This is not "absent" and not "not exploitable". |
| `present` | A sensor is on the resource, but no package-level claim is possible. |
| `unknown` | No usable runtime evidence. |

When the check could not run at all, `accepted` is `false`:

| `reason` | Action | Meaning |
|---|---|---|
| `feature_disabled` | `enable_feature` | Runtime evidence is not enabled for your organization. |
| `no_resource` | `review_finding` | The finding names no resource a sensor could run on. |
| `no_packages` | `review_finding` | The finding names no package to look for. |
| `cache_unavailable` | `retry_later` | The runtime evidence store did not answer. |
| `no_sensors` | `deploy_sensor` | No LimaCharlie sensor runs on this resource. |
| `sensors_partial` | `review_manually` | Not every sensor on the resource reported. |

Reasons on a verdict:

| `reason` | Action | Meaning |
|---|---|---|
| `no_evidence` | `wait_for_collection` | No runtime evidence has been recorded yet. |
| `expired` | `run_runtime_check` | The evidence is past its 30-minute window. |
| `not_relevant` | `run_runtime_check` | The package was not watched when the evidence was recorded. |
| `window_short` | `wait_for_collection` | The telemetry window is too short to support a claim. |
| `window_interrupted` | `check_sensor_health` | The telemetry window was interrupted. |
| `telemetry_dropped` | `check_sensor_health` | The sensor dropped telemetry during the window. |
| `telemetry_absent` | `check_sensor_health` | The sensor sent no process or module telemetry. |
| `stale_confirmation` | `check_sensor_health` | The sensor's confirmation is out of date. |
| `write_shed` | `retry_later` | Some evidence was dropped under load. |
| `unattributable` | `review_manually` | The activity cannot be attributed to this package. |
| `attribution_incomplete` | `review_manually` | The package's file paths could not all be identified. |
| `relevance_truncated` | `review_manually` | Too many packages were watched to cover them all. |
| `unversioned` | `review_manually` | The package version is not known. |
| `inventory_conflict` | `review_finding` | The sensor's inventory disagrees with the finding. |

`observed_executing`, `observed_loaded` and `complete_window` are the positive
reasons.

## Remediation runs

### Errors from the remediation routes

The `error` field on `/findings/{id}/remediations`, `/remediations/...` and
`/code/autofix`:

| HTTP | `error` | Meaning and fix |
|---|---|---|
| 400 | `invalid_request` | A malformed request: bad ID, a body over 4 KiB, an unknown field, or a bad idempotency key or generation. |
| 403 | `missing_permission` | You lack `cloudsec.respond`. `cloudsec.set` does not include it. See [Permissions](containment-setup.md#permissions). |
| 404 | `not_found`, `finding_not_found` | No such run or finding in this organization. |
| 409 | `idempotency_mismatch` | The same idempotency key was used for a different request. |
| 409 | `generation_conflict` | The run changed since you read it. Reload and decide again. |
| 409 | `illegal_transition` | That decision is not possible from the run's current state. |
| 409 | `target_changed` | The target changed after you reviewed it. Reload and review again. |
| 410 | `approval_expired` | The approval window closed. Request a new run. |
| 422 | `action_unavailable` | The action is not enabled, the playbook is not installed, or the finding is not one this action can fix. |
| 429 | `capacity` | Your organization has 100 active runs, or the finding has 10. Wait for runs to finish. |
| 503 | `disabled` | Remediation is not enabled for your organization. `cancel` still works. |
| 502, 503 | `unavailable` | A backend failure. Try again. |

### Why a run failed

A run in state `failed` or `expired` carries `failure`:

| `failure` | Action | Meaning |
|---|---|---|
| `action_unavailable` | `enable_feature` | The action is not available. |
| `policy_refused` | `review_finding` | The response policy refused the run. |
| `executor_error`, `callback_failed` | `contact_support` | The executor reported an error. See `playbook_reason` or `failure_reason`. |
| `dispatch_exhausted` | `retry_later` | The executor could not be reached. |
| `deadline` | `request_remediation` | The run's deadline passed. |
| `window_ended` | `request_remediation` | The run's window ended. The finding is not verified as fixed. |
| `pr_closed` | `request_remediation` | The fix pull request was closed without merging. |
| `pr_merged_unverifiable` | `review_finding` | The pull request merged, but the fix could not be verified. |
| `invalid_run` | `contact_support` | The run was invalid. |

### Fix pull requests and AutoFix

`failure_reason` on an `open_fix_pr` run (AutoFix button presses included):

| `failure_reason` | Action | Meaning |
|---|---|---|
| `repository_not_connected` | `connect_repository` | The repository is not connected, or no enabled policy selects it. |
| `repository_finding_not_found` | `rescan_repository` | The matching finding is not in the repository. |
| `repository_finding_ambiguous` | `review_finding` | More than one repository finding matches. |
| `provenance_unknown` | `push_build_provenance` | The image's source commit is not known, so no fix pull request can be opened. |
| `write_app_not_configured` | `configure_write_access` | No write access is configured for the repository. |
| `write_app_lacks_contents` | `configure_write_access` | Write access lacks permission to change contents. |
| `finding_not_autofixable`, `autofix_not_applicable` | `review_manually` | No automatic fix applies. See [AutoFix](autofix.md#when-no-pull-request-appears). |
| `autofix_pr_already_open` | `review_manually` | An AutoFix pull request for this package is already open. |
| `autofix_budget_exhausted` | `retry_later` | The daily AutoFix limit of 20 per connection is used up. |
| `autofix_budget_unavailable`, `executor_unavailable` | `retry_later` | The service could not be reached. |
| `autofix_job_failed` | `contact_support` | The fix job failed. |
| `autofix_pr_failed` | `configure_write_access` | The pull request could not be opened. |

### Playbook actions

`playbook_reason` on a notify, ticket, temporary-detection or isolation run.
The catalog also holds `consent_expired` and `claim_stale`, which apply only to
validation templates that are not generally available.

| `playbook_reason` | Action | Meaning |
|---|---|---|
| `installation_missing` | `enable_feature` | The response playbook is no longer installed. |
| `installation_changed` | `request_remediation` | The installation changed after the run was approved. |
| `target_changed` | `review_finding` | The finding no longer points at the approved target. |
| `approval_stale` | `request_remediation` | The approval was too old when the playbook was about to act. |
| `target_already_isolated` | `review_manually` | The sensor was already isolated by someone else. LimaCharlie left it alone. |
| `effector_unavailable`, `executor_unavailable` | `contact_support` | A service the playbook needed refused or failed. |
| `effect_unconfirmed` | `review_manually` | The change was applied, but reading it back did not confirm it. |
| `control_ended` | `request_remediation` | The temporary control had already ended, or too little of its window was left. |

### Verification

While a run is `monitoring`, each observation step lists why it is not yet
`verified`:

| `reason` | Action | Meaning |
|---|---|---|
| `old_digest_running` | `wait_for_rollout` | A deployment in scope still runs the old artifact. |
| `deployment_partial` | `wait_for_rollout` | The rollout has reached only part of the scope. |
| `deployment_missing` | `check_provider_access` | A workload in scope has no deployment evidence. |
| `deployment_stale` | `wait_for_collection` | Deployment evidence is past its window. |
| `deployment_scope_empty` | `review_finding` | No deployments are in scope. |
| `scope_truncated` | `review_finding` | The scope is too large to verify. |
| `unexpected_digest` | `review_finding` | A workload runs an artifact that is neither the old nor the fixed one. |
| `finding_open` | `wait_for_collection` | Detection still reports the finding. |
| `finding_operator_closed` | `review_finding` | Someone closed the finding by hand. That does not count as a fix. |
| `finding_unknown` | `wait_for_collection` | The finding's state could not be read. |
| `source_finding_open` | `rescan_repository` | The finding is still open in the source repository. |
| `fix_digest_unproven` | `push_build_provenance` | No build record proves which image contains the fix. |
| `fix_builds_truncated` | `review_manually` | Too many builds to check which contain the fix. |
| `fix_digest_unscanned` | `wait_for_collection` | No completed scan of the fixed image yet. An image without a scan is never treated as clean. |
| `fix_digest_still_vulnerable` | `review_finding` | The image built from the fix is still vulnerable. |
| `fix_scan_source_unavailable` | `review_manually` | None of the scanners that found this vulnerability reports completed scans of the fixed image. Check it by hand. |
| `expectation_unproven` | `review_manually` | What the fix should look like in production cannot be checked automatically. |

## Pushing maps and provenance

`POST /code/iac-map`:

| HTTP | `error` | Meaning and fix |
|---|---|---|
| 400 | `iac_map_raw_terraform` | You sent a raw state or plan. Run the extractor it names and push its output. See [Terraform maps](containment-setup.md#terraform-maps). |
| 400 | `iac_map_invalid` | Not a valid `lc-iac-map/v1` document, or it carries a secret-looking key. |
| 400 | `iac_map_bounds` | Over 20 MiB, 100,000 resources, nesting depth 8 or 4 KiB per string. Split it by workspace. |
| 400 | `iac_map_workspace_limit` | More than 100 workspaces for one repository. |
| 409 | `iac_map_stale` | A newer revision is already published. |
| 415 | | Send uncompressed `application/json`. |
| 429 | | More than 30 pushes a minute. |
| 503 | `codesec_disabled` | This feature is not enabled for your organization. |
| 503 | `iac_map_busy`, `iac_map_storage_unavailable`, `iac_map_ingest_unavailable` | Try again. Resubmitting the same document is safe. |

`GET /code/iac-map/status` reports `processing`, `published`, `retryable`
(resubmit the same document) or `superseded`, and `iac_map_not_found` for an
unknown receipt.

`POST /code/provenance` uses `error_code`:

| HTTP | `error_code` | Meaning and fix |
|---|---|---|
| 400 | `provenance_invalid_document` | Bad JSON, over 1 MiB, or a reserved field such as `trust`, `verified` or `signer`. LimaCharlie sets those itself. |
| 400 | `provenance_identity_required` | The request has no authenticated identity. |
| 400 | `provenance_rejected` | The statement was refused. Details are withheld on purpose. Check it against the format. |
| 429 | | More than 60 pushes a minute. |
| 503 | `provenance_unavailable` | Try again. |

## Feature switched off

`feature_disabled` (evidence chain, coverage, impact, runtime check),
`disabled` (remediation) and `codesec_disabled` (map push) all mean the same
thing: the feature is not enabled for your organization. These capabilities are
enabled region by region. Contact LimaCharlie support to find out when yours is.
