# DigitalOcean

The DigitalOcean CLI, or `doctl`, is the official CLI for the DigitalOcean API. This component of the Cloud CLI Extension lets you interact with DigitalOcean directly from LimaCharlie.

This extension uses [DigitalOcean's official `doctl` CLI tool](https://github.com/digitalocean/doctl). [Reference documentation](https://docs.digitalocean.com/reference/doctl/reference/) is also available.

## Example

This example of a response action lists the compute droplets in a DigitalOcean instance.

```yaml
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    tool: '{{ "doctl" }}'
    command_line: '{{ "compute droplet list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To use the `doctl` capabilities, you need:

- A personal access token. See the [create-personal-access-token reference](https://docs.digitalocean.com/reference/api/create-personal-access-token/) from DigitalOcean.
- Create a secret in the secrets manager in this format:

  ```text
  personalAccessToken
  ```
