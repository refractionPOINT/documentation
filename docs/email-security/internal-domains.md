# Internal Domains and Message Direction

--8<-- "includes/email-security-beta.md"

Every message Email Security processes gets a `direction`:

| Direction | Meaning |
|---|---|
| `internal` | The sender belongs to your organization |
| `inbound` | The message came from outside your organization |
| `outbound` | A message your users sent, observed from their Sent mail |

Direction changes how a message is judged. Many default rules and signals apply
to inbound mail only, such as first-contact and impersonation checks, and sender
history is tracked differently for colleagues than for outside senders. A
partner domain wrongly treated as internal skips those inbound checks. One of
your own domains wrongly treated as external makes every colleague look like a
first-time sender.

Email Security decides whether a sender is internal by comparing the sender's
domain with your organization's domains. Most organizations never need to
configure that list, because Email Security builds it from your connected
tenants.

## How your domains are detected

Your organization's domains are the union of the following, across all your
connections:

1. **Mailbox domains.** The domain of every protected mailbox's primary address.
2. **Alias domains.** The domains of those mailboxes' alias and send-as addresses.
    - Microsoft 365: the user's SMTP proxy addresses, which includes the
      addresses added under a user's email aliases in the Microsoft 365 admin
      center.
    - Google Workspace: the user's aliases and non-editable aliases.
3. **The delivery mailbox.** The domain of the mailbox a message was delivered to.

Only protected mailboxes count. Guest accounts and directory entries that are
not protected by a connection do not add domains.

No extra permissions are needed. Detection reads the same directory data the
connection already uses for mailbox discovery: Microsoft Graph `User.Read.All`
for Microsoft 365, and the Admin SDK scope
`https://www.googleapis.com/auth/admin.directory.user.readonly` for Google
Workspace.

A subdomain of one of your domains is also internal. If `example.com` is yours,
mail from `mail.example.com` is internal. Sibling domains are not: if only
`sales.example.com` is yours, mail from `support.example.com` is inbound.

Detection follows mailbox discovery. A new alias is picked up on the next
discovery pass, and the updated list can take up to about 15 minutes to apply
to new mail.

## Safety rules

Some domains are never internal, whatever the directory says:

- **Shared mailbox providers**, such as `gmail.com`, `outlook.com` and
  `yahoo.com`, stay external even if one of your users has an alias there.
  Anyone can hold a mailbox on those domains, so treating one as internal would
  exempt every stranger on it from the inbound rules.
- **Google routing aliases** under `test-google-a.com` are ignored. Every
  Workspace tenant shares that parent domain.

Your Microsoft 365 tenant's own `yourtenant.onmicrosoft.com` domain is kept,
because only your tenant can hold it.

A matching domain alone does not make a message internal. If a message claims
to come from one of your domains but fails the receiving mail server's
authentication, it stays `inbound`. That covers a DMARC fail, an SPF fail, a
Microsoft composite authentication fail, or no authenticated identity that
belongs to your organization. Exact-domain spoofing is therefore still judged as
external mail.

## Additional internal domains

If your organization sends from a domain that has no mailbox or alias in the
connected tenant, add it yourself. Typical cases:

- A brand domain you send from through a relay or marketing platform.
- A newly acquired company whose mail has not been migrated yet.

Set it in the **Additional internal domains** field of the connection setup
wizard, or later by editing the connection under **Email Security → Settings**.

The setting affects direction only. It does not change which mailboxes the
connection protects.

Validation rules:

- Enter domains only, such as `example.net`, not addresses.
- Public suffixes such as `co.uk` are refused.
- Shared mailbox providers such as `gmail.com` are refused.
- Up to 100 domains per connection.

Domains are lowercased and de-duplicated on save.

### In the connection record

If you manage connections through the API, the CLI or infrastructure as code,
the list is `scope.internal_domains` on the `mailsec_provider` Hive record:

```yaml
provider: m365
credentials: hive://secret/m365-mail
scope:
  internal_domains:
    - example.net
    - example.org
```

```json
{
  "provider": "m365",
  "credentials": "hive://secret/m365-mail",
  "scope": {
    "internal_domains": ["example.net", "example.org"]
  }
}
```

!!! warning "`scope.domains` is a different setting"
    `scope.domains` limits which mailboxes the connection covers: only
    mailboxes in the listed domains are protected. Do not use it to mark a
    domain as internal, or you will stop protecting every mailbox outside it.
    Use `scope.internal_domains`. See
    [the connection record](providers.md#scope).

## See the effective list

In **Email Security → Settings**, each connection card has an **Internal
domains** section. Expand it to see the domains currently in effect for that
connection, each with its source:

| Source | Where the domain came from |
|---|---|
| **Mailbox domain** | A protected mailbox's primary address |
| **Alias domain** | An alias or send-as address of a protected mailbox |
| **Configured** | Your **Additional internal domains** (`scope.internal_domains`) |
| **Mailbox scope** | The connection's `scope.domains` |

If more than 1,000 domains are detected, only the first 1,000 are listed.

## Existing messages

Direction is set when a message is processed. Changing your domains, or adding
an alias, affects newly processed mail only. Messages already processed keep the
direction they were given.
