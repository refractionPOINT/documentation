# Extensions

Extensions add capabilities to LimaCharlie. Each extension is a separate piece of functionality that an organization subscribes to from the marketplace. After you subscribe, you can configure an extension, call it from a D&R rule, or invoke it directly.

For the subscription and configuration model, and how to invoke extensions, see [Using Extensions](using-extensions.md).

## Categories

- [**LimaCharlie Extensions**](limacharlie/index.md) — built and maintained by LimaCharlie. Includes platform features (Git Sync, YARA Manager, Sensor Cull, Usage Alerts) and forensic data collection (Artifact, BinLib, Dumper, Payload Manager). Also includes workflow tools (Cases, Feedback, Playbook) and protection / detection tooling (EPP, Exfil, Integrity, Lookup Manager, Reliable Tasking).

- [**Third-Party Extensions**](third-party/index.md) — built by partners or the community to integrate external tools and services. Examples: Velociraptor (DFIR collections), Zeek (network analysis), Hayabusa / Atomic Red Team / YARA (detection tooling), PagerDuty / Twilio (notifications), OTX / SecureAnnex (threat intel).

- [**Cloud CLI**](cloud-cli/index.md) — a single extension that runs cloud-provider CLIs as D&R response actions. Each supported platform (AWS, Azure, GCP, Okta, GitHub, etc.) has its own configuration page.

## Building extensions

To publish your own extension, see the [Building Extensions](../../6-developer-guide/extensions/building-extensions.md) developer guide.

## See Also

- [Using Extensions](using-extensions.md)
- [API Integrations](../api-integrations/index.md) — the lookup side that goes with the action side of Cloud CLI
- [Outputs](../outputs/index.md) — to send data out instead of to act on it
