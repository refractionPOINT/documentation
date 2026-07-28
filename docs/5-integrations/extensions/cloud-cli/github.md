# GitHub

The GitHub CLI is a tool that gives access to GitHub from the terminal. It lets you control Git accounts, repositories, organizations, and users from the CLI. This component of the Cloud CLI Extension lets you interact with GitHub directly from LimaCharlie.

This extension uses [the GitHub CLI](https://cli.github.com/manual/).

## Example

This example returns a list of GitHub organizations.

```yaml
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "gh" }}'
    command_line: '{{ "org list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To use the GitHub CLI, you need:

- A [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
- Create a secret in the secrets manager in this format:

```text
access_token
```
