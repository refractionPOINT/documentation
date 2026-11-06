# Controlling Access to Mail Content

--8<-- "includes/email-security-availability.md"

Email Security reads your users' mail, so the first access question for a new
deployment is who in your organization may read it. This guide walks through the
two controls that answer it: the `mailsec.*` permissions, and a
[Resource ACL](../7-administration/access/resource-acls.md) on the mailbox sensors.

Set this up before you invite analysts, or before you connect a provider if you
can. The default roles give mail access to more people than most teams expect.

## Where mail content lives

LimaCharlie keeps mail content in two places, and each place has its own gate.

| Where | What it holds | Who can read it |
|---|---|---|
| The Email Security message store | The queue, the message drawer, campaigns, user reports, the action audit, and the original message bytes | Anyone with `mailsec.get`. The original bytes also need `mailsec.get.eml` and a justification |
| Organization telemetry | The `EMAIL_*` events on the mailbox sensors. `EMAIL_MESSAGE` carries the whole parsed message, body included. Detections built from these events carry it too | Anyone who can read events or detections (`insight.evt.get`, `insight.evt.get.simple`, `insight.det.get`), unless a Resource ACL restricts the sensors |

The configuration that drives the product is a third, smaller place: the
provider credential, the connection record and the mail policy are
[Hive records](automation.md#configuration-as-code), gated by Hive permissions and
optionally by ACL tags on the records.

The two controls in this guide line up with the two places:

- **Permissions** decide who can use the Email Security console, CLI, API and
  MCP tools.
- **A Resource ACL** decides who can read the mail events in the timeline, in
  LCQL search, in detections and in outputs.

Resource ACLs do **not** apply to the Email Security message store. Anyone holding
`mailsec.get` sees every protected mailbox in the organization, whatever `acl:`
tags the mailbox sensors carry. Plan your permissions with that in mind.

## Step 1: Decide who gets which permission

Email Security has four permissions of its own. They are described in
[Overview → Permissions](index.md#permissions).

| Permission | Lets the holder |
|---|---|
| `mailsec.get` | Read the queue and the drawer, including message bodies, plus campaigns, sender profiles, user reports, the action audit and coverage |
| `mailsec.set` | Change triage state, such as resolving a user report |
| `mailsec.act` | Remediate live mail at the provider (quarantine, trash, release, banner) and run the connection test |
| `mailsec.get.eml` | Download a message's original bytes. Only works together with `mailsec.get`, and every download needs a written justification |

Connections and policy use ordinary Hive permissions: `mailsec_provider.*` for
connections, `secret.*` for credentials, and `mailsec_policy.*`, `dr-mail.*` and
`lookup.*` for policy, rules and VIP lists.

### What the predefined roles grant

| Role | Email Security permissions | Can read mail events in telemetry |
|---|---|---|
| Owner | All of them | Yes |
| Administrator | `mailsec.get`, `mailsec.set`, `mailsec.act`, `mailsec.get.eml`, and `mailsec_provider.*` | Yes |
| Operator | `mailsec.get`, `mailsec.set`, `mailsec.act` | Yes |
| Viewer | `mailsec.get` | Yes |
| Basic | None | No |

Two things in this table surprise people:

- **Viewer reads mail.** `mailsec.get` shows message bodies in the drawer, so
  every Viewer can read every protected mailbox. If you give Viewer to people
  outside the mail team, such as auditors or a help desk, remove `mailsec.get`
  from them or give them a custom permission set.
- **Every role above Basic can read mail events**, even without any `mailsec.*`
  permission, because the events are ordinary telemetry. Step 2 closes that
  path.

Permissions are stored on the user when the role is assigned. A user who was
given a role before Email Security existed in your organization's role
definitions keeps the permissions they had then. Check with
`limacharlie user permissions list` rather than assuming.

### Suggested access levels

| Person | Grant |
|---|---|
| Mail administrator, who connects tenants and edits policy | `mailsec.get`, `mailsec.set`, `mailsec.act`, `mailsec_provider.*`, `mailsec_policy.*`, `dr-mail.*`, `secret.set`, `secret.get.mtd` |
| Mail analyst, who triages and remediates | `mailsec.get`, `mailsec.set`, `mailsec.act` |
| Mail reviewer, read-only | `mailsec.get` |
| Investigator who needs original messages for an incident | The analyst set, plus `mailsec.get.eml`, granted to named people only |
| Everyone else in the SOC | No `mailsec.*` permission, and not a member of the ACL scope from Step 2 |

The full list of what setup needs, permission by permission, is in
[Setup with the CLI → Grant the permissions](setup-cli.md#2-grant-the-permissions).

### Granting and removing permissions

From the CLI:

```bash
# Start from a role, then adjust.
limacharlie user permissions set-role --email analyst@example.com --role Operator --oid $OID

# Give one investigator the right to download original messages.
limacharlie user permissions add --email investigator@example.com \
  --permission mailsec.get.eml --oid $OID

# Take mail access away from a Viewer who should not read mail.
limacharlie user permissions remove --email auditor@example.com \
  --permission mailsec.get --oid $OID
```

`set-role` replaces all of the user's current permissions. In the web console, the
same changes are made from the organization's **Users** page. See
[User Access](../7-administration/access/user-access.md) for groups and for
managing access across several organizations.

Automation that calls Email Security should use an
[API key](../7-administration/access/api-keys.md) holding only what it needs. A
SOAR playbook that quarantines messages needs `mailsec.get` and `mailsec.act`, and
nothing that lets it download originals:

```bash
limacharlie api-key create --name mail-soar --permissions mailsec.get,mailsec.act --oid $OID
```

## Step 2: Restrict the mail events with a Resource ACL

Every protected mailbox is a sensor on the `email` platform, and each connection
also has its own sensor, `mailsec-<connection name>`. See
[Events & Automation → The sensors](automation.md#the-sensors). Without an ACL,
anyone who can search the organization's telemetry can read message bodies from
`EMAIL_MESSAGE`, with or without `mailsec.get`.

A Resource ACL scope fixes this. You tag the mail sensors `acl:<scope>`, and from
then on only members of the scope can read their events and detections. Everyone
else still sees that the sensors exist, with their hostnames (the mailbox
addresses), tags and online status. The general mechanism is described in
[Resource ACLs](../7-administration/access/resource-acls.md). The steps below
apply it to Email Security, using a scope named `email`.

You need `acl.set` for these steps, plus `ikey.set` and `sensor.tag`. The Owner
and Administrator roles include `acl.set`, but only for users who were assigned the
role after ACLs were introduced. See
[Resource ACLs → Permissions](../7-administration/access/resource-acls.md#permissions).

### 2.1 Create the scope in warn-only mode

List the people and keys that should read mail events. Use user IDs rather than
email addresses, so that the members' personal API keys are covered too, and use
an organization group if your mail team already has one.

```yaml
# email.yaml
data:
  members:
    - type: user
      id: "<mail administrator UID>"
    - type: user
      id: "<mail analyst UID>"
    - type: group
      id: "<mail team group ID>"
  warn_only: true
```

```bash
limacharlie hive set --hive-name acl --key email --input-file email.yaml --enabled --oid $OID
```

Always pass `--enabled`. A disabled scope locks the tagged sensors for everyone,
members included. `warn_only: true` lets you find out who would lose access before
anyone does.

### 2.2 Tag each connection's installation key

Email Security creates one installation key per connection, described as
`email security ingestion (<connection name>)` and tagged `lc:system,mailsec`.
Every mailbox sensor enrolls through it, and an installation key stamps its tags on
every sensor that enrolls with it. Tagging the key therefore covers the mailboxes
that appear later, for example when a new employee starts receiving mail.

Find the keys:

```bash
limacharlie installation-key list --oid $OID --output yaml
```

The CLI has no command to edit a key, so update it through the API. Pass the key's
`iid`, its description and its **full** tag list: the update replaces the tags, so
keep `lc:system` and `mailsec` and add the scope.

```bash
limacharlie api -X POST 'installationkeys/{oid}' \
  -f iid=<IID> \
  -f 'desc=email security ingestion (<connection name>)' \
  -f 'tags=lc:system,mailsec,acl:email' \
  --oid $OID
```

Repeat for each connection. Check the result with
`limacharlie installation-key get --iid <IID> --oid $OID`.

### 2.3 Tag the mailbox sensors that already exist

The key's tags only reach sensors that enroll after the change. Tag the existing
mail sensors directly:

```bash
limacharlie tag mass-add --selector 'plat == email' --tag acl:email --oid $OID
```

Run it again a few minutes later. Tags from an installation key are applied right
after enrollment, so a mailbox that enrolled while you were editing the keys can
miss both steps.

Confirm that every mail sensor carries the tag:

```bash
limacharlie tag find --tag acl:email --oid $OID --output yaml
limacharlie sensor list --selector 'plat == email' --oid $OID --output yaml
```

### 2.4 Fix what the restriction would break

Before you enforce the scope, update the things that read mail events on behalf of
the organization. Each of these keeps working in warn-only mode and stops once the
scope is enforced.

**Outputs.** Events and detections from restricted sensors are excluded from
outputs by default, including outputs that already exist. If you stream
`EMAIL_*` events or mail detections to a SIEM, add the scope to that output's
`acl_scopes`. See
[Resource ACLs → Outputs](../7-administration/access/resource-acls.md#outputs).

**D&R rules that act on mail.** Three response actions send event content out of
the platform and are refused on restricted events: `extension request`,
`service request` and `start ai agent`. The `ask ai` operator is refused too. That
covers the most common Email Security automations:

- a rule that quarantines, trashes or banners a message through
  `extension request` to `ext-email-security`
  ([Acting on mail from a D&R rule](automation.md#acting-on-mail-from-a-dr-rule))
- AI triage with `start ai agent` ([AI Triage](ai-triage.md))
- AI triage with `ask ai` ([AI Triage with ask ai](ask-ai-triage.md))

Add the scope to each such rule, at the top level next to `detect` and `respond`:

```yaml
acl_scopes:
  - email
```

Saving `acl_scopes` requires membership in every listed scope, or `acl.set`. Keep
the field whenever you rewrite the rule: `limacharlie dr set --detect ... --respond
...` writes only `detect` and `respond`, which removes the scopes. Save the whole
rule with `limacharlie hive set --hive-name dr-general` instead. Rules that only
`report` need no change. Details are in
[Resource ACLs → D&R rules](../7-administration/access/resource-acls.md#dr-rules).

**Extensions and AI sessions.** An extension that reads mail sensors, or an AI
agent that searches mail events, reads as its own API key. Add that key's name as
an `api_key` member of the scope. See
[Resource ACLs → Extensions](../7-administration/access/resource-acls.md#extensions).

Listing a scope on a rule or adding a key to it is a decision to let that rule or
key carry restricted mail content. An `ask ai` rule with `acl_scopes` sends message
content to your AI provider. Make each of these decisions on purpose.

### 2.5 Watch, then enforce

While the scope is warn-only, every read it would have refused is reported as an
organization error under `acl/email`, naming the user or key and the resource:

```bash
limacharlie org errors --oid $OID --output yaml
```

The organization keeps the most recent violation per scope, reported about once
every 15 minutes, so leave warn-only on long enough to see your regular users and
automations come through. Add the ones that should read mail events. For everyone
else, a refusal is the point.

When the errors only name people who should not read mail, remove `warn_only`
from `email.yaml` (or set it to `false`) and apply the record again:

```bash
limacharlie hive set --hive-name acl --key email --input-file email.yaml --enabled --oid $OID
```

### What changes for people outside the scope

- The mailbox sensors still appear in the sensor list, with the mailbox address as
  the hostname.
- The timeline, LCQL search and Replay return no `EMAIL_*` events from those
  sensors. Results are filtered, not refused, so a search returns fewer rows rather
  than an error.
- Detections from the mail sensors are hidden.
- Live event streams in the console carry only the scopes the viewer holds.
- **The Email Security console is unchanged.** If they hold `mailsec.get`, they
  still read the queue and the drawer.

Email Security itself keeps working: it reads its own configuration and writes its
events as the platform, not as a user, so ingestion, verdicts and remediation are
not affected by the scope.

## Step 3: Restrict the credentials and connection records (optional)

The provider credential in the `secret` Hive is the most sensitive piece of the
configuration. For an IMAP connection it is a mailbox password; for Microsoft 365
and Google Workspace it grants read access to every mailbox in scope. Anyone with
`secret.get` can read it.

Tag the credential and the connection record with the same scope:

```bash
limacharlie hive set --hive-name secret --key <credential secret name> --tag-add acl:email --oid $OID
limacharlie hive set --hive-name mailsec_provider --key <connection name> --tag-add acl:email --oid $OID
```

Users outside the scope then see each record's name and metadata, but its `data`
comes back as `{"acl_restricted": true}`, and they cannot overwrite it from that
view. Ingestion is not affected. You can tag `mailsec_policy`, `dr-mail` and VIP
`lookup` records the same way if your policy or VIP lists are themselves
sensitive.

Adding or removing an `acl:` tag on a Hive record needs `acl.set` on top of the
Hive's own `set` permission.

## Step 4: Audit who read mail

Access controls decide who *can* read mail. The audit trail records who *did*.

| Question | Where to look |
|---|---|
| Who opened a message in the console or read its body through the API? | The `mailsec_message_content_read` audit event, with `content: mdm` |
| Who downloaded an original message, and why? | The same audit event with `content: eml`, which carries the justification. Every download attempt, served or refused, is also an `EMAIL_ACTION` event with `action: get_eml` and a row in the [action audit](messages.md#the-audit-trail) |
| Who changed the ACL scope, or added or removed an `acl:` tag? | The organization audit log: scope changes are `acl` Hive writes, and tag changes are recorded as their own entries |
| Who would have been refused while the scope was warn-only? | Organization errors under `acl/<scope>` |

```bash
limacharlie audit list --event-type mailsec_message_content_read \
  --start $(date -d '7 days ago' +%s) --end $(date +%s) --oid $OID
```

Reading the audit log needs `audit.get`. Details of the content-read event, and how
often it is written, are in
[Messages & Triage → Who read a message](messages.md#who-read-a-message-the-content-read-audit-event).

## Limits to know

- **No per-mailbox access in the Email Security console.** `mailsec.get` covers
  every protected mailbox in the organization. You cannot let one analyst triage
  the sales mailboxes but not the executive ones.
- **`acl.set` can see everything in the telemetry.** Holding `acl.set` does not
  grant read access by itself, but its holder can add themselves to the scope.
  Treat it as equivalent to membership.
- **ACLs never grant access.** A scope member still needs the normal permission,
  such as `insight.evt.get`, to read events.
- **Exports drop restricted events.** Exporting query or Replay results to an
  output drops every restricted record, whatever scopes you hold.
- **Audit logs are not restricted.** The content-read events name the mailbox
  address and message ID, not the content, and anyone with `audit.get` can read
  them.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Mail events disappeared from the SIEM after you enforced the scope | The output does not list the scope | Add `email` to the output's `acl_scopes` |
| Automatic quarantine stopped, and `org errors` shows `cannot run "extension request"` | The remediation rule does not list the scope | Add `acl_scopes` to the rule |
| AI triage stopped, and `org errors` shows `cannot run "ask ai"` or `cannot run "start ai agent"` | The triage rule does not list the scope | Add `acl_scopes` to the rule |
| A new mailbox's events are visible to everyone | The mailbox enrolled through a key without the `acl:` tag, or before the tag was applied | Tag the connection's installation key (2.2), then re-run the `tag mass-add` from 2.3 |
| Nobody, members included, can read mail events | The `email` scope record is missing, disabled or expired | Recreate it, or apply it again with `--enabled`. Deleting or disabling a scope locks its sensors, it does not unlock them |
| A user outside the scope can still read message bodies | They hold `mailsec.get`. The scope does not cover the Email Security console | Remove `mailsec.get` from the user |
| A member lost access to mail events through a personal API key | The member is listed by email address | List the member by user ID |

## See also

- [Resource ACLs](../7-administration/access/resource-acls.md)
- [User Access](../7-administration/access/user-access.md)
- [Reference: Permissions](../8-reference/permissions.md)
- [Messages & Triage](messages.md)
- [Events & Automation](automation.md)
- [Data Residency & Encryption](data-residency.md)
