# Cloud CLI

The Cloud CLI extension runs cloud-provider CLIs (AWS, Azure, GCP, Okta, etc.) as D&R response actions. Use it to take action *in* a cloud service when a LimaCharlie detection fires. For example, a rule can disable an Okta user, isolate an EC2 instance, or revoke a GitHub token.

The extension uses the native CLI of each platform. Every action that the CLI can do is available as an automated response.

## When to use Cloud CLI vs API Integrations

- **Cloud CLI** — *write* actions into an external service (run a command, change state).
- **[API Integrations](../../api-integrations/index.md)** — *read* from an external service for enrichment (look up reputation, geolocation, etc.).

Most setups use both. API integrations enrich detections with context, and Cloud CLI acts on them.

## Supported Platforms

- [1Password](1password.md)
- [AWS](aws.md)
- [Azure](azure.md)
- [DigitalOcean](digitalocean.md)
- [GitHub](github.md)
- [Google Cloud](google-cloud.md)
- [Microsoft 365](microsoft365.md)
- [Okta](okta.md)
- [SDM](sdm.md)
- [Sublime](sublime.md)
- [Tailscale](tailscale.md)
- [Vultr](vultr.md)

## See Also

- [Extensions Overview](../index.md)
- [Using Extensions](../using-extensions.md)
- [API Integrations](../../api-integrations/index.md)
