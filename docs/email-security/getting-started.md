# Getting Started with Email Security

--8<-- "includes/email-security-beta.md"

Connect your organization's Microsoft 365 or Google Workspace mail to analyze
messages for threats. You do not need to change mail routing or install software
on employees' computers. This walkthrough uses the web app. The provider guides offer **Web console**
tabs for browser setup and **Cloud Shell / CLI** tabs if you prefer commands.
No terminal is required for either provider.

Your first goal is to **connect a small set of mailboxes, verify access, and open
an analyzed message**. You can configure automated responses later.

## Before you start

Have these ready before enabling the trial:

| What you need | Where to get it |
|---|---|
| A LimaCharlie account and organization | Sign in to the console and select the organization that should hold the email data. An organization is your team's workspace. |
| Permission to enable Email Security and configure it | Ask your LimaCharlie organization administrator if you cannot subscribe, save a secret, add a connection, or run its test. |
| Administrator access to your mail provider | For Microsoft 365, someone must create an app registration and grant Microsoft Graph application permissions. For Google Workspace, you need a Workspace Super Admin and an administrator of a Google Cloud project. |
| A few mailbox addresses for a first test | Choose mailboxes you administer and can send an ordinary test message to. Personal Gmail and Outlook.com accounts are not this setup path. |

A **credential** is the key the product uses to access your mail provider. A
**secret** is the securely stored copy of that credential in LimaCharlie. A
**connection** combines that secret with your provider and mailbox choices.

!!! info "Trial limits"
    Free-tier organizations can try Email Security for **14 days**, with up to
    **25 mailboxes**. The clock starts when you subscribe, and resubscribing does
    not restart it. Prepare your administrator access first. At expiry ingestion
    pauses; data is removed 30 days later unless the organization moves off the
    free tier. See [trial details](policy.md#plans-the-free-trial-and-the-mailbox-cap).

## 1. Enable Email Security

In your LimaCharlie organization, open **Extensions**, find **Email Security**,
and subscribe. Then open **Email Security → Settings**.

If an action is unavailable, ask your organization administrator for access.
Connection management uses `mailsec_provider.get` and `mailsec_provider.set`;
saving credentials uses Secrets Manager permissions, and testing a connection
requires `mailsec.act`. Reading results requires `mailsec.get`.

New subscriptions start with **alert-only** automation: automatic rules record
what they would do without moving or modifying messages. The provider credential
still grants the access required for response actions. Actions you explicitly
run yourself can change mail even in alert-only mode.

<span id="2-grant-the-permissions"></span>
<span id="3-prepare-the-provider-credential"></span>

## 2. Prepare your mail provider and save its credential

Follow the guide for the service that hosts your mail:

- [Microsoft 365 setup](provider-setup/microsoft-365.md): create an application,
  grant access, and copy its tenant ID, client ID, and secret value.
- [Google Workspace setup](provider-setup/google-workspace.md): create a service
  account, authorize it in Workspace, and set up notification delivery in Google
  Cloud. The guide explains which console to use at each step.

Each guide shows the exact credential to save under **Organization Settings →
Secrets Manager**. Keep that console page in another browser tab so you can
return to the wizard. Save only the credential JSON in the secret's value field;
do not add an outer `secret` property. Remember the name you gave it, such as
`mailsec-primary`.

**Checkpoint:** you have a saved secret and have completed the provider's access
grants. Knowing the secret's name alone does not prove that access works; you
will test it after connecting.

<span id="4-connect-the-mail-tenant"></span>

## 3. Add the connection

Back in **Email Security → Settings**, select **Add connection** (or **Start
setup wizard** on an empty page), then select your provider.

The wizard includes the provider's access checklist. For Google Workspace,
connection details come first so the checklist can use your project ID.

| Field | What to enter |
|---|---|
| Connection name | A label you choose, such as `company-mail`. This is not a Microsoft or Google ID. |
| Saved secret name | The name from Secrets Manager, such as `mailsec-primary`. Do not paste the credential itself here. |
| Service account project ID (Google only) | The `project_id` in your downloaded key. It identifies the project containing the notification topic and subscription. |
| Service account email (Google only) | The `client_email` in that key. This fills in the setup commands; it is different from the Workspace administrator address. |
| Mailboxes to include | For a pilot, enter the mailbox email addresses separated by commas. Leaving this blank includes all discovered mailboxes, subject to other scope restrictions and your plan limit. |
| Reports mailbox (optional) | An existing mailbox where employees forward suspicious messages. Leaving it blank is fine; the User reports queue will stay empty. |
| Existing mail to analyze (days) | Keep 14 to analyze recent history, or enter 0 to start with new mail only. Historical analysis does not move old messages. |
| Observe outbound mail | Whether to analyze sent messages for signs of compromised accounts. Sent mail is observation-only. |

For a trial, keep your selected mailboxes within the 25-mailbox cap. If you use a
reports mailbox, include it in your pilot selection too. A selection in
LimaCharlie does not narrow the permissions granted to the application at your
mail provider. See [provider scope](providers.md) for domain, group, and exclusion
rules.

Review the summary and select **Save connection**. Saving starts setup and
collection; it does **not** prove the credential works.

<span id="5-verify-the-connection"></span>

## 4. Test access

The connection diagnostic opens after saving if you have permission. Select
**Run connection test**. You can reopen it using **Test connection** in Settings.

- **Required check failed:** read **How to fix it**, correct the provider grant
  or saved credential, then run the test again.
- **Optional check skipped or unavailable:** the connection may still work.
  Read which feature will be unavailable before deciding to add that permission.
- **Required checks passed:** access checks succeeded. Next, verify that mail is
  actually being collected.

For Google Workspace, enable **Verify notification delivery** to test the path
Gmail uses to announce new mail. This creates a real, temporary Gmail watch;
passing only credential checks does not verify notification delivery.

<span id="6-watch-coverage-fill-in"></span>
<span id="7-read-the-first-judged-message"></span>

## 5. Confirm mail is arriving

Open **Email Security → Overview** and check mailbox coverage counts and connection
health. Compare the protected count with the number you intended to include.
These are summary counts, not a per-mailbox checklist; verify individual pilot
mailboxes by sending test messages to them.

| State | What it means / what to do |
|---|---|
| Protected | The mailbox is being watched. Send it an ordinary new test message. |
| Discovered | The mailbox was found but is not yet protected. Check setup progress and the trial cap. |
| Excluded | The mailbox is outside the configured scope. Check your selection if this is unexpected. |
| Error | The mailbox could not be protected. Check the connection diagnostic and provider permissions. |

Then open **Email Security → Messages** and locate your test message. Open the
row to see its verdict (the analysis result), the signals behind it, and the
action history. A normal message need not produce a threat alert to prove that
collection works. See [Messages & Triage](messages.md) for interpreting results.

Recent historical mail also appears as it is analyzed. This **backfill** runs in
the background and can take hours, or days for a large environment. It does not
perform response actions or emit the live-mail automation events. You do not
need to wait for all history to finish before checking a new message.

## If you get stuck

| Problem | Next step |
|---|---|
| Cannot create the credential or grant access | Send your mail administrator the provider setup guide above. LimaCharlie access does not grant Microsoft or Google administrator access. |
| Connection saved but tests fail | Recheck the secret's contents and required grants. Saving checks configuration, not working access. |
| Tests pass but Messages is empty | Check Overview coverage counts, mailbox selection, the trial cap, and notification delivery. Send a new message to a protected mailbox. |
| User reports is empty | Confirm an existing reports mailbox is configured, included in scope, and receiving forwarded messages. |

More fixes: [Troubleshooting](troubleshooting.md).

<span id="8-decide-whether-the-product-may-act"></span>

## After your first successful test

Review a few messages before enabling automated responses. Read
[Policy → Automations](policy.md#automations): enforcement currently has an
organization-wide consent effect, so enabling one rule can authorize other
automated paths to act too. Expand mailbox coverage when you are ready.

For scripted setup, use [Setup with the CLI](setup-cli.md). The
[provider reference](providers.md) covers advanced configuration.
