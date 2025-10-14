# Config Hive: Secrets

With its multitude of data ingestion and output options, LimaCharlie users can end up with a myriad of credentials and secret keys to faciliate unique data operations. However, not all users should be privy to these secret keys. Within the Config Hive, the `secrets` hive component allows you to decouple secrets from their usage or configuration across LimaCharlie. Furthermore, you can also grant permissions to users that allows them to see the configuration of an output, but not have access to the associated credentials.

The most common usage is for storing secret keys used by various [Adapters](/v2/docs/adapters) or [Outputs](/v2/docs/outputs). By referencing `secrets` within the Config Hive, we can configure these services without needing to reveal secret keys to all users.

Watch the video below to learn more about hive secrets, or continue reading below.

## Format

A secret record in `hive` has a very basic format:

```
{
    "secret": "data"
}
```

The `data` portion of the records in this hive must have a single key called `secret` who's value will be used by various LimaCharlie components.

## Permissions

The `secret` hive requires the following permissions for the various operations:

* `secret.get`
* `secret.set`
* `secret.del`
* `secret.get.mtd`
* `secret.set.mtd`

## Secret Management

Over time, and with enough integrations, you may need to create and/or update secrets on demand. We provide quick options for both via either the LimaCharlie CLI or web app.

### Creating Secrets

With the appropriate permissions, users can create secrets in the following ways:

1. Using the LimaCharlie CLI, secrets can be created using the `limacharlie hive set secret` command (example below).
2. Via the web app, under **Organization Settings** > **Secrets Manager**.

### Updating Secrets

Once they are set, secrets can be updated via the following methods:

1. Using the LimaCharlie CLI, secrets can be updated using the `limacharlie hive update secret` command.
2. Via the web app, **Organization Settings** > **Secrets Manager**. Select the secret you wish to update, and update in the dialog box. Click **Save Secret** to save changes in the platform.

## Usage

Using a secret in combination with an output has very few steps:

1. Create a secret in the `secret` hive
2. Create an Output and use the format `hive://secret/my-secret-name` as the value for a credentials field.

## Example

Let's create a simple secret using the LimaCharlie CLI in a terminal. First, create a small file with the secret record in it:

```
$ echo "my-secret-value" > my-secret
```

Next, set this secret in Hive via the LimaCharlie CLI:

```
$ limacharlie hive set secret --key my-secret --data my-secret --data-key secret
```

You should get a confirmation that the secret was created, including metadata of the secret and associated OID:

```
{
    "guid": "3a7a2865-a439-4d1a-8f50-b9a6d833075c",
    "hive": {
        "name": "secret",
        "partition": "8cbe27f4-aaaa-bbbb-cccc-138cd51389cd"
        },
    "name": "my-secret"
}
```

Next, create an output in the web app, using the value `hive://secret/my-secret` as the Secret Key value.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/secret.png)

And that's it! The output should start as expected, however when viewing the output's configuration, the secret should refer to the `hive` ARN, rather than the actual credentials.

---

In LimaCharlie, an Organization ID (OID) is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.