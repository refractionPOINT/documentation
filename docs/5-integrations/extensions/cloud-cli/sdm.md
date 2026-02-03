# StrongDM

The StrongDM CLI allows you to manage your StrongDM platform(s) via the command-line. With this component of the Cloud CLI Extension, you can interact with StrongDM's directly from LimaCharlie.

More information about the StrongDM CLI can be found [here](https://www.strongdm.com/docs/cli/).

## Example

The following response action returns a list of all users in your Organization.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "sdm" }}'
    command_line: '{{ "admin users list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To utilize StrongDM's CLI capabilities, you will need:

* An admin or service account token. More information on provisioning this token can be found [here](https://www.strongdm.com/docs/admin/tokens-and-keys/).
* Create a secret in the secrets manager in the following format:

```
token
```
