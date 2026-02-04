# Reliable Tasking

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

```powershell
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"context":"version","selector":"plat==windows","task":"run --shell-command whoami","ttl":3600}'
```

All parameters are provided in the request body as URL-encoded form data. The `data` parameter should contain a JSON object with the following fields:

**Required Parameters:**

* `task`: The command to execute, similar to a command-line `task` (e.g., `"run --shell-command whoami"`, `"mem_map --pid 4"`)

**Optional Parameters:**

* `selector`: A [Sensor Selector Expression](../../../8-reference/sensor-selector-expressions.md) to specify which sensors should receive the task. If omitted, the task will be sent to all sensors in the organization.
  * Examples:
    * `"selector":"plat==windows"` - All Windows sensors
    * `"selector":"sid=='abc-123-def'"` - A specific sensor by ID
    * `"selector":"production in tags"` - All sensors with the "production" tag
    * `"selector":"plat==linux and int_ip matches '^10\\.3\\..*'"` - Complex expressions using AND/OR logic
* `context`: An identifier that will be reflected in the `investigation_id` of the corresponding `RECEIPT` or `_REP` event, allowing you to craft D&R rules based on the response
* `ttl`: Time-to-live in seconds - how long the extension should try to keep sending the task to sensors that haven't acknowledged it. Defaults to 1 week (604800 seconds)

For more details on sensor selector syntax and available fields (`sid`, `plat`, `tags`, `hostname`, `int_ip`, etc.), see the [Sensor Selector Expressions reference](../../../8-reference/sensor-selector-expressions.md).

**Additional Examples:**

Target a specific sensor:
```python
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"task":"os_version","selector":"sid=='\''sensor-123-abc'\''","ttl":86400}'
```

Target all Linux servers with a specific tag:
```python
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"task":"file_get -f /etc/passwd","selector":"plat==linux and production in tags","context":"audit-2024","ttl":172800}'
```

Target all sensors (no selector):
```python
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"task":"os_version","ttl":3600}'
```

#### **List Tasks**

```python
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=list&data={}'
```

This returns all pending reliable tasks for the organization. The response includes task details such as the task ID, command, sensor selector expression, and which sensors have acknowledged execution.

**Note:** The current API returns all tasks regardless of selector. If you need to filter tasks by sensor characteristics, retrieve all tasks and filter the results based on the `sensor_selector` field in each task object.

## Capturing Task Responses

If you're using reliable tasks to issue commands across your sensors, you're probably going to want to view or act on the responses from these commands as well.

If you add a value to the `context` parameter in the extension request, this value will be reflected in the `investigation_id` of the corresponding `RECEIPT` or `_REP` event, allowing you to craft a D&R rule based on the response.

The above example cURL command has a `context` of `version` so the below D&R rule looks for that value.

#### Example detect block:

```yaml
op: contains
event: RECEIPT
path: routing/investigation_id
value: version
```

#### Example respond block:

```yaml
- action: output
  name: tasks-output         # Send responses to the specified output
- action: report
  name: "Reliable task ran"  # Detect on the task being run
```

## Migrating Rule from legacy Service to new Extension

***Note: LimaCharlie has migrated from Services to Extensions. Legacy services are no longer supported.***

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a direct way to assess if any rules reference the legacy reliable tasking service and convert them to use the extension.

Command line to preview Reliable Tasking rule conversion:

```bash
limacharlie extension convert_rules --name ext-reliable-tasking
```

A dry-run response (default) will display the rule name being changed, a JSON of the service request rule and a JSON of the incoming extension request change.

To execute the change in the rule, explicitly set `--dry-run` flag to `--no-dry-run`

Command line to execute reliable tasking rule conversion:

```bash
limacharlie extension convert_rules --name ext-reliable-tasking --no-dry-run
```
