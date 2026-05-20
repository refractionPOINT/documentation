# Compliance

LimaCharlie ships a compliance toolkit, **`lc-compliance`**, that maps seven major compliance frameworks directly onto your deployed sensors, detections, and case queue. It is delivered as a Claude Code plugin sourced from the public [`refractionPOINT/lc-ai`](https://github.com/refractionPOINT/lc-ai) marketplace, and is licensed under Apache 2.0.

The toolkit has two complementary halves that solve different parts of the compliance problem:

- A **case-reviewer agent** that runs continuously inside your LimaCharlie organization, classifying every new case against the relevant control citations and writing audit-grade documentation directly into the case record. Built on [AI Sessions](../index.md).
- A set of **four Claude Code skills** that an engineer runs on demand from their Claude Code session: control lookups, ad-hoc gap analysis, guided agent deployment, and full rule-baseline deployment.

The continuous half produces durable audit evidence. The on-demand half supports the engineering work that surrounds an audit — answering "how does LC cover this control?", "what am I missing before the audit?", and "deploy the recommended rule set to this new tenant."

## Frameworks covered

| Framework | Authoritative source |
|---|---|
| **CMMC v2** | NIST SP 800-171 Rev 2 |
| **NIST SP 800-53 Rev 5** | NIST OSCAL catalog |
| **PCI DSS v4.0** | PCI Security Standards Council |
| **HIPAA Security Rule** | eCFR 45 CFR §164 |
| **SOC 2** | AICPA Trust Services Criteria |
| **ISO/IEC 27001:2022** | ISO (Annex A) |
| **CIS Critical Security Controls v8** | Center for Internet Security |

Each framework ships with a control-to-capability mapping document, a set of deployable D&R / file-integrity / artifact-collection / exfil rules across Windows, Linux, and macOS, a recommended-rules baseline used by the gap-analysis skill, an attribution document declaring the verification level, and a case-reviewer agent manifest ready to deploy. See [Frameworks](frameworks.md).

## The two shapes — when to use which

| Use case | Shape |
|---|---|
| Continuous per-case compliance classification | **Agent** (`<framework>-compliance-reviewer`) — fires on every `case_created` |
| Ad-hoc "what does LC do for this one control?" | **Skill** (`compliance-lookup`) |
| Ad-hoc "what am I missing?" before an audit | **Skill** (`compliance-gap`) |
| First-time reviewer-agent deployment | **Skill** (`compliance-deploy`) |
| Push the full framework rule baseline into an org | **Skill** (`compliance-baseline-deploy`) |

The agent owns continuous, event-driven evidence production — cases, notes, tags persisted in the LC org that auditors rely on. Skills own request-driven interactive work that engineers run during development without leaving artifacts behind in the org.

!!! info "Gap analysis is skill-only"
    There is no backend gap-analyzer agent. A gap report is an engineering punch list, not audit evidence. If you want the report persisted in the LC org for an auditor to reference, create a [Case](../../5-integrations/extensions/limacharlie/cases.md) yourself and paste the skill's output into it.

## Quickstart

```text
/plugin marketplace add https://github.com/refractionPOINT/lc-ai
/plugin install lc-compliance@lc-marketplace
```

Once installed, the four skills are immediately available:

```text
/lc-compliance:compliance-lookup pci 10.2.1.4
/lc-compliance:compliance-gap hipaa --oid <your-oid>
/lc-compliance:compliance-deploy cmmc --oid <your-oid>
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply
```

For a step-by-step walkthrough of the first three commands, see [Installation](installation.md). For arguments and behavior of each skill, see [Skills Reference](skills.md). To deploy the case-reviewer agent into an organization, see [Case-Reviewer Agent](case-reviewer-agent.md).

## What `lc-compliance` does not do

- **Issue compliance attestations.** The plugin reports evidence. The human auditor / QSA / ISSO decides compliance status.
- **Modify deployed configuration without confirmation.** Every write (API key creation, secret staging, rule deployment) requires explicit confirmation. `compliance-baseline-deploy` defaults to a dry-run; `--apply` is required to write rules.
- **Replace your SOC.** The case-reviewer agent runs in parallel to whatever Level-1 triage flow already exists in the organization, classifying for compliance impact, not security severity. It does not contain, isolate, or remediate.
- **Provide normative control wording.** Mappings paraphrase. The normative text of each standard lives in the publisher's document, linked in every framework's attribution document.

## See also

- [AI Sessions](../index.md) — the underlying mechanism the case-reviewer agent runs on
- [Cases](../../5-integrations/extensions/limacharlie/cases.md) — the case lifecycle the agent operates against
- [D&R-Driven Sessions](../dr-sessions.md) — how the case-reviewer agent is triggered
- [Hive Secrets](../../7-administration/config-hive/secrets.md) — where the agent's API keys are stored
