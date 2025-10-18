---
title: DigitalOcean
slug: ext-cloud-cli-digitalocean
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-digitalocean
articleId: 58898079-357b-4da2-b117-21e9d35c4189
---

* * *

DigitalOcean

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# DigitalOcean

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

The DigitalOcean CLI, or `doctl`, is the official CLI for the DigitalOcean API. With this component of the Cloud CLI Extension, you can interact with DigitalOcean directly from LimaCharlie.

This extension makes use of DigitalOcean's official CLI tool, which can be found [here](https://github.com/digitalocean/doctl). Reference documentation can be found [here](https://docs.digitalocean.com/reference/doctl/reference/).

## Example

The following example of a response action will enumerate a list of compute droplets within a DigitalOcean instance.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "doctl" }}' 
        command_line: '{{ "compute droplet list" }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

To utilize `doctl` capabilities, you will need:

  * A personal access token. More information on this can be found [here](https://docs.digitalocean.com/reference/api/create-personal-access-token/).

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

  * [ GitHub ](/docs/ext-cloud-cli-github) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


