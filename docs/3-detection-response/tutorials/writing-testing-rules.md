# Writing and Testing Rules

Detection & Response () Rules are similar to Google Cloud Functions or AWS Lambda.
You push D&R rules to the LimaCharlie cloud. The cloud applies the rules in real
time to the data that comes from the sensors.

You can also apply D&R rules to [Artifact Collection](../../5-integrations/extensions/limacharlie/artifact.md). This page describes
the simple case: a rule that applies to sensor events.

For the full list of rule operators and more documentation, see the [Detection and Response](../examples.md) section.

## Life of a Rule

The cloud usually applies a D&R rule to one event at a time. First, it evaluates the
"detection" component of the rule to find if the rule matches. If the rule matches, the
cloud applies the "response" component.

The cloud evaluates the detection one step at a time. It starts at the root of the
detection. If the root matches, the rule matches.

The detection component contains "nodes". Each node has an operator that describes the
logical evaluation. Most operators are simple, such as `is` and `starts with`. You can
combine simple nodes with Boolean (true/false) logic through the `and` and `or` operators,
which reference a series of nodes. An `and` node matches if all of its sub-nodes match.
An `or` node matches if one or more of its sub-nodes match.

In an `or` node, the cloud stops at the first sub-node that matches. It skips the other
sub-nodes, because they cannot change the result of the "or". In an "and" node, the first
sub-node that fails stops the evaluation immediately.

If the "detection" component matches, the "response" evaluation starts.

The "response" component is a list of actions to do. If an action refers to a sensor, that
sensor is the sensor that sent the event.

Put the parts of the rule that most probably eliminate the event at the start of the rule.
LC can then move to the next event more quickly.

## Introduction

### Goal

This code lab creates a D&R rule that detects execution of
[Control Panel Items](https://attack.mitre.org/techniques/T1196/) in the MITRE ATT&CK framework.

### Services Used

This code lab uses the Replay service to validate and test the rule before you push it to production.

## Setup and Requirements

This code lab assumes that you have access to a Linux host (or a MacOS terminal with
`brew`). It also assumes that you have "owner" access to an LC Organization. If you do not
have one, create one. This code lab works with the free tier that comes with all
organizations.

### Install CLI

You can always interact with LC through the [web app](https://app.limacharlie.io), but you
can do daily operations and automation with the Command Line Interface (CLI). This code lab
uses the CLI.

Install the CLI: `pip install limacharlie --user`. If `pip` is not installed, install it.
The exact instructions depend on your Linux distribution.

### Create REST API Key

Create an API key that the CLI uses to authenticate with LC. Go to the REST API section of
the web app.

1. In the REST API section, click the "+" button in the top right of the page.
2. Give your key a name.
3. For simplicity, click the "Select All" button to enable all permissions. This is not recommended in a production environment.
4. Click the copy-to-clipboard button for the new key. Keep a record of the key, for example in a temporary text note.
5. On the REST API page, copy the "Organization ID" at the top of the page. Keep a record of it, as you did for the API key.

The Organization ID (OID) is the unique identifier of your organization. The API key grants specific permissions to this organization.

### Login to the CLI

In your terminal, log in with your credentials: `limacharlie auth login`.

1. When the CLI asks for the Organization ID, paste the OID from the previous step.
2. When the CLI asks for a name for this access, leave it blank to set the default credentials.
3. When the CLI asks for the secret API key, enter the key from the previous step.

The setup is complete. If you run `limacharlie dr list`, the command shows no errors.

## Draft Rule

To draft the rule, open a text editor and save the rule to a file named `T1196.rule`.
A rule uses the [YAML](https://en.wikipedia.org/wiki/YAML) format. If you do not know YAML, spend a few minutes to learn it. YAML is not complex.

The rule is based on the [T1196](https://attack.mitre.org/techniques/T1196/) technique. It
needs these constraints:

1. The rule applies to Windows only.
2. The event is the load of a module (a DLL on Windows).
3. The module that loads ends with `.cpl` (the control panel extension).
4. The module loads from outside the `C:\windows\` directory.

LC supports many event types. To make the rule fail as quickly as possible, first filter out
all events that do not matter.

This rule uses only [CODE_IDENTITY](../../8-reference/edr-events.md#code_identity) events. The rule also uses more than one
criterion. The rule AND-s the criteria together, because it must match only when all of them
match.

```yaml
op: and
event: CODE_IDENTITY
rules:
  -
```

The block above sets up criterion #2 and the AND operation that follows. The `and` node is at
the top of the rule, and it has an `event:` clause. Therefore, the rule skips any event that
is NOT a `CODE_IDENTITY` event immediately.

Next, add the other criteria to the `rules:` list. This list holds all the sub-nodes that the
rule AND-s together.

Criterion #1 limits the rule to Windows:

```yaml
op: and
event: CODE_IDENTITY
rules:
  - op: is windows
  -
```

Criteria #3 and #4 come next. The `FILE_PATH` component of the `CODE_IDENTITY` event gives
both of them. To confirm the structure of these events, open the Historic View. Start a new
process on that host. Then find the relevant event. On a Windows host, the event looks like
this example:

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

The rule therefore applies to `event/FILE_PATH`. For criterion #3, test that
`event/FILE_PATH` ends with `.cpl`. Use the `ends with` operator.

Most operators use a `path` and a `value`. The `path` describes how to get to the value that
you want to compare in the event. For example, `event/FILE_PATH` means "start in the `event`,
then get the `FILE_PATH`". The `value` is the value that you compare to the element at the
`path`. The operator controls how the comparison works.

```yaml
op: and
event: CODE_IDENTITY
rules:
  - op: is windows
  - op: ends with
    path: event/FILE_PATH
    value: .cpl
```

One critical component is missing. By default, D&R rules are case sensitive. The node above
matches `.cpl` but does NOT match `.cPl`. To correct this, add the `case sensitive: false`
statement.

```yaml
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

Last, make sure that `event/FILE_PATH` is NOT in the `windows` directory. Use a regular
expression with the `matches` operator. The rule must EXCLUDE the paths that contain the
`windows` directory, so it must invert the match. The `not: true` statement inverts the
match.

```yaml
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

The draft of the first rule is complete.

## Validate Rule

Now validate the rule. Validation does not show that the rule is correct. It shows that the
structure is correct, that the operators are known, and so on. Validation is the first pass
to find possible format problems or typos.

Validation uses the Replay service. This service can test rules or replay historical events
against a rule. This step uses only the validation function.

The steps above cover only the "detection" part of the rule. A full rule also contains a
"response" component. Add this structure before you continue. The response uses
`action: report`. The `report` action creates a "detection" (alert).

```yaml
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

Now validate the structure of the rule. Save the detect and respond components to separate files (`T1196_detect.yaml` and `T1196_respond.yaml`), then run:

`limacharlie dr validate --detect T1196_detect.yaml --respond T1196_respond.yaml`

After a few seconds, the response shows `success: true` if the rule is valid.

## Test rule

### Test Plan

The rule is now structurally sound. Test it against some events.

The test plan uses these steps:

1. Test a positive match: a `.cpl` that loads outside `windows`.
2. Test a negative match for each major criterion:

   1. Test that a non-`.cpl` file that loads outside `windows` does not match.
   2. Test that a `.cpl` that loads in `windows` does not match.
3. Test on historical data.

Steps #1 and #2 are a good match for [unit tests](https://en.wikipedia.org/wiki/Unit_testing).
Step #3 uses Replay to run historical events through the rule and to find
[false positives](https://en.wikipedia.org/wiki/False_positives_and_false_negatives).

This plan can be more than you need, or more than a simple rule needs. You decide how much to
test. This code lab uses a short version of the tests as a demonstration.

### Testing a Single Event

For tests #1 and #2, create some synthetic events. Real-world samples are better, but the
choice is yours.

Take the event sample from the "Draft Rule" section and copy it to two new files that you
name `positive.json`, `negative-1.json` and `negative-2.json`.

In `positive.json`, change the `FILE_PATH` at the bottom from
`"C:\\Windows\\System32\\setupcln.dll"` to `"C:\\temp\\System32\\setupcln.cpl"`. The event
then describes a `.cpl` that loads in the `temp` directory, and the rule must detect it.

In `negative-1.json`, change the same `.dll` to `.cpl`. This event must NOT match, because
the path is still in the `windows` directory.

In `negative-2.json`, change the `windows` directory to `temp`. This event must NOT match,
because the file is not a `.cpl`.

Now run the 3 samples against the rule with Replay.

The command `limacharlie dr test --input-file T1196.rule --events positive.json` shows that
the event matched. The result contains the `report` action:

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

The command `limacharlie dr test --input-file T1196.rule --events negative-1.json` shows that
the event did NOT match:

```json
{
  "num_evals": 4,
  "eval_time": 0.00011777877807617188,
  "num_events": 1,
  "responses": [],
  "errors": []
}
```

The result of `limacharlie dr test --input-file T1196.rule --events negative-2.json` is the same as the result for `negative-1.json`.

### Testing Historical Data

The last test runs the rule against historical data. The Replay API is billed on usage if
your organization is not on the free tier. The next step runs against all historical data
from the organization. A large organization that is not on the free tier can therefore cause
significant costs.

To run the rule against the last week of data, use these commands:

```bash
START=$(date -d '7 days ago' +%s)
END=$(date +%s)
limacharlie replay run --detect-file T1196_detect.yaml --respond-file T1196_respond.yaml --start $START --end $END
```

A result with no matches looks like this:

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

After the rule is complete and you evaluate events for matches, move these events to
[D&R Rules Unit Tests](../unit-tests.md). LC then runs the tests at each rule update.

## Publish Rule

Now push the new rule to production.

Run `limacharlie dr set --key T1196 --input-file T1196.rule --enabled`.
Then run `limacharlie dr list` to confirm that the rule is operational.
The `--enabled` flag creates the rule and enables it in one step. Without
the flag, the cloud stores the rule as disabled, and the rule does not fire on matching events.
