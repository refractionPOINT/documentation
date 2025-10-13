LimaCharlie's Cloud CLI Extension (`ext-cloud-cli`) allows you to trigger actions against CLI or API endpoints for third-party products. This extension facilitates bi-directional communication between LimaCharlie and nearly any telemetry source. Actions can be triggered from the Cloud CLI UI or automated via  rules.

For a list of platforms supported by this extension, see the nested items on the left-side navigation.

## Usage

The Cloud CLI extension is enabled via the [Add-Ons Marketplace](https://app.limacharlie.io/add-ons/category/featured). When enabled, the Cloud CLI extension provides the following UI, available via the Extensions menu in LimaCharlie.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/ext-cloud-cli.png)

From this UI, you can build and execute commands against the CLI or API endpoints of the chosen product.

Cloud CLI commands can also be executed via D&R rules and the use of the `extension request` action.

**Example 1:** Stop EC2 instances based on an `instance_id` parameter found in [AWS telemetry](/v2/docs/adapter-types-aws-cloudtrail).

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    tool: '{{ "aws" }}'
    command_tokens:
      - ec2
      - stop-instances
      - '--instance-ids'
      - '{{ .event.instance_id  }}'
      - '--region'
      - us-east-1
    credentials: '{{ "hive://secret/secret-name" }}'
```

**Example 2:** Enumerate a list of VMs from an Azure tenant.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    tool: '{{ "az" }}'
    command_line: '{{ "vm list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

### Credentials

You must set up credentials in the respective third-party tools or platforms prior to utilizing this extension. Once procured, credentials can be stored in the [Secrets config hive](/v2/docs/config-hive-secrets) or provided ad-hoc to the extension in the UI. We recommend storing credentials in the Secrets config hive if you plan to make repetitive calls with this extension.

Where available, details for procuring third-party credentials are provided in their respective sub-pages.

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.
