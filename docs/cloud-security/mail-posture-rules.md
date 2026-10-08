# Mail Posture Rules

Mail posture rules evaluate mailbox and domain **configuration**: forwarding,
delegates, transport rules, connectors, and authentication policy. They produce
cloud-security findings through `cloudsec_policy`. For message content, verdict
scoring, and responses to individual messages, use
[Email Security custom rules](../email-security/custom-rules.md).

## Resource types and fields

All detection paths start with `event/`. These are normalized resource
properties, not the Message Data Model. For example, `event/policy` on a
`DmarcPolicy` describes the domain's configuration; `auth/dmarc/result` in a
`dr-mail` rule describes authentication of one message.

| Resource type | Properties |
|---|---|
| `Mailbox` | `address`, `display_name`, `provider_id`, `status` |
| `MailboxForwardingRule` | `mailbox_urn`, `mailbox_address`, `name`, `source_kind`, `enabled`, `destinations` (string array), `external`, `external_observed`, `keep_copy`, `inspected` |
| `MailboxDelegation` | `mailbox_urn`, `mailbox_address`, `delegate_address`, `permissions` (string array), `status`, `suspicious`, `suspicious_reason`, `inspected` |
| `MailTransportRule` | `name`, `enabled`, `priority` (integer), `bypasses_filtering`, `inspected` |
| `MailConnector` | `name`, `direction`, `enabled`, `domains` (string array), `inspected` |
| `DkimConfig` | `domain`, `selector`, `present`, `enabled`, `enabled_observed`, `record`, `inspected` |
| `SpfRecord` | `domain`, `present`, `record`, `inspected` |
| `DmarcPolicy` | `domain`, `present`, `policy`, `record`, `inspected` |

Flags are booleans; other unannotated properties are strings. Optional properties
can be absent. The presence of a resource type in the authoring vocabulary does
not guarantee that your provider or connection collects it. Inspect the actual
resources and collection coverage before treating a rule with no findings as a
successful control.

## Require an observation

Use `event/inspected: true` before making a claim about configuration. A failed
or unavailable inspection must not become a finding that a setting is absent.
Two properties need an additional guard:

- Forwarding: test `external_observed: true` before interpreting `external`.
- DKIM: test `enabled_observed: true` before interpreting `enabled`. The
  optional `enabled` flag may be omitted when false; `present` describes the
  DNS record and does not establish whether the provider enabled signing.

DMARC's `present` is serialized even when false. An inspected `present: false`
is therefore an observed missing record. Without `inspected: true`, the same
boolean does not establish that a DNS lookup completed.

## Example: external forwarding from a sensitive mailbox

Save this as `mail-posture.json`. It extends the built-in external-forwarding
condition with a mailbox restriction. It keeps the forwarding-rule resource as
the finding subject so different rules on the same mailbox remain distinct.

```json
{
  "policy_type": "rules",
  "rules": {
    "rules": [
      {
        "id": "custom-finance-external-forward",
        "name": "Finance mailbox forwards externally",
        "resource_type": "MailboxForwardingRule",
        "finding_class": "misconfig",
        "severity": "HIGH",
        "title": "Finance mailbox automatically forwards mail outside the organization",
        "detect": {
          "op": "and",
          "rules": [
            {"op": "is", "path": "event/inspected", "value": true},
            {"op": "is", "path": "event/enabled", "value": true},
            {"op": "is", "path": "event/external_observed", "value": true},
            {"op": "is", "path": "event/external", "value": true},
            {"op": "is", "path": "event/mailbox_address", "value": "finance@corp.example"}
          ]
        },
        "meta": {
          "description": "An inspected forwarding rule on the finance mailbox is enabled and forwards outside the tenant's known domains.",
          "rationale": "Automatic forwarding can disclose invoices and payment instructions without further account access.",
          "false_positives": "Approved archiving or accounting integrations may intentionally forward mail. Verify the destination and approval."
        }
      }
    ]
  }
}
```

```bash
limacharlie hive validate --hive-name cloudsec_policy --key mail-posture \
  --input-file mail-posture.json --oid $OID
limacharlie hive set --hive-name cloudsec_policy --key mail-posture \
  --input-file mail-posture.json --enabled --oid $OID
```

`event/destinations` is an array of strings. `scope` iterates objects and cannot
re-root a condition onto one of those strings; a scalar equality comparison on
the whole array does not test membership either. The example uses the collector's
observed `external` classification rather than trying to walk this string array.
Customer posture rules reject wildcard paths and nested scopes, and permit at
most two scopes per rule. Use the [posture operator allowlist and limits](custom-rules.md)
rather than the mail-message operator list; `lookup` and `string distance` are
not supported in custom posture rules.

## Other mail conditions

These are `detect` blocks. Place one inside the rule envelope above, changing
the ID, resource type, title, severity, and metadata to describe that control.
Each corresponds to a built-in condition, so first consider whether an override
of the existing rule would meet your needs.

### Missing or monitor-only DMARC

Resource type: `DmarcPolicy`. Built-in rule: `dmarc-missing-or-monitor-only`.

```yaml
op: and
rules:
  - op: is
    path: event/inspected
    value: true
  - op: or
    rules:
      - op: is
        path: event/present
        value: false
      - op: is
        path: event/policy
        value: none
```

### Enabled transport rule bypassing filtering

Resource type: `MailTransportRule`. Built-in rule:
`mail-transport-rule-bypasses-filtering`.

```yaml
op: and
rules:
  - op: is
    path: event/inspected
    value: true
  - op: is
    path: event/enabled
    value: true
  - op: is
    path: event/bypasses_filtering
    value: true
```

### Suspicious mailbox delegate

Resource type: `MailboxDelegation`. Built-in rule: `suspicious-mailbox-delegate`.

```yaml
op: and
rules:
  - op: is
    path: event/inspected
    value: true
  - op: is
    path: event/suspicious
    value: true
```

`suspicious` is an observed collector judgment. Read `suspicious_reason` and the
delegate's status when assessing the finding. Preserve the default resource
subject instead of setting `subject_path: mailbox_urn`: two suspect delegates
on one mailbox should remain independently identifiable.

## Validate the behavior

Check a positive observation, a benign observation, and an unavailable
observation for each rule. In particular, removing `inspected`, setting it to
false, or removing `external_observed` from a forwarding observation must prevent
a match. Also check that two forwarding rules or delegates on the same mailbox
produce independently identifiable findings.

These rules do not change an individual message's verdict or quarantine mail.
Use the [generic posture authoring guide](custom-rules.md) for record composition,
overrides, IDs, severity, and finding behavior, and the
[MailSec rule guide](../email-security/custom-rules.md) for message evaluation.
