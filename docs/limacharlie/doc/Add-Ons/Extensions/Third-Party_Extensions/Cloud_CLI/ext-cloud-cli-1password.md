# 1Password

The 1Password CLI brings 1Password to the terminal, allowing you to interact with a 1Password instance from LimaCharlie.

This Extension makes use of 1Password's native CLI, which can be found [here](https://developer.1password.com/docs/cli).

## 1Password Account Types

Please note that some 1Password functionality is limited to 1Password Business. Please validate you have the correct type of account(s) to ensure that commands run.

## Example

Returns a list of all items the account has read access to by default.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "op" }}'
    command_line: '{{ "item list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To utilize 1Password's automated CLI capabilities, you will need to create and utilize a Service Account. More information can be found [here](https://developer.1password.com/docs/service-accounts/get-started/).

* Create a secret in the secrets manager in the following format:

```
serviceAccountToken
```
