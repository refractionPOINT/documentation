---
title: API Keys
slug: api-keys
breadcrumb: Platform Management > Access and Permissions
source: https://docs.limacharlie.io/docs/api-keys
articleId: 2754cb85-7f6f-4b2a-a2ce-a01e88ed2508
---

* * *

API Keys

  *  __09 Jun 2025
  *  __ 4 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# API Keys

  *  __Updated on 09 Jun 2025
  *  __ 4 Minutes to read 



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

LimaCharlie Cloud has a concept of API keys. Those are secret keys that can be created and named, and then in turn be used to retrieve a JWT that can be associated with the LC REST API at https://api.limacharlie.io.

This allows construction of headless applications able to securely acquire time-restricted REST authentication tokens it can then use.

The list of available permissions can be programmatically retrieved from this URL: <https://app.limacharlie.io/owner_permissions>

## Managing

The API Keys are managed through the Organization view of the https://limacharlie.io web interface.

## Getting a JWT

Simply issue an HTTP POST such as:

`curl -X POST "https://jwt.limacharlie.io" -H "Content-Type: application/x-www-form-urlencoded" -d "oid=<YOUR_OID>&secret=<YOUR_API_KEY>"`

where the `oid` parameter is the Organization ID as found through the web interface and the `secret` parameter is the API key.

The return value is a simple JSON response with a `jwt` component which is the JSON web token. This token is only valid for one hour to limit the possible damage of a leak, and make the deletion of the API keys easier.

Response:

`{ "jwt": "<JWT_VALUE_HERE>" }`

### User API Keys

User API keys are to generate JSON web tokens (JWTs) for the REST API. In contrast to Organization API keys, the User API keys are associated with a specific user and provide the exact same access across all organizations.

This makes User API Keys very powerful but also riskier to manage. Therefore we recommend using Organization API keys whenever possible.

The User API keys can be used through all the same interfaces as the Organization API keys. The only difference is how you get the JWT. Instead of giving an `oid` parameter to `https://jwt.limacharlie.io/`, provide it with a `uid` parameter available through the LimaCharlie web interface.

`curl -X POST "https://jwt.limacharlie.io" -H "Content-Type: application/x-www-form-urlencoded" -d "uid=<YOUR_USER_ID>&secret=<YOUR_API_KEY>"`

In some instances, the JWT resulting from a User API key may be to large for normal API use, in which case you will get an `HTTP 413 Payload too large` from the API gateway. In those instances, also provide an `oid` (on top of the `uid`) to the `jwt.limacharlie.io` REST endpoint to get a JWT valid only for that organization.

`curl -X POST "https://jwt.limacharlie.io" -H "Content-Type: application/x-www-form-urlencoded" -d "oid=<YOUR_OID>&uid=<YOUR_USER_ID>&secret=<YOUR_API_KEY>"`

You may also use a User API Key to get the list of organizations available to it by querying the following REST endpoint:

`https://app.limacharlie.io/user_key_info?secret=<YOUR_USER_API_KEY>&uid=<YOUR_USER_ID>&with_names=true`

#### Ingestion Keys

The [artifact collection](/v2/docs/artifacts) in LC requires Ingestion Keys, which can be managed through the REST API section of the LC web interface. Access to manage these Ingestion Keys requires the `ingestkey.ctrl` permission.

## Python

A simple [Python API](https://github.com/refractionpoint/python-limacharlie/) is also provided that simplifies usage of the REST API by taking care of the API Key -> JWT exchange as necessary and wraps the functionality into nicer objects.

## Privileges

API Keys have several on-off privileges available.

To see a full list, see the "REST API" section of your organization.

Making a REST call will fail with a `401` if your API Key / token is missing some privileges and the missing privilege will be specified in the error.

## Required Privileges

Below is a list of privileges required for some common tasks.

### Go Live

When "going Live" through the web UI, the following is required by the user:

  * `output.*`: for the creation of the real-time output via HTTP to the browser.

  * `sensor.task`: to send the commands (both manually for the console and to populate the various tabs) to the Sensor.




## Flair

API Keys may have "flair" as part of the key name. A flair is like a tag surrounded by `[]`. Although it is not required, we advise to put the flair at the end of the API key name for readability.

For example:  
`orchestration-key[bulk]` is a key with a `bulk` flair.

Flairs are used to modify the behavior of an API key or provide some usage hints to various systems in LimaCharlie.

The following flairs are currently supported:

  * `bulk`: indicates to the REST API that this key is meant to do a large amount of calls, the API gateway tweaks the API call limits accordingly.

  * `segment`: indicates that only resources created by this key will be visible by this key. This is useful to provide access to a 3rd party in a limited fashion.




## Allowed IP Range

When creating an API key, you can optionally include an `allowed_ip_range`, which should be a [CIDR notation](https://aws.amazon.com/what-is/cidr/) IP range from which the API key can be used. Any use of the API key from a different IP address will fail. This is currently only configurable when creating an API key via the API and not in the UI.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.

  
  


Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

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

  * [ LimaCharlie SDK & CLI ](/docs/limacharlie-sdk)



* * *

###### What's Next

  * [ User Access ](/docs/user-access) __



Table of contents

    * Managing 
    * Getting a JWT 
    * Python 
    * Privileges 
    * Required Privileges 
    * Flair 
    * Allowed IP Range 



Tags

  * [ api ](/docs/en/tags/api)
  * [ platform ](/docs/en/tags/platform)


