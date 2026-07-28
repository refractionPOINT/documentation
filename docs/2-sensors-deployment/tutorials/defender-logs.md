# Ingesting Defender Event Logs

The Windows Sensor can listen for many Defender events. It can alert on these events and automate actions.

To do this, ingest [artifacts from the Defender Event Log Source](../../5-integrations/extensions/limacharlie/artifact.md). Then use [Detection & Response rules](../../3-detection-response/index.md) to take the correct action.

A [config template for common Defender events](https://github.com/refractionPOINT/templates/blob/master/anti-virus/windows-defender.yaml) is available. Use the template with the [Infrastructure Extension](../../5-integrations/extensions/limacharlie/infrastructure.md), or with the user interface of that extension in the [web app](https://app.limacharlie.io).

The template alerts on these Defender events:

- windows-defender-malware-detected (`event ID 1006`)
- windows-defender-history-deleted (`event ID 1013`)
- windows-defender-behavior-detected (`event ID 1015`)
- windows-defender-activity-detected (`event ID 1116`)
