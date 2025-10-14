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

Single Sign-On

* 10 Oct 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Single Sign-On

* Updated on 10 Oct 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Single sign-on (SSO) is available at no extra cost for customers that leverage LimaCharlie's custom branded offering. If this applies to your Organization, and if you are interested in using the SSO, please submit a [Custom Branding / SSO Request](https://limacharlie.io/custom-branding).

If your organization does not currently have a custom branded site with LimaCharlie, you can learn about the requirements, costs & get started here.

Strict SSO Enforcement

LimaCharlie offers the ability to implement strict SSO enforcement. This means that  SSO can be configured as the only authentication option.

With this capability, you may say that any user with your email domain @example.com must authenticate via Google. This way you can disable the login + password, GitHub, and Microsoft login options for users with your email domain (@example.com) - regardless if they are logging in via your custom branded site, or via app.limacharlie.io

## How It Works

LimaCharlie's single sign-on functionality lets companies add their own SSO option that goes through their authentication server instead of through Google or something else. Identity Platform acts as the coordinator here. After configuring new Providers in Identity Platform, the app only needs to specify a provider ID, and then Identity Platform will handle talking to the company's auth server.

## User Experience

The high-level user experience is as follows:

* For organizations that choose to use SSO, the SSO will be enforced. Users going to custom branded versions of the LimaCharlie site will be presented with only the option to login through SSO, if their domain has the SSO configuration.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sso-1.png)

* The same user going to the non-branded site would still be presented with all other authentication options. However, a user would only be able to use the authentification option approved for their domain.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sso-2.png)

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

###### Related articles

* [User Access](/docs/user-access)

---

###### What's Next

* [Reference: Permissions](/docs/reference-permissions)

Table of contents

+ [How It Works](#how-it-works)
+ [User Experience](#user-experience)

Tags

* [platform](/docs/en/tags/platform)
