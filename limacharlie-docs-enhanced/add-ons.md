LimaCharlie allows you to extend the capability of the platform via various add-ons. These can be enabled via the [add-ons marketplace](https://app.limacharlie.io/add-ons).

## Types of Add-Ons

We categorize our add-ons into four different categories, depending on the functionality or method with which it augments the LimaCharlie platform.

* `api` add-ons are tightly integrated add-ons that enable LimaCharlie's core features
* `extension` add-ons are cloud services that can perform jobs on behalf of or add new capabilities to an Organization.
* `lookup` add-ons maintain reference to dynamic lists for use within D&R rules.
* `ruleset` add-ons provide managed sets of rules to use within D&R rules.

## Subscribing to Add-Ons

Add-ons can be found and added to organizations through the [add-ons marketplace](https://app.limacharlie.io/add-ons) or by searching from within the Add-ons view in an organization (see below). The description of the add-on may include usage information about how to use it once it's installed.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/addons.png)

The following add-ons enable additional functionality in the web application:

* `atomic-red-team` - scan Windows sensors right from their `Overview` page
* `exfil` - enables `Exfil Control` to configure which events should be collected per platform
* `infrastructure-service` - enable `Templates` in the UI to manage org config in `yaml`
* `insight` - enables retention & browsing events and detections via `Timeline` and `Detections`
* `logging` - enables `Artifact Collection` to configure which paths to collect from
* `replay` - adds a component next to  rules for testing them against known / historical events
* `responder` - sweep sensors right from their `Overview` page to find preliminary IoCs
* `yara` - enables `YARA Scanners` view to pull in sources of YARA rules and automate scans with them

## Creating Add-ons

Users can create their own add-ons and optionally share them in the marketplace. Add-ons are your property, but may be evaluated and approved / dismissed due to quality or performance concerns. If you have questions, [contact us](https://limacharlie.io/contact).

Got an idea?

Are you interested in creating an add-on or developing another project for LimaCharlie? Check out our [Developer Grant Program](/v2/docs/developer-grant-program).

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.
