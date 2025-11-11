# Frequently Asked Questions

Common questions about the LimaCharlie platform.

## General

**Q: What platforms does LimaCharlie support?**

A: LimaCharlie sensors support Windows, Linux, macOS, Chrome OS, and cloud platforms (AWS, Azure, GCP).

**Q: Is there a free tier?**

A: Yes! LimaCharlie offers a free tier for testing and small deployments. Check the [pricing page](https://limacharlie.io/pricing) for details.

**Q: Where is my data stored?**

A: You can choose your data residency region. LimaCharlie operates in multiple regions worldwide.

## Sensors

**Q: How much overhead do sensors add?**

A: LimaCharlie sensors are lightweight, typically using <1% CPU and <50MB RAM under normal operation.

**Q: Can I deploy sensors without internet access?**

A: Sensors require outbound HTTPS connectivity to the LimaCharlie cloud. See [Sensor Connectivity](../Sensors/sensor-connectivity.md) for requirements.

## Detection & Response

**Q: How do I test detection rules without alerting?**

A: Use the testing feature in the web console to validate rules against historical events before deployment.

**Q: Can I import Sigma rules?**

A: Yes! LimaCharlie supports importing and converting Sigma rules. See the Sigma integration documentation.

## Data & Privacy

**Q: Does LimaCharlie store my data?**

A: Telemetry retention is configurable per organization. You control data retention periods and can export or delete data at any time.

**Q: Is my data encrypted?**

A: Yes, all data is encrypted in transit (TLS 1.2+) and at rest (AES-256).

## Support

**Q: How do I get help?**

A: Join our [Community Slack](https://slack.limacharlie.io), email [support@limacharlie.io](mailto:support@limacharlie.io), or check the documentation.

**Q: Do you offer professional services?**

A: Yes, professional services are available for deployment, detection engineering, and custom integrations.
