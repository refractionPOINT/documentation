# What is LimaCharlie?

LimaCharlie is cloud-hosted security operations infrastructure that serves as an EDR, a SIEM, or both. Endpoint sensors, log ingestion, and detection and response (D&R) rules run on one multi-tenant system. It is a commercial service with usage-based pricing and a free tier.

The LimaCharlie [sensor](../2-sensors-deployment/index.md) provides EDR on Windows, macOS, Linux, and ChromeOS. [Adapters](../2-sensors-deployment/adapters/index.md) bring in logs from cloud, identity, and SaaS sources, and telemetry from an existing EDR such as CrowdStrike, SentinelOne, or Microsoft Defender. [D&R rules](../3-detection-response/index.md) act on every event as it arrives, and a year of telemetry stays searchable for hunting and investigation.

Each environment is its own organization, so service providers run every client from one account, and security teams run every business unit the same way. You run LimaCharlie from the web app, the `limacharlie` CLI, or the API, and [AI assistants](../6-developer-guide/mcp-server.md) operate it through the same CLI or the MCP server.

Our documentation can walk you through setting up your own Organization, deploying Sensors, writing detection and response rules, or outputting your data to any destination of your choosing. To dive in immediately, see our [Quickstart](quickstart.md) guide.

Dig in, and build the security program you need and have always wanted.

---

## See Also

- [Quickstart Guide](quickstart.md)
- [Core Concepts](core-concepts.md)
- [Use Cases](use-cases/edr.md)
