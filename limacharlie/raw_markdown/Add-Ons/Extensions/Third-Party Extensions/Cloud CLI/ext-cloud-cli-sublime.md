# Sublime

The Sublime Security CLI brings the power of Sublime's email platform to the command-line. With this component of the Cloud CLI Extension, you can interact with Sublime's email platform directly from LimaCharlie.

This extension makes use of Tailscale's native CLI, which can be found [here](https://docs.sublimesecurity.com/reference/analysis-api-cli). The CLI is a Python package - the source code can be found [here](https://github.com/sublime-security/sublime-cli).

## Example

The following response action returns information about the currently authentication Sublime Security user.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "sublime" }}'
    command_line: '{{ "me" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To utilize Sublime's CLI capabilities, you will need:

* You will need an API key. More information about provisioning an API key can be found [here](https://docs.sublimesecurity.com/reference/authentication).

* Create a secret in the secrets manager in the following format:

```
api_key
```
