---
title: Webhook
slug: outputs-destinations-webhook
breadcrumb: Outputs > Output Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-webhook
articleId: 257ec159-6aa1-450f-b78c-6e24762ae554
---

* * *

Webhook

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Webhook

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

Output individually each event, detection, audit, deployment or artifact through a POST webhook.

  * `dest_host`: the IP or DNS, port and page to HTTP(S) POST to, format `https://www.myorg.com:514/whatever`.

  * `secret_key`: an arbitrary shared secret used to compute an HMAC (SHA256) signature of the webhook to verify authenticity. [See "Webhook Details" section.](https://doc.limacharlie.io/docs/documentation/ZG9jOjE5MzExMTY-outputs#webhook-details)

  * `auth_header_name` and `auth_header_value`: set a specific value to a specific HTTP header name in the outgoing webhooks.




Example:
    
    
    dest_host: https://webhooks.corp.com/new_detection
    secret_key: this-is-my-secret-shared-key
    auth_header_name: x-my-special-auth
    auth_header_value: 4756345846583498
    

Example [hook to Google Chat](https://developers.google.com/chat/how-tos/webhooks):
    
    
    dest_host: https://chat.googleapis.com/v1/spaces/AAAA4-AAAB/messages?key=afsdfgfdgfE6vySjMm-dfdssss&token=pBh2oZWr7NTSj9jisenfijsnvfisnvijnfsdivndfgyOYQ%3D
    secret_key: gchat-hook-sig42
    custom_transform: |
       {
          "text": "Detection {{ .cat }} on {{ .routing.hostname }}: {{ .link }}"
       }
    

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

  * [ Webhook (Bulk) ](/docs/outputs-destinations-webhook-bulk) __



Tags

  * [ outputs ](/docs/en/tags/outputs)


