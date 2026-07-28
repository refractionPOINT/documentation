# Sublime

The Sublime Security CLI gives access to the email platform of Sublime from the command line. This component of the Cloud CLI Extension lets you interact with the email platform of Sublime directly from LimaCharlie.

This extension uses [Sublime Security's native CLI](https://docs.sublimesecurity.com/reference/analysis-api-cli). The CLI is a Python package — its [source code](https://github.com/sublime-security/sublime-cli) is on GitHub.

## Example

This response action returns information about the authenticated Sublime Security user.

```yaml
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "sublime" }}'
    command_line: '{{ "me" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To use the CLI capabilities of Sublime, you need:

- An API key. For details about how to provision a key, see the [authentication reference](https://docs.sublimesecurity.com/reference/authentication) from Sublime Security.
- Create a secret in the secrets manager in this format:

```text
api_key
```
