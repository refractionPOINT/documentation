# Azure

The Azure CLI is a set of commands that create and manage Azure resources. This component of the Cloud CLI Extension lets you interact with Azure directly from LimaCharlie.

This extension uses [the Azure CLI](https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli).

## Example

This example returns a list of the virtual machines in Azure and their details.

```yaml
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    tool: '{{ "az" }}'
    command_line: '{{ "vm list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To use the Azure CLI, you need:

- An application and a [service principal](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal) with the correct permissions and a [client secret](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal#option-3-create-a-new-client-secret)
- Create a secret in the secrets manager in this format:

```text
appID/clientSecret/tenantID
```
