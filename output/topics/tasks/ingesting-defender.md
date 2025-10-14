```markdown
# Ingesting Defender Event Logs

The Windows Sensor can listen, alert, and automate based on various Defender events.

This is done by ingesting [artifacts from the Defender Event Log Source](/v2/docs/artifacts) and using [Detection & Response rules](/v2/docs/detection-and-response) to take the appropriate action.

## Configuration Template

A config template to alert on the common Defender events of interest is available [here](https://github.com/refractionPOINT/templates/blob/master/anti-virus/windows-defender.yaml). The template can be used in conjunction with [Infrastructure Extension](/v2/docs/ext-infrastructure) or its user interface in the [web app](https://app.limacharlie.io).

## Monitored Defender Events

Specifically, the template alerts on the following Defender events:

* **windows-defender-malware-detected** (`event ID 1006`)
* **windows-defender-history-deleted** (`event ID 1013`)
* **windows-defender-behavior-detected** (`event ID 1015`)
* **windows-defender-activity-detected** (`event ID 1116`)

## How It Works

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.
```