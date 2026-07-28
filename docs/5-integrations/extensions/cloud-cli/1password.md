# 1Password

The 1Password CLI gives access to 1Password from the terminal. It lets you interact with a 1Password instance from LimaCharlie.

This extension uses [1Password's native CLI](https://developer.1password.com/docs/cli).

## 1Password Account Types

Some 1Password functions are limited to 1Password Business. Check that you have the correct type of account, to make sure that the commands run.

## Example

By default, this returns a list of all the items that the account can read.

```yaml
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "op" }}'
    command_line: '{{ "item list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To use the automated CLI capabilities of 1Password, create and use a Service Account. For more detail, see the [Service Accounts getting-started guide](https://developer.1password.com/docs/service-accounts/get-started/) from 1Password.

- Create a secret in the secrets manager in this format:

```text
serviceAccountToken
```
