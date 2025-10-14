# Soteria M365 Rules

Soteria's O365 ruleset provides coverage across O365 (aka M365) telemetry streams. The ruleset is designed for in-depth analysis of the Office 365 ecosystem which includes:

* Teams
* Word
* Excel
* PowerPoint
* Outlook
* OneDrive
* ...and other productivity applications.

## Data access

Please note that Soteria won't get access to your data, and you won't be able to see or edit their rules - LimaCharlie acts as a broker between the two parties.

To leverage detection logic provided by the ruleset:

1. Subscribe your tenant to the [Soteria Office 365 ruleset extension](https://app.limacharlie.io/add-ons/extension-detail/soteria-rules-o365)
2. Subscribe your tenant to [tor](https://app.limacharlie.io/add-ons/detail/tor-ips) lookup (provided at no cost).
3. Configure Office 365 Sensor to start collecting [Office 365 audit logs](/v2/docs/adapter-types-microsoft-365).

## Enabling Soteria's O365 Rules

Soteria's O365 rules can be activated via two means.

### Activating via the Web UI

To enable Soteria's O365 ruleset, navigate to the Extensions section of the Add-On Marketplace and search for Soteria. You can also directly select `soteria-rules-o365`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-o365-1.png)

Under the Organization dropdown, select a tenant (organization) you want to subscribe to Soteria O365 rules and click **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-o365-2.png)

You can also manage add-ons from the **Subscriptions** menu under **Billing**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/soteria-o365-3.png)

### Infrastructure as Code

Alternatively, to manage tenants and LimaCharlie functionality at scale, you can leverage our Infrastructure as Code functionality.