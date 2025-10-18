---
title: LimaCharlie CLI
slug: limacharlie-cli
breadcrumb: Add-Ons > Extensions > LimaCharlie Extensions
source: https://docs.limacharlie.io/docs/limacharlie-cli
articleId: 98561e07-6563-4a5b-8dbd-54f98cc26368
---

* * *

LimaCharlie CLI

  *  __15 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# LimaCharlie CLI

  *  __Updated on 15 Oct 2024
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

LimaCharlie CLI Extension allows you to issue [LimaCharlie CLI commands](/v2/docs/limacharlie-sdk) using extension requests.

Repo - <https://github.com/refractionPOINT/python-limacharlie>

You may use a  rule to trigger a LimaCharlie CLI event. For example the following rule response actions:
    
    
    - action: extension request
      extension action: run
      extension name: limacharlie-cli
      extension request:
        command_line: '{{ "limacharlie configs push --dry-run --oid" }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

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

  * [ LimaCharlie SDK & CLI ](/docs/limacharlie-sdk)



* * *

###### What's Next

  * [ BinLib ](/docs/binlib) __



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


