# Data Residency, Encryption and Data Flows

--8<-- "includes/email-security-beta.md"

This page answers the questions a security or privacy review asks about Email
Security: where your mail is stored, how it is protected, how long it is kept, and
what can leave the region your organization lives in. Every statement here is about
behavior of the product as built. Where a question cannot be answered from that,
the page says so in [What this page does not cover](#what-this-page-does-not-cover).

See [Storage and privacy](pipeline.md#storage-and-privacy) for the short version of
the encryption and retention facts, and
[Data retention and deletion](policy.md#data-retention-and-deletion) for purge.

## Where your data lives

Email Security runs as its own deployment in **each LimaCharlie datacenter**, and
an organization's mail is processed and stored in the datacenter that hosts the
organization, the one chosen as the
[Data Residency Region](../8-reference/faq/general.md#where-will-my-data-be-processed-and-stored)
when the organization was created. Requests for an organization are served by that
datacenter's deployment, and so is the work of reading its mailboxes.

Each datacenter's deployment has its own stores, all in that datacenter's region:

| Data | Where it is held | Notes |
|---|---|---|
| Message index | A single-region database in the datacenter | One row per message per protected mailbox: sender, mailbox, subject, verdict, hashes used for clustering, campaign and remediation state. It does not hold the message body. Also holds campaigns, sender profiles, the action audit and user reports |
| Raw messages | A single-region storage bucket dedicated to Email Security, one per datacenter | The original message, and beside it the parsed model the engine judged with. Both are encrypted, see below |
| Key that wraps the encryption root | A key in the cloud key management service, in the same region as the bucket | The service holds the root only as ciphertext, see below |
| Link-detonation results | A separate single-region bucket in the datacenter | Short-lived, see [What can leave the region](#what-can-leave-the-region) |
| Short-lived caches | The datacenter's own cache | Holds shared facts about public domains, such as a registration date, and short-lived coordination state |

Email Security does not copy any of these stores to another datacenter. Each
datacenter has its own database, bucket and wrapping key, created in its own region.

The `EMAIL_*` events are ordinary LimaCharlie telemetry. They are ingested by the
same datacenter and stored in your organization's telemetry lake like any other
event, under the platform's own residency guarantees and your retention settings.

## Encryption of stored messages

The full raw message is stored encrypted, and so is the parsed copy the engine
judged it with. Each object is compressed and then sealed with **AES-256-GCM**.

- **Per-organization keys.** Every organization has its own data-encryption key.
  It is derived with **HKDF** (SHA-256) from the datacenter's root key, with the
  organization id as the salt, so two organizations never share a key. The derived
  key is computed in memory when needed and is not stored.
- **A KMS-wrapped root.** The root key is held as ciphertext that can only be
  unwrapped by calling the cloud key management service, and the permission to do so
  is scoped to the Email Security services that write or read raw messages. A
  service configured without the key management key fails to start rather than fall
  back to an unwrapped root.
- **Authenticated, and bound to its location.** GCM detects any change to the
  stored bytes. The object's own storage path is part of the authenticated data, so
  an object copied to another path, another message's or another organization's,
  does not open. The bytes an analyst receives are the bytes that were stored.
- **Access to the bucket is not access to the mail.** The bucket holds ciphertext.
  The service that answers API reads can read the bucket, and has no code path
  that writes to it.

The message index is stored in the regional database, not in the encrypted
bucket, and holds metadata rather than message bodies, as listed above.

## Retention

| Lane | Kept | Holds |
|---|---|---|
| Transient | **35 days** | Every message |
| Retained | up to **400 days** | Flagged messages and the evidence attached to them |

The two windows are enforced by lifecycle rules on the raw-message bucket itself,
in addition to Email Security's own sweeps, so the data ages out even if a sweep is
delayed. Your [`retention`](policy.md#retention) policy can only shorten them. A
tenant purge removes everything the product holds for an organization at once,
including stored raw messages and detonation results.

`EMAIL_*` telemetry follows your ordinary telemetry retention, not these lanes.

## What can leave the region

Most of Email Security's work happens inside the datacenter: reading mail,
parsing, scoring, clustering, attachment inspection and storing. The table lists
everything that sends data out of that datacenter, or to a party other than you,
and what it sends.

| Flow | What is sent, and to whom | You control it with |
|---|---|---|
| **Your mail provider** | Email Security reads mail from Microsoft 365 or Google Workspace and sends remediation calls back (move, label, banner). That traffic is between the datacenter and your provider | The provider connection, its scopes and its scope of mailboxes |
| **`EMAIL_*` events to your Outputs and rules** | Event bodies, including parsed message text (each body part is capped at about 256 KB). They go wherever you send them: an Output destination, a D&R response action or a webhook | Your [Outputs](../5-integrations/outputs/index.md) and D&R rules |
| **AI triage** | If you build and enable it, the agent reads parsed messages through the Email Security API and sends what it reads to the AI provider you configured. See [AI Triage](ai-triage.md). Nothing is sent unless you create the agent | Whether you create the agent, which model provider you give it, and the permissions of its API key. Do not grant it `mailsec.get.eml` |
| **Domain registration lookups** | Domain-age enrichment asks the domain's public registry, using the open RDAP protocol, when the domain was registered. The query contains the domain name, taken from a message's links or sender, and nothing else from the message. It does not go through an aggregator. The list of registries comes from the public IANA RDAP bootstrap file. Answers are cached for all organizations in the datacenter, so one domain is looked up once rather than once per message | Not configurable per organization |
| **Link detonation** | Where it is deployed, a suspicious link is fetched from an isolated environment in the same datacenter region, so the destination server sees a request from that region. The request is for the link as written in the message, after a mail gateway's rewrite is removed, including its query string. The isolated environment holds no credential and is not told which organization the link came from. Only a bounded summary comes back: redirect chain, certificate facts, a hash, a title and a short text excerpt, never the page body. Links carrying embedded credentials, and non-web addresses, are refused | Detonation is an enrichment. It runs automatically only for [suspicious messages](detections.md#link-detonation), and otherwise when an analyst, a rule or an AI triage agent asks for it with `crawl_link`. A link that identifies the recipient in its address identifies them to its destination, as it would if they clicked it |
| **Usage metering** | A daily per-organization count of protected mailboxes goes to platform usage metering. It carries no message data | Not configurable |

Two things people expect to be on this list are not:

- **Attachment inspection stays in the datacenter.** Attachments are opened by a
  scanning service that runs in the datacenter's own cluster and is reached over the
  datacenter's internal network. Email Security sends the bytes to it, scans, and
  drops them when the message leaves the pipeline. What Email Security keeps is a
  summary and hashes, not the attachment.
- **Threat-intelligence feeds are not queried per message.** Email Security does
  not send message content, links or hashes to a third-party reputation service. A
  feed such as a malicious-URL list reaches rules as an ordinary
  [lookup in your organization](ioc-feeds.md), and is matched inside the
  datacenter. The popularity ranking used to spot unranked domains is downloaded
  into the service; downloading it sends no message data.

## What this page does not cover

These are not claimed either way, because they go beyond what Email Security
itself does:

- Where the platform's telemetry lake, usage metering and billing systems
  store their data. That is the platform's own residency behavior, described in
  the general [FAQ](../8-reference/faq/general.md#where-will-my-data-be-processed-and-stored).
- The path a response takes from the datacenter to the person or tool that asked
  for it, through the platform's API gateway. A message you read in the console or
  through the API, including a raw download, is returned over that path.
- Where AI Sessions, if you use it for triage, runs, and what your chosen model
  provider does with the content it is given.
- The handling of change notifications your mail provider sends to LimaCharlie,
  and of the provider's own copy of your mail.
- Backups and operational access by LimaCharlie staff.
