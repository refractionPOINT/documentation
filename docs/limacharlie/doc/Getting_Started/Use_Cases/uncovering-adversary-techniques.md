# Uncovering Adversary Techniques

LimaCharlie's SecOps Cloud Platform provides a comprehensive approach to combating ransomware, focusing on early detection during the reconnaissance stage and rapid response in the event of a detonation. By gathering telemetry from a wide range of sources, enabling widespread deployment, and leveraging real-time response capabilities, LimaCharlie empowers organizations to effectively detect, stop, and mitigate ransomware attacks, minimizing damage and ensuring business continuity.

#### Problems with uncovering adversary techniques

Ransomware attacks have become increasingly sophisticated and targeted, posing a significant threat to organizations of all sizes. The challenges in effectively combating ransomware include:

* **Extended dwell time:** Ransomware attacks often involve weeks or months of reconnaissance, during which malicious actors seek to identify optimal detonation points. Detecting and stopping the attack during this stage is crucial but challenging.
* **Difficulty in correlating data:** Malicious actors often move around and attempt to hide their presence, making it difficult to identify and correlate their activities across various systems and data sources.
* **Rapid spread and damage:** In the event of a successful ransomware detonation, the malware can spread rapidly, encrypting files and causing significant damage before security teams can respond.

#### LimaCharlie's solution

LimaCharlie's SecOps Cloud Platform offers a comprehensive approach to combating ransomware, focusing on early detection during the reconnaissance stage and rapid response in the event of a detonation:

* **Comprehensive telemetry gathering:** LimaCharlie gathers telemetry and external artifacts from a wide range of sources, including endpoints, networks, and cloud environments. By normalizing all data to JSON and processing it through the SecOps Cloud Platform's detection, automation, and response engine, LimaCharlie gains a global view of the organization's security posture, enabling it to identify suspicious activities and correlations that may indicate a ransomware attack in progress.
* **Early detection through widespread deployment:** LimaCharlie's ability to deploy everywhere allows it to detect intruders faster than the competition, often before malicious actors can lay an effective trap. By monitoring everything from one place and leveraging advanced detection logic, LimaCharlie can identify and stop ransomware attacks during the crucial reconnaissance stage.
* **Real-time response with semi-persistent TLS connection:** In the event of a ransomware detonation, LimaCharlie's real-time, semi-persistent TLS connection with endpoints enables an unparalleled response capability. If detection logic is in place to catch a ransomware event, response actions can be taken across the entire fleet in real-time. This allows security teams to instantly isolate affected machines from the network while maintaining command and control through LimaCharlie, minimizing further damage and data exfiltration.
* **Advanced threat hunting and remediation:** With LimaCharlie, analysts responding to a ransomware event have access to all affected machines and a full year's history of telemetry. This enables them to run remediation scripts on the endpoints, kill process trees, and hunt for any malicious presence. By leveraging advanced indicators, such as FILE_TYPE_ACCESSED events, security teams can detect ransomware detonation events before the malware proliferates, significantly reducing the impact of the attack.

## What's Next

* [WEL Monitoring](./wel-monitoring.md)
