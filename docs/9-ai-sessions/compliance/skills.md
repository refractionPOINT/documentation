# Skills Reference

`lc-compliance` supplies four Claude Code skills. All four parse framework shorthand in the same way, and all four use `--oid` to select one LimaCharlie organization. No skill changes your organization without your confirmation. The two skills that can write (`compliance-deploy` and `compliance-baseline-deploy`) ask for confirmation at each write to the platform. `compliance-baseline-deploy` also needs `--apply` to leave dry-run mode.

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

If the skill cannot parse a framework from the input, it asks you to clarify.

## `compliance-lookup`

Look up how LimaCharlie covers one compliance control. The skill returns the conceptual coverage of the control, from the mapping document of the framework. It also returns the deployable rules that cite the control, from the implementation document of the framework. The skill is read-only. It does not contact your LimaCharlie organization.

### Syntax

```text
/lc-compliance:compliance-lookup <framework> <control-id>
```

### Arguments

| Argument | Required | Notes |
|---|---|---|
| `<framework>` | Yes | One of the framework shorthand values above. The skill can infer it from the format of the control ID if the format is unambiguous (e.g., `CC6.1` → SOC 2, `§164.312` → HIPAA, `AU-2` → NIST 800-53). |
| `<control-id>` | Yes | Citation in the format that the framework uses. See [Frameworks](frameworks.md) for the citation format of each framework. |

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

A markdown block in your chat. The block contains:

- The framework name and the citation
- The verification level of the framework (MACHINE_VERIFIED / ATTESTATION / UNVERIFIED)
- A verbatim quote of the conceptual coverage from the mapping document of the framework
- A table of every deployable rule whose metadata cites this control ID. The table gives the rule name, the LimaCharlie event type that triggers the rule, and a one-line summary
- Pointers to the bundled source files

If the control ID is not in the bundled mapping document or the bundled implementation document, the skill reports this. It does not fabricate a response.

### When to use

- Answer a targeted "how does LC cover control X?" question from an auditor, an engineer, or a security lead
- Check that a control citation has deployable rules behind it before you use the citation in a design document
- See which rule names to expect in the organization for one control

If the question is broader — "what am I missing for this whole framework?" — use [`compliance-gap`](#compliance-gap) instead.

## `compliance-gap`

Run an ad-hoc gap analysis against a live LimaCharlie organization. The skill compares what the organization collects and detects with the recommended rule set of the framework. It returns a markdown punch list in the chat. The skill creates no case and writes nothing to the organization.

### Syntax

```text
/lc-compliance:compliance-gap <framework> [--oid <oid>] [--baseline <level>] [--ig <group>]
```

### Arguments

| Argument | Required | Notes |
|---|---|---|
| `<framework>` | Yes | Framework shorthand. |
| `--oid <oid>` | No | Target organization UUID. Defaults to the organization that the CLI selects. |
| `--baseline <low\|moderate\|high>` | No | NIST 800-53 only. Limits the analysis to the named FIPS 199 baseline. There is no hard-coded default. Omit the flag to evaluate all bundled controls. |
| `--ig <1\|2\|3>` | No | CIS v8 only. Limits the analysis to the safeguards in the named Implementation Group. There is no hard-coded default. Omit the flag to evaluate all bundled safeguards. The skill also obeys the `cis-ig1`, `cis-ig2`, and `cis-ig3` tags on sensors if you set them. |

### Output

A markdown gap report with these sections:

- **Summary** — counts of telemetry / artifact / FIM / D&R / sensor-coverage gaps
- **Telemetry (Exfil) Gaps** — events that the framework expects but that are not in the exfil profile of the organization, listed by platform
- **Artifact Collection Gaps** — artifact-collection rules from the recommended baseline that are not deployed
- **FIM Gaps** — file-integrity-monitoring rules that are not deployed, and if `ext-integrity` is subscribed
- **D&R Rule Gaps** — recommended D&R rule names that are not deployed in the organization
- **Sensor-Coverage Issues** — in-scope sensors that are offline for longer than the retention window that the framework expects
- **Name-Drift Candidates** — deployed rules whose names are close to a recommended name but not identical to it (manual review)
- **Deployed Extras** — rules deployed in the organization that are not part of the recommended baseline. These are informational and are never flagged as a gap
- **Prioritized Remediation** — a short, ordered punch list

The report is informational only. The skill writes nothing to the LC organization. See [Gap Analysis](gap-analysis.md) to learn how to read the output and act on it.

!!! info "Persisting a gap report"
    To keep a gap report in the LC organization for auditors, create a [Case](../../5-integrations/extensions/limacharlie/cases.md) yourself and paste the output of the skill into a case note. This separation is deliberate. Gap reports are engineering punch lists, not audit evidence.

## `compliance-deploy`

Guided deployment of the case-reviewer agent of a framework to a LimaCharlie organization. A human confirms each sensitive step: creation of the API key, staging of the secret, sync of the agent hive, and installation of the trigger D&R rule. The skill does not change the organization silently.

### Syntax

```text
/lc-compliance:compliance-deploy <framework> [--oid <oid>] [--with-rules]
```

### Arguments

| Argument | Required | Notes |
|---|---|---|
| `<framework>` | Yes | Framework shorthand. |
| `--oid <oid>` | No | Target organization UUID. Defaults to the organization that the CLI selects. |
| `--with-rules` | No | Also deploy a small starter subset of rules (5–10 representative rules across D&R / FIM / artifact / exfil). Useful for demonstrations. **For the full baseline, use [`compliance-baseline-deploy`](#compliance-baseline-deploy) instead.** |

### What it does

The skill does these steps. It asks for confirmation before each write to the platform:

1. **Pre-flight checks** — checks that `ext-cases` is subscribed on the target organization, that the bundled assets of the framework are accessible, and that an Anthropic key is staged or ready to stage.
2. **API-key creation** — creates a scoped LimaCharlie API key for the reviewer agent. The key holds the minimum permissions needed (usually `org.get`, `sensor.list`, `sensor.get`, `dr.list`, `insight.det.get`, `insight.evt.get`, `investigation.get`, `investigation.set`, `ext.request`, `ext.list`, `org_notes.read`, `sop.get`, `sop.get.mtd`, `ai_agent.operate`).
3. **Anthropic secret staging** — captures or stages the Anthropic key in a [Hive Secret](../../7-administration/config-hive/secrets.md).
4. **Agent hive sync** — pushes the reviewer manifest (`ai_agent` record) and its trigger rule (`dr-general` record) into the organization.
5. **Verification** — reads the hive records back to confirm that the deploy succeeded, and reports the agent identifier for later use.

The skill does not deploy the full rule baseline of the framework. To do this as a later step, use [`compliance-baseline-deploy`](#compliance-baseline-deploy).

See [Case-Reviewer Agent](case-reviewer-agent.md) for the runtime behavior of the deployed agent.

## `compliance-baseline-deploy`

Deploy the FULL recommended rule baseline for a compliance framework. This includes every D&R rule, FIM rule, artifact-collection rule, and exfil rule in the implementation document of the framework. The default is a dry-run plan. `--apply` is necessary to write to the organization. The skill is idempotent: it skips rules that are already present under the same name.

### Syntax

```text
/lc-compliance:compliance-baseline-deploy <framework> [--oid <oid>] [--apply] [--overwrite] [--kinds <list>]
```

### Arguments

| Argument | Required | Notes |
|---|---|---|
| `<framework>` | Yes | Framework shorthand. |
| `--oid <oid>` | No | Target organization UUID. Defaults to the organization that the CLI selects. |
| `--apply` | No | Necessary to leave dry-run mode and write rules to the organization. Without this flag, the skill prints the deployment plan and stops. |
| `--overwrite` | No | Replace rules that are already deployed under the same name with the bundled definitions. Without this flag, the skill skips existing rules (idempotent). |
| `--kinds <list>` | No | Comma-separated subset of rule kinds to deploy. Valid values: `dr`, `fim`, `artifact`, `exfil`. Defaults to all four. |

### Typical usage

Use a workflow with two passes:

```text
# First pass — preview the deployment plan
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid>

# Review the plan with stakeholders, then apply
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply
```

For partial deployments (for example, only file-integrity rules, with D&R rules deferred until after a SOC review):

```text
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply --kinds fim
```

After a plugin update, re-sync a baseline that you deployed before. This adds only the new rules:

```text
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply
```

To replace existing rules with updated definitions:

```text
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply --overwrite
```

### What it does not do

`compliance-baseline-deploy` does not:

- Deploy the case-reviewer agent. Use [`compliance-deploy`](#compliance-deploy) for that.
- Subscribe to extensions. If `ext-integrity` (file-integrity monitoring) or `ext-cases` (case management) are not subscribed, the skill reports the dependency and asks you to subscribe before it continues.
- Tag sensors. To tag the in-scope sensors (for example, `cde` for PCI) is a separate operational decision. The skill does not make that decision for you. See [Sensor Tags](../../2-sensors-deployment/sensor-tags.md).

## Permission and credential model

All four skills take their LimaCharlie credentials from your CLI session. The plugin has no separate authentication step. The skills call the `limacharlie` CLI for operations on the organization. The CLI resolves the API key in the same way as it does for your interactive CLI work.

`compliance-deploy` creates a dedicated scoped API key inside the target organization for the case-reviewer agent. This key is not shared with your interactive CLI key. The agent operates with that scoped key and an Anthropic secret. See [Case-Reviewer Agent](case-reviewer-agent.md#permissions).

## See also

- [Frameworks](frameworks.md) — citation formats and recommended scope tags for each framework
- [Case-Reviewer Agent](case-reviewer-agent.md) — runtime behavior of the deployed reviewer
- [Gap Analysis](gap-analysis.md) — how to read `compliance-gap` output and act on it
- [Hive Secrets](../../7-administration/config-hive/secrets.md) — where the Anthropic and LC API keys are stored
