# StrongDM

The StrongDM CLI lets you manage your StrongDM platforms from the command line. This component of the Cloud CLI Extension lets you interact with StrongDM directly from LimaCharlie.

See the [StrongDM CLI documentation](https://www.strongdm.com/docs/cli/) for more detail.

## Example

This response action returns a list of all the users in your Organization.

```yaml
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "sdm" }}'
    command_line: '{{ "admin users list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To use the CLI capabilities of StrongDM, you need:

- An admin or service account token. For details about how to provision a token, see the [tokens and keys reference](https://www.strongdm.com/docs/admin/tokens-and-keys/) from StrongDM.
- Create a secret in the secrets manager in this format:

```text
token
```
