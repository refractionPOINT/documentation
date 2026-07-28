# Cloudflare

The Cloudflare LimaCharlie Extension gives D&R rules and AI agents access to the Cloudflare v4 API. This API is the incident-response and investigation surface of a Cloudflare account or zone. The extension automates containment at the edge and in Zero Trust directly from detections, with no separate SOAR. You can block a malicious source at the WAF or revoke the sessions of a Zero Trust Access user. You can also add IOCs to a Gateway block list, purge the cache, or correct a hijacked DNS record.

The extension has two layers:

- **Typed actions** for the common containment, triage, and investigation workflows. They use clear parameter names and include safety checks.
- A generic **`api_call`** passthrough for each Cloudflare v4 endpoint without a typed action. This includes non-enveloped endpoints such as the GraphQL Analytics API.

Authentication uses a scoped **API Token** (Bearer) or the legacy **Global API Key**. Both are static and need no user interaction.

## Setup

### 1. Create an API Token

In the Cloudflare dashboard (**My Profile → API Tokens**, or **Account Home → Manage Account → API Tokens**), create a token. Grant only the permission groups for the actions that you use. Scope the token to the specific account and/or zone, not to "all accounts / all zones". The least-privilege set for each capability:

| Capability | Permission group (Read/Edit) | Scope |
| --- | --- | --- |
| IP Access Rules (account) | Account Firewall Access Rules — Edit | Account |
| IP Access Rules (zone) | Firewall Services — Edit | Zone |
| WAF custom rules / rulesets | Account WAF / Zone WAF + Rulesets — Edit | Account / Zone |
| Zero Trust Access (users, sessions, policies) | Access: Apps and Policies + Access: Organizations, Identity Providers, and Groups — Edit | Account |
| Gateway lists & rules | Zero Trust — Edit | Account |
| DNS read / edit | DNS — Read / Edit | Zone |
| Cache purge | Cache Purge — Purge | Zone |
| Audit log | Logs — Read | Account |
| Firewall events (GraphQL) | Account Analytics — Read | Account |
| Account members | Account Membership — Edit | Account |

Add only the permission groups that you use. If a valid token does not have a permission group, that endpoint returns `403`. This is a scope problem, not a bad token. To get the current names and IDs of the permission groups at setup, call `GET /accounts/{account_id}/tokens/permission_groups`.

A legacy **Global API Key** also works (your account email plus the key). The key has full account access and you **cannot scope** it, so use a token instead.

### 2. Subscribe to the extension

Subscribe to `ext-cloudflare` from the LimaCharlie **Marketplace** (Extensions → Add-Ons).

### 3. Store the secret

In **Secrets Manager**, create a new secret (for example `cloudflare-api-token`) and paste the API token (or Global API Key) as its value.

### 4. Configure the extension

In **Extensions → ext-cloudflare → Configuration**, fill in:

| Field | Required | Value |
| --- | --- | --- |
| `api_token` | one auth mode | Reference to the API token secret, e.g. `hive://secret/cloudflare-api-token`. |
| `email` | legacy only | Account email for legacy Global API Key auth (paired with `api_key`). |
| `api_key` | legacy only | Reference to the Global API Key secret (paired with `email`). |
| `account_id` | no | Default account id for account-scoped actions. Any action can override it. |
| `zone_id` | no | Default zone id for zone-scoped actions. Any action can override it. |

Give **either** `api_token` **or** `email` + `api_key`, but not both.

## Scoping: account vs zone

Cloudflare resources are **account-scoped** or **zone-scoped**. Set the default `account_id` and `zone_id` in the configuration. Any action can override them in each request.

- **Account-scoped:** Zero Trust Access, Gateway, account members, the audit log.
- **Zone-scoped:** DNS records, cache purge.
- **Either:** IP Access Rules and WAF custom rules accept `account_id` **or** `zone_id`. Account scope applies to *all* the zones in the account, and zone scope applies to one zone. Pass exactly one. If you pass both, the extension rejects the request as ambiguous. If you pass neither, the extension uses the defaults from the configuration and **prefers the zone**, because the zone has the smaller effect.

## Actions

Every action that targets an entity needs an explicit selector. A selector is an `ip`, `asn`, or `country`, a `rule_id`, an `email`, a `list_id` with `values`, a `dns_record_id`, a `member_id`, and so on. The extension refuses to run without a selector. This stops an accidental response across the full account. `purge_cache` also refuses to run unless you choose exactly one purge mode.

Typed list actions return `{data: [...], pagination: {...}}`. The `pagination` field holds Cloudflare's `result_info` without change: the offset fields (`page`, `per_page`, `total_pages`, …) or a `cursor`. To page, increase `page` until `page == total_pages`, or send the `cursor` back. The maximum value of `per_page` is 100.

### Generic

#### `api_call`

Generic passthrough to any Cloudflare v4 endpoint.

| Field | Type | Notes |
| --- | --- | --- |
| `method` | enum | `GET` (default), `POST`, `PUT`, `PATCH`, `DELETE`. |
| `path` | string | **Required.** Path relative to `https://api.cloudflare.com/client/v4` (e.g. `zones/{zone_id}/dns_records`, or `graphql` for the GraphQL Analytics API) or a full URL. |
| `query` | object | Query-string parameters. |
| `headers` | object | Extra request headers. |
| `body` | object | JSON body for `POST`/`PUT`/`PATCH`. |

Returns the full response body without change: the `{success, errors, result, result_info}` envelope, or the raw structure for non-enveloped endpoints such as GraphQL.

### Investigation (reads)

| Action | Parameters | What it does |
| --- | --- | --- |
| `verify_token` | — | Check the configured API token (health check). Returns the status of the token. |
| `list_accounts` | `name`, `page`, `per_page`, `extra_query` | List the accounts that the credential can see. Use it to find an `account_id`. |
| `list_zones` | `name`, `account_id`, `status`, `page`, `per_page`, `extra_query` | List or search zones. Use it to find a `zone_id`. |
| `list_ip_access_rules` | `account_id`/`zone_id`, `target`, `value`, `mode`, `page`, `per_page` | List IP Access Rules. Use a returned rule id with `remove_ip_access_rule`. |
| `list_dns_records` | `zone_id`, `type`, `name`, `content`, `page`, `per_page` | List the DNS records of a zone. Use a returned id with `edit_dns_record` or `delete_dns_record`. |
| `list_access_users` | `account_id`, `email`, `name`, `search`, `page`, `per_page` | List Zero Trust Access users. |
| `get_access_user_activity` | `account_id`, `user_id`, `kind` | Get the `active_sessions`, `last_seen_identity`, or `failed_logins` of an Access user. |
| `list_gateway_lists` | `account_id`, `page`, `per_page` | List Zero Trust Gateway lists. Use it to find a `list_id`. |
| `list_members` | `account_id`, `status`, `page`, `per_page` | List the members of the account. Use a returned membership id (`result[].id`, **not** `user.id`) with `remove_member`. |
| `get_audit_logs` | `account_id`, `since`, `before`, `action_type`, `actor_email`, `limit`, `cursor`, `direction` | Query the audit log of the account (v2, cursor-paginated). The v2 API needs a `since`+`before` window. If you omit the window, the default is the last 7 days. Pass the same explicit window for each page to keep pagination stable. |
| `search_firewall_events` | `zone_id`, `since`, `until`, `client_ip`, `action`, `limit` | Search the WAF and firewall events of a zone with the GraphQL Analytics API (`firewallEventsAdaptive`). The counts are sampled. The window depends on the plan (~31 days). |
| `get_waf_custom_ruleset` | `account_id`/`zone_id` | Get the `http_request_firewall_custom` phase ruleset. Its id is the `ruleset_id` for `add_waf_custom_rule`. |

### Edge / WAF containment

| Action | Parameters | What it does |
| --- | --- | --- |
| `block_ip` | `ip`, `account_id`/`zone_id`, `mode`, `notes` | Block one IP (v4/v6) with an IP Access Rule. |
| `block_ip_range` | `range`, `account_id`/`zone_id`, `mode`, `notes` | Block a CIDR range (IPv4 /16 or /24; IPv6 /32, /48, /64). |
| `block_asn` | `asn`, `account_id`/`zone_id`, `mode`, `notes` | Block an ASN (bare AS number, no `AS` prefix). |
| `block_country` | `country`, `account_id`/`zone_id`, `mode`, `notes` | Block a country (ISO-3166-1 alpha-2). |
| `remove_ip_access_rule` | `rule_id`, `account_id`/`zone_id` | Delete an IP Access Rule (undo a block) at the scope where it was created. |
| `add_waf_custom_rule` | `expression`, `account_id`/`zone_id`, `action`, `description`, `ruleset_id` | Add a WAF custom rule (wirefilter `expression`, e.g. `(ip.src eq 198.51.100.4)`). If you omit `ruleset_id`, the extension finds the custom-phase ruleset. |

The default `mode` for the block actions is `block`. To change it, use `challenge`, `managed_challenge`, `js_challenge`, or `whitelist` (an allow-list entry). An account-scoped rule applies to *all* the zones in the account.

### Zero Trust containment

| Action | Parameters | What it does |
| --- | --- | --- |
| `revoke_access_user` | `email`, `account_id`, `revoke_devices` (default `true`), `warp_session_reauth` | Revoke the sessions of a Cloudflare Access user (by email). `revoke_devices` also ends the device and WARP sessions. |
| `gateway_add_to_blocklist` | `list_id`, `values`, `account_id` | Add IOCs (domains, IPs, URLs, … as the list type allows) to a Zero Trust Gateway list. |
| `gateway_remove_from_blocklist` | `list_id`, `values`, `account_id` | Remove IOCs from a Gateway list (undo). |

`revoke_access_user` propagates in about 1 minute and does **not** disable the upstream IdP identity. For a durable block, also disable the identity in the IdP or add a `deny` Access policy with `api_call`. A Gateway list enforces nothing until you add it to a Gateway block rule.

### DNS / cache response

| Action | Parameters | What it does |
| --- | --- | --- |
| `edit_dns_record` | `dns_record_id`, `zone_id`, `content`, `name`, `type`, `ttl`, `proxied`, `comment` | Update part of a DNS record (only the fields that you set change). For example, point a hijacked record to a sinkhole. |
| `delete_dns_record` | `dns_record_id`, `zone_id` | Delete a DNS record. For example, remove a record that an attacker created. |
| `purge_cache` | `zone_id`, `purge_everything`, `files`, `hosts`, `tags`, `prefixes` | Purge cache. Choose **exactly one** mode: `purge_everything=true`, or one of `files` / `hosts` / `tags` / `prefixes` (`hosts`/`tags`/`prefixes` are Enterprise-only). |

### Account containment

| Action | Parameters | What it does |
| --- | --- | --- |
| `remove_member` | `member_id`, `account_id` | Remove a member from the account. Use the membership id (`result[].id` from `list_members`, **not** `user.id`). To downgrade a member instead of removing the member, use `api_call` to send a `PUT` with a read-only role. |

## Detection & Response

This example response action blocks the source IP from a detection at the Cloudflare edge:

```yaml
- action: extension request
  extension action: block_ip
  extension name: ext-cloudflare
  extension request:
    ip: '{{ .event/SOURCE_IP }}'
    zone_id: '{{ "<your-zone-id>" }}'
    notes: '{{ "Blocked by LimaCharlie D&R rule" }}'
```

> **Wrap literal strings in `{{ "..." }}`.**
> The extension evaluates the values under `extension request` as templates. A bare string without `{{ }}` is a [gjson](https://github.com/tidwall/gjson) path into the event. If the path does not resolve, the extension drops the key from the payload without a message.

`extension request` actions do not return a result. The rule engine does not put the response into the evaluation context of the rule. Put chained workflows in a [Playbook](../limacharlie/playbook.md) or an AI agent, because these can keep ids between calls. A chained workflow is, for example: find the zone, block the IP, then confirm the block.

## Notes

- **`success: false` is an error.** On a logical error, Cloudflare often answers `200` with `success: false`. The extension treats this as a failure and shows the Cloudflare error code and message. A typed action never reports a no-op as a success.
- **IP Access Rule scope matters.** An account-scoped rule applies to *all* the zones in the account, and a zone-scoped rule applies to one zone. `remove_ip_access_rule` must delete the rule at the scope where you created it.
- **`revoke_access_user` is not a durable block.** It ends the current sessions, but it does not disable the IdP identity. Also disable the identity in the IdP or add a `deny` policy.
- **Purge is explicit.** `purge_cache` needs exactly one mode. You must set `purge_everything` to `true` yourself. `tags`/`hosts`/`prefixes` are Enterprise-only.
- **User API tokens can't be revoked cross-member.** The token-revocation endpoint of Cloudflare is user-scoped. To contain a different member, use `remove_member`, or downgrade the member with `api_call`.
- **Secret rotation recovers automatically.** A `401`, or a `403`/`400` with the Cloudflare authentication error code `10000`, removes the cached client. The extension then re-reads the secret from Secrets Manager on the next call. A `403` from a missing permission is *not* an authentication failure. Error messages have the format `cloudflare api error <status> on <method> <path>: <code> <message>` (`cloudflare auth error …` for authentication failures), with query strings redacted.
- If you unsubscribe from the extension, the saved configuration stays. If you subscribe again, the extension restores the configuration and you do not configure it again.
