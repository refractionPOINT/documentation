The Reliable Tasking Extension enables you to task a Sensor(s) that are currently offline. The extension will automatically send the task(s) to Sensor(s) once it comes online.

## Enabling the Reliable Tasking Extension

To enable the Reliable Tasking extension, navigate to the [Reliable Tasking extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-reliable-tasking) in the marketplace. Select the Organization you wish to enable the extension for, and select **Subscribe**.

After clicking **Subscribe**, the Reliable Tasking extension should be available almost immediately.

## Using the Reliable Tasking Extension

Once enabled, you will see a **Reliable Tasking** option under **Automation** within the LimaCharlie web UI. You can also interact with the extension via REST API.

Within the Reliable Tasking module, you can:

* Task Sensor(s)
* Untask Sensor(s)
* List active task(s)

## Actions via REST API

The following REST API actions can be sent to interact with the Reliable Tasking extension:

#### **Create a Task**

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"context":"version","selector":"plat==windows","task":"run --shell-command whoami","ttl":3600}'
```

The `task` is similar to a command-line `task`. Optionally, you can also specify which endpoints to task by specifying:

* `sid` : A specific Sensor ID
* `tag` : All Sensor(s) with a Tag
* `plat`: All Sensor(s) of the specified platform

You can use the `ttl` to specify how long the extension should try to keep sending the task. The `ttl` value is a number of seconds and defaults to 1 week.

#### **List Tasks**

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=list&data={}'
```

When listing tasks, you can specify which endpoints to get queued tasks from by using one of:

* `sid` : A specific sensor ID
* `tag` : All Sensor(s) with a tag
* `plat`: All Sensor(s) of the specified platform

## Capturing Task Responses

If you’re using reliable tasks to issue commands across your sensors, you’re probably going to want to view or act on the responses from these commands as well.

If you add a value to the `context` parameter in the extension request, this value will be reflected in the `investigation_id` of the corresponding `RECEIPT` or `_REP` event, allowing you to craft a D&R rule based on the response.

The above example cURL command has a `context` of `version` so the below D&R rule looks for that value.

#### Example detect block:

```
op: contains
event: RECEIPT
path: routing/investigation_id
value: version
```

#### Example respond block:

```
- action: output
  name: tasks-output         # Send responses to the specified output
- action: report
  name: "Reliable task ran"  # Detect on the task being run
```

## Migrating Rule from legacy Service to new Extension

***LimaCharlie is migrating away from Services to a new capability called Extensions. Support of legacy services will end on June 30, 2024.***

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a direct way to assess if any rules reference legacy reliable tasking service, preview the change and execute the conversion required in the rule "response".

Command line to preview Reliable Tasking rule conversion:

```
limacharlie extension convert_rules --name ext-reliable-tasking
```

A dry-run response (default) will display the rule name being changed, a JSON of the service request rule and a JSON of the incoming extension request change.

To execute the change in the rule, explicitly set `--dry-run` flag to `--no-dry-run`

Command line to execute reliable tasking rule conversion:

```
limacharlie extension convert_rules --name ext-reliable-tasking --no-dry-run
```

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

In LimaCharlie, a Sensor ID is a unique identifier assigned to each deployed endpoint agent (sensor). It distinguishes individual sensors across an organization's infrastructure, allowing LimaCharlie to track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as sending commands, collecting telemetry, and monitoring activity, ensuring that actions and data are accurately linked to specific devices or endpoints.

Tags in LimaCharlie are strings linked to sensors for classifying endpoints, automating detection and response, and triggering workflows. Tags appear in every event under the `routing` component and help simplify rule writing. Tags can be added manually, via API, or through detection & response rules. System tags like `lc:latest`, `lc:stable`, and `lc:debug` offer special functionality. Tags can be checked, added, or removed through the API or web app, streamlining device management.
