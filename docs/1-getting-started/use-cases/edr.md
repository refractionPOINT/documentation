# Endpoint Detection and Response (EDR)

The Agentic SecOps Workspace gives true real-time visibility, many detection capabilities, integration with open-source and managed rulesets, and vendor-agnostic telemetry ingestion. LimaCharlie uses an API-first approach and a flexible billing model, and it integrates with your existing security stack. With these capabilities, security teams can detect, investigate, and respond to threats without the limits of a traditional EDR solution.

## EDR problems

Endpoint Detection and Response (EDR) solutions let an organization detect, investigate, and respond to threats on endpoints. But traditional EDR solutions cause several problems:

- **Lack of real-time visibility:** Many EDR solutions use periodic scans or collect data with a delay. This makes it difficult to detect threats and to respond to them in real time.
- **Limited customization and flexibility:** Traditional EDRs often use proprietary detection languages or rulesets. This limits the ability of a security team to write custom detections for its own environment.
- **Vendor lock-in and high costs:** Legacy EDR solutions often need long-term contracts and high minimum commitments. They can be expensive to scale, which causes vendor lock-in and budget constraints.

## LimaCharlie's solution

- **True real-time EDR:** LimaCharlie streams verbose telemetry from the endpoint sensor to the cloud over a semi-persistent TLS connection. This gives true real-time visibility. The endpoint can do a response action within 100ms of the action or behavior that triggers it. This decreases the time to detect threats and to respond to them.
- **Versatile detection syntax:** LimaCharlie uses a detection syntax that is based on YAML. Security teams can write complex detections, track state, and build detection logic with multiple steps. With this syntax, a team writes custom detections for its own needs and environment.
- **Integration with open-source and managed rulesets:** Use the detections that security professionals write in managed and open-source rulesets. Sources such as SOC Prime, Soteria, Sigma, and YARA are available with one click. Teams decrease their costs and respond to new threats sooner.
- **Reduced mean time to respond (MTTR):** Security teams can run a full set of remediation responses with LimaCharlie. Examples are a memory dump and a kill of a process tree. LimaCharlie makes it easier to activate rulesets and to build custom rules, which decreases MTTR.
- **Vendor-agnostic telemetry ingestion:** Ingest data from any source in real time, including existing EDR solutions. Security teams avoid vendor lock-in. They can use the Detection, Automation, and Response Engine of the ASW on all of their telemetry, from any source.
