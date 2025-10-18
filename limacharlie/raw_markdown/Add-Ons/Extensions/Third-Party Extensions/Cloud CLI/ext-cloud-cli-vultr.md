---
title: Vultr
slug: ext-cloud-cli-vultr
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-vultr
articleId: 6088beb9-c8de-4d9b-b573-c3b7255a4e6a
---

* * *

Vultr

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Vultr

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

The [Vultr](https://vultr.com/) CLI, or `vultr-cli`, is the official CLI for the Vultr API. With this component of the Cloud CLI Extension, you can interact with Vultr directly from LimaCharlie.

This extension makes use of Vultr's official CLI tool, which can be found [here](https://github.com/vultr/vultr-cli). Reference documentation can be found [here](https://www.vultr.com/news/how-to-easily-manage-instances-with-vultr-cli/).

## Example

The following example of a response action will enumerate a list of instance within a Vultr account.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "vultr-cli" }}' 
        command_line: '{{ "instance list" }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

To utilize `vultr-cli` capabilities, you will need:

  * A personal access token. To create one, click [here](https://my.vultr.com/settings/#settingsapi).

  * Your access token will need to have access control open to IPv6  
![Screenshot 2024-04-25 at 10.31.29 AM.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Screenshot%202024-04-25%20at%2010.31.29%E2%80%AFAM.png)

  * Create a secret in the secrets manager in the following format:
    
        personalAccessToken
    




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

###### What's Next

  * [ Atomic Red Team ](/docs/ext-atomic-red-team) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


