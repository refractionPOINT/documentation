# Skills Reference

`lc-compliance` exposes four Claude Code skills. All four follow the same framework-shorthand parsing convention and use `--oid` to target a specific LimaCharlie organization. None of the skills modify your organization without explicit confirmation; the two write-capable skills (`compliance-deploy`, `compliance-baseline-deploy`) prompt for confirmation at each platform write, and `compliance-baseline-deploy` additionally requires `--apply` to leave dry-run mode.

## Framework shorthand parsing

All four skills accept the same framework aliases as the first positional argument:

| Input | Resolved |
|---|---|
| `pci`, `pci-dss` | pci-dss |
| `nist`, `800-53`, `nist-800-53` | nist-800-53 |
| `cmmc` | cmmc |
| `hipaa` | hipaa |
| `soc2` | soc2 |
| `iso`, `iso-27001` | iso-27001 |
| `cis`, `cis-v8` | cis-v8 |

If a framework cannot be parsed from the input, the skill prompts the user to clarify.

## `compliance-lookup`

Look up how LimaCharlie covers a specific compliance control. Returns the control's conceptual coverage (from the framework's mapping document) plus the specific deployable rules that cite it (from the framework's implementation document). Read-only — does not contact your LimaCharlie organization.

### Syntax

```text
/lc-compliance:compliance-lookup <framework> <control-id>
```

### Arguments

| Argument | Required | Notes |
|---|---|---|
| `<framework>` | Yes | One of the framework shorthand values above. May be inferred from the control ID format if unambiguous (e.g., `CC6.1` → SOC 2, `§164.312` → HIPAA, `AU-2` → NIST 800-53). |
| `<control-id>` | Yes | Citation in the format the framework uses. See [Frameworks](frameworks.md) for per-framework citation formats. |

### Examples

```text
/lc-compliance:compliance-lookup pci 10.2.1.4
/lc-compliance:compliance-lookup nist AU-2
/lc-compliance:compliance-lookup cmmc AU.L2-3.3.1
/lc-compliance:compliance-lookup hipaa §164.312(b)
/lc-compliance:compliance-lookup soc2 CC6.1
/lc-compliance:compliance-lookup iso A.8.15
/lc-compliance:compliance-lookup cis 8.2
```

### Output

A markdown block in your chat containing:

- The framework name and citation
- The framework's verification level (MACHINE_VERIFIED / ATTESTATION / UNVERIFIED)
- A verbatim quote of the conceptual coverage from the framework's mapping document
- A table listing every deployable rule whose metadata cites this control ID, with the rule name, the LimaCharlie event type it triggers on, and a one-line summary
- Pointers to the bundled source files

If the control ID is not present in the bundled mapping or implementation document, the skill reports that explicitly rather than fabricating a response.

### When to use

- Answering a targeted "how does LC cover control X?" question from an auditor, engineer, or security lead
- Verifying that a specific control citation has deployable rules behind it before referencing the citation in a design document
- Inspecting which rule names you would expect to see in the org for a given control

If the question is broader — "what am I missing for this whole framework?" — use [`compliance-gap`](#compliance-gap) instead.

## `compliance-gap`

Run an ad-hoc gap analysis against a live LimaCharlie organization. Compares what the org is currently collecting and detecting against the framework's recommended rule set, and returns a markdown punch list directly in chat. No case is created; nothing is written to the org.

### Syntax

```text
/lc-compliance:compliance-gap <framework> [--oid <oid>] [--baseline <level>] [--ig <group>]
```

### Arguments

| Argument | Required | Notes |
|---|---|---|
| `<framework>` | Yes | Framework shorthand. |
| `--oid <oid>` | No | Target organization UUID. Defaults to the CLI's currently-selected org. |
| `--baseline <low\|moderate\|high>` | No | NIST 800-53 only. Scopes analysis to the named FIPS 199 baseline. No hard-coded default — omit to evaluate all bundled controls. |
| `--ig <1\|2\|3>` | No | CIS v8 only. Scopes analysis to safeguards in the named Implementation Group. No hard-coded default — omit to evaluate all bundled safeguards (the skill will also honour `cis-ig1`/`cis-ig2`/`cis-ig3` tags on sensors if set). |

### Output

A markdown gap report with these sections:

- **Summary** — counts of telemetry / artifact / FIM / D&R / sensor-coverage gaps
- **Telemetry (Exfil) Gaps** — events the framework expects that are not in the org's exfil profile, broken down by platform
- **Artifact Collection Gaps** — artifact-collection rules from the recommended baseline that are not deployed
- **FIM Gaps** — file-integrity-monitoring rules that are not deployed (and whether `ext-integrity` is even subscribed)
- **D&R Rule Gaps** — recommended D&R rule names that are not deployed in the org
- **Sensor-Coverage Issues** — in-scope sensors that have gone offline beyond the framework's expected retention window
- **Name-Drift Candidates** — deployed rules whose names are close to but not identical to a recommended name (manual review)
- **Deployed Extras** — rules deployed in the org that are not part of the recommended baseline (informational, never flagged as a gap)
- **Prioritized Remediation** — a short, ordered punch list

The report is informational only. Nothing is written to the LC org. See [Gap Analysis](gap-analysis.md) for how to read and act on the output.

!!! info "Persisting a gap report"
    If you want a gap report stored in the LC org for auditors to reference, create a [Case](../../5-integrations/extensions/limacharlie/cases.md) yourself and paste the skill's output into a case note. This separation is deliberate — gap reports are engineering punch lists, not audit evidence.

## `compliance-deploy`

Guided deployment of a framework's case-reviewer agent to a LimaCharlie organization. Human-in-the-loop at each sensitive step (API-key creation, secret staging, agent hive sync, trigger D&R rule installation). Does not silently modify the org.

### Syntax

```text
/lc-compliance:compliance-deploy <framework> [--oid <oid>] [--with-rules]
```

### Arguments

| Argument | Required | Notes |
|---|---|---|
| `<framework>` | Yes | Framework shorthand. |
| `--oid <oid>` | No | Target organization UUID. Defaults to the CLI's currently-selected org. |
| `--with-rules` | No | Also deploy a small starter rule subset (5–10 representative rules across D&R / FIM / artifact / exfil). Useful for demos. **For the full baseline, use [`compliance-baseline-deploy`](#compliance-baseline-deploy) instead.** |

### What it does

The skill walks through these steps, asking for confirmation before each platform write:

1. **Pre-flight checks** — verifies `ext-cases` is subscribed on the target org, that the framework's bundled assets are accessible, and that an Anthropic key is staged or available to stage.
2. **API-key creation** — creates a scoped LimaCharlie API key for the reviewer agent, with the minimum permissions needed (typically `org.get`, `sensor.list`, `sensor.get`, `dr.list`, `insight.det.get`, `insight.evt.get`, `investigation.get`, `investigation.set`, `ext.request`, `ext.list`, `org_notes.read`, `sop.get`, `sop.get.mtd`, `ai_agent.operate`).
3. **Anthropic secret staging** — captures or stages the Anthropic key into a [Hive Secret](../../7-administration/config-hive/secrets.md).
4. **Agent hive sync** — pushes the reviewer manifest (`ai_agent` record) and its trigger rule (`dr-general` record) into the org.
5. **Verification** — reads the resulting hive records back to confirm the deploy succeeded and reports the agent identifier for follow-up.

The skill does not deploy the framework's full rule baseline. To do that as a follow-up step, use [`compliance-baseline-deploy`](#compliance-baseline-deploy).

See [Case-Reviewer Agent](case-reviewer-agent.md) for the runtime behavior of the deployed agent.

## `compliance-baseline-deploy`

Deploy the FULL recommended rule baseline for a compliance framework — every D&R rule, FIM rule, artifact-collection rule, and exfil rule defined in the framework's implementation document. Defaults to a dry-run plan; `--apply` is required to actually write to the organization. Idempotent: rules already present under the same name are skipped.

### Syntax

```text
/lc-compliance:compliance-baseline-deploy <framework> [--oid <oid>] [--apply] [--overwrite] [--kinds <list>]
```

### Arguments

| Argument | Required | Notes |
|---|---|---|
| `<framework>` | Yes | Framework shorthand. |
| `--oid <oid>` | No | Target organization UUID. Defaults to the CLI's currently-selected org. |
| `--apply` | No | Required to leave dry-run mode and write rules to the org. Without this flag, the skill prints the deployment plan and exits. |
| `--overwrite` | No | Replace rules already deployed under the same name with the bundled definitions. Without this flag, existing rules are skipped (idempotent). |
| `--kinds <list>` | No | Comma-separated subset of rule kinds to deploy. Valid values: `dr`, `fim`, `artifact`, `exfil`. Defaults to all four. |

### Typical usage

A two-pass workflow is recommended:

```text
# First pass — preview the deployment plan
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid>

# Review the plan with stakeholders, then apply
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply
```

For partial deployments (e.g., only file-integrity rules, deferring D&R rules until after a SOC review):

```text
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply --kinds fim
```

To re-sync a previously-deployed baseline after a plugin update, picking up only new rules:

```text
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply
```

To force-replace existing rules with updated definitions:

```text
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply --overwrite
```

### What it does not do

`compliance-baseline-deploy` does not:

- Deploy the case-reviewer agent. Use [`compliance-deploy`](#compliance-deploy) for that.
- Subscribe to extensions. If `ext-integrity` (file-integrity monitoring) or `ext-cases` (case management) are not subscribed, the skill reports the dependency and prompts you to subscribe before continuing.
- Tag sensors. In-scope-sensor tagging (e.g., `cde` for PCI) is a separate operational decision that the skill does not make for you. See [Sensor Tags](../../2-sensors-deployment/sensor-tags.md).

## Permission and credential model

All four skills inherit their LimaCharlie credentials from your existing CLI session — there is no separate authentication step for the plugin. The skills shell out to the `limacharlie` CLI for org operations, which uses the same API key resolution as your interactive CLI work.

For the case-reviewer agent deployed by `compliance-deploy`, a dedicated scoped API key is created inside the target organization (not shared with your interactive CLI key). The agent uses that scoped key plus an Anthropic secret to operate; see [Case-Reviewer Agent](case-reviewer-agent.md#permissions).

## See also

- [Frameworks](frameworks.md) — per-framework citation formats and recommended scope tags
- [Case-Reviewer Agent](case-reviewer-agent.md) — runtime behavior of the deployed reviewer
- [Gap Analysis](gap-analysis.md) — how to read and act on `compliance-gap` output
- [Hive Secrets](../../7-administration/config-hive/secrets.md) — where the Anthropic and LC API keys are stored
