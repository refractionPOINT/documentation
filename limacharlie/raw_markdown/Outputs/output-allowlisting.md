---
title: Adding Outputs to an Allow List
slug: output-allowlisting
breadcrumb: Outputs
source: https://docs.limacharlie.io/docs/output-allowlisting
articleId: 28578c65-81df-4145-ac82-07fbd1fd6667
---

* * *

Adding Outputs to an Allow List

  *  __06 Jun 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Adding Outputs to an Allow List

  *  __Updated on 06 Jun 2025
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

At LimaCharlie, we rely on infrastructure with auto-scalers, and thus do not have static IPs nor a CIDR that you can rely on for an allow list (or "whitelisting").

Typically, the concern around adding IPs to an allow list for Outputs is based on wanting to limit abuse and ensure that data from webhooks is truly coming from LimaCharlie and not other sources. To address this, we provide a `secret_key` parameter that can be used as a _shared secret_ between LimaCharlie and your webhook receiver. When we issue a webhook, we include a `lc-signature` header that is an HMAC of the content of the webhook using the shared `secret_key`.

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

###### What's Next

  * [ Output Billing ](/docs/output-billing) __



Tags

  * [ outputs ](/docs/en/tags/outputs)


