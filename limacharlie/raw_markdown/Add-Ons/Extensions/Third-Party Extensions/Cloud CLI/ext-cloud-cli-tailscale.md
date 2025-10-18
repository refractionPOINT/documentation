# Tailscale

The Tailscale CLI brings Tailscale's powerful software-defined networking, based on WireGuard, to the command line. This Extension allows you to interact with a Tailscale network(s) from LimaCharlie.

This extension makes use of Tailscale's native CLI, which can be found [here](https://tailscale.com/kb/1031/install-linux).

## Example

Returns the current Tailscale status.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "tailscale" }}'
    command_line: '{{ "status --json" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To utilize Tailscale's CLI capabilities, you will need:

* An [auth key](https://tailscale.com/kb/1085/auth-keys)

* Create a secret in the secrets manager in the following format:

```
authKey
```
