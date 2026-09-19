# Google Workspace

--8<-- "includes/email-security-beta.md"

A Google Workspace connection reads and remediates Gmail through the Gmail API,
using a **service account with domain-wide delegation**. There is no mail
routing change and no content compliance rule: the product is not in the
delivery path.

Workspace needs setup that Microsoft 365 does not, and the reason is worth
stating once: **Gmail will only publish change notifications to a Pub/Sub topic
in the service account's own Google Cloud project.** That topic and its
subscription are therefore yours, in your project, and the same service account
that reads mail is the one that reads the subscription — so a Workspace
connection still needs exactly one credential.

**Auth model:** a Google Cloud **service account** whose numeric OAuth2 client ID
is authorized in your Workspace admin console for a specific list of scopes,
impersonating a Workspace admin.

## Prerequisites

- A Google Cloud project you control (it can be a new, empty one).
- **Super Admin** access to the Workspace admin console, to authorize
  domain-wide delegation.
- A Workspace administrator address for the service account to impersonate.

## Scopes

| Scope | Required | What it buys | Without it |
|---|:--:|---|---|
| `https://www.googleapis.com/auth/admin.directory.user.readonly` | ✅ | Read the list of users in your domain, so we know which mailboxes to protect | No mailbox can be discovered, so nothing is protected at all |
| `https://www.googleapis.com/auth/gmail.modify` | ✅ | Read messages, change their labels, and move them to trash. It does **not** permit permanent deletion | No mail can be analyzed, quarantined or restored |
| `https://mail.google.com/` | — | Insert and delete messages, which is the only way to place a warning banner on delivered mail — Gmail has no API to edit a message in place. Also enables reporter auto-replies | Everything works except banners and reporter replies. Quarantine, trash, restore and move-to-spam are unaffected. Grant it only if you want those; it is broader access than the rest |

!!! info "Mail *configuration* is a different product"
    Scopes such as `gmail.settings.basic` are not part of this connection.
    Diffable mail configuration — forwarding rules, delegation, transport rules,
    DKIM/SPF/DMARC posture — belongs to
    [Cloud Security](../../cloud-security/provider-setup/google-workspace.md),
    which collects it as posture findings. Email Security owns the *messages*.

## Which console does what?

Keep these tabs open:

| Console | What you do there |
|---|---|
| [Google Cloud](https://console.cloud.google.com/) | Create the service account (the application's identity), download its key, and configure notifications. |
| [Google Admin](https://admin.google.com/) | Authorize that identity to access Workspace users' mail. This is called **domain-wide delegation**. |
| LimaCharlie | Store the key securely and configure the connection. |

A **Pub/Sub topic** receives Gmail's new-mail notifications. A **pull subscription**
lets LimaCharlie retrieve those notifications. Both belong to your Google Cloud
project; they do not replace or reroute email.

## Setup steps

Choose **Web console** to use browser forms or **Cloud Shell / CLI** to run
commands. Complete each step once; the tabs are alternative ways to create the
same resources. Step 3 requires the Workspace Admin console whichever path you
choose.

For command tabs, open **Cloud Shell** in Google Cloud (the terminal icon).
It includes `gcloud`. Replace `<YOUR_PROJECT_ID>` with the project ID shown in
the Google Cloud project selector. After downloading the key, replace
`<SERVICE_ACCOUNT_EMAIL>` with its `client_email` value. The LimaCharlie
wizard can also fill these values into its setup commands for you.

### 1. Create a service account and download its JSON key

=== "Web console"

    1. In Google Cloud, select the project you want to use for Email Security.
    2. Open **IAM & Admin → Service Accounts → Create service account**, choose a
       name such as `limacharlie-mail`, and create it. You do not need a broad project
       role for mail access; the scoped Pub/Sub grant is added in step 7.
    3. Open the service account, then **Keys → Add key → Create new key → JSON**.
       Download the key. If your organization's policy blocks key creation, ask
       your Google Cloud administrator to resolve that before continuing.
    4. In the service account details, find its **OAuth 2 client ID** for domain-wide
       delegation. This is a number, not the service account's email address.

=== "Cloud Shell / CLI"

    In Cloud Shell, select your project and run:

    ```bash
    gcloud iam service-accounts create limacharlie-mail \
      --display-name="LimaCharlie Email Security" --project=<YOUR_PROJECT_ID>

    gcloud iam service-accounts keys create mailsec-key.json \
      --iam-account=limacharlie-mail@<YOUR_PROJECT_ID>.iam.gserviceaccount.com \
      --project=<YOUR_PROJECT_ID>
    ```

    Use Cloud Shell's **Download file** action to download `mailsec-key.json`.
    If key creation is blocked by organization policy, ask your Google Cloud
    administrator to resolve it. The key includes the numeric `client_id` needed
    in step 3.

The downloaded JSON contains `project_id`, `client_email`, and `client_id`.
You will use the first two in the LimaCharlie wizard and the numeric client ID
in Google Admin. Keep the key intact, including the private key's escaped line
breaks. Google's [credential creation guide](https://developers.google.com/workspace/guides/create-credentials)
provides the current console steps.

### 2. Enable the APIs

=== "Web console"

    1. In Google Cloud, select the project that owns the service account.
    2. Open **APIs & Services → Library**. Search for and open **Gmail API**, then
       select **Enable**. If it is already enabled, leave it enabled.
    3. Repeat for **Admin SDK API** and **Cloud Pub/Sub API**.
    4. Under **APIs & Services → Enabled APIs & services**, confirm all three are
       listed for this project.

    API IDs: `gmail.googleapis.com`, `admin.googleapis.com`, and
    `pubsub.googleapis.com`. See Google's [API enablement guide](https://docs.cloud.google.com/service-usage/docs/enable-disable).

=== "Cloud Shell / CLI"

    ```bash
    gcloud services enable gmail.googleapis.com admin.googleapis.com \
      pubsub.googleapis.com --project=<YOUR_PROJECT_ID>
    ```

### 3. Authorize the service account in the Workspace admin console

**Security → Access and data control → API controls → Domain-wide delegation →
Add new.** Paste the numeric client ID and the scopes as one comma-separated
line. Include `https://mail.google.com/` only if you want banners and reporter
replies.

*Verified by the `directory` check in the connection test.*

### 4. Create the notification topic

It **must** be in the same project as the service account — Gmail refuses a
topic in any other project.

=== "Web console"

    1. In that Google Cloud project, open **Pub/Sub → Topics → Create topic**.
    2. Set **Topic ID** to `mailsec-gmail-push`.
    3. Clear **Add a default subscription**; you will create the named subscription
       with the required settings in step 6. Leave the other optional features off.
    4. Select **Create** and confirm the topic appears in the list.

    See Google's [topic creation guide](https://docs.cloud.google.com/pubsub/docs/create-topic).

=== "Cloud Shell / CLI"

    ```bash
    gcloud pubsub topics create mailsec-gmail-push --project=<YOUR_PROJECT_ID>
    ```

### 5. Let Gmail publish to the topic

=== "Web console"

    1. In **Pub/Sub → Topics**, select `mailsec-gmail-push`. Open **Show info panel**
       if needed, then **Permissions → Add principal**.
    2. Enter `gmail-api-push@system.gserviceaccount.com` as the principal.
    3. Select **Pub/Sub Publisher** (`roles/pubsub.publisher`) and save. Apply this
       grant to the topic, not the entire project.
    4. Confirm this principal and role appear in the topic's permissions.

=== "Cloud Shell / CLI"

    ```bash
    gcloud pubsub topics add-iam-policy-binding mailsec-gmail-push \
      --project=<YOUR_PROJECT_ID> \
      --member="serviceAccount:gmail-api-push@system.gserviceaccount.com" \
      --role="roles/pubsub.publisher"
    ```

`gmail-api-push@system.gserviceaccount.com` is a Google-owned account outside
your organization. If a domain restriction blocks it, ask your Google Cloud
administrator to allow this publisher; do not substitute your service account.

*Verified by the `pubsub_watch` check.*

### 6. Create the subscription we read from

Create a **pull** subscription on the topic from step 4.

=== "Web console"

    1. Open **Pub/Sub → Subscriptions → Create subscription** in the same project.
    2. Set **Subscription ID** to `mailsec-gmail-push-sub` and choose the topic
       `mailsec-gmail-push` from this project.
    3. Select **Pull** as the delivery type. Set **Acknowledgement deadline** to
       **60 seconds** and leave the other settings at their defaults.
    4. Select **Create**. Confirm the subscription's topic and delivery type on
       its details page. If this subscription already exists, edit and verify it
       rather than creating a second subscription with a different name.

    See Google's [pull subscription guide](https://docs.cloud.google.com/pubsub/docs/create-subscription).

=== "Cloud Shell / CLI"

    ```bash
    gcloud pubsub subscriptions create mailsec-gmail-push-sub \
      --topic=mailsec-gmail-push --project=<YOUR_PROJECT_ID> --ack-deadline=60
    ```

### 7. Let us read the subscription

Grant access to the **same** service account you created in step 1.

=== "Web console"

    1. Open **Pub/Sub → Subscriptions** and select `mailsec-gmail-push-sub`.
    2. Open its information panel and **Permissions → Add principal**.
    3. Paste `client_email` from your JSON key, for example
       `limacharlie-mail@your-project.iam.gserviceaccount.com`.
    4. Select **Pub/Sub Subscriber** (`roles/pubsub.subscriber`) and save. Apply
       this grant to the subscription, not the entire project.
    5. Confirm the service account and role appear in the subscription's permissions.

    See Google's [Pub/Sub access-control instructions](https://docs.cloud.google.com/pubsub/docs/access-control#controlling_access_through_the_google_cloud_console).

=== "Cloud Shell / CLI"

    ```bash
    gcloud pubsub subscriptions add-iam-policy-binding mailsec-gmail-push-sub \
      --project=<YOUR_PROJECT_ID> \
      --member="serviceAccount:<SERVICE_ACCOUNT_EMAIL>" \
      --role="roles/pubsub.subscriber"
    ```

*Verified by the `pubsub_pull` check.*

## Store the credential

In the setup wizard's **Connection details**, choose **Credential → Add New**
and name the secret `gws-mail`. Paste the **complete downloaded JSON key** into
**Secret**, adding an `admin_email` property containing your Workspace
administrator's address as shown below. Select **Create**. The wizard saves and
selects the secret, then fills in the project ID and service account email from
the key. Keep the secret enabled. Do not replace the real private key with the
abbreviated example or wrap the JSON in an extra `secret` property.

The secret is the service-account JSON key **plus** the Workspace administrator
address to impersonate:

```json
{
  "admin_email": "admin@corp.example",
  "type": "service_account",
  "project_id": "<YOUR_PROJECT_ID>",
  "private_key_id": "<key-id>",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "<SERVICE_ACCOUNT_EMAIL>",
  "client_id": "<numeric-oauth2-client-id>",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

Alternatively, save the edited JSON as `gws-credential.json` and use the
configured LimaCharlie CLI:

```bash
limacharlie secret set --key gws-mail \
  --value "$(cat gws-credential.json)" --enabled --oid $OID
```

## Create the connection

Open **Email Security → Settings → Add connection → Google Workspace**. Select
`gws-mail` under **Credential**. If you selected an existing secret, copy
`project_id` and `client_email` from its original key into the project ID and
service account email fields. If you just created the secret here, these fields
are filled automatically. Choose the mailboxes for your pilot.
The wizard uses `mailsec-gmail-push` and `mailsec-gmail-push-sub`, matching the
resources created above. Complete the checklist, review, and save.

Run the connection diagnostic after saving. Enable **Verify notification
delivery** to test Gmail notifications as well as access. Then follow
[verify your first message](../getting-started.md#5-confirm-mail-is-arriving).
Google's [notification setup guide](https://developers.google.com/workspace/gmail/api/guides/push)
explains the topic, subscription, and Gmail publisher grant.

### Alternative: LimaCharlie CLI

```yaml
# gws.yaml
provider: gworkspace
credentials: hive://secret/gws-mail
ingest:
  mode: push
  backfill_days: 14
features:
  outbound_observation: true
  reports_mailbox: phishing@corp.example
  pubsub_topic: projects/<YOUR_PROJECT_ID>/topics/mailsec-gmail-push
  pubsub_subscription: projects/<YOUR_PROJECT_ID>/subscriptions/mailsec-gmail-push-sub
```

```bash
limacharlie hive set --hive-name mailsec_provider --key gws-prod \
  --input-file gws.yaml --enabled --oid $OID
```

Google Workspace supports `ingest.mode: push` only, and requires **both**
`pubsub_topic` and `pubsub_subscription`. An omitted, `auto` or `poll` mode—or a
push record that names nowhere to receive—is refused at save with the fields to
repair.

## Verify

```bash
limacharlie mailsec connection test gws-prod --oid $OID --output yaml
limacharlie mailsec connection test gws-prod --include-watch --oid $OID --output yaml
```

| Check | Required | Meaning if it fails |
|---|:--:|---|
| `credential` | ✅ | The service-account key is malformed, or `admin_email` is missing |
| `directory` | ✅ | `admin.directory.user.readonly` is not delegated |
| `mail_modify` | ✅ | `gmail.modify` is not delegated — no analysis or remediation |
| `mail_full` | — | `https://mail.google.com/` not delegated; banners and reporter replies are unavailable. Reported as `skipped`, and `ok` stays true |
| `mailbox_read` | ✅ | Delegation is in place but the directory returned nothing, or the impersonated admin cannot list users |
| `pubsub_pull` | ✅ | The service account lacks `roles/pubsub.subscriber` on the subscription, or the subscription name is wrong |
| `pubsub_watch` | ✅ (with `--include-watch`) | Gmail cannot publish to the topic — usually the missing publisher binding, or a topic outside the service account's project. Without the flag it is reported as `skipped` and is not required, because it is the one probe with a side effect |

`--include-watch` establishes a real Gmail watch and requires a real Pub/Sub pull
before lifecycle can pass. It is idempotent and the watch expires on its own.

## How ingestion works

- **Discovery** lists users per domain through the Admin SDK.
- **Push mode**: a `users.watch` per mailbox publishes to your topic; the
  collector pulls your subscription with the same service-account credential and
  reads the change history from the last known point. Watches are renewed on a
  daily schedule — Gmail expires them within seven days.
- Push is the only supported Workspace delivery mode. If Pub/Sub delivery is
  interrupted, coverage shows the connection degradation. Once delivery returns,
  the collector resumes from the stored Gmail history watermark rather than
  claiming a separate polling fallback.
- Sent mail is ingested as `direction: outbound`, observation-only.

!!! warning "Gmail cannot enumerate active watches"
    There is no Gmail API that lists the watches currently established for a
    domain, so reconciliation compares against **our** stored state rather than
    the provider's own view. That is a genuinely lower assurance than the
    Microsoft 365 side, and it is surfaced on every Workspace connection row
    rather than hidden. `--include-watch` is how you positively prove delivery.

## Remediation semantics

| Action | What happens in Gmail |
|---|---|
| `quarantine_message` | `INBOX` removed, an `LC Quarantine` label added — restorable, and out of the user's inbox |
| `trash_message` | `TRASH` added. The product's own quarantine label is removed afterwards, so the message's placement reads as trashed rather than still quarantined |
| `move_to_spam` | `SPAM` added, resolved through Gmail's own identifiers |
| `restore_message` | The labels are inverted |
| `banner_message` / `unbanner_message` | Gmail cannot edit a stored message, so the message is **replaced**: the banner-carrying copy is inserted before the original is deleted (so an interruption leaves a repairable duplicate rather than data loss), preserving thread, internal date and labels. **The provider message id changes**, and the new one is persisted. Requires `https://mail.google.com/`; without it the action is refused by name |

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `credential` fails | Key JSON malformed, or `admin_email` missing from the secret | Re-store the secret with `admin_email` included |
| `directory` fails | Delegation authorized against the service-account **email** instead of its **numeric client ID**, or a scope typo | Re-add the delegation with the numeric client ID and the exact scope strings |
| `mail_full` fails and banners are refused | `https://mail.google.com/` is not in the delegated scope list | Add it to the same delegation entry, or accept that banners and reporter replies are unavailable |
| `pubsub_watch` fails | Missing publisher binding for `gmail-api-push@system.gserviceaccount.com`, or the topic is in a different project | Add the binding; move the topic into the service account's project |
| `pubsub_pull` fails or times out | Missing `roles/pubsub.subscriber`, wrong subscription name, or the subscription is push rather than pull | Grant the role; recreate as a pull subscription |
| Banner "worked" but a later action fails | Something cached the pre-banner provider message id | Re-read `provider_message_id`; a Workspace banner mints a new one |
