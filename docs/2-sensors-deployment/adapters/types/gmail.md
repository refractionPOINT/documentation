# Gmail

## Overview

This adapter collects telemetry from one or more Gmail mailboxes with the [Gmail REST API](https://developers.google.com/workspace/gmail/api/reference/rest). It also collects the mailbox configuration and the change signals for **Business Email Compromise (BEC)**. These signals are the mail rules, forwarding, aliases, delegates, protocol access, and deletions that an intruder uses to keep access, exfiltrate mail, and hide activity.

Each signal is an independent **capability** that you enable, and each capability sends its own event type. The default `gmail.readonly` scope can read all of them.

With the service-account flow, the adapter can collect **many mailboxes at once**: an explicit list, or every mailbox in a Google Workspace domain through auto-discovery. The adapter sends each mailbox to its own LimaCharlie sensor.

## Capabilities

Enable any combination of the `collect_*` flags. If you set none, the adapter collects only message telemetry (`collect_messages`).

| Flag | Event type(s) | What it gives you |
| --- | --- | --- |
| `collect_messages` | `gmail_message` | Incoming email as telemetry. This is the raw signal to detect phishing and lures. |
| `collect_filters` | `gmail_filter` | Mail rules. Attackers create rules that auto-delete, auto-forward, or hide replies about invoices and wires. |
| `collect_forwarding` | `gmail_forwarding_address`, `gmail_auto_forwarding` | Forwarding destinations and the account-wide auto-forward setting. Attackers use these to exfiltrate mail. |
| `collect_send_as` | `gmail_send_as` | Send-as / "from" identities. A new identity is a signal of impersonation or persistence. |
| `collect_delegates` | `gmail_delegate` | Mailbox delegates. A new delegate gives persistence. **Workspace only** (see the note below). |
| `collect_imap_pop` | `gmail_imap`, `gmail_pop` | IMAP/POP access settings. If these are enabled, a desktop client can download the full mailbox. |
| `collect_vacation` | `gmail_vacation` | The vacation responder. Attackers sometimes abuse it for harvesting and social engineering. |
| `collect_history` | `gmail_history` | Mailbox changes: message **deletions** and **label changes** (marking a security alert read, trashing the fraud thread). |

> **Delegates are Workspace-only.** Google gives the delegates listing only to service-account clients that have domain-wide delegation. On a consumer account, or without delegation, the call returns an error. The adapter logs the error and skips the capability. The adapter continues to run, and the other capabilities are not affected.

The configuration-state capabilities (filters, forwarding, send-as, delegates, IMAP/POP, vacation) are **change-only**. The adapter sends an item only when the item first appears or when its content changes. After an adapter restart, the in-memory dedupe state is empty, so the adapter sends the current state one time as a new baseline. Write detections against the *state* in these events, and do not treat every event as a new change.

## Authentication

Choose one of two modes.

### OAuth 2.0 refresh token (a single mailbox)

Use this mode to collect the mailbox of one user.

1. Create an OAuth client (Desktop or Web) in the Google Cloud console.
2. Enable the Gmail API.
3. Complete the authorization-code flow one time. The flow gives a refresh token for the `gmail.readonly` scope.

| Field | Description |
| --- | --- |
| `client_id` | OAuth client id |
| `client_secret` | OAuth client secret |
| `refresh_token` | Long-lived refresh token for the mailbox owner |

### Service account with domain-wide delegation (Google Workspace)

Use this mode to monitor Workspace mailboxes without consent from each user.

1. Create a service account.
2. Enable domain-wide delegation for the service account.
3. In the Workspace Admin console, authorize the client id of the service account for the `https://www.googleapis.com/auth/gmail.readonly` scope.

| Field | Description |
| --- | --- |
| `service_account_credentials` | The service account JSON key, inline |
| `service_account_file` | Path to the service account JSON key file (alternative to the inline form) |
| `subject` | A single mailbox owner to impersonate, e.g. `user@yourdomain.com` |

Select the mailboxes with `subject` (one mailbox), `subjects` (a list), or `discover_mailboxes` (the full domain). You can combine them. You must set at least one.

## Multiple mailboxes

With the service-account flow, the adapter impersonates each mailbox independently and sends each one **to its own sensor**. When the adapter collects more than one mailbox, the sensor seed key becomes `<sensor_seed_key>/<mailbox-address>`, and the sensor hostname becomes the mailbox address.

Two methods enumerate mailboxes. You can combine them, and the adapter collects the union:

- **Static list** (`subjects`): name each mailbox. Use this method for a fixed set of high-value mailboxes, such as executives, finance, and AP.
- **Auto-discovery** (`discover_mailboxes`): enumerate the mailboxes of the Workspace domain with the Admin SDK Directory API. The adapter repeats discovery on `discovery_interval` (default 1h), so it adds new mailboxes and drops deprovisioned ones automatically. The adapter skips suspended accounts unless you set `include_suspended`.

Auto-discovery needs two items more than the Gmail collection:

1. `admin_subject` — a Workspace admin user that the service account impersonates for the Directory call.
2. An extra delegated scope — authorize the service account's client id for `https://www.googleapis.com/auth/admin.directory.user.readonly` in the Workspace Admin console.

If a discovery pass fails or returns nothing while the adapter already collects mailboxes, the current set continues to collect and the adapter logs a warning. A temporary failure of discovery does not stop the mailboxes that work.

## Deployment Configurations

All adapters support the same `client_options`. Always set them when you use the binary adapter:

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) for this adapter.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: `gmail`.
- `client_options.sensor_seed_key`: a name for this adapter. LimaCharlie generates Sensor IDs (SID) from this name.

### Adapter-specific Options

Adapter Type: `gmail`

| Key | Default | Description |
| --- | --- | --- |
| `client_id` / `client_secret` / `refresh_token` | — | OAuth refresh-token flow credentials (single mailbox). |
| `service_account_credentials` / `service_account_file` | — | Service-account flow credentials (Workspace). |
| `subject` | — | Single mailbox to impersonate (service-account flow). |
| `subjects` | — | Static list of mailboxes to impersonate. |
| `discover_mailboxes` | `false` | Enumerate the mailboxes of the domain with the Directory API. |
| `admin_subject` | — | Admin user to impersonate for the Directory API (necessary with `discover_mailboxes`). |
| `customer` | `my_customer` | Directory API customer id (mutually exclusive with `domain`). |
| `domain` | — | Restrict discovery to one domain of a multi-domain Workspace. |
| `discovery_query` | — | Optional Directory API user search filter, e.g. `orgUnitPath='/Finance'`. |
| `discovery_interval` | `1h` | How often discovery enumerates again. |
| `include_suspended` | `false` | Also collect suspended mailboxes. |
| `max_concurrent_polls` | `10` | Maximum number of mailboxes that poll the Gmail API at the same time. |
| `collect_messages` … `collect_history` | see [Capabilities](#capabilities) | Capability toggles. |
| `settings_poll_interval` | `15m` | Cadence for the configuration-state capabilities. |
| `user_id` | `me` | Mailbox path segment for the refresh-token flow. The service-account flow ignores it. |
| `query` | `in:inbox` | Gmail [search query](https://support.google.com/mail/answer/7190) that selects messages. The adapter appends a time bound automatically. Do not add one. |
| `scopes` | `gmail.readonly` | OAuth scopes to request. |
| `format` | `full` | Message detail: `minimal`, `full`, `raw`, or `metadata`. |
| `metadata_headers` | — | Headers to keep when `format` is `metadata`. |
| `label_ids` | — | Only list messages that carry all of these label ids. |
| `include_spam_trash` | `false` | Include SPAM and TRASH messages. |
| `max_results` | `100` | Page size for the message listing (max 500). |
| `poll_interval` | `5m` | Wait between message and history polls. |
| `overlap` | `2m` | Backdates the window to prevent gaps from mail that Gmail indexes late. The adapter dedupes messages that it lists again. |
| `initial_lookback` | `0` | At startup, go back this far to backfill recent mail. |
| `dedupe_ttl` | `168h` (7d) | How long the adapter remembers a message id and does not send it again. |
| `retry_base_delay` / `max_retry_delay` / `max_retry_attempts` | `5s` / `30s` / `3` | Retry tuning for temporary failures. |

## How collection works

- **Messages**: each poll lists the message ids that match `query` in a rolling time window. The adapter gets each message in the configured `format` and sends the full message resource unchanged. A deduper uses the immutable Gmail message id, so each message ships one time even when the windows overlap. The event timestamp is the `internalDate` of the message.
- **Configuration state**: the adapter polls on `settings_poll_interval` and sends only new items and changes.
- **History**: the first run records a baseline `historyId` and sends nothing. Later polls list forward from the cursor and keep only deletions and label changes. Gmail keeps history for about one week. If the cursor expires, the adapter makes a new baseline and continues instead of stopping.
- **Errors**: a `401` causes one token refresh. The adapter retries `429`, `5xx`, and `403` rate-limit errors with backoff. Credentials that stay rejected stop the collector of that mailbox, but the other mailboxes continue. The adapter logs and skips a BEC capability that fails, and the other capabilities continue.

## CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter gmail \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$INSTALLATION_KEY \
  client_options.platform=gmail \
  client_options.sensor_seed_key=gmail \
  client_id=$GMAIL_CLIENT_ID \
  client_secret=$GMAIL_CLIENT_SECRET \
  refresh_token=$GMAIL_REFRESH_TOKEN \
  query="in:inbox" \
  poll_interval=5m
```

## Infrastructure as Code Deployment

This example gives full BEC monitoring of a Workspace mailbox: message telemetry with the persistence, exfiltration, and tamper signals.

```yaml
# For cloud sensor deployment, store credentials as hive secrets:
#
#   service_account_credentials: "hive://secret/gmail-service-account"

sensor_type: "gmail"
gmail:
  service_account_credentials: "hive://secret/gmail-service-account"
  subject: "soc-mailbox@yourdomain.com"
  collect_messages: true
  collect_filters: true
  collect_forwarding: true
  collect_send_as: true
  collect_delegates: true
  collect_imap_pop: true
  collect_vacation: true
  collect_history: true
  poll_interval: 5m
  settings_poll_interval: 15m
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_GMAIL"
    platform: "gmail"
    sensor_seed_key: "gmail-sensor"
```

This example uses domain-wide auto-discovery. It collects every mailbox in the Workspace, each mailbox on its own sensor.

```yaml
sensor_type: "gmail"
gmail:
  service_account_credentials: "hive://secret/gmail-service-account"
  discover_mailboxes: true
  admin_subject: "admin@yourdomain.com"
  discovery_interval: 1h
  collect_messages: true
  collect_filters: true
  collect_forwarding: true
  collect_history: true
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_GMAIL"
    platform: "gmail"
    sensor_seed_key: "gmail-sensor"
```

## Sample Rule

The BEC capabilities send each signal with its own event type, so a D&R rule can match the signal directly. This example flags each change to the account-wide auto-forwarding setting:

```yaml
# Detection
event: gmail_auto_forwarding
op: is
path: event/enabled
value: true

# Response
- action: report
  name: Gmail auto-forwarding enabled
```

> **Note:** the `gmail.metadata` scope does not allow the `q` search parameter. If you limit the adapter to that scope, leave `query` empty and use `label_ids` and `include_spam_trash`. The default `gmail.readonly` scope covers every capability. The narrower `gmail.metadata` scope cannot read the settings sub-resources, so the adapter logs and skips a capability that uses them.

## API Docs

- Gmail API reference: [https://developers.google.com/workspace/gmail/api/reference/rest](https://developers.google.com/workspace/gmail/api/reference/rest)
- Admin SDK Directory API (`users.list`, used by auto-discovery): [https://developers.google.com/admin-sdk/directory/reference/rest/v1/users/list](https://developers.google.com/admin-sdk/directory/reference/rest/v1/users/list)
