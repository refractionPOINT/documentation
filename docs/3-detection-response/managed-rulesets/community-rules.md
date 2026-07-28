# Community Rules

The Community Rules feature uses AI to convert third-party rules into LimaCharlie syntax. Browse thousands of community rules and select one as a start. Convert it to LimaCharlie syntax with one click, then change it for your needs.

## Accessing the Community Rules

To access the Community Rules:

1. Log into LimaCharlie
2. Select an Organization
3. Click the Automation drop down on the left panel
4. Select Rules
5. Look in the upper right corner of the D&R Rules page for the Add Rule button
6. Click the Add Rule button
7. Look in the upper right corner of the rule creation page for the Community Library button
8. Click the Community Library button

The Community Rules search page opens and gives access to thousands of third-party detection rules. The library currently contains detection rules written by [Anvilogic](https://github.com/anvilogic-forge/armory/blob/main/detections/cloud/aws/aws_disableawsserviceaccess/aws_disableawsserviceaccess-splunk-awscloudtrail.yml), [Sigma](https://github.com/SigmaHQ/sigma/blob/master/rules/network/zeek/zeek_http_susp_file_ext_from_susp_tld.yml), [Panther](https://github.com/panther-labs/panther-analysis/blob/develop/rules/gsuite_activityevent_rules/google_workspace_many_docs_downloaded.yml), and [Okta](https://github.com/okta/customer-detections).

> You can search for rules by CVE number, keyword, or pre-defined descriptors (Tags). Searchable tags include attack techniques, MITRE ATT&CK id codes, and other key rule identifiers.

![Community Rules Search Interface](../../assets/images/image(337).png)

## Loading a Community Rule

When you find the rule that you want to use, click "Load Rule" to import it into the organization. The AI engine creates the rule with verified LimaCharlie syntax.

> This process can take a few seconds.

When the rule is ready, LimaCharlie returns you to the Add Rule page. The Detect and Response sections of the rule contain LimaCharlie logic with explanatory comments. You can then manage this rule as you manage any other D&R rule.

## Digging Deeper

These rules are the property of third parties. The Community Rules search page gives more information about their licensing and source code. To see these details, click a rule.

The example below shows the result when you click the Anvilogic Potential CVE-2021-44228 - Log4Shell rule.

Below the rule name are the options to load the rule, check its source code, and read more licensing information. A reference section in the bottom left corner of the window gives links that relate to the rule.

![Rule Details Example](https://lh7-rt.googleusercontent.com/docsz/AD_4nXf3SZQZu4j4kEp2Y0wpnoeHA0t_XaR5VqaoB9SupPHl0t91e-12QhMj0epDi742peW0gpu8e44HhJ4lDN1esspiMRUfpFr3W2aNiQcIeff2HhNCxmgp1h3oLqphpqJ8AohoDDxFdA?key=7BgiNipN3DxRQXGQyEk06w)
