# Azure SQL Audit Logs

Microsoft Azure SQL is a scalable, cloud-hosted database that integrates with the Azure ecosystem. For more detail, see the Microsoft [Azure SQL Database product page](https://azure.microsoft.com/en-us/products/azure-sql/database).

LimaCharlie can ingest and parse Azure SQL Server audit logs directly.

## Log Ingestion

You can ingest Azure SQL Server audit logs through:

- [Azure Event Hub](../azure-event-hub.md)
- LimaCharlie [Webhooks](../../tutorials/webhook-adapter.md)

When you configure the adapter, set `client_options.platform: azure_sql_audit` to select the dedicated parser. At ingestion, the log `category` field sets the event type, and the `time` field supplies the event timestamp.
