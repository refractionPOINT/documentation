# Connecting Providers

--8<-- "includes/email-security-availability.md"

A mail connection is one `mailsec_provider` Hive record plus one credential (one
per mailbox, for IMAP) in
the [secret](../7-administration/config-hive/secrets.md) Hive. Three providers are
supported, and an organization may hold **one connection of each**:

| Provider | `provider` | Auth model | Setup |
|---|---|---|---|
| Microsoft 365 / Exchange Online | `m365` | Entra ID app registration (client credentials) with Microsoft Graph **application** permissions | [Microsoft 365](provider-setup/microsoft-365.md) |
| Google Workspace / Gmail | `gworkspace` | Google Cloud service account with **domain-wide delegation**, plus Pub/Sub in the same project | [Google Workspace](provider-setup/google-workspace.md) |
| Personal Gmail and other IMAP hosts | `imap` | One password or Gmail **app password** per mailbox; no admin API or directory | [IMAP Mailboxes](provider-setup/imap.md) |

!!! info "One enabled record per provider"
    Creating a second enabled record for a provider that already has one is
    refused at write time. Notifications carry a mailbox and a subscription, not
    a credential, so two same-provider connections in one organization would
    make it ambiguous which tenant's credential should fetch a given message.
    An M365, a Workspace **and** an IMAP connection in the same organization
    is fully supported and runs concurrently; a campaign can span all of them.

    The IMAP connection still follows the rule: its one record holds a **list of
    mailboxes**, each with its own login and secret, instead of one record per
    mailbox. See [the IMAP record](#the-imap-record).

## The connection record

```yaml
provider: m365 | gworkspace | imap
credentials: hive://secret/<name>   # must be empty for imap

scope:
  include_addresses: []
  exclude_addresses: []
  include_groups: []
  domains: []
  internal_domains: []

ingest:
  mode: auto | push        # Workspace requires explicit push
  backfill_days: 14

features:
  outbound_observation: true
  reports_mailbox: ""
  pubsub_topic: ""          # Google Workspace only
  pubsub_subscription: ""   # Google Workspace only
```

### The IMAP record

An `imap` record replaces the single `credentials` reference with a list of
mailboxes. Everything else (`ingest`, `features`) works as above.

```yaml
provider: imap
imap:
  mailboxes:
    - address: alice@gmail.com        # required, unique, the mailbox's identity
      host: imap.gmail.com            # required, a public DNS name
      port: 993                       # 993 (default) or 143
      security: tls                   # tls (default) or starttls; never plaintext
      username: ""                    # optional, defaults to address
      credentials: hive://secret/imap-alice   # this mailbox's own secret
ingest:
  mode: auto
  backfill_days: 14
```

- The top-level `credentials` must be empty. Each mailbox carries its own, so
  adding or removing a mailbox never reads or rewrites another mailbox's secret.
- The mailbox list is the scope: `scope.include_addresses`, `scope.domains` and
  `scope.include_groups` are refused. `scope.exclude_addresses` pauses a mailbox
  without deleting its entry, and `scope.internal_domains` keeps its meaning.
- At most 1,000 mailboxes per record. `ingest.mode` accepts `auto` only, and
  `features.pubsub_*` are refused.
- `features.reports_mailbox`, when set, must be one of the listed addresses.

Full setup is in [IMAP Mailboxes](provider-setup/imap.md).

The record is decoded strictly: an unknown key is **refused**, not ignored. A
typo in a security control that silently does nothing is the worst available
failure mode, so a rejected record is preferred to an ignored field.

### `credentials`

Always a `hive://secret/<name>` reference. The credential is resolved in the
collector's memory only; a decoded connection record carries no secret material,
which is what makes it safe to read through the API, mirror and log.

### `scope`

Which mailboxes the connection covers. (Not applicable to IMAP, where the
mailbox list is the scope.)

| Field | Meaning |
|---|---|
| `include_addresses` | Exact mailbox addresses to cover. **Empty means every discovered mailbox** — the intended default. |
| `exclude_addresses` | Mailboxes never to cover. Excludes always win over includes. |
| `include_groups` | Directory groups to expand into addresses before discovery. |
| `domains` | Restrict to mailboxes in these domains. **Every listed domain is enumerated**, so an account hosting several domains can name as many as it needs. **Empty means every domain in the account** — the intended default, and what the setup wizard writes. |
| `internal_domains` | Extra domains your organization sends from, used only to label mail from them as `internal`. It does not change which mailboxes are covered. Most organizations leave it empty, because your mailbox and alias domains are detected automatically. See [Internal Domains](internal-domains.md). |

Addresses and domains are lowercased on save.

!!! warning "Group expansion is fail-closed on the connection, not on the scope"
    A group-scoped connection whose groups cannot be expanded is treated as a
    **connection error** rather than proceeding — because an unexpanded group
    scope would silently widen to every mailbox.

### `ingest`

| Field | Meaning |
|---|---|
| `mode` | Microsoft 365 accepts `auto` (the default, resolving to Graph notification push) or explicit `push`. Google Workspace requires explicit `push` plus both Pub/Sub fields. IMAP accepts `auto` only (an `IDLE` session plus a periodic sweep) and refuses `push`. Other values are refused at save. |
| `backfill_days` | Historical bootstrap window, 0–90, default **14**. That history is **judged** with the same rules live mail is judged with, and it seeds sender profiles and campaign statistics — but it **emits no telemetry and performs no actions** (no `EMAIL_MESSAGE`, no `EMAIL_VERDICT`, no automation, no remediation), and it is paced so it cannot compete with live ingestion. `0` disables the setup pass, but expired Gmail history IDs or Graph delta tokens can trigger a 14-day recovery walk even at `0`. It does not delete existing history. See [cleanup guidance](#cleaning-up-an-unwanted-backfill). Disabling setup comes at the cost of an empty queue on day one and first-contact signals being uninformative for the first weeks. |

Push is the only implemented live-delivery path for Microsoft 365 and Google
Workspace; IMAP uses `IDLE` with a 2-minute sweep. During a notification-path
outage, coverage reports the degradation and recovery resumes from the durable
provider watermark; the product does not claim a polling fallback it does not
run.

### `features`

| Field | Meaning |
|---|---|
| `outbound_observation` | Ingest Sent mail as `direction: outbound`, observation-only — it is never remediated. **Defaults on**: outbound is where account takeover shows itself. |
| `reports_mailbox` | The abuse mailbox to ingest as user reports. See [User Reports](user-reports.md). |
| `pubsub_topic` | Google Workspace only. The topic Gmail publishes notifications to. It **must** live in the service account's own Google Cloud project — Gmail rejects any other. |
| `pubsub_subscription` | Google Workspace only. The pull subscription the collector reads. Separate from the topic because a topic is write-only from Gmail's side. |

A Pub/Sub field on an `m365` record is refused rather than ignored: it means a
Workspace record was copied, and ignoring it would leave an operator believing
push was configured through a topic nothing reads.

## The connection test

The single most useful thing after saving a record. It reports each requirement
independently, so a UI (and a human) can say "step 4 is missing" instead of
"connection failed".

```bash
limacharlie mailsec connection test <record-name> --oid $OID --output yaml
```

Every check carries `id`, `name`, `required`, `status` and — when it fails — a
`detail` and a `remediation` naming the exact fix. `ok` is the AND of the
**required** checks only.

| Provider | Checks |
|---|---|
| Microsoft 365 | `credential` (authenticate to Graph), `mailbox_read` (list mailboxes), `mail_write` (`Mail.ReadWrite` — required), `mail_send` (`Mail.Send` — optional) |
| IMAP | One block of checks **per mailbox**, ids suffixed with the mailbox's position: network guard and DNS, TLS and certificate, `login`, Inbox open, `UIDPLUS` (these four required), `MOVE` and `IDLE` (optional), folders found (Junk required), `LC Quarantine` creatable (required for quarantine), and an informational note that filters which skip the Inbox are not covered |
| Google Workspace | `credential` (key well formed), `directory` (`admin.directory.user.readonly`), `mail_modify` (`gmail.modify`), `mail_full` (`https://mail.google.com/` — optional), `mailbox_read` (list mailboxes in the domain), `pubsub_pull` (read the subscription), `pubsub_watch` (Gmail can publish to the topic) |

Three properties are worth knowing:

- **It takes a record name, not a credential.** The obvious shape — post the key,
  get a verdict — would put a service-account private key in a request body,
  where it transits the gateway and lands in logs. The credential stays in the
  secret Hive; the test reads what is already there.
- **A failed optional check is not an error.** A tenant that granted only the
  narrow scopes has a working connection, and the missing capability is named
  rather than silently absent.
- **`--include-watch` has a side effect.** It establishes a real Gmail watch to
  verify notification delivery end to end. The watch is idempotent and expires on
  its own. Every other check is read-only.

It requires `mailsec.act`, because it makes real calls against your provider.

## Capability differences between providers

Provider mechanics differ, and the differences are surfaced rather than papered
over.

| | Microsoft 365 | Google Workspace | IMAP |
|---|---|---|---|
| **Quarantine** | Move to a hidden `LC Quarantine` folder. Restorable, and the user does not see the folder | Remove `INBOX` **and `SPAM`**, add a **visible** `LC Quarantine` label, so mail the provider had already filed as junk leaves the Spam folder too. Restorable, and the user can still find the message under that label | Move to an `LC Quarantine` folder, created on first use (a visible label on Gmail). Restorable |
| **Trash** | Move to Recoverable Items — invisible to the user, recoverable by an admin. Distinct from Deleted Items | Add `TRASH`, and remove `SPAM` if the message was in the Spam folder | Move to the Trash folder |
| **Move to spam** | Move to the Junk Email folder | Add `SPAM`, remove `INBOX` and any `LC Quarantine` label | Move to the Junk/Spam folder |
| **Restore** | Move back to the folder we recorded, falling back to the Inbox. A message we quarantined from the provider's own spam folder goes to the **Inbox**, not back to Spam | Invert the labels, with the same Inbox rule for mail quarantined from Spam | Move back to the folder we recorded |
| **Banner** | Edited **in place**; the message keeps its provider id | Gmail cannot edit a stored message, so the message is **replaced** and gets a **new provider id**. Requires the optional `https://mail.google.com/` scope; without it the action is refused by name, never reported as a silent success | The message is **replaced** (the banner copy is appended, then the original deleted) and gets a **new provider id**. Needs `UIDPLUS`, which every connected mailbox must have |
| **Notification state** | Graph subscriptions can be listed, so reconciliation compares against the provider's own view | Gmail **cannot enumerate active watches**, so reconciliation uses stored state with correspondingly lower assurance. Every Workspace connection row says so | An `IDLE` session per mailbox plus a 2-minute sweep; there is no provider-side subscription to enumerate or expire |
| **Reporter replies** | Need the optional `Mail.Send` application permission | Need the optional `https://mail.google.com/` scope | **Not supported.** IMAP cannot send mail, so replies are refused by name |

!!! note "Provider message ids are live handles"
    A move mints a new provider id and invalidates the old one. The product
    rewrites the stored handle after every action, which is why a restore days
    after a quarantine still addresses the right message. If you script against
    `provider_message_id`, re-read it rather than caching it.

## Common pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Nothing is discovered or ingested | The Hive record was created disabled | `limacharlie hive enable --hive-name mailsec_provider --key <name>` |
| `coverage` shows mailboxes as `discovered` but not `protected` | Discovery ran, subscription has not yet been established for those mailboxes | Give the subscription sweep a pass; if it persists, run the connection test |
| Save refused with an unknown-field error | A key that is not in the record contract, or a Workspace-only field on an M365 record | Fix the key; the refusal names it |
| Second connection for the same provider refused | Only one enabled record per provider is supported | Edit the existing record instead. For IMAP, add the new mailbox to the existing record's `imap.mailboxes` list |
| An `imap` record is refused for `credentials`, `scope` or `ingest.mode` | IMAP takes credentials per mailbox, uses the mailbox list as its scope, and supports `auto` only | Move `credentials` into each mailbox entry, remove `include_*`/`domains`/`include_groups`, and use `mode: auto` |
| One IMAP mailbox reports a credential fault | Its app password was revoked or its account password changed | Update that mailbox's secret; other mailboxes are unaffected |
| `connections.state` is `unconfigured` | No connection record exists, or none has completed a pass | Create/enable the record; an empty list is never reported as healthy |

## Cleaning up an unwanted backfill

Setting `ingest.backfill_days: 0` disables the connection-setup history pass. It
is not a deletion command, a way to reset a completed bootstrap, or a guaranteed
cancellation of work already queued. It applies equally on create and update.
Recovery after an expired provider watermark can still walk 14 days of history.
Deleting the provider record offboards the connection; recreating it does not
remove history already indexed.

A [retention policy](policy.md#retention) can age out unwanted indexed history:
choose `message_days` in **1–35** for the message index and transient raw copies.
This is organization-wide and time-based: it also deletes live-ingested mail
past the same horizon, cannot select one backfill or connection, and cannot
immediately erase everything because the minimum is one day. Flagged evidence
and its retained copy follow `flagged_days` (**1–400**, default **400**) separately.

Deletion is asynchronous. The deployment must have retention deletion enabled;
a changed retention window gets a report-only sweep before deletion, and large
backlogs can take multiple sweeps. Verify sweep completion before treating
cleanup as complete. Restore your intended ongoing retention only after verifying it.
This removes MailSec data, not messages from the provider's mailbox.

Backfilled historical messages are judged but emit no `EMAIL_MESSAGE` or
`EMAIL_VERDICT` telemetry and trigger no automation or remediation. An unwanted
setup backfill therefore does not itself mean MailSec acted on those messages.

### If a zero update appears not to stick

There is no intended create/update difference. Keep the exact provider YAML or
JSON used for the write, the organization ID, hive partition, and record name.
Capture the `hive set --output json` response and `hive get --output json` before
and after the write, comparing both `data.ingest.backfill_days` and
`sys_mtd.etag`. Read back again if the first result appears stale, and check for
another console session or infrastructure-as-code writer restoring the record.
An unchanged readback etag alone does not prove the server took its no-op path;
a changed etag alone does not prove the intended field was written. Send these
provider-record captures to support if the discrepancy persists; do not include
the referenced secret or service-account private key.
