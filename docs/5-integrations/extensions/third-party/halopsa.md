# HaloPSA

MSPs use [HaloPSA](https://halopsa.com/) for ticketing, asset management, and time tracking. It is a professional services automation platform.

The HaloPSA LimaCharlie Extension gives outbound HaloPSA actions to D&R rules and AI agents. These actions cover the ticket lifecycle (create, update, and search), notes, and billable time entries. They also link LC sensor telemetry to assets in the MSP CMDB, and look up clients and sites.

## Setup

### 1. Create a HaloPSA API application

In HaloPSA, create an API application under **Configuration → Integrations → HaloPSA API**. Configure it for the OAuth2 `client_credentials` flow:

- **Authentication Method:** Client ID and Secret (Services)
- **Login Type:** Log on as **Agent**. Select the HaloPSA agent that owns the tickets, actions, and assets that this extension creates.
- **Permissions:** grant `edit:tickets`, `edit:assets`, and `read:customers`

These three scopes are the verified least-privilege set for the six actions below:

- `edit:tickets` covers `create_ticket`, `update_ticket`, `search_tickets`, and `add_action`. An action is a sub-resource of a HaloPSA ticket. There is no separate `read:actions` or `edit:actions` scope; the HaloPSA token endpoint rejects them as `invalid_scope`.
- `edit:assets` covers asset lookup and the create-if-missing path in `link_asset_to_ticket`.
- `read:customers` covers `lookup_client_site` for both clients *and* sites (a site is a sub-resource of a customer). The extension never writes clients or sites, so you do not need `edit:customers`.

If you do not want to list the scopes, the default of `all` in the extension also works.

Copy the **Client ID** and the **Client Secret**. You need them in the next step. For the current path in the UI, see the HaloPSA product documentation. The labels above can differ between HaloPSA versions.

### 2. Subscribe to the extension

Subscribe to `ext-halopsa` from the LimaCharlie **Marketplace** (Extensions → Add-Ons).

### 3. Store the client secret

In **Secrets Manager**, create a new secret, for example `halopsa-client-secret`. Paste the HaloPSA Client Secret as its value.

### 4. Configure the extension

In **Extensions → ext-halopsa → Configuration**, fill in:

| Field | Value |
| --- | --- |
| `instance_url` | The URL of your HaloPSA tenant, for example `https://acme.halopsa.com` |
| `client_id` | The Client ID from step 1 |
| `client_secret` | A reference to the secret from step 3, for example `hive://secret/halopsa-client-secret` |
| `tenant` | (optional) Tenant identifier. Needed only on hosted deployments with shared authentication |
| `scope` | (optional) OAuth2 scopes, separated by spaces. Defaults to `all`. |

At save time, the configuration is validated against `instance_url`, `client_id`, and `client_secret`. If the OAuth2 token cannot be obtained, requests show a `401` from the upstream HaloPSA API.

## Actions

The extension gives six actions. Each action accepts a JSON request body when a D&R rule calls it with `extension request`.

### `create_ticket`

Open a new ticket. Only `summary` is required.

| Field | Type | Notes |
| --- | --- | --- |
| `summary` | string | **Required.** Ticket subject line. |
| `details` | string | Ticket body. |
| `client_id` | int | HaloPSA client (company) id. |
| `site_id` | int | HaloPSA site id. |
| `user_id` | int | End-user id (ticket requester). |
| `agent_id` | int | Agent id (assignee). |
| `team` | string | Team name. |
| `tickettype_id` | int | Ticket type id (Incident, Change, …). |
| `priority_id` | int | Priority id. |
| `status_id` | int | Initial status id. |
| `impact` | int | ITIL impact (1=high … 4=low). |
| `urgency` | int | ITIL urgency (1=high … 4=low). |
| `category_1` | string | Top-level category. |
| `parent_id` | int | Parent ticket id (for sub-tickets). |
| `asset_ids` | list of int | Asset ids to attach. |
| `customfields` | list of object | Each entry `{name\|id, value}`. |
| `extra` | object | Raw HaloPSA ticket fields to merge into the request. Use it for fields that the list above does not model. |

Returns the new ticket and its assigned `id`.

### `update_ticket`

Update an existing ticket. Use this action to change the status, to reassign the ticket, to set the priority, or to set the linked assets. A status change drives the HaloPSA status → outcome → workflow transitions.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | int | **Required.** Ticket id to update. |
| `summary` | string | New summary. |
| `details` | string | New body. |
| `status_id` | int | New status id. |
| `agent_id` | int | New assignee. |
| `priority_id` | int | New priority. |
| `asset_ids` | list of int | **Replaces** the asset list of the ticket. Use `link_asset_to_ticket` to merge a new asset into the existing list. |
| `customfields` | list of object | Custom fields to set. |
| `extra` | object | Raw HaloPSA ticket fields to merge. |

### `search_tickets`

Search tickets or list them. Use this action to avoid duplicates before you create a ticket, or to find existing work for an asset.

| Field | Type | Notes |
| --- | --- | --- |
| `search` | string | Free-text search across the summary and the details of a ticket. |
| `client_id` | int | Restrict to a client. |
| `agent_id` | int | Restrict to an assignee. |
| `status_ids` | string | Status ids, separated by commas. |
| `tickettype_id` | int | Restrict to a ticket type. |
| `page_size` | int | Default `50`. |
| `page_no` | int | Default `1` (1-based). |
| `order` | string | Order-by field (for example `id`). |
| `orderdesc` | bool | Descending order. |

Returns `{ "record_count": N, "tickets": [...] }`.

### `add_action`

Append a HaloPSA Action to a ticket. The Action is a private note (agents only) or a public reply that the end-user sees. It can also carry billable time. AI agents can use this action to record triage findings and work time.

| Field | Type | Notes |
| --- | --- | --- |
| `ticket_id` | int | **Required.** Ticket id to append to. |
| `note` | string | **Required.** Content of the note or the reply. |
| `hiddenfromuser` | bool | `true` (default) = private; `false` = public reply. |
| `timetaken` | int | Time taken on this action (whole hours only). For fractional hours, use `extra.timetaken`. |
| `actionchargehours` | int | Billable hours (whole hours only). For fractional hours, use `extra.actionchargehours`. |
| `outcome` | string | Outcome label (drives HaloPSA workflow transitions). Defaults to `Note`. |
| `extra` | object | Raw HaloPSA action fields to merge. |

> The default is **private** (`hiddenfromuser=true`), so that security notes do not go to end-users by accident. For a public reply, set `hiddenfromuser: false`.

### `link_asset_to_ticket`

Resolve a hostname to a HaloPSA asset under the given client or site, then attach the asset to the ticket. The action can also create the asset if it does not exist. This action links LC sensor telemetry to the MSP CMDB.

| Field | Type | Notes |
| --- | --- | --- |
| `ticket_id` | int | **Required.** Ticket id to link the asset to. |
| `hostname` | string | **Required.** Hostname to resolve. The match uses `inventory_number` or `key_field`. |
| `client_id` | int | Required when the asset must be created. |
| `site_id` | int | Used on asset create. |
| `asset_type_id` | int | Required when the asset must be created (HaloPSA rejects asset creates without an asset type). |
| `create_if_missing` | bool | If `true` (default), create the asset when there is no match. |

Returns `{ "asset_id": N, "asset_created": bool, "asset": {...}, "ticket": {...} }`. The link is idempotent. If you run the action again on an asset that is already linked, it makes no duplicates.

### `lookup_client_site`

Resolve a HaloPSA client id or site id from a name. AI agents use this action to map an LC org to a Halo client.

| Field | Type | Notes |
| --- | --- | --- |
| `type` | enum | **Required.** `client` or `site`. |
| `search` | string | Name match. |
| `client_id` | int | Restrict sites to a client (only when `type=site`). |
| `page_size` | int | Default `50`. |
| `page_no` | int | Default `1`. |

Returns `{ "record_count": N, "clients": [...] }` or `{ "record_count": N, "sites": [...] }`, based on `type`.

## Detection & Response

This example response action opens a HaloPSA ticket for a detection:

```yaml
- action: extension request
  extension action: create_ticket
  extension name: ext-halopsa
  extension request:
    summary: '{{ .cat }} - {{ .routing.hostname }}'
    details: '{{ .event }}'
    client_id: 12
    site_id: 18
    tickettype_id: 1
    priority_id: 3
```

> **Wrap literal strings in `{{ "..." }}`.**
> The values under `extension request` are evaluated as templates. A bare string without `{{ }}` is read as a [gjson](https://github.com/tidwall/gjson) path into the event. If the path does not resolve, the key is dropped from the payload without a message.

`extension request` actions do not return a result. The rule engine does not put the response into the evaluation context of the rule. The id of the new ticket is therefore not available to a later action in the same rule. A workflow that must chain steps (open a ticket, link an asset, then add a note) belongs in a [Playbook](../limacharlie/playbook.md) or in an AI agent. A Playbook or an AI agent can hold the ticket id between calls.

Use `add_action` to append triage findings to an existing ticket. For example, a Playbook or an AI agent that already knows the ticket id can call it:

```yaml
- action: extension request
  extension action: add_action
  extension name: ext-halopsa
  extension request:
    ticket_id: 2884
    note: '{{ .routing.hostname }}: suspicious process tree observed. See LC for details.'
    hiddenfromuser: true
    timetaken: 1
    outcome: '{{ "Note" }}'
```

## Notes

- HaloPSA returns an OAuth2 access token. The token is cached for each `(org, instance_url, client_id, secret)` for the lifetime of a client. If you rotate the secret in the Secrets Manager, the next `401` evicts the cached client.
- `actionchargehours` results in a billable charge only if the tenant has a charge rate for the agent that posts the action. If there is no charge rate, HaloPSA accepts the value but reports `Charge Rate: No Charge`.
- HaloPSA keeps the main body of a ticket as the first entry in its action timeline. `update_ticket.details` replaces that first entry. It does not change a separate body field.
