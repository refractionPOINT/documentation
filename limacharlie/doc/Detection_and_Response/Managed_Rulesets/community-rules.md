# Community Rules

The LimaCharlie Endpoint Agent is a cross platform endpoint Sensor. It is a low-level, light-weight sensor which executes detection and response functionality in real-time.

Our Community Rules feature leverages the power of AI to quickly transform a plethora of third-party rules into LimaCharlie syntax so you can make them your own. The process is fast and efficient: Browse thousands of community rules, select one as a starting point, convert it to LimaCharlie syntax with one click, and customize it to your liking.

## Accessing the Community Rules

To access the Community Rules:

1. Log into LimaCharlie
2. Select an Organization
3. Click the Automation drop down on the left panel
4. Select Rules
5. Look in the upper right corner of the D&R Rules page for the Add Rule button
6. Click the Add Rule button
7. Look in the upper right corner of the rule creation page for the Community Library button
8. Click the Community Library button

This takes you to the Community Rules search page, and gives you access to thousands of third-party detection rules. The library currently contains detection rules written by [Anvilogic](https://github.com/anvilogic-forge/armory/blob/main/detections/cloud/aws_disableawsserviceaccess/aws_disableawsserviceaccess-splunk-awscloudtrail.yml), [Sigma](https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_susp_file_ext_from_susp_tld.yml), [Panther](https://github.com/panther-labs/panther-analysis/blob/develop/rules/gsuite_activityevent_rules/google_workspace_many_docs_downloaded.yml), and [Okta](https://github.com/okta/customer-detections).

> Rules are searchable by CVE number, keyword, or pre-defined descriptors (Tags). Searchable tags include attack techniques, MITRE ATT&CK id codes and other key rule identificators.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(337).png)

## Loading a Community Rule

Once you find the rule you want to use, import it to the organization by clicking "Load Rule", and our AI engine will create it using verified LimaCharlie syntax.

> This process may take a few seconds so please be patient.

Once the rule is ready, it will return you to the Add Rule page in LimaCharlie. The Detect and Response sections of the rule will be filled out with LimaCharlie logic that includes explanatory comments. From here you can manage this rule just as you would any other D&R rule.

## Digging Deeper

As these rules are the property of third parties you may be interested in knowing more about their licensing or source code. This information is accessible through the Community Rules search page. To see these details click on a rule.

The example below shows what appears when you click Anvilogic's Potential CVE-2021-44228 - Log4Shell rule

Under the rule name you will see the options to load the rule, check its source code, and read additional licensing information. There is also a reference section at the bottom left corner of the window providing links related to the rule.

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXf3SZQZu4j4kEp2Y0wpnoeHA0t_XaR5VqaoB9SupPHl0t91e-12QhMj0epDi742peW0gpu8e44HhJ4lDN1esspiMRUfpFr3W2aNiQcIeff2HhNCxmgp1h3oLqphpqJ8AohoDDxFdA?key=7BgiNipN3DxRQXGQyEk06w)

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Tags in LimaCharlie are strings linked to sensors for classifying endpoints, automating detection and response, and triggering workflows. Tags appear in every event under the `routing` component and help simplify rule writing. Tags can be added manually, via API, or through detection & response rules. System tags like `lc:latest`, `lc:stable`, and `lc:debug` offer special functionality. Tags can be checked, added, or removed through the API or web app, streamlining device management.
