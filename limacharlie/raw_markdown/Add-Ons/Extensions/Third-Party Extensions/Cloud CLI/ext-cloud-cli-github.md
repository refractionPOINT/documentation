---
title: GitHub
slug: ext-cloud-cli-github
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-github
articleId: 2dd5fa71-1699-4016-86e4-7f63e6e7168f
---

* * *

GitHub

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# GitHub

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

The GitHub CLI is a tool that brings GitHub to the terminal, allowing you to interact with and control Git accounts, repositories, organizations, and users from the CLI. With this component of the Cloud CLI Extension, you can interact with GitHub directly from LimaCharlie.

This extension makes use of the GitHub CLI, which can be found [here](https://cli.github.com/manual/).

## Example

The following example returns a list of GitHub organizations.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "gh" }}' 
        command_line: '{{ "org list" }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

To utilize the GitHub CLI, you will need:

  * A [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)

  * Create a secret in the secrets manager in the following format:



    
    
    access_token
    

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

  * [ Google Cloud ](/docs/ext-cloud-cli-google-cloud) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


