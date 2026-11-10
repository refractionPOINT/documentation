# Permissions

The Investigation Engine is checked at the API gateway. The engine itself trusts
the gateway and never sees a permission list, so everything on this page is what
the gateway (and the Config Hive) require.

!!! warning "Plan and policy permissions are not part of any role"
    `investigation_plan.*` and `investigation_policy.*` are **not** in the Owner
    role or in any preset role. They are granted explicitly, to a person or to an
    API key. An organization Owner who has not been granted them is refused by the
    Hive when saving a template or a policy.

## Using runs

The gateway requires **all** permissions of a row.

| To do this | Required permissions |
|---|---|
| Read runs, steps, the evidence graph, events, cases, labels, statistics, templates, operators, fact packs, the effective policy, the autonomy state, the approvals inbox, the authoring kit; validate a template; read test results | `investigation.get`, `insight.evt.get` |
| Start a run or a wave; add inputs to a run; cancel or compare a run; **test a template on past alerts** | `investigation.set`, `insight.evt.get` |
| Approve, deny, revert, extend or confirm an action | `investigation.set`, `insight.evt.get`, **and the permission of the action's class** (below) |
| Pause or resume automatic actions for the organization | `org.conf.set` only |

`insight.evt.get` is required on every route except pausing and resuming. It means a
role that can use Cases (`investigation.get`) but cannot read telemetry cannot read
the results an investigation gathered. Among the preset roles, only **Owner** holds
`investigation.get` and `investigation.set`; the Administrator, Operator and Viewer
presets hold neither, and Operator and Viewer also carry only `insight.evt.get.simple`.
Grant the permissions in the table above explicitly to anyone else who should use the
engine.

### Permission of the action class

Deciding an action needs `investigation.set` plus the permission of what the action
does, because approving is how a person authorizes the engine to do it:

| Action class | Additional permission |
|---|---|
| `contain.email` | `mailsec.act` |
| `contain.network`, `contain.process`, `contain.identity` | `sensor.task` |
| `eradicate.process`, `eradicate.file` | `sensor.task` |
| `collect.memory`, `collect.file`, `collect.artifact` | `sensor.task` |
| `tag` | `sensor.tag` |

A class with no mapping is refused (fail closed). For classes with an approver
list in the [policy](policies.md#autonomy-modes), the person must also be on that
list.

### Who can see a run

A run belongs to the organization. Anyone with `investigation.get` and
`insight.evt.get` sees all of the organization's runs, and anyone with
`investigation.set` and `insight.evt.get` can cancel or compare one. Only the
identity that **started** a run can add inputs to it, because later steps run with
that identity's token.

## Templates and policies

Templates and policies are Hive records. The permissions follow the usual
[Config Hive](../7-administration/config-hive/index.md) convention.

| To do this | Required permission |
|---|---|
| Read a template's record (its YAML) from the Hive | `investigation_plan.get`. Listing the templates the engine serves needs only the run read permissions. |
| Create or edit templates, promote a draft | `investigation_plan.set` (and `.get`) |
| Delete templates | `investigation_plan.del` |
| Read or change template metadata only | `investigation_plan.get.mtd`, `investigation_plan.set.mtd` |
| Read, change or delete policies and their metadata | `investigation_policy.get`, `.set`, `.del`, `.get.mtd`, `.set.mtd` |

Running a validation or a test needs only the run permissions above. It stores
nothing.

### Active templates can only be written by a person

A write that results in `status: active` is **refused when it comes from an API
key**, including an API key owned by a user. Only a person signed in as a user, in the
console or with a user login in the CLI (`limacharlie auth login`), can create an active
template, promote a draft or edit an active one. Demoting a
template to `draft` always works.

This is deliberate: an AI agent or script holding an API key can write drafts but can
never put a template in a position to start from a rule or act on its own. An
organization that manages active templates with API keys, for example from a
Git-synced pipeline, can opt out by adding the tag `allow-api-key-promotion` to
the enabled `investigation_policy/default` record. Setting that tag needs
`investigation_policy.set.mtd`, so **never give an AI agent's key any
`investigation_policy.*` permission**: it could turn the gate off and promote its own
drafts. If the policy record cannot be read, the gate stays
closed.

### Naming a secret as the run identity

The `identity` section of the default policy can name an organization API key stored
as a Hive secret, as `hive://secret/<name>`. Adding a **new** secret reference
requires that the person saving the policy can read that secret (`secret.get`, or
`secret.get.<name>` within the secret's access scope), and the secret must already
exist. Only an organization API key can be a run identity: a user API key is refused.

## What a run can do

A run executes with the permissions of its identity: the token of the person or key
that started it, or the API key the policy names. Everything a run reads and every
action it takes is checked against those permissions. A run can never read or do what
its identity cannot.

A **sensor read** (`sensor.read.*`) tasks a sensor and needs `sensor.task` and
`output.set` on the identity. Without them the fact is `unknown`, never "absent".

## Console access

The console needs `investigation.get` **and** `insight.evt.get` to show the
Investigations section at all. Controls the gateway would refuse are disabled with a
tooltip naming the permissions you need. See [Console](console.md).

## Keys: two limits to know

- An API key must have a key id to own runs. A key without one is refused with
  `this API key has no key id, so it cannot own investigation runs`.
- An API key restricted to an IP range (`allowed_ip_range`) currently fails, because
  the engine presents the forwarded token from a different address.
