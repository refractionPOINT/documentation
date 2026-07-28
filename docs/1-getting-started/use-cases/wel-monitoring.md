# WEL Monitoring

The LimaCharlie Agentic SecOps Workspace changes how you monitor the Windows Event Log. It gives visibility in real time, simpler infrastructure, and detection and response capabilities. You can monitor and protect your Windows environments and respond quickly to a security incident.

## WEL monitoring problems

- **Limited real-time visibility:** Traditional WEL monitoring solutions collect logs at intervals. Visibility into a possible security incident is therefore delayed, and there is little visibility in real time.
- **Complex and costly infrastructure:** To send WEL data to a central monitoring system, you need more infrastructure, such as log collectors and forwarders. This infrastructure is difficult to set up and maintain, and expensive to scale.
- **Difficulty in creating custom detection rules:** Custom rules that detect malicious behavior in WEL data are difficult to write. Large volumes of logs and the absence of a standard format add to the difficulty.

### LimaCharlie's solution

- **Real-time WEL ingestion:** The LimaCharlie Sensor imports WEL data directly and in real time. You do not need a complex forwarding infrastructure, so costs and management work are lower.
- **Detection & Response (****) engine**: LimaCharlie indexes the ingested WEL data against common indicators of compromise (IoCs). It then sends the data through the Detection and Response engine, which detects malicious activity quickly.
- **Flexible and customizable rule creation:** WEL data is structured as JSON. Security teams can create custom D&R rules that detect and respond to specific Windows events when the events occur. Each team adapts the monitoring to its own environment.
- **Historical log analysis:** Import historical event log data from disk. Teams can then do detailed investigations and get context about the activity on an endpoint.

Like agents, Sensors send telemetry to the LimaCharlie platform as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless solution that connects the endpoints of an organization to the cloud securely.

## What's Next

- [SOAR / Automation](soar-automation.md)
