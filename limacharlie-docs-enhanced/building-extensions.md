This section is a work in progress

Feel free to reach out to us on our Community Slack if you'd like to learn more

## Why Extensions?

Building functionality as a LimaCharlie Extension provides you specific convenience:

* **Multi-tenancy**: LC organizations can subscribe to your extension and you can replicate the features you're building across tenants.
* **Credentials handling**: you don't need to store any credentials from LC organizations. Every callback you receive will include an authenticated LimaCharlie SDK for the Organization relevant to the callback, with the permissions you requesed for the extension.
* **Configuration**: you're always welcome to store some configuration wherever the extension lives, but as a convenience LC will provide you with a configuration JSON object for your extension (stored in Hive) and with a callback for you to validate the content of the configuration when a user makes a modification.
* **GUI**: each extension defines its own Schema, a structure indicating to LimaCharlie what actions the extension exposes, how to call it and what to expect as a return value from actions. This information is then automatically interpreted by LimaCharlie to generate a custom user interface for your extension, making it extremely easy to expose new functionality in LimaCharlie without having to build any kind of UI (though you're always free to build one if you'd like).

### Public/Private Limitations

Anyone can build Extensions for LimaCharlie. The only limit is put on making an Extension public. Private extensions require the owner of the extension to have the `billing.ctrl` and `user.ctrl` permission on an organization in order to subscribe the organization to the private extension.

### Want to take your Extension public?

If you'd like to make your extension public (and/or monetize it), reach out to `answers@limacharlie.io` and we'll help you out. Once public, an extension is visible by everyone and can subscribed by everyone.

## High Level Structure

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28252%29.png)

Extensions are small services that receive webhooks from LimaCharlie. This means building an extension requires exposing a small HTTPS service to the internet. We recommend using something like [Google Cloud Run](https://cloud.google.com/run/), but ultimately you could also use AWS Lambdas or even host on your own hardware.

This https server will communicate with the LimaCharlie cloud according to a simple protocol using JSON.

That being said, don't worry, you don't need to know the underlying way the extension protocol works as long as you're comfortable with our public implementations.

## Getting Started

Want to get your hands on an example? We recommend using one of the following frameworks to get started.

* Golang: <https://github.com/refractionPOINT/lc-extension>
* Python: <https://github.com/refractionPOINT/lc-extension/tree/master/python>

For a more step-by-step overview, let's dig into some of the core concepts of building an extension. We will reference Golang since it provides stricter typing, but conceptually it's the same across implementations.

### Extension Definition

To create an extension, start by creating a definition - accessible through the [web interface for your personal add-ons](https://app.limacharlie.io/add-ons/published).

The required aspects of your definition are as follows:

* **Destination URL:** this is the HTTPS URL where your extension will be reachable at.
* **Required Extensions:** this is the list of other extensions your extension assumes it will have access to. When an org subscribes and is missing one of those, the user will be prompted to subscribe to these.
* **Shared Secret:** this is an arbitrary string that will be used by LimaCharlie and your extension to sign webhooks to your extension, allowing it to very the authenticity of the hook. Make it something at least 32 characters and random.
* **Extension Flairs:** these are modifiers that will be applied to your extension. Namely the `segment` flair will isolate the resources the extension can access so that it can only see and modify things (like  rules) that it has created, making it great for extensions that need a narrow scope, you should enable it unless you know you need it off. The `bulk` flair tells LimaCharlie that it expects to make a lot of API calls to the LC cloud, which will increase the API quota for the extension.
* **Permissions:** the list of permissions this extension requires on each organization subscribed to it. Use the least amount of permissions possible.

### Schema

The Extension Schema is the next important piece of building your extension. It describes what your extension can do and helps define the GUI.

Here's an example high-level structure of a schema.

```
{
  "config_schema": {
    "fields": { ... }
    "requirements": null
  },
  "request_schema": {
    // defines two custom requests, 'dir_list' and 'refresh'
    "dir_list": {
      "is_impersonated": false,
      "is_user_facing": false,
      "long_description": "directory listing",
      "parameters": {
        "fields": { ... },
        "requirements": null
      },
      "short_description": "directory listing"
    },
    "refresh": {
      "is_impersonated": false,
      "is_user_facing": true,
      "long_description": "refresh data",
      "parameters": {
        "fields": { ... },
        "requirements": null
      },
      "short_description": "refresh data"
    },
  },
  "required_events": [
    "subscribe",
    "unsubscribe"
  ]
}
```

**The Field Configuration**
 Notice that for both the `config_schema` and the `request_schema` there is a recurring object structure that looks like the following:

```
"fields": { .. }, // key-value pair
"requirements": [[]],
```

While hidden in the example above, each `field` key-value pair shares the same structure and has a minimal implementation as such:

```
field_name: {
  data_type: "string",
  description: "",
},
```

The `requirements` field references the field keys to define whether or not certain fields individually or as a set are required. You can think of the first array to join elements with an AND, while the nested array serves as an OR.
 For example:

* `[['denominator'], ['numerator']]` means:
   (denominator AND numerator),
* `[['denominator'], ['numerator', 'default']]` means:
   (denominator AND ( one of numerator OR default)).

When getting started, we recommend utilizing the simplest data type applicable. This will enable you to get a grasp of the whole extensions framework and allow you to quickly test our your service. Such as `string`, `boolean`, `json`, etc.

Afterwards, we recommend you define the data\_type and other optional fields further, so that the UI may adapt to your defined data types. For more details, please see the [page on data types](/v2/docs/schema-data-types) or review the code definitions [here](https://github.com/refractionPOINT/lc-extension/blob/master/common/config_schema.go).

#### Config Schema (optional)

The config schema is a description of what the extension's config should look like, when stored as a Hive record in the `extension_configuration` [Hive](/v2/docs/config-hive) for convenience.

Not all extensions will have a configuration, feel free to reach out on the community slack if you need help determining whether or not your extension needs a configuration.

At the core, the config schema is simply a list of fields.

#### Request Schema

Every Request Schema exists as a key value pair of the request name, and a corresponding schema contents. The critical contents include the following fields:

* **is\_impersonated**: Whether or not the request impersonates the user through it's authentication
* **is\_user\_facing**: Whether or not this request should be visisble to the user in the UI. It does not prevent this request from bieng used through the API or as a `supported_action` (more on that later).
* **parameters**: This contains the data\_type and other fields *(recall the same fields format as the config schema)*

Other optional fields exist to facilitate the user experience, such as:

* **short\_description**
* **long\_description**
* **messages**: Includes 3 nested fields, `in_progress`, `success`, `error` to provide additional context for each case.

#### Response Schema (optional)

Each request schema may optionally contain a response schema in the same fields format as a config schema and the request parameters.

When getting started, we recommend that you skip this until you are ready to refine the extension's GUI, or you wish to clarify that kind of response a user should expect.

### Callbacks

Callbacks are functionality that an extension can specify whenever some type of event occurs.

#### Configuration Validation Callback

This callback is used by LimaCharlie to check the validity of a change in configuration done in Hive. If the configuration is valid, return success, otherwise you can return an error.

#### Event Callback

Events are events generated by the LimaCharlie platform outside your control. Currently, these 3 events are supported:

* **subscribe**: called when an organization subscribes to an extension.
* **unsubscribe**: called when an organization unsubscribes from an extension.
* **update**: called once a day per organization subscribed to the extension. It is a convenient way to perform updates to an organization like when needing to update D&R rules used by the extension.

Your extension will only receive these events if they were specified as of-interest in the extension's Schema.

#### Request Callback

The requests are the core way users, D&R rules or other extensions can interact with your extension. You can define one callback per `action`. It is common for an extension to have multiple actions, some public (for user-generated requests) and some private (to be used internally by the extension in the course of doing whatever it does).

## Simplified Frameworks

The Golang implementation of Extensions provides 3 different simplified frameworks to make the job of producing a new extension more straight forward in specific cases: <https://github.com/refractionPOINT/lc-extension/tree/master/simplified>

### D&R

This simplified framework, found in `dr.go` allows you to package D&R rules as an extension making it easy for you to distribute and update D&R rules to many orgs. Its core mechanism is based on defining the `GetRules()` function and returning a structure like `map[DR-Namespace]map[RuleName]RuleContent`. The simplified framework takes care of the recurring updates and everything else.

### Lookup

Similarl to the D&R simplified framework, but is used to package Lookups. Example: <https://github.com/refractionPOINT/lc-extension/blob/master/examples/lookup/main.go>

### CLI

This simplified framework serves to streamline the integration of 3rd party Command Line Interface tools so that they can be automated using LimaCharlie, often bringing bi-directionality to the platform.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.
