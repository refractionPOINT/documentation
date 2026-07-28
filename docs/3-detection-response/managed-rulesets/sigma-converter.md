# Sigma Converter

LimaCharlie contributes to the [Sigma Project](https://github.com/SigmaHQ/sigma) and maintains the LimaCharlie Backend for Sigma. The backend converts most Sigma rules to the [Detection & Response rule](../examples.md) format.

A LimaCharlie Service applies [many of those converted rules](https://github.com/refractionPOINT/sigma-limacharlie/tree/rules) to an Organization with one click.

If you have your own Sigma rules, or if you want to convert and apply specific rules yourself, use the Sigma Converter service that is described below.

## Converter Service

The Converter service converts one or more Sigma rules into the LimaCharlie rule format. It uses the HTTPS endpoints below, which are available at <https://sigma.limacharlie.io/>:

### Single Rule

Endpoint: `https://sigma.limacharlie.io/convert/rule`
 Verb: `POST`
 Form Parameters:

- `rule`: the content of a literal Sigma rule to convert.
- `target`: optional [target](../alternate-targets.md) within LimaCharlie, one of `edr` (default) or `artifact`.
   Output Example:

```json
{
    "rule": "detect:\n  events:\n  - NEW_PROCESS\n  - EXISTING_PROCESS\n  op: and\n  rules:\n  - op: is windows\n  - op: or\n    rules:\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: domainlist\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: trustdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: dcmodes\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: adinfo\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: ' dclist '\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: computer_pwdnotreqd\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: objectcategory=\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: -subnets -f\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: name=\"Domain Admins\"\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: '-sc u:'\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: domainncs\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: dompol\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: ' oudmp '\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: subnetdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: gpodmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: fspdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: users_noexpire\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: computers_active\nrespond:\n- action: report\n  metadata:\n    author: Janantha Marasinghe (https://github.com/blueteam0ps)\n    description: AdFind continues to be seen across majority of breaches. It is used\n      to domain trust discovery to plan out subsequent steps in the attack chain.\n    falsepositives:\n    - Admin activity\n    level: high\n    references:\n    - https://thedfirreport.com/2020/05/08/adfind-recon/\n    - https://thedfirreport.com/2021/01/11/trickbot-still-alive-and-well/\n    - https://www.microsoft.com/security/blog/2021/01/20/deep-dive-into-the-solorigate-second-stage-activation-from-sunburst-to-teardrop-and-raindrop/\n    tags:\n    - attack.discovery\n    - attack.t1482\n    - attack.t1018\n  name: AdFind Usage Detection\n\n"
}
```

CURL Example:

```python
curl -X POST  https://sigma.limacharlie.io/convert/rule -H 'content-type: application/x-www-form-urlencoded' --data-urlencode "rule@my-rule-file.yaml"
```

### Multiple Rules

Endpoint: `https://sigma.limacharlie.io/convert/repo`
 Verb: `POST`
 Form Parameters:

- `repo`: the source of the rules to convert, one of:

  - An HTTPS link to a direct resource like: `https://corp.com/my-rules.yaml`
  - A GitHub link to a file or repo like:

    - `https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/proc_creation_win_ad_find_discovery.yml`
    - `https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation`
  - An [Authenticated Resource Locator](../../8-reference/authentication-resource-locator.md)
- `target`: optional [target](../alternate-targets.md) within LimaCharlie, one of `edr` (default) or `artifact`.

Output Example:

```json
{
    "rules":[
        {
            "file":"https://raw.githubusercontent.com/SigmaHQ/sigma/master/rules/windows/process_creation/proc_creation_win_ad_find_discovery.yml","rule":"detect:\n  events:\n  - NEW_PROCESS\n  - EXISTING_PROCESS\n  op: and\n  rules:\n  - op: is windows\n  - op: or\n    rules:\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: domainlist\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: trustdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: dcmodes\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: adinfo\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: ' dclist '\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: computer_pwdnotreqd\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: objectcategory=\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: -subnets -f\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: name=\"Domain Admins\"\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: '-sc u:'\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: domainncs\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: dompol\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: ' oudmp '\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: subnetdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: gpodmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: fspdmp\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: users_noexpire\n    - case sensitive: false\n      op: contains\n      path: event/COMMAND_LINE\n      value: computers_active\nrespond:\n- action: report\n  metadata:\n    author: Janantha Marasinghe (https://github.com/blueteam0ps)\n    description: AdFind continues to be seen across majority of breaches. It is used\n      to domain trust discovery to plan out subsequent steps in the attack chain.\n    falsepositives:\n    - Admin activity\n    level: high\n    references:\n    - https://thedfirreport.com/2020/05/08/adfind-recon/\n    - https://thedfirreport.com/2021/01/11/trickbot-still-alive-and-well/\n    - https://www.microsoft.com/security/blog/2021/01/20/deep-dive-into-the-solorigate-second-stage-activation-from-sunburst-to-teardrop-and-raindrop/\n    tags:\n    - attack.discovery\n    - attack.t1482\n    - attack.t1018\n  name: AdFind Usage Detection\n\n"
        },
        ...
    ]
}
```

CURL Example:

```python
curl -X POST  https://sigma.limacharlie.io/convert/repo -d "repo=https://github.com/SigmaHQ/sigma/blob/master/rules/windows/process_creation/proc_creation_win_ad_find_discovery.yml"
```
