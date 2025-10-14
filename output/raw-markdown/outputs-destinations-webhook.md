[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v2

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Webhook

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Webhook

* Updated on 05 Oct 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Output individually each event, detection, audit, deployment or artifact through a POST webhook.

* `dest_host`: the IP or DNS, port and page to HTTP(S) POST to, format `https://www.myorg.com:514/whatever`.
* `secret_key`: an arbitrary shared secret used to compute an HMAC (SHA256) signature of the webhook to verify authenticity. [See "Webhook Details" section.](https://doc.limacharlie.io/docs/documentation/ZG9jOjE5MzExMTY-outputs#webhook-details)
* `auth_header_name` and `auth_header_value`: set a specific value to a specific HTTP header name in the outgoing webhooks.

Example:

```
dest_host: https://webhooks.corp.com/new_detection
secret_key: this-is-my-secret-shared-key
auth_header_name: x-my-special-auth
auth_header_value: 4756345846583498
```

Example [hook to Google Chat](https://developers.google.com/chat/how-tos/webhooks):

```
dest_host: https://chat.googleapis.com/v1/spaces/AAAA4-AAAB/messages?key=afsdfgfdgfE6vySjMm-dfdssss&token=pBh2oZWr7NTSj9jisenfijsnvfisnvijnfsdivndfgyOYQ%3D
secret_key: gchat-hook-sig42
custom_transform: |
   {
      "text": "Detection {{ .cat }} on {{ .routing.hostname }}: {{ .link }}"
   }
```

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### Related articles

* [Tutorial: Creating a Webhook Adapter](/docs/tutorial-creating-a-webhook-adapter)

---

###### What's Next

* [Webhook (Bulk)](/docs/outputs-destinations-webhook-bulk)

Tags

* [outputs](/docs/en/tags/outputs)
