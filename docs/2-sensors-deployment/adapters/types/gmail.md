# Gmail

## Overview

This Adapter collects telemetry from one or many Gmail mailboxes using the [Gmail REST API](https://developers.google.com/workspace/gmail/api/reference/rest). Beyond incoming-email telemetry, it can collect the mailbox configuration and change signals most relevant to **Business Email Compromise (BEC)** — the mail rules, forwarding, aliases, delegates, protocol access, and deletions an intruder uses to persist, exfiltrate mail, and cover their tracks.

Each signal is an independent, opt-in **capability** that ships its own event type. They are all readable with the default `gmail.readonly` scope.

With the service-account flow the adapter can watch **many mailboxes at once** — an explicit list, or every mailbox in a Google Workspace domain via auto-discovery — and ships each mailbox to its own LimaCharlie sensor.

## Availability

The Gmail adapter runs through the LimaCharlie Adapter, either the [adapter binary or the Docker image](../deployment.md#adapter-binaries), on a host you control. It can be configured on the command line, from a local configuration file, or from an [External Adapter record](../deployment.md#on-prem-cloud-management) managed in LimaCharlie.

It is **not available as a cloud-to-cloud (Cloud Sensor) adapter** at this time, so there is no `cloud_sensor` record type for it.

## Capabilities

Enable any combination with the `collect_*` flags. If you set none, the adapter defaults to message telemetry only (`collect_messages`).

| Flag | Event type(s) | What it gives you |
| --- | --- | --- |
| `collect_messages` | `gmail_message` | Incoming email as telemetry — the raw signal for phishing/lure detection. |
| `collect_filters` | `gmail_filter` | Mail rules. Attackers create rules that auto-delete, auto-forward, or hide replies about invoices/wires. |
| `collect_forwarding` | `gmail_forwarding_address`, `gmail_auto_forwarding` | Forwarding destinations and the account-wide auto-forward toggle — a classic mail-exfiltration vector. |
| `collect_send_as` | `gmail_send_as` | Send-as / "from" identities. An added identity is an impersonation/persistence signal. |
| `collect_delegates` | `gmail_delegate` | Mailbox delegates — granting a delegate is persistence. **Workspace only** (see note below). |
| `collect_imap_pop` | `gmail_imap`, `gmail_pop` | IMAP/POP access settings. Enabling these allows bulk mailbox download via a desktop client. |
| `collect_vacation` | `gmail_vacation` | The vacation responder, occasionally abused for harvesting/social engineering. |
| `collect_history` | `gmail_history` | Mailbox changes: message **deletions** and **label changes** (marking a security alert read, trashing the fraud thread). |

> **Delegates are Workspace-only.** Google exposes the delegates listing only to service-account clients with domain-wide delegation. On a consumer account (or without delegation) the call returns an error, which the adapter logs and skips — it does not stop the adapter or affect the other capabilities.

The configuration-state capabilities (filters, forwarding, send-as, delegates, IMAP/POP, vacation) are **change-only**: an item is shipped when it first appears or its content changes, and suppressed otherwise. On adapter restart the in-memory dedupe state is empty, so the current state is re-emitted once as a fresh baseline — write detections against the *state* in these events rather than treating every event as a brand-new change.

## Authentication

The adapter needs read access to the mailbox through the Gmail API. Choose **one** of two modes. Providing both sets of credentials is rejected at startup.

### OAuth 2.0 refresh token (a single mailbox)

Use this when you want to monitor one user's mailbox and that user can complete a Google consent screen once.

**1. Create a project and enable the Gmail API.** In the [Google Cloud console](https://console.cloud.google.com/), create or select a project. Under **APIs & Services → Library**, find **Gmail API** and click **Enable**.

**2. Configure the OAuth consent screen.** Under **APIs & Services → OAuth consent screen**, choose **Internal** if the project belongs to the same Google Workspace organization as the mailbox, otherwise **External**. Add the scope `https://www.googleapis.com/auth/gmail.readonly`. For an External app, add the mailbox owner as a test user.

!!! warning
    For an External app left in the **Testing** publishing status, Google expires refresh tokens after 7 days, and the adapter stops collecting that mailbox once the token is rejected. Use an Internal app, or move the app to production, for a long-running deployment.

**3. Create an OAuth client.** Under **APIs & Services → Credentials → Create Credentials → OAuth client ID**, choose **Web application** and add `https://developers.google.com/oauthplayground` as an authorized redirect URI. Record the **Client ID** and **Client secret**.

**4. Obtain a refresh token.** The simplest route is the [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground):

1. Click the gear icon, select **Use your own OAuth credentials**, set the access type to **Offline**, and enter the client ID and secret.
2. In Step 1, enter the scope `https://www.googleapis.com/auth/gmail.readonly` and authorize as the mailbox owner.
3. In Step 2, click **Exchange authorization code for tokens** and copy the **Refresh token**.

You can remove the Playground redirect URI from the client afterwards.

| Field | Description |
| --- | --- |
| `client_id` | OAuth client id |
| `client_secret` | OAuth client secret |
| `refresh_token` | Long-lived refresh token for the mailbox owner |

### Service account with domain-wide delegation (Google Workspace)

Use this to monitor Workspace mailboxes without per-user consent. It is required for `collect_delegates` and for collecting more than one mailbox.

**1. Enable the APIs.** In a Google Cloud project, enable the **Gmail API**. If you plan to use mailbox auto-discovery, also enable the **Admin SDK API**.

**2. Create a service account and key.** Under **APIs & Services → Credentials → Create Credentials → Service account**, create the account. Open it, go to **Keys → Add key → Create new key → JSON**, and download the key file. Treat it as a secret. Note the service account's numeric **Client ID** (shown as the unique ID on its details page).

**3. Authorize domain-wide delegation.** As a super administrator, open the [Workspace Admin console](https://admin.google.com/) and go to **Security → Access and data control → API controls → Manage Domain Wide Delegation**. Click **Add new** and enter:

- **Client ID**: the numeric Client ID from step 2. Using the service account's email address instead causes `unauthorized_client` errors.
- **OAuth scopes**: `https://www.googleapis.com/auth/gmail.readonly`. For auto-discovery, add `https://www.googleapis.com/auth/admin.directory.user.readonly` as well, separated by a comma.

Delegation usually takes a few minutes to apply but can take up to 24 hours.

The adapter signs a JWT assertion that impersonates each configured mailbox owner.

| Field | Description |
| --- | --- |
| `service_account_credentials` | The service account JSON key, inline |
| `service_account_file` | Path to the service account JSON key file (alternative to the inline form) |
| `subject` | A single mailbox owner to impersonate, e.g. `user@yourdomain.com` |

Provide the mailbox(es) with `subject` (one), `subjects` (a list), and/or `discover_mailboxes` (the whole domain). At least one of these is required.

> **Least privilege:** `gmail.readonly` covers every capability. The narrower `gmail.metadata` scope cannot read message bodies or the settings sub-resources.

## Multiple mailboxes

With the service-account flow, each mailbox is impersonated independently and **shipped to its own sensor**: when more than one mailbox is collected, the sensor seed key is derived as `<sensor_seed_key>/<mailbox-address>` and the sensor hostname is set to the mailbox address.

There are two ways to enumerate mailboxes, and they can be combined (the union is collected):

- **Static list** (`subjects`): list the mailboxes explicitly — good for a fixed set of high-value mailboxes (executives, finance, AP).
- **Auto-discovery** (`discover_mailboxes`): enumerate the Workspace domain's mailboxes via the Admin SDK Directory API, re-run on `discovery_interval` (default 1h) so newly-provisioned mailboxes are picked up and deprovisioned ones dropped automatically. Suspended accounts are skipped unless `include_suspended` is set.

Auto-discovery has two extra requirements beyond the Gmail collection itself:

1. `admin_subject` — a Workspace admin user the service account impersonates for the Directory call.
2. An extra delegated scope — authorize the service account's client id for `https://www.googleapis.com/auth/admin.directory.user.readonly` in the Workspace Admin console.

If a discovery pass fails or comes back empty while mailboxes are already being collected, the current set keeps collecting (with a warning logged) — discovery never tears down working mailboxes on a transient blip.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify when running the adapter binary or container:

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: `gmail`.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from.
- `client_options.hostname`: a hostname for the sensor. With more than one mailbox, the adapter sets this to each mailbox address instead.

### Adapter-specific Options

Adapter Type: `gmail`

| Key | Default | Description |
| --- | --- | --- |
| `client_id` / `client_secret` / `refresh_token` | — | OAuth refresh-token flow credentials (single mailbox). |
| `service_account_credentials` / `service_account_file` | — | Service-account flow credentials (Workspace). |
| `subject` | — | Single mailbox to impersonate (service-account flow). |
| `subjects` | — | Static list of mailboxes to impersonate. |
| `discover_mailboxes` | `false` | Enumerate the domain's mailboxes via the Directory API. |
| `admin_subject` | — | Admin user impersonated for the Directory API (required with `discover_mailboxes`). |
| `customer` | `my_customer` | Directory API customer id (mutually exclusive with `domain`). |
| `domain` | — | Restrict discovery to one domain of a multi-domain Workspace. |
| `discovery_query` | — | Optional Directory API user search filter, e.g. `orgUnitPath='/Finance'`. |
| `discovery_interval` | `1h` | How often discovery re-enumerates. |
| `include_suspended` | `false` | Also collect suspended mailboxes. |
| `max_concurrent_polls` | `10` | Cap on how many mailboxes poll the Gmail API at once. |
| `collect_messages` … `collect_history` | see [Capabilities](#capabilities) | Capability toggles. |
| `settings_poll_interval` | `15m` | Cadence for the configuration-state capabilities. |
| `user_id` | `me` | Mailbox path segment for the refresh-token flow. Ignored by the service-account flow. |
| `query` | `in:inbox` | Gmail [search query](https://support.google.com/mail/answer/7190) selecting messages. A time bound is appended automatically — do not add one. |
| `scopes` | `gmail.readonly` | OAuth scopes to request. |
| `format` | `full` | Message detail: `minimal`, `full`, `raw`, or `metadata`. |
| `metadata_headers` | — | Headers to keep when `format` is `metadata`. |
| `label_ids` | — | Only list messages carrying all of these label ids. |
| `include_spam_trash` | `false` | Include SPAM and TRASH messages. |
| `max_results` | `100` | Page size for the message listing (max 500). |
| `poll_interval` | `5m` | Wait between message/history polls. |
| `overlap` | `2m` | Window backdating to avoid gaps from late-indexed mail; re-listed messages are deduped. |
| `initial_lookback` | `0` | On startup, reach back this far to backfill recent mail. |
| `dedupe_ttl` | `168h` (7d) | How long a message id is remembered to suppress re-shipping. |
| `retry_base_delay` / `max_retry_delay` / `max_retry_attempts` | `5s` / `30s` / `3` | Transient-failure retry tuning. |

## How collection works

- **Messages**: each poll lists message ids matching `query` over a rolling time window, fetches each message at the configured `format`, and forwards the full message resource verbatim. A deduper keyed on the immutable Gmail message id guarantees each message ships exactly once despite overlapping windows. The event timestamp is the message's `internalDate`.
- **Configuration state**: polled on `settings_poll_interval`; only appearances and changes are shipped.
- **History**: the first run records a baseline `historyId` and ships nothing; later polls list forward from the cursor, filtered to deletions and label changes. Gmail retains history for roughly a week — if the cursor ages out, the adapter re-baselines and resumes rather than stopping.
- **Errors**: `401` triggers one transparent token refresh; `429`/`5xx`/`403` rate-limit errors are retried with backoff; persistently rejected credentials stop that mailbox's collector (other mailboxes are unaffected); a failing BEC capability is logged and skipped without affecting the others.

## CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

Single mailbox with an OAuth refresh token:

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter gmail \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$INSTALLATION_KEY \
  client_options.platform=gmail \
  client_options.sensor_seed_key=gmail \
  client_options.hostname=gmail \
  client_id=$GMAIL_CLIENT_ID \
  client_secret=$GMAIL_CLIENT_SECRET \
  refresh_token=$GMAIL_REFRESH_TOKEN \
  query="in:inbox" \
  poll_interval=5m
```

Single Workspace mailbox with a service account key file:

```bash
/path/to/lc_adapter gmail \
  client_options.identity.oid=$OID \
  client_options.identity.installation_key=$INSTALLATION_KEY \
  client_options.platform=gmail \
  client_options.sensor_seed_key=gmail \
  client_options.hostname=gmail \
  service_account_file=/secrets/gmail-collector.json \
  subject=soc-mailbox@yourdomain.com \
  collect_filters=true \
  collect_forwarding=true \
  collect_history=true
```

Lists such as `subjects` are easier to set in a configuration file, shown next.

## Configuration File Deployment

Put the configuration in a YAML file whose root key is `gmail`, and pass the file after the adapter type:

```bash
/path/to/lc_adapter gmail /path/to/gmail.yaml
```

Full BEC monitoring of a Workspace mailbox, with message telemetry plus the persistence, exfiltration, and tamper signals:

```yaml
gmail:
  service_account_file: "/secrets/gmail-collector.json"
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
    hostname: "gmail-sensor"
```

Domain-wide auto-discovery, with every mailbox on its own sensor:

```yaml
gmail:
  service_account_file: "/secrets/gmail-collector.json"
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

## Docker Deployment

The adapter is published as the [`refractionpoint/lc-adapter`](https://hub.docker.com/r/refractionpoint/lc-adapter) image. Mount the configuration file and the service account key into the container:

```bash
docker run -d --rm \
  -v /path/to/gmail.yaml:/conf/gmail.yaml:ro \
  -v /path/to/gmail-collector.json:/secrets/gmail-collector.json:ro \
  refractionpoint/lc-adapter gmail /conf/gmail.yaml
```

## Cloud-Managed Deployment

The adapter binary can also fetch its configuration from LimaCharlie, so you can update it remotely. Create a record in the `external_adapter` Hive with `sensor_type: gmail` and the same `gmail:` block as the configuration file above, then start the adapter against that record's GUID. See [On-Prem + Cloud Management](../deployment.md#on-prem-cloud-management).

```yaml
sensor_type: gmail
gmail:
  service_account_file: "/secrets/gmail-collector.json"
  subject: "soc-mailbox@yourdomain.com"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_GMAIL"
    platform: "gmail"
    sensor_seed_key: "gmail-sensor"
    hostname: "gmail-sensor"
```

The credential file path in the record is resolved on the host running the adapter, so the key file must be present there.

## Sample Rule

The BEC capabilities ship each signal under its own event type, so D&R rules can route directly on the signal. For example, flag every change to the account-wide auto-forwarding setting:

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

> **Note:** the `gmail.metadata` scope does not allow the `q` search parameter. If you restrict the adapter to that scope, leave `query` empty and rely on `label_ids` / `include_spam_trash` instead. The default `gmail.readonly` scope covers every capability; the narrower `gmail.metadata` scope cannot read the settings sub-resources, so a capability using them will be logged and skipped.

## API Docs

- Gmail API reference: [https://developers.google.com/workspace/gmail/api/reference/rest](https://developers.google.com/workspace/gmail/api/reference/rest)
- Admin SDK Directory API (`users.list`, used by auto-discovery): [https://developers.google.com/admin-sdk/directory/reference/rest/v1/users/list](https://developers.google.com/admin-sdk/directory/reference/rest/v1/users/list)
