# Ingesting Windows Event Logs

You can enable real-time Windows Event Log (WEL) ingestion using the LimaCharlie EDR Sensor.

First, navigate to the Exfil Control section of LimaCharlie and ensure that `WEL` events are enabled for your Windows rules.

Next, navigate to the `Artifact Collection` section and set up an artifact collection rule for the Windows Event Log(s) of interest.

To ingest WEL real-time events in the timeline, use the `wel://[Log Name]` format. For example, to ingest the System event log, you'd use the following pattern:

`wel://system:*`

Difference between `.evtx` versus `wel://` ingestion

If you specify the file on disk, via the `evtx` file extension (as seen in the image above), LimaCharlie will upload the entire Windows Event Log file from disk. This will be represented as a collected artifact, not as real-time events on the sensor's timeline. This method incurs regular artifact ingestion costs for "Telemetry Sources" as seen on our [pricing](https://limacharlie.io/pricing) page.

If you ingest Windows Event Logs with a `wel://` pattern, they are streamed in real-time as first-class telemetry alongside the native EDR events, and are included in the flat rate price of the sensor.

After you apply those, you should start seeing your Windows Event Log data coming through for your endpoints. You can verify this by going into the Timeline view and choosing `WEL` event type.
