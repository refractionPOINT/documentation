# WEL Monitoring

LimaCharlie's SecOps Cloud Platform transforms Windows Event Log monitoring by providing real-time visibility, streamlined infrastructure, and powerful detection and response capabilities. Effectively monitor and protect your Windows environments, ensuring rapid detection and response to potential security incidents.

## WEL monitoring problems

* **Limited real-time visibility:** Traditional WEL monitoring solutions often rely on periodic log collection, resulting in delayed visibility into potential security incidents, limiting real-time visibility.
* **Complex and costly infrastructure:** Forwarding WEL data to a centralized monitoring system typically requires additional infrastructure, such as log collectors and forwarders, which can be complex to set up and maintain, as well as costly to scale.
* **Difficulty in creating custom detection rules:** Writing custom rules to detect malicious behavior in WEL data can be challenging, especially when dealing with large volumes of logs and a lack of standardized formats.

## LimaCharlie's solution

* **Real-time WEL ingestion:** LimaCharlie's Sensor enables direct, real-time importation of WEL data, eliminating the need for complex forwarding infrastructure and reducing costs and management overhead.
* **Powerful Detection & Response engine:** Ingested WEL data is automatically indexed against common indicators of compromise (IoCs) and processed through LimaCharlie's advanced Detection and Response engine, enabling rapid detection of malicious activity.
* **Flexible and customizable rule creation:** With WEL data structured as JSON, security teams can easily create custom D&R rules to detect and respond to specific Windows events as they occur, tailoring the monitoring process to their unique needs and environment.
* **Historical log analysis:** Import historical event log data from disk, empowering teams to conduct in-depth investigations and gain valuable context around endpoint activity.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.