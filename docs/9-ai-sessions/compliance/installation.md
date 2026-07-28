# Installation

`lc-compliance` is a Claude Code plugin from the LimaCharlie marketplace at [`refractionPOINT/lc-ai`](https://github.com/refractionPOINT/lc-ai). The plugin gives you the four interactive compliance skills and the bundled reference content for all seven frameworks. You deploy the case-reviewer agent separately for each organization. See [Case-Reviewer Agent](case-reviewer-agent.md).

## Prerequisites

Before you install the plugin:

- A working **Claude Code** environment. Install it with `curl -fsSL https://claude.ai/install.sh | bash`, or use Claude Code in the LimaCharlie web app at [app.limacharlie.io](https://app.limacharlie.io), where `lc-essentials` is pre-configured.
- The **LimaCharlie CLI** (`limacharlie`), installed and authenticated against the organization that you operate on. The skills call the CLI for operations on the organization.
- The **`lc-essentials`** plugin, already installed in the same Claude Code session. `lc-compliance` does not duplicate the API access layer. It uses `lc-essentials` to list organizations, operate on sensors, and deploy rules. The [`lc-essentials` README](https://github.com/refractionPOINT/lc-ai/tree/master/marketplace/plugins/lc-essentials) gives the setup steps.
- For the case-reviewer agent: an **Anthropic API key** (or a key for another supported provider — see [Alternative AI Providers](../alternative-providers.md)), and a **LimaCharlie API key** with case-investigation permissions. The `compliance-deploy` skill creates the key and stages the secret for you.

## Installing the plugin

From any Claude Code session:

```text
/plugin marketplace add https://github.com/refractionPOINT/lc-ai
/plugin install lc-compliance@lc-marketplace
```

After the installation, the four skills are available:

| Slash command | Purpose |
|---|---|
| `/lc-compliance:compliance-lookup` | Look up control coverage |
| `/lc-compliance:compliance-gap` | Run an ad-hoc gap analysis |
| `/lc-compliance:compliance-deploy` | Deploy the case-reviewer agent |
| `/lc-compliance:compliance-baseline-deploy` | Deploy the full framework rule baseline |

See [Skills Reference](skills.md) for the full argument syntax and behavior.

## Verifying the installation

Run the lookup skill against a known control. This confirms that the plugin is loaded and that the bundled reference content is accessible:

```text
/lc-compliance:compliance-lookup nist AU-2
```

The response includes:

- A conceptual coverage description quoted from the NIST 800-53 mapping document
- The verification level for the NIST 800-53 framework (**MACHINE_VERIFIED**)
- A list of deployable rules that cite AU-2 in their metadata

If the response says that it cannot find the framework, the plugin is installed but its bundled content is not on disk. Check that `${CLAUDE_PLUGIN_ROOT}/compliance/nist-800-53/` exists.

## First deployment to an organization

After you install the plugin, the deployment of compliance capabilities to one organization is a separate step. Use this sequence for a new organization:

### 1. Choose your framework and identify in-scope sensors

For most frameworks, only a part of your fleet is in scope: the cardholder data environment for PCI, the systems that handle ePHI for HIPAA, and so on. Each reviewer accepts a small set of tag aliases. To put a sensor in scope, add *one* of the accepted tags.

| Framework | Accepted scope tags (any one is enough) |
|---|---|
| PCI DSS | `cde`, `pci-scope`, `card-data`, `pci-dss` |
| HIPAA | `ephi-host`, `hipaa-scope`, `phi-host`, `covered-entity` |
| CMMC | `cui`, `cui-host`, `cmmc-scope`, `dib-host` |
| NIST 800-53 | `fisma-scope`, `fedramp-scope`, `federal-system`, `nist-scope` |
| SOC 2 | `soc2-scope`, `in-scope-system`, `audit-scope` |
| ISO 27001 | `isms-scope`, `iso-scope`, `iso-27001-scope`, `soa-included` |
| CIS v8 | `cis-scope`, `cis-v8-scope` (plus optional `cis-ig1`/`cis-ig2`/`cis-ig3` for tier) |

Use the standard CLI to apply tags:

```bash
limacharlie tag add --sid <sensor-id> -t cde --oid <your-oid>
```

To tag many sensors at one time, see [Sensor Tags](../../2-sensors-deployment/sensor-tags.md).

### 2. Deploy the case-reviewer agent

```text
/lc-compliance:compliance-deploy pci-dss --oid <your-oid>
```

The skill takes you through the creation of the API key, the staging of the Anthropic secret, the sync of the agent hive record, and the installation of the trigger D&R rule. It asks for confirmation at each write to the cloud. See [Case-Reviewer Agent](case-reviewer-agent.md).

### 3. Deploy the recommended rule baseline (optional)

```text
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid>
```

This command is a dry-run by default. It prints the rules that it would create, then asks for confirmation. To apply the rules, run the command again with `--apply`:

```text
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply
```

The skill is idempotent. It skips the rules that are already deployed with the same name, so you can run it again after an update to the bundled implementation document. See [Skills Reference](skills.md#compliance-baseline-deploy) for the details of the behavior and for the `--overwrite` and `--kinds` flags.

### 4. Run an initial gap analysis

After you deploy the baseline, run a gap analysis to confirm that no gaps remain in the coverage:

```text
/lc-compliance:compliance-gap pci-dss --oid <your-oid>
```

The output is a markdown punch list in your chat. See [Gap Analysis](gap-analysis.md) for how to read the report.

## Updating the plugin

To get new framework content, new rule definitions, or changes to the skills:

```text
/plugin update lc-compliance@lc-marketplace
```

The plugin reads its bundled reference content from disk when you call a skill. The next call to a skill therefore uses the update, and you do not restart Claude Code. A plugin update does not change the reviewer agents and rules that are already deployed in your LimaCharlie organizations. They continue with the configuration from the last sync. To move them to the new plugin content, run `compliance-deploy` for the agent, or `compliance-baseline-deploy` for the rules, against the relevant organizations.

!!! info "Multi-tenant operators"
    Each skill takes an `--oid` argument. Run the skill one time for each organization to onboard, audit, or deploy across a portfolio. You install the plugin one time into your Claude Code environment, not one time for each organization. See [Skills Reference](skills.md) for the behavior of each skill.

## Uninstalling

To remove the plugin from your Claude Code environment:

```text
/plugin uninstall lc-compliance@lc-marketplace
```

This command removes the skills and the bundled reference content from your local Claude Code installation. **It removes nothing from your LimaCharlie organizations.** The deployed case-reviewer agents, hive records, secrets, API keys, and D&R rules stay in place and continue to run. To remove them, use `limacharlie sync` against an empty manifest, or delete the affected hive records manually.
