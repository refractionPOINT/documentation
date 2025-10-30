# Vultr

The [Vultr](https://vultr.com/) CLI, or `vultr-cli`, is the official CLI for the Vultr API. With this component of the Cloud CLI Extension, you can interact with Vultr directly from LimaCharlie.

This extension makes use of Vultr's official CLI tool, which can be found [here](https://github.com/vultr/vultr-cli). Reference documentation can be found [here](https://www.vultr.com/news/how-to-easily-manage-instances-with-vultr-cli/).

## Example

The following example of a response action will enumerate a list of instance within a Vultr account.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "vultr-cli" }}'
    command_line: '{{ "instance list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To utilize `vultr-cli` capabilities, you will need:

* A personal access token. To create one, click [here](https://my.vultr.com/settings/#settingsapi).
* Your access token will need to have access control open to IPv6
  ![Screenshot 2024-04-25 at 10.31.29 AM.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/Screenshot 2024-04-25 at 10.31.29 AM.png)
* Create a secret in the secrets manager in the following format:

  ```
  personalAccessToken
  ```
