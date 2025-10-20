# DigitalOcean

The DigitalOcean CLI, or `doctl`, is the official CLI for the DigitalOcean API. With this component of the Cloud CLI Extension, you can interact with DigitalOcean directly from LimaCharlie.

This extension makes use of DigitalOcean's official CLI tool, which can be found [here](https://github.com/digitalocean/doctl). Reference documentation can be found [here](https://docs.digitalocean.com/reference/doctl/reference/).

## Example

The following example of a response action will enumerate a list of compute droplets within a DigitalOcean instance.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "doctl" }}'
    command_line: '{{ "compute droplet list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To utilize `doctl` capabilities, you will need:

* A personal access token. More information on this can be found [here](https://docs.digitalocean.com/reference/api/create-personal-access-token/).
* Create a secret in the secrets manager in the following format:

  ```
  personalAccessToken
  ```

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.
