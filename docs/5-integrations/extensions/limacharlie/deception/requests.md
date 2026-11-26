# Deception: Requests

You drive Deception with extension requests, from the CLI, the API, MCP or a D&R rule. From version 5.14.0, the LimaCharlie CLI has a command for each request, with a flag for each field (`limacharlie deception <command> --ai-help` lists them; see the [command reference](https://github.com/refractionPOINT/python-limacharlie/blob/master/doc/cli/deception.md)):

| Request | CLI command |
| --- | --- |
| `plan`, `deploy`, `coverage`, `verify`, `rotate`, `remove`, `uninstall` | `limacharlie deception plan`, `deploy`, ... (`remove` and `uninstall` need `--confirm`) |
| `list`, `list_hosts`, `list_hits`, `list_readers`, `list_test_runs`, `list_test_paths` | `limacharlie deception list`, `list-hosts`, `list-hits`, `list-readers`, `list-test-runs`, `list-test-paths` |
| `test_fire`, `rollout_status`, `restore_rules`, `uninstall_status`, `list_kinds` | `limacharlie deception test-fire`, `rollout-status`, `restore-rules`, `uninstall-status`, `kinds` |
| `create_drop`, `list_drops`, `get_drop`, `update_drop`, `rotate_drop`, `delete_drop`, `draft_drop_document` | `limacharlie deception drops create`, `list`, `get`, `update`, `rotate`, `delete` (needs `--confirm`), `draft-document` |

Any CLI version can send a request with its fields as JSON:

```bash
limacharlie extension request --name ext-deception --action <action> --data '<json>' --oid "$OID"
```

Every request is idempotent and listed in the extension's request schema, so the CLI, the web app and MCP discover them. Sending a request needs the `ext.request` permission. Requests that plan, place, remove, verify or test decoys, and the token requests, are refused for an organization that is not subscribed or is being unsubscribed (`not_subscribed`).

Requests that read your policies and templates (`plan`, `deploy`, `verify`, `rotate`, `remove`, `test_fire`, `list_test_paths`, `coverage`, the token requests including `draft_drop_document`, and `list` or `list_hosts` with a policy) also refuse while the `ext-deception` configuration record is disabled (`config_disabled`). The extension never writes that record, so it never enables it for you: see [Enabling the configuration record](configuration.md#enabling-the-configuration-record). `list` and `list_hosts` without a policy, `list_hits`, `list_test_runs` and `list_readers` read the extension's own store and keep working while the record is disabled (`list_readers` then judges no reader approved and says so in `allowlist_unavailable`). `list_hits` and `list_test_runs` take `policy` as a plain filter, so they accept the name of a policy you have since removed. `uninstall`, `uninstall_status`, `rollout_status` and `restore_rules` need only a subscribed organization, so they work even when your configuration is broken (`restore_rules`, like `deploy`, is refused while an uninstall is in progress).

Secret values of decoys placed on hosts never appear in any response or log: decoys are described by instance id, template, path and type. The one exception is a token, whose value is what you paste: `create_drop`, `get_drop` and `rotate_drop` return it (see [Tokens](drops.md)).

| Action | Purpose |
| --- | --- |
| [`plan`](#plan) | Read-only preview of what `deploy` would do, with rollout progress. |
| [`deploy`](#deploy) | Converge rules and configuration entries, then start a rollout. |
| [`rollout_status`](#rollout_status) | Read how far the rollout is, cheaply enough to poll. |
| [`restore_rules`](#restore_rules) | Put shipped detection rules back as shipped and enabled, without a rollout. |
| [`list`](#list) | Page through decoys, with filters and an optional summary by failure cause. |
| [`list_hosts`](#list_hosts) | Page through every targeted sensor, with a status and its last rollout visit. |
| [`verify`](#verify-rotate-and-remove) | Re-check that decoys are still in place. |
| [`rotate`](#verify-rotate-and-remove) | Retire decoys and plant replacements. |
| [`remove`](#verify-rotate-and-remove) | Remove decoys from their hosts. |
| [`test_fire`](#test_fire) | Check the synthetic detection path of each alert, or of one token. |
| [`list_test_runs`](#list_test_runs) | Page through recent `test_fire` runs and their outcomes. |
| [`list_test_paths`](#list_test_paths) | Every alert path with its latest test result, or why no test proves it. |
| [`list_hits`](#list_hits) | Page through the hits the extension recorded. |
| [`list_readers`](#list_readers) | Who reads the decoys, and an allowlist entry to approve each. |
| [`coverage`](#coverage) | What is active, unavailable, partial or broken, per template and layer. |
| [`list_kinds`](#list_kinds) | Decoy kinds, their schemas, the template library and the benign-reader starter list. |
| [`create_drop`, `list_drops`, `get_drop`, `update_drop`, `rotate_drop`, `delete_drop`](drops.md) | Tokens. |
| [`draft_drop_document`](#draft_drop_document) | The content a document token would be generated with. |
| [`uninstall`](operations.md#uninstalling-before-you-unsubscribe) | Remove everything the extension owns, before you unsubscribe. |
| [`uninstall_status`](#uninstall_status) | Read where an uninstall stands, without changing anything. |
| [`respond`](detections.md#the-respond-request) | Called by detection rules on a hit, and by the web app's Isolate host and Tag host actions. |

Every `list*` request applies its filters before it cuts a page, so a page holds `page_size` rows unless it is the last one, and `next_page_token` is empty exactly when nothing more exists. A token is opaque and tied to the filters it was issued for (`invalid_page_token` otherwise). `page_size` is at most 500, default 100.

`candidate`, `task_reply`, `helper_start`, `sweep`, `rollout`, `connected`, `daily` and `test_detected` are internal. The extension's own rules call them, and you do not need to send them. The `daily` request advances each organization once a day, `sweep` runs every 30 minutes, and `rollout` continues a [rollout](operations.md#rollouts).

Most requests accept `policy` (limit to one policy) and `sid` (limit to one sensor). Requests that read your configuration reject an unknown policy name (`unknown_policy`).

## Errors and refusal codes

A request that is refused because of something in your request, your configuration or the organization's state says what is wrong in English, naming the field, and ends with a **stable code** in brackets:

```text
drop limit reached for the organization [drop_cap]
```

The sentence may be reworded in a later release; the code will not. Scripts, pipelines and AI agents should react to the code: take the **last** bracketed token of the message that is a code from the table below (your own input, such as a quoted policy name, comes before it). The platform hands a caller only the text of an extension's error, which is why the code travels inside it.

Codes also appear:

- in `issues` (of `deploy`, `plan`, `verify`, `rotate`, `remove`, `test_fire`, `uninstall`, the rollout and the daily run), as a `code` field next to the `reason`. Every issue has one: a refusal's code from the tables below, or, for a note about what was or was not done, a [note code](#codes-notes-of-plan-deploy-test_fire-and-the-daily-run). A failed step whose cause is internal carries `step_failed`;
- in the daily run's response, as `config_error_code` beside `config_error`;
- in `respond`, as the `code` of each action that was not done, next to its `reason`.

A failure on the extension's side, a store or platform error for example, never shows its internal text. It reads `internal error (ref <id>)`, with an id that is new for each failure and that LimaCharlie support can use to find the details. Quote the id when you contact support. The `reason` of a failed decoy (in `list`) keeps its own form, for example `placement could not start: internal error [placement_start_failed]`, and is grouped by its [failure cause](#list).

The codes, by area. A code's meaning never changes; new codes may be added.

### Codes: the organization and its configuration

| Code | Meaning |
| --- | --- |
| `not_subscribed` | The organization is not subscribed to ext-deception, or is being unsubscribed. |
| `subscribed_again` | The organization subscribed again while a cleanup of its earlier subscription ran; the cleanup was abandoned. |
| `config_disabled` | The ext-deception configuration record is disabled, so there are no policies. |
| `config_unreadable` | The configuration record could not be read or confirmed just now (retried); in a respond action: the isolation cap is unknown because of it. |
| `invalid_config` | The configuration is invalid; the text names the fields. |
| `config_etag_mismatch` | The configuration record changed while the extension was writing it. |
| `entry_not_owned` | The extension refused to change an entry it did not create. |
| `engine_unavailable` | Decoy planning and placement are not available in this deployment. |
| `request_timeout` | The request ran out of time before it finished; it is retried. |

### Codes: the platform refusing the extension

| Code | Meaning |
| --- | --- |
| `extension_permission_missing` | The extension's API key is missing a permission (named in the text when the platform says which). |
| `platform_forbidden` | The platform refused the extension's permissions or credentials for this organization. |
| `sensor_not_in_org` | The platform says the sensor does not exist in this organization. |
| `sensor_offline` | The platform could not deliver a task to the sensor: it is offline or unreachable. |
| `platform_rate_limited` | The platform is rate limiting the organization or its quota is used up. |

### Codes: request shape and filters

| Code | Meaning |
| --- | --- |
| `bad_request_type` | The request's data does not have the shape of the action. |
| `unknown_policy` | The request names a policy that is not in the configuration. |
| `unknown_state` | A state filter or value is not one the request accepts. |
| `unknown_layer` | A layer filter is not a known alert layer. |
| `unknown_event_type` | An event_types filter names an unknown hit event type. |
| `too_many_event_types` | The event_types filter lists more types than exist. |
| `unknown_classification` | A classification filter is not a known classification. |
| `unknown_mode` | A mode is neither live nor observe. |
| `unknown_platform` | A platform is not windows, linux or macos. |
| `filter_text_too_long` | A text filter is longer than allowed. |
| `invalid_time_window` | Since is not before until. |
| `invalid_days` | Days is out of range. |
| `invalid_page_token` | The page token is not the next_page_token of the previous page. |
| `scope_required` | Rotate or remove names no instance_ids, sid, policy or template: it would act on every decoy of the org. |
| `unknown_failure_cause` | A cause filter is not a known failure cause. |
| `failure_cause_state` | A cause filter is given with states other than failed. |
| `unknown_host_status` | A status filter is not protected, partial, pending, failed, skipped, no_decoy or none. |
| `test_fire_target_conflict` | Test_fire names a policy and a drop_id; it takes one. |
| `rules_required` | Restore_rules names no rule: it needs at least one. |
| `unknown_pack_rule` | Restore_rules names a rule that is not a shipped detection rule (the rules of plan's `pack` or coverage's `pack_issues`). |
| `bad_event` | An event sent by the extension's own rules lacks a field it needs. |
| `event_too_large` | An event sent by the extension's own rules is larger than the extension accepts. |
| `unknown_sign_in_source` | A sign-in source is not one the extension knows. |

### Codes: decoys, sensors and operations

| Code | Meaning |
| --- | --- |
| `sensor_not_found` | The sensor is not one the extension knows in this organization. |
| `instance_not_found` | The decoy instance is not one the extension knows in this organization. |
| `too_many_instances` | The sensor holds more decoy instances than one request processes. |
| `unsupported_platform` | The sensor's platform is not supported. |
| `operation_not_found` | The operation the request continues does not exist. |
| `resume_needs_sid` | Resuming an operation needs a sensor id. |
| `rotation_contended` | Other requests are changing the rotation's record; try again. |
| `test_fire_incomplete` | Earlier attempts of this test request did not complete; retry with a new request. |
| `sweep_backlog` | Held events remain after the 30-minute sweep's time budget; it is retried to continue. |
| `held_candidates_failed` | Some held events could not be judged (the text says how many). |

### Codes: uninstall

| Code | Meaning |
| --- | --- |
| `uninstalling` | An uninstall is in progress: nothing is placed or reinstalled. |
| `uninstall_flags_conflict` | Uninstall was given force and cancel together. |
| `uninstall_superseded` | The uninstall request belongs to an earlier subscription of the organization. |
| `uninstall_moved` | The uninstall state changed while the request ran; run it again. |
| `cleanup_running` | The final cleanup is running and cannot be cancelled now. |
| `cleanup_lease_lost` | The final cleanup is no longer owned by this request. |
| `entries_left_unsubscribed` | Entries of ours remain in the config of extensions the organization left, and the platform refuses their removal. |

### Codes: tokens (drops)

| Code | Meaning |
| --- | --- |
| `drops_unavailable` | Drops are not available in this deployment (no token issuer or decoy domain is configured). |
| `drop_not_found` | The drop is not one of the organization's. |
| `invalid_drop_id` | The drop_id does not have the shape of a drop id. |
| `drop_cap` | The organization has reached its drop limit. |
| `drop_rate` | Too many drops were created in the last hour. |
| `drop_rotations` | The drop was rotated too often recently. |
| `drop_version_conflict` | The drop changed since it was read; read it again and retry with its version. |
| `drop_deleted` | The drop is deleted and cannot change. |
| `drop_invalid` | The drop write is outside the store's bounds; the text says which. |
| `drop_contended` | The drop kept changing while the request read or deleted it; retry. |
| `unknown_form` | The drop form is not url, qr, hostname or document. |
| `invalid_label` | The drop label is missing, too long or holds control characters. |
| `invalid_memo` | The drop memo is too long or holds control characters. |
| `invalid_observe_until` | Observe_until is not an RFC 3339 time. |
| `observe_until_live` | Observe_until is set on a drop that is not in observe mode. |
| `unknown_domain` | The domain is not one of this deployment's decoy domains. |
| `format_document_only` | A format is given for a drop that is not a document. |
| `format_unavailable` | The document format is not generated in this release. |
| `format_required` | A document drop needs a format. |
| `unknown_format` | The document format is unknown. |
| `invalid_state_change` | Update_drop sets a state other than active or disabled. |
| `drop_not_active` | The drop is disabled or deleted, so it cannot be tested. |
| `drop_test_unavailable` | Drops cannot be tested in this deployment. |
| `drop_test_timed_out` | The request's earlier drop tests timed out without a detection; the next request tests again. |
| `redirect_flagged` | Google Web Risk lists the redirect target as malware, social engineering or unwanted software. |
| `redirect_check_unavailable` | The redirect target could not be checked against Google Web Risk right now; try again later. |
| `redirect_unavailable` | Redirect targets are not available in this deployment (no URL reputation check is configured). |
| `redirect_form` | A redirect applies to url and qr drops only. |
| `redirect_invalid` | The redirect_url is not an acceptable public https URL; the text says why. |
| `target_check_rate_hour` | Too many redirect target checks for the organization in the last hour. |
| `target_check_rate_minute` | Too many redirect target checks for the organization this minute. |

### Codes: tokens declared in the configuration

| Code | Meaning |
| --- | --- |
| `drop_config_managed` | The drop is declared in the configuration's drops: change or remove its entry there instead. |
| `drop_config_immutable` | A drops entry changes its drop's form, format or domain, which cannot change: give the entry a new name. |
| `drop_sync_backlog` | The configuration's drops are not all applied after a sync pass's time budget; the request is retried to continue. |
| `drop_ref_required` | Get_drop takes a drop_id or a name, exactly one of them. |
| `unknown_managed_by` | A managed_by filter is neither config nor api. |

### Codes: `respond`: the request

| Code | Meaning |
| --- | --- |
| `hit_id_required` | Respond names no hit_id. |
| `unknown_action` | Respond names an action other than isolate, tag, ai_triage or policy. |

### Codes: `respond`: an action not done (the action's code)

| Code | Meaning |
| --- | --- |
| `hit_not_found` | The hit is not one of the organization's. |
| `synthetic_hit` | The hit is a synthetic (test) hit. |
| `unmatched_test_instance_hit` | The hit is on a test decoy that no test run matches. |
| `delete_only_hit` | The hit is a delete only, which never isolates. |
| `off_host_hit` | The hit has no on-host evidence from the sensor. |
| `scanner_likely_hit` | The hit looks like a scanner. |
| `sensor_gone` | The decoy's sensor is gone. |
| `host_rebuilt` | The host was enrolled again after the hit. |
| `hit_too_old` | The hit is older than the response window. |
| `isolation_in_progress` | Another request is isolating for the same incident. |
| `already_isolated_for_incident` | The incident was already isolated. |
| `org_hourly_cap` | The organization's hourly isolation cap is reached. |
| `org_inactive` | The organization is unsubscribed. |
| `no_endpoint` | The hit names no endpoint (a drop hit, or a hit without a sensor). |
| `isolation_cap_invalid` | The configuration's isolation_cap_per_hour is invalid, so the isolation cap is unknown. |
| `observe_mode_hit` | The hit was judged in observe mode: no automatic response. |
| `no_automatic_response` | The hit's policy asks for no automatic response. |
| `policy_disabled` | The hit's policy is disabled, so it asks for no automatic response. |
| `policy_not_in_config` | The hit's policy is not in the configuration, so it asks for no automatic response. |
| `ai_triage_unavailable` | Starting an AI triage session from the extension is not available in this release. |

### Codes: notes of plan, deploy, test_fire and the daily run

An issue that is not a refusal still has a `code`, taken from this table, and names what it is about in fields next to the sentence (all absent when they do not apply): `sid`, `hostname`, `instance_id`, `policy`, `template`, `layer` (or `layers`), `field` (the configuration field of a configuration problem, for example `templates[3].spec.file_name`), `rule`, `lookup`, `status`, and `count` with `total` when the sentence is about "N of M". The sentence may be reworded; the code and the fields will not change. A note that means what a refusal means reuses the refusal's code (for example `sensor_offline`, `sensor_gone`, `instance_not_found`, `drop_cap`, `org_inactive`, `request_timeout`, `uninstalling`). A code in the tables above belongs to a refusal and a code in this one to a note, with no code in both, except that a note may reuse the code of the refusal it means. Tell them apart by where a code appears: a `[code]` at the end of a refused request's error message is always a refusal, and the `code` of an entry of `issues` is a note's or a refusal's. Note codes never travel inside an error message.

| Code | Meaning |
|---|---|
| `step_failed` | A step failed for a cause that is not the customer's to act on; the text names the step (the cause is logged, never shown). |
| `more_issues` | More issues than one answer lists; count is how many were left out. |
| `request_already_completed` | This request (its idempotency key) already completed: nothing was started again. |
| `config_problem` | A field of the configuration has a problem; field names it. |
| `config_record_skipped` | A record of the configuration was skipped on read; field names it. |
| `retire_held_config_disabled` | The configuration record is disabled: the daily run retires no decoy until it is enabled. |
| `retire_held_config_skipped` | Records of the configuration were skipped on read: the daily run retires no decoy for configuration reasons until it is fixed. |
| `retire_not_counted` | Records of the configuration were skipped on read: plan does not count the decoys to retire. |
| `policy_schema_too_new` | The policy's schema_version is newer than this extension understands: it is skipped. |
| `template_disabled` | The template is disabled: the policy places none of it. |
| `template_not_found` | The policy names a template that is not in the configuration. |
| `template_schema_too_new` | The template's schema_version is newer than this extension understands: it is skipped. |
| `template_unknown_kind` | The template's kind is not one this extension knows: it is skipped. |
| `template_kind_version_too_new` | The template's kind_version is newer than its kind understands: it is skipped. |
| `template_spec_invalid` | The template's spec is not valid for its kind; the text says why. |
| `template_plan_failed` | The kind could not plan the template on the sensor; the text says why. |
| `template_needs_ext_artifact` | The template places a file, which needs a subscription to ext-artifact. |
| `placement_skipped` | A planned decoy was not placed on the sensor this time (another pass superseded it, an earlier attempt on this inventory found the placement impossible, or the kind produced an unusable placement); the text says which. |
| `host_cloud_sensor` | The sensor is an adapter or cloud sensor: no decoy is ever placed on it. |
| `host_daemonset` | The sensor is a Kubernetes DaemonSet sensor, which sees the node read-only: no decoy can be placed. |
| `host_sleeper_mode` | The sensor is in lc:sleeper mode: no decoy can be placed (the extension never changes sensor modes). |
| `host_only_unavailable_templates` | Every template that targets the sensor is unavailable in this release: nothing is placed on it (coverage lists those paths as unavailable). |
| `host_response_mode` | The sensor is in lc:response mode: no decoy can be placed (the extension never changes sensor modes). |
| `targets_unlisted` | The platform could not list the targeted sensors this time: the counts come from the first pages of the sensor list. |
| `target_count_lower_bound` | The policy targets more sensors than were counted: its count is a lower bound. |
| `decoy_count_lower_bound` | The policy's sensors with decoys were counted over its first decoys only: the count is a lower bound. |
| `detail_sampled` | Only the first pages of sensors were inspected: the detail covers a sample of the sensors. |
| `detail_first_sensors` | Placed, to-place and to-retire cover the first targeted sensors only (count is how many). |
| `more_plan_notes` | More reasons something was not planned than plan lists; count is how many were left out. |
| `plan_stopped` | Plan ran out of time before every sensor was planned. |
| `no_inventory_today` | Sensors have no inventory from today: what would be placed on them is not counted (deploy collects it first). |
| `sensor_not_targeted` | No enabled policy targets the sensor. |
| `deploy_policy_disabled` | The policy is disabled: nothing to deploy. |
| `no_enabled_policy` | No policy is enabled: nothing to deploy. |
| `dc_logon_ignored` | The policy's dc_logon_collection is ignored in this release. |
| `observe_no_end` | The policy is in observe mode with no observe_until: its on-host hits alert at low priority with no automatic response until mode is set back to live. |
| `observe_until_set` | The policy is in observe mode until its observe_until. |
| `observe_ended` | The policy's observe_until has passed, so it is live; set mode: live to make that explicit. |
| `observe_rule_not_shipped` | A detection rule that judges observe-mode hits is not the shipped one; rule names it. |
| `lookups_partly_checked` | The reader allowlists reference more Lookups than plan checks; count is how many, total how many were checked. |
| `lookup_approves_nothing` | A reader allowlist Lookup approves no reader; lookup names it, status says why. |
| `lookup_invalid_records` | Records of a reader allowlist Lookup are not valid allowlist entries and approve nothing; count of total. |
| `signal_unsupported` | A template asks for an event type this release does not forward. |
| `signal_matcher_invalid` | A template's path, command-line or domain matcher cannot be made into a safe candidate rule and is skipped; rule names the candidate rule, the text says why. |
| `watch_entry_skipped` | The template's ext-exfil watch entry cannot be built; the text says why. |
| `fim_entry_skipped` | The template's ext-integrity rule cannot be built; the text says why. |
| `rollout_all_policies` | The org's rollout round places every enabled policy together, the named one included. |
| `rollout_continues` | The rollout continues on its own; count is the targeted sensors done, total all of them when known. |
| `rollout_resumes_later` | The rollout resumes within 30 minutes; count is the targeted sensors done, total all of them when known. |
| `rollout_idle` | No rollout pass ran now; the text says why. |
| `rollout_paging` | The platform's resolution of the targeted sensors is too slow: the rollout pages the sensor list. |
| `rollout_fail_streak` | The rollout pass stopped after too many sensors in a row failed: the next pass retries them. |
| `rollout_resolve_failed` | The targeted sensors could not be resolved: the next pass tries again. |
| `rollout_no_time` | The daily run had no time left for the rollout: a round under way continues on its own. |
| `instance_ids_truncated` | More instance_ids than one request processes; count is how many were processed. |
| `instance_other_policy` | The decoy belongs to another policy than the request names. |
| `instance_other_sensor` | The decoy is on another sensor than the request names. |
| `instance_other_template` | The decoy is of another template than the request names. |
| `sensors_offline` | Sensors were offline; count is how many, the text says what happens to their work. |
| `sensors_busy` | Sensors have an inventory or planning pass already running: they are placed when it completes. |
| `template_tags_added` | Template tags were added for decoys already on sensors; count is the sensors, total the tags. |
| `more_decoys_match` | More decoys match: send the request again to continue. |
| `test_decoy_not_rotated` | Test decoys are not rotated. |
| `teardown_stopped` | The teardown stopped before every decoy was handled. |
| `teardown_sensors_offline` | Sensors were offline during the teardown: their decoys stay inert on disk. |
| `teardown_bounded` | More decoys than one teardown handles: the rest stay inert on disk. |
| `tag_sweep_bounded` | The template has more live decoys than one daily run reads: missing tags are added for those read, none is removed. |
| `stranded_placements_failed` | Decoys whose placement never started were failed and will be planned again. |
| `stranded_test_decoys_retired` | Test decoys whose placement never started were retired and will be recreated. |
| `reconcile_stopped_early` | The reconcile stopped early to leave the rollout its time: the next daily run continues it. |
| `failed_placements_redeployed` | Sensors whose last placement of a wanted decoy failed were deployed again. |
| `pack_check_failed` | The shipped detection rules could not be checked this time. |
| `pack_rule_broken` | A shipped detection rule is missing or disabled; rule names it. |
| `nothing_to_test` | No alert path to test: no enabled policy selects a usable template. |
| `path_not_testable` | The alert path is not tested because of its coverage status (status). |
| `more_paths` | More alert paths than one test_fire request tests: call it again to continue (count). |
| `path_unavailable_in_release` | The alert paths (layers) are unavailable in this release: not tested. |
| `more_unavailable_paths` | More policy and template pairs have alert paths unavailable in this release than are listed (count). |
| `test_decoy_lacks_file_events` | The test decoy is on a sensor that cannot report the file events this alert path needs: not tested. |
| `test_already_starting` | An earlier request with the same key is still starting this test: not tested again. |
| `test_not_buildable` | The kind could not build a test for this alert path. |
| `test_no_action` | The kind describes no test action for this alert path. |
| `test_unsupported_binding` | The kind's test action has a binding the sensor command does not support. |
| `test_decoy_has_no_file` | The alert path's sensor action needs a decoy file, which the test decoy does not have. |
| `test_decoy_path_unusable` | The test decoy's path cannot be used by the placement helper. |
| `test_collector_unavailable` | The collector's internal test path is not configured for this extension: not tested. |
| `test_decoy_no_secret` | The test decoy has no secret of the type its test needs: not tested. |
| `test_pipeline_unavailable` | The hit pipeline is not available to this extension: not tested. |
| `test_decoy_placing` | Not tested yet: the test decoy is being placed (test_fire again in a few minutes). |
| `test_decoy_ready` | Not tested yet: the test decoy is in place; the next test run tests this path. |
| `test_decoy_failed` | Not tested yet: the last test decoy could not be placed on its sensor (sid, cause); the next test run tries the other sensors first. |
| `test_not_run_yet` | Not tested yet: no test of this alert path has finished; the daily run or test_fire tests it. |
| `test_result_unread` | The latest test result of this alert path could not be read this time: ask again. |
| `test_no_candidate_sensor` | Not tested: the policy targets no sensor the extension knows yet and holds no placed decoy of the template. |
| `layer_has_no_test` | No test proves this alert path: the template's kind has no test for its layer (a test never deletes its decoy). |
| `test_tag_restored` | Not tested yet: the test decoy's sensor had lost the template's tag, which is back; the rules reach it within minutes. |
| `test_rules_settling` | Not tested yet: the test decoy is new and the template's watch rules are still reaching its sensor. |
| `test_sensor_search_continues` | Not tested yet: no sensor looked at so far can take the test decoy; test_fire again to keep looking. |
| `test_no_sensor_with_file_events` | Not tested: no online sensor of the policy looked at can report the file events the alert path needs. |
| `test_no_sensor_with_inventory` | Not tested: no online sensor of the policy has an inventory from today (deploy collects inventories). |
| `test_rule_off` | Not proven: the `deception-test` rule is missing or disabled, so no test is started, and a test that ran while it was off is neither passed nor failed. Alert paths are not changed by it. Also a `list_test_paths` row state, a coverage item's note and a token form's coverage reason. |
| `test_not_proven` | A coverage item's note: the path's latest test produced no detection while every rule and source it needs is fine. The path keeps its status and is not proven on that test's host (`not_proven` names it). |
| `check_failed` | The drop detection rules could not be checked this time. |
| `drop_rule_broken` | A drop detection rule is missing or disabled. |
| `not_tested` | The drop form has not been tested yet: the daily test-fire tests it. |
| `test_not_detected` | The latest test hit of the drop form was not detected. |
| `rule_edited` | A drop detection rule differs from the shipped one: the extension does not judge edits. |
| `requirement_missing` | Coverage item: the alert path lacks a requirement your organization has not met; `missing` names it. |
| `context_only` | Coverage item: the policy alerts on use only, so this path's hits are recorded for context and raise no alert. |
| `source_quiet` | Coverage item: a source the path needs delivered no data recently. |
| `source_note` | Coverage item: a note on a source the path needs (no sign-in observed recently); the path stays active. |
| `file_events_unavailable` | Coverage item: the sensors cannot report the file events the path needs. |
| `file_events_version_unknown` | Coverage item: the sensor's version is not known, so its file events are not confirmed. |
| `decoy_not_placed` | A sensor's coverage: no decoy of the template is placed on it. |
| `decoy_placed_some` | A sensor's coverage: the decoy is placed on some of its targets; the others were skipped. |
| `decoys_placing` | Coverage item: decoys of the template are still being placed or verified. |
| `placement_outcome_unknown` | The placement history was read in part: the outcome of some targets is not known. |
| `placements_failed` | Coverage item: placements of the template failed and are current (`sensors_failed` counts their sensors). |
| `decoys_skipped` | Coverage item: sensors skipped the template on purpose because its folder is not on them (`sensors_skipped`). |
| `template_tag_missing` | Coverage item: none of the sensors holding a verified decoy of the template carries its tag yet. |
| `template_tag_partial` | Coverage item: some sensors holding a verified decoy of the template do not carry its tag yet. |
| `registry_capped` | Coverage item: the registry was read up to its bound, so the item's counts are lower bounds. |

## plan

Read-only. Shows, per policy, how many sensors it targets, how many hold its decoys already, what would be placed or retired, and what is unavailable and why.

- `sensors` is the number of sensors the policy targets, resolved by the platform, and exact up to 100,000 per policy (`sensors_exact`). Past that, or when the platform could not resolve the targets this time, it is a lower bound and an issue says so.
- `sensors_with_decoys` (with `sensors_with_decoys_exact`) is the number of distinct sensors holding a placed or verified decoy of the policy. With `sensors` it is the rollout's progress per policy.
- `already_placed`, `to_place` and `to_retire` are computed over the sensors planned in detail: `detail.sensors` of them, the lowest sensor ids, at most 100 (`detail.complete` says whether that is every targeted sensor). Send `sid` to plan one sensor.
- A sensor with no inventory from today is not counted in `to_place` (`deploy` collects the inventory first), and `to_retire` is not computed while some configuration records were skipped on read.
- Why a template could not be placed is in `plan.issues` (`<policy>/<template> <field>: <reason>`, with how many of the planned sensors it applies to), most frequent first. Each such issue carries the skip's `code`, `policy`, `template`, `field`, and `count` (the sensors it applies to) with `total` (the sensors planned), so a script never reads the sentence. "Nothing can be placed" carries the host's code (`host_cloud_sensor`, `host_daemonset`, `host_sleeper_mode` or `host_response_mode`).

It also reports:

- `plan.deploy`: `in_progress` while a [rollout](operations.md#rollouts) round is running, and `rollout`, its progress.
- `pack`: the state of each shipped detection rule (`missing`, `current` or `modified`). `modified` compares the rule's content only (detect, respond and the rest of the rule): a rule that was only disabled, or whose tags or expiry changed, is `current` here (`coverage` still reports it). For a modified rule it includes the current shipped version, so you can compare it with yours. A newer shipped version is offered here and never applied implicitly (see [Upgrading](operations.md#upgrading)).
- `watch_budget`: Exfil watch rules per sensor against the limit of 100 (see [Watch-rule budget](decoys.md#watch-rule-budget)).
- `sources`: which of `ext-artifact`, `ext-exfil`, `ext-integrity` are subscribed and which adapters the organization has.
- `reader_lookups`: every Lookup the reader allowlists reference, read now, with its `status`, records, entries, where it is used and its invalid records (see [Lookups](configuration.md#share-one-list-across-organizations-lookups)).
- `isolation_cap`: the hourly isolation cap in effect (`per_hour`, `source`). Absent when `respond` could not know it and would refuse to isolate.
- `drops`: what the next sync of your declared tokens would do (see [Declare tokens in the configuration](drops.md#declare-tokens-in-the-configuration)).
- `warnings` (a list of strings) and `warning_details` (the same warnings in the same order, each an issue whose `reason` is the text, with its `code` and subject fields, for example `config_problem` with the `field`): configuration records skipped on read, rule signals skipped as unsafe, policies that observe and until when, a passed `observe_until`, shipped observe rules that are missing or not current, Lookups that approve nothing, and a warning for each policy that sets `dc_logon_collection` (ignored in this release).

```bash
limacharlie deception plan --policy linux-servers --oid "$OID"
```

```json
{
  "plan": {
    "policies": [
      {"policy": "linux-servers", "enabled": true,
       "sensors": 4200, "sensors_exact": true,
       "sensors_with_decoys": 1310, "sensors_with_decoys_exact": true,
       "already_placed": 62, "to_place": 76, "to_retire": 0,
       "unavailable": [{"id": "ext-exfil", "human": "Subscribe ext-exfil"}]}
    ],
    "detail": {"sensors": 100, "complete": false},
    "deploy": {"in_progress": true,
               "rollout": {"state": "running", "trigger": "deploy", "done": 1450, "total": 4200,
                           "total_exact": true, "remaining": 2750, "started": 1300, "offline": 120,
                           "skipped": 25, "failed": 5, "passes": 14}}
  },
  "pack": [{"name": "deception-alert", "state": "current"}],
  "watch_budget": {"limit": 100, "sensors": 100, "sid": "…", "owned": 3, "customer": 12, "total": 15, "over": false},
  "sources": {"ext_artifact": true, "ext_exfil": false, "ext_integrity": true},
  "isolation_cap": {"per_hour": 5, "source": "default"}
}
```

## deploy

Idempotent. Converges, in order:

1. the webhook adapter,
2. the plumbing rules in `dr-service`,
3. the missing shipped detection rules in `dr-general` (never overwriting one you edited, and never replacing one with a newer shipped version unless you ask with `apply_pack`),
4. the `ext-deception-` entries in the `ext-exfil` and `ext-integrity` configurations (and removes any `ext-deception-` entry an earlier build left in `ext-artifact`; this release adds none there),

applies your declared tokens (`drops`) again, then starts the organization's [rollout](operations.md#rollouts) round when none is running, works on it for about 20 seconds, and returns its progress. The round goes on by itself after the request returns: you do not need to call `deploy` again. A second `deploy` while it runs only reports. With `policy`, the round still places every enabled policy, that one included, and the answer says so. With `sid`, only that sensor is deployed, at once. It never subscribes the organization to another extension: extensions it needs that are not subscribed are listed in `not_subscribed`.

| Parameter | Meaning |
| --- | --- |
| `policy`, `sid` | `sid` deploys to one sensor now (the web app's **Place on this host now**). |
| `apply_pack` | List of shipped rule names to overwrite with the current shipped version, for example `["deception-alert"]`. The rule is restored as a whole, including its tags and expiry, so it also repairs a rule that reads `unverified`. |
| `apply_all_pack` | Overwrite every shipped rule. Replaces your edits. |

```bash
limacharlie deception deploy --oid "$OID"
limacharlie deception deploy --apply-pack deception-alert --oid "$OID"
```

The response has `ops` (`started`, `skipped`, `operations` ids, `issues`, `rollout` with the round's progress, and `more`, true while the round is not finished), `plumbing_written`, `pack_installed`, `pack_applied`, `others_updated`, `not_subscribed`, `drops` and `warnings`. Placement is asynchronous: sensors reply later, and a decoy counts only after its hash is verified. Use `plan`, `list` and `coverage` to follow it. Every sensor a deploy reaches also gets the missing [template tags](decoys.md#per-host-watch-rules) of the decoys it already holds.

## list

Paginated list of decoys, ordered by state then id. Test decoys are hidden unless you ask.

| Parameter | Meaning |
| --- | --- |
| `policy`, `sid` | Filters. |
| `template`, `kind` | Only decoys of this template name, or of this kind. |
| `states` | Any of `planned`, `placed`, `verified`, `retired`, `gone`, `failed`. Default: `planned`, `placed`, `verified`. |
| `cause` | Only failed decoys of this cause (below). `states` must then be empty or `failed` (`failure_cause_state`). |
| `text` | Only decoys whose path, template, policy, hostname or sensor id contains this text (case-insensitive, at most 128 characters). |
| `summary` | Also count every decoy the filters match, before paging (below). |
| `include_test` | Include test-fire decoys. |
| `include_superseded` | Include the failed attempts that were superseded (see below). |
| `exclude_skipped` | With `states: ["failed"]`, leave out the decoys skipped on purpose, so only faults are listed. Live states are not affected. |
| `page_token`, `page_size` | Paging. |

```json
{"instances": [{
  "id": "…", "sid": "…", "hostname": "web-01", "policy": "linux-servers", "template": "kubeconfig-backup",
  "kind": "file", "state": "verified", "path": "/root/.kube/config.prod-old",
  "sha256": "…", "layers": ["read", "modify", "delete", "use"], "is_test": false,
  "created_at": "…", "verified_at": "…"}],
 "next_page_token": ""}
```

`hostname` is the sensor's hostname when the decoy was placed (absent on a decoy placed before it was recorded); the sensor id is the identity. `reason` explains a `failed`, `retired` or `gone` state. Instance states:

| State | Meaning |
| --- | --- |
| `planned` | Chosen, not yet sent. |
| `placed` | The sensor acknowledged, not yet verified. |
| `verified` | The file's hash matched on the host. This is the state that counts as covered. |
| `retired` | Changed or removed. Never overwritten. |
| `gone` | The sensor is gone. Tokens are kept for a retention period. |
| `failed` | Placement or removal failed. |

The `failed` filter, the `cause` filter and the summary show **current** failures only: one row per sensor, template and path, the latest attempt, and none while a live decoy of that template is on the sensor (see [Failed decoys](decoys.md#failed-decoys)). `include_superseded` brings back the earlier attempts, for a host's history; nothing is deleted. A failed decoy carries a `cause`: `directory_missing`, `path_in_use`, `directory_appeared`, `placement_not_started`, `task_not_sent`, `helper_refused`, `helper_failed`, `placement_check_failed`, `never_landed`, `timed_out`, `org_inactive` or `other`.

`directory_missing` is a decoy **skipped on purpose**, not a fault: the template's fixed folder (such as `~/.aws`) is not on the host, and the extension never creates a folder that other software owns. A failed decoy that is a skip has `skipped: true` next to its `cause`. The `cause` filter still lists skips.

With `summary: true` the answer adds `summary`: the number of `decoys` and distinct `sensors` the filters match, `failed` and `skipped` (each `{decoys, sensors}` over the matching failed decoys: the faults and the skips, a sensor with both is in both), and `causes` (each with its decoy and sensor counts and one sample reason, largest first, and `skipped: true` on a cause that is a skip). It reads at most the first 100,000 matching decoys: past that, `capped` is true and the counts are lower bounds. The web app's failed-decoy view and its scoped actions rely on it.

## list_hosts

Paginated by sensor id: every **targeted** sensor, with a decoy or not, with its hostname, a `status`, its decoys and the last rollout visit. It answers "which of my targeted hosts are not protected" without one sensor lookup per row. The web app shows it as **Decoys** > **View: Hosts** and on each sensor's Overview page.

| Parameter | Meaning |
| --- | --- |
| `policy`, `template` | Filters. `template` keeps the sensors that have a decoy of that template. |
| `sid` | One sensor. |
| `status` | Only sensors of this status: `protected`, `partial`, `pending`, `failed`, `skipped`, `no_decoy` or `none` (see [Host status](decoys.md#host-status)), judged over the decoys the other filters match. |
| `text` | Only sensors whose hostname, sensor id, or a decoy's path, template or policy contains this text (case-insensitive). |
| `states` | Default: `planned`, `placed`, `verified`, `failed`. |
| `include_test` | Include test-fire decoys. |
| `include_superseded` | Judge the status over every failed attempt, not only the current ones. |
| `summary` | Also return `summary`: `{hosts, by_status, capped, scan_cap}`, the number of hosts of each status at once, ignoring the `status` filter. Counts are lower bounds when `capped` is true. |
| `page_token`, `page_size` | Paging. |

The `status` is `protected` (a verified decoy and no fault), `partial` (a verified decoy and a decoy the policy wants missing: a current failure, or a template still to place, `to_place`), `pending` (planned or placed only), `failed` (no live decoy and a fault), `skipped` (no live decoy, and only decoys skipped on purpose), `no_decoy` (targeted, nothing placed yet) or `none` (only retired or removed decoys). Each row has the counts per state (`counts.failed` counts faults only, and `skipped` counts the skips), and up to 50 decoys in the same shape as `list` (`more` marks a cut list; the status and counts cover all of them).

A targeted sensor with no decoy has a row with status `no_decoy`. Every row of a listed sensor carries `rollout`: `{outcome, detail, code, visited_at, policies}`, what the last rollout round did when it reached the host. `outcome` is `offline` (offline then), `blocked` (nothing can be placed on it; `code` is the reason, for example `host_cloud_sensor`, `host_daemonset`, `host_sleeper_mode`, `host_response_mode` or `host_only_unavailable_templates`), `inventory` (its inventory was started; decoys follow), `planned`, `nothing_planned` (no room, or no template fits) or `failed` (the round could not deploy to it and tries again next round). It is the state at that visit, not live.

The answer's `targets` says what is listed: `listed` (false when the filters select decoys rather than hosts, as with `template`, or when no policy in scope is enabled, so only hosts with decoys are listed), `listed_since` and `rollout` (the round's progress, as in `plan`). A targeted sensor the rollout has not reached yet has no row; `rollout.remaining` says how many are left.

## verify, rotate and remove

All three act on the decoys named by `instance_ids`, or on the live decoys of a scope: a `sid`, a `policy`, a `template`, or a combination of them (for example every decoy of one template on one host). `template` need not be in your configuration any more, so the decoys of a removed template stay reachable. `rotate` and `remove` refuse to act on the whole organization: one of `instance_ids`, `sid`, `policy` or `template` is required (`scope_required`). A scoped call never includes test decoys; a test decoy you name by id in `instance_ids` is acted on.

The decoys a scoped call acts on are exactly the ones `list` with the same `sid`, `policy` and `template` and `summary: true` counts. Each call handles a bounded batch (verification: at most 200 decoys) and answers `more: true` when there is more: send it again to continue. The web app's **All decoys of …** menu on the Decoys tab does this for you.

- **`verify`** starts a read-only `file_hash` check of each decoy. The daily run also verifies the decoys of the sensors it reconciles. An offline sensor is not queued: run it again when the sensor is online.
- **`rotate`** retires the decoys and plants replacements with new secrets at new paths, for example after a decoy leaked or a decoy domain is burned. A replacement is planted only where the helper can create the file exclusively: if a changed file still occupies the path, the replacement fails as `path in use` and is reported. For decoys on offline sensors, rotate the ones its issues name by `instance_ids` later: a new scoped rotation would rotate the whole scope again, its own replacements included.
- **`remove`** removes the decoys from their hosts after checking that each file is still the one the extension placed. A file the extension cannot prove is its own is left in place and the instance is retired; it never counts as removed. A removal for an offline sensor is queued and runs when it connects. While a policy still selects the template, the next rollout round plants a replacement: that is the next configuration change, change of sources or weekly recheck, so run `deploy` (or `deploy` with the `sid`) if you want it back now. For a full cleanup before unsubscribing, use [`uninstall`](operations.md#uninstalling-before-you-unsubscribe).

```bash
limacharlie deception rotate --template kubeconfig-backup --oid "$OID"
```

## test_fire

Fires the test-only decoys of a policy, one run per alert path (for example read, modify and use of a credential file are separate runs), to check that each path reaches a detection. Deletion is not exercised: there is no delete run. The detection is the synthetic `deception-test` rule: a passing test does not prove that the real-alert rules, cases or isolation work. See [Test-fire](detections.md#test-fire) for what a test does and does not do.

```bash
limacharlie deception test-fire --policy linux-servers --oid "$OID"
```

`test_fire` takes an optional `policy`, or a `drop_id` to fire one token instead (not both: `test_fire_target_conflict`). The extension picks the test decoys and their sensors. The response lists the started `runs` (run id, policy, template, layer, deadline; never a token or planted name), `issues` (each "not tested" outcome has a `code` from the [note table](#codes-notes-of-plan-deploy-test_fire-and-the-daily-run), and `policy`, `template` and `layer`, plus the test decoy's `sid`, `hostname` and `instance_id` when it is about one), and a `pack_check` object with the result of the [rule integrity](decoys.md#rule-integrity) check. When the `deception-test` rule is missing or disabled, nothing is started: `runs` is empty, `not_run` is `test_rule_off` (the only value; absent when tests ran), and `issues` holds one issue with code `test_rule_off`. This applies with a `drop_id` too. A call starts at most 20 runs. A large configuration is covered by repeated calls, and the daily run walks it over time. Only alert paths whose requirements you meet are tested, since testing a path that cannot work would only report it broken. Paths that are not available in this release (fake AD accounts, internal-domain hostnames) are not tested: `issues` names at most 10 of those policy and template pairs and says how many more there are, and `coverage` lists every one. Refused while an uninstall is in progress.

A run is final as soon as its detection comes back, or, when none does, about an hour after it starts (see [When the result is final](detections.md#test-fire)). A test detection is reported under the reserved `__deception-test` category, which the platform never lists, so read the outcome with `list_test_runs` and `coverage`. A Windows sensor that does not report file events is not used for the paths that need them (see [Sensor versions](decoys.md#sensor-versions-windows)).

## list_test_runs

Read-only, paginated, newest first: the retained runs of `test_fire` (kept for 30 days after their deadline), one per alert path. Needs no configuration.

| Parameter | Meaning |
| --- | --- |
| `policy`, `template`, `layer` | Filters. `layer` is `read`, `modify`, `delete` or `use`. |
| `state` | `pending` (outcome not recorded yet) or `finished`. Default: both. |
| `page_token`, `page_size` | Paging. |

Each run has `run_id`, `policy`, `template`, `layer`, `instance_id`, `state`, `opened_at`, `deadline` and, for a pending run, `expected_final_at`, or for a finished one `finalized_at`. The `state` is `pending`, `detected` (the detection came back) or `not_detected`. A run's binding, planted names and tokens are never returned.

## list_hits

Read-only, paginated, newest first: the hits the extension recorded, as they were sent to the `ext-deception` adapter. They come from the extension's own store (kept for 90 days), so the request runs no detection query and needs no configuration.

| Parameter | Meaning |
| --- | --- |
| `since`, `until` | Unix seconds. `until` is exclusive. |
| `layer`, `template`, `policy`, `sid` | Filters. |
| `classification` | `unknown`, `human-likely`, `automated`, `ai-agent-likely`, `scanner-likely`, `sanctioned-agent-touched-decoy`, `copied-decoy` or `link-preview-likely` (tokens). |
| `mode` | `observe` or `live`. Hits recorded before observe mode existed read as live. Default: both. |
| `event_type` | `deception_hit`, `deception_drop_hit` or `deception_coverage_warning`. Default: every type. `event_types` takes a list instead. |
| `drop_id` | Only the hits of this token. |
| `include_test` | Include the synthetic hits of `test_fire` runs, which are left out by default. |
| `page_token`, `page_size` | Paging. |

A row is the [`deception_hit` event](detections.md#the-deception_hit-event) (or the [token hit](drops.md#what-a-hit-looks-like)): `hit_id`, `event_type`, `time`, `decoy_id`, `kind`, `template`, `policy`, `layer`, `sid`, `hostname`, `on_host`, `classification`, `mode`, `platform`, `reader_key`, `synthetic`, `case_group_key`, `source_ip`, `user_agent`, `process` and `details`, plus `drop_id` and `label` on token hits. Approved reads are not hits and are not listed: they are [`deception_read_allowed`](configuration.md#every-approved-read-is-recorded) events in your telemetry.

```bash
limacharlie deception list-hits --layer read --mode observe --page-size 50 --oid "$OID"
```

## list_readers

Read-only, paginated by reader: who reads the decoys. It aggregates the recorded on-host reads and modifications of decoys (not uses, not test hits) of the last `days` days by reader identity (platform, image path, and the code signer on Windows and macOS or the SHA-256 on Linux) and by the policy whose decoys it read. Use it with [observe mode](configuration.md#observe-mode) to build your allowlist.

| Parameter | Meaning |
| --- | --- |
| `days` | The window, ending now: default 30, at most 90 (`invalid_days`). |
| `policy`, `template`, `platform` | Filters, applied before paging. |
| `page_token`, `page_size` | Paging. |

Each row of `readers` has `reader_key`, `policy`, `platform`, `image_path`, `signer` or `file_hash`, the counts `hits`, `observe_hits`, `live_hits`, `decoys` and `hosts`, `first_seen`, `last_seen`, and:

- `allowed` and `allowed_by`: whether the current allowlist approves the reader for that policy's decoys, and by which entries (at most 20 listed, `allowed_by_truncated`). An entry that also constrains the user, package or ancestry is marked `conditional`.
- `approvable` and `allowlist_entry`: an entry to paste into `reader_allowlist` as is, when the identity has what one needs; otherwise `not_approvable_reason`. A shared interpreter, a missing signer (Windows, macOS), or an unknown platform is never approvable. A Linux reader is offered a `match: path` entry only when the file event named it (`named_in_event`), it is not in a container (`container`), and the [starter list](configuration.md#starter-list-of-benign-readers) lists a program at exactly that path; any other Linux path the rules accept is yours to write by hand (see [Reader allowlist](configuration.md#reader-allowlist)).
- `library_id`: the [starter-list](configuration.md#starter-list-of-benign-readers) entry this reader is, if any.

The first page also has `unknown_process`: reads whose event named no process, which can never be approved. `lookups` describes the Lookups the page was judged with. A page reads at most the newest 50,000 hits of the window, counted before the filters: when the window holds more, `window.capped` is true and `window.since` is the oldest hit read.

## coverage

Per template and layer: `active`, `unavailable` with the missing piece, `partial` or `broken` (`blind` is not set in this release). A template that uses the AD phantom-account form or the internal hostname form shows every layer `unavailable` with "not available in this release". A quiet Entra ID or Okta sign-in feed adds an informational note ("no sign-in observed in N hours") and never changes a status. The per-template view is organization-level: it does not list hosts, and `active` is not proof that every selected host is covered; the org-wide host counts below, and `list_hosts`, are. Host-level exclusions (sensor mode, Kubernetes DaemonSet sensors, a Windows sensor without file events) are decided per sensor and are not part of this answer or of `plan`; `list_hosts` shows them per host (a `no_decoy` host whose last rollout visit was `blocked`, with the reason), except a Windows sensor's missing file events. See [Coverage statuses](decoys.md#coverage-statuses). It also returns:

- `coverage.sensors`: `{targeted, targeted_exact, with_decoys, with_decoys_exact}`, the organization's host counts: the distinct sensors an enabled policy targets that a decoy can go on, and those holding a placed or verified decoy of an enabled policy (test decoys excluded). An exact flag that is false means the count is a lower bound. A request on a usable configuration returns it. With `policy`, every count in `sensors` except `total` is that policy's own: the sensors it targets, the sensors holding a decoy of it, its targeted hosts by status as `list_hosts` with the same `policy` judges them, and `offline_now` of its targeted sensors. These are computed the same way as the organization's counts, when the request runs, and are never stored. `total` stays the organization's count. A disabled policy counts 0, exactly. The [board's](board.md#columns-and-freshness) **Hosts with decoys** column is these numbers. They count hosts holding a decoy that is placed or verified, so they can be higher than the verified-only count of `list_hosts`' summary.
- `coverage.sensors.by_status`: the targeted hosts by [host status](decoys.md#host-status), judged exactly as `list_hosts` judges them (the same numbers as its `summary.targeted`, computed by this request): `protected`, `partial`, `pending`, `failed`, `skipped`, `no_decoy`, `not_reached` and `restricted`, every key present (0 included). `offline` counts the targeted hosts, whatever their status, whose last rollout visit found the sensor not connected (the platform's online flag at that visit; there is no time threshold). It overlaps the statuses, so do not add it to them. `by_status_exact` is false when the counts are lower bounds, and `by_status_as_of` is when the targeted sensors were counted. `unlisted` is the targeted sensors with no host row yet: no rollout round has visited them and they have not connected since. It is given only when both `sensors.targeted_exact` and `by_status_exact` are true. `offline_now` counts the targeted sensors that were not connected when this request read them, so a sensor that went offline after the last rollout visit is counted here and not in `offline`. Like `offline`, it overlaps the statuses, and it counts every targeted sensor (`sensors.targeted`), not only the hosts that have a row. It is given only when `sensors.targeted_exact` is true and the online state of every targeted sensor could be read; when it is absent, the number is not known (it is never sent as 0 for unknown). With `policy`, these are that policy's targeted hosts and sensors. Absent when the host count failed.
- An item whose only missing piece is a decoy [skipped on purpose](decoys.md#failed-decoys) has the requirement `decoy-skipped` and `skipped_sensors`; its note counts the skips apart from failed placements.
- Each item also has `sensors_verified`, `sensors_failed` (a current failure that is not a skip) and `sensors_skipped`: the sensors of its policy and template, from the same registry read. An organization-wide request, or one with `policy`, adds `sensors_targeted` and `sensors_targeted_exact`, the sensors the item's policy targets.
- An item with skipped sensors has `skipped_platforms`: its `sensors_skipped` counted by platform (`windows`, `linux`, `macos`). It uses the platform the sensor had when the skipped decoy was planned. A skip recorded before this field existed counts as `unknown` until the sensor's next attempt at the template. Use it to pick a template whose folder exists on those hosts.
- Each item with a `note` has `note_code` (the code of its first sentence) and `note_codes` (one code per sentence, in order), so a program never parses the sentence. A sentence can contain "; " itself, so do not split `note` to pair it with the codes. The codes are: `requirement_missing`, `context_only`, `source_quiet`, `source_note`, `file_events_unavailable`, `file_events_version_unknown`, `path_unavailable_in_release`, `pack_rule_broken`, `test_not_proven`, `decoys_placing`, `placements_failed`, `decoys_skipped`, `template_tag_missing`, `template_tag_partial`, `registry_capped` and `test_rule_off`. The [note table](#codes-notes-of-plan-deploy-test_fire-and-the-daily-run) says what each means.

- `coverage.tag_gaps` and `coverage.tag_check_note`: verified decoys on sensors that do not carry the template's tag yet (see [Coverage statuses](decoys.md#coverage-statuses)).
- `drops`: one row per token form in use (see [Testing and coverage](drops.md#testing-and-coverage)). A form that is not `active` has a `reason`: `check_failed` (its detection rules could not be checked), `drop_rule_broken`, `not_tested`, `test_not_detected`, `rule_edited` or `test_rule_off` (the form's latest test ran while the `deception-test` rule was missing or disabled: `unverified`, never `broken`). A `drop_rule_broken` or `rule_edited` row also has `rule`, the name of the drop rule to pass to [`restore_rules`](#restore_rules), and `rule_edited` (`true` or `false`, present whenever `rule` is): whether that rule's stored content differs from the shipped one.
- `sources`: what the organization sends.
- `metering`: `day` (the last completed UTC day), with that day's `covered_sensors` and `covered_sensors_distinct`, and `active_drops`, the number of active tokens counted when the request ran.
- `coverage.pack_check` and `coverage.pack_issues`: the [rule integrity](decoys.md#rule-integrity) result for the shipped detection rules (`checked_at`, `attempted_at`, and each rule that is missing, disabled or edited). Each issue always has `edited`, `true` or `false`: `true` when the stored rule's content (detect, respond and the rest of the rule) differs from the shipped one, including a disabled rule whose content was also changed: restoring it replaces that change. Enabling, disabling and the rule's tags, expiry or comment are not compared, so a rule that was only disabled is not edited.
- `alert_paths` (organization-wide requests) also has `alerting: {paths, touch, touch_alerting}`: `paths` is the alert paths that raise an alert now (active, or partial only because some hosts hold no decoy while at least one holds a verified decoy, or a working token form); `touch` is the paths whose detection tells a touch apart (the templates' read, modify and use paths and the token forms), and `touch_alerting` how many of them alert. With `touch_alerting` at 0, only a Delete can still alert. `not_proven` counts the paths whose latest test produced no detection while their rules and sources are fine; they are also counted as working, partial or skipped, and still alert.
- `verdict` (organization-wide requests): `state` is `working`, `gaps` or `not_alerting`, and `reasons` the [board's](board.md#one-verdict) reasons that decide it, in order, the same answer as the organization's board row. These reasons make it `not_alerting`: `alert_rule_off`, `no_alert_path_works`, `only_delete_alerts`. Every other reason makes it `gaps`: `alert_path_broken`, `drop_form_broken`, `pack_rule_broken`, `test_failing`, `respond_rule_off`, `test_rule_off`, `rule_edited`, `rule_unverified`, `rules_unchecked`, `paths_partial`, `not_configured`, `nothing_deployed`, `no_test_48h`, `tests_untested`, `tests_alert_rule_off`, `tests_test_rule_off`, `tests_old`, `tests_incomplete`, `templates_unavailable`, `source_quiet`, `rollout_incomplete`, `rollout_unknown`, `hosts_not_protected` and `hosts_unknown`. No reason: `working`. `reasons` never includes `deploy_in_progress`: a running rollout round never changes the verdict (it still appears in the board row's `status_reasons`). It includes `observe_mode` when a policy observes now, and that reason never changes `state` either.
- `observing`: the enabled policies in [observe mode](configuration.md#observe-mode) now, each `{policy, until}` (`until` absent when observe mode has no end); with `policy`, only that policy. `[]` when none. Their items say `observe: true` on the read, modify and delete layers.
- An item whose latest test produced no detection while every rule and source it needs is fine keeps its status, with note code `test_not_proven` and `not_proven`: `run_id`, `at`, and when known `sid` and `hostname` of the host the test ran on and `offline_now` (whether that host is offline now). See [Coverage statuses](decoys.md#coverage-statuses).
- An item whose latest test ran while the `deception-test` rule was missing or disabled keeps the status its other checks give it, with note code `test_rule_off`: that test proves nothing either way.
- `coverage.test_results_unread`: how many alert paths' latest test result this request could not read. Those paths are not marked `broken` by it.
- `coverage.time_to_protected_seconds`, per policy (only the requested policy's when you pass `policy`): the average time from the later of a sensor's enrollment and the policy's first recorded decoy to the sensor's first verified decoy, estimated from a bounded sample, when known.

Counts are read from the registry in bounded pages. When a registry is very large, the counts are lower bounds and the item's note says so. An organization-wide `coverage` also refreshes the organization's row on the [Deception board](board.md#the-deception-board).

## rollout_status

Read-only and cheap enough to poll: where the organization's [rollout](operations.md#rollouts) round stands as of its last pass, read from the extension's own record with no call to the platform. It takes no parameters and answers `deploy`, the same block `plan` returns: `in_progress` (a round is under way; its passes continue on their own) and `rollout` with the round's progress (the fields in [Rollouts](operations.md#rollouts)), absent when the organization never had a round.

```bash
limacharlie deception rollout-status --oid "$OID"
```

## restore_rules

Writes the current shipped version of each named shipped detection rule over your organization's record and enables it: the repair for a shipped rule that is disabled, missing, expired or edited (`coverage`'s rule issues, `plan`'s `pack`), `deception-respond` among them. It starts no rollout and places nothing; `deploy` with `apply_pack` writes the same and then deploys to the sensors. `rules` (required, at least one: `rules_required`) names the rules; an unknown name is refused (`unknown_pack_rule`), and the request is refused while an uninstall is in progress (`uninstalling`). Each rule is restored on its own, and the answer has one row per rule: `name`, `restored` (the shipped version was written), `enabled` (the record reads enabled afterwards), and `error` and `code` when it was not restored or could not be read back. The CLI command exits 1 unless every rule was restored and reads enabled.

Restoring replaces the whole record: any change you made to that rule (its detection, response, scopes, tags or expiry) is lost, even when the rule was only disabled. Check `edited` in `coverage`'s `pack_issues` (or `rule_edited` on a token form's row) before you restore a rule you may have changed.

```bash
limacharlie deception restore-rules --rule deception-respond --oid "$OID"
```

## list_test_paths

Read-only, paginated by template, policy and layer, then the token forms: one row per alert path of the enabled policies (and per token form in use) with its latest test result. A path `test_fire` tests is `passed`, `rule_off`, `test_rule_off`, `failed` or `untested`; an untested row says why (`test_decoy_placing`, `test_decoy_failed` with the sensor and cause, `test_not_run_yet`, or `not_tested` for a token form). A path it never tests is `not_testable` with its code: `layer_has_no_test` (a test never deletes its decoy), `path_not_testable` (the path cannot alert now; `status` says why) or `path_unavailable_in_release`. Filters: `policy`, `template`, `state` (`passed`, `rule_off`, `test_rule_off`, `failed`, `untested`, `not_testable`, or `testable` for all but `not_testable`).

The answer also has `counts` (the paths by state, `rule_off` and `test_rule_off` among them), `last_result_at`, `oldest_pass_at` (the oldest result among the passed paths), and `proven` with `not_proven`, the first reason that applies: `nothing_testable`, `test_failing`, `alert_rule_off`, `test_rule_off`, `results_unread`, `untested` or `results_old`. These are about the whole organization (or the policy given), whatever the `template` and `state` filters: proven when every testable path passed (its latest test raised its detection and its alert rule is on), the test rule is on, and every pass is within 48 hours.

- A row whose latest test raised no detection while the `deception-test` rule was missing or disabled reads `test_rule_off` (code `test_rule_off`; `last_result` keeps the outcome): the test could not pass, so it proves nothing either way, and it is never counted as `failed` or as a broken path (the [board](board.md#one-verdict) can lag until its row is recomputed). While the rule is off the answer has `test_rule_ok: false` and `test_rule`, no test is started (token form tests included), and `last_not_run` (`at`, `trigger`, `reason: test_rule_off`) records the latest test fire that started nothing for that reason, while it is newer than `last_run`. Restore the rule with [`restore_rules`](#restore_rules); the next test proves the path.

- A row of code `test_no_sensor_with_inventory` has `blockers`: the sensors the test decoy search looked at, by why none can take the test decoy: `offline`, `no_inventory` (no inventory from today), `restricted` (refused for its `acl:` tags), `directory_missing` (the test decoy placed there failed because the template's folder is not on the host), `refused` (the placement helper on the host refused it), `no_decoy` (the template places nothing there, or a test decoy placed there did not last, and the sensor holds no verified decoy of the template either) and `other` (the same, on a sensor that does hold a verified decoy of the template). When `no_decoy` could not be counted this time, it is absent and `other` includes those sensors.
- A `failed` row of a template's path has `last_result.sid` and `last_result.hostname`: the sensor of the test decoy the latest test ran on, where the detection did not come back. They are absent when that run or its test decoy is no longer kept, or could not be read this time.
- A row whose shipped alert rule is missing, disabled or broken has `alert_rule_ok: false` and `alert_rule`, the rule's name. A test's detection goes through the `deception-test` rule, so a test proves the sensor and the pipeline but not that rule. A test is not passed while the rule it relies on is off: a row whose shipped alert rule is missing or disabled and whose latest test raised its detection reads `rule_off` (code `alert_rule_off`), with `last_result` still showing the detection. An edited rule is not judged and never makes a row `rule_off`. It is counted in `counts.rule_off`, never in `passed`, and the organization is not proven (`not_proven: alert_rule_off`). A `failed` or `untested` row keeps its state. The `fleet_summary` row counts them in `tests.rule_off`, judged by the row's own rule check: after a rule is turned off or restored, the two agree once the row is recomputed. A rule check that fails marks nothing; the next request checks again. Fix it with [`restore_rules`](#restore_rules).
- `last_run`: the latest test fire that started runs, with `at` and `trigger` (`daily` for the daily run, `manual` for a `test_fire` request). `next_daily_test_at`: when the daily run is expected to test again, 24 hours after its last test (a time in the past means it is due). Both are absent until recorded.

```bash
limacharlie deception list-test-paths --state failed --oid "$OID"
```

## draft_drop_document

Read-only: the content a [document token](drops.md) would be generated with, as `create_drop` would generate it (a library template of the format, picked at random each call, filled from your organization's vocabulary). It takes `format` (`docx` or `svg`, required) and an optional `document` whose fields are checked as `create_drop` checks them and kept. The answer is `document` with `file_name`, `title`, `lines`, `link_text` and `author`. The web app fills its create form with it.

```bash
limacharlie deception drops draft-document --format docx --oid "$OID"
```

## list_kinds

Every decoy kind with its settings version and JSON schema, plus `library` (the default templates, built into the extension and shipped with each release), `benign_readers` (the [starter list of benign readers](configuration.md#starter-list-of-benign-readers)) and the record `schema_version`. Use it to write a valid template for a kind you have not used, including from an AI agent.

## uninstall_status

Read-only view of the [uninstall](operations.md#uninstalling-before-you-unsubscribe). Unlike `uninstall`, it never starts an uninstall, removes a decoy, deletes a rule, renews a lease or cancels anything, and it takes no parameters. It answers with `state` (`not_started`, `removing_decoys`, `removing_rules`, `done`, `cancelled` or `engine_unavailable`), `safe_to_unsubscribe`, a `message`, the `decoys` counts, `rules_kept`, `leftovers`, `tags_left`, `started_at` and, once done, `finished_at`. It needs no configuration.
