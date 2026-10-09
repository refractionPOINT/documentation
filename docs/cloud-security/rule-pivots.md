# Pivots in Rules and Outputs

A pivot lets a Detection & Response (D&R) rule or an output ask a question about an identifier and get the answer from your organization's [Entities](entity-pivot.md). You name an identifier the event has, say what type it is, and say the one thing you want back: the owner's email, the hostnames of the same machine, the sensor that reported an IP address.

Use a pivot when the event does not carry the context you need. A firewall log names an IP address but not the machine behind it. A process event names a sensor but not the person who owns it.

!!! note "Requirements"
    Pivots require Cloud Security, because the answers come from the User and Host entities that Cloud Security builds from your sensors and connected providers. Saving a rule or an output that contains a pivot also needs extra permissions; see [Permissions](#permissions).

## Pivot vocabulary

A pivot is a triple: `from`, a value, and `to`.

- `from` is the type of the identifier you have.
- The value is read from the event, or written in a template.
- `to` is what you want back.

`from` and `to` are always literal strings. They cannot be templated.

### `from`

`from` is one of the [identifier types](entity-pivot.md#identifiers-and-confidence): `sensor_id`, `hostname`, `fqdn`, `email`, `ad_account`, `ad_account_short`, `username`, `windows_sid`, `device_id`, `serial`, `mac`, `cloud_instance_id`, `aws_arn`, `graph_urn`, `entra_object_id`, `okta_user_id`, `gws_user_id`, `github_login` or `github_user_id`.

`ip` is also accepted, with different behavior. See [Address pivots](#address-pivots).

### `to`

| `to` | Returns |
|------|---------|
| `entity` | The entity ID. |
| `name` | The entity's display name. |
| An identifier type, such as `hostname`, `email` or `sensor_id` | The other identifiers of that type on the same entity. |
| `owner.entity`, `owner.name`, `owner.<identifier type>` | Starting from a Host, the same value for the Users that own it. |
| `owned.entity`, `owned.name`, `owned.<identifier type>` | Starting from a User, the same value for the Hosts they own. |

For example, `from: sensor_id` with `to: owner.email` returns the email addresses of the Users that own the machine behind a sensor. `from: email` with `to: owned.hostname` returns the hostnames of the machines a User owns.

A pair that does not exist is refused when the rule or output is saved.

### What an answer contains

- Only confirmed links are followed. A [possible match](entity-pivot.md#identifiers-and-confidence) is never used.
- An identifier that resolves to more than one entity is ambiguous. It returns nothing.
- An answer holds at most 32 values. When more exist, `truncated` is `true`.

## The `pivot` operator

The `pivot` operator is part of the detection half of a rule. It reads an identifier from the event, asks for the value you want, and matches when at least one value is found.

```yaml
op: pivot
path: routing/sid
from: sensor_id
to: owner.email
name: owner
metadata_rules:
  op: matches
  re: '@example\.com$'
  path: values/?
```

| Parameter | Required | Meaning |
|-----------|----------|---------|
| `path` | Yes | Where the identifier is read in the event. |
| `from` | Yes | Literal identifier type of the value at `path`. |
| `to` | Yes | Literal value to return. |
| `name` | No | Names the result in the detection's metadata. |
| `metadata_rules` | No | Detection logic evaluated against the result. Omit it to match on any answer. |

If `path` yields several values, each one is pivoted, up to 16, and the answers are merged. If `path` yields no value, or the answer is empty, the operator does not match.

### The result

On a match, the result is added to the detection's metadata, in `mtd`. The key is `pivot_<from>_<to>`, with every non-alphanumeric character replaced by `_`, or `pivot_<name>` when `name` is set. For the operator above the key is `pivot_owner`:

```yaml
pivot_owner:
  values:
    - alice@example.com
  count: 1
  truncated: false
  approximate: false
```

| Field | Meaning |
|-------|---------|
| `values` | The values found. |
| `count` | The number of values. |
| `truncated` | `true` when more than 32 values exist and only some are returned. |
| `approximate` | `true` when the answer is a best guess. It is always `true` for address pivots. |

`metadata_rules` use paths relative to this result, so write `count` or `values/?`, not `mtd/...`. A path with `?` is tested against every element of the list.

Two `pivot` operators in one rule that would write the same key are refused when the rule is saved. Give each one a distinct `name`.

The result is part of the detection, so outputs, cases and playbooks that receive the detection already have it under `mtd`. Copying it into a report's `metadata` is optional.

In response actions the result is available under `.mtd`. The `values` of a stored result are a generic list, and `join` only accepts a list of strings, so `join` does not apply to it. Read it with `index`, `json` or `range` instead:

- One value: `{{ index .mtd.pivot_owner.values 0 }}`.
- All values as JSON: `{{ json .mtd.pivot_owner.values }}`, which renders like `["alice@example.com","bob@example.com"]`.
- All values separated by commas: `{{ range $i, $v := .mtd.pivot_owner.values }}{{ if $i }},{{ end }}{{ $v }}{{ end }}`.
- The number of values: `{{ .mtd.pivot_owner.count }}`.

The `pivots` template function is different: it returns a list of strings, so `join` works with it.

## Template functions

Two template functions give the same answers inside [template strings](../4-data-queries/template-strings.md):

- `pivot` renders the value as a string. Several values are joined with `,`. This is for display only, because a value can itself contain a comma.
- `pivots` returns a list of strings, for use with `range`, `index`, `join` and `json`.

Both take `from`, the identifier and `to`.

```text
{{ pivot "sensor_id" .routing.sid "owner.email" }}
{{ join ", " (pivots "sensor_id" .routing.sid "owned.hostname") }}
{{ range pivots "email" .event.USER_NAME "owned.hostname" }}{{ . }};{{ end }}
{{ json (pivots "sensor_id" .routing.sid "owner.email") }}
```

The functions are available:

- In D&R rule templates: values in the detection half, and fields in the response half such as a `report` name and metadata, extension request payloads, and the `prompt` and `data` of `ask ai`.
- In [outputs](#outputs).

Address pivots are not available as template functions. See [Address pivots](#address-pivots).

## Address pivots

`from: ip` answers the question "which of my sensors reported this address within about the last two hours?" The answer is built from the internal and external addresses that sensors report.

Address pivots are available only through the `pivot` operator in a rule. They cannot be used in templates or in outputs.

The `to` values are `entity`, `name`, an identifier type, and `owner.*`.

```yaml
op: pivot
path: event/SOURCE_IP
from: ip
to: hostname
```

How to read the answer:

- **Several sensors can hold one address.** Home networks, overlapping ranges, and a shared office or VPN address all produce this. All of them are returned, and the answer is always flagged `approximate`. A rule that needs exactly one host tests `count`.
- **A very common address is capped.** The answer is flagged `truncated` and means "at least these".
- **The answer is about the present.** An event older than about two hours, or one with a missing or badly wrong time, is not answered, and the operator does not match for it.
- **No match is not proof.** The device behind the address can be unmanaged, or its sensor can be offline. No match never shows that no managed device has the address.

Because no match proves nothing, an address pivot cannot be placed under `not: true`, either on the operator itself or on any operator that encloses it. Such a rule is refused when it is saved.

For questions about the past, such as who had an address yesterday at 14:02, use the [Entity Pivot](entity-pivot.md) API or CLI with a time. A rule cannot ask that question.

## Examples

### Find the host behind an address in firewall logs

An adapter delivers firewall events that name an internal client address. The event type and field names below depend on your adapter mapping; replace them with yours.

Check that the address is internal first, so the pivot only runs for addresses a sensor could have reported.

```yaml
detect:
  event: firewall-traffic
  op: and
  rules:
    - op: is private address
      path: event/SOURCE_IP
    - op: pivot
      path: event/SOURCE_IP
      from: ip
      to: hostname
respond:
  - action: report
    name: firewall-blocked-internal-client
    metadata:
      client_hosts: '{{ json .mtd.pivot_ip_hostname.values }}'
```

### Require a single host for failed logons

On a server, report failed logons from an internal address, but only when exactly one sensor reported that address. `metadata_rules` tests the `count` of the answer.

```yaml
detect:
  event: WEL
  op: and
  rules:
    - op: is
      path: event/EVENT/System/EventID
      value: '4625'
    - op: is private address
      path: event/EVENT/EventData/IpAddress
    - op: pivot
      path: event/EVENT/EventData/IpAddress
      from: ip
      to: hostname
      metadata_rules:
        op: is
        path: count
        value: 1
respond:
  - action: report
    name: failed-logon-from-managed-host
    metadata:
      source_host: '{{ index .mtd.pivot_ip_hostname.values 0 }}'
```

### Check the kind of host at the other end of a connection

A workstation connects to an internal address over RDP or SMB. Report it when that address belongs to a host whose name marks it as a server. The `metadata_rules` test every returned hostname, and the rule matches if any of them starts with `srv-`.

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: scope
  path: event/NETWORK_ACTIVITY/
  rule:
    op: and
    rules:
      - op: or
        rules:
          - op: is
            path: event/DESTINATION/PORT
            value: 3389
          - op: is
            path: event/DESTINATION/PORT
            value: 445
      - op: is private address
        path: event/DESTINATION/IP_ADDRESS
      - op: pivot
        path: event/DESTINATION/IP_ADDRESS
        from: ip
        to: hostname
        metadata_rules:
          op: starts with
          path: values/?
          value: srv-
respond:
  - action: report
    name: workstation-to-server-rdp-smb
```

### Compare the source and the destination

When a rule needs two address pivots, both with the same `from` and `to`, give each a `name`. Without it both would write `pivot_ip_hostname` and the rule would be refused.

```yaml
detect:
  event: firewall-traffic
  op: and
  rules:
    - op: is private address
      path: event/SOURCE_IP
    - op: is private address
      path: event/DEST_IP
    - op: pivot
      path: event/SOURCE_IP
      from: ip
      to: hostname
      name: source
    - op: pivot
      path: event/DEST_IP
      from: ip
      to: hostname
      name: destination
respond:
  - action: report
    name: managed-host-to-managed-host
    metadata:
      source_host: '{{ json .mtd.pivot_source.values }}'
      destination_host: '{{ json .mtd.pivot_destination.values }}'
```

The rule matches when both addresses are answered.

### Add the owner to a detection

Put the owner of the machine in a report's metadata. This pivot starts from the event's own sensor, so it works for any detection.

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is windows
    - op: contains
      path: event/COMMAND_LINE
      value: -enc
respond:
  - action: report
    name: encoded-powershell
    metadata:
      owner: '{{ pivot "sensor_id" .routing.sid "owner.email" }}'
```

The same function adds the owner to an output. See [Outputs](#outputs).

### Acting on the pivoted sensor

Response actions act on the event's own sensor. If the event came from a firewall, [`isolate network`](../8-reference/response-actions.md#isolate-network) would act on the firewall's sensor, not the machine behind the address. To act on the pivoted machine, use `to: sensor_id` in the pivot so its sensor ID is in the detection's metadata, and have a [playbook](../5-integrations/extensions/limacharlie/playbook.md) read it from there.

## Outputs

The template functions work in:

- `custom_transform`, for all output types.
- The Slack `message` and `attachment_text` templates.
- The SMTP `subject` and `template` templates.
- The Microsoft Teams `message` template.
- The Telegram `message` template.

They are refused in Elastic and OpenSearch `index` names. Address pivots are refused in outputs.

To add the owner of the sensor to every event an output sends, use the additive form of `custom_transform`:

```text
custom_transform: |-
  {
    "+owner_email": "{{ pivot \"sensor_id\" .routing.sid \"owner.email\" }}"
  }
```

An output never waits for a lookup:

- The event is always delivered.
- The first event for a given identifier can be delivered with an empty value while the answer is fetched. The events that follow carry it.
- Values are refreshed periodically, so an answer can be up to about half an hour old.

## Permissions

Saving a rule or an output that contains a pivot needs `cloudsec.get` in addition to the permission you normally need: `dr.set` for a rule, `output.set` for an output. This applies to every save of that rule or output, not only the save that adds the pivot.

A rule with an address pivot also needs `insight.evt.get`.

The same applies to [API keys](../7-administration/access/api-keys.md) used by automation that pushes rules. A rule or an output saved without the permissions is refused, and the message names the missing permission. Enabling, disabling or tagging a rule does not need them.

See [Permissions](../8-reference/permissions.md) for the full list.

## When a pivot cannot be answered

A pivot cannot be answered when Entities are not ready for the organization (see [Readiness](entity-pivot.md#readiness-history-and-incomplete-results)), when a lookup fails temporarily, when the organization's lookup budget is exceeded, when the identifier is ambiguous, or when the rule was not saved with the required permission.

What happens depends on where the pivot is.

| Where | Result |
|-------|--------|
| Detection half, `pivot` operator or template function, except address pivots | The evaluation of that event fails. The rule does not match, including under `not:`. |
| Detection half, address pivot | The operator does not match. The rest of the rule is still evaluated, so other branches of an `or` still work. |
| Response half, a `report` | The detection is not lost. The report keeps its unrendered name and metadata text. |
| Response half, an action that acts with the value, such as `add tag`, `task` with an investigation ID, an extension request, or the fields of `start ai agent` | The action fails for that event. The other actions still run. |
| Outputs | The event is delivered. The value renders empty. |

Each failure is reported to the organization's error stream, at most about once per rule per minute. A stale event on an address pivot is not reported.

## Cost and placement

Lookups are cached. Each organization has a budget of new lookups per second. Exceeding it is reported as an error that tells you to put the pivot behind a cheaper condition. There is no per-lookup charge.

To stay within the budget:

- Put the `pivot` operator after cheaper conditions in an `and`. Conditions are evaluated in order, so an event that fails an earlier condition never triggers a lookup.
- Do not point a pivot at a field with unbounded values, such as remote internet addresses or external senders. Each new value costs a new lookup.
- For an internal address pivot, put `is private address` on the same path first.

## Testing rules and Replay

[Replay](../5-integrations/services/replay.md) and rule tests validate pivots, so unknown pairs and the refusals described on this page are reported. They do not answer pivots.

- An event whose evaluation reaches a pivot is counted as not evaluated. It is not a match.
- The results list `{action: "pivot", data: {oid, from, to}}` once per `from` and `to` pair.
- The Replay response stats include `events_pivot_not_evaluated`.

Order matters. In `or: [pivot, X]`, an event that `X` would have matched is reported as not matched.

To check what a pivot returns, test the rule on live events.

## See Also

- [Entity Pivot](entity-pivot.md)
- [Detection Logic Operators: pivot](../8-reference/detection-logic-operators.md#pivot)
- [Template Strings and Transforms](../4-data-queries/template-strings.md)
- [Outputs](../5-integrations/outputs/index.md)
