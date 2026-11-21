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
that source needs, stores it in a Hive secret named
`investigation-engine-autopilot-<source>`, names that secret as the run identity, and
subscribes the source's detections. A key created this way is **setup-owned**: the
engine made it, and it may replace it later. Everything it does uses your token and
your permissions (turning a source on needs permission to change investigation
policies), never the engine's own credential.

### What each source's key gets

**Each source's key holds what that source's template needs, and nothing more.** An
email-only source never gets a sensor permission. The set is worked out from the
template, from a fixed table, so the same template gets the same permissions in every
organization: nothing is learned and there is no setting to tune. It adds up:

- **Every operator the template calls**, including the steps of the fact packs it uses
  and of the [checks](templates.md#checks-templates-other-templates-call) it calls
  (nested calls and calls per element included). A check never acts, so action classes
  are the calling template's.
- **Every action class in its `act` entries.** An action a person approves still runs
  with the key, so the key needs the class's permission even for actions a person
  decides.
- **What every run does**, whatever its template: `ext.request` (the case is written
  through the Cases extension), `insight.det.get` (the triggering detection),
  `investigation.get` and `investigation.set` (reading related cases, closing the case).
- **`mailsec.get` and `mailsec.set`** when the template reads a message: closing a
  message as a false positive.
- **`lookup.get`** when the template's `trust` names Lookups.
- **For the source itself**: `dr.set.managed`, `dr.list.managed` and `dr.del.managed`
  (the managed D&R rules that start its investigations) and, for the mailsec source,
  `mailsec.get` for its readiness check.

| Permission | What needs it |
|---|---|
| `cloudsec.get` | Entity, identity, cloud-security and code findings, and the endpoint click and coverage checks. |
| `dr.set.managed`, `dr.list.managed`, `dr.del.managed` | Every source: the managed D&R rules that start its investigations. |
| `ext.request` | Every run (writing the case); the reads of vulnerabilities and application control. |
| `insight.det.get` | Every run: the triggering detection; detection reads. |
| `insight.evt.get` | Telemetry reads and searches, process ancestry, prevalence, and the domain intelligence of link checks. |
| `investigation.get`, `investigation.set` | Every run: related cases, and the case close. |
| `lookup.get` | Your Lookups, including the trust lists. |
| `mailsec.act` | `contain.email`: quarantining a message and releasing it. |
| `mailsec.detonate` | Requesting a link detonation. |
| `mailsec.get` | Every Email Security read, the quarantine, the message close, and the mailsec source's readiness check. |
| `mailsec.set` | Closing a message as a false positive, and undoing it. |
| `output.set` | The answer stream of live sensor reads (`sensor.read.*`) and of file eradication. |
| `sensor.get` | Sensor records: host state before isolation or tagging. |
| `sensor.list` | The sensor roster (`org.roster`). |
| `sensor.tag` | `tag`, `tag.add`, `tag.remove`. |
| `sensor.task` | `contain.network` (isolating a sensor and releasing it), file eradication and the live sensor reads. |

For the default library, the template part of a key (the source's own
`dr.*.managed` permissions come on top) is:

| Template | Permissions |
|---|---|
| `appcontrol`, `cloud-exposure-finding` | `cloudsec.get`, `ext.request`, `insight.det.get`, `insight.evt.get`, `investigation.get`, `investigation.set` |
| `code-finding`, `identity-sign-in`, `saas-admin-action` | `cloudsec.get`, `ext.request`, `insight.det.get`, `investigation.get`, `investigation.set` |
| `endpoint-detection`, `suspicious-process` | The six of `appcontrol`, plus `lookup.get`, `output.set`, `sensor.get`, `sensor.tag`, `sensor.task` |
| `mailsec-message` | The six of `appcontrol`, plus `mailsec.act`, `mailsec.detonate`, `mailsec.get`, `mailsec.set` |
| `phishing-campaign` | The six of `appcontrol`, plus `mailsec.act`, `mailsec.get`, `mailsec.set`, `sensor.get`, `sensor.task` (it isolates the hosts that clicked) |

The mailsec source running `mailsec-message` therefore holds 13 permissions: those of
its row, the three `dr.*.managed` and nothing for sensors. A template of your own
gets the set its own steps and actions add up to. A template that calls something the
table does not know is refused when you turn the source on, with
`recipe_grants_unknown`.

These are ordinary LimaCharlie permissions. **What runs by itself is still decided by
the policy**, not by the key: the autonomy modes, the caps and the
[registered authorizations](policies.md#autonomy-modes) apply whatever the key can do.
A source starts in `shadow` mode, which investigates and records without changing
anything.

### When the template changes

- **Switching a source to another template** (saving its settings) runs setup again
  and replaces the key when the new template needs a permission the key lacks.
- **Editing the template's record in the Hive** does not run setup again. The
  [readiness check](#the-readiness-check) compares the key with what the template
  needs now and reports the gap until someone re-runs setup (turn the source off and
  on, or save its settings again). A template edit can take up to a minute to show.
- **A run in the meantime is never broken without saying why.** A step the platform
  refuses is `unknown` (`forbidden`), a case it cannot write is
  `cases_access_denied` naming `ext.request`, and an action it refuses fails with a
  note that starts `permission_denied:` and names the permissions the class needs.

### Narrowing and extra permissions

Re-running setup replaces a setup-owned key in two cases: it lacks a permission the
template needs, or it holds a permission that setup gave and the template no longer
needs. The new key is exactly the required set plus every permission **an
administrator added** to the old one, which is kept. So a key created with the
broader list of an earlier release narrows to its template's set the next time setup
runs, and a key widened for a bigger template narrows back when the template needs
less. Setup tells its own permissions from an administrator's by one fixed list:
every permission setup has ever given. One an administrator added that is on that list
(for example `sensor.list`) looks like setup's own and is dropped when the template
does not need it. Add permissions outside it (for example `apikey.ctrl`) and they
stay.

### One secret can serve several templates

A run picks its identity through the policy's `identity` entry for its template, so a
secret serves every template that can select it. The key then holds the permissions of
the source's current template **plus** those of every other template bound to the
same secret: after you switch a source from one template to another, the old template
stays bound, and its D&R, case and API runs still use the key, so its permissions stay
until you remove that binding.

When a secret can be selected by runs that setup cannot know in advance, which are
the **inline plans** (`identity.templates.inline`), the **org-wide identity**
(`identity.default` or `allow`, which covers every template without its own entry)
and a bound template that does not parse, the key needs the **full set the default
library uses**. Setup widens it to that set and never narrows it, and says why in the
`identity` step and in the readiness `fix_hint`, for example "This key is also the
identity for inline plans, so it keeps every grant."

### The readiness check

The Autopilot settings and the `GET /autopilot` route report, for each source that is
turned on, `identity_readiness`: `{source, identity, ready, missing_permissions,
extra_permissions, error_code, fix_hint}`. `identity` names the Hive secret, never the
key. A source is `ready` when its key holds every permission its template needs
(plus those of the other bound templates). When it is not ready, `fix_hint` names who
needs each missing permission (the source's template, another template bound to the
secret, or the source itself for its intake rules) and what to do:

- For a **setup-owned** key: re-run setup (turn the source off and on, or save its
  settings again).
- For a key **you supplied**: add the permissions to it, or give the source's template
  its own identity (see below).

Extra permissions are informational and never block readiness. On a setup-owned key,
the extras that setup gave come with a hint to re-run setup to narrow the key. A
template that is not in the Hive or the library is `recipe_not_found`, one that does
not parse `recipe_invalid`. Reading the check needs `investigation_policy.get`,
`investigation_plan.get`, `secret.get` and `apikey.ctrl`; without them the answer is
`identity_unavailable`.

### Bring your own key

Setup replaces only a key it created. A key you stored in the secret yourself is never
rotated or revoked: setup requires it to hold **every** permission its source needs
(extras are accepted), and refuses to turn the source on with `credential_permissions`
and the names of the missing ones when it does not.

**A key you supplied as the org-wide identity** (`identity.default` in the
[policy](policies.md#run-identity)) serves every template without its own
entry, so it has to hold the full library set, not just the source's template's. When
it does not, turning the source on is refused, and the answer says who needs each
missing permission (the source's template, the source's intake rules, or "because this
key is also the org-wide identity") and gives both fixes:

1. Add the permissions to the key stored in the secret.
2. Give the source's template its own identity: in `investigation_policy/default`, set
   `identity.templates.<template>.default` to `caller`, then turn the source on again.
   Setup then creates a narrow setup-owned key for that template instead.

A read-only identity (no `sensor.task`, no `mailsec.act`) is **not** accepted by setup
for a template whose actions need them. To keep the engine from changing anything,
leave the action classes at `suggest` or `off` in the
[policy](policies.md#autonomy-modes): the engine then never executes those actions,
even though the key could. For runs started by a D&R rule or a person, the policy's own
`identity` can instead name a key that you restrict yourself: for an observe-only key
grant `sensor.task.read` and `output.set` rather than `sensor.task`, as in
[What a run can do](#what-a-run-can-do).

### Turning a source on: what to expect from setup

Turning a source on is one operation. Its answer lists the steps (`recipe`,
`identity`, `detection_subscription`, `enable`), each with a status and a reason:

| Status | Meaning |
|---|---|
| `done` | The step wrote something: the template was installed or activated, the identity was created or bound. |
| `already_present` | Nothing to change: the template was already active, the key already held what it needs. |
| `rotated` | `identity` only: the setup-owned key was replaced (widened or narrowed) and the old one revoked. The reason names the permissions added and removed, for example "Rotated the setup-owned key: added sensor.get, sensor.task; the old key was revoked." |
| `undone` | `recipe` only: a later step failed, so setup reverted what it wrote to the template. |
| `failed` | The step was refused or could not finish; its `error_code` and reason say why. |

- **A refused enable changes nothing.** Setup first checks, read-only, that the
  template is readable, enabled and parses (with the checks it calls), that its
  permissions can be worked out, that the policy and the secret are usable and that a
  key you supplied holds what it must. A refusal there writes nothing: no template is
  installed or activated, and the policy and secrets are untouched.
- **A write refused later is undone.** If promoting the template, writing the secret,
  creating the key or writing the policy is refused or gets no answer, setup reverts
  what it wrote to the template in the same call: an activated draft goes back to
  draft, and a library template it installed is removed (only while it still holds
  exactly what setup wrote; if someone edited it, setup leaves their version and the
  step says what to do). Those steps report `undone`. A key created before the failure
  stays in its reserved secret, bound to nothing, and the retry reuses it. A failure
  after setup (the managed rule, the settings write) leaves the completed steps in
  place, and a retry completes the enable.
- **One enable per organization at a time.** A second enable while one is running (a
  double click, a retry) is refused with `409` and `setup_in_progress` before it
  writes anything. A lease left by a crashed enable lapses after 10 minutes.
- **The refusal carries the step's own code.** The answer's top-level `error_code` is
  the failed step's (`credential_permissions`, `credential_missing`,
  `recipe_not_found`, `setup_in_progress`, `setup_unavailable`, ...), with the HTTP
  status and retry rule of its class (`error_class`). The steps stay in the answer.

### Keys from earlier releases

A key created before 2026-11-21 had a shorter, fixed list that lacked `ext.request`,
`mailsec.act`, `output.set`, `sensor.tag` and `sensor.task`, and later keys held one
broad list for every source. The readiness check reports what such a key lacks for its
template, and re-running setup replaces it with the template's set.

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
