[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v2

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Access and Permissions

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Access and Permissions

* Updated on 05 Oct 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

LimaCharlie is [multi-tenant](https://en.wikipedia.org/wiki/Multitenancy); tenants are called Organizations and both data and billing are tied to the Organization.

Users, API Keys and Groups exist as ways of managing access and permissions to Organizations.

## Users

Users are operators or administrators. Permissions are applied directly to the User account and allow for fine-grained access control.

One user can be a member of multiple organizations.

## API Keys

An API Key represents a set of permissions and are used to interact with LimaCharlie.

Full documentation on API Keys can be [here](/v2/docs/api-keys).

## Groups

Groups provides a way for managing permissions for multiple Users across multiple Organizations.

Groups each have a set of permissions associated with them that are applied (additively) to all Users in the group, for all Organizations in the group. Groups drastically reduce the admin overhead in managing fine-grained access control.

More information [here](/v2/docs/user-access).

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### What's Next

* [API Keys](/docs/api-keys)

Table of contents

+ [Users](#users)
+ [API Keys](#api-keys)
+ [Groups](#groups)

Tags

* [platform](/docs/en/tags/platform)
