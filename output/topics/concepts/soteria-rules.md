# Soteria Rules

[Soteria](https://soteria.io/) is a US-based MSSP and longtime MSSP, and has built a wealth of experience writing and managing LimaCharlie [detection & response](/v2/docs/detection-and-response) rules. With one click, you can apply their rules to your environment. When Soteria updates the rules for their customers, you will get those updates in real time as well. Soteria provides their rules in the form of managed rulesets, available via the [Add-ons Marketplace](https://app.limacharlie.io/add-ons/category/rulesets).

> **Note:** Soteria won't get access to your data, and you won't be able to see or edit their rules - LimaCharlie acts as a broker between the two parties.

Soteria provides the following rulesets:

* [AWS Rules](/v2/docs/soteria-aws-rules)
* [EDR Rules](/v2/docs/soteria-edr-rules)
* [M365/O365 Rules](/v2/docs/soteria-m365-rules)

Soteria rules are available for a fee, either per-Sensor or per-Organization, which can be found on their respective pages within the Add-ons Marketplace.

## Definitions

**Managed Security Services Provider**

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.