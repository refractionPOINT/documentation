# Reference: Permissions

## Overview

LimaCharlie uses a granular permission system that controls access to all platform functionality. Permissions are applied through User accounts, API Keys, or Groups and follow a hierarchical naming convention: `category`.`action`

## Permission Structure

### Naming Convention

- **Category**: Functional area (e.g. sensor, org, dr)
- **Action**: Operation type (e.g. get, list, set, del, ctrl)

## Core Permissions

### Organization Management

| Permission | Description |
| --- | --- |
| org.get | View organization information |
| org.del | Delete organization |
| org.set\_quota | Manage organization quotas |
| org.conf.get | View organization configuration |
| org.conf.set | Modify organization configuration |

### User & Access Control

| Permission | Description |
| --- | --- |
| apikey.ctrl | Create, delete, and modify API keys |
| user.ctrl | Manage user accounts and permissions |
| billing.ctrl | Access and modify billing information |
| acl.get | View [Resource ACL](../7-administration/access/resource-acls.md) scopes and the resources tagged with them |
| acl.set | Manage Resource ACL scopes and add or remove `acl:` tags. Does not grant read access to restricted content |

Unlike most hive permissions, these have no per-record form: `acl.set.<scope>` grants nothing.

### Sensor Management

| Permission | Description |
| --- | --- |
| sensor.list | List all sensors in organization |
| sensor.get | View detailed sensor information |
| sensor.task | Send commands and tasks to sensors |
| sensor.del | Delete sensors |
| sensor.tag | Manage sensor tags and labels |

### Installation Keys

| Permission | Description |
| --- | --- |
| ikey.list | List installation keys |
| ikey.set | Create new installation keys |
| ikey.del | Delete installation keys |

### Detection & Response (D&R)

#### General D&R Rules

| Permission | Description |
| --- | --- |
| dr.list | List general detection rules |
| dr.set | Create and modify general detection rules |
| dr.del | Delete general detection rules |

#### Managed D&R Rules

| Permission | Description |
| --- | --- |
| dr.list.managed | List managed detection rules |
| dr.set.managed | Create and modify managed detection rules |
| dr.del.managed | Delete managed detection rules |

#### Service D&R Rules

| Permission | Description |
| --- | --- |
| dr.list.service | List service detection rules |
| dr.set.service | Create and modify service detection rules |
| dr.del.service | Delete service detection rules |

#### False Positives

| Permission | Description |
| --- | --- |
| fp.ctrl | Manage false positive suppressions |

## Configuration Management (Hive)

### Secrets

| Permission | Description |
| --- | --- |
| secret.get | Access secret values |
| secret.set | Create and modify secrets |
| secret.del | Delete secrets |
| secret.get.mtd | View secret metadata only |
| secret.set.mtd | Modify secret metadata only |

### Lookups

| Permission | Description |
| --- | --- |
| lookup.get | Access lookup tables |
| lookup.set | Create and modify lookup tables |
| lookup.del | Delete lookup tables |
| lookup.get.mtd | View lookup metadata only |
| lookup.set.mtd | Modify lookup metadata only |

### Models

| Permission | Description |
| --- | --- |
| model.get | Access behavioral models |
| model.set | Create and modify behavioral models |
| model.del | Delete behavioral models |
| model.get.mtd | View model metadata only |
| model.set.mtd | Modify model metadata only |

### Queries

| Permission | Description |
| --- | --- |
| query.get | Access saved queries |
| query.set | Create and modify saved queries |
| query.del | Delete saved queries |
| query.get.mtd | View query metadata only |
| query.set.mtd | Modify query metadata only |

### YARA Rules

| Permission | Description |
| --- | --- |
| yara.get | Access YARA rules |
| yara.set | Create and modify YARA rules |
| yara.del | Delete YARA rules |
| yara.get.mtd | View YARA rule metadata only |
| yara.set.mtd | Modify YARA rule metadata only |

### AI Agents

| Permission | Description |
| --- | --- |
| ai\_agent.get | Access AI agent configurations |
| ai\_agent.set | Create and modify AI agents |
| ai\_agent.del | Delete AI agents |
| ai\_agent.get.mtd | View AI agent metadata only |
| ai\_agent.set.mtd | Modify AI agent metadata only |
| ai_agent.exec | Launch a configured AI agent through a UI action |
| ai_agent.operate | Allow an AI agent to operate on this organization using the authenticated identity's permissions |

#### `ai_agent.exec`: launch a configured agent

Grant `ai_agent.exec` to the **user or API key invoking an AI agent UI action**.
It authorizes execution of an existing `ai_agent` Hive record. Reading, editing,
and deleting that configuration use the separate `.get`, `.set`, and `.del`
permissions above; those permissions do not substitute for `.exec`.

Launching a configured agent creates an AI Session that continues in the
background. The agent uses the LimaCharlie credentials configured in the record
(for example, through `lc_api_key_secret`). Its organization access is determined
by those credentials, which can differ from the caller's permissions.

Treat execution access as permission to initiate the configured workflow: an
agent with response privileges may make changes even when the person launching
it has no direct response privileges. Review the agent's prompt and credentials
before granting execution access. [Resource ACLs](../7-administration/access/resource-acls.md)
can additionally restrict access to a particular agent record.

This permission specifically covers launching a configured agent through a UI
action. It is not a blanket requirement for every way of creating a session;
[user sessions](../9-ai-sessions/user-sessions.md) and
[D&R-driven sessions](../9-ai-sessions/dr-sessions.md) have their own setup and
authentication requirements.

#### `ai_agent.operate`: allow agent access to an organization

Grant `ai_agent.operate` to the **identity the AI agent uses to access LimaCharlie**:
its organization API key, or the user whose credentials it uses. This permission
is organization-scoped. Access to one organization does not authorize AI
operations on another organization.

`ai_agent.operate` is an additional gate for AI access, including read-only
operations. It does not grant access to telemetry, sensors, configurations, or
response actions by itself. The identity also needs each operation's normal API
permission. For example:

| Agent task | Permissions on the agent's identity |
| --- | --- |
| List sensors | `ai_agent.operate`, `sensor.list` |
| Read historical detections | `ai_agent.operate`, `insight.det.get` |
| Read CloudSec posture and findings | `ai_agent.operate`, `cloudsec.get` |
| Read MailSec messages and campaigns | `ai_agent.operate`, `mailsec.get` |

These are task-specific examples, not complete permission sets for an entire
investigation. Add the permissions needed for the other operations in your
workflow, and grant write permissions only when the agent needs to make changes.

Managed AI Sessions instruct the agent to verify `ai_agent.operate` before its
first operation on each organization and refuse to operate when it is missing.
The [MCP server](../6-developer-guide/mcp-server.md#permission-enforcement) also
enforces this permission by default for organization-scoped tools, with explicit
exceptions such as AI generation tools. This is an AI access control; it does not
replace the normal permissions enforced by the REST API.

#### Choosing which identity gets each permission

| Workflow | Caller launching the workflow | Identity used by the agent |
| --- | --- | --- |
| Analyst launches an existing agent UI action | `ai_agent.exec` | `ai_agent.operate` plus permissions for the configured workflow |
| User works interactively in an AI Session | Follow the user-session authentication setup | `ai_agent.operate` on each target organization plus task permissions |
| External AI assistant connects through MCP | Follow the MCP authentication setup | `ai_agent.operate` plus permissions for the requested tools |
| D&R rule starts an automated agent | Follow the D&R session setup | `ai_agent.operate` plus task permissions on the configured LimaCharlie credentials |

Neither permission implies the other. An agent does not need `ai_agent.exec`
merely to read detections through MCP, and a caller's `ai_agent.exec` does not
supply `ai_agent.operate` to the credentials inside a launched session.

#### Troubleshooting access

| Symptom | What to check |
| --- | --- |
| Launching an agent UI action is denied | Check `ai_agent.exec` on the caller in the target organization, and any Resource ACL on the agent record. |
| A session opens, but the agent refuses organization operations | Check `ai_agent.operate` on the credentials actually used inside the session, for that specific organization. |
| MCP reports missing `ai_agent.operate` | Check the MCP connection's API key or authenticated user's permissions in the target organization. |
| The agent passes the AI permission check, but an operation is denied | Check the operation's normal API permission and any applicable Resource ACL. |
| A tool is unavailable or requires approval | Check the MCP profile and session tool settings; these are separate from organization permissions. |

Assign permissions through [User Access](../7-administration/access/user-access.md)
or [API Keys](../7-administration/access/api-keys.md). Session settings such as
`allowed_tools`, `denied_tools`, and `permission_mode` control tool execution and
approval; they do not grant organization API permissions. See
[Tool Permissions & Profiles](../9-ai-sessions/tool-permissions.md).


### Cloud Sensors

| Permission | Description |
| --- | --- |
| cloudsensor.get | Access cloud sensor configurations |
| cloudsensor.set | Create and modify cloud sensor configurations |
| cloudsensor.del | Delete cloud sensor configurations |
| cloudsensor.get.mtd | View cloud sensor metadata only |
| cloudsensor.set.mtd | Modify cloud sensor metadata only |

### Playbooks

| Permission | Description |
| --- | --- |
| playbook.get | Access playbooks |
| playbook.set | Create and modify playbooks |
| playbook.del | Delete playbooks |
| playbook.get.mtd | View playbook metadata only |
| playbook.set.mtd | Modify playbook metadata only |

### SOPs

| Permission | Description |
| --- | --- |
| sop.get | Access Standard Operating Procedures |
| sop.set | Create and modify SOPs |
| sop.del | Delete SOPs |
| sop.get.mtd | View SOP metadata only |
| sop.set.mtd | Modify SOP metadata only |

### Organization Notes

| Permission | Description |
| --- | --- |
| org_notes.get | Access organization notes |
| org_notes.set | Create and modify organization notes |
| org_notes.del | Delete organization notes |
| org_notes.get.mtd | View organization note metadata only |
| org_notes.set.mtd | Modify organization note metadata only |

### Apps

| Permission | Description |
| --- | --- |
| app.get | Access app records |
| app.set | Create and modify app records |
| app.del | Delete app records |
| app.get.mtd | View app metadata only |
| app.set.mtd | Modify app metadata only |

### External Adapters

| Permission | Description |
| --- | --- |
| externaladapter.get | Access external adapter configurations |
| externaladapter.set | Create and modify external adapters |
| externaladapter.del | Delete external adapter configurations |
| externaladapter.get.mtd | View external adapter metadata only |
| externaladapter.set.mtd | Modify external adapter metadata only |

## Extensions & Services

### Extensions

| Permission | Description |
| --- | --- |
| ext.request | Request extension actions |
| ext.conf.get | View extension configurations |
| ext.conf.set | Modify extension configurations |
| ext.conf.del | Delete extension configurations |
| ext.conf.get.mtd | View extension metadata only |
| ext.conf.set.mtd | Modify extension metadata only |
| ext.sub | Subscribe to extension services |
| ext.sub.mtd | Manage extension subscription metadata |

### Replicant Services

| Permission | Description |
| --- | --- |
| replicant.get | View replicant service status |
| replicant.ctrl | Control replicant services |

## Data Access & Analytics

### Insight & Detections

| Permission | Description |
| --- | --- |
| insight.list | List available insights |
| insight.ctrl | Control insight generation |
| insight.del | Delete insights |
| insight.evt.get | Access detailed event data |
| insight.evt.get.simple | Access simplified event data |
| insight.det.get | Access detection details |
| insight.stat | Access insight statistics |

### Audit & Logging

| Permission | Description |
| --- | --- |
| audit.get | Access audit logs and error messages |
| audit.set | Create audit logs entries |

## Operations Management

### Jobs

| Permission | Description |
| --- | --- |
| job.get | View job status and results |
| job.ctrl | Create and schedule jobs |

### Outputs

| Permission | Description |
| --- | --- |
| output.list | List output configurations |
| output.set | Create and modify output configurations |
| output.del | Delete output configurations |

### Payloads

| Permission | Description |
| --- | --- |
| payload.ctrl | Manage sensor payloads |

### Module Management

| Permission | Description |
| --- | --- |
| module.update | Update sensor modules |

### Ingestion

| Permission | Description |
| --- | --- |
| ingestkey.ctrl | Manage data ingestion keys |

## Permission Application

Permissions can be applied through:

1. **User Accounts**: Direct assignment to individual users
2. **API Keys**: Embedded in API key configurations for programmatic access
3. **Groups**: Assigned to groups, then inherited by group members

## Best Practices

1. **Principle of Least Privilege**: Grant only the minimum permissions required
2. **Use Groups**: Manage permissions through groups rather than individual assignments
3. **Regular Auditing**: Periodically review and audit permission assignments
4. **Separate Environments**: Use different permission sets for development, staging, and production
5. **API Key Management**: Rotate API keys regularly and scope them appropriately
