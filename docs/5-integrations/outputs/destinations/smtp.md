# SMTP

SMTP is one option to export data from LimaCharlie. You can send emails directly to an inbox for case management. You can also send high-priority detections to a shared on-call email.

To use the SMTP output, you need:

- An SMTP server that uses SSL
- Username and password to send through the SMTP server (if applicable)
- A destination email, to receive output

## Webapp Configuration

![smtp](../../../assets/images/smtp(1).png)

This output sends each event, detection, audit, deployment or log in a separate email.

- `dest_host`: the IP or DNS (and optionally the port) of the SMTP server that sends the email.
- `dest_email`: one or more email addresses that receive the email. To give more than one address, separate the addresses with commas (for example `soc@corp.com, oncall@corp.com`). Display names are supported (for example `SOC <soc@corp.com>`). Every address gets a copy and appears in the `To:` header.
- `cc_email`: (optional) one or more email addresses, separated with commas, to add to the `Cc:` header. Each address gets a copy.
- `bcc_email`: (optional) one or more email addresses, separated with commas, that get a copy but do not appear in the message headers (blind copy).
- `from_email`: the email address set in the From field.
- `username`: the username (if any) that authenticates to the SMTP server.
- `password`: the password (if any) that authenticates to the SMTP server.
- `secret_key`: a shared secret of your choice. It computes an HMAC (SHA256) signature of the email to check authenticity. This field is required. See the "Webhook Details" section below.
- `is_readable`: if 'true', the email format is HTML that a human can read instead of a machine.
- `is_starttls`: if 'true', use the Start TLS method to secure the connection instead of pure SSL.
- `is_authlogin`: if 'true', authenticate with `AUTH LOGIN` instead of `AUTH PLAIN`.
- `subject`: if specified, use this as the alternate "subject" line.

Example:

```text
dest_host: smtp.gmail.com
dest_email: soc@corp.com
from_email: lc@corp.com
username: lc
password: password-for-my-lc-email-user
secret_key: this-is-my-secret-shared-key
is_readable: true
is_starttls: false
is_authlogin: false
subject: LC Detection- <Name>
```

Example that sends to more than one recipient with `Cc` and `Bcc`:

```text
dest_host: smtp.gmail.com
dest_email: soc@corp.com, oncall@corp.com
cc_email: manager@corp.com
bcc_email: audit@corp.com
from_email: lc@corp.com
secret_key: this-is-my-secret-shared-key
is_readable: true
```

> Note: recipients in `dest_email` and `cc_email` appear in the message headers, so they can see each other. Use `bcc_email` for recipients that get a copy but stay hidden from the others. If an address in one of these fields is malformed, the output fails validation when you save it.

## Related articles

- [IMAP](../../../2-sensors-deployment/adapters/types/imap.md)

## What's Next

- [Splunk](splunk.md)
