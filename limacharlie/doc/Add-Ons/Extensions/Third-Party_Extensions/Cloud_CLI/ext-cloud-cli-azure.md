# Azure

The Azure CLI is a set of commands used to create and manage Azure resources. With this component of the Cloud CLI Extension, you can interact with Azure directly from LimaCharlie.

This extension makes use of the Azure CLI, which can be found [here](https://learn.microsoft.com/en-us/cli/azure/get-started-with-azure-cli).

## Example

The following example returns a list of virtual machines and their respective details in Azure.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "az" }}'
    command_line: '{{ "vm list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To utilize the Azure CLI, you will need:

* An application and a [service principal](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal) with the appropriate permissions and a [client secret](https://learn.microsoft.com/en-us/entra/identity-platform/howto-create-service-principal-portal#option-3-create-a-new-client-secret)
* Create a secret in the secrets manager in the following format:

```
appID/clientSecret/tenantID
```

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.
