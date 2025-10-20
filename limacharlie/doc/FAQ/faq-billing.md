# FAQ - Billing

This page contains frequently asked questions about billing within LimaCharlie.

Pricing Details

Please note that our pricing is transparent, and is available via our [Pricing webpage](https://limacharlie.io/pricing).

## How Can I Change My Quota/Upgrade to the Paid Tier?

When you sign up for the LimaCharlie account, you will automatically be on a free tier, allowing you to create two organizations with two sensors each. All add-ons and additional services are free on this tier.

To upgrade to paid tier, simply navigate to the Setup section of the Organization you are looking to upgrade and perform the following actions:

1. Ensure you have a payment method on file by clicking the **Billing & Usage** tab.
2. In the **Billing & Usage** tab, set the quota number you would like and click **Update Quota**. Quota is the number of sensors concurrently online you would like to support.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/billing-1.png)

## What is the Cost of Deploying Payloads via LimaCharlie?

Payload pricing is provided via our [pricing page](https://limacharlie.io/pricing). For example, assume deploying Payloads via LimaCharlie costs $0.19 per 1 GB of data sent. A 1GB payload sent to 10 endpoints will cost $1.9 (10GBs x  $0.19).

This only impacts organizations that leverage Payloads functionality, as well as Atomic Red Team and Dumper services (they are running as Payloads in LC).

To understand the impact on your organization, check the **Metered Usage** section of the **Billing** page. You will notice the new **Payload Data Sent** metric along with the size of payloads deployed and price.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/billing-2.png)

## What is Usage-Based Billing?

Along with our predictable per endpoint pricing model, LimaCharlie offers a pure usage-based billing model for our Endpoint Detection & Response (EDR) capability. Pricing within this model is calculated solely on the time the Sensor is connected, events processed, and events stored. You can find more information about our billing options [here](../Platform_Management/Billing/billing-options.md).

We acknowledge that some might not need the entirety of available components all the time, and might benefit from having access to an Endpoint Agent on an ad-hoc basis. This approach enables the following:

1. Incident responders will now be able to offer pre-deployments to their customers at almost zero cost. That is, they can deploy across an organization's entire fleet and lay dormant in [sleeper mode](../Sensors/Endpoint_Agent/sleeper.md). With agents deployed ahead of an incident, responders can offer competitive SLA's.
2. Product developers can take advantage of usage-based billing to leverage narrow bands of functionality at a low cost. This means getting the functionality they need without building it from the ground up or paying for a full EDR deployment.

## For Lc Adapters Billed on Usage, What Does "Block of Data" Mean & How Will It Impact the Price I Pay?

Some LimaCharlie Adapters are billed based on usage. Updated pricing details can be found on our [pricing page](https://limacharlie.io/pricing).

For example, assume $0.15 per block of data of 1 GB (on the organizational level). This means that 10 adapters with less than 1 GB (total) in the same organization will be $0.15 total for that month.

## How Do I Determine How Much I Need to Pay for an Org If It Was in Usage-Based Billing Mode?

If the organization you are trying to assess has [1-year telemetry retention](https://app.limacharlie.io/add-ons/detail/insight) enabled, you could use the stats API to see the number of events retained:

`https://api.limacharlie.io/v1/usage/OID`
 or
`https://api.limacharlie.io/static/swagger/#/Organizations/getOrgUsageStats`

You will want to check the `sensor_events` and `sensor_retained` values.

## How Is the Price of Sensors & Add-Ons Calculated in LimaCharlie?

There are two categories of Sensors: sensors billed on Quota set by the user (vSensor basis) and sensors billed on usage basis.

### vSensors

LimaCharlie has the concept of a vSensor. A vSensor is a virtual sensor used for the purpose of setting up quota and billing of [Endpoint Agents](/v2/docs/endpoint-agent). vSensor pricing matches that listed on our pricing page, and includes a year of full telemetry storage.

Our transparent pricing and quota-based approach allows you to easily mix and match deployments, while staying within a certain price point.

If you set the quota to 100 vSensors, you can have concurrently:

* 50 Windows Sensors + 50 Linux Sensors, OR
* 20 Windows Sensors + 30 Linux Sensors + 50 macOS Sensors, OR
* 100 macOS Sensors
* Or any other combination as long as the total number of sensors does not exceed the quota of 100 vSensors.

### Sensors Over Quota

If the quota is maxed out when a sensor attempts to come online, the sensor will be given a message to go away for a period of time and then they can check again. A `sensor_over_quota` event will be emitted in the deployments stream as well enabling users to set up alerts and be notified about this happening. The amount of time sensors are told to go away for increases if they connect again and the organization is still over quota.

## When Will My Credit Card Be Charged?

Quota-based items are charged a month ahead, while usage items are billed the month following, similar to most cellphone invoices (or hosting).

## How Do I Change My Billing Credit Card?

If you are using a credit card for payment and wish to change your address or card details, navigate to **Billing > Billing & Usage** within the web UI. From there, select **Change Payment Details** to update the appropriate details.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Endpoint Detection & Response

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.
