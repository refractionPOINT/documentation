---
title: Azure Event Hub
slug: outputs-destinations-azure-event-hub
breadcrumb: Outputs > Output Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-azure-event-hub
articleId: d44e60fd-0c4f-443a-bfb6-53fa8a413c41
---

* * *

Azure Event Hub

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Azure Event Hub

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

Output events and detections to an Azure Event Hub (similar to PubSub and Kafka).

  * `connection_string`: the connection string provided by Azure.




Note that the connection string should end with `;EntityPath=your-hub-name` which is sometimes missing from the "Connection String" provided by Azure.

Example:
    
    
    connection_string: Endpoint=sb://lc-test.servicebus.windows.net/;SharedAccessKeyName=lc;SharedAccessKey=jidnfisnjfnsdnfdnfjd=;EntityPath=test-hub
    

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

  * [ Azure Kubernetes Service (AKS) ](/docs/azure-kubernetes-service)
  * [ Azure Monitor ](/docs/azure-monitor)
  * [ Azure Network Security Group ](/docs/azure-network-security-group)
  * [ Azure SQL Audit Logs ](/docs/azure-sql-audit-logs)
  * [ Azure Event Hub ](/docs/adapter-types-azure-event-hub)
  * [ Microsoft Entra ID ](/docs/adapter-types-microsoft-entra-id)
  * [ Azure ](/docs/ext-cloud-cli-azure)



* * *

###### What's Next

  * [ Azure Storage Blob ](/docs/outputs-destinations-azure-storage-blob) __



Tags

  * [ azure ](/docs/en/tags/azure)
  * [ outputs ](/docs/en/tags/outputs)


