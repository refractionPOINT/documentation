# Gmail

## Overview

This Adapter connects to one or many Gmail mailboxes using the [Gmail REST API](https://developers.google.com/gmail/api/reference/rest) and ingests them into LimaCharlie as `json` telemetry.

Beyond incoming-email telemetry, it can collect the mailbox configuration and change signals most relevant to **Business Email Compromise (BEC)** — the mail rules, forwarding, aliases, delegates, protocol access, and deletions an intruder uses to persist, exfiltrate mail, and cover their tracks. Each signal is an independent, opt-in capability that ships its own event type, and all of them are readable with the default `gmail.readonly` scope.

With the service-account flow the adapter can watch **many mailboxes at once** — an explicit list, or every mailbox in a Workspace domain via auto-discovery — and ships **each mailbox to its own LimaCharlie sensor**. See [Monitoring multiple mailboxes](#monitoring-multiple-mailboxes).

| Capability flag | Event type(s) | What it gives you / BEC relevance |
|-----------------|---------------|-----------------------------------|
| `collect_messages` (default) | `gmail_message` | Incoming email as telemetry. The raw signal for phishing/lure detection. |
| `collect_filters` | `gmail_filter` | Mail rules. Attackers create rules that auto-delete or auto-forward invoice/wire replies so the victim never sees them. |
| `collect_forwarding` | `gmail_forwarding_address`, `gmail_auto_forwarding` | Forwarding destinations and the account-wide auto-forward toggle — a classic mail-exfiltration vector. |
| `collect_send_as` | `gmail_send_as` | Send-as / "from" identities. An added identity is an impersonation/persistence signal. |
| `collect_delegates` | `gmail_delegate` | Mailbox delegates. Granting a delegate is persistence. **Workspace only** (requires the service-account flow). |
| `collect_imap_pop` | `gmail_imap`, `gmail_pop` | IMAP/POP access. Enabling these allows bulk mailbox download via a desktop client, bypassing browser-session controls. |
| `collect_vacation` | `gmail_vacation` | The vacation responder, occasionally abused for harvesting/social engineering. |
| `collect_history` | `gmail_history` | Mailbox changes: message deletions and label changes (marking a security alert read, trashing the fraud thread) — how an intruder covers their tracks. |

> If you set none of the `collect_*` flags, the adapter defaults to message telemetry only (`collect_messages`).

## Granting Access

The adapter needs read access to the target mailbox through the Gmail API. Choose **one** of two authentication modes.

### Mode 1 — OAuth 2.0 refresh token (a single mailbox)

Best when you want to monitor one user's mailbox and that user can complete a consent screen once.

#### Step 1 — Create a Google Cloud project and enable the Gmail API

1. In the [Google Cloud Console](https://console.cloud.google.com/), create (or select) a project.
2. Go to **APIs & Services → Library**, search for **Gmail API**, and click **Enable**.

#### Step 2 — Configure the OAuth consent screen

1. Go to **APIs & Services → OAuth consent screen**.
2. Pick **Internal** (recommended, if the project belongs to your Workspace org) or **External**.
3. Add the scope `https://www.googleapis.com/auth/gmail.readonly`.
4. If you chose **External**, add the mailbox owner as a **Test user**.

#### Step 3 — Create an OAuth client

1. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**.
2. Choose application type **Desktop app** (or **Web application** if you prefer to run the code flow yourself).
3. Record the generated **Client ID** and **Client secret**.

#### Step 4 — Obtain a refresh token

The simplest path is the [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground):

1. Click the gear icon (top right) → check **Use your own OAuth credentials** and paste your Client ID/secret.
2. In **Step 1**, enter the scope `https://www.googleapis.com/auth/gmail.readonly` and authorize as the mailbox owner.
3. In **Step 2**, click **Exchange authorization code for tokens** and copy the **Refresh token**.

You now have the three values the adapter needs: **client id**, **client secret**, and **refresh token**.

### Mode 2 — Service account with domain-wide delegation (Google Workspace)

Best for monitoring one or many Workspace mailboxes without per-user consent. This mode is **required for `collect_delegates`** and for collecting more than one mailbox.

#### Step 1 — Enable the Gmail API

Enable the Gmail API in a Google Cloud project, as in Mode 1, Step 1. If you also intend to use mailbox auto-discovery, enable the **Admin SDK API** in the same project as well.

#### Step 2 — Create a service account and key

1. Go to **APIs & Services → Credentials → Create Credentials → Service account**.
2. Once created, open the service account → **Keys → Add key → Create new key → JSON**, and download the key file. Keep it secret.
3. On the service account's **Details** page, note its numeric **Client ID** (the "Unique ID").

#### Step 3 — Authorize domain-wide delegation in the Workspace Admin console

1. In the [Workspace Admin console](https://admin.google.com/), go to **Security → Access and data control → API controls → Domain-wide delegation**.
2. Click **Add new** and enter:
   - **Client ID**: the service account's numeric Client ID from Step 2.
   - **OAuth scopes**: `https://www.googleapis.com/auth/gmail.readonly`
     - To use **auto-discovery** of mailboxes, also add `https://www.googleapis.com/auth/admin.directory.user.readonly` (comma-separated).
3. Save. Delegation can take a few minutes to propagate.

The adapter signs a JWT assertion impersonating each `subject` mailbox you configure. You need: the **service account JSON key** (inline or as a file) and at least one of `subject`, `subjects`, or `discover_mailboxes` (see [Monitoring multiple mailboxes](#monitoring-multiple-mailboxes)).

> **Least privilege:** `gmail.readonly` is sufficient for every capability above. The narrower `gmail.metadata` scope cannot read message bodies or any of the settings/history sub-resources, and it disallows the `query` search parameter — if you must use it, leave `query` empty and rely on `label_ids` / `include_spam_trash`, and expect the settings-based capabilities to be skipped.

## Monitoring multiple mailboxes

The service-account flow can collect more than one mailbox. Each mailbox is impersonated independently and **shipped to its own sensor**: when more than one mailbox is collected, the sensor seed key is derived as `<client_options.sensor_seed_key>/<mailbox-address>` and the sensor hostname is set to the mailbox address. (A single explicit `subject` keeps the `sensor_seed_key` / `hostname` you configured, verbatim.)

There are two ways to enumerate mailboxes, and they can be combined (the union is collected):

### Static list (`subjects`)

List the mailboxes explicitly. Good for a fixed set of high-value mailboxes.

```yaml
gmail:
  service_account_file: /secrets/gmail-collector.json
  subjects:
    - ceo@yourdomain.com
    - cfo@yourdomain.com
    - ap@yourdomain.com
```

### Auto-discovery (`discover_mailboxes`)

Enumerate the Workspace domain's mailboxes via the Admin SDK [Directory API `users.list`](https://developers.google.com/admin-sdk/directory/reference/rest/v1/users/list), re-run on `discovery_interval` so newly-provisioned mailboxes are picked up and deprovisioned ones are dropped automatically (their collector is stopped and torn down). Suspended accounts are skipped unless `include_suspended` is set.

Discovery has **two extra requirements** beyond the Gmail collection itself:

1. **An admin to impersonate** — `admin_subject` must be a Workspace admin user the service account impersonates for the Directory call (the Gmail collection of each discovered mailbox still impersonates that mailbox).
2. **An extra delegated scope** — the service account's client id must additionally be authorized for `https://www.googleapis.com/auth/admin.directory.user.readonly` (see Mode 2, Step 3).

```yaml
gmail:
  service_account_file: /secrets/gmail-collector.json
  discover_mailboxes: true
  admin_subject: admin@yourdomain.com
  # customer: my_customer                        # default; or restrict to a single domain:
  # domain: yourdomain.com
  # discovery_query: "orgUnitPath='/Finance'"    # optional Directory user filter (note the quoting)
  discovery_interval: 1h
```

If a discovery pass fails (e.g. the directory scope is missing) or comes back empty/truncated while mailboxes are already being collected, the current set is **kept** (and a warning logged) rather than torn down — a safety net against a misconfigured `discovery_query` or a transient API blip. Discovery never stops the adapter or the explicitly-listed mailboxes.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
- `client_options.platform`: the type of data ingested through this adapter — use `json`.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from.

### Adapter-specific Options

Adapter Type: `gmail`

**Authentication (Mode 1 — refresh token):**

- `client_id`: OAuth client id.
- `client_secret`: OAuth client secret.
- `refresh_token`: long-lived refresh token for the mailbox owner.

**Authentication (Mode 2 — service account):**

- `service_account_credentials`: the service account JSON key, inline.
- `service_account_file`: path to the service account JSON key file (alternative to the inline form).
- `subject`: a single mailbox owner to impersonate, e.g. `mailbox@yourdomain.com`. Provide the mailbox(es) with `subject` (one), `subjects` (a list), and/or `discover_mailboxes` (the whole domain) — at least one is required for this mode.

**Multi-mailbox options (service-account flow only):**

| Field | Default | Description |
|-------|---------|-------------|
| `subjects` | — | Static list of mailboxes to impersonate. |
| `discover_mailboxes` | `false` | Enumerate the domain's mailboxes via the Directory API. |
| `admin_subject` | — | Admin user to impersonate for the Directory API (required with `discover_mailboxes`). |
| `customer` | `my_customer` | Directory API customer id (mutually exclusive with `domain`). |
| `domain` | — | Restrict discovery to one domain of a multi-domain Workspace. |
| `discovery_query` | — | Optional Directory API user search filter (e.g. `orgUnitPath='/Finance'`). |
| `discovery_interval` | `1h` | How often discovery re-enumerates. |
| `include_suspended` | `false` | Also collect suspended mailboxes. |
| `max_concurrent_polls` | `10` | Cap on how many mailboxes poll the Gmail API at once (protects the per-project quota). |

**Capability toggles:**

| Field | Default | Description |
|-------|---------|-------------|
| `collect_messages` | on when no capability is set | Ship incoming email as `gmail_message`. |
| `collect_filters` | `false` | Ship mail filters/rules as `gmail_filter`. |
| `collect_forwarding` | `false` | Ship `gmail_forwarding_address` + `gmail_auto_forwarding`. |
| `collect_send_as` | `false` | Ship send-as aliases as `gmail_send_as`. |
| `collect_delegates` | `false` | Ship delegates as `gmail_delegate` (Workspace / service-account only). |
| `collect_imap_pop` | `false` | Ship IMAP/POP access as `gmail_imap` / `gmail_pop`. |
| `collect_vacation` | `false` | Ship the vacation responder as `gmail_vacation`. |
| `collect_history` | `false` | Ship deletions/label changes as `gmail_history`. |
| `settings_poll_interval` | `15m` | Cadence for the configuration-state capabilities (messages and history poll on `poll_interval`). |

**Collection knobs:**

| Field | Default | Description |
|-------|---------|-------------|
| `user_id` | `me` | Mailbox path segment for the refresh-token flow (`me` or an email address). Ignored by the service-account flow, where each mailbox is reached as `me` under its own impersonation. |
| `query` | `in:inbox` | Gmail [search query](https://support.google.com/mail/answer/7190); a time bound is appended automatically — do not add one. |
| `scopes` | `gmail.readonly` | OAuth scopes to request. |
| `format` | `full` | Message detail: `minimal`, `full`, `raw`, or `metadata`. |
| `metadata_headers` | — | Headers to keep when `format` is `metadata`. |
| `label_ids` | — | Only list messages carrying all of these label ids. |
| `include_spam_trash` | `false` | Include SPAM and TRASH messages. |
| `max_results` | `100` | Page size for `messages.list` (max 500). |
| `poll_interval` | `5m` | Wait between polls. |
| `overlap` | `2m` | Window backdating to avoid gaps from late-indexed mail; re-listed messages are deduped. |
| `initial_lookback` | `0` | On startup, reach back this far to backfill recent mail. |
| `dedupe_ttl` | `168h` (7d) | How long a message id is remembered to suppress re-shipping. |
| `retry_base_delay` | `5s` | Base backoff for transient API failures. |
| `max_retry_delay` | `30s` | Max backoff for transient API failures. |
| `max_retry_attempts` | `3` | Attempts per request before abandoning a poll. |

### CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

Refresh-token flow (single mailbox):

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter gmail client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
client_id=$GMAIL_CLIENT_ID \
client_secret=$GMAIL_CLIENT_SECRET \
refresh_token=$GMAIL_REFRESH_TOKEN \
query="in:inbox" \
initial_lookback=24h \
poll_interval=5m
```

### Infrastructure as Code Deployment

Service-account flow (Workspace), with the full BEC capability set enabled:

```yaml
sensor_type: gmail
gmail:
  service_account_file: "/secrets/gmail-collector.json"
  subject: "mailbox@yourdomain.com"
  user_id: "me"
  query: "in:inbox"
  initial_lookback: 24h
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
    platform: "json"
    sensor_seed_key: "gmail-mailbox-adapter"
    hostname: "gmail-mailbox-adapter"
    indexing: []
```

For cloud-sensor deployments, store the service account JSON as a hive secret and reference it, e.g. `service_account_credentials: "hive://secret/gmail-service-account"`.

Auto-discovery of every mailbox in the domain (each shipped to its own sensor), with the BEC capability set enabled:

```yaml
sensor_type: gmail
gmail:
  service_account_file: "/secrets/gmail-collector.json"
  discover_mailboxes: true
  admin_subject: "admin@yourdomain.com"
  # domain: "yourdomain.com"                  # optional: restrict to one domain
  # discovery_query: "orgUnitPath='/Finance'" # optional: restrict to an org unit
  discovery_interval: 1h
  include_suspended: false
  max_concurrent_polls: 10
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
    platform: "json"
    sensor_seed_key: "gmail-workspace"
    indexing: []
```

In multi-mailbox mode (a `subjects` list or `discover_mailboxes`) the `sensor_seed_key` and `hostname` you set are not used verbatim — each mailbox gets `sensor_seed_key=<your-seed>/<mailbox-address>` and `hostname=<mailbox-address>`.

## How it works

- **Messages** are listed each poll (paginated) and fetched at the configured `format`; the full message resource is forwarded verbatim, and the event timestamp comes from the message's `internalDate`. A deduper keyed on the immutable Gmail message id guarantees each message ships exactly once even though overlapping windows re-list recent ids. The high-water mark only advances after a fully-successful poll, so a failed poll is re-covered on the next cycle with no gaps.
- **Configuration-state capabilities** (filters, forwarding, send-as, delegates, imap/pop, vacation) are change-only: an item is shipped when it first appears or its content changes, and suppressed otherwise. They poll on the slower `settings_poll_interval` since configuration changes rarely. On restart the in-memory state is empty, so the current state is re-emitted once as a fresh baseline — write detections against the state of these events rather than treating every event as a brand-new change.
- **History** establishes a baseline on the first run (shipping nothing), then lists `messageDeleted` / `labelAdded` / `labelRemoved` records forward from the cursor. Gmail retains history for roughly a week; if the cursor ages out, the adapter re-baselines and resumes.
- **Multiple mailboxes** each get their own collector, token (impersonation), deduper namespace, and sensor. Up to `max_concurrent_polls` mailboxes poll the Gmail API at once. With discovery enabled, the mailbox set is re-enumerated every `discovery_interval`: new mailboxes spin up a collector and dropped ones are torn down.

## Error handling

- **401 Unauthorized** — the access token is transparently refreshed once and the request retried.
- **429 / 5xx / 403 rate-limit** — treated as transient and retried with exponential backoff.
- **Rejected credentials** (a dead refresh token, a bad service account key, or a delegation/scope problem surfacing as a persistent 401/403) — that **mailbox's** collector stops, since it needs operator attention rather than endless retries. Other mailboxes are unaffected; if every mailbox fails, the adapter winds down.
- **A discovery pass failing** (e.g. the admin lacks the directory scope) — logged as a warning; the currently-collecting mailboxes (including the static ones) keep running, and discovery retries on the next interval.
- **404 on a single message** (deleted between the list and the fetch) — skipped; the poll continues.
- **A BEC capability failing** (e.g. `delegates` on a consumer account, or a settings sub-resource unreadable under the chosen scope) — logged as a warning and skipped for that cycle, without affecting the other capabilities.
- **404 on the history cursor** (it aged out of Gmail's ~1 week retained history) — the adapter re-baselines from the current mailbox state and resumes on the next cycle.

## API Doc

See the official [Gmail API documentation](https://developers.google.com/gmail/api/reference/rest).
