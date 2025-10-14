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

Microsoft 365

* 10 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Microsoft 365

* Updated on 10 Oct 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

The CLI **for Microsoft 365** is a tool created to help manage Microsoft 365 tenant(s) and SharePoint framework projects. With this component of the Cloud CLI Extension, you can interact with a Microsoft 365 tenant(s) directly from LimaCharlie.

This extension makes use of the PnP Microsoft 365 CLI, which can be found [here](https://github.com/pnp/cli-microsoft365).

## Example

The following example disables the user account with the provided user ID.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "m365" }}'
    command_tokens:
      - entra
      - user
      - set
      - '--id'
      - '{{ .event.user_id  }}'
      - '--accountEnabled'
      - false
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

* Per the Microsoft 365 CLI documentation, there are multiple login or authentication mechanisms available. The current LimaCharlie implementation utilizes a client secret for authentication. More information on provisioning client secrets can be found [here](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app).
* Upon invocation, LimaCharlie will first run the `m365 login` command with the credentials provided.
* Create a secret in the secrets manager in the following format:

  ```
  appID/clientSecret/tenantID
  ```

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

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

###### Related articles

* [Microsoft 365](/docs/adapter-types-microsoft-365)

---

###### What's Next

* [Okta](/docs/ext-cloud-cli-okta)

Table of contents

+ [Example](#example)
+ [Credentials](#credentials)

Tags

* [add-ons](/docs/en/tags/add-ons)
* [azure](/docs/en/tags/azure)
* [extensions](/docs/en/tags/extensions)
* [m365](/docs/en/tags/m365)
