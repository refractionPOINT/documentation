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

1Password

* 05 Oct 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# 1Password

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

The 1Password CLI brings 1Password to the terminal, allowing you to interact with a 1Password instance from LimaCharlie.

This Extension makes use of 1Password's native CLI, which can be found [here](https://developer.1password.com/docs/cli).

1Password Account Types

Please note that some 1Password functionality is limited to 1Password Business. Please validate you have the correct type of account(s) to ensure that commands run.

## Example

Returns a list of all items the account has read access to by default.

```
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "op" }}'
    command_line: '{{ "item list" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To utilize 1Password's automated CLI capabilities, you will need to create and utilize a Service Account. More information can be found [here](https://developer.1password.com/docs/service-accounts/get-started/).

* Create a secret in the secrets manager in the following format:

```
serviceAccountToken
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

* [1Password](/docs/1password)

---

###### What's Next

* [AWS](/docs/ext-cloud-cli-aws)

Table of contents

+ [Example](#example)
+ [Credentials](#credentials)

Tags

* [add-ons](/docs/en/tags/add-ons)
* [extensions](/docs/en/tags/extensions)
