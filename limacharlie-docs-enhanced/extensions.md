LimaCharlie Extensions provide a robust framework for enhancing and customizing the LimaCharlie Cloud's capabilities, enabling seamless integration with third-party tools, services, and custom logic. Extensions serve as modular components that expand LimaCharlie’s native functionality, allowing organizations to tailor their security environments to meet specific needs without being constrained by built-in features.

### Overview of Extensions

Extensions are defined at the global level across all LimaCharlie datacenters. This means that once an Extension is created, it is available for use in any Organization, provided that organization subscribes to it. Once subscribed, Extensions can interact with various components within the subscribing organization, whether through automated workflows or user-driven actions.

### Subscription and Permissions

To use an Extension, an organization must first subscribe to it. Upon subscription, the Extension is granted a set of predefined permissions that govern what actions it can perform within the organization. These permissions ensure that each Extension has controlled access to sensitive areas of the organization’s security infrastructure.

Some Extensions are also capable of "impersonating" the user or automation component that triggered them, which allows the Extension to perform actions as if it were the user itself. This feature is particularly useful for Extensions that need to execute actions in response to detection and response rules or other automated triggers, without needing separate user credentials.

### Types of Extensions: Public, Private, Labs

* **Private Extensions**: These are created by individual users (known as Owners) and are restricted for use only within the organizations where the Owner holds specific permissions, such as `billing.ctrl` and `user.ctrl`. Private Extensions are ideal for internal integrations or for extending capabilities within a limited scope, such as an organization’s specific infrastructure or toolset.
* **Public Extensions**: Public Extensions are available for subscription by any organization across the LimaCharlie platform. To make an Extension public, users first create it as private and, once fully developed and tested, they can submit it to LimaCharlie for approval. Once approved, the Extension becomes available for any organization to subscribe to. This process ensures that public Extensions are stable, secure, and beneficial to the broader community.
* **LimaCharlie Labs:** Labs extensions are capabilities that LimaCharlie is making available on the SecOps Cloud Platform in an preview state.

  > **Note:** Extensions with this label are expected to grow and change. The extension has been tested and is ready to be used by users, but some things such as a polished user interface may be missing or in prototype form.
  >
  > **Your feedback is greatly appreciated!**

  Here is the list of current capabilities under LimaCharlie Labs:

  + [Playbooks extension](/v2/docs/playbook)
  + [AI Agent Engine](/v2/docs/ai-agent-engine)

### Use Cases for Extensions

Extensions can be used for a wide range of purposes, including but not limited to:

* **Third-party Integrations**: Organizations can use Extensions to integrate LimaCharlie with external systems like SIEMs, threat intelligence platforms, or incident response tools. This enables seamless data flow between LimaCharlie and other components of the security stack.
* **Custom Automation**: Extensions can be designed to handle organization-specific automation tasks, such as alerting, incident response workflows, or data enrichment based on internal processes or external APIs.
* **Augmenting Detection and Response**: Some Extensions provide enhanced detection and response capabilities, offering additional insights or actions that can be executed in response to specific triggers or threats. These could range from triggering a custom script when a detection occurs to pulling data from external systems to enrich an alert.

### Developing Extensions

Any user with the necessary permissions can develop their own Extension, allowing for high levels of customization and control. Private Extensions offer flexibility for organizations looking to develop internal tools or workflows without exposing them to the public.

Any User (called Owners) can create an Extension, but those can only be "private", meaning only Organizations where the Owner has the `billing.ctrl` and `user.ctrl` permissions can subscribe to the Extension. To make an Extension "public" (where anyone can subscribe to it), first create your private Extension and once ready, reach out to LimaCharlie `answers@limacharlie.io`.

The process of developing an Extension is relatively straightforward:

1. **Creation**: The Owner of the Extension defines its purpose, functionality, and permissions. These permissions dictate what resources the Extension can interact with and what actions it can perform.
2. **Testing and Deployment**: Private Extensions can be deployed within the Owner’s organization and tested before being considered for broader release. This allows organizations to ensure that the Extension works as expected without impacting production environments.
3. **Public Release**: When an Extension is ready for broader use, the Owner can request that LimaCharlie make the Extension public. LimaCharlie reviews the Extension to ensure it meets security and functionality standards before it’s made available to the community.

For more information, see [Building Extensions](/v2/docs/building-extensions).

### Security Considerations

Extensions operate with a defined set of permissions to prevent misuse or overreach within an organization’s infrastructure. By allowing granular control over what an Extension can do, LimaCharlie ensures that even third-party or public Extensions operate within the boundaries of an organization's security policies.

Furthermore, because Extensions can impersonate users to perform actions, organizations must carefully manage which Extensions they subscribe to and ensure they align with their security posture. Public Extensions go through an additional vetting process by LimaCharlie, offering another layer of trust for organizations that want to extend their capabilities through third-party tools.

### Scaling and Flexibility

As organizations grow and their security needs evolve, Extensions offer a flexible, scalable solution to integrate new tools, automate complex workflows, or enhance existing functionality. Organizations can subscribe to the Extensions that align with their specific use cases, effectively creating a customized security environment that adapts to both current and future challenges.

By leveraging LimaCharlie’s Extension framework, organizations can expand their security capabilities without needing to constantly switch platforms or build integrations from scratch. Whether it's to incorporate new detection rules, automate response actions, or add support for a new tool, Extensions enable organizations to stay agile in an ever-changing security landscape.

In summary, LimaCharlie Extensions provide a powerful way for organizations to customize and scale their security infrastructure, offering a balance of flexibility, security, and control. With the ability to create both private and public Extensions, users can tailor LimaCharlie to their specific needs while contributing to the broader security community when ready.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.
