---
title: VirusTotal
slug: api-integrations-virustotal
breadcrumb: Add-Ons > API Integrations
source: https://docs.limacharlie.io/docs/api-integrations-virustotal
articleId: 55a72bf8-3c34-4035-8031-f052de7e8b72
---

* * *

VirusTotal

  *  __29 Aug 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# VirusTotal

  *  __Updated on 29 Aug 2025
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

## API Keys

The VirusTotal API key is added via the [ _integrations_](https://docs.limacharlie.io/v2/docs/add-ons-api-integrations#configuration) menu within LimaCharlie.

## Usage

With the `vt`[ add-on](https://app.limacharlie.io/add-ons/detail/vt) subscribed and a VirusTotal API Key configured in the Integrations page, VirusTotal can be used as an API-based lookup.
    
    
    event: CODE_IDENTITY
    op: lookup
    path: event/HASH
    resource: hive://lookup/vt
    metadata_rules:
      op: is greater than
      value: 1
      path: /
      length of: true
    

Step-by-step, this rule will do the following:

  * Upon seeing a `CODE_IDENTITY` event, retrieve the `event/HASH` value and send it to VirusTotal via the `api/vt` resource.

  * Upon receiving a response from `api/vt`, evaluate it using `metadata_rules` to see if the length of the response is greater than 1 (in this case meaning that more than 1 vendor reporting a hash is bad).




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

  * [ VirusTotal Integration ](/docs/tutorials-integratons-virustotal-integration)



* * *

###### What's Next

  * [ Extensions ](/docs/extensions) __



Table of contents

    * API Keys 
    * Usage 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)


