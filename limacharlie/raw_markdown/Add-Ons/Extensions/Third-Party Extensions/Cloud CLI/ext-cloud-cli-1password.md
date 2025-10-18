---
title: 1Password
slug: ext-cloud-cli-1password
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-1password
articleId: 4881640d-f98f-42ea-be4b-347f00ca05be
---

* * *

1Password

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# 1Password

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

The 1Password CLI brings 1Password to the terminal, allowing you to interact with a 1Password instance from LimaCharlie.

This Extension makes use of 1Password's native CLI, which can be found [here](https://developer.1password.com/docs/cli).

1Password Account Types

Please note that some 1Password functionality is limited to 1Password Business. Please validate you have the correct type of account(s) to ensure that commands run.

## Example

Returns a list of all items the account has read access to by default.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "op" }}' 
        command_line: '{{ "item list" }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

To utilize 1Password's automated CLI capabilities, you will need to create and utilize a Service Account. More information can be found [here](https://developer.1password.com/docs/service-accounts/get-started/).

  * Create a secret in the secrets manager in the following format:



    
    
    serviceAccountToken
    

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

  * [ 1Password ](/docs/1password)



* * *

###### What's Next

  * [ AWS ](/docs/ext-cloud-cli-aws) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


