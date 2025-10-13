The GitHub CLI is a tool that brings GitHub to the terminal, allowing you to interact with and control Git accounts, repositories, organizations, and users from the CLI. With this component of the Cloud CLI Extension, you can interact with GitHub directly from LimaCharlie.

This extension makes use of the GitHub CLI, which can be found [here](https://cli.github.com/manual/).

## Example

The following example returns a list of GitHub organizations.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "gh" }}'
    command_line: '{{ "org list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To utilize the GitHub CLI, you will need:

* A [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
* Create a secret in the secrets manager in the following format:

```
access_token
```

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.
