# Permissions

The Investigation Engine is checked at the API gateway, which requires the
permissions below. Beyond them, every read or action a run makes is authorized as the run's identity (see
[What a run can do](#what-a-run-can-do)). There are no approver lists.

!!! warning "Template and settings permissions are not part of any role"
    `investigation_plan.*` and `investigation_policy.*` are **not** in the Owner role
    or in any preset role. They are granted explicitly, to a person or to an API key.
    An Owner who has not been granted them is refused by the Hive when saving a
    template or the settings record.

## Using runs

The gateway requires **all** permissions of a row. A missing one is answered `401`
with `unauthorized: missing permission <name>`.

| To do this | Required permissions |
|---|---|
| Read runs, steps, the run graph, events, case documents, labels, templates, operators, fact packs, the settings as the engine enforces them, the run queue, the approvals inbox, the log of automatic actions and the authoring kit; validate a template; read test results | `investigation.get`, `insight.evt.get` |
| Start a run or a wave; add inputs; cancel, compare or delete a run; submit a label; flush the run queue; **test a template on past alerts** | `investigation.set`, `insight.evt.get` |
| Approve, deny, revert, extend or confirm an action; **undo an automatic action** | `investigation.set`, `insight.evt.get`, **and the permission of the action's class** (below) |
| Answer an AI agent step (from the agent's session) | `investigation.get`, plus the one-time answer token the engine gave the session |
| Bulk undo by selector (a route and a time range) | the above, plus `investigation_policy.set` |
| Read the performance stats; filter the run list by outcome or verdict | `investigation.get`, `insight.evt.get` (the console still shows its **Measure** page only to people who also hold `investigation_policy.set`) |

`insight.evt.get` is required everywhere because a run's results are what a search of
the organization's telemetry found: a role that can use Cases but cannot read
telemetry cannot read them through the engine either. Grant these permissions
explicitly to anyone who should use the engine, and check your roles: holding
`investigation.get` alone shows nothing.

### Permission of the action class

Deciding an action needs `investigation.set` plus the permission of what the action
does, because approving is how a person authorizes the engine to do it:

| Action | Additional permission |
|---|---|
| `contain.email` | `mailsec.act` |
| `contain.network`, `contain.seal`, `eradicate.file` | `sensor.task` |
| `tag`, `tag.add`, `tag.remove` | `sensor.tag` |
| `close.false_positive` | Nothing more for a case (the `investigation.set` every decision needs); `mailsec.set` for an email message, and for a close whose product is unknown |
| `playbook:<name>`, `extension:<name>/<action>` | `ext.request` |

An action with no mapping is refused (fail closed), and so is any decision on an
`extension:ext-playbook/...` action. Anyone holding these permissions may decide an
action: there are no approver lists. Which actions can execute is in
[What an action can do](actions.md#what-an-action-can-do).

### Who can see a run

A run belongs to the organization. Anyone with the read permissions sees all of the
organization's runs, and anyone with the write permissions can cancel, compare or
delete one. Only the identity that **started** a run can add inputs to it
(`403` otherwise); the steps the added inputs release run as the run's own identity.

## Templates and settings

Templates and the settings record are Hive records with the usual
[Config Hive](../7-administration/config-hive/index.md) permissions.

| To do this | Required permission |
|---|---|
| Read a template's record (its YAML) from the Hive | `investigation_plan.get`. Listing the templates the engine serves (`GET /templates`) needs only the run read permissions. |
| Create or edit templates, make a draft active | `investigation_plan.get`, `investigation_plan.set` |
| Delete templates | `investigation_plan.del` |
| Read or change template metadata only | `investigation_plan.get.mtd`, `investigation_plan.set.mtd` |
| Read, change or delete the settings record and its metadata (including the pause) | `investigation_policy.get`, `.set`, `.del`, `.get.mtd`, `.set.mtd` |
| Change what the AI may decide for a template | Editing the template (`ai_may_decide` is a key of the template) |
| Read or write organization fact packs (`investigation_pack` records) | The `investigation_plan.*` permissions above. A write must come from a person, or from an API key when the settings record is tagged `allow-api-key-promotion` |

Running a validation needs the read permissions, and a test the write permissions. A
test creates no run, case or action; its result is kept for 24 hours.

### Active templates can only be written by a person

A write that results in `status: active` is **refused when it comes from an API
key**, including an API key owned by a user. Only a person signed in as a user, in the
console or with an interactive login in the CLI (`limacharlie auth login --oauth`),
can create an active template, make a draft active or edit an active one. Demoting a
template to `draft` always works.

This is deliberate: an AI agent or a script holding an API key can write drafts but
cannot make a template start from a rule or act on its own.

An organization that manages active templates with API keys, for example from a
Git-synced pipeline, can opt out by adding the tag `allow-api-key-promotion` to the
enabled `investigation_policy/default` record. Setting that tag needs
`investigation_policy.set.mtd`, so **never give an AI agent's key any
`investigation_policy.*` permission**: it could turn the gate off and make its own
drafts active. If the settings record cannot be read, the write is refused.

!!! warning "Checks are not behind this gate"
    A [check](templates.md#checks-templates-other-templates-call) runs as it is stored,
    whatever its `status` (an active template that calls a draft check only gets the warning
    `check_is_draft`). So a key holding `investigation_plan.set` can change what an
    **active** template decides through a check it calls: an approval condition that reads
    the check, or a "check again" that releases a containment. Treat `investigation_plan.set`
    on a key as the power to change active templates' checks, review check edits like edits
    of active templates, and keep the checks your active templates call in the same
    reviewed source (Git) as the templates.

### Naming a secret as the run identity

The `identity` section of the settings record can name an organization API key
stored as a Hive secret, as `hive://secret/<name>`. Adding a **new** secret reference
requires that the person saving the record can read that secret (`secret.get`, or
`secret.get.<name>` within the secret's access scope), and the secret must already
exist. Only an organization API key can be a run identity: a user API key is refused
when the run starts. Granting `investigation_policy.set` therefore lets its holder
point runs at any secret they can read.

## What a run can do

A run executes with the permissions of its identity: the token of the person or key
that started it, or the API key the settings name. Everything it reads and every action
it takes is checked against those permissions; a run can never read or do what its
identity cannot. The gateway permissions above only get a call to the engine; each
operator then needs the permission of its own data source. Without it the step is
`unknown` (`forbidden`), never empty. A worked example of a run key is in
[step 2 of the walkthrough](walkthrough.md#2-the-key-the-engine-runs-as).

A **live sensor read** (`sensor.read.*`) tasks a sensor and needs `sensor.task.read`
(or the broader `sensor.task`) plus `output.set` on the identity. `sensor.task.read`
is an explicit grant, never part of a preset role. It permits only allowlisted live
metadata reads (processes, connections, autoruns, services, file hashes); file
contents, scripts, process termination, file deletion, isolation and unknown commands
are refused. For an observe-only identity, grant `sensor.task.read` instead of
`sensor.task` and write no `act` entry with `approval: none`.

## The key a template's runs use

A run without a person (started by a D&R rule or for a case) runs with the identity
the settings record names for its template: an **organization API key** stored as a
Hive secret (see [Naming a secret as the run identity](#naming-a-secret-as-the-run-identity)
and [Identity](settings.md#identity)). You create that key, store it as a
secret and name it in the settings, the same way in every organization, so it can be
deployed as code. The engine never creates, rotates or revokes a key.

### What the key needs

**The key needs what the template does, and nothing more.** An email-only template needs
no sensor permission. The set is worked out from the template, from a fixed table, so
the same template needs the same permissions in every organization. It adds up:

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

| Permission | What needs it |
|---|---|
| `cloudsec.get` | Entity, identity, cloud-security and code findings, and the endpoint click and coverage checks. |
| `ext.request` | Every run (writing the case); the reads of vulnerabilities and application control; Playbook steps; Playbook and extension actions. |
| `playbook.get` | Playbook steps and actions (the record is read before each call). |
| `ai_agent.get` | AI agent steps (the record is read before each start). |
| `insight.det.get` | Every run: the triggering detection; detection reads. |
| `insight.evt.get` | Telemetry reads and searches, process ancestry, prevalence, and the domain intelligence of link checks. |
| `investigation.get`, `investigation.set` | Every run: related cases, and the case close. |
| `lookup.get` | Your Lookups, including the trust lists. |
| `mailsec.act` | `contain.email`: quarantining a message and releasing it. |
| `mailsec.detonate` | Requesting a link detonation. |
| `mailsec.get` | Every Email Security read, the quarantine and the message close. |
| `mailsec.set` | Closing a message as a false positive, and undoing it. |
| `output.set` | The answer stream of live sensor reads (`sensor.read.*`) and of file eradication. |
| `sensor.get` | Sensor records: host state before isolation or tagging. |
| `sensor.list` | The sensor roster (`org.roster`). |
| `sensor.tag` | `tag`, `tag.add`, `tag.remove`. |
| `sensor.task` | `contain.network` (isolating a sensor and releasing it), `contain.seal`, file eradication and the live sensor reads. |

For the default library, a template's key needs:

| Template | Permissions |
|---|---|
| `appcontrol`, `cloud-exposure-finding` | `cloudsec.get`, `ext.request`, `insight.det.get`, `insight.evt.get`, `investigation.get`, `investigation.set` |
| `code-finding`, `identity-sign-in`, `saas-admin-action` | `cloudsec.get`, `ext.request`, `insight.det.get`, `investigation.get`, `investigation.set` |
| `endpoint-detection`, `suspicious-process` | The six of `appcontrol`, plus `lookup.get`, `output.set`, `sensor.get`, `sensor.tag`, `sensor.task` |
| `mailsec-message` | The six of `appcontrol`, plus `mailsec.act`, `mailsec.detonate`, `mailsec.get`, `mailsec.set` |
| `phishing-campaign` | The six of `appcontrol`, plus `mailsec.act`, `mailsec.get`, `mailsec.set`, `sensor.get`, `sensor.task` (it isolates the hosts that clicked) |

A template of your own needs the set its own steps and actions add up to. When one
secret is named for several templates (or as the org-wide `identity.default`, which
covers every template without its own entry), its key needs the permissions of all of
them.

These are ordinary LimaCharlie permissions, and they are the real limit on what a run
can do: there is no allow or deny list of operators or actions in the settings. **What
acts by itself is decided by the template's `act` entries**, inside the pause and the
circuit breaker. `limacharlie investigate settings get` checks each template's key before
its first run (`template_readiness`: `missing_grants`, and `needed_for` naming what needs
each one).

## ACL-scoped sensors

A sensor tagged `acl:<scope>` shows its content only to the members of that
[resource ACL scope](../7-administration/access/resource-acls.md). For a run on such a
sensor:

- the D&R rule that starts it must list the scope in `acl_scopes`, or the start is refused
  (see [Automatic Starts](automation.md#sensors-with-resource-acl-tags));
- the run's key must be a member of the scope (`hive://acl/<scope>` members). Otherwise its
  reads of that sensor are `unknown(acl_restricted)`, never "not found", and a detection
  read by its id is `unknown(not_found_or_restricted)`, with the scopes named. An undo on
  such a sensor fails with `acl_restricted` until the key is a member.

`settings get` lists per template the scopes its key is outside of
(`template_readiness.<template>.acl.outside_scopes`). It is a warning, not a refusal: a
key outside a scope works for every sensor that does not carry that scope's tag. A key
holding `access.global` is never gated.

**A run whose key lacks a permission is never broken without saying why.** A step the
platform refuses is `unknown` (`forbidden`), a case it cannot write is
`cases_access_denied` naming `ext.request`, and an action it refuses fails with a note
that starts `permission_denied:` and names the permissions the class needs.

## Console access

The console needs `investigation.get` **and** `insight.evt.get` to show the
Investigations section at all, and the automatic-actions log needs only those two to
read (**Undo** needs `investigation.set`). The **Measure** page needs
`investigation_policy.set` as well and is hidden without it. Controls the gateway would refuse are disabled with a
tooltip naming the permissions you need. See [Console](console.md).

## Keys: two limits to know

- An API key must have a key id to use the Investigation Engine. A key without one is
  refused on every route with `this API key has no key id, so it cannot own
  investigation runs`.
- An API key restricted to an IP range (`allowed_ip_range`) currently fails, because
  the engine presents the forwarded token from a different address.
