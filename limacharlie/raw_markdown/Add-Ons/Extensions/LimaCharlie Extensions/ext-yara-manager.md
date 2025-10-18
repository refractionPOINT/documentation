---
title: YARA Manager
slug: ext-yara-manager
breadcrumb: Add-Ons > Extensions > LimaCharlie Extensions
source: https://docs.limacharlie.io/docs/ext-yara-manager
articleId: 939294e5-ea43-4714-b55f-5dd2a17eeb01
---

* * *

YARA Manager

  *  __31 Jul 2025
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# YARA Manager

  *  __Updated on 31 Jul 2025
  *  __ 2 Minutes to read 



  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




* * *

Article summary

 __

Did you find this summary helpful? __ __ __ __

__

Thank you for your feedback!

The [YARA](https://github.com/Yara-Rules/rules) manager Extension allows you to reference external YARA rules (rules maintained in GitHub, for example) to use in your YARA scans within LimaCharlie.

YARA rule sources defined in the YARA manager configuration will be synced every 24 hours, and can be manually synced by clicking the `Manual Sync` button on the extension page.

If you add rule sources and want them to become available immediately, you will need to click the `Manual Sync` button to trigger the initial sync of the rules.

Rule sources can be either direct links (URLs) to a given YARA rule or [ARLs](/v2/docs/reference-authentication-resource-locator).

### Option 1: Predefined YARA rules

LimaCharlie provides a list of YARA rule repositories, available in the configuration menu. To leverage these rules select “Predefined” and a list of LimaCharlie and Community rules will populate. By selecting one or more of these repositories, the respective rules will be automatically imported and will appear in your YARA rules under Automation → YARA Rules.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image\(322\).png)

### Option 2: Publicly available YARA rules

An example of setting up a rule using this repo: [Yara-Rules](https://github.com/Yara-Rules/rules)

For an `Email and General Phishing Exploit` rule we could use the following URL, which is a link to a single YARA rule.

<https://raw.githubusercontent.com/Yara-Rules/rules/master/email/Email_generic_phishing.yar>

For creating a rule out of multiple YARA rules, we could use the following ARL, which is a link to a directory of YARA rules.

`[github,Yara-Rules/rules/email]`

Giving the rule configuration a name, the URL or ARL, and clicking the Save button will create the new rule source to sync to your YARA rules.

### Option 3: Private YARA Repository

To use a YARA rule from a private Gihub repository you will need to make use of an [Authentication Resource Locator](/v2/docs/reference-authentication-resource-locator).

**Step 1: Create a token in GitHub**  
In GitHub go to _Settings_ and click _Developer settings_ in the left hand side bar.

Next click _Personal access token_ followed by _Generate new token_. Select repo permissions and finally _Generate token_.

**Step 2: Connect LimaCharlie to your GitHub repository**  
Inside of LimaCharlie, click on _Yara Manager_ in the left hand menu. Then click _Add New Yara Configuration_.

Give your rule a name and then use the token you generated with the following format linked to your repo.

`[github,my-org/my-repo-name/path/to/rule.yar,token,bfuihferhf8erh7ubhfey7g3y4bfurbfhrb]`

or

`[github,my-org/my-repo-name/path/to/rules_directory,token,bfuihferhf8erh7ubhfey7g3y4bfurbfhrb]`

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

* * *

Was this article helpful?

__Yes __No

 __

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change  


Please enter a valid email

Cancel

* * *

###### Related articles

  * [ Config Hive: Yara ](/docs/config-hive-yara)
  * [ Detection and Response Examples ](/docs/detection-and-response-examples)
  * [ BinLib ](/docs/binlib)
  * [ Detection and Response ](/docs/detection-and-response)
  * [ Reference: Endpoint Agent Commands ](/docs/reference-endpoint-agent-commands)



* * *

###### What's Next

  * [ AI Agent Engine [LABS] ](/docs/ai-agent-engine) __



Table of contents




Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ dfir ](/docs/en/tags/dfir)
  * [ extensions ](/docs/en/tags/extensions)


