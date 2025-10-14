[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v2

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Microsoft 365

* 07 Aug 2025
* 4 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Microsoft 365

* Updated on 07 Aug 2025
* 4 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Microsoft 365, formerly Office 365, is a product family of productivity software, collaboration and cloud-based services owned by Microsoft. This Adapter allows you to ingest audit events from the [Office 365 Management Activity API](https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference).

Microsoft 365 events can be ingested in LimaCharlie and observed as the `office365` platform.

## Adapter Deployment

Microsoft 365 events are ingested via a cloud-to-cloud Adapter configured specifically to review M365 events. When creating an Adapter, the following data points are required:

* `domain`: Office 365 domain
* `tenant_id`: Office 365 tenant ID
* `publisher_id`: Office 365 publisher ID (for single-tenant Apps, the PublisherID is the same as the Tenant ID)
* `client_id`: Office 365 client ID
* `client_secret`: Office 365 client secret
* `endpoint`: Office 365 API endpoint
* `content_types`: content types of events to ingest.

  + Options include:

    - `Audit.AzureActiveDirectory`
    - `Audit.Exchange`
    - `Audit.SharePoint`
    - `Audit.General`
    - `DLP.All`
  + *Default is all of the above*

If creating a Microsoft 365 Adapter via the Web UI, the helper form will navigate you through providing these values.

Establishing a cloud-to-cloud connector between LimaCharlie and Office 365 requires a few steps to provide the correct permissions for the [Office 365 Management Activity API](https://learn.microsoft.com/en-us/office/office-365-management-api/office-365-management-activity-api-reference).

### Infrastructure as Code Deployment

```
# Office 365 Management Activity API Specific Docs: https://docs.limacharlie.io/docs/adapter-types-office-365-management-activity-api
# For cloud sensor deployment, store credentials as hive secrets:

#   tenant_id: "hive://secret/o365-tenant-id"
#   client_id: "hive://secret/o365-client-id"
#   client_secret: "hive://secret/o365-client-secret"

sensor_type: "office365"
office365:
  tenant_id: "hive://secret/azure-o365-tenant-id"
  client_id: "hive://secret/azure-o365-client-id"
  client_secret: "hive://secret/azure-o365-client-secret"
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_O365"
    hostname: "ms-o365-adapter"
    platform: "json"
    sensor_seed_key: "office365-audit-sensor"
    mapping:
      sensor_hostname_path: "ClientIP"
      event_type_path: "Operation"
      event_time_path: "CreationTime"
    indexing: []
  # Office 365 specific configuration
  content_types:
    - "Audit.AzureActiveDirectory"
    - "Audit.Exchange"
    - "Audit.SharePoint"
    - "Audit.General"
    - "DLP.All"
  # Optional configuration
  endpoint: "enterprise"                           # Default: "enterprise"
  start_time: "2024-01-01T00:00:00Z"              # Optional: historical start time
  domain: "yourcompany.onmicrosoft.com"           # Optional: for GCC environments
  publisher_id: "hive://secret/o365-publisher-id" # Optional: usually same as tenant_id
```

## Configuring a Microsoft 365 Adapter in the Web UI

### Preparing Office 365 details

To establish an Office 365 adapter, we will need to complete a few steps within the Azure portal. Ensure that you have the correct permissions to set up a new App registration.

* Within the Microsoft Azure portal, create a new App registration. You can follow Microsoft's Quickstart guide [here](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app).
* The LimaCharlie connector requires a secret for Office 365 data. You can create one under `Certificates & secrets`. Be sure to copy this value and save it somewhere - you can only view it once.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2873%29.png)

* Additionally, you'll need to ensure that the app has the correct permissions to view Office 365 data via the Management API. Within `API Permissions`, configure the following permissions:

  + `ActivityFeed.Read` (Delegated & Application)
  + `ActivityFeed.ReadDlp` (Delegated & Application) *[if you want DLP permissions]*

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2874%29.png)

Additionally, you may need to grant admin consent to the above permissions.

At this point, you should have all the details you need to configure the Adapter.

### Setting Up the Adapter

Within the LimaCharlie web application, select `+ Add` Sensor, and then select `Office 365`:

You can select a pre-existing Installation Key or create a new one, unique for this adapter. Once an Installation Key is selected, you will be prompted with a form to finish setting up the adapter. Choose your desired adapter name, and provide the following values:

| Item | Azure Portal Location |
| --- | --- |
| Domain | Home |
| Tenant ID | App Registration Overview |
| Publisher ID | App Registration Overview |
| Client ID | App Registration Overview |
| Client Secret | Created during creation in Certificates & secrets |
| API Endpoint | `enterprise`, `gcc-gov`, `gcc-high-gov`, or `dod-gov` |

Finally, you will also need to select a "Content Type" to import. This is the type of events you want to bring in to LimaCharlie. The options are as follows:

* `Audit.AzureActiveDirectory`
* `Audit.Exchange`
* `Audit.SharePoint`
* `Audit.General`
* `DLP.All`

Without a value, the default is *all of the above*.

Click `Complete Cloud Installation`, and LimaCharlie will attempt to connect to the Microsoft Office 365 Management API and pull events.

## Sample Rule

When ingested into LimaCharlie, Office 365 data can be referenced directly in your D&R rules. You could do this via a platform operator:

```
op: is platform
name: office365
```

We can also reference Office 365 events directly. The following sample rule looks at `FileAccessed` events from anonymous user names, and reports accordingly.

```
# Detection
event: FileAccessed
path: event/UserId
op: contains
value: anon

# Response
- action: report
  name: OneDrive File Accessed by Anonymous User
```

Note that in the detection above, we pivot on the `FileAccessed` event, which is associated with SharePoint activity. Available event types will depend on source activity and events ingested. More information on audit log activities can be found [here](https://learn.microsoft.com/en-us/purview/audit-log-activities).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### Related articles

* [Soteria M365 Rules](/docs/soteria-m365-rules)
* [Microsoft 365](/docs/ext-cloud-cli-microsoft365)

---

###### What's Next

* [Mimecast](/docs/adapter-types-mimecast)

Table of contents

+ [Adapter Deployment](#adapter-deployment)
+ [Configuring a Microsoft 365 Adapter in the Web UI](#configuring-a-microsoft-365-adapter-in-the-web-ui)
+ [Sample {{glossary.D&amp;R}} Rule](#sample-{{glossary-d-amp-r}}-rule)

Tags

* [adapters](/docs/en/tags/adapters)
* [azure](/docs/en/tags/azure)
* [m365](/docs/en/tags/m365)
* [sensors](/docs/en/tags/sensors)
