# Building Extensions

This section is a work in progress

To learn more, ask a question on the [community forum](https://community.limacharlie.com/)

## Why Extensions?

When you build functionality as a LimaCharlie Extension, you get these advantages:

- **Multi-tenancy**: LC organizations can subscribe to your extension. You can replicate the features that you build across many organizations.
- **Credentials handling**: you do not need to store credentials from LC organizations. Each callback that you receive includes an authenticated LimaCharlie SDK for the Organization of that callback. The SDK has the permissions that you requested for the extension.
- **Configuration**: you can store configuration where the extension runs. LC also gives you a configuration JSON object for your extension, stored in Hive. LC gives you a callback to validate the content of the configuration when a user changes it.
- **GUI**: each extension defines its own Schema. The Schema shows LimaCharlie what actions the extension exposes, how to call them, and what each action returns. LimaCharlie reads the Schema and generates a custom user interface for your extension. You do not need to build a user interface, but you can build one.

### Public/Private Limitations

Anyone can build Extensions for LimaCharlie. The only limit applies when you make an Extension public. To subscribe an organization to a private extension, the owner of the extension needs the `billing.ctrl` and `user.ctrl` permission on that organization.

### Want to take your Extension public?

To make your extension public, or to monetize it, send a message to `answers@limacharlie.io`. A public extension is visible to everyone, and everyone can subscribe to it.

## High Level Structure

![image.png](../../assets/images/image(252).png)

Extensions are small services that receive webhooks from LimaCharlie. To build an extension, you must expose a small HTTPS service to the internet. LimaCharlie recommends a service such as [Google Cloud Run](https://cloud.google.com/run/), but you can also use AWS Lambdas or host the service on your own hardware.

This HTTPS server communicates with the LimaCharlie cloud with a simple protocol that uses JSON.

You do not need to know how the extension protocol works if you use the public implementations.

## Getting Started

To start from an example, use one of these frameworks.

- Golang: <https://github.com/refractionPOINT/lc-extension>
- Python: <https://github.com/refractionPOINT/lc-extension/tree/master/python>

The next sections explain the core concepts to build an extension. The examples use Golang because it has stricter typing, but the concepts are the same in each implementation.

### Extension Definition

To create an extension, first create a definition. Use the [web interface for your personal add-ons](https://app.limacharlie.io/add-ons/published).

Your definition needs these parts:

- **Destination URL:** the HTTPS URL where your extension is reachable.
- **Required Extensions:** the list of other extensions that your extension needs access to. If an org subscribes and one of them is missing, the user is prompted to subscribe to it.
- **Shared Secret:** an arbitrary string. LimaCharlie and your extension use it to sign webhooks to your extension, so the extension can verify that a hook is authentic. Use a random string of at least 32 characters.
- **Extension Flairs:** modifiers that apply to your extension. The `segment` flair isolates the resources that the extension can access. The extension then sees and changes only the objects, such as rules, that it created. This flair is good for extensions that need a narrow scope, and you should enable it unless you know that you need it off. The `bulk` flair tells LimaCharlie that the extension expects to make many API calls to the LC cloud. This flair increases the API quota for the extension.
- **Permissions:** the list of permissions that this extension needs on each organization that subscribes to it. Use the smallest number of permissions.

### Schema

The Extension Schema is the next important part of your extension. It describes what your extension can do, and it helps define the GUI.

This example shows the high-level structure of a schema.

```json
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
 The `config_schema` and the `request_schema` both use the same object structure:

```text
"fields": { .. }, // key-value pair
"requirements": [[]],
```

The example above hides the contents of `fields`. Each `field` key-value pair has the same structure. The minimal form is:

```text
field_name: {
  data_type: "string",
  description: "",
},
```

The `requirements` field references the field keys. It defines which fields are required, alone or as a set. The first array joins its elements with an AND. The nested array joins its elements with an OR.
 For example:

- `[['denominator'], ['numerator']]` means:
   (denominator AND numerator),
- `[['denominator'], ['numerator', 'default']]` means:
   (denominator AND ( one of numerator OR default)).

When you start, use the simplest data type that applies, such as `string`, `boolean`, or `json`. A simple data type helps you learn the extensions framework and test your service quickly.

After that, define the data_type and the other optional fields in more detail. The UI then adapts to the data types that you define. For more details, see the [data types reference](schema-data-types.md) or the [lc-extension SDK source](https://github.com/refractionPOINT/lc-extension/blob/master/common/config_schema.go).

#### Config Schema (optional)

The config schema describes the extension's config, as stored in a Hive record in the `extension_configuration` Hive.

Not all extensions have a configuration. If you need help to decide if your extension needs one, ask on the [community forum](https://community.limacharlie.com/).

The config schema is a list of fields.

#### Request Schema

Each Request Schema is a key-value pair of the request name and the contents of its schema. The critical contents are these fields:

- **is_impersonated**: shows if the request impersonates the user through its authentication.
- **is_user_facing**: shows if the request is visible to the user in the UI. It does not stop the use of the request through the API or as a `supported_action`.
- **parameters**: contains the data_type and other fields *(the same fields format as the config schema)*

Other optional fields improve the user experience:

- **short_description**
- **long_description**
- **messages**: includes 3 nested fields, `in_progress`, `success`, and `error`, to give more context for each case.

#### Response Schema (optional)

Each request schema can contain a response schema. It uses the same fields format as a config schema and the request parameters.

Skip the response schema when you start. Add it when you refine the extension's GUI, or when you want to show what kind of response a user gets.

### Callbacks

Callbacks are code that an extension can specify for each type of event that occurs.

#### Configuration Validation Callback

LimaCharlie uses this callback to check a change of configuration in Hive. If the configuration is valid, return success. If it is not valid, return an error.

#### Event Callback

The LimaCharlie platform generates events that you do not control. Currently, it supports these 3 events:

- **subscribe**: called when an organization subscribes to an extension.
- **unsubscribe**: called when an organization unsubscribes from an extension.
- **update**: called one time each day for each organization that subscribes to the extension. Use it to make updates to an organization, for example to update the D&R rules that the extension uses.

Your extension receives these events only if the extension's Schema specifies them as of-interest.

#### Request Callback

Requests are the core way for users, D&R rules, or other extensions to interact with your extension. You can define one callback for each `action`. Many extensions have multiple actions. Some actions are public, for requests that users generate. Other actions are private, and the extension uses them internally.

## Simplified Frameworks

The Golang implementation of Extensions gives you 3 different simplified frameworks. They make a new extension easier to build in specific cases: <https://github.com/refractionPOINT/lc-extension/tree/master/simplified>

### D&R

This simplified framework is in `dr.go`. It lets you package D&R rules as an extension, and then distribute and update the D&R rules to many orgs. To use it, define the `GetRules()` function and return a structure such as `map[DR-Namespace]map[RuleName]RuleContent`. The simplified framework does the recurring updates and the other work.

### Lookup

This framework is similar to the D&R simplified framework, but it packages Lookups. Example: <https://github.com/refractionPOINT/lc-extension/blob/master/examples/lookup/main.go>

### CLI

This simplified framework integrates 3rd party Command Line Interface tools. LimaCharlie can then automate those tools, which often adds bi-directionality to the platform.

LimaCharlie Extensions let users expand and customize their security environments. An Extension integrates third-party tools, automates workflows, and adds new capabilities. An organization subscribes to an Extension and grants it specific permissions to interact with the infrastructure of the organization. An Extension can be private, for tailored use, or public, to share with the community. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives you complete control of security operations. This structure supports flexible, multi-tenant setups for managed security providers, and for enterprises that manage many departments or clients.
