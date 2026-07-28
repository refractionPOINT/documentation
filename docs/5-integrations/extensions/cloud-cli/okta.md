# Okta

The Okta CLI lets you interact with your Okta instances from the command line. This component of the Cloud CLI Extension lets you interact with Okta directly from LimaCharlie.

This extension uses [the Okta CLI](https://cli.okta.com/manual/).

## Example

This example returns a list of registered Okta applications.

```yaml
- action: extension request
  extension action: run
  extension name: ext-cloud-cli
  extension request:
    cloud: '{{ "okta" }}'
    command_line: '{{ "apps" }}'
    credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To use the Okta CLI, you need:

- An API key. See the [Create an API token guide](https://developer.okta.com/docs/guides/create-an-api-token/main/) from Okta.
- Create a secret in the secrets manager in this format:

```text
okta_domain/api_key
```

## Available Commands

> All "USERID" fields need the Okta User ID, not the name of the user

### Get User Details

Gets a user from your Okta organization.

#### Command

```bash
user get USERID
```

#### Example Input

```bash
user get 00untroxqpl08VcNC5d7
```

#### Example Output

```json
{
  "_links": {
    "deactivate": {
      "href": "https://dev-8675309.okta.com/api/v1/users/00up0nl0lftw7331WSz/lifecycle/deactivate",
      "method": "POST"
    },
    "schema": {
      "href": "https://dev-8675309.okta.com/api/v1/meta/schemas/user/otyn3jlrawrlmageyL2d7"
    },
    "self": {
      "href": "https://dev-8675309.okta.com/api/v1/users/00up0nl0lftw7331WSz"
    },
    "type": {
      "href": "https://dev-8675309.okta.com/api/v1/meta/types/user/otyn3jlrawrlmageyL2d7"
    },
    "unsuspend": {
      "href": "https://dev-8675309.okta.com/api/v1/users/00up0nl0lftw7331WSz/lifecycle/unsuspend",
      "method": "POST"
    }
  },
  "activated": "2025-03-13T17:37:33Z",
  "created": "2025-03-13T17:37:33Z",
  "credentials": {
    "password": {},
    "provider": {
      "name": "OKTA",
      "type": "OKTA"
    }
  },
  "id": "00up0nl0lftw7331WSz",
  "lastUpdated": "2025-03-14T13:37:10Z",
  "passwordChanged": "2025-03-13T17:37:33Z",
  "profile": {
    "email": "fake.user@limacharlie.com",
    "firstName": "Fake",
    "lastName": "User",
    "login": "fake.user@limacharlie.com",
    "mobilePhone": null,
    "secondEmail": null
  },
  "status": "ACTIVE",
  "statusChanged": "2025-03-14T13:37:10Z",
  "type": {
    "id": "otyn3jlrwwlmageyL2d7"
  }
}
```

### Get List of Users

By default, this lists the users that do not have a status of "DEPROVISIONED", up to the maximum (200 for most orgs). Most responses use pagination. The command can return a subset of users that match a supported filter expression or search criteria.

> This command takes an optional filter. If you do not give a filter, the command returns all users. For more information about the query filters of Okta, see <https://developer.okta.com/docs/reference/user-query/#filter-users>

#### Command

```bash
user list OPTIONAL_FILTER
```

#### Example Input

```bash
user list
```

#### Example Output

```json
[
  {
    "_links": {
      "self": {
        "href": "https://dev-8675309.okta.com/api/v1/users/00un2JpnNwheWSzOe5d7"
      }
    },
    "created": "2025-01-31T12:26:30Z",
    "credentials": {
      "password": {},
      "provider": {
        "name": "OKTA",
        "type": "OKTA"
      }
    },
    "id": "00up0nl0lftw7331WSz",
    "lastLogin": "2025-03-14T13:36:13Z",
    "lastUpdated": "2025-02-10T15:33:00Z",
    "passwordChanged": "2025-02-10T15:33:00Z",
    "profile": {
      "email": "fake.user@limacharlie.com",
      "firstName": "Fake",
      "lastName": "User",
      "login": "fake.user@limacharlie.com",
      "mobilePhone": null,
      "secondEmail": null
    },
    "status": "ACTIVE",
    "statusChanged": "2025-02-10T15:33:00Z",
    "type": {
      "id": "otyn2jpriwmLdgaiL5d7"
    }
  }
]
```

### Deactivate User

Deactivates a user.

> You can do this operation only on users that do not have a "DEPROVISIONED" status.

#### Command

```bash
user deactivate USERID
```

#### Example Input

```bash
user deactivate 00up0nl0lftw7331WSz
```

#### Example Output

```text
None
```

### Activate User

Activates a user.

> You can do this operation only on users that have a "STAGED" status.

#### Command

```bash
user activate USERID
```

#### Example Input

```bash
user activate 00up0nl0lftw7331WSz
```

#### Example Output

```text
None
```

### Expire User Password

This operation moves the user to the status "PASSWORD\_EXPIRED". The user must then change the password at the next login.

#### Command

```bash
user expire-password USERID
```

#### Example Input

```bash
user expire-password 00up0nl0lftw7331WSz
```

#### Example Output

```text
None
```

### Suspend User

Suspends a user. The user has a status of "SUSPENDED" when the process is complete.

> You can do this operation only on users that have an "ACTIVE" status.

#### Command

```bash
user suspend USERID
```

#### Example Input

```bash
user suspend 00up0nl0lftw7331WSz
```

#### Example Output

```text
None
```

### Unsuspend User

Unsuspends a user and returns the user to the "ACTIVE" state. You can do this operation only on users that have a "SUSPENDED" status.

> You can do this operation only on users that have a "SUSPENDED" status.

#### Command

```bash
user unsuspend USERID
```

#### Example Input

```bash
user unsuspend 00up0nl0lftw7331WSz
```

#### Example Output

```text
None
```

### Unlock User

Unlocks a user that has a "LOCKED\_OUT" status and returns the user to "ACTIVE" status. The user can then log in with the current password.

#### Command

```bash
user unlock USERID
```

#### Example Input

```bash
user unlock 00up0nl0lftw7331WSz
```

#### Example Output

```text
None
```
