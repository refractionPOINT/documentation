# Reliable Tasking

The Reliable Tasking Extension lets you task Sensor(s) that are offline. The extension queues the task in the cloud. It delivers the task automatically when the Sensor(s) come online.

## How It Works

When you create a reliable task, the extension:

1. Resolves the targeting criteria (`sid`, `tag`, or `selector`) to a list of sensors. It records one queued task for each sensor, with an expiry of `now + ttl`.
2. Tries delivery immediately to the sensors that are online.
3. Tries delivery again each time a targeted sensor reconnects to the cloud (on its `CONNECTED` event).
4. Removes the queued task for a sensor after that sensor confirms receipt of the command.

This design has two results:

- **Delivery only happens when a sensor is connected.** The extension never pre-stages a task on an offline sensor. A task for an offline sensor stays only in the queue of the extension until the sensor reconnects.
- **The extension checks the TTL at delivery time.** At each delivery attempt, the extension skips expired tasks. If a sensor is offline for the full TTL and reconnects after it, the extension does *not* deliver the task.

> **Note:** The sensor commands `restart` and `upgrade_core` do not give a receipt from the sensor. The extension marks them as confirmed, and removes them from the queue, when it sends them to a connected sensor.

## Enabling the Reliable Tasking Extension

1. Open the [Reliable Tasking extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-reliable-tasking) in the marketplace.
2. Select the Organization for which you want to enable the extension.
3. Select **Subscribe**.

After you select **Subscribe**, the Reliable Tasking extension becomes available almost immediately.

## Using the Reliable Tasking Extension

After you enable the extension, a **Reliable Tasking** option shows under **Automation** in the LimaCharlie web app. You can also use the extension through the REST API.

In the Reliable Tasking module, you can:

- Task Sensor(s)
- Untask Sensor(s)
- List active task(s)

## Actions via REST API

You can send these REST API actions to the Reliable Tasking extension:

### Create a Task

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"context":"version","selector":"plat==windows","task":"run --shell-command whoami","ttl":3600}'
```

Give all parameters in the request body as URL-encoded form data. The `data` parameter must contain a JSON object with these fields:

**Required Parameters:**

- `task`: The command to run, similar to a command-line `task` (e.g., `"run --shell-command whoami"`, `"mem_map --pid 4"`)
- One of `sid`, `tag`, or `selector` (targeting criteria):
  - `sid`: Target a single sensor by Sensor ID
  - `tag`: Target all sensors that have this tag
  - `selector`: A [Sensor Selector Expression](../../../8-reference/sensor-selector-expressions.md) that specifies which sensors get the task. Use `"*"` to target all sensors in the organization.
    - Examples:
      - `"selector":"plat==windows"` - All Windows sensors
      - `"selector":"sid=='abc-123-def'"` - A specific sensor by ID
      - `"selector":"production in tags"` - All sensors with the "production" tag
      - `"selector":"plat==linux and int_ip matches '^10\\.3\\..*'"` - Complex expressions that use AND/OR logic

**Optional Parameters:**

- `context`: An identifier that shows in the `investigation_id` of the matching `RECEIPT` or `_REP` event. Use it to write D&R rules on the response.
- `ttl`: Time-to-live in seconds - how long the extension continues to try delivery to sensors that did not acknowledge the task. The default is 1 week (604800 seconds). There is no minimum value. Short TTLs, even a few seconds, are valid and are a supported way to bound how late a task can be delivered. See [TTL and Delivery Guarantees](#ttl-and-delivery-guarantees).

For more about the syntax of sensor selectors and the available fields (`sid`, `plat`, `tags`, `hostname`, `int_ip`, etc.), see the [Sensor Selector Expressions reference](../../../8-reference/sensor-selector-expressions.md).

**Response:**

```json
{
  "task_id": "abc123...",
  "total_sensors": 250,
  "tasked_sensors": 200,
  "queued_sensors": 50
}
```

- `task_id`: The unique ID for this tasking request across all targeted sensors. Keep it to [untask](#untask) later or to correlate feedback events.
- `total_sensors`: The number of sensors that match the targeting criteria.
- `tasked_sensors`: The sensors that were online and got the task immediately.
- `queued_sensors`: The sensors that were offline. The task stays in the queue for them until they reconnect or the TTL expires.

**Additional Examples:**

Target a specific sensor:

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"task":"os_version","selector":"sid=='\''sensor-123-abc'\''","ttl":86400}'
```

Target all Linux servers with a specific tag:

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"task":"file_get -f /etc/passwd","selector":"plat==linux and production in tags","context":"audit-2024","ttl":172800}'
```

Target all sensors:

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=task&data={"task":"os_version","selector":"*","ttl":3600}'
```

### List Tasks

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=list&data={}'
```

This action returns the pending reliable tasks, grouped by sensor and then by `task_id`. Each queued task includes the command, the context, and the expiry time.

Like `task` and `untask`, the `list` action accepts `sid`, `tag`, or `selector` to scope which queues of sensors it returns. The selector defaults to `*` (all sensors), so an empty `data` object works. The scope applies to *sensors*, not to the selector that created the task. The action does not list tasks that expired or that the sensor confirmed.

### Untask

The `untask` action deletes queued tasks. It stops delivery of ALL tasks that match the given criteria. Use it to cancel tasks that the extension did not yet deliver, for example tasks for sensors that are still offline.

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=untask&data={"selector":"*","task_id":"$TASK_ID"}'
```

**Parameters:**

- One of `sid`, `tag`, or `selector` is necessary. It scopes which sensors to untask, with the same meaning as in `task`. Use `"*"` to cover all sensors.
- `task_id` (optional): Remove only the tasks with this task ID, as returned by the `task` action. If you omit it, the action removes ALL queued tasks on the matching sensors.

**Response:**

```json
{
  "deleted": 50
}
```

`deleted` is the number of queued task records that the action removed.

**Examples:**

Cancel one tasking request on every sensor where it is still in the queue:

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=untask&data={"selector":"*","task_id":"abc123"}'
```

Remove all queued tasks from a single sensor:

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-reliable-tasking' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=untask&data={"sid":"sensor-123-abc"}'
```

The `untask` action removes tasks from the delivery queue. The queue is the only place where a task that is not yet delivered exists. After `untask` returns, the extension cannot deliver the queued task. You cannot recall a task that the extension already delivered to a connected sensor.

## TTL and Delivery Guarantees

The `ttl` is the authoritative bound on how late the extension can deliver a task:

- The extension checks the expiry (`creation time + ttl`) at each delivery attempt. After a task expires, the extension never delivers it, even to a sensor that reconnects after the TTL.
- There is no minimum TTL. For "run this in the next 2 minutes or not at all", `"ttl":120` does exactly that.
- Expired tasks do not show in `list` results and need no cleanup. A call to `untask` on them causes no problem.

To build your own timeout on top of reliable tasking, for example to mark a task as failed after N seconds, use this pattern:

1. Create the task with `ttl` set to your timeout. The platform then does not deliver the task after your deadline.
2. Call `untask` with the `task_id` when you declare the timeout. This step is optional and cleans up immediately.

The TTL bounds when delivery *starts*, not when results arrive. A sensor that reconnects just before the expiry can still get the task. Its `RECEIPT` and `_REP` events can arrive after your deadline. Make your response handling (D&R rules, `context` matching) accept a late receipt for a task that the extension delivered near the end of its TTL.

## Monitoring Task Delivery

The extension reports its activity as events in your organization. It uses a webhook Adapter named `ext-reliable-tasking`, which LimaCharlie installs automatically when you subscribe. The type of each event shows the action:

- `add_task`: The extension recorded a new tasking request (includes `task_id`, the targeting criteria, and `ttl`)
- `try_task`: A targeted sensor is online, and the extension tries delivery
- `task_sent`: The extension sent the task to the sensor (includes `sid` and `task_id`)
- `task_done`: The sensor confirmed receipt, and the extension removed the task from the queue
- `task_failure`: The extension failed to send the task to a sensor (includes the error)

Use these events in D&R rules to track completion across the fleet or to alert on failures. For example:

```yaml
detect:
  event: task_failure
  op: is
  path: routing/hostname
  value: ext-reliable-tasking
respond:
  - action: report
    name: reliable-task-delivery-failure
```

## Capturing Task Responses

If you use reliable tasks to send commands to your sensors, you can also see or act on the responses to these commands.

If you add a value to the `context` parameter in the extension request, that value shows in the `investigation_id` of the matching `RECEIPT` or `_REP` event. You can then write a D&R rule on the response.

The example cURL command above has a `context` of `version`. The D&R rule below looks for that value.

### Example detect block

```yaml
op: contains
event: RECEIPT
path: routing/investigation_id
value: version
```

### Example respond block

```yaml
- action: output
  name: tasks-output         # Send responses to the specified output
- action: report
  name: "Reliable task ran"  # Detect on the task being run
```

## Fanning Out at Scale

One `task` request fans out on the server. The extension resolves the `tag` or the `selector` to the full list of sensors, queues one task for each sensor, and paces the deliveries. To send one command to many sensors, make **one** API call with a `tag` or a `selector`. Do not loop over the sensors and make one call for each `sid`.

Like all LimaCharlie REST API calls, requests to the extension endpoint obey API rate limits for each credential, measured over a 60-second window. A client that exceeds its quota gets an `HTTP 429` response. The response includes the `X-RateLimit-Quota` header (requests allowed for each window) and the `X-RateLimit-Period` header (window length in seconds). After such a response, back off and retry after the window. With fan-out on the server, even large deployments need only a few API calls, which keeps you below the limits.

## Migrating Rule from legacy Service to new Extension

***Note: LimaCharlie migrated from Services to Extensions. Legacy services are no longer supported.***

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a direct way to check if any rules reference the legacy reliable tasking service, and to convert them to use the extension.

Command line to preview Reliable Tasking rule conversion:

```bash
limacharlie extension convert_rules --name ext-reliable-tasking
```

A dry-run response (the default) shows the name of the rule that changes, a JSON of the service request rule, and a JSON of the new extension request.

To apply the change to the rule, set the `--dry-run` flag to `--no-dry-run`.

Command line to execute reliable tasking rule conversion:

```bash
limacharlie extension convert_rules --name ext-reliable-tasking --no-dry-run
```
