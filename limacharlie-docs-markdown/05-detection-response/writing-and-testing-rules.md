# Writing and Testing Rules
Detection & Response () Rules are similar to Google Cloud Functions or AWS Lambda.
They allow you to push D&R rules to the LimaCharlie cloud where the rules will be applied
in real-time to data coming from the sensors.

D&R rules can also be applied to [Artifact Collection](/v2/docs/artifacts), but for now we will focus
on the simple case where it is applied to Sensor events.

For a full list of all rule operators and detailed documentation see the [Detection and Response](/v2/docs/detection-and-response) section.

## Life of a Rule

D&R rules are generally applied on a per-event basis. When the rule is applied, the "detection"
component of the rule is processed to determine if it matches. If there is a match, the "response"
component is applied.

The detection is processed one step at a time, starting at the root of the detection. If the
root matches, the rule is considered to be matching.

The detection component is composed of "nodes", where each node has an operator describing the
logical evaluation. Most operators are simple, like `is`, `starts with` etc. These simple nodes
can be combined with Boolean (true/false) logic using the `and` and `or` operators, which
themselves reference a series of nodes. The `and` node matches if all the sub-nodes match, while
the `or` node matches if any one of the sub-nodes matches.

When evaluating an `or`, as soon as the first matching sub-node is found, the rest of the sub-nodes
are skipped since they will have no impact on the final matching state of the "or". Similarly, failure of a sub-node in an "and" node will immediately terminate its evaluation.

If the "detection" component is matched, then the "response" evaluation begins.

The "response" component is a list of actions that should be taken. When an action refers to a
sensor, that sensor is assumed to be the sensor the event being evaluated is coming from.

The best general strategy for D&R rules is to put the parts of the rule most likely
to eliminate the event at the beginning of the rule, so that LC may move on to the next event
as quickly as possible.

## Introduction

### Goal

The goal of is code lab will be to create a D&R rule to detect the MITRE ATT&CK framework
[Control Panel Items](https://attack.mitre.org/techniques/T1196/) execution.

### Services Used

This code lab will use the Replay service to validate and test the rule prior to pushing it to production.

## Setup and Requirements

This code lab assumes you have access to a Linux host (MacOS terminal with `brew`). This
code lab also assumes you have "owner" access to an LC Organization. If you don't have
one already, create one, this code lab is compatible with the free tier that comes with
all organizations.

### Install CLI

Interacting with LC can always be done via the [web app](https://app.limacharlie.io) but
day to day operations and automation can be done via the Command Line Interface (CLI). This
will make following this code lab easier.

Install the CLI: `pip install limacharlie --user`. If you don't have `pip` installed, install
it, the exact instructions will depend on your Linux distribution.

### Create REST API Key

We need to create an API key we can use in the CLI to authenticate with LC. To do so, go
to the REST API section of the web app.

1. In the REST API section, click the "+" button in the top right of the page.
2. Give your key a name.
3. For simplicity, click the "Select All" button to enable all permissions. Obviously this would not be a recommended in a production environment,
4. Click the copy-to-clipboard button for the new key and take note of it (pasting it in a temporary text note for example).
5. Back on the REST API page, copy the "Organization ID" at the top of the page and keep note of it like the API key in the previous step.

The Organization ID (OID) identifies uniquely your organization while the API key grants specific permissions to this organization.

### Login to the CLI

Back in your terminal, log in with your credentials: `limacharlie login`.

1. When asked for the Organization ID, paste your OID from the previous step.
2. When asked for a name for this access, you can leave it blank to set the default credentials.
3. When asked for the secret API key, enter the key you got from the previous step.

You're done! If you issue a `limacharlie dr list` you should not get any errors.

## Draft Rule

To draft our rule, open your preferred text editor and save the rule to a file, we'll call it `T1196.rule`.
The format of a rule is [YAML](https://en.wikipedia.org/wiki/YAML), if you are unfamiliar with it, there is benefit to spending a few minutes getting familiar. It won't take long as it is not overly complex.

For our rules based on the [T1196](https://attack.mitre.org/techniques/T1196/) technique, we need
to apply the following constraints:

1. It only applies to Windows.
2. The event is a module (DLL for example on Windows) loading.
3. The module loading ends with `.cpl` (control panel extension).
4. The module is loading from outside of the `C:\windows\` directory.

LC supports a lot of different event types, this means that the first thing we should strive to
do to try to make the rule fail as quickly as possible is to filter all events we don't care about.

In this case, we only care about [CODE\_IDENTITY](/v2/docs/reference-edr-events#codeidentity) events. We also know that
our rule will use more than one criteria, and those criteria will be AND-ed together because we only
want to match when they all match.

```
op: and
event: CODE_IDENTITY
rules:
  -
```

The above sets up the criteria #2 preceding it, with the AND-ing that will follow. Since the AND is at the
top of our rule, and it has an `event:` clause, it will ensure that any event processed by this rule
but is NOT a `CODE_IDENTITY` event will be skipped over right away.

Next, we should look at the other criteria, and add them to the `rules:` list, which are all the sub-nodes
that will be AND-ed together.

Criteria #1 was to limit to Windows, that's easy:

```
op: and
event: CODE_IDENTITY
rules:
  - op: is windows
  -
```

Next up is criteria #3 and #4. Both of those can be determined using the `FILE_PATH` component of the
`CODE_IDENTITY` event. If you are unure what those events look like, the best way to get a positive confirmation
of the structure is simply to open the Historic View, start a new process on that specific host and look for
the relevant event. If we were to do this on a Windows host, we'd get an example like this one:

```json
{
    "routing": {
        "parent": "...",
        "this": "...",
        "hostname": "WIN-...",
        "event_type": "CODE_IDENTITY",
        "event_time": 1567438408423,
        "ext_ip": "XXX.176.XX.148",
        "event_id": "11111111-1111-1111-1111-111111111111",
        "oid": "11111111-1111-1111-1111-111111111111",
        "plat": 268435456,
        "iid": "11111111-1111-1111-1111-111111111111",
        "sid": "11111111-1111-1111-1111-111111111111",
        "int_ip": "172.XX.223.XXX",
        "arch": 2,
        "tags": [
            "..."
        ],
        "moduleid": 2
    },
    "ts": "2019-09-02 15:33:28",
    "event": {
        "HASH_MD5": "7812c2c0a46d1f0a1cf8f2b23cd67341",
        "HASH": "d1d59eefe1aeea20d25a848c2c4ee4ffa93becaa3089745253f9131aedc48515",
        "ERROR": 0,
        "FILE_INFO": "10.0.17134.1",
        "HASH_SHA1": "000067ac70f0e38f46ce7f93923c6f5f06ecef7b",
        "SIGNATURE": {
            "FILE_CERT_IS_VERIFIED_LOCAL": 1,
            "CERT_SUBJECT": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Windows",
            "FILE_PATH": "C:\\Windows\\System32\\setupcln.dll",
            "FILE_IS_SIGNED": 1,
            "CERT_ISSUER": "C=US, S=Washington, L=Redmond, O=Microsoft Corporation, CN=Microsoft Windows Production PCA 2011"
        },
        "FILE_PATH": "C:\\Windows\\System32\\setupcln.dll"
    }
}
```

This means what we want is to apply rules to the `event/FILE_PATH`. First part, #3 is easy, we just want
to test for the `event/FILE_PATH` ends in `.cpl`, we can do this using the `ends with` operator.

Most operators will use a `path` and a `value`. General convention is the `path` describes
how to get to a value we want to compare within the event. So `event/FILE_PATH` says "starting in the `event`
then get the `FILE_PATH`. The `value` generally represents a value we want to compare to the element found
in the `path`. How it is compared depends on the operator.

```
op: and
event: CODE_IDENTITY
rules:
  - op: is windows
  - op: ends with
    path: event/FILE_PATH
    value: .cpl
```

That was easy, but we're missing a critical component! By default, D&R rules operate in a case sensitive mode.
This means that the above node we added will match `.cpl` but will NOT match `.cPl`. To fix this, we just add
the `case sensitive: false` statement.

```
op: and
event: CODE_IDENTITY
rules:
  - op: is windows
  - op: ends with
    path: event/FILE_PATH
    value: .cpl
    case sensitive: false
  -
```

Finally, we want to make sure the `event/FILE_PATH` is NOT in the `windows` directory. To do this, we will use
a regular expression with a `matches` operator. But in this case, we want to EXCLUDE the paths that include
the `windows` directory, so we want to "invert" the match. We can do this with the `not: true` statement.

```
op: and
event: CODE_IDENTITY
rules:
  - op: is windows
  - op: ends with
    path: event/FILE_PATH
    value: .cpl
    case sensitive: false
  - op: matches
    path: event/FILE_PATH
    re: ^.\:\\windows\\
    case sensitive: false
    not: true
```

Here we go, we're done drafting our first rule.

## Validate Rule

What we want to do now is validate the rule. If the rule validates, it doesn't mean it's correct, it
just means that the structure is correct, the operators we use are known, etc. It's the first pass at
detecting possible formatting issues or typos.

To validate, we will simply leverage the Replay service. This service can be used to test rules or replay
historical events against a rule. In this case however, we just want to start by validating.

Up until now we focused on the "detection" part of the rule. But a full rule also contains a "response"
component. So before we proceed, we'll add this structure. For a response, we will use a
simple `action: report`. The `report` creates a "detection" (alert).

```
detect:
  op: and
  event: CODE_IDENTITY
  rules:
    - op: is windows
    - op: ends with
      path: event/FILE_PATH
      value: .cpl
      case sensitive: false
    - op: matches
      path: event/FILE_PATH
      re: ^.\:\\windows\\
      case sensitive: false
      not: true
respond:
  - action: report
    name: T1196
```

Now validate: `limacharlie replay --validate --rule-content T1196.rule`

After a few seconds, you should see a response with `success: true` if the rule
validates properly.

## Test rule

### Test Plan

Now that we know our rule is generally sound, we need to test it against some events.

Our test plan will take the following approach:

1. Test a positive (a `.cpl` loading outside of `windows`).
2. Test a negative for the major criteria:

   1. Test a non-`.cpl` loading outside of `windows` does not match.
   2. Test a `.cpl` loading within `windows` does not match.
3. Test on historical data.

With this plan, #1 and #2 lend themselves well to [unit tests](https://en.wikipedia.org/wiki/Unit_testing)
while #3 can be done more holistically by using Replay to run historical events
through the rule and evaluate if there are any [false positives](https://en.wikipedia.org/wiki/False_positives_and_false_negatives).

This may be excessive for you, or for certain rules which are very simple, we leave that
evaluation to you. For the sake of this code lab, we will do a light version to demonstrate
how to do tests.

### Testing a Single Event

To test #1 and #2, let's just create some synthetic events. It's always better to use
real-world samples, but we'll leave that up to you.

Take the event sample we had in the "Draft Rule" section and copy it to two new files
we will name `positive.json`, `negative-1.json` and `negative-2.json`.

Modify the `positive.json` file by renaming the `FILE_PATH` at the bottom from
`"C:\\Windows\\System32\\setupcln.dll"` to `"C:\\temp\\System32\\setupcln.cpl"` so that
the event now describes a `.cpl` loading in the `temp` directory, which we should detect.

Then modify the `negative-1.json` file by changing the same `.dll` to `.cpl`. This should NOT
match because the path is still in the `windows` directory.

Then modify the `negative-2.json` file by changing the `windows` directory to `temp`. This
should still NOT match because it's not a `.cpl`.

Now we can run our 3 samples against the rule using Replay,

`limacharlie replay --rule-content T1196.rule --events positive.json` should output a result
indicating the event matched (by actioning the `report`) like:

```json
{
  "num_evals": 4,
  "eval_time": 0.00020599365234375,
  "num_events": 1,
  "responses": [
    {
      "report": {
        "source": "11111111-1111-1111-1111-111111111111.11111111-1111-1111-1111-111111111111.11111111-1111-1111-1111-111111111111.10000000.2",
        "routing": {
...
```

`limacharlie replay --rule-content T1196.rule --events negative-1.json` should output a result
indicating the event did NOT match like:

```json
{
  "num_evals": 4,
  "eval_time": 0.00011777877807617188,
  "num_events": 1,
  "responses": [],
  "errors": []
}
```

`limacharlie replay --rule-content T1196.rule --events negative-2.json` be the same as `negative-1.json`.

### Testing Historical Data

The final test is to run the rule against historical data. If you are not using an
organization on the free tier, note that the Replay API is billed on usage. In the
following step we will run against all historical data from the organization, so if
your organization is not on the free tier and it is large, there may be non-trivial
costs associated.

Running our rule against the last week of data is simple:

`limacharlie replay --rule-content T1196.rule --entire-org --last-seconds 604800`

No matches should look like that:

```json
{
  "num_evals": 67354,
  "eval_time": 1107.2150619029999,
  "num_events": 222938,
  "responses": [],
  "errors": []
}
```

### Moving to Unit Tests

Once your rule is done and you’ve evaluated various events for matches, you can move these to [D&R Rules Unit Tests](/v2/docs/unit-tests) so that the tests are run during rule update.

## Publish Rule

Now is the time to push the new rule to production, the easy part.

Simply run `limacharlie dr add --rule-name T1196 --rule-file T1196.rule`
and confirm it is operational by running `limacharlie dr list`.

Amazon Web Services

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Command-line Interface

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

In LimaCharlie, an Organization ID (OID) is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

---

### Related articles

* [Detection and Response Examples](/docs/detection-and-response-examples)
* [Detection and Response](/docs/detection-and-response)
* [Detection on Alternate Targets](/docs/detection-on-alternate-targets)
* [Sigma Converter](/docs/sigma-converter)

---

#### What's Next

* [Create a D&R Rule Using a Threat Feed](/docs/create-a-dr-rule-using-a-threat-feed)

Table of contents

+ [Introduction](#introduction)
+ [Setup and Requirements](#setup-and-requirements)
+ [Draft Rule](#draft-rule)
+ [Validate Rule](#validate-rule)
+ [Test rule](#test-rule)
+ [Publish Rule](#publish-rule)

Tags

* [detection and response](/docs/en/tags/detection%20and%20response)
* [tutorial](/docs/en/tags/tutorial "Tutorial")