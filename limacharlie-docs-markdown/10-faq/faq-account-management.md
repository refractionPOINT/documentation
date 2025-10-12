# FAQ - Account Management
## How Can I Create More Than Two Organizations?

By default, LimaCharlie has a limit of two organizations. If you need to create more organizations, please reach out to the support team and we will change this limit.

## How Do I Delete an Organization?

Please navigate to the bottom of the Billing & Usage section of the organization you want to delete, and click Delete Organization button. Note that this action is final and cannot be undone.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/account-3.png)

## Is There a Way to Wipe an Organization?

You can wipe the data retention by disabling the `Insight` add on on the marketplace and re-enabling it again. Please note that unsubscribing from `Insight` will delete all telemetry stored for a selected organization, and this action cannot be undone.

To wipe the configuration, you can use Templates / Infrastructure as Code functionality with the `is_force` flag to remove everything. To learn more about the infrastructure as code, visit [Infrastructure Extension](/v2/docs/ext-infrastructure).

## Can I Transfer Ownership of an Organization?

You can transfer ownership of an organization to any other entity. The request needs to be initiated by the current owner (billing or legal contact) of the organization. To do so, contact support@limacharlie.io.

## I Created an Account and Have Been Given Access, but I Do Not Seem to Have Access to Other Organizations.

With LimaCharlie's granular role-based access control you can be granted access in one of two ways:

* On a per-organization basis
* To a set of organizations using [Organization Groups](/v2/docs/user-access)

You'll want to ask the person who granted access if they added you to the individual organizations, or if they'd set up an organization group.  Either method works, but they'll have to ensure that either you're added to each organization individually, or that they set up a group.

## How Can I Update My Time Zone?

All dates and times displayed in the web app follow the user preferred time zone.

To set your time zone, navigate to the settings icon in the right hand corner and select `Manage User Settings`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/account-1.png)

You can set your preferred time zone under `Display` section of the `User Settings`; all changes are saved automatically.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/account-2.png)

## How Can I Unsubscribe/Cancel/Delete My Limacharlie Account?

You can unsubscribe / cancel your subscription from app.limacharlie.io by logging in and going to the Billing & Usage under the Billing section. Click the Delete Organization button at the bottom of the page and follow the instructions on screen.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/account-3.png)

## Why Didn't I Receive My Account Activation Email?

Account activation emails are sent when you sign up for a new LimaCharlie account. If you do not see the activation email in your inbox, it can typically be found in a spam / junk folder. If you're a user of Microsoft Office 365, or similar service that has server-side filtering, you may wish to check your online Quarantine (or equivalent). See the [Microsoft instructions](https://docs.microsoft.com/en-us/microsoft-365/security/office-365-security/quarantine-email-messages?view=o365-worldwide) for details.

Please reach out to our support team and we can verify if a successful delivery response message was received from your mail server.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

---

### What's Next

* [FAQ - Billing](/docs/faq-billing)

Table of contents

+ [How Can I Create More Than Two Organizations?](#how-can-i-create-more-than-two-organizations-)
+ [How Do I Delete an {{glossary.Organization}}?](#how-do-i-delete-an-{{glossary-organization}}-)
+ [Is There a Way to Wipe an Organization?](#is-there-a-way-to-wipe-an-organization-)
+ [Can I Transfer Ownership of an Organization?](#can-i-transfer-ownership-of-an-organization-)
+ [I Created an Account and Have Been Given Access, but I Do Not Seem to Have Access to Other Organizations.](#i-created-an-account-and-have-been-given-access-but-i-do-not-seem-to-have-access-to-other-organizations-)
+ [How Can I Update My Time Zone?](#how-can-i-update-my-time-zone-)
+ [How Can I Unsubscribe/Cancel/Delete My Limacharlie Account?](#how-can-i-unsubscribe-cancel-delete-my-limacharlie-account-)
+ [Why Didn't I Receive My Account Activation Email?](#why-didn-t-i-receive-my-account-activation-email-)

Tags

* [faq](/docs/en/tags/faq)