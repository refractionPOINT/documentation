The Okta CLI allows you to interact with your Okta instance(s) via the command line. With this component of the Cloud CLI Extension, you can interact with Okta directly from LimaCharlie.

This extension makes use of the Okta CLI, which can be found [here](https://cli.okta.com/manual/).

## Example

The following example returns a list of registered Okta applications.

```
- action: extension request
 Â extension action: run
 Â extension name: ext-cloud-cli
 Â extension request:
 Â  Â cloud: '{{ "okta" }}'
 Â  Â command_line: '{{ "apps" }}'
 Â  Â credentials: '{{ "hive://secret/secret-name" }}'
```

## Credentials

To make use of the Okta CLI, you will need:

* An API key. More information about provisioning an API key can be found [here](https://developer.okta.com/docs/guides/create-an-api-token/main/).
* Create a secret in the secrets manager in the following format:

```
okta_domain/api_key
```

## Available Commands

> All â€śUSERIDâ€ť fields require the Okta User ID, not the userâ€™s name

### Get User Details

Fetches a user from your Okta organization.

#### Command

```
user get USERID
```

#### Example Input

```
user get 00untroxqpl08VcNC5d7
```

#### Example Output

```
{
 Â "_links": {
 Â  Â "deactivate": {
 Â  Â  Â "href": "https://dev-8675309.okta.com/api/v1/users/00up0nl0lftw7331WSz/lifecycle/deactivate",
 Â  Â  Â "method": "POST"
 Â  Â },
 Â  Â "schema": {
 Â  Â  Â "href": "https://dev-8675309.okta.com/api/v1/meta/schemas/user/otyn3jlrawrlmageyL2d7"
 Â  Â },
 Â  Â "self": {
 Â  Â  Â "href": "https://dev-8675309.okta.com/api/v1/users/00up0nl0lftw7331WSz"
 Â  Â },
 Â  Â "type": {
 Â  Â  Â "href": "https://dev-8675309.okta.com/api/v1/meta/types/user/otyn3jlrawrlmageyL2d7"
 Â  Â },
 Â  Â "unsuspend": {
 Â  Â  Â "href": "https://dev-8675309.okta.com/api/v1/users/00up0nl0lftw7331WSz/lifecycle/unsuspend",
 Â  Â  Â "method": "POST"
 Â  Â }
 Â },
 Â "activated": "2025-03-13T17:37:33Z",
 Â "created": "2025-03-13T17:37:33Z",
 Â "credentials": {
 Â  Â "password": {},
 Â  Â "provider": {
 Â  Â  Â "name": "OKTA",
 Â  Â  Â "type": "OKTA"
 Â  Â }
 Â },
 Â "id": "00up0nl0lftw7331WSz",
 Â "lastUpdated": "2025-03-14T13:37:10Z",
 Â "passwordChanged": "2025-03-13T17:37:33Z",
 Â "profile": {
 Â  Â "email": "fake.user@limacharlie.com",
 Â  Â "firstName": "Fake",
 Â  Â "lastName": "User",
 Â  Â "login": "fake.user@limacharlie.com",
 Â  Â "mobilePhone": null,
 Â  Â "secondEmail": null
 Â },
 Â "status": "ACTIVE",
 Â "statusChanged": "2025-03-14T13:37:10Z",
 Â "type": {
 Â  Â "id": "otyn3jlrwwlmageyL2d7"
 Â }
}
```

### Get List of Users

Lists users that do not have a status of â€śDEPROVISIONEDâ€ť (by default), up to the maximum (200 for most orgs), with pagination in most cases. A subset of users can be returned that match a supported filter expression or search criteria.

> This command takes an optional filter. If no filter is provided, all users are returned. For more information on Oktaâ€™s query filters, visit <https://developer.okta.com/docs/reference/user-query/#filter-users>

#### Command

```
user list OPTIONAL_FILTER
```

#### Example Input

```
user list
```

#### Example Output

```
[
 Â {
 Â  Â "_links": {
 Â  Â  Â "self": {
 Â  Â  Â  Â "href": "https://dev-8675309.okta.com/api/v1/users/00un2JpnNwheWSzOe5d7"
 Â  Â  Â }
 Â  Â },
 Â  Â "created": "2025-01-31T12:26:30Z",
 Â  Â "credentials": {
 Â  Â  Â "password": {},
 Â  Â  Â "provider": {
 Â  Â  Â  Â "name": "OKTA",
 Â  Â  Â  Â "type": "OKTA"
 Â  Â  Â }
 Â  Â },
 Â  Â "id": "00up0nl0lftw7331WSz",
 Â  Â "lastLogin": "2025-03-14T13:36:13Z",
 Â  Â "lastUpdated": "2025-02-10T15:33:00Z",
 Â  Â "passwordChanged": "2025-02-10T15:33:00Z",
 Â  Â "profile": {
 Â  Â  Â "email": "fake.user@limacharlie.com",
 Â  Â  Â "firstName": "Fake",
 Â  Â  Â "lastName": "User",
 Â  Â  Â "login": "fake.user@limacharlie.com",
 Â  Â  Â "mobilePhone": null,
 Â  Â  Â "secondEmail": null
 Â  Â },
 Â  Â "status": "ACTIVE",
 Â  Â "statusChanged": "2025-02-10T15:33:00Z",
 Â  Â "type": {
 Â  Â  Â "id": "otyn2jpriwmLdgaiL5d7"
 Â  Â }
 Â }
]
```

### Deactivate User

Deactivates a user.

> This operation can only be performed on users that do not have a â€śDEPROVISIONEDâ€ť status.

#### Command

```
user deactivate USERID
```

#### Example Input

```
user deactivate 00up0nl0lftw7331WSz
```

#### Example Output

```
None
```

### Activate User

Activates a user.

> This operation can only be performed on users with a â€śSTAGEDâ€ť status.

#### Command

```
user activate USERID
```

#### Example Input

```
user activate 00up0nl0lftw7331WSz
```

#### Example Output

```
None
```

### Expire User Password

This operation transitions the user to the status of â€śPASSWORD\_EXPIREDâ€ť so that the user is required to change their password at their next login.

#### Command

```
user expire-password USERID
```

#### Example Input

```
user expire-password 00up0nl0lftw7331WSz
```

#### Example Output

```
None
```

### Suspend User

Suspends a user. The user will have a status of â€śSUSPENDEDâ€ť when the process is complete.

> This operation can only be performed on users with an â€śACTIVEâ€ť status.

#### Command

```
user suspend USERID
```

#### Example Input

```
user suspend 00up0nl0lftw7331WSz
```

#### Example Output

```
None
```

### Unsuspend User

Unsuspends a user and returns them to the â€śACTIVEâ€ť state. This operation can only be performed on users that have a â€śSUSPENDEDâ€ť status.

> This operation can only be performed on users that have a â€śSUSPENDEDâ€ť status.

#### Command

```
user unsuspend USERID
```

#### Example Input

```
user unsuspend 00up0nl0lftw7331WSz
```

#### Example Output

```
None
```

### Unlock User

Unlocks a user with a â€śLOCKED\_OUTâ€ť status and returns them to â€śACTIVEâ€ť status. Users will be able to login with their current password.

#### Command

```
user unlock USERID
```

#### Example Input

```
user unlock 00up0nl0lftw7331WSz
```

#### Example Output

```
None
```

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.
