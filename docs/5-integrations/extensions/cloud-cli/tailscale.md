# Tailscale

The Tailscale CLI gives access to the software-defined networking of Tailscale, based on WireGuard, from the command line. This Extension lets you interact with Tailscale networks from LimaCharlie.

This extension uses [Tailscale's native CLI](https://tailscale.com/kb/1031/install-linux).

## Example

Returns the current Tailscale status.

```yaml
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "tailscale" }}'
    command_line: '{{ "status --json" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To use the CLI capabilities of Tailscale, you need:

- An [auth key](https://tailscale.com/kb/1085/auth-keys)
- Create a secret in the secrets manager in this format:

```text
authKey
```

## Command-line Interface

LimaCharlie Extensions let users expand and customize their security environments. Extensions integrate third-party tools, automate workflows, and add new capabilities. Organizations subscribe to Extensions. Each Extension gets specific permissions to interact with the infrastructure of the organization. An Extension can be private for custom use, or public to share with the community. This framework supports scalability, flexibility, and secure, repeatable deployments.
