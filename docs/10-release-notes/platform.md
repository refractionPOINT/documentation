# Platform, CLI & SDKs Release Notes

Release notes for platform announcements, the command line interface and the SDKs. For the latest releases of every component, see the [release notes overview](index.md).

!!! tip "Subscribe"
    Get each release as it ships with the [Platform announcements RSS feed](https://docs.limacharlie.io/10-release-notes/platform.xml) or [CLI RSS feed](https://docs.limacharlie.io/10-release-notes/cli.xml).

## 2026-08-20

### Platform: Multi-Provider AI Sessions

#### New Features

- **AI provider choice for user sessions**: user AI Sessions can now run on OpenAI (API key or Azure OpenAI), Google Gemini (AI Studio key or Vertex AI service account), and OpenRouter, in addition to Claude. Connect your own provider credentials under **User Settings → AI Terminal** (or via the API) and pick the provider on a session profile. Tool use and approvals, MCP servers, USD budget caps, hibernation, forking, and cost tracking work the same on every provider; a few capabilities stay Claude-only (plan mode, `bypassPermissions`, Task subagents, extended thinking). See [AI Providers](../9-ai-sessions/providers.md).

---

## 2026-05-09

### Vulnerability Management Uplift

Major uplift to the Vulnerability Reporting extension and its surfaces.

- **Canonical asset-tag namespace**: introduces the `lc:asset:*` tag convention (criticality, exposure, environment, owner, compliance) for cross-cutting asset metadata. The Vulnerability Reporting extension is the first consumer; the namespace is intended to be reused across LimaCharlie surfaces. See [Asset Tag Namespace](../2-sensors-deployment/asset-tags.md).
- **Vulnerability Reporting extension**: new public-facing documentation covering setup, scan modes (`scheduled` / `manual` / `all`), criticality-tag overrides, KEV + EPSS enrichment, LC Risk scoring, and the full action surface. See [Vulnerability Reporting](../5-integrations/extensions/limacharlie/vulnerability-reporting.md).
- **Finding resolutions**: documented the resolution model — every finding is implicitly **open** until an operator records `mitigated`, `accepted`, or `false_positive`. Accepted-exception expiries lapse back into the open count, and `vuln_finding.*` events (`created`, `closed`, `kev_match`, `state_changed`) can be routed via Outputs to Jira, Slack, Cases, etc.

---

## 2025-08-28

### Other Notable Updates

- **Org Templates**: Re-introduction of org templates during org creation. Currently offering EDR Quick Start and Basic Browser Monitoring to get the new org configured on creation. You can always add configurations as code using the IaC Generator.
- **Parsing Unstructured Logs**: With `parsing_grok` you can use OpenSearch Grok processor syntax, and tap into powerful ready-to-use Grok patterns and the vast knowledge of grokking data with Elastic.

---

## 2025-06-27

### New Community Rule Sets

Two new rule sets from community partners added to the LimaCharlie Add-Ons collection:

- **SoteriaSec Commercial Ruleset**: Google Workspace Rules
- **BLOKWORX Detection & Response**: Rules covering detection of a collection of remote access services usage

---

## 2025-05-20

### LimaCharlie Endpoint Protection

Releasing LimaCharlie Endpoint Protection, which integrates with third-party EDR solutions to provide a better view of security operations and extend agent capabilities. This functionality comprises the EPP Extension, Web App, and a previously released Endpoint Agent v4.33.6.

---

## 2025-02-28

### LimaCharlie Labs

Introducing LimaCharlie Labs, where we share brave experiments and early prototypes of features and extensions that may or may not become production, based on your input and feedback. Check the LABS badge on the Web App.

**Playbook Extension** is now available in Labs.

---

## 2025-02-21

### CLI 4.9.12

Add users, simplified. Wrapping the new API, a new command `limacharlie users invite` makes it easy to add a user, or a batch of users, to the org without requiring them to create a LimaCharlie account.

---

## 2024-10-28

### New MITRE Report API

Added a new REST API and CLI for producing a MITRE report for a given organization based on the D&R rules in place (using their tags like `attack..t1000.xxx`).

- **CLI**: `limacharlie mitre-report`

The resulting JSON report can be used with the [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/). This capability makes it easier to track security coverage against the MITRE ATT&CK framework.

---

## 2024-10-17

### New Sort and Bulk Actions for Tables

Added the ability to sort columns in the LimaCharlie web app. In addition, tables now support bulk actions (Enable/Disable and Delete). This applies to the following sections: Adapters, YARA Rules, Secrets, Lookups, False Positive Rules, and Detection and Response Rules.
