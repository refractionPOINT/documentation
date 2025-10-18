---
title: StrongDM
slug: ext-cloud-cli-sdm
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-sdm
articleId: 985129ae-6c32-4ed2-a802-781063c0bed7
---

* * *

StrongDM

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# StrongDM

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

The StrongDM CLI allows you to manage your StrongDM platform(s) via the command-line. With this component of the Cloud CLI Extension, you can interact with StrongDM's directly from LimaCharlie.

More information about the StrongDM CLI can be found [here](https://www.strongdm.com/docs/cli/).

## Example

The following response action returns a list of all users in your Organization.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "sdm" }}' 
        command_line: '{{ "admin users list" }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

To utilize StrongDM's CLI capabilities, you will need:

  * An admin or service account token. More information on provisioning this token can be found [here](https://www.strongdm.com/docs/admin/tokens-and-keys/).

  * Create a secret in the secrets manager in the following format:



    
    
    token
    

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

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

  * [ Sublime ](/docs/ext-cloud-cli-sublime) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


