---

Azure Event Hub

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Azure Event Hub

* Updated on 05 Oct 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Output events and detections to an Azure Event Hub (similar to PubSub and Kafka).

* `connection_string`: the connection string provided by Azure.

Note that the connection string should end with `;EntityPath=your-hub-name` which is sometimes missing from the "Connection String" provided by Azure.

Example:

```
connection_string: Endpoint=sb://lc-test.servicebus.windows.net/;SharedAccessKeyName=lc;SharedAccessKey=jidnfisnjfnsdnfdnfjd=;EntityPath=test-hub
```

---

Thank you for your feedback! Our team will get back to you

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

---

###### Related articles

* [Azure Kubernetes Service (AKS)](/docs/azure-kubernetes-service)
* [Azure Monitor](/docs/azure-monitor)
* [Azure Network Security Group](/docs/azure-network-security-group)
* [Azure SQL Audit Logs](/docs/azure-sql-audit-logs)
* [Azure Event Hub](/docs/adapter-types-azure-event-hub)
* [Microsoft Entra ID](/docs/adapter-types-microsoft-entra-id)
* [Azure](/docs/ext-cloud-cli-azure)

---

###### What's Next

* [Azure Storage Blob](/docs/outputs-destinations-azure-storage-blob)

Tags

* [azure](/docs/en/tags/azure)
* [outputs](/docs/en/tags/outputs)
