# Ingesting Defender Event Logs

The Windows Sensor can listen, alert, and automate based on various Defender events.

This is done by ingesting [artifacts from the Defender Event Log Source](../../artifacts.md) and using [Detection & Response rules](../../detection-and-response.md) to take the appropriate action.

A config template to alert on the common Defender events of interest is available [here](https://github.com/refractionPOINT/templates/blob/master/anti-virus/windows-defender.yaml). The template can be used in conjunction with [Infrastructure Extension](../../ext-infrastructure.md) or its user interface in the [web app](https://app.limacharlie.io).

Specifically, the template alerts on the following Defender events:

* windows-defender-malware-detected (`event ID 1006`)
* windows-defender-history-deleted (`event ID 1013`)
* windows-defender-behavior-detected (`event ID 1015`)
* windows-defender-activity-detected (`event ID 1116`)
