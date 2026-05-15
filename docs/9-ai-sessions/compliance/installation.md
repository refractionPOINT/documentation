# Installation

`lc-compliance` is a Claude Code plugin distributed through the LimaCharlie marketplace at [`refractionPOINT/lc-ai`](https://github.com/refractionPOINT/lc-ai). Installing the plugin gives you the four interactive compliance skills and the bundled reference content for all seven frameworks. The case-reviewer agent is deployed separately on a per-organization basis — see [Case-Reviewer Agent](case-reviewer-agent.md).

## Prerequisites

Before installing:

- A working **Claude Code** environment. Install via `curl -fsSL https://claude.ai/install.sh | bash`, or use Claude Code through the LimaCharlie web interface at [app.limacharlie.io](https://app.limacharlie.io), where `lc-essentials` is pre-configured.
- The **LimaCharlie CLI** (`limacharlie`) installed and authenticated against the organization you will operate on. The skills shell out to the CLI for org operations.
- The **`lc-essentials`** plugin already installed in the same Claude Code session. `lc-compliance` does not duplicate the API access layer — it relies on `lc-essentials` for org listing, sensor operations, and rule deployment. See the [`lc-essentials` README](https://github.com/refractionPOINT/lc-ai/tree/master/marketplace/plugins/lc-essentials) for setup.
- For the case-reviewer agent: an **Anthropic API key** (or other supported provider — see [Alternative AI Providers](../alternative-providers.md)), and a **LimaCharlie API key** with case-investigation permissions. The `compliance-deploy` skill handles key creation and secret staging for you.

## Installing the plugin

From any Claude Code session:

```text
/plugin marketplace add https://github.com/refractionPOINT/lc-ai
/plugin install lc-compliance@lc-marketplace
```

After installation, the four skills become available immediately:

| Slash command | Purpose |
|---|---|
| `/lc-compliance:compliance-lookup` | Look up control coverage |
| `/lc-compliance:compliance-gap` | Run an ad-hoc gap analysis |
| `/lc-compliance:compliance-deploy` | Deploy the case-reviewer agent |
| `/lc-compliance:compliance-baseline-deploy` | Deploy the full framework rule baseline |

See [Skills Reference](skills.md) for full argument syntax and behavior.

## Verifying the installation

Run the lookup skill against a known control to confirm the plugin is loaded and the bundled reference content is accessible:

```text
/lc-compliance:compliance-lookup nist AU-2
```

You should receive a response that includes:

- A conceptual coverage description quoted from the NIST 800-53 mapping document
- The verification level for the NIST 800-53 framework (**MACHINE_VERIFIED**)
- A list of deployable rules that cite AU-2 in their metadata

If the response says the framework cannot be located, the plugin is installed but its bundled content was not found on disk — verify that `${CLAUDE_PLUGIN_ROOT}/compliance/nist-800-53/` exists.

## First deployment to an organization

Once the plugin is installed, deploying compliance capabilities to a specific organization is a separate step. The recommended sequence for a new organization is:

### 1. Choose your framework and identify in-scope sensors

For most frameworks, only a subset of your fleet is in scope (the cardholder data environment for PCI, systems handling ePHI for HIPAA, etc.). Each reviewer accepts a small set of tag aliases; tagging any *one* of the accepted tags is enough to place the sensor in scope.

| Framework | Accepted scope tags (any one is sufficient) |
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

See [Sensor Tags](../../2-sensors-deployment/sensor-tags.md) for tagging at scale.

### 2. Deploy the case-reviewer agent

```text
/lc-compliance:compliance-deploy pci-dss --oid <your-oid>
```

The skill walks you through API-key creation, Anthropic secret staging, agent hive sync, and trigger D&R rule installation, with explicit confirmation at each platform write. See [Case-Reviewer Agent](case-reviewer-agent.md).

### 3. Deploy the recommended rule baseline (optional)

```text
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid>
```

This is a dry-run by default. It prints exactly which rules would be created, then asks for confirmation. To apply, re-run with `--apply`:

```text
/lc-compliance:compliance-baseline-deploy pci-dss --oid <your-oid> --apply
```

The skill is idempotent — rules already deployed under the same name are skipped, so it is safe to re-run after the bundled implementation document is updated. See [Skills Reference](skills.md#compliance-baseline-deploy) for behavior details and the `--overwrite` / `--kinds` flags.

### 4. Run an initial gap analysis

After the baseline is deployed, run a gap analysis to confirm there are no remaining coverage holes:

```text
/lc-compliance:compliance-gap pci-dss --oid <your-oid>
```

The output is a markdown punch list directly in your chat. See [Gap Analysis](gap-analysis.md) for how to read the report.

## Updating the plugin

To pick up new framework content, rule definitions, or skill changes:

```text
/plugin update lc-compliance@lc-marketplace
```

The plugin reads its bundled reference content from disk at invocation time, so an update is picked up on the next skill invocation without restarting Claude Code. Already-deployed reviewer agents and rules in your LimaCharlie organizations are unaffected by a plugin update — they continue running their previously-synced configuration. To bring them in line with new plugin content, re-run `compliance-deploy` (for the agent) or `compliance-baseline-deploy` (for the rules) against the relevant orgs.

!!! info "Multi-tenant operators"
    Each skill takes an `--oid` argument. Run the skill once per organization to onboard, audit, or deploy across a portfolio. The plugin itself is installed once into your Claude Code environment, not per organization. See [Skills Reference](skills.md) for the per-skill behavior.

## Uninstalling

To remove the plugin from your Claude Code environment:

```text
/plugin uninstall lc-compliance@lc-marketplace
```

This removes the skills and bundled reference content from your local Claude Code installation. **It does not remove anything from your LimaCharlie organizations.** Deployed case-reviewer agents, hive records, secrets, API keys, and D&R rules remain in place and continue running. To remove those, use `limacharlie sync` against an empty manifest or manually delete the affected hive records.
