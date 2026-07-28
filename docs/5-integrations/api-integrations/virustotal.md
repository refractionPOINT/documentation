# VirusTotal

## API Keys

Add the VirusTotal API key in the integrations menu in LimaCharlie.

## Usage

If you subscribe to the `vt` add-on and configure a VirusTotal API Key on the Integrations page, you can use VirusTotal as an API-based lookup.

```yaml
event: CODE_IDENTITY
op: lookup
path: event/HASH
resource: lcr://api/vt
metadata_rules:
  op: is greater than
  value: 1
  path: /
  length of: true
```

This rule does these steps:

- When a `CODE_IDENTITY` event occurs, the rule gets the `event/HASH` value and sends it to VirusTotal through the `api/vt` resource.
- When `api/vt` sends a response, the rule evaluates it with `metadata_rules` to see if the length of the response is greater than 1. Here, this means that more than 1 vendor reports that a hash is bad.

## Related Articles

- [VirusTotal Integration](../tutorials/virustotal-integration.md)
- [Extensions](../extensions/using-extensions.md)
