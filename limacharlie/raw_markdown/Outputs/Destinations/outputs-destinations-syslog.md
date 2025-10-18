---
title: Syslog
slug: outputs-destinations-syslog
breadcrumb: Outputs > Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-syslog
articleId: 9371ac70-e5f0-4a64-8357-4e5d6f169c59
---

* * *

Syslog

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Syslog

  *  __Updated on 05 Oct 2024
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

## Syslog (TCP)

Output events and detections to a syslog target.

  * `dest_host`: the IP or DNS and port to connect to, format `www.myorg.com:514`.

  * `is_tls`: if `true` will output over TCP/TLS.

  * `is_strict_tls`: if `true` will enforce validation of TLS certs.

  * `is_no_header`: if `true` will not emit a Syslog header before every message. This effectively turns it into a TCP output.

  * `structured_data`: arbitrary field to include in syslog "Structured Data" headers. Sometimes useful for cloud SIEMs integration.




Example:
    
    
    dest_host: storage.corp.com
    is_tls: "true"
    is_strict_tls: "true"
    is_no_header: "false"
    

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

  * [ Syslog ](/docs/adapter-types-syslog)



* * *

###### What's Next

  * [ Tines ](/docs/output-destinations-tines) __



Table of contents

    * Syslog (TCP) 



Tags

  * [ outputs ](/docs/en/tags/outputs)


