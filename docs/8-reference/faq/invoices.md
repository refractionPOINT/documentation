# FAQ - Invoices

This page contains frequently asked questions about the invoices that you receive for the LimaCharlie service.

Pricing Details

LimaCharlie pricing is available on the [Pricing webpage](https://limacharlie.io/pricing).

## LimaCharlie Invoices

LimaCharlie offers two types of invoices:

- Individual Organization
- Unified billing

The sections below describe each type in detail.

### Individual organization invoices

Your invoice includes a detailed breakdown of the usage for your LimaCharlie tenant organization. There is a line item for each LimaCharlie product that you used, with your usage for the period. For example:

- Sensors
- Output usage
- Artifact ingestion
- Replay usage

Invoices have lines for standard billable items and for consumption-based items. Standard items such as the Sensor quota are pre-paid for the next month. Consumption-based items, for example the costs for each gigabyte in the prior period, are post-paid after the month ends.

Your monthly invoices include a detailed breakdown that shows the exact periods covered for each product listed.

You can adjust the quota of your organization on demand, and this triggers proration of the charges. Your invoice then has line items that show "Remaining time on ..." or "Unused time on ...". The proration is calculated for each second.

### Unified Billing invoices

Customers on Unified Billing receive one invoice with a summary of all their LimaCharlie organizations, so they can pay for all of them together. The Unified invoice has one line item for each tenant organization. Each line item gives the sub-invoice number of that organization. Use the sub-invoices for detailed line-level information about each organization.

#### Example Unified invoice

Your browser does not support PDF. [Download the example unified invoice](../../assets/images/EXAMPLE---Unified---Invoice-ABC1234D-0011.pdf).

#### Example individual Tenant invoice

Your browser does not support PDF. [Download the example tenant invoice](../../assets/images/EXAMPLE---Alpha-Customer---Invoice-BCDE9876-0035.pdf).

With the Unified Billing invoice, customers also receive a LimaCharlie Global Billing email. This email contains:

1. A table with all the organizations in the period. The table gives a link to the detailed invoice of each organization, which shows the breakdown of the charges. These individual invoices have a zero-dollar balance, because the amounts are on the Unified Invoice. A line item called "UNIFIED-BILLING" shows that the invoice total moved to the unified invoice.
2. A summary report (attachment) in CSV format with a list of the organizations on the global billing invoice. The CSV has these fields:
    A - Org Name
    B - Org ID
    C - Payment
    D - Sub-total
    E - Total Due
    F - Total Paid

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives you full control over security operations. This structure supports flexible, multi-tenant setups for managed security providers, and for enterprises that manage many departments or clients.

Like agents, Sensors send telemetry to the LimaCharlie cloud as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless solution that connects the endpoints of an organization to the cloud in a secure way.

In LimaCharlie, an Organization ID (OID) is a unique identifier for each tenant or customer account. It distinguishes the different organizations, so LimaCharlie can manage resources, permissions, and the separation of data in a secure way. The Organization ID keeps all telemetry, configurations, and operations isolated and specific to each organization. This gives multi-tenant support and a clear separation between customer environments.
