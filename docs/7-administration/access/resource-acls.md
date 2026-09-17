# Resource ACLs

Resource ACLs restrict who can read the content of specific sensors and Config Hive records inside an organization. Use them when part of an org holds sensitive data, such as a mail feed with PII, that only some users should see.

You restrict a resource by tagging it `acl:<scope>`, and you control who holds a scope with a record in the `acl` hive.

ACLs are opt-in. An organization with no `acl:` tags behaves exactly as before.

## How it works

- **Metadata stays visible, content is gated.** Everyone with normal org permissions still sees that a sensor or record exists, along with its name, hostname, tags and online status. Only what is inside is restricted.
- **ACLs only restrict.** A caller needs the normal permission first (for example `sensor.get` or `secret.get`), then membership in the scope. Scope membership never grants a permission.
- **Multiple scopes are AND.** A resource tagged `acl:hr` and `acl:finance` is readable only by members of both. Adding a tag can only narrow access.
- **Missing scopes lock.** An `acl:` tag with no matching scope record, or with a disabled or expired one, locks the resource for everyone. Deleting a scope record does not unlock anything.
- **Current tags apply.** Restriction follows the tags a sensor has now. Tagging a sensor hides its full history. Removing the tag exposes it again.

## What is restricted

| Visible to anyone with org permissions | Restricted to scope members |
| --- | --- |
| Sensor list: hostname, platform, tags, online status, last seen | Sensor telemetry: timeline, historical events, Replay results |
| Hive record name, `usr_mtd` (tags, enabled, expiry, comment), `sys_mtd` | Hive record `data` |
| Artifact metadata | Artifact content and original logs |
| Output names | Tasking the sensor, output samples |
| Detection counts, dashboards, tag search | Detections from restricted sensors (hidden, not redacted) |

A few details:

- A restricted hive record comes back with its metadata intact and `data` replaced by `{"acl_restricted": true}`. Writing that marker back as data is rejected, so a sync from a restricted view cannot erase the real content.
- Fetching a restricted record for execution (playbooks, secrets resolved with `hive://secret/...`) is refused instead of redacted.
- Tasking a restricted sensor is refused for every command.
- A detection is hidden when its sensor, or any sensor that contributed to a stateful detection, is restricted for the caller.

## Permissions

| Permission | Allows |
| --- | --- |
| `acl.get` | Read scope records and list the resources tagged with a scope |
| `acl.set` | Create, change and delete scope records, and add or remove any `acl:` tag |

The `Owner` and `Administrator` roles include both. Existing Owners and Administrators need their role re-applied to receive them. Both can be granted individually to users and API keys.

`acl.set` does **not** grant read access. An administrator who can edit scopes still sees nothing restricted until they add themselves as a member. Since an `acl.set` holder can add themselves to any scope, treat `acl.set` as equivalent to seeing everything and grant it accordingly.

## Setting up a scope

The steps below use the [CLI](../../6-developer-guide/sdks/index.md). The same operations are available through the REST API and the SDKs.

### 1. Create the scope record

The record name is the scope name. This record creates scope `mailsec`:

```yaml
# mailsec.yaml
data:
  members:
    - type: user
      id: "<user UID>"
    - type: api_key
      id: "mail-pipeline"
    - type: group
      id: "<organization group ID>"
  warn_only: true
```

```bash
limacharlie hive set --hive-name acl --key mailsec --input-file mailsec.yaml --enabled
```

Always pass `--enabled`. A disabled scope locks every resource tagged with it, including for its members.

Starting with `warn_only: true` is recommended. See [Warn-only mode](#warn-only-mode).

### 2. Tag the resources

Sensors:

```bash
limacharlie tag add --sid <SID> --tag acl:mailsec
limacharlie tag mass-add --selector 'hostname contains "mail"' --tag acl:mailsec
```

Installation keys, so every sensor or adapter enrolled with the key gets the tag:

```bash
limacharlie installation-key create --description "mail adapters" --tags acl:mailsec
```

Hive records, such as secrets and extension configs:

```bash
limacharlie hive set --hive-name secret --key mail-imap-password --tag-add acl:mailsec
```

Each of these requires `acl.set` in addition to the usual permission (`sensor.tag`, `ikey.set`, or the hive's own set permission).

### 3. Check the result, then enforce

While the scope is warn-only, watch the organization errors for `acl/mailsec` entries. Each one names a user or key that would have been denied. Add the ones who should have access, then set `warn_only: false` (or remove it) and apply the record again.

To list the hive records carrying a scope:

```bash
limacharlie api 'orgs/{oid}/acl/mailsec/resources'
```

This returns metadata only, grouped by hive, and requires `acl.get`. Use `limacharlie tag find --tag acl:mailsec` for sensors.

## Scope records

| Field | Description |
| --- | --- |
| `members` | List of principals holding the scope. An empty list is valid and locks the scope's resources for everyone. |
| `members[].type` | `user`, `api_key` or `group`. |
| `members[].id` | For `user`, the user's UID or email. For `api_key`, the org API key's name. For `group`, the organization group ID. |
| `warn_only` | `true` to report instead of enforce. Defaults to `false`. |

Scope names are case-insensitive and stored lowercase. They cannot be empty or contain `,`, `/`, spaces, tabs, line breaks or control characters.

Record `usr_mtd` works as in any hive, with one difference in effect: disabling or expiring a scope record **locks** its resources rather than releasing them.

Notes on members:

- Prefer the UID for users. A member listed by email matches the user's web and CLI sessions, but not the user's personal API keys. A UID member covers both.
- A `user` member never matches an org API key, even one named after the user.
- Records are limited to 64 KiB.

## Warn-only mode

With `warn_only: true`, a scope is not enforced. Every caller is treated as a member, so tagged resources behave as if the tag was absent. Every access the scope would have denied is reported as an organization error under the component `acl/<scope>`, naming the user or key and the resource.

Use it to roll out a scope without locking out analysts or cutting a SIEM feed by surprise.

- The org keeps one error entry per scope, holding the most recent violation. Reports are throttled to about one per scope every 15 minutes.
- Members of the scope are never reported.
- Warn-only does not relax tag writes. `acl.set` is still required to add or remove `acl:` tags.
- Warn-only does not apply to a disabled or expired record. Those still lock.
- Outputs are covered too. A record that would have been withheld from an output is delivered and reported.

## Outputs

Events and detections from restricted sensors are **excluded from outputs by default**. This includes outputs that existed before the tag was added, so tagging a sensor removes its data from your SIEM feed unless you opt the output in.

To opt an output in, set `acl_scopes` to the list of scopes it may carry:

```yaml
# output.yaml
dest_host: siem.example.com:6514
acl_scopes:
  - mailsec
```

```bash
limacharlie output create --name siem --module syslog --type event --input-file output.yaml
```

- A record reaches the output only if every `acl:` tag on its sensor is listed.
- To set `acl_scopes`, the caller needs `acl.set` or membership in every listed scope. The check runs when the output is saved. Later membership changes do not affect an existing output.
- Reading samples of an opted-in output requires membership in all of its scopes.
- Records with no sensor, such as billing or some deployment events, are not affected.
- Live streams in the web app only carry the scopes the viewer holds.

## D&R rules

D&R rules cannot add or remove `acl:` tags. The `add tag`, `remove tag`, `add hive tag` and `remove hive tag` actions reject them, because rules run without a user identity to check `acl.set` against.

Three response actions send event content outside the platform and are refused on events from restricted sensors: `service request`, `extension request` and `start ai agent`. To allow them, list the scopes in the rule's `acl_scopes` field, next to `detect` and `respond`:

```yaml
detect:
  event: NEW_DOCUMENT
  op: ends with
  path: event/FILE_PATH
  value: .eml
respond:
  - action: extension request
    extension name: ext-reliable-tasking
    extension action: task
    extension request:
      sid: '{{ .routing.sid }}'
      task: 'os_version'
acl_scopes:
  - mailsec
```

- The action is allowed only when every `acl:` scope on the event's sensor is in `acl_scopes`.
- Changing `acl_scopes` requires `acl.set` or membership in every scope in the new list. Removing all scopes requires `acl.set`.
- Editing other parts of the rule does not require membership, as long as `acl_scopes` is unchanged.
- The rule's scopes are forwarded to the extension, which uses them to decide what the request may reach.
- `report` and `task` actions are not affected. Their results go through channels that are already gated.

## Extensions

An extension acts through its own org API key, named `_<extension name>-<uuid>`. To let an extension read or task restricted resources, add that key's name as an `api_key` member of the scope.

- A playbook tagged with a scope can only be run by the Playbook extension once its key is a member.
- Extensions also receive the scopes held by the user or rule that made the request, and are expected to honor them.
- Reliable Tasking checks both. A sensor is skipped with reason `creator_not_member` when the task's creator does not hold the sensor's scopes, and with `extension_not_member` when the extension's key does not. Skipped tasks are not retried; re-create them after fixing membership.

## Infrastructure as Code

Scope records are ordinary hive records in the `acl` hive, so `limacharlie hive list|get|set --hive-name acl` and the SDK hive clients work on them.

The Infrastructure extension includes the `acl` hive only when its identity holds both `acl.get` and `acl.set`. Pushing any record or sensor change that adds or removes an `acl:` tag also requires `acl.set`.

## Errors

| Code | Meaning |
| --- | --- |
| `ACL_CONTENT_RESTRICTED` | HTTP 403. The caller is not a member of every scope on the resource. |
| `UNAUTHORIZED_ACL_TAG` | HTTP 401. Adding or removing an `acl:` tag without `acl.set`. |
| `ACL_TAG_TTL_NOT_ALLOWED` | `acl:` tags cannot have a TTL. |
| `ACL_SCOPE_UNAVAILABLE`, `ACL_SCOPES_UNAVAILABLE` | Scope membership could not be resolved. Retry. |

When membership cannot be resolved, restricted content stays locked. Unrestricted content is not affected.

## Limits and behavior to know

- **Propagation.** Tag changes usually apply within seconds. Membership changes also usually apply within seconds, and at most within about 5 minutes.
- **Enrollment.** Tags from an installation key are applied right after enrollment, not atomically with it. A new sensor can be briefly unrestricted.
- **Deleting is not gated.** Deleting a sensor, a hive record or an installation key does not require `acl.set` or membership. Deletion destroys content instead of exposing it. Deleting an installation key does not remove tags from sensors already enrolled.
- **Tag TTLs.** `acl:` tags cannot expire, so a restriction is never removed silently.
- **IOC search.** Object and IOC searches still list the sensors that saw a value, including restricted ones. Only event content is gated.
- **Audit logs** are not restricted.

## Troubleshooting

If a user reports that data disappeared:

1. Check whether the org has any `acl:` tags (`limacharlie tag list`). If not, ACLs are not involved.
2. Check that each `acl:` tag in use has a matching `acl` hive record that is enabled and not expired. A tag without one locks its resources.
3. Check that the user or key is a member of **every** scope on the missing resources. For personal API keys, the member must be listed by UID.
4. Check the outputs. Existing outputs stop receiving a sensor's data once it is tagged, until they list the scope in `acl_scopes`.

## See also

- [User Access](user-access.md)
- [API Keys](api-keys.md)
- [Sensor Tags](../../2-sensors-deployment/sensor-tags.md)
- [Config Hive](../config-hive/index.md)
- [Reference: Permissions](../../8-reference/permissions.md)
