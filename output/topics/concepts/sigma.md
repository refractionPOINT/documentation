# Sigma Rules

Sigma is an open source project that provides a generic query language for security rules and known anomalies, including Common Vulnerabilities and Exposures (CVEs). The community actively maintains and updates these rules, responding quickly to emerging threats and interesting anomalies.

LimaCharlie maintains a [backend for Sigma](https://github.com/SigmaHQ/sigma) that converts most Sigma rules into the [Detection & Response rule](/v2/docs/detection-and-response) format. Organizations can subscribe to hundreds of these converted rules for free, with automatic updates every 15 minutes requiring no management overhead.

## Enabling Sigma Rules

To enable Sigma rules in your organization:

1. Navigate to the Add-ons section
2. Search for "Sigma" in the search bar
3. Under the `Organization` dropdown, select the tenant (organization) where you want to apply Sigma rules
4. Click `Subscribe`

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sigma-rules-1.png)

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sigma-rules-2.png)

**Important Notes:**
- Add-ons are applied per-tenant. If you have multiple organizations, you must subscribe each one separately to Sigma
- You can also manage add-ons from the Subscriptions menu under Billing
- Organizations subscribed to the add-on are marked with a green check mark in the `Organization` dropdown

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sigma-rules-3.png)

**Windows Event Log Requirements:**
Some Sigma rules on Windows rely on Windows Event Logs that are not collected by LimaCharlie by default. To leverage these rules, configure automated collection of relevant Windows Event Logs through the Artifact Collection service.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations.

## Converted Rules and Updates

All converted rules are available in the [sigma-limacharlie repository](https://github.com/refractionPOINT/sigma-limacharlie/tree/rules). You can track changes via the [RSS feed](https://github.com/refractionPOINT/sigma-limacharlie/commits/rules.atom).

## Identifying Sigma Rule Detections

To identify detections from Sigma rules:

1. Click on the detection details
2. Look at the `author` field

Detections from managed Sigma rules will have the author listed as starting with `_ext_sigma`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sigma-rules-4(1).png)

## Severity Levels

Sigma rule detections include a level parameter with values provided by the rule author:

* Critical
* High
* Medium
* Low

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sigma-rules-5.png)

## Converting Sigma Rules

LimaCharlie provides a public converter service at `https://sigma.limacharlie.io/` for converting custom Sigma rules or specific rules into the LimaCharlie format. This is useful when you have your own Sigma rules or want to convert/apply specific rules yourself.

### Single Rule Conversion

Convert individual Sigma rules to LimaCharlie format.

**Endpoint:** `https://sigma.limacharlie.io/convert/rule`  
**Method:** `POST`  
**Form Parameters:**
* `rule`: The content of a literal Sigma rule to be converted
* `target`: Optional [target](/v2/docs/detection-on-alternate-targets) within LimaCharlie, one of `edr` (default) or `artifact`

**Example Output:**

```json
{
    "rule": "detect:\n  events:\n  - NEW_PROCESS\n  - EXISTING_PROCESS\n  op: and\n  rules:\n  - op: is windows\n  - op: or\n    rules:\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: domainlist\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: trustdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: dcmodes\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: adinfo\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: ' dclist '\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: computer_pwdnotreqd\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: objectcategory=\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: -subnets -f\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: name=\"Domain Admins\"\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: '-sc u:'\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: domainncs\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: dompol\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: ' oudmp '\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: subnetdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: gpodmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: fspdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: users_noexpire\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: computers_active\nrespond:\n- action: report\n  metadata:\n    author: Janantha Marasinghe (https://github.com/blueteam0ps)\n    description: AdFind continues to be seen across majority of breaches. It is used\n      to domain trust discovery to plan out subsequent steps in the attack chain.\n    falsepositives:\n    - Admin activity\n    level: high\n    references:\n    - https://thedfirreport.com/2020/05/08/adfind-recon/\n    - https://thedfirreport.com/2021/01/11/trickbot-still-alive-and-well/\n    - https://www.microsoft.com/security/blog/2021/01/20/deep-dive-into-the-solorigate-second-stage-activation-from-sunburst-to-teardrop-and-raindrop/\n    tags:\n    - attack.discovery\n    - attack.t1482\n    - attack.t1018\n  name: AdFind Usage Detection\n\n"
}
```

**CURL Example:**

```bash
curl -X POST https://sigma.limacharlie.io/convert/rule \
  -H 'content-type: application/x-www-form-urlencoded' \
  --data-urlencode "rule@my-rule-file.yaml"
```

### Multiple Rules Conversion

Convert multiple Sigma rules from various sources, including GitHub repositories.

**Endpoint:** `https://sigma.limacharlie.io/convert/repo`  
**Method:** `POST`  
**Form Parameters:**
* `repo`: The source where to access the rules to convert, one of:
  * An HTTPS link to a direct resource: `https://corp.com/my-rules.yaml`
  * A GitHub link to a file or repository:
    * `https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/proc_creation_win_ad_find_discovery.yml`
    * `https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation`
  * An [Authenticated Resource Locator](/v2/docs/reference-authentication-resource-locator)
* `target`: Optional [target](/v2/docs/detection-on-alternate-targets) within LimaCharlie, one of `edr` (default) or `artifact`

**Example Output:**

```json
{
    "rules":[
        {
            "file":"https://raw.githubusercontent.com/SigmaHQ/sigma/master/rules/windows/process_creation/proc_creation_win_ad_find_discovery.yml",
            "rule":"detect:\n  events:\n  - NEW_PROCESS\n  - EXISTING_PROCESS\n  op: and\n  rules:\n  - op: is windows\n  - op: or\n    rules:\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: domainlist\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: trustdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: dcmodes\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: adinfo\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: ' dclist '\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: computer_pwdnotreqd\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: objectcategory=\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: -subnets -f\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: name=\"Domain Admins\"\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: '-sc u:'\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: domainncs\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: dompol\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: ' oudmp '\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: subnetdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: gpodmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: fspdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: users_noexpire\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: computers_active\nrespond:\n- action: report\n  metadata:\n    author: Janantha Marasinghe (https://github.com/blueteam0ps)\n    description: AdFind continues to be seen across majority of breaches. It is used\n      to domain trust discovery to plan out subsequent steps in the attack chain.\n    falsepositives:\n    - Admin activity\n    level: high\n    references:\n    - https://thedfirreport.com/2020/05/08/adfind-recon/\n    - https://thedfirreport.com/2021/01/11/trickbot-still-alive-and-well/\n    - https://www.microsoft.com/security/blog/2021/01/20/deep-dive-into-the-solorigate-second-stage-activation-from-sunburst-to-teardrop-and-raindrop/\n    tags:\n    - attack.discovery\n    - attack.t1482\n    - attack.t1018\n  name: AdFind Usage Detection\n\n"
        }
    ]
}
```

**CURL Example:**

```bash
curl -X POST https://sigma.limacharlie.io/convert/repo \
  -d "repo=https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/proc_creation_win_ad_find_discovery.yml"
```