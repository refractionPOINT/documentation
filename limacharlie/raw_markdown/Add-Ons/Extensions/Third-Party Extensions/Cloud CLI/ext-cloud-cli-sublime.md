---
title: Sublime
slug: ext-cloud-cli-sublime
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-sublime
articleId: 87eace3f-2bb8-47bc-bc27-0c888203dcaf
---

* * *

Sublime

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Sublime

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

The Sublime Security CLI brings the power of Sublime's email platform to the command-line. With this component of the Cloud CLI Extension, you can interact with Sublime's email platform directly from LimaCharlie.

This extension makes use of Tailscale's native CLI, which can be found [here](https://docs.sublimesecurity.com/reference/analysis-api-cli). The CLI is a Python package - the source code can be found [here](https://github.com/sublime-security/sublime-cli).

## Example

The following response action returns information about the currently authentication Sublime Security user.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "sublime" }}' 
        command_line: '{{ "me" }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

To utilize Sublime's CLI capabilities, you will need:

  * You will need an API key. More information about provisioning an API key can be found [here](https://docs.sublimesecurity.com/reference/authentication).

  * Create a secret in the secrets manager in the following format:



    
    
    api_key
    

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

  * [ Sublime Security ](/docs/adapter-types-sublime-security)



* * *

###### What's Next

  * [ Tailscale ](/docs/ext-cloud-cli-tailscale) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


