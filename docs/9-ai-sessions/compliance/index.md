# Compliance

LimaCharlie supplies a compliance toolkit, **`lc-compliance`**, that maps seven major compliance frameworks onto your deployed sensors, detections, and case queue. The toolkit is a Claude Code plugin from the public [`refractionPOINT/lc-ai`](https://github.com/refractionPOINT/lc-ai) marketplace. Its license is Apache 2.0.

The toolkit has two complementary halves that solve different parts of the compliance problem:

- A **case-reviewer agent** that runs continuously inside your LimaCharlie organization. It classifies each new case against the relevant control citations and writes audit-grade documentation into the case record. The agent is built on [AI Sessions](../index.md).
- A set of **four Claude Code skills** that an engineer runs on demand from a Claude Code session: control lookups, ad-hoc gap analysis, guided agent deployment, and full rule-baseline deployment.

The continuous half produces durable audit evidence. The on-demand half supports the engineering work around an audit. It answers questions such as "how does LC cover this control?" and "what am I missing before the audit?", and it does tasks such as "deploy the recommended rule set to this new tenant."

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

Each framework comes with these items:

- a document that maps controls to capabilities
- a set of deployable D&R, file-integrity, artifact-collection, and exfil rules for Windows, Linux, and macOS
- a baseline of recommended rules that the gap-analysis skill uses
- an attribution document that declares the verification level
- a case-reviewer agent manifest that is ready to deploy

See [Frameworks](frameworks.md).

## The two shapes — when to use which

| Use case | Shape |
|---|---|
| Continuous per-case compliance classification | **Agent** (`<framework>-compliance-reviewer`) — fires on every `case_created` |
| Ad-hoc "what does LC do for this one control?" | **Skill** (`compliance-lookup`) |
| Ad-hoc "what am I missing?" before an audit | **Skill** (`compliance-gap`) |
| First-time reviewer-agent deployment | **Skill** (`compliance-deploy`) |
| Push the full framework rule baseline into an org | **Skill** (`compliance-baseline-deploy`) |

The agent produces continuous, event-driven evidence: the cases, notes, and tags that stay in the LC organization for auditors. The skills do interactive work on request. Engineers run the skills during development, and the skills leave no artifacts in the organization.

!!! info "Gap analysis is skill-only"
    There is no gap-analyzer agent in the cloud. A gap report is an engineering punch list, not audit evidence. To keep the report in the LC organization for an auditor, create a [Case](../../5-integrations/extensions/limacharlie/cases.md) and paste the output of the skill into it.

## Quickstart

```text
/plugin marketplace add https://github.com/refractionPOINT/lc-ai
/plugin install lc-compliance@lc-marketplace
```

After the installation, the four skills are available:

```text
/lc-compliance:compliance-lookup pci 10.2.1.4
/lc-compliance:compliance-gap hipaa --oid <your-oid>
/lc-compliance:compliance-deploy cmmc --oid <your-oid>
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply
```

For a step-by-step walkthrough of the first three commands, see [Installation](installation.md). For the arguments and the behavior of each skill, see [Skills Reference](skills.md). To deploy the case-reviewer agent into an organization, see [Case-Reviewer Agent](case-reviewer-agent.md).

## What `lc-compliance` does not do

- **Issue compliance attestations.** The plugin reports evidence. The human auditor, QSA, or ISSO decides the compliance status.
- **Change deployed configuration without confirmation.** Every write needs your confirmation: the creation of an API key, the staging of a secret, and the deployment of a rule. `compliance-baseline-deploy` does a dry-run by default. You must give `--apply` to write rules.
- **Replace your SOC.** The case-reviewer agent runs in parallel with the Level-1 triage flow that the organization already has. It classifies the compliance impact, not the security severity. It does not contain, isolate, or remediate.
- **Supply normative control wording.** The mappings paraphrase. The normative text of each standard is in the document of the publisher. The attribution document of each framework links to that document.

## See also

- [AI Sessions](../index.md) — the mechanism that runs the case-reviewer agent
- [Cases](../../5-integrations/extensions/limacharlie/cases.md) — the case lifecycle that the agent works on
- [D&R-Driven Sessions](../dr-sessions.md) — how the case-reviewer agent is triggered
- [Hive Secrets](../../7-administration/config-hive/secrets.md) — where the API keys of the agent are stored
