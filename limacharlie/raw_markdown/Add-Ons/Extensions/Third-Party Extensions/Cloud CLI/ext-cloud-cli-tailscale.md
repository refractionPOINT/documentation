---
title: Tailscale
slug: ext-cloud-cli-tailscale
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-tailscale
articleId: 28e0a0f2-4e08-42a0-9ef3-4d972c3251aa
---

* * *

Tailscale

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Tailscale

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

The Tailscale CLI brings Tailscale's powerful software-defined networking, based on WireGuard, to the command line. This Extension allows you to interact with a Tailscale network(s) from LimaCharlie.

This extension makes use of Tailscale's native CLI, which can be found [here](https://tailscale.com/kb/1031/install-linux).

## Example

Returns the current Tailscale status.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "tailscale" }}' 
        command_line: '{{ "status --json" }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

To utilize Tailscale's CLI capabilities, you will need:

  * An [auth key](https://tailscale.com/kb/1085/auth-keys)

  * Create a secret in the secrets manager in the following format:



    
    
    authKey
    

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

  * [ Tailscale ](/docs/adapter-types-tailscale)



* * *

###### What's Next

  * [ Vultr ](/docs/ext-cloud-cli-vultr) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


