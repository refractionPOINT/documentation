---
title: Microsoft 365
slug: ext-cloud-cli-microsoft365
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-microsoft365
articleId: 95b2264f-d90d-4f0e-a854-2db799e9b9d6
---

* * *

Microsoft 365

  *  __10 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Microsoft 365

  *  __Updated on 10 Oct 2024
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

The CLI**for Microsoft 365** is a tool created to help manage Microsoft 365 tenant(s) and SharePoint framework projects. With this component of the Cloud CLI Extension, you can interact with a Microsoft 365 tenant(s) directly from LimaCharlie.

This extension makes use of the PnP Microsoft 365 CLI, which can be found [here](https://github.com/pnp/cli-microsoft365).

## Example

The following example disables the user account with the provided user ID.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "m365" }}' 
        command_tokens:
          - entra
          - user
          - set
          - '--id'
          - '{{ .event.user_id  }}'
          - '--accountEnabled'
          - false
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

  * Per the Microsoft 365 CLI documentation, there are multiple login or authentication mechanisms available. The current LimaCharlie implementation utilizes a client secret for authentication. More information on provisioning client secrets can be found [here](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app).

  * Upon invocation, LimaCharlie will first run the `m365 login` command with the credentials provided.

  * Create a secret in the secrets manager in the following format:
    
        appID/clientSecret/tenantID




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

  * [ Microsoft 365 ](/docs/adapter-types-microsoft-365)



* * *

###### What's Next

  * [ Okta ](/docs/ext-cloud-cli-okta) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ azure ](/docs/en/tags/azure)
  * [ extensions ](/docs/en/tags/extensions)
  * [ m365 ](/docs/en/tags/m365)


