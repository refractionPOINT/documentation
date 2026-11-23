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

    client = Client(uid='USER_ID', api_key='USER_API_KEY')
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

Organization names are unique across all of LimaCharlie. After you delete an organization, its name stays reserved for about 2 hours. The error you get when creating with that name says how many minutes remain.

## Regions

The region decides which datacenter stores and processes the organization's data. It is set at creation and cannot be changed afterwards.

Pass the region as `loc` in the REST API, `location` in the SDKs, or `--location` in the CLI. Matching is case-insensitive.

| Code | Datacenter | GCP region |
| --- | --- | --- |
| `usa` | United States | `us-central1` |
| `canada` | Canada | `northamerica-northeast1` |
| `europe` | Europe | `europe-west4`, Netherlands |
| `uk` | United Kingdom | `europe-west2`, London |
| `india` | India | `asia-south1`, Mumbai |
| `australia` | Australia | `australia-southeast1`, Sydney |
| `auto` | The datacenter nearest the API server that handles the call | Varies |

`auto` is the CLI default, but today it only ever lands on `usa`, `europe` or `australia`. For `canada`, `uk` or `india`, name the region. In automation and Infrastructure as Code, always pass an explicit code so the result does not depend on where the call was routed.

The web app lists the regions available to the signed-in user, taken from `GET /v1/plans`. If you use a [custom plan](billing/custom-plans.md), see that page for how to select it.

## Deleting an Organization

Deleting an organization cannot be undone. There is no restore.

### Who can delete

The caller needs both `billing.ctrl` and `user.ctrl` on the organization, as a user, either directly or through a group. Of the built-in roles, only Owner has both. Administrator does not have `billing.ctrl`.

Organization API keys cannot delete an organization. Use a user session or a user API key.

### What deletion does

- The subscription is cancelled immediately.
- All configuration is removed: Hive records, D&R rules, outputs, extension subscriptions, installation keys, API keys, and user and group memberships.
- Telemetry storage is deleted immediately. Backups are purged about 2 days later.
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

Make the delete call within 1 minute of getting the token. The deletion can take several minutes. If the delete call returns `503` with a `Retry-After` header, the deletion is still running: retry the same call with the same token. For those retries, the token stays accepted for up to 15 minutes.

### Offboarding a customer organization

For an MSSP removing a customer, a safe order is:

1. Export what you want to keep. Pull the configuration with [Git Sync](../5-integrations/extensions/limacharlie/git-sync.md) or an Infrastructure as Code export, and make sure outputs or archives have delivered the telemetry you need.
2. Uninstall the endpoint agents. See [Endpoint Agent Uninstallation](../2-sensors-deployment/endpoint-agent/uninstallation.md). Deleting the organization stops the agents from reporting but leaves them installed.
3. Delete the organization as above. This also removes it from every Organization Group, so no separate cleanup is needed there.
4. Wait about 2 hours before reusing the organization name.

---

## See Also

- [User Access](access/user-access.md)
- [API Keys](access/api-keys.md)
- [Custom Plans](billing/custom-plans.md)
- [Account Management FAQ](../8-reference/faq/account-management.md)
