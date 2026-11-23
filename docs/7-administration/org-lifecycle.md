# Organization Lifecycle

This page covers creating an organization, choosing its region, and deleting it when a customer leaves.

## Creating an Organization

Any signed-in user can create an organization. No organization permission is needed, because the organization does not exist yet. The user who creates it becomes its Owner.

The request must come from a user identity, either a web login or a [user API key](access/api-keys.md#user-api-keys). Organization API keys are refused, since they belong to an existing organization and carry no user.

=== "Web app"

    Sign in and create the organization from the web app. You pick a globally unique name and a region.

=== "CLI"

    ```bash
    limacharlie org create --name my-new-org --location usa
    ```

    Add `--use` to make the new organization the default for later commands.

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization

    client = Client(oid='-', uid='USER_ID', api_key='USER_API_KEY')
    new_org = Organization.create_org(client, 'my-new-org', location='usa')
    ```

=== "REST API"

    ```bash
    curl -s -X POST "https://api.limacharlie.io/v1/orgs/new" \
      -H "Authorization: Bearer $LC_JWT" \
      -d "name=my-new-org&loc=usa"
    ```

The REST call also accepts `description` and `template`, an [Infrastructure as Code](../5-integrations/extensions/limacharlie/infrastructure.md) template applied to the new organization.

### Organization limit

By default, a user can create a new organization only while they are a direct member of fewer than 2 organizations. The count covers every organization the user is a direct member of, whether they created it or were added to it individually. Access through an [Organization Group](access/user-access.md) does not count. The limit only applies to creating organizations: other people can still add the user to more organizations.

For MSSPs, this means an analyst who was added directly to two customer organizations can no longer create one. Grant access through Organization Groups, and have one account with a raised limit create the organizations.

When you hit the limit, the API returns `Maximum number of organization reached, contact support@limacharlie.io to get more`. Contact support to raise it.

### Names

Organization names are unique across all of LimaCharlie, ignoring case. Check name availability before creating an organization, with `GET /v1/orgs/new?name=NAME` or `Organization.check_name`. After deletion starts, the name used to create the organization stays reserved for about 2 hours by default. The create error tells you how long remains. Renaming an organization later changes only its display name, so the original name is the one that stays reserved.

## Regions

The region is the organization's primary data region. It decides which datacenter hosts the organization. It is set at creation and cannot be changed afterwards.

Pass the region as `loc` in the REST API, `location` in the SDKs, or `--location` in the CLI. Matching is case-insensitive.

| Code | Datacenter | Primary GCP region |
| --- | --- | --- |
| `usa` | United States | `us-central1` |
| `canada` | Canada | `northamerica-northeast1` |
| `europe` | Europe | `europe-west4`, Netherlands |
| `uk` | United Kingdom | `europe-west2`, London |
| `india` | India | `asia-south1`, Mumbai |
| `australia` | Australia | `australia-southeast1`, Sydney |
| `auto` | The default region of the API server that handles the request | Varies |

`auto` is the CLI default. Today it resolves to `usa`, `europe` or `australia`, depending on which API server handles the request. Pass an explicit code to control placement. Always do so in automation and Infrastructure as Code, and for `canada`, `uk` or `india`, which `auto` does not pick today.

The web app lists the regions available to the signed-in user, taken from `GET /v1/plans`. If you use a [custom plan](billing/custom-plans.md), see that page for how to select it.

## Deleting an Organization

Deletion can't be undone from the web app or API.

### Who can delete

The caller needs both `billing.ctrl` and `user.ctrl` on the organization, as a user, either directly or through a group. Of the built-in roles, only Owner has both. Administrator does not have `billing.ctrl`.

Organization API keys cannot delete an organization. Use a user session or a user API key.

### What deletion does

- The subscription is cancelled immediately.
- Deletion removes the organization's configuration: Hive records, D&R rules, outputs, extension subscriptions, installation keys, API keys, and user and group memberships.
- Deleting the organization starts cleanup of its stored telemetry. Backups become eligible for purge after about 2 days. Cleanup can take longer.
- Every connected sensor is told to disconnect. The agent is **not** uninstalled from the endpoint, so uninstall it first if you want it gone.

### How to delete

=== "Web app"

    Open `Billing & Usage`, scroll to the Danger Zone and click `Delete Organization`. You can also go through the organizations list, choose `Edit`, then `Delete Organization`. The button only shows for users with `billing.ctrl`.

=== "CLI"

    The first call prints a confirmation token. The second call, within 60 seconds, deletes the organization.

    ```bash
    limacharlie org delete --oid OID
    limacharlie org delete --oid OID --confirm-token TOKEN
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization

    client = Client(oid='ORG_ID', uid='USER_ID', api_key='USER_API_KEY')
    org = Organization(client)

    # First call returns {"confirmation": "<token>"}
    token = org.delete_org()["confirmation"]
    # Second call, within 1 minute, deletes
    org.delete_org(token)
    ```

=== "REST API"

    ```bash
    # Step 1: get a confirmation token, valid for 1 minute
    curl -s "https://api.limacharlie.io/v1/orgs/YOUR_OID/delete" \
      -H "Authorization: Bearer $LC_JWT"
    # {"confirmation": "<token>"}

    # Step 2: delete
    curl -s -X DELETE \
      "https://api.limacharlie.io/v1/orgs/YOUR_OID/delete?confirmation=<token>" \
      -H "Authorization: Bearer $LC_JWT"
    ```

Send the `DELETE` within one minute of getting the token. The deletion can take several minutes. If it returns `503` with `retryable: true`, wait for the `Retry-After` delay and retry the same `DELETE` with the same token. Once the deletion has been accepted, the token can be retried for up to 15 minutes. If the API says the token expired and the organization still exists, get a new confirmation token.

The Python `delete_org()` and the CLI do not retry a `503` for you. Retry the second call yourself.

### Offboarding a customer organization

For an MSSP removing a customer, a safe order is:

1. Export what you want to keep. Pull the configuration with [Git Sync](../5-integrations/extensions/limacharlie/git-sync.md) or an Infrastructure as Code export, and make sure outputs or archives have delivered the telemetry you need.
2. Uninstall the endpoint agents. See [Endpoint Agent Uninstallation](../2-sensors-deployment/endpoint-agent/uninstallation.md). Deleting the organization stops the agents from reporting but leaves them installed.
3. Delete the organization as above. This also removes it from every Organization Group, so no separate cleanup is needed there.
4. Wait for the name hold reported by the API before reusing the name.

---

## See Also

- [User Access](access/user-access.md)
- [API Keys](access/api-keys.md)
- [Custom Plans](billing/custom-plans.md)
- [Account Management FAQ](../8-reference/faq/account-management.md)
