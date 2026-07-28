# Billing Options

LimaCharlie has more than one billing option for the different needs of its users. This page describes the two options, *Default Billing* and *Unified Billing*.

## Default Billing

By default, LimaCharlie bills each Organization with a credit card that you set on that organization. The billing cycle of an organization starts when the organization moves from the free tier to a paid tier. The invoices go to the email address of the user who created the organization.

## Unified Billing

Unified billing is for customers who need flexibility when they manage many organizations. It lets the customer change the billing configuration for their needs.

All the options below apply to a "billing domain". A billing domain is the domain name in the email address of a user. For example, the users `ceo@mycorp.com` and `sales@mycorp.com` both belong to the `mycorp.com` billing domain.

All the organizations in the same billing domain have their billing cycle on the same day. The creation time of the organization, and the time when it exits the free tier, do not change this day. LimaCharlie aggregates all the invoices for a billing domain into one invoice, and sends this invoice manually each month.

You can configure these options as part of Unified Billing:

- Override the email address for the invoice of each organization. LimaCharlie then uses a central email address, for example <billing@mycorp.com>, instead of the email address of the creator. A billing domain with unified billing gets a monthly report. The report summarizes all the organizations in the domain and their billing.
- Select manual invoices. LimaCharlie sends the invoices of the organizations in a billing domain manually by email, without a credit card. The recipient can then pay the invoices with ACH or with a credit card. The recipient must do this payment manually each month.

## Default Billing Setup vs Unified Billing

|  | Default Billing Setup | Unified Billing |
| --- | --- | --- |
| **Can be used by** | Anyone | Customers whose users share a custom domain name in the email address (for example, the users `ceo@mycorp.com` and `sales@mycorp.com` both belong to the `mycorp.com` domain). |
| **Best suited for** | *Customers that have one to three tenants to manage* Enterprise clients that want to manage billing at the department level (billed to different cards) | *Service providers (MSP, MSSP, DFIR) who manage many tenants* Enterprise clients that want to manage billing at the company level (billed to one card) |
| **Payment method used** | LimaCharlie bills with a credit card that you set on each organization. | One payment method applies to all the organizations in the same billing domain. |
| **Manual invoicing** | Not available | Available  LimaCharlie sends the invoices of the organizations in a billing domain manually by email, without a credit card. The recipient can then pay the invoices with ACH or with a credit card, manually each month. |
| **Billing cycle** | Starts when the organization moves from the free tier to a paying tier (a different billing cycle for each tenant). | All the organizations in the same billing domain have their billing cycle on the same day. |
| **Invoicing** | Users get one invoice for each organization. | LimaCharlie aggregates all the invoices for a billing domain into one invoice, and sends it manually each month. |
| **Email invoices go to** | The email address of the user who created the organization. | LimaCharlie uses a central email address (like `billing@mycorp.com`) instead of the email address of the creator. A billing domain with unified billing gets a monthly report. The report summarizes all the organizations in the domain and their billing. |

To learn more about Unified Billing, or to set it up, [contact LimaCharlie](https://limacharlie.io/contact).
