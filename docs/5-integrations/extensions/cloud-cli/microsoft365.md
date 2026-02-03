# Microsoft 365

The CLI **for Microsoft 365** is a tool created to help manage Microsoft 365 tenant(s) and SharePoint framework projects. With this component of the Cloud CLI Extension, you can interact with a Microsoft 365 tenant(s) directly from LimaCharlie.

This extension makes use of the PnP Microsoft 365 CLI, which can be found [here](https://github.com/pnp/cli-microsoft365).

## Example

The following example disables the user account with the provided user ID.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "m365" }}'
    command_tokens:
      - entra
      - user
      - set
      - '--id'
      - '{{ .event.user_id  }}'
      - '--accountEnabled'
      - false
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

* Per the Microsoft 365 CLI documentation, there are multiple login or authentication mechanisms available. The current LimaCharlie implementation utilizes a client secret for authentication. More information on provisioning client secrets can be found [here](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app).
* Upon invocation, LimaCharlie will first run the `m365 login` command with the credentials provided.
* Create a secret in the secrets manager in the following format:

  ```
  appID/clientSecret/tenantID
  ```
