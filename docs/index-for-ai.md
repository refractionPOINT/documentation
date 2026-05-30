# Topic Index for Automation & AI Consumers

> **Curated and may lag the tree.** This page is a hand-maintained map of major
> topics and integrations to their canonical doc paths, meant to help tooling
> and AI consumers route quickly. It is not exhaustive and can fall behind the
> actual documentation tree — when in doubt, the live docs are authoritative.
>
> A complementary, fully auto-generated flat index of every navigation page is
> published at [`/llms.txt`](https://docs.limacharlie.io/llms.txt) (built from
> the navigation on every build). This page adds the cross-references that the
> flat index cannot express — most importantly the adapter-vs-extension layout.

## Top-level sections

- [Getting Started](1-getting-started/index.md)
- [Sensors & Deployment](2-sensors-deployment/index.md)
- [Detection & Response](3-detection-response/index.md)
- [Data & Queries](4-data-queries/index.md)
- [Integrations](5-integrations/index.md)
- [Developer Guide](6-developer-guide/index.md)
- [Administration](7-administration/index.md)
- [Reference](8-reference/index.md)
- [AI Sessions](9-ai-sessions/index.md)
- [Release Notes](10-release-notes/index.md)

## Adapter vs. extension dual layout

Some third-party products are documented in **two** complementary places:

- An **adapter** under `2-sensors-deployment/adapters/types/` — ingests that
  product's events into LimaCharlie (the **input** side: what events you
  receive and their shape).
- An **extension** under `5-integrations/extensions/third-party/` — exposes the
  actions an AI agent or Playbook calls to enrich those events and act back
  (the **action** side: requests you can send and the responses you get).

When automating such a product you usually need **both** pages: the adapter to
understand the incoming events, and the extension to understand the actions and
their response shapes. One line per integration that has both, pointing to each:

| Integration | Adapter (input) | Extension (actions) |
| --- | --- | --- |
| ThreatLocker | [adapter](2-sensors-deployment/adapters/types/threatlocker.md) | [extension](5-integrations/extensions/third-party/threatlocker.md) |

## Full integration catalogs

- All adapter types: [`2-sensors-deployment/adapters/types/`](2-sensors-deployment/adapters/index.md)
- All third-party extensions: [`5-integrations/extensions/third-party/`](5-integrations/extensions/third-party/index.md)
- First-party (LimaCharlie) extensions: [`5-integrations/extensions/limacharlie/`](5-integrations/extensions/limacharlie/index.md)
