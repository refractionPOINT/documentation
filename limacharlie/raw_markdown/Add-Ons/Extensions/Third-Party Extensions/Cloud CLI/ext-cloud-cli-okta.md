---
title: Okta
slug: ext-cloud-cli-okta
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-okta
articleId: ba31239a-99bb-49a7-9183-0d2c1b83a4be
---

* * *

Okta

  *  __20 Mar 2025
  *  __ 3 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Okta

  *  __Updated on 20 Mar 2025
  *  __ 3 Minutes to read 



  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




* * *

Article summary

 __

Did you find this summary helpful? __ __ __ __

__

Thank you for your feedback!

The Okta CLI allows you to interact with your Okta instance(s) via the command line. With this component of the Cloud CLI Extension, you can interact with Okta directly from LimaCharlie.

This extension makes use of the Okta CLI, which can be found [here](https://cli.okta.com/manual/).

## Example

The following example returns a list of registered Okta applications.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "okta" }}' 
        command_line: '{{ "apps" }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

To make use of the Okta CLI, you will need:

  * An API key. More information about provisioning an API key can be found [here](https://developer.okta.com/docs/guides/create-an-api-token/main/).

  * Create a secret in the secrets manager in the following format:



    
    
    okta_domain/api_key
    

## Available Commands

> All “USERID” fields require the Okta User ID, not the user’s name

### Get User Details

Fetches a user from your Okta organization.

#### Command
    
    
    user get USERID

#### Example Input
    
    
    user get 00untroxqpl08VcNC5d7

#### Example Output
    
    
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

### Get List of Users

Lists users that do not have a status of “DEPROVISIONED” (by default), up to the maximum (200 for most orgs), with pagination in most cases. A subset of users can be returned that match a supported filter expression or search criteria.

> This command takes an optional filter. If no filter is provided, all users are returned. For more information on Okta’s query filters, visit <https://developer.okta.com/docs/reference/user-query/#filter-users>

#### Command
    
    
    user list OPTIONAL_FILTER

#### Example Input
    
    
    user list

#### Example Output
    
    
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

### Deactivate User

Deactivates a user.

> This operation can only be performed on users that do not have a “DEPROVISIONED” status.

#### Command
    
    
    user deactivate USERID

#### Example Input
    
    
    user deactivate 00up0nl0lftw7331WSz

#### Example Output
    
    
    None

### Activate User

Activates a user.

> This operation can only be performed on users with a “STAGED” status.

#### Command
    
    
    user activate USERID

#### Example Input
    
    
    user activate 00up0nl0lftw7331WSz

#### Example Output
    
    
    None

### Expire User Password

This operation transitions the user to the status of “PASSWORD_EXPIRED” so that the user is required to change their password at their next login.

#### Command
    
    
    user expire-password USERID

#### Example Input
    
    
    user expire-password 00up0nl0lftw7331WSz

#### Example Output
    
    
    None

### Suspend User

Suspends a user. The user will have a status of “SUSPENDED” when the process is complete.

> This operation can only be performed on users with an “ACTIVE” status.

#### Command
    
    
    user suspend USERID

#### Example Input
    
    
    user suspend 00up0nl0lftw7331WSz

#### Example Output
    
    
    None

### Unsuspend User

Unsuspends a user and returns them to the “ACTIVE” state. This operation can only be performed on users that have a “SUSPENDED” status.

> This operation can only be performed on users that have a “SUSPENDED” status.

#### Command
    
    
    user unsuspend USERID

#### Example Input
    
    
    user unsuspend 00up0nl0lftw7331WSz

#### Example Output
    
    
    None

### Unlock User

Unlocks a user with a “LOCKED_OUT” status and returns them to “ACTIVE” status. Users will be able to login with their current password.

#### Command
    
    
    user unlock USERID

#### Example Input
    
    
    user unlock 00up0nl0lftw7331WSz

#### Example Output
    
    
    None

Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

* * *

Was this article helpful?

__Yes __No

 __

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change  


Please enter a valid email

Cancel

* * *

###### Related articles

  * [ Okta ](/docs/adapter-types-okta)



* * *

###### What's Next

  * [ StrongDM ](/docs/ext-cloud-cli-sdm) __



Table of contents

    * Example 
    * Credentials 
    * Available Commands 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


