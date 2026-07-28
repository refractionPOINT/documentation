# YARA Manager

The [YARA](https://github.com/Yara-Rules/rules) manager Extension lets you reference external YARA rules, for example rules that you keep in GitHub. You then use these rules in your YARA scans in LimaCharlie.

The YARA manager syncs the rule sources in its configuration every 24 hours. To sync them manually, click the `Manual Sync` button on the extension page.

If you add rule sources and want them available immediately, click the `Manual Sync` button. This starts the first sync of the rules.

A rule source is a direct link (URL) to one YARA rule, or an [ARL](../../../8-reference/authentication-resource-locator.md).

## Option 1: Predefined YARA rules

LimaCharlie supplies a list of repositories with YARA rules in the configuration menu. To use these rules, select "Predefined". A list of LimaCharlie rules and Community rules appears. Select one or more of these repositories. LimaCharlie imports the rules from them and shows them in your YARA rules under Automation → YARA Rules.

![Option 1: Predefined YARA rules LimaCharlie provides a list of YARA rule repositories, available in the configuration me](../../../assets/images/image(322).png)

## Option 2: Publicly available YARA rules

This example sets up a rule with the [Yara-Rules](https://github.com/Yara-Rules/rules) repository.

For an `Email and General Phishing Exploit` rule, use the URL below. It is a link to one YARA rule.

<https://raw.githubusercontent.com/Yara-Rules/rules/master/email/Email_generic_phishing.yar>

To make a rule from more than one YARA rule, use the ARL below. It is a link to a directory of YARA rules.

`[github,Yara-Rules/rules/email]`

1. Give the rule configuration a name.
2. Give the URL or the ARL.
3. Click the Save button.

LimaCharlie creates the new rule source and syncs it to your YARA rules.

## Option 3: Private YARA Repository

To use a YARA rule from a private GitHub repository, you need an [Authentication Resource Locator](../../../8-reference/authentication-resource-locator.md).

**Step 1: Create a token in GitHub.** Do these steps:

1. In GitHub, go to *Settings*.
2. Click *Developer settings* in the left side bar.
3. Click *Personal access token*.
4. Click *Generate new token*.
5. Select the repo permissions.
6. Click *Generate token*.

**Step 2: Connect LimaCharlie to your GitHub repository.** Do these steps:

1. In LimaCharlie, click *Yara Manager* in the left menu.
2. Click *Add New Yara Configuration*.
3. Give your rule a name.
4. Use the token that you generated in one of the formats below, linked to your repository.

`[github,my-org/my-repo-name/path/to/rule.yar,token,bfuihferhf8erh7ubhfey7g3y4bfurbfhrb]`

or

`[github,my-org/my-repo-name/path/to/rules_directory,token,bfuihferhf8erh7ubhfey7g3y4bfurbfhrb]`

LimaCharlie Extensions let users expand and customize their security environments. Extensions integrate third-party tools, automate workflows, and add new capabilities. An organization subscribes to Extensions and gives them specific permissions to interact with its infrastructure. An Extension can be private or public. A private Extension gives tailored use, and a public Extension is shared with the community. This framework supports scale, flexibility, and secure, repeatable deployments.
