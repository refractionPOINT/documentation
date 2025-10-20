# YARA

The [YARA](https://github.com/Yara-Rules/rules) Extension is designed to help you with all aspects of YARA scanning. It takes what is normally a manual piecewise process, provides a framework and automates it. Once configured, YARA scans can be run on demand for a particular endpoint or continuously in the background across your entire fleet.

Yara configurations are synchronized with sensors every few minutes.

There are three main sections to the YARA job:

* Sources
* Rules
* Scan

Where Does My YARA Scan?

Automated YARA scanners in LimaCharlie will run on all files loaded in memory (e.g. exe, dll, etc), and on the memory itself.

Files on disk can be scanned using a Sensor command.  You can trigger a Manual Scan that's run on-demand by:

* Clicking the Run YARA scan button on the sensor details page,
* Clicking the Scan button on the YARA Scanners page
* Using the console
* Within the Response section of a  rule (sample below)
* Using the LimaCharlie API

### Rules

This is where you define your YARA rule(s). You can copy and paste your YARA rules into the `Rule` box, or you can define sources via the [ext-yara-manager](../LimaCharlie_Extensions/ext-yara-manager.md). Sources can be either direct links (URLs) to a given YARA rule (or directory of rules) or [ARLs](../../Reference/reference-authentication-resource-locator.md) to a YARA rule.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/yara-1.png)

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/yara-2.png)

### Scanners

Scanners define which sets of sensors should be scanned with which sets of YARA rules.

Filter Tags are tags that must ALL be present on a sensor for it to match (AND condition), while the platform of the sensor much match one of the platforms in the filter (OR condition).

To apply YARA rules to scan an endpoint (or set of endpoints), you must select the platform or tags, and then add the YARA rules you would like to run.

## Using Yara in D&R Rules

If you want to trigger a Yara scan as a response to one of your detections, you can configure an extension request in the respond block of a rule.
 A Yara scan request can be executed with a blank selector OR Sensor ID. However, one of them must be specified.

```
- action: extension request
  extension action: scan
  extension name: ext-yara
  extension request:
	sources: [ ]# Specify Yara Rule sources as strings
	selector: ''
        sid: '{{ .routing.sid }}' # Use a sensor selector OR a sid, **not both**
	yara_scan_ttl: 86400 # "Default: 1 day (86,400 seconds)"
```

### Migrating D&R Rule from legacy Service to new Extension

***LimaCharlie is migrating away from Services to a new capability called Extensions. Support of legacy services will end on June 30, 2024.***

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a direct way to assess if any rules reference legacy Yara service, preview the change and execute the conversion required in the rule "response".

Command line to preview Yara rule conversion:

```
limacharlie extension convert_rules --name ext-yara
```

A dry-run response (default) will display the rule name being changed, a JSON of the service request rule and a JSON of the incoming extension request change.

To execute the change in the rule, explicitly set `--dry-run` flag to `--no-dry-run`

Command line to execute Yara rule conversion:

```
limacharlie extension convert_rules --name ext-yara --no-dry-run
```

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Tags in LimaCharlie are strings linked to sensors for classifying endpoints, automating detection and response, and triggering workflows. Tags appear in every event under the `routing` component and help simplify rule writing. Tags can be added manually, via API, or through detection & response rules. System tags like `lc:latest`, `lc:stable`, and `lc:debug` offer special functionality. Tags can be checked, added, or removed through the API or web app, streamlining device management.

In LimaCharlie, a Sensor ID is a unique identifier assigned to each deployed endpoint agent (sensor). It distinguishes individual sensors across an organization's infrastructure, allowing LimaCharlie to track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as sending commands, collecting telemetry, and monitoring activity, ensuring that actions and data are accurately linked to specific devices or endpoints.
