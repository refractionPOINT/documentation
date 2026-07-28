# Network Monitoring

The LimaCharlie Agentic SecOps Workspace integrates with Zeek for network security monitoring. The integration gives semantic analysis at scale, artifact ingestion, and detection and response capabilities. It automates threat detection and makes incident investigation and response efficient. This helps an organization to keep pace with new network threats and to maintain its security posture.

## Network monitoring problems

- **Scalability issues:** Traditional monitoring tools cannot process the increased volume and variety of network traffic. The result is low performance and less visibility.
- **Lack of semantic analysis:** Many network monitoring solutions only capture and store network traffic data. They do not do a semantic analysis of the content. This makes it difficult to find and understand sophisticated threats.
- **Limited automation and response capabilities:** Many monitoring tools do not have advanced detection, automation, and response features. An operator must act manually, and incident response is slower.

### LimaCharlie's solution

- **Scalable semantic security monitoring:** LimaCharlie uses the Zeek platform to do semantic security monitoring at scale. The Zeek service analyzes ingested PCAP files automatically. It extracts structured data about network activity and possible security threats.
- **Seamless integration with Artifact Ingestion:** The LimaCharlie Zeek extension integrates with the Artifact Ingestion system. When the system ingests a PCAP file, the Zeek service processes it and creates detailed log files. The Artifact Ingestion system then ingests those log files for more analysis and action.
- **Customizable Detection & Response (D&R) rules:** The Zeek log files are artifacts in LimaCharlie. A security team can write D&R rules against these artifacts to automate threat detection and response. Customize the rules for the security requirements of your organization to find and mitigate threats quickly.
- **Efficient incident investigation and response:** The integration with Zeek gives a security team contextual data about network activity for efficient incident investigations. The query capabilities of LimaCharlie find the relevant artifacts quickly. The team can then contain and remediate the threats.
