# Permissions

The Investigation Engine is checked at the API gateway, which requires the
permissions below. Three more checks happen beyond them: the engine applies the
policy's per-class `approvers` list to decisions, a few reads need
`investigation_policy.set`, and every read or action a run makes is authorized as the
run's identity (see [What a run can do](#what-a-run-can-do)).

!!! warning "Plan and policy permissions are not part of any role"
    `investigation_plan.*` and `investigation_policy.*` are **not** in the Owner role
    or in any preset role. They are granted explicitly, to a person or to an API key.
    An Owner who has not been granted them is refused by the Hive when saving a
    template or a policy.

## Using runs

The gateway requires **all** permissions of a row. A missing one is answered `401`
with `unauthorized: missing permission <name>`.

| To do this | Required permissions |
|---|---|
| Read runs, steps, the run graph, events, case documents, labels, templates, operators, fact packs, the effective policy, the approvals inbox and the authoring kit; validate a template; read test results | `investigation.get`, `insight.evt.get` |
| Start a run or a wave; add inputs; cancel, compare or delete a run; submit a label; **test a template on past alerts** | `investigation.set`, `insight.evt.get` |
| Approve, deny, revert, extend or confirm an action | `investigation.set`, `insight.evt.get`, **and the permission of the action's class** (below) |
| Read the performance stats; filter the run list by outcome or verdict | `investigation.get`, `insight.evt.get` **and `investigation_policy.set`** |

`insight.evt.get` is required everywhere because a run's results are what a search of
the organization's telemetry found: a role that can use Cases but cannot read
telemetry cannot read them through the engine either. Grant these permissions
explicitly to anyone who should use the engine, and check your roles: holding
`investigation.get` alone shows nothing.

### Permission of the action class

Deciding an action needs `investigation.set` plus the permission of what the action
does, because approving is how a person authorizes the engine to do it:

| Action class | Additional permission |
|---|---|
| `contain.email` | `mailsec.act` |
| `contain.network`, `contain.seal`, `contain.process`, `contain.identity` | `sensor.task` |
| `eradicate.process`, `eradicate.file` | `sensor.task` |
| `collect.memory`, `collect.file`, `collect.artifact` | `sensor.task` |
| `tag`, `tag.add`, `tag.remove` | `sensor.tag` |
| `close.false_positive` | `investigation.set` for a case; `mailsec.set` for an email message |

A class with no mapping is refused (fail closed). Which classes can actually execute
is in [Action classes](policies.md#action-classes).

When the class's policy names `approvers`, the engine also requires the person to be
on that list to **approve, deny, extend or confirm**; **revert** only needs the
permissions above. See [Approvals](policies.md#approvals).

### Who can see a run

A run belongs to the organization. Anyone with the read permissions sees all of the
organization's runs, and anyone with the write permissions can cancel, compare or
delete one. Only the identity that **started** a run can add inputs to it
(`403` otherwise); the steps the added inputs release run as the run's own identity.

## Templates and policies

Templates and policies are Hive records with the usual
[Config Hive](../7-administration/config-hive/index.md) permissions.

| To do this | Required permission |
|---|---|
| Read a template's record (its YAML) from the Hive | `investigation_plan.get`. Listing the templates the engine serves (`GET /templates`) needs only the run read permissions. |
| Create or edit templates, promote a draft | `investigation_plan.get`, `investigation_plan.set` |
| Delete templates | `investigation_plan.del` |
| Read or change template metadata only | `investigation_plan.get.mtd`, `investigation_plan.set.mtd` |
| Read, change or delete policies and their metadata | `investigation_policy.get`, `.set`, `.del`, `.get.mtd`, `.set.mtd` |
| Change what the AI may decide for a template (**AI may decide** in the console, `ai_may_decide` in the `default` policy record) | `investigation_policy.get`, `investigation_policy.set` |
| Use organization fact packs (`investigation_pack` records) | The `investigation_plan.*` permissions above |

Running a validation needs the read permissions, and a test the write permissions. A
test creates no run, case or action; its result is kept for 24 hours.

### Active templates can only be written by a person

A write that results in `status: active` is **refused when it comes from an API
key**, including an API key owned by a user. Only a person signed in as a user, in the
console or with an interactive login in the CLI (`limacharlie auth login --oauth`),
can create an active template, promote a draft or edit an active one. Demoting a
template to `draft` always works.

This is deliberate: an AI agent or a script holding an API key can write drafts but
can never put a template in a position to start from a rule or act on its own. An
organization that manages active templates with API keys, for example from a
Git-synced pipeline, can opt out by adding the tag `allow-api-key-promotion` to the
enabled `investigation_policy/default` record. Setting that tag needs
`investigation_policy.set.mtd`, so **never give an AI agent's key any
`investigation_policy.*` permission**: it could turn the gate off and promote its own
drafts. If the policy record cannot be read, the write is refused.

### Naming a secret as the run identity

The `identity` section of the `default` policy can name an organization API key
stored as a Hive secret, as `hive://secret/<name>`. Adding a **new** secret reference
requires that the person saving the policy can read that secret (`secret.get`, or
`secret.get.<name>` within the secret's access scope), and the secret must already
exist. Only an organization API key can be a run identity: a user API key is refused
when the run starts. Granting `investigation_policy.set` therefore lets its holder
point runs at any secret they can read.

## What a run can do

A run executes with the permissions of its identity: the token of the person or key
that started it, or the API key the policy names. Everything it reads and every action
it takes is checked against those permissions; a run can never read or do what its
identity cannot. The gateway permissions above only get a call to the engine; each
operator then needs the permission of its own data source. Without it the step is
`unknown` (`forbidden`), never empty. A recommended starting set for a policy identity
is in [step 3 of the walkthrough](walkthrough.md#3-the-run-identity-an-api-key-the-policy-names).

A **live sensor read** (`sensor.read.*`) tasks a sensor and needs `sensor.task.read`
(or the broader `sensor.task`) plus `output.set` on the identity. `sensor.task.read`
is an explicit grant, never part of a preset role. It permits only allowlisted live
metadata reads (processes, connections, autoruns, services, file hashes); file
contents, scripts, process termination, file deletion, isolation and unknown commands
are refused. For an observe-only identity, grant `sensor.task.read` instead of
`sensor.task` and keep actions at `suggest`.

## The key that turning a source on creates

Turning on automatic investigation for a source (the **Autopilot** settings in the
console) sets up everything the engine needs in one step: it installs the template
recipe for that product, creates an **organization API key** with the permissions
below, stores it in a Hive secret named `investigation-engine-autopilot-<source>`,
names that secret as the run identity, and subscribes the source's detections. A key
created this way is **setup-owned**: the engine made it, and it may replace it later.
Everything it does uses your token and your permissions (turning a source on needs
permission to change investigation policies), never the engine's own credential.

!!! note "Today's grants"
    This table is the full list of what a setup-owned key gets today. It is the same
    for every source: the key is not yet narrowed to the templates a source uses, and a
    later release is expected to narrow it. Check this page after an upgrade.

A setup-owned key is created with exactly what the library's templates and actions
do under it, so that nothing you enable later fails with `forbidden`:

| Permission | Why the key has it |
|---|---|
| `investigation.get`, `investigation.set` | Reading related cases, and writing the case a run opens and closing it as a false positive. |
| `ext.request` | Writing the case (the Cases extension is reached through an extension request), and the reads of vulnerabilities and application control. |
| `mailsec.get`, `mailsec.detonate`, `mailsec.set` | Reading stored messages, requesting a link detonation, and closing a message as a false positive. |
| `mailsec.act` | `contain.email`: quarantining a message and releasing it. |
| `sensor.tag` | `tag`, `tag.add`, `tag.remove`. |
| `sensor.task` | `contain.network` (isolating a sensor and releasing it) and the live sensor reads. |
| `output.set` | The answer stream of live sensor reads (`sensor.read.*`). |
| `sensor.get`, `sensor.list` | Sensor records, host state before isolation or tagging, and the roster. |
| `insight.det.get`, `insight.evt.get` | Detections and telemetry, including searches. |
| `cloudsec.get` | Entity, identity, cloud-security and code findings, and the endpoint click and coverage checks. |
| `lookup.get` | Your Lookups, including the trust lists. |
| `dr.set.managed`, `dr.list.managed`, `dr.del.managed` | The managed D&R rules that start the source's investigations. |

These are ordinary LimaCharlie permissions. **What runs by itself is still decided by
the policy**, not by the key: the autonomy modes, the caps and the
[registered authorizations](policies.md#autonomy-modes) apply whatever the key can do,
and an action a person approves runs with the key too, so the key needs the class's
permission even for actions a person decides. A source starts in `shadow` mode, which
investigates and records without changing anything.

### The readiness check

The Autopilot settings and the `GET /autopilot` route report, for each source that is
turned on, `identity_readiness`: `{source, identity, ready, missing_permissions,
extra_permissions, error_code, fix_hint}`. `identity` names the Hive secret, never the
key. A source is `ready` when its key holds every permission above. Extra permissions
are only informational. When it is not ready, `fix_hint` says what to do: restore or
enable the secret, or re-run setup. Reading the check needs `investigation_policy.get`,
`secret.get` and `apikey.ctrl`; without them the answer is `identity_unavailable`.

A key created before 2026-11-21 lacks `ext.request`, `mailsec.act`, `output.set`,
`sensor.tag` and `sensor.task`. It could not write cases, quarantine, tag, isolate or
read live state, and the check lists those as missing.

**The fix is to turn the source off and on again.** Setup runs again, finds the
setup-owned key short of permissions and replaces it with a key that has the full list
plus any extra permission an administrator had added, then revokes the old key. It
changes nothing when the key already has everything.

### Bring your own key

Setup rotates only a key it created. A key you stored in the secret yourself is never
rotated or revoked: setup requires it to hold **every** permission in the table
(extras are accepted), and refuses to turn the source on with `credential_permissions`
and the names of the missing ones when it does not. Use this to hold the key in your
own key-management process or to name it your way.

A read-only identity (no `sensor.task`, no `mailsec.act`) is **not** accepted by
setup today, because the library's actions need those permissions. To keep the engine
from changing anything, leave the action classes at `suggest` or `off` in the
[policy](policies.md#autonomy-modes): the engine then never executes those actions,
even though the key could.
For runs started by a D&R rule or a person, the policy's own `identity` can instead
name a key that you restrict yourself: for an observe-only key grant `sensor.task.read`
and `output.set` rather than `sensor.task`, as in
[What a run can do](#what-a-run-can-do).

## Console access

The console needs `investigation.get` **and** `insight.evt.get` to show the
Investigations section at all. Controls the gateway would refuse are disabled with a
tooltip naming the permissions you need. See [Console](console.md).

## Keys: two limits to know

- An API key must have a key id to use the Investigation Engine. A key without one is
  refused on every route with `this API key has no key id, so it cannot own
  investigation runs`.
- An API key restricted to an IP range (`allowed_ip_range`) currently fails, because
  the engine presents the forwarded token from a different address.
