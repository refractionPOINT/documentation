---
title: Azure
slug: ext-cloud-cli-azure
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-azure
articleId: fa6e6269-8f3f-46e5-883d-50238978fad1
---

* * *

Azure

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Azure

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

The Azure CLI is a set of commands used to create and manage Azure resources. With this component of the Cloud CLI Extension, you can interact with Azure directly from LimaCharlie.

This extension makes use of the Azure CLI, which can be found [here](https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli).

## Example

The following example returns a list of virtual machines and their respective details in Azure.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "az" }}' 
        command_line: '{{ "vm list" }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

To utilize the Azure CLI, you will need:

  * An application and a [service principal](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal) with the appropriate permissions and a [client secret](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal#option-3-create-a-new-client-secret)

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

  * [ Azure SQL Audit Logs ](/docs/azure-sql-audit-logs)
  * [ Azure Kubernetes Service (AKS) ](/docs/azure-kubernetes-service)
  * [ Azure Key Vault ](/docs/azure-logs-key-vault)
  * [ Azure Event Hub ](/docs/adapter-types-azure-event-hub)
  * [ Azure Storage Blob ](/docs/outputs-destinations-azure-storage-blob)
  * [ Azure Event Hub ](/docs/outputs-destinations-azure-event-hub)
  * [ Azure Network Security Group ](/docs/azure-network-security-group)
  * [ Azure Monitor ](/docs/azure-monitor)



* * *

###### What's Next

  * [ DigitalOcean ](/docs/ext-cloud-cli-digitalocean) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ azure ](/docs/en/tags/azure)
  * [ extensions ](/docs/en/tags/extensions)


