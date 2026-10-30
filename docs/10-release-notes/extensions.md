# Extensions Release Notes

Release notes for limaCharlie extensions, such as Email Security. For the latest releases of every component, see the [release notes overview](index.md).

!!! tip "Subscribe"
    Get each release as it ships with the [Extensions RSS feed](https://docs.limacharlie.io/10-release-notes/extensions.xml).

## 2026-09-07

### Extensions: Email Security bulk remediation, verdict revisions and the managed-detection switch

#### New Features

- **Bulk remediation over a selection you name.** Any search result — a filtered page of the queue, a hunt, a list of ids in a file — can now be remediated at the provider in one operation, with the campaign sweep's preview-then-confirm discipline: `POST /actions/bulk/preview` reports each message's current state and the distinct-mailbox blast radius and mints a confirmation derived from that exact selection, `POST /actions/bulk/execute` returns a `bulk_id` immediately and paces the provider writes in the background, and `GET /actions/bulk/{bulk_id}` reports per-message outcomes and running counts. Capped at 500 per call, refused rather than truncated above it. `limacharlie mailsec message bulk-action` wraps the pair, reads its selection from `--msg-uuids`, `--input-file` or standard input, and carries the outcome in its exit code.
- **Verdict revisions are documented end to end.** `POST /messages/{msg_uuid}/verdict` re-judges one message in the `analyst` or `ai` seat with a required rationale, and `GET /messages/{msg_uuid}/revisions` serves the whole append-only chain with the prior state each revision displaced. Re-recording a verdict a message already carries is a success reporting `applied: false`, not an error. Revising requires `mailsec.act` rather than `mailsec.set`, because it can promote a message's evidence to the 400-day lane and emits an `EMAIL_VERDICT`.
- **A resolved user report can be reopened.** `POST /reports/{report_id}/reopen` (`limacharlie mailsec report reopen`) puts a report back in the queue and keeps its resolution columns, so the row still reads "previously resolved by …" rather than erasing what is being disputed. It is the escape hatch the abuse-mailbox auto-resolver depends on.
- **The managed detection pack has a documented switch.** The `managed_rules` policy record, the console's Settings toggle, and the `set_managed_rules` / `get_managed_rules` extension actions all write the same thing. Absent means enabled; a record that states no value is refused; a change reaches the pipeline in seconds, with a five-minute backstop.
- **Link detonation is documented**: what triggers it (a `suspicious` verdict with links, up to five URLs per message), the organization-wide claim that makes a campaign cost one fetch, every refusal reason, and what a `mode: detonation` verdict revision means — including that it never overrules a person or an agent.
- **Time to verdict is a real number.** `coverage`'s `overview.processing_latency_p95` reports p50/p95/p99 with the basis it measures, the denominator it measured over, and — when there is no number — which of the two honest reasons applies. Backfilled and re-driven mail is excluded so a recovery cannot report a latency measured in days.
- New [Troubleshooting](../email-security/troubleshooting.md) page: the entitlement gate (mail that arrives while unsubscribed is never read and is never backfilled), watch renewals, silent-mailbox stalls, `EMAIL_INGEST_ERROR`, connection handover during a platform update, and the 30-day deletion clock.
- Custom rules now document `scope` versus the `?` path wildcard — only `scope` correlates two conditions on the *same* link or attachment — and state plainly that a rule using `lookup`, or a `post_verdict` rule, cannot be backtested.

See [Bulk Remediation](../email-security/remediation.md), [Detections & Verdicts](../email-security/detections.md#revising-a-verdict), [Policy Reference](../email-security/policy.md#managed_rules) and [Troubleshooting](../email-security/troubleshooting.md).

---

## 2026-09-04

### Extensions: Email Security tenant purge

#### New Features

- **Tenant purge for Email Security**: everything Email Security holds for an organization can now be deleted on request — the message index and the up-to-400-day evidence lane, campaigns, sender profiles, the product's action audit trail, user (abuse-mailbox) reports, stored raw messages and their parsed copies, link-detonation results, and the organization's provider connection and policy configuration. The purge also stops the mail connections at Microsoft 365 and Google Workspace, so the provider stops sending notifications instead of repopulating the index. It is irreversible, requires Owner-level authority (`mailsec.act`, `billing.ctrl` and `user.ctrl` together), and is recorded in the organization's audit log with the caller's identity and an optional reason.
- The purge is two steps, and previews by default: `limacharlie mailsec tenant purge` prints the warning and mints a single-use confirmation token that expires in five minutes, and destroys nothing until that token is passed back with `--confirm`. A purge that reports `complete: false` did not finish and can simply be re-run with a fresh token. The Python SDK exposes the same pair as `Mailsec.prepare_tenant_purge()` and `Mailsec.purge_tenant()`.
- Email Security data is now also deleted **automatically**: 30 days after an organization unsubscribes from the extension — resubscribing at any point inside that window cancels the scheduled deletion — and immediately when the organization itself is deleted.

See [Data retention and deletion](../email-security/policy.md#data-retention-and-deletion), the [CLI notes](../email-security/cli.md#the-tenant-purge-is-irreversible) and [`DELETE /tenant`](../email-security/api-reference.md#delete-tenant).

---

## 2025-05-20

### Extensions

Endpoint Protection extension: a component of the EPP solution that codifies key configurations for Microsoft Defender.

---

## 2025-03-28

### Extensions and Adapters

- **Git-Sync**: Take the best from LimaCharlie Infrastructure as Code by connecting with Git and syncing the desired sections of your configurations in an easy-to-use UI. See [documentation](../5-integrations/extensions/limacharlie/git-sync.md).
- **ext-renigma v1.0.0**: Initial release of integration with REnigma, an advanced malware analysis platform leveraging its unique Record and Replay technology.
- **Mimecast adapter**: Connect to the Mimecast API to stream audit events as they happen.

---

## 2025-03-14

### Add-Ons and Adapters

- **PandaDoc adapter**: Connect and fetch PandaDoc API logs.
- **CrowdStrike Falcon Cloud adapter**: Connect to CrowdStrike Falcon Cloud to stream events as they happen in the CrowdStrike Falcon Console.
- **Cloud-CLI v1.4.8 Extension**: Improved observability in CLI extensions such as ext-cloud-cli. Additionally, improved error handling and reporting around long-running CLI commands which may have gotten stuck or timed out.

---

## 2025-01-09

### ext-usage-alerts v1.0.0

Newly released extension which allows you to create, maintain, and automatically refresh usage alert conditions for an organization.
