# Protecting VIP identities

--8<-- "includes/email-security-availability.md"

VIP settings protect names and email addresses that attackers may impersonate,
such as executives and finance staff. In **Email Security → Policy → Protected
identities**, add each VIP's display name, email address and optional title.
Titles provide context; they do not establish identity.

## Bind platform accounts

A platform notification may show a VIP's name even when an outside account acted.
Account bindings let Email Security distinguish configured accounts from namesakes.
Edit the VIP and use **Add platform account** to enter:

- **GitHub:** the account's login, without `@` or a profile URL.
- **Google:** the exact Google account email used to share the document or file.

Add only accounts you have independently confirmed belong to that VIP. Each VIP
supports up to eight accounts. Values are trimmed and lowercased. GitHub logins
contain 1–39 ASCII letters or digits with single internal hyphens. Google values
must be plain ASCII email addresses. Wildcards and bot names are unsupported;
Google aliases, plus tags and dotted addresses are compared exactly.

Update or remove bindings after an account rename, reassignment or ownership
change. GitHub's old usernames can become available to other people after a
[username change](https://docs.github.com/en/account-and-profile/concepts/username-changes).

## What verification proves

A matching display name alone never establishes account ownership. Email Security
requires a supported canonical notification, receiver-verified aligned platform
DMARC and DKIM, and a provider-controlled actor identifier covered by the message's
signature. GitHub PR, issue and comment notifications can supply a signed sender
login. Google Drive/Docs/Sheets share notifications can supply the sharing account's
email in the provider's invitation header.

Supported notifications from a configured account receive **Verified VIP account**
in the message drawer when their name findings were interpreted. This removes
only the supported VIP-name impersonation contribution. Credential or payment
requests, payloads, malicious or external destinations, incomplete inspection and
independent threat findings still receive their normal checks. Account verification
does not establish that the content or account is safe from compromise.

Missing bindings, mismatched accounts, failed authentication and unknown templates
retain the existing checks. Display names, authored comments/titles/messages,
mentions, assignees, avatar links and opaque reply tokens are not account proof.
Google comment notifications without a provider-issued actor account identifier
remain unverified, even if their name matches a configured VIP. Other platforms
remain unsupported until reliable actor identifiers are available.

## Configure with Hive

The console and Hive use the same optional field on each VIP:

```yaml
policy_type: vips
vips:
  - name: Example Executive
    email: executive@example.test
    title: Finance director
    platform_identities:
      - platform: github
        login: executive-example
      - platform: google
        email: executive@example.test
```

Use the existing `mailsec_policy` record workflow in the [Policy Reference](policy.md).
VIP lookup-list metadata supports the same `platform_identities` field in both
email-keyed and name-keyed entries. Inline VIP settings take precedence over
lookup entries for the same identity. Invalid account metadata preserves name/email
protection and reports a configuration problem; it never grants verification.

## Preview limitations

`mailsec analyze --with-org-context` can read current VIP bindings and reports
`vip_account_binding` availability. Submitted EML cannot establish receiver
authentication from its own headers, so it cannot receive verified actor credit.
Use retained delivery evidence to confirm that the interpretation applied. Changing
a binding affects future judgements; it does not automatically clear retained mail
or change mailbox placement.
