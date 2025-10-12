# Extensions
LimaCharlie Extensions provide a robust framework for enhancing and customizing the LimaCharlie Cloud's capabilities, enabling seamless integration with third-party tools, services, and custom logic. Extensions serve as modular components that expand LimaCharlie’s native functionality, allowing organizations to tailor their security environments to meet specific needs without being constrained by built-in features.

## Overview of Extensions

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
#### Related articles

* [LimaCharlie Extensions](/docs/lc-extensions)
* [Using Extensions](/docs/using-extensions)
* [Third-Party Extensions](/docs/third-party-extensions)

---

##### What's Next

* [Artifact](/docs/ext-artifact)

Table of contents

Tags

* [add-ons](/docs/en/tags/add-ons)
* [extensions](/docs/en/tags/extensions)