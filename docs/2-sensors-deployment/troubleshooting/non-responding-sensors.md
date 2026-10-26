# Alerting on sensors that stop sending data

A sensor showing as online does not mean that data is arriving from it. To know when a device stops reporting, alert on the data itself. Check on a schedule whether each sensor you care about has sent anything recently, and raise a detection when it has not.

This page sets that up with a [Playbook](../../5-integrations/extensions/limacharlie/playbook.md) run by a scheduled [D&R rule](../../3-detection-response/index.md). It works for any sensor: endpoint agents, adapters, and the per-device sensors that an adapter creates for each firewall, switch or appliance it receives logs for.

## Why the online status is not enough

The online status reflects the connection to LimaCharlie, not the data:

- **Endpoint agents** are online while the agent is connected. An agent can be connected while some of the data you expect from it has stopped.
- **Adapters** that report as a single sensor are online while the adapter is connected. They stay online when the source they read from has stopped producing logs, because the adapter itself is still running.
- **Per-device sensors** come from an adapter configured with `client_options.mapping.sensor_key_path`, which creates one sensor per device found in the logs. Such a sensor shows online once data arrives for its device. It goes offline after a period with no data for that device, or when the adapter disconnects.

When logs from many devices pass through a single collector, such as a central log manager or a syslog relay, the status of every device follows the collector. They all go offline when the collector stops forwarding and come back online as it resumes, whatever state the devices themselves are in.

You can't change how LimaCharlie computes the online status. To get an alert that means "this device has not reported for N minutes", use the data-based check below. It does not use the online status.

## How it works

1. A D&R rule on the `schedule` target runs the playbook every 30 minutes. Other [schedules](../../8-reference/schedule-events.md) work too.
2. The playbook lists the sensors that match a [sensor selector](../../8-reference/sensor-selector-expressions.md) and asks LimaCharlie, for each one, whether any data from it was stored during the last `threshold_minutes`.
3. Sensors with no data get the `data-silent` tag, and the playbook returns one detection listing the sensors that just went silent.
4. A sensor already tagged `data-silent` is not reported again, so one outage produces one alert. The tag expires after `realert_hours` (24 by default), which reports the sensor again if it is still silent. When data from the sensor arrives again, the playbook removes the tag.
5. An [Output](../../5-integrations/outputs/index.md) sends the detection to your webhook, Slack, email, SIEM or ticketing system.

The sensors that are silent right now are the ones with the `data-silent` tag, so you can also filter on that tag in the sensor list.

## Prerequisites

- The [Playbook extension](../../5-integrations/extensions/limacharlie/playbook.md) (`ext-playbook`) is subscribed in the Organization.
- [Insight](../../1-getting-started/core-concepts.md#insight) (data retention) is enabled, which is the default. The check reads the timeline of data stored for each sensor.

## Step 1: Choose the sensors to watch

The playbook uses a sensor selector to pick the sensors to check. The simplest selector is a tag, for example `firewall`, applied to the sensors you want to watch.

- With an installation key that has the tag, every sensor enrolled with that key, including the per-device sensors an adapter creates, gets it automatically.
- Otherwise, add the tag from the sensor list in the web app or with `limacharlie tag add`.

You can also select by platform with `plat == fortigate`, by hostname with `hostname contains "fw-"`, or combine conditions. See [Sensor Selector Expressions](../../8-reference/sensor-selector-expressions.md).

## Step 2: Create an API key for the playbook

The playbook calls the LimaCharlie API with its own key. Create one with only these permissions:

| Permission | Used to |
|---|---|
| `sensor.list` | list the sensors matching the selector |
| `insight.evt.get` | check whether data from each sensor was stored |
| `sensor.tag` | add and remove the `data-silent` tag |

The following command creates the key and stores it in the [secret Hive](../../7-administration/config-hive/secrets.md) as `silent-sensors-playbook`, so it can be referenced as `hive://secret/silent-sensors-playbook`:

```bash
limacharlie api-key create \
  --name silent-sensors-playbook \
  --permissions sensor.list,sensor.tag,insight.evt.get \
  --store-secret silent-sensors-playbook
```

## Step 3: Create the playbook

In the web app, go to **Automation > Playbooks**, create a playbook named `silent-sensors`, set the **Python SDK** selector to v5 and paste the code below. The constants at the top are defaults, and each D&R rule can override them as shown in Step 4.

```python
--8<-- "snippets/python/silent_sensors_playbook.py"
```

To create it with the CLI instead, save the code above as `silent_sensors_playbook.py` and run:

```bash
python3 -c 'import json; print(json.dumps({"sdk_version": "5", "python": open("silent_sensors_playbook.py").read()}))' > silent-sensors.json
limacharlie hive set --hive-name playbook --key silent-sensors --input-file silent-sensors.json --enabled
```

!!! note
    The playbook uses the Python SDK v5, so its record must have `sdk_version` set to `"5"`. See [Python SDK version](../../5-integrations/extensions/limacharlie/playbook.md#python-sdk-version).

## Step 4: Run it on a schedule

Create a D&R rule that runs the playbook every 30 minutes.

Detect:

```yaml
target: schedule
event: 30m_per_org
op: exists
path: event/frequency
```

Respond:

```yaml
- action: extension request
  extension name: ext-playbook
  extension action: run_playbook
  extension request:
    name: '{{ "silent-sensors" }}'
    credentials: '{{ "hive://secret/silent-sensors-playbook" }}'
    data:
      selector: '{{ "`firewall` in tags" }}'
      threshold_minutes: 60
```

With the CLI, save the two parts as `detect.yaml` and `respond.yaml` and run:

```bash
limacharlie dr set --key silent-sensors-check --detect detect.yaml --respond respond.yaml --enabled
```

Write text values as templates (`'{{ "..." }}'`): a plain string such as `selector: firewall` is read as a path in the schedule event and left out of the request. Numbers and `true`/`false` can be written as is. See [Writing the request values](../../8-reference/response-actions.md#writing-the-request-values). The settings you can pass are:

| Setting | Default | Meaning |
|---|---|---|
| `selector` | `` `firewall` in tags `` | Sensors to check. |
| `threshold_minutes` | `60` | Report a sensor once no data arrived from it for this many minutes. |
| `realert_hours` | `24` | Report a sensor again if it is still silent after this many hours. `0` reports it once per outage. |
| `report_recovery` | `false` | Also raise a `sensor-data-resumed` detection when a silent sensor sends data again. A run raises a single detection, so if the same run also finds newly silent sensors, the recovered ones are listed in `recovered` of that `sensor-data-silent` detection instead. |
| `silent_tag` | `data-silent` | Tag that marks silent sensors. |

To watch groups of sensors with different thresholds, for example firewalls after 1 hour and servers after 3 hours, create one D&R rule per group with its own `selector` and `threshold_minutes`. If the selectors of two rules can match the same sensor, give each rule its own `silent_tag`.

### When the alert fires

A sensor is reported on the first run after its data has been missing for `threshold_minutes`. With the 30-minute schedule, that is between `threshold_minutes` and `threshold_minutes + 30` minutes after the last data arrived, plus a few minutes for the data to be stored. Use a threshold of at least 30 minutes.

## Step 5: Send the alert where you need it

The detection uses the category `sensor-data-silent`. Like any detection, it appears in the Detections view and can trigger [D&R rules on the `detection` target](../../3-detection-response/alternate-targets.md) or be sent out by an Output.

To send it to a webhook, create an Output with the **Detection** stream and the [Webhook](../../5-integrations/outputs/destinations/webhook.md) destination, and limit it to this category:

```yaml
dest_host: https://alerts.example.com/limacharlie
secret_key: my-shared-secret
cat_white_list: |
  sensor-data-silent
  sensor-data-resumed
  sensor-data-check-error
```

The same `cat_white_list` setting works on other destinations, such as [Slack](../../5-integrations/outputs/destinations/slack.md), [Microsoft Teams](../../5-integrations/outputs/destinations/ms-teams.md) or [email (SMTP)](../../5-integrations/outputs/destinations/smtp.md).

The detection is raised by the Playbook extension, and what the playbook returned is under `detect.event.detection`:

```json
{
  "cat": "sensor-data-silent",
  "detect": {
    "event": {
      "event": "playbook_detection",
      "cat": "sensor-data-silent",
      "detection": {
        "summary": "1 sensor(s) sent no data in the last 60 minutes",
        "selector": "`firewall` in tags",
        "threshold_minutes": 60,
        "sensors": [
          {"sid": "36690639-573d-46d0-a867-6a1e2fa97591", "hostname": "fw-branch-02"}
        ],
        "recovered": [],
        "errors": []
      }
    },
    "routing": {
      "hostname": "ext-playbook",
      ...
    }
  },
  ...
}
```

The `routing` of the detection points to the Playbook extension's own sensor, not to the silent devices. Use the `sid` and `hostname` values in `detect.event.detection.sensors` to identify the devices.

To send a short message rather than the whole detection, for example to a chat webhook, add a `custom_transform` to the Output:

```yaml
custom_transform: |
  {
    "text": "{{ .detect.event.detection.summary }}: {{ range .detect.event.detection.sensors }}{{ .hostname }} {{ end }}"
  }
```

This produces `{"text": "1 sensor(s) sent no data in the last 60 minutes: fw-branch-02 "}`.

## Testing the setup

Run the playbook on demand with the same settings as the rule:

```bash
limacharlie extension request --name ext-playbook --action run_playbook --data '{
  "name": "silent-sensors",
  "credentials": "hive://secret/silent-sensors-playbook",
  "data": {"selector": "`firewall` in tags", "threshold_minutes": 60}
}'
```

The response contains what the playbook returned: a summary of the run under `data` and, when a sensor just went silent, the `detection` and `cat` that were raised:

```yaml
data:
  cat: sensor-data-silent
  data:
    checked: 3
    newly_silent:
    - hostname: fw-branch-02
      sid: 36690639-573d-46d0-a867-6a1e2fa97591
    recovered: []
    errors: []
    silent: 1
  detection:
    ...
```

Running it again right away reports `newly_silent: []`, because `fw-branch-02` already has the `data-silent` tag.

To see the alert path end to end, use a short `threshold_minutes` (such as `10`) on a test sensor that has stopped sending data, then set it back.

## Things to know

- **Large numbers of sensors.** The playbook makes one API call per sensor, eight at a time. For several thousand sensors, split them into more than one D&R rule with narrower selectors.
- **Sensors that never sent data.** A per-device sensor is created when the first log for that device arrives, so a device that has never sent a log has no sensor and cannot be reported.
- **Errors.** If checking or tagging a sensor fails, for example because it was deleted during the run or the API key lacks a permission, the playbook skips it and checks the other sensors. It raises a `sensor-data-check-error` detection listing the failures, so a broken check does not look like a quiet one. When the same run also finds newly silent sensors, the failures are listed under `errors` in the `sensor-data-silent` detection instead. The sensor is checked again on the next run.
- **Deleted sensors** are not checked.
- **Removing a sensor from the watch list.** Remove its tag or change the selector. If the sensor still has the `data-silent` tag, remove that tag too.
