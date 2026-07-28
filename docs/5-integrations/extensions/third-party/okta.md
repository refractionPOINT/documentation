# Okta

The Okta LimaCharlie Extension gives D&R rules and AI agents access to the **Okta management API**. This API contains the incident-response and investigation functions of an Okta org. A detection can start an automated investigation or containment of a compromised Okta account. The extension can suspend a user, reset the MFA of the user, and stop the sessions **and** the OAuth tokens of the user. It can also revoke app grants, move the user into a quarantine group, and read the System Log for triage.

The extension has two layers:

- **Typed actions** for the usual workflows for containment, credentials, MFA, sessions, and triage. These actions have clear parameter names and built-in safety controls.
- A generic **`api_call`** passthrough for an Okta management endpoint that no typed action covers.

For authentication, use a user-owned **SSWS API token** or an **OAuth 2.0 "API Services" app** (client credentials). Neither mode needs user interaction or delegated tokens. The extension obeys the **DPoP** (sender-constrained token) requirement of Okta automatically.

## Setup

Select **one** authentication mode.

### Option A — SSWS API token (simplest)

1. In the Okta Admin Console, go to **Security → API → Tokens → Create Token**. Copy the token value. Okta shows the value one time only.
2. Create the token from a **dedicated service admin account**, not from the account of a person. An SSWS token gets the privilege level of the account that creates it. Okta revokes the token after 30 days of no activity, or if the account that created it is deactivated.

### Option B — OAuth API Services app (recommended)

1. In the Admin Console, go to **Applications → Create App Integration → API Services**.
2. On the **General** tab of the app, set client authentication to **Public key / Private key**. Generate a key or add one. Save the private key. The key is a PEM or the private JWK that Okta supplies.
3. On the **Okta API Scopes** tab of the app, grant the `okta.*` scopes for the actions that you use. The table below shows the least-privilege set. Then give admin consent to the scopes.

> **Okta needs `private_key_jwt` for management scopes.** The org authorization server rejects a plain `client_id` with a `client_secret` for `okta.*` scopes. Use a private key. The extension accepts a `client_secret` field, but Okta rejects it for these scopes. New API Services apps also have **DPoP** always enabled. The extension detects this and obeys it automatically.

Least-privilege scopes:

| Capability | Scope |
| --- | --- |
| Read users / lists | `okta.users.read` |
| User lifecycle / password / factor writes | `okta.users.manage` |
| Clear sessions / revoke tokens | `okta.sessions.manage` |
| Read groups | `okta.groups.read` |
| Group membership changes | `okta.groups.manage` |
| System Log | `okta.logs.read` |

> If you request a scope that is not granted, the org authorization server **removes it without a message** from the minted token. The mint does not fail. Instead, the endpoint returns **403** (`insufficient_scope`). Grant only the scopes that you use. Each action fails independently of the other actions.

### Subscribe to the extension

Subscribe to `ext-okta` from the LimaCharlie **Marketplace** (Extensions → Add-Ons).

### Store the secret

In **Secrets Manager**, create a secret, for example `okta-api-token` or `okta-private-key`. Set its value to the SSWS token or to the private key.

### Configure the extension

In **Extensions → ext-okta → Configuration**, complete `org_url` and the fields for your authentication mode:

| Field | Required | Value |
| --- | --- | --- |
| `org_url` | yes | Okta org URL or host, for example `https://acme.okta.com`. The extension normalizes admin and `-admin` URLs. |
| `api_token` | Option A | Reference to the secret that holds the SSWS token, for example `hive://secret/okta-api-token`. |
| `client_id` | Option B | The client ID of the API Services app. |
| `private_key` | Option B | Reference to the secret that holds the private key (PEM or private RSA JWK), for example `hive://secret/okta-private-key`. |
| `key_id` | no | The `kid` for a PEM private key. A JWK carries its own. |
| `client_secret` | no | Client secret of the app, as an alternative to `private_key`. Okta rejects it for management scopes. |
| `scopes` | no | Override for the OAuth scopes. If empty, the extension uses a default set for incident response. |

Give `api_token` **or** the OAuth fields, not both.

## Actions

Every action that targets an entity needs an explicit selector: `user_id`, `group_id` with `user_id`, or `factor_id`. The extension does not run without a selector. This stops accidental containment of the full org.

`user_id` accepts the Okta user id, for example `00u1a2b3c4...`, or the login of the user, for example `alex@acme.com`.

### Pagination

Okta paginates with the HTTP `Link` header (`rel="next"`), not with a cursor in the body. The `list_*` actions return `{data: [...], pagination: {next_link}}`. To get the next page, send the opaque `next_link` value back as the `next_link` parameter. The value is an absolute, self-contained URL. Do not build it yourself. The extension clamps `limit` to 200 for users and groups, and to 1000 for the System Log.

### Generic

#### `api_call`

Generic passthrough to the Okta management API.

| Field | Type | Notes |
| --- | --- | --- |
| `method` | enum | `GET` (default), `POST`, `PUT`, `DELETE`. |
| `path` | string | **Required.** Path relative to the org base, for example `api/v1/users/{id}/lifecycle/reactivate`, or a full `Link: rel="next"` URL. |
| `query` | object | Query-string parameters. |
| `headers` | object | More request headers. |
| `body` | object | JSON body for `POST` and `PUT`. |

### User investigation

| Action | Parameters | What it does |
| --- | --- | --- |
| `list_users` | `q`, `search`, `filter`, `sort_by`, `sort_order`, `limit`, `after`, `next_link`, `extra_query` | List or search users. Use `q` for a starts-with search on the name or the email. Use `search` for an expression, for example `status eq "ACTIVE"` or `profile.email eq "a@b.com"`. Use `filter` for the older syntax. |
| `get_user` | `user_id` | Get one user. Read the `status` in the result before a lifecycle action (see below). |
| `list_user_factors` | `user_id` + pagination | List the enrolled MFA factors of a user (`id`, `factorType`, `status`). Use it to find MFA that an attacker registered. |
| `list_user_groups` | `user_id` + pagination | List the group memberships of a user. Use it to find a privileged group to remove, or to confirm a quarantine. |
| `list_user_grants` | `user_id` + pagination | List the OAuth consent grants of a user, which show the apps and the scopes that the user authorized. |
| `list_user_roles` | `user_id` + pagination | List the admin roles of a user. Use it to see if the account is privileged, for example `SUPER_ADMIN`. |
| `list_groups` | `q`, `search`, `filter`, `limit`, `after`, `next_link`, `extra_query` | List or search groups. Only groups of type `OKTA_GROUP` accept membership changes. |
| `list_system_log` | `since`, `until`, `filter`, `q`, `sort_order`, `limit`, `next_link`, `extra_query` | Query the System Log (`/api/v1/logs`). Limit the scope with `since` and `until` (ISO-8601) and with a SCIM `filter`, for example `eventType eq "user.session.start"`, `actor.id eq "00u..."`, or `target.id eq "00u..."`. |

Read the `status` of the user first. `suspend` needs `ACTIVE`, `unsuspend` needs `SUSPENDED`, `activate` needs `STAGED` or `DEPROVISIONED`, and `unlock` needs `LOCKED_OUT`. A `400` from a lifecycle action shows a state mismatch. A `403` shows a problem with a scope or with a role.

### User lifecycle

| Action | Parameters | What it does |
| --- | --- | --- |
| `suspend_user` | `user_id` | Block sign-in but keep the account and its assignments. This is the recommended **reversible** containment action. To reverse it, use `unsuspend_user`. |
| `unsuspend_user` | `user_id` | Return a suspended user to `ACTIVE`. |
| `deactivate_user` | `user_id`, `send_email` (default `false`) | Deactivate or deprovision the user. This action is **destructive**. It removes app access, and it is not a clean inverse of `activate`. Use `suspend_user` instead. On a large org, the action can complete asynchronously. |
| `activate_user` | `user_id`, `send_email` (default `false`) | Activate a user that is `STAGED` or `DEPROVISIONED`. With `send_email=false`, the response includes an activation URL and token. |
| `unlock_user` | `user_id` | Unlock a `LOCKED_OUT` user and return the user to `ACTIVE`. |

### Credentials

| Action | Parameters | What it does |
| --- | --- | --- |
| `expire_password` | `user_id`, `temp_password` (default `false`) | Force a password change at the next sign-in (`PASSWORD_EXPIRED`). With `temp_password=true`, Okta invalidates the current password immediately and returns a one-time temporary password. |
| `reset_password` | `user_id`, `send_email` (default `false`) | Start a reset. The user moves to `RECOVERY`. With `send_email=false`, the response carries a one-time `resetPasswordUrl` to deliver out-of-band. |
| `set_user_password` | `user_id`, `password` | Set a specific new password directly. Use it to lock out an attacker with a value that only you know. The password must obey the password policy of the org. |

### MFA

| Action | Parameters | What it does |
| --- | --- | --- |
| `reset_user_factors` | `user_id`, `remove_recovery_enrollment` (default `false`) | Unenroll **all** MFA factors of a user and force re-enrollment. This has high value against MFA that an attacker registered. It does not change the password. |
| `reset_user_factor` | `user_id`, `factor_id`, `remove_recovery_enrollment` (default `false`) | Unenroll a **single** factor, from `list_user_factors`. If you remove a push factor or a signed-nonce factor, Okta also removes the related Okta Verify factors of the user. |

### Sessions & OAuth tokens

| Action | Parameters | What it does |
| --- | --- | --- |
| `clear_user_sessions` | `user_id`, `oauth_tokens` (default `true`), `forget_devices` (default `false`) | Revoke all Okta sessions of a user and force re-authentication. `oauth_tokens` defaults to **`true`**, which is the safe choice for incident response, so Okta also revokes the refresh tokens and the access tokens. The Okta API default of `false` keeps those tokens valid, and this is the most common containment mistake. `forget_devices` also clears remembered devices and factor trust. |
| `revoke_user_grants` | `user_id` | Revoke **all** OAuth consent grants of a user, across all clients, and stop OAuth-based persistence. Inspect the grants first with `list_user_grants`. |

> When you clear Okta sessions, the sessions that are already open in downstream apps (M365, Salesforce, and others) do **not** stop. To stop those sessions, use the session revocation of each app.

### Group containment

| Action | Parameters | What it does |
| --- | --- | --- |
| `add_user_to_group` | `group_id`, `user_id` | Add a user to an `OKTA_GROUP`. For example, move a compromised user into a quarantine group, or into a group with a high-friction sign-on policy. Find the group id with `list_groups`. |
| `remove_user_from_group` | `group_id`, `user_id` | Remove a user from a group. For example, remove a compromised user from a privileged group or an admin group. |

### Containment sequencing

For a confirmed account takeover, use this sequence of actions:

1. Run `reset_user_factors` to remove the MFA of the attacker.
2. Run `expire_password` with `temp_password=true`, or run `set_user_password`, to invalidate the credential.
3. Run `clear_user_sessions` to stop the live sessions **and** the OAuth tokens.
4. Run `revoke_user_grants` to stop OAuth persistence.

Revoke the sessions and the tokens **last**. This stops the live session of the attacker from continuing after the other steps. To stop everything first with one reversible action, use `suspend_user`.

## Detection & Response

This example response action suspends the Okta user that a detection names:

```yaml
- action: extension request
  extension action: suspend_user
  extension name: ext-okta
  extension request:
    user_id: '{{ .event/user_id }}'
```

> **Put literal strings in `{{ "..." }}`.**
> The extension evaluates the values under `extension request` as templates. A bare string without `{{ }}` is a [gjson](https://github.com/tidwall/gjson) path into the event. If the path does not resolve, the extension removes the key from the payload without a message.

`extension request` actions do not return a result. The rule engine does not put the response into the evaluation context of the rule. Use a [Playbook](../limacharlie/playbook.md) or an AI agent for a chain of actions, such as find the user, reset the factors, clear the sessions, and revoke the grants. A Playbook or an AI agent keeps state between calls.

## Notes

- **Two authentication modes.** SSWS is the fastest to set up, but it uses the privilege of an admin account and it stops after 30 days of no activity. The OAuth API Services app (private_key_jwt) is separate from any person and uses short-lived scoped tokens. Okta officially moves integrations to this mode.
- **DPoP** (sender-constrained tokens) is always enabled for new API Services apps. The extension mints a plain token first. If Okta answers `invalid_dpop_proof`, the extension changes to DPoP for the token request and for every API call.
- If one call with an OAuth token returns `401`, the extension treats it as an expired token. It drops the cached token and tries the request one more time with a new token. If you rotate the secret in Secrets Manager, the recovery is the same. The next authentication failure removes the cached client and reads the secret again.
- The extension backs off and retries a `429` or a `5xx` from the token endpoint. For a `429` from a data endpoint, it obeys the `Retry-After` value of Okta for a limited number of retries.
- The extension formats error messages as `okta api <status> on <method> <path>: <errorCode>: <errorSummary>`, and it redacts query strings.
- If you unsubscribe from the extension, its saved configuration stays. If you subscribe again, the extension restores the configuration and you do not configure it again.
