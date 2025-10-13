Sigma is an open source project that aims at creating a generic query language for security and  rules. It looks up known anomalies and Common Vulnerabilities and Exposures (CVEs).

Many people use Sigma as the community tends to respond quickly, but also puts interesting anomalies often in there.

In LimaCharlie, you can subscribe to the hundreds of rules that are a part of Sigma, for free. Every 15 minutes we re-process those rules in your organization; there's no management required, it just happens.

Rules converted are available [here](https://github.com/refractionPOINT/sigma-limacharlie/tree/rules).

You can also follow an RSS feed of changes to the `rules` rep [here](https://github.com/refractionPOINT/sigma-limacharlie/commits/rules.atom).

Converting Sigma rules

You can utilize our public REST API to convert Sigma rules. More information available [here](/v2/docs/sigma-converter).

## Enabling Sigma

To enable the Sigma rules, you want to navigate to the Add-ons section and search for Sigma in the search bar.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sigma-rules-1.png)

Under the `Organization` dropdown, select a tenant (organization) you want to subscribe to Sigma rules and click `Subscribe`:

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sigma-rules-2.png)

Please note that add-ons are applied on the per-tenant basis. If you have multiple organizations you want to subscribe to Sigma, you will need to subscribe each organization to the add-on separately.

You can also manage add-ons from the Subscriptions menu under Billing.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sigma-rules-3.png)

Tenants that have been subscribed to the add-on, will be marked with a green check mark in the `Organization` dropdown.

Please note that some Sigma rules on Windows rely on Windows Event Logs that are not collected by LimaCharlie by default. In order to leverage these you will need to configure an automated collection of relevant Windows Event Logs through the Artifact Collection service.

## Identifying Sigma Rule Hits

To identify the source of the detection, click on the detection details where you will be able to see the `author` field. It contains the identity (email or key name) of the entity that created the rule.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sigma-rules-4(1).png)

Detections that come in through a managed Sigma rule will have the author listed as starting with `_ext_sigma`.

Severity of Sigma Rules

Once you enable the Sigma add-on you may start seeing detections come through. Â These detections can include a level parameter with a value of:

* Critical
* High
* Medium
* Low

These level classifications are provided by the rule author.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sigma-rules-5.png)
