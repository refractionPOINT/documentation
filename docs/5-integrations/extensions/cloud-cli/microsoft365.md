# Microsoft 365

The CLI **for Microsoft 365** is a tool that helps you manage Microsoft 365 tenants and SharePoint framework projects. This component of the Cloud CLI Extension lets you interact with Microsoft 365 tenants directly from LimaCharlie.

This extension uses [the PnP Microsoft 365 CLI](https://github.com/pnp/cli-microsoft365).

## Example

This example disables the user account that has the given user ID.

```yaml
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

- The Microsoft 365 CLI documentation shows that many authentication mechanisms are available. LimaCharlie now uses a client secret. For details about how to provision an app, see the [Register an app quickstart](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app) from Microsoft.
- When you call the extension, LimaCharlie first runs the `m365 login` command with the credentials that you supply.
- Create a secret in the secrets manager in this format:

  ```text
  appID/clientSecret/tenantID
  ```
