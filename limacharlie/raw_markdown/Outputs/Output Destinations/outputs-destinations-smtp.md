---
title: SMTP
slug: outputs-destinations-smtp
breadcrumb: Outputs > Output Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-smtp
articleId: b211d7cb-c672-4f8d-8d36-3e9db4a8c345
---

* * *

SMTP

  *  __08 Oct 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# SMTP

  *  __Updated on 08 Oct 2025
  *  __ 1 Minute to read 



  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




* * *

Article summary

 __

Did you find this summary helpful? __ __ __ __

__

Thank you for your feedback!

One option to export data from LimaCharlie is via SMTP, allowing you to send emails directly to a ticketing inbox or send high-priority detections to an on-call, shared email.

To utilize SMTP output, you will need:

  * An SMTP server that utilizes SSL

  * Username and password to send through the SMTP server (if applicable)

  * A destination email, to receive output




## Webapp Configuration

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/smtp\(1\).png)

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
    

* * *

Was this article helpful?

__Yes __No

 __

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change  


Please enter a valid email

Cancel

* * *

###### Related articles

  * [ IMAP ](/docs/adapter-types-imap)



* * *

###### What's Next

  * [ Splunk ](/docs/outputs-destinations-splunk) __



Table of contents

    * Webapp Configuration 



Tags

  * [ outputs ](/docs/en/tags/outputs)


