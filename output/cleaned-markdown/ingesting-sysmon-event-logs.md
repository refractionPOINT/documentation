# Ingesting Sysmon Event Logs

Sysmon can be a valuable addition to any defender's toolkit, given it's verbosity and generous log data. It's worth noting that LimaCharlie's native EDR capabilities mirror much of the same telemetry. However, Sysmon and LimaCharlie can be combined to provide granular coverage across Windows systems.

With Sysmon deployed, you can utilize LimaCharlie's native Windows Event Log (WEL) streaming capabilities to bring logs into the Sensor timeline.

1. Install [Sysmon](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon) on the endpoint.

   * This can easily be done via LimaCharlie's Payload functionality, with a rule, or manually.
   * Please note that the LimaCharlie agent must be restarted in order for Sysmon data to show up in the timeline.
   * Example rule to deploy Sysmon via payloads on Windows systems tagged with `deploy-sysmon`:

     ```
     detect:
       events:
         - CONNECTED
       op: and
       rules:
         - op: is platform
           name: windows
         - op: is tagged
           tag: deploy-sysmon
     respond:
     - action: task
       command: put --payload-name sysmon.exe --payload-path "C:\Windows\Temp\sysmon.exe"
     - action: wait
       duration: 10s
     - action: task
       command: put --payload-name sysmon-config.xml --payload-path "C:\Windows\Temp\sysmon-config.xml"
     - action: wait
       duration: 10s
     - action: task
       command: run --shell-command "C:\Windows\Temp\sysmon.exe -accepteula -i C:\Windows\Temp\sysmon-config.xml"
     - action: wait
       duration: 10s
     - action: task
       command: file_del "C:\Windows\Temp\sysmon.exe"
     - action: task
       command: file_del "C:\Windows\Temp\sysmon-config.xml"
     - action: remove tag
       tag: deploy-sysmon
     - action: task
       command: restart
     ```

2. Within the Organization where you wish to collect Sysmon data, go to the `Event Collection > Event Collection Rules` section.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ingest-sysmon-1.png)

3. Ensure that for Windows systems, `WEL` events are collected.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ingest-sysmon-2.png)

4. Go to the `Artifact Collection` section and add a new collection rule with the following path to bring in all Sysmon events:

`wel://Microsoft-Windows-Sysmon/Operational:*`

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ingest-sysmon-3.png)

> **Note:** You can use tagging or other filters to narrow down the systems that logs are collected from.

## Event Filtering

You can filter events by event ID to import select events. For example:

`wel://Microsoft-Windows-Sysmon/Operational:16`

`wel://Microsoft-Windows-Sysmon/Operational:25`

5. Allow up to 10 minutes for data to come into LimaCharlie after setting up a new Artifact Collection rule. Data will flow in real-time after that point.

6. Navigate to the Timeline view of a Sensor to confirm that Sysmon logs are present. You can search for Event Type `WEL` and Search for `Microsoft-Windows-Sysmon` to validate the telemetry.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%2896%29.png)