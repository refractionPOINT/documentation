---
title: Webhook (Bulk)
slug: outputs-destinations-webhook-bulk
breadcrumb: Outputs > Output Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-webhook-bulk
articleId: 3b95c2f9-2a2f-4742-9328-09cd0790c380
---

* * *

Webhook (Bulk)

  * __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Webhook (Bulk)

  * __Updated on 05 Oct 2024
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

Output batches of events, detections, audits, deployments or artifacts through a POST webhook.

  * `dest_host`: the IP or DNS, port and page to HTTP(S) POST to, format `https://www.myorg.com:514/whatever`.

  * `secret_key`: an arbitrary shared secret used to compute an HMAC (SHA256) signature of the webhook to verify authenticity. This is a required field. [See "Webhook Details" section.](https://doc.limacharlie.io/docs/documentation/ZG9jOjE5MzExMTY-outputs#webhook-details)

  * `auth_header_name` and `auth_header_value`: set a specific value to a specific HTTP header name in the outgoing webhooks.

  * `sec_per_file`: the number of seconds after which a file is cut and uploaded.

  * `is_no_sharding`: do not add a shard directory at the root of the files generated.




Example:
    
    
    dest_host: https://webhooks.corp.com/new_detection
    secret_key: this-is-my-secret-shared-key
    auth_header_name: x-my-special-auth
    auth_header_value: 4756345846583498
    

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

  * [ Tutorial: Creating a Webhook Adapter ](/docs/tutorial-creating-a-webhook-adapter)



* * *

###### What's Next

  * [ Testing Outputs ](/docs/testing-outputs) __



Tags

  * [ outputs ](/docs/en/tags/outputs)


