# Code rules

Static analysis runs **exactly your organization's enabled code rules** — nothing
else. They are records in the `cloudsec_code_rule` Hive, and LimaCharlie's rules
are records there too: there is no hidden built-in pack and no separate override
layer. What the Hive holds is what a scan runs. The [scan policy](policy.md)
decides whether static analysis runs on a repository; code rules decide what it
looks for.

In the console they are under **Cloud Security → Policies → Code rules**: search
and filter by language, severity, source, tag and status, turn records on and off,
and create, edit (as YAML or JSON) or delete them. Reading them needs
`cloudsec.get`; changing them needs `cloudsec.set`.

## The default rules

When the organization subscribes to `ext-cloud-security`, LimaCharlie installs its
default rule set: its own rules, and a licence-filtered subset of GitLab's
open-source [sast-rules](https://gitlab.com/gitlab-org/security-products/sast-rules).
Each rule is its own record, so each can be switched off or deleted on its own:

- the record key is the rule id, e.g. `lc.python.cwe-295.tls-verify-disabled` for
  a LimaCharlie rule or `go_crypto_rule-tlsversion` for a third-party one;
- tags name the source (`limacharlie` or `gitlab-sast-rules`) and the language;
- a third-party rule's `metadata` carries its licence (`license`,
  `license_notice`, the full `license_text`) and the pinned upstream `source_url`.

After that they are **your records**. Edit, disable or delete any of them,
LimaCharlie's included. Installing is create-only: a record whose key already
exists is never overwritten, and nothing puts back a rule you deleted until you
ask for it.

**Restore defaults** (on the Code rules page) asks for that. The button appears
only for users who have **both** `cloudsec.set` and `ext.request`.

- By default it only **re-creates default rules that are missing**. Existing
  records, including defaults you edited or disabled, stay as they are.
- With **Also reset existing default rules to the shipped content**, default-keyed
  records that LimaCharlie installed are also rewritten to its rule, enabled state,
  tags and comment (`acl:` tags are kept). Your edits to those records are lost.
  A default-keyed record that you created yourself, for example by deleting a
  default and saving a record under the same key, cannot be reset: it is reported
  as failed. Delete it and restore again to get LimaCharlie's version back.

Records whose key is not a default key are never touched either way, and running it
again is safe. The same action is available outside the console:

```bash
limacharlie extension request --name ext-cloud-security \
  --action restore_default_code_rules --data '{"overwrite": false}'
```

It answers with the `total`, `created`, `overwritten`, `skipped` and `failed`
counts, plus a `failures` list of `{key, error}` for the records that could not
be written. The list holds at most 50 entries; `failed` is the full count.

!!! warning "Restoring is authorized by `ext.request`, not `cloudsec.set`"
    The extension writes the records with its own credentials. Anyone who may make
    extension requests on the organization can re-create deleted defaults and, with
    `overwrite`, reset edited or disabled ones, and resource ACL tags are not checked
    against the caller. Grant `ext.request` accordingly.

## Writing a rule

A record is one Semgrep/Opengrep rule **file**, stored as its JSON equivalent:
`{"rules": [ ... ]}`, exactly what the YAML `rules:` document parses to. A record
may hold up to 100 rules; use one rule per record when you want to turn rules on
and off individually.

```yaml
# requests-timeout.yaml
rules:
  - id: acme.python.requests-without-timeout
    languages: [python]
    severity: MEDIUM
    message: >-
      This HTTP request has no timeout, so a slow or unresponsive server can hang
      the worker indefinitely. Pass timeout=<seconds>.
    metadata:
      cwe: "CWE-400"
      category: security
    patterns:
      - pattern: requests.$METHOD(...)
      - pattern-not: requests.$METHOD(..., timeout=$T, ...)
      - metavariable-regex:
          metavariable: $METHOD
          regex: ^(get|post|put|patch|delete|head|request)$
```

```bash
limacharlie hive set --hive-name cloudsec_code_rule \
    --key acme.python.requests-without-timeout \
    --input-file requests-timeout.yaml --enabled --tag-add acme
```

The YAML file is taken as-is and stored as JSON. Pass `--enabled`: a new record is
disabled unless you say otherwise, and a disabled record does not run. The rest is
the standard Hive surface — `limacharlie hive list`, `get`, `enable`, `disable`,
`delete` and `validate` with `--hive-name cloudsec_code_rule`, or the
`/v1/hive/cloudsec_code_rule/<oid>/<key>` REST routes. Like the other `cloudsec_*`
Hives, it is not walked by `limacharlie sync`.

A record is checked when you save it, and a rule that cannot run is rejected with
an error naming it:

| Field | Requirement |
|---|---|
| `id` | Required. Letters, digits, `.`, `_` and `-`, at most 256 characters, unique within the record. It is the finding's rule id. |
| `message` | Required, non-empty. |
| `severity` | Required: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, or the older `ERROR`, `WARNING`, `INFO`, in any case. `ERROR` files a `HIGH` finding, `WARNING` a `MEDIUM` one, `INFO` an `INFO` one. `EXPERIMENT` and `INVENTORY` are refused because they never report. |
| `languages` | Required, non-empty. Each a language name the engine accepts, including its aliases (`js`, `py`, `golang`, `tf`, …) and `generic` / `regex` for language-independent rules. |
| matcher | **Exactly one** of `pattern`, `patterns`, `pattern-either`, `pattern-regex` or `match`; or `mode: taint` with non-empty `pattern-sources` and `pattern-sinks`; or a `taint:` block with `sources` and `sinks`. Mixing them is refused, because the engine would silently ignore one side. `mode` is `search` (the default) or `taint`. |
| `metadata`, `options`, `paths`, `fix` | Optional. `metadata` and `options` are objects, `paths` takes only `include` / `exclude` lists, and `fix` is a string. Every other key the engine understands is stored and passed through untouched. |

A record is at most **256 KB** of JSON; split larger rule files across records.

Saving checks structure, not whether a pattern parses for its language — only the
engine can tell that. A rule that fails to load at scan time is reported by name and
skipped, and every other rule still runs (see
[When rules cannot run](#when-rules-cannot-run)). A rule id that an earlier record
(by key order) already uses is skipped the same way, so keep ids unique across the
organization.

Changes apply to scans that start about a minute after the save. A rule change does
not rescan anything by itself; rescan the repository (**Rescan now**, or `limacharlie cloudsec code rescan <owner>/<name>`) to see its effect
immediately.

## Limits on the rule set

| Limit | Value |
|---|---|
| Rules per record | 100 |
| Record size | 256 KB of JSON |
| Enabled rules per organization | 5,000 |
| Enabled rule JSON per organization | 20 MB |

Above either organization limit the **whole set is refused**, never an arbitrary
subset, and static analysis does not run until you disable rules.

## When rules cannot run

A problem with the rule set affects **static analysis only**. The repository reads
`scan_status: partial` and carries the reason in `scan_limits`; its existing
`code_weakness` findings are kept rather than closed, and its dependency, secret,
infrastructure and license findings are complete and still close normally.

| Reason | Meaning | What to do |
|---|---|---|
| `sast_no_rules` | No code rule is enabled, so static analysis ran no rules. | Enable rules, or **Restore defaults**. |
| `sast_rules_over_cap:rules` / `sast_rules_over_cap:bytes` | More than 5,000 rules, or more than 20 MB of rules, are enabled. Static analysis did not run. | Disable rules. |
| `sast_rule_errors` | Static analysis ran, but some rules failed to load and were skipped. | Fix or disable the named rules. |
| `sast_rules_unavailable` (optionally `:<step>`) | The rule set could not be prepared for this scan. | Nothing; the next scan retries. |
| `sast_rules_hive_unavailable` | This deployment cannot read code rules yet. | Nothing; it is fixed on LimaCharlie's side. |

The rules that failed are listed by record key, rule id and the engine's error. On
the **Code security** page, a repository's **Details** drawer lists them, each
linking to its record in Code rules. In the API and `limacharlie cloudsec code repos` output, a repository
that static analysis covered also carries:

| Field | Meaning |
|---|---|
| `sast_rules_sha256` | The digest of the rule set the scan ran. |
| `sast_rules_count` | How many rules that set held. |
| `sast_rule_errors` | The rules that failed to load: `{record_key, rule_id, message}`. `rule_id` is empty when the record itself is not a rule file. |
| `sast_rule_errors_total` | The exact number of failed rules. The list may be shorter. |

## Pull-request checks

A pull-request check uses **one** rule set for both commits, taken when the check
starts, so a rule added in the meantime cannot make existing code look new.

- **No enabled code rules, or the same rules failing to load on both commits.**
  The check's conclusion is unchanged. Its summary adds one line saying what
  static analysis did not examine, such as *"Static analysis ran no rules: this
  organization has no enabled code rules."* or *"2 code rule(s) failed to load and
  were not run on either commit …"*.
- **Rules that could not be used at all** (over the
  [organization limits](#limits-on-the-rule-set), not available for the scan, or
  every enabled record unusable), **or different rules failing on the two commits.**
  The check is incomplete: code weaknesses are left out of the comparison, so none
  can fail the check, and a check with no other new finding concludes `neutral`,
  never `success`. New findings of other classes still count and can still fail
  `gating.fail_on`.

See [What the check says](pull-requests.md#what-the-check-says).

## Local scans

Local scans never apply your organization's code rules. See
[Scan locally or in CI](bring-your-own-scanner.md#scan-locally-or-in-ci) for which
rules they run.
