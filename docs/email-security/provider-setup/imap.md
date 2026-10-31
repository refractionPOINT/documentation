# IMAP Mailboxes (Personal Gmail and Other IMAP Hosts)

--8<-- "includes/email-security-availability.md"

An IMAP connection protects mailboxes that have no admin API and no directory:
a **personal Gmail account**, or a mailbox on any other host that speaks IMAP.
The product signs in to each mailbox the way a mail app would, using a password
you create for it, reads new mail, and can move messages between folders. There
is no mail routing change and nothing in the delivery path.

Microsoft 365 and Google Workspace connections discover every mailbox in a
tenant. IMAP has no tenant, so **you list the mailboxes you want protected**,
one login each.

**Auth model:** one **app password** (Gmail) or password (other hosts) per
mailbox, stored as one [secret](../../7-administration/config-hive/secrets.md)
per mailbox.

## How the connection is shaped

An organization has **one** IMAP connection, the same one-enabled-record-per-provider
rule as the other providers (see [Connecting Providers](../providers.md)). That
single `imap` record holds a **list of mailboxes**:

- The record is not one connection per mailbox. You add and remove mailboxes
  by editing the list in the one record.
- Each mailbox in the list points at its **own** secret, so changing one
  mailbox's password never touches another's.
- The record's top-level `credentials` field stays empty for IMAP.
- The mailbox list is the scope. `scope.include_addresses`, `scope.domains` and
  `scope.include_groups` are refused. Use `scope.exclude_addresses` to pause a
  mailbox without deleting its entry.

An IMAP connection can coexist with a Microsoft 365 and a Google Workspace
connection in the same organization.

## Prerequisites

- The email address and password (or Gmail app password) of each mailbox.
- For Gmail: **2-Step Verification** turned on for the account.
- For other hosts: the IMAP server name, and whether it uses port **993** (TLS)
  or **143** (STARTTLS).

## Gmail: create an app password

Gmail does not let other applications use your Google password over IMAP. You
create a separate **app password** instead.

1. Turn on **2-Step Verification** for the Google account. App passwords are not
   offered without it.
2. Open [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   while signed in to that account.
3. Name the password (for example `LimaCharlie`) and click **Create**.
4. Copy the 16-character password. Google shows it as four groups of four
   letters; the spaces are ignored, so you can paste it exactly as shown. Google
   shows it once.

!!! warning "When an app password is not available or stops working"
    - **Advanced Protection.** Accounts enrolled in Google's Advanced Protection
      Program cannot create app passwords, so they cannot use this connection.
    - **Google password change.** Changing the Google account password revokes
      its app passwords. The mailbox then reports a credential fault until you
      create a new app password and update that mailbox's secret.
    - **Revoking it yourself.** Deleting the app password at the page above
      disconnects the mailbox immediately.

Google keeps IMAP turned on for every Gmail account, so there is no IMAP setting
to enable.

## Other hosts

For any other IMAP host, collect these values for each mailbox:

| Value | Notes |
|---|---|
| `host` | The server's DNS name, such as `imap.example.org`. IP addresses and `localhost` are refused. |
| `port` and `security` | **993** with `tls` (implicit TLS, the default), or **143** with `starttls`. STARTTLS is mandatory on 143: a server that does not offer it fails the connection. |
| `username` | Only if the login name differs from the mailbox address. |
| Password | The mailbox password, or an app-specific password if the host offers one. |

There is **no plaintext option**, and the server's certificate is always
verified. The host must be reachable from the public internet: addresses on
private networks, loopback, link-local and cloud metadata ranges are refused, so
a mail server that is only reachable inside your network cannot be connected.

The server must support the `UIDPLUS` extension (nearly all modern servers do).
`MOVE` and `IDLE` are used when offered; without them the product falls back to
copy-and-delete, and to the periodic sweep for new mail.

## Connect the mailboxes

Each mailbox needs a `secret` record whose value is JSON with a `password` key,
then all mailboxes go into one `mailsec_provider` record.

Store one secret per mailbox. `read -rs` takes the password without echoing it
or saving it in shell history, and `jq` builds the secret record's envelope and
escapes any special characters, without the password appearing in process
arguments:

```bash
read -rs IMAP_PASSWORD; printf %s "$IMAP_PASSWORD" \
  | jq -Rs '{secret: ({password: .} | tojson)}' \
  | limacharlie secret set --key imap-alice --enabled --oid $OID; unset IMAP_PASSWORD
```

Save the connection. The top-level `credentials` is left out, and each
mailbox references its own secret:

```yaml
# imap.yaml
provider: imap
imap:
  mailboxes:
    - address: alice@gmail.com
      host: imap.gmail.com
      port: 993
      security: tls
      credentials: hive://secret/imap-alice
    - address: bob@mail.example.org
      host: imap.example.org
      port: 143
      security: starttls
      username: bob
      credentials: hive://secret/imap-bob
ingest:
  mode: auto
  backfill_days: 14
```

```bash
limacharlie hive set --hive-name mailsec_provider --key imap \
  --input-file imap.yaml --enabled --oid $OID
limacharlie mailsec connection test imap --oid $OID --output yaml
```

`hive set` creates records disabled unless you pass `--enabled`.

The same guide is available headless, with a Gmail variant and a generic-host
variant:

```bash
limacharlie mailsec onboarding --provider imap --oid $OID
```

## Adding and removing mailboxes

Everything happens in the one record:

- **Add** a mailbox: create its secret, then add an entry to `imap.mailboxes`
  and save the record. The record accepts up to 1,000 mailboxes.
- **Remove** a mailbox: delete its entry from the list. Its connection is
  closed. Mail already indexed stays under your retention policy.
- **Pause** a mailbox without deleting it: add its address to
  `scope.exclude_addresses`.
- **Change a password**: update that mailbox's secret. Nothing else changes.

## The connection test

`limacharlie mailsec connection test imap` reports a block of checks **per mailbox**. Each check carries a
remediation when it fails. The checks cover:

| Check | Required |
|---|:--:|
| Network address allowed and DNS resolves | ✅ |
| TLS handshake and certificate | ✅ |
| Login | ✅ |
| Open the Inbox | ✅ |
| `UIDPLUS` supported | ✅ |
| `MOVE` supported (falls back to copy-and-delete) | — |
| `IDLE` supported (without it, new mail waits for the periodic sweep) | — |
| Junk, Trash and Sent folders found (Junk required) | ✅ |
| `LC Quarantine` folder can be created (required for quarantine) | ✅ |
| Note that filters which skip the Inbox are not covered | — |

An optional check that fails leaves the overall result `ok: true`, and names
the capability that is reduced.

## What works

| Action | What happens |
|---|---|
| `quarantine_message` | The message moves to a folder named `LC Quarantine`, created the first time it is needed. On Gmail the folder is a label, so the message leaves the Inbox and the user can still find it under that label |
| `trash_message` | Moves to the Trash folder |
| `move_to_spam` | Moves to the Junk/Spam folder |
| `restore_message` | Moves back to the folder it came from |
| `banner_message` / `unbanner_message` | **Not available on Gmail mailboxes** (see below). On other IMAP hosts the message is **replaced**: a copy carrying the banner is added to the same folder, keeping its flags and date, and then the original is deleted. An interruption leaves a duplicate rather than a loss. The provider message id changes and the new one is stored. It follows the same message-rewrite rules as [Google Workspace](google-workspace.md#remediation-semantics) |

Every action is idempotent: if the message is already where the action would
put it, nothing moves. Message identifiers are tied to a folder, so they change
when a message moves; re-read `provider_message_id` instead of caching it. If a
user moves a message themselves, the product finds it again by its
`Message-ID` header.

Outbound observation works too: with `features.outbound_observation` on (the
default), the Sent folder is ingested as `direction: outbound` and never
remediated.

## What does not work

- **Warning banners on Gmail mailboxes.** Adding or removing a warning banner is
  refused for personal Gmail accounts connected over IMAP (the request fails with
  a clear error and is not retried), because Gmail's IMAP server does not let the
  product replace a message safely. Quarantine, trash, spam and restore work as
  usual. Banners work on other IMAP hosts. Gmail banner support is planned for a
  later release; no date is committed.
- **Reporter auto-replies.** IMAP is read and move only; the product cannot send
  mail from an IMAP mailbox. The [reporter reply](../user-reports.md#reporter-replies)
  policy is refused for these mailboxes by name. Reports themselves can still be
  ingested from a `reports_mailbox` that is one of the listed mailboxes.
- **Directory features.** There is no directory, so there is no group scope and
  no discovery. Only the mailboxes you list exist.
- **"Internal" mail between personal addresses.** Personal domains such as
  `gmail.com` are never treated as your organization's domains, so mail between
  two Gmail users is not internal. Direction comes from the folder (Sent is
  outbound) and from `scope.internal_domains`, which keeps its usual meaning.

## Limits and behavior to know about

- **Mail that filters move out of the Inbox is not covered.** The product reads
  the Inbox and Junk folders (and Sent when outbound observation is on). If a
  user's own filter files mail straight into another folder, skipping the Inbox
  (in Gmail, a filter with **Skip the Inbox**), that mail is not seen. The
  connection test says so. Review your filters if you rely on them.
- **New mail is near-instant, with a safety sweep.** The product keeps an IMAP
  `IDLE` session open on the Inbox of each mailbox, so new mail is picked up
  within moments. Independently of that, a sweep every **2 minutes** checks all
  folders, which covers Junk, Sent and any dropped `IDLE` session.
- **Two of Gmail's 15 connections.** Gmail allows 15 simultaneous IMAP
  connections per account. The product uses at most **2** per mailbox: one
  long-lived connection for new-mail notification and one short-lived connection
  for reading and remediation, closed after about a minute idle. Your own mail
  apps keep their share.
- **Authentication results are only trusted from Gmail.** For
  `imap.gmail.com` mailboxes, the SPF/DKIM/DMARC results Google stamped on
  delivery are used as evidence. For other hosts they are not, because a generic
  server may pass through a header the sender wrote, so authentication is
  treated as unproven rather than assumed.
- **A refused login affects one mailbox.** The product retries once with the
  current secret (so a rotated password is picked up), then marks that mailbox
  with a credential fault and backs off. The connection test and coverage name
  the mailbox. No mail is deleted and other mailboxes keep working.

## Free tier

IMAP mailboxes are protected mailboxes like any other. Free-tier organizations
can protect up to **10 mailboxes in total**, counted across all connections, and
each IMAP mailbox counts as one. Above the cap, the mailboxes that rank last stay
listed but are not protected until you move to a paid plan. See
[security product billing](/7-administration/billing/security-products/) for
pricing and upgrading.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Login check fails for a Gmail mailbox | Wrong or revoked app password, 2-Step Verification off, or the Google password changed | Create a new app password and update that mailbox's secret |
| No app password option on the Google page | 2-Step Verification is off, or the account is in Advanced Protection | Turn on 2-Step Verification; Advanced Protection accounts cannot use this connection |
| Network check fails | The host is not a public DNS name, resolves to a private address, or uses a port other than 993/143 | Use a publicly reachable host on 993 or 143 |
| Certificate error | The server presents a certificate that does not match its name or is not publicly trusted | Fix the server's certificate; verification cannot be turned off |
| `STARTTLS` error on port 143 | The server does not offer STARTTLS | Use port 993 with `tls`, or enable STARTTLS on the server |
| `UIDPLUS` check fails | The server lacks the extension | The mailbox cannot be connected; move to a server that supports it |
| Some mail never appears | A user filter moves it out of the Inbox | Change the filter so mail passes through the Inbox |
| Mailbox shows a credential fault | The password was revoked or changed | Update that mailbox's secret |
| Save refused for `credentials` | The top-level `credentials` is set on an `imap` record | Remove it; set `credentials` on each mailbox |
