# Azure SQL Audit Logs

Microsoft Azure SQL is a scalable, cloud-hosted database that integrates with the Azure ecosystem. More information on Azure SQL can be found [here](https://azure.microsoft.com/en-us/products/azure-sql/database).

LimaCharlie can ingest and natively parse Azure SQL Server audit logs.

## Log Ingestion

Azure SQL Server audit logs can be ingested via:

* [Azure Event Hub](adapter-types-azure-event-hub)
* LimaCharlie [Webhooks](tutorial-creating-a-webhook-adapter)

Upon ingestion, the log `category` field is used to define the Event Type.
