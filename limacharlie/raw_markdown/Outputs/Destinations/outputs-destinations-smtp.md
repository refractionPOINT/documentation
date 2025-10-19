# SMTP

One option to export data from LimaCharlie is via SMTP, allowing you to send emails directly to a ticketing inbox or send high-priority detections to an on-call, shared email.

To utilize SMTP output, you will need:

  * An SMTP server that utilizes SSL

  * Username and password to send through the SMTP server (if applicable)

  * A destination email, to receive output




## Webapp Configuration

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/smtp(1).png)

Output individually each event, detection, audit, deployment or log through an email.

  * `dest_host`: the IP or DNS (and optionally port) of the SMTP server to use to send the email.

  * `dest_email`: the email address to send the email to.

  * `from_email`: the email address set in the From field.

  * `username`: the username (if any) used to authenticate to the SMTP server.

  * `password`: the password (if any) used to authenticate to the SMTP server.

  * `secret_key`: an arbitrary shared secret used to compute an HMAC (SHA256) signature of the email to verify authenticity. This is a required field. See "Webhook Details" section below.

  * `is_readable`: if 'true' the email format will be HTML and designed to be readable by a human instead of a machine.

  * `is_starttls`: if 'true', use the Start TLS method of securing the connection instead of pure SSL.

  * `is_authlogin`: if 'true', authenticate using `AUTH LOGIN` instead of `AUTH PLAIN`.

  * `subject`: is specified, use this as the alternate "subject" line.




Example:
    
    
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
