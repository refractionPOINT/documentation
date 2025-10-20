# Detecting Sensors No Longer Sending Data

A common request is to alert an administrator if a Sensor that normally forwards data, stops or fails to send data. This LimaCharlie Playbook is meant to be triggered on a schedule by  rule. It checks for data sent, via the LimaCharlie Python SDK, within a given time window. If no data is sent during the time period, then an alert is generated, one per sensor.

### Example Playbook Code

```
import limacharlie
import time

SENSOR_SELECTOR = "plat == windows or plat == linux or plat == macos or plat == chrome"
DATA_WITHIN = 10 * 60 * 1000 # 10 minutes

def get_relevant_sensors(sdk, data) -> list[limacharlie.Sensor]:
    data = data["data"]
    sensor_selector = data.get("sensor_selector",SENSOR_SELECTOR)
    sensors = sdk.sensors(selector=sensor_selector)
    relevant_sensors = []
    for sensor in sensors:
        relevant_sensors.append(sensor)
    return relevant_sensors

def playbook(sdk, data) -> dict | None:

    # Get the sensors we care about.
    relevant_sensors = get_relevant_sensors(sdk, data)

    stopped_sensors = []

    # For each sensor, check if we've received data within that time period.
    for sensor in relevant_sensors:
        # To do that we will get the data overview and see if a recent time stamp is present.
        data_overview = sensor.getHistoricOverview(int(time.time() - DATA_WITHIN), int(time.time()))
        after = int(time.time() * 1000) - DATA_WITHIN
        for timestamp in data_overview:
            if timestamp > after:
                break
        else:
            stopped_sensors.append(sensor)

    # Report a detection for stopped sensors.
    if stopped_sensors:
        return {"detection":{
            "stopped_sensors": [sensor.getInfo() for sensor in stopped_sensors]
        }}
    return None
```

### Example D&R Rule to Trigger Playbook

```
#detect
event: 30m_per_org
op: exists
path: /
target: schedule

#respond
- action: extension request
  extension action: run_playbook
  extension name: ext-playbook
  extension request:
    credentials: '{{ "hive://secret/playbook-missing-data-creds" }}'
    name: '{{ "check-missing-data" }}'
```

### IaC Configuration

Import this IaC to your organization to create the playbook and corresponding rule that will trigger the playbook's execution.

> API Key Secret
>
> You'll need to create an API key for the playbook to execute and add it to the organization's secrets for the playbook to execute. The D&R rule in this configuration looks for a secret named `playbook-missing-data-creds`. If you name your secret something else, make sure the name is updated in the D&R rule's action, or the playbook will not be able to execute.

```
version: 3
hives:
    dr-general:
         Detect Sensors No Longer Sending Data:
            data:
                detect:
                    event: 30m_per_org
                    op: exists
                    path: /
                    target: schedule
                respond:
                    - action: extension request
                      extension action: run_playbook
                      extension name: ext-playbook
                      extension request:
                        credentials: '{{ "hive://secret/playbook-missing-data-creds" }}'
                        name: '{{ "check-missing-data" }}'
            usr_mtd:
                enabled: true

    playbook:
        check-missing-data:
            data:
                python: "import limacharlie\nimport time\n\nSENSOR_SELECTOR = \"plat == windows or plat == linux or plat == macos or plat == chrome\"\nDATA_WITHIN = 10 * 60 * 1000 # 10 minutes\n\ndef get_relevant_sensors(sdk, data) -> list[limacharlie.Sensor]:\n    data = data[\"data\"]\n    sensor_selector = data.get(\"sensor_selector\",SENSOR_SELECTOR)\n    sensors = sdk.sensors(selector=sensor_selector)\n    relevant_sensors = []\n    for sensor in sensors:\n        relevant_sensors.append(sensor)\n    return relevant_sensors\n\ndef playbook(sdk, data) -> dict | None:\n\n    # Get the sensors we care about.\n    relevant_sensors = get_relevant_sensors(sdk, data)\n\n    stopped_sensors = []\n\n    # For each sensor, check if we've received data within that time period.\n    for sensor in relevant_sensors:\n        # To do that we will get the data overview and see if a recent time stamp is present.\n        data_overview = sensor.getHistoricOverview(int(time.time() - DATA_WITHIN), int(time.time()))\n        after = int(time.time() * 1000) - DATA_WITHIN\n        for timestamp in data_overview:\n            if timestamp > after:\n                break\n        else:\n            stopped_sensors.append(sensor)\n    \n    # Report a detection for stopped sensors.\n    if stopped_sensors:\n        return {\"detection\":{\n            \"stopped_sensors\": [sensor.getInfo() for sensor in stopped_sensors]\n        }}\n    return None"
            usr_mtd:
                enabled: true
    secret:
        playbook-missing-data-creds:
            data:
                secret: CHANGEME
            usr_mtd:
                enabled: true
```
