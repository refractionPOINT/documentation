# Building on LimaCharlie

The LimaCharlie SecOps Cloud Platform (SCP) is a unified platform for modern cybersecurity operations that delivers core cybersecurity capabilities and infrastructure via a public cloud model: on-demand, pay-per-use, and API-first. This paradigm shift enables cybersecurity startups, builders, and service providers to create valuable products and services without reinventing foundational security infrastructure.

## Why Build on LimaCharlie?

Building on the SecOps Cloud Platform offers three key advantages:

### Focus on Your Core Value

**Clarify your differentiators.** In a crowded marketplace where buyers are wary of tool sprawl, you must demonstrate clear value and differentiate yourself. Determine what sets you apart and where you can deliver the greatest value to customers—this is where your internal engineering resources should be focused.

**Offload infrastructure work.** The SCP provides mature cybersecurity capabilities that teams used to develop themselves or purchase as part of a product, including:
- Deploying endpoint capabilities via a multiplatform agent
- Alerting and correlating logs from any source
- Automating real-time analysis and response regardless of environment
- Routing telemetry data to any destination
- Performing historical threat hunts
- Isolating endpoints from a network remotely

Cybersecurity builders no longer need to "reinvent the wheel" to get to market. Just as software developers leverage cloud-based services like AWS Lambda instead of managing physical servers, you can use the SCP's infrastructure capabilities to spend time on your core value proposition—reducing maintenance and integration challenges, eliminating external dependencies, and avoiding the risk of building on someone else's product.

**Work with SCP engineers to develop custom integrations.** The SecOps Cloud Platform is a vendor-neutral provider of tooling and infrastructure for the cybersecurity industry—not a potential competitor. Reach out to LimaCharlie engineers for support in creating customized integrations, advice on best practices for configurations or deployments, or feature requests. The SCP's public cloud business model means the platform succeeds when its users succeed.

### Reduce Up-front Costs

**Conduct research and develop a prototype for free.** The SCP provides all users access to a fully featured free tier that includes two sensors. There is zero up-front cost to begin researching the platform, testing your idea, or developing a prototype.

**Build without lock-in.** The SCP's pricing model means you only pay for what you need, for as long as you use it. No mandatory minimums, long-term contracts, complex licensing, or termination fees. You're not committed to a spending level before your growth justifies it—and you're not locked into your infrastructure provider.

**Use available SCP resources to save money.** The platform is designed to be user-friendly and supported by extensive documentation, an active community forum, and a learning library full of tutorials and walkthroughs. You can reach out to SCP engineers at any time for help, and qualified builders can apply for a $1000 platform credit through the Cybersecurity Infrastructure Grant Program.

**Meet compliance needs with free storage.** All telemetry data brought into the SCP is stored for the cost of ingestion for one full year. Leverage this default storage capability to help keep your data storage costs down if your project has data retention or compliance needs.

**Take advantage of discounted pricing.** The SCP provides volume-based discounts as usage increases, as well as annual or multi-year discounts for those ready to commit to longer-term platform usage.

### Build to Scale

**Future-proof your infrastructure.** While open-source or custom-built infrastructure may work early on, its limitations become apparent over time. The complexity, integration challenges, and troubleshooting work that are manageable with a small user base can quickly become untenable at scale. Consider the challenges you will encounter later if you are successful before basing part of your project on a custom or open-source solution.

**Build on a scalable platform.** The SCP is designed to help organizations scale their security operations. Basic assumptions include multitenancy, flexibility, open APIs, and rich automation capabilities. Plan to scale from the outset—leverage the SCP's engineering-centric approach to support future growth by developing architectures, integrations, and workflows that will enable scaling without limits.

**Scale with your revenue.** Leverage the SCP's pay-per-use pricing to scale your infrastructure spending with your revenue. Even if you start with a small customer base, you won't be losing money on infrastructure costs. Conserve your resources and allocate your spending to development, marketing, and sales efforts instead.

## Building Extensions

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Extensions are small services that receive webhooks from LimaCharlie, enabling you to build functionality that organizations can subscribe to and replicate features across tenants.

### Why Extensions?

Building functionality as a LimaCharlie Extension provides specific conveniences:

- **Multi-tenancy**: LC organizations can subscribe to your extension and you can replicate features across tenants
- **Credentials handling**: You don't need to store any credentials from LC organizations. Every callback includes an authenticated LimaCharlie SDK for the relevant Organization with the permissions you requested
- **Configuration**: LC provides a configuration JSON object for your extension (stored in Hive) with a callback for validating configuration modifications
- **GUI**: Each extension defines its own Schema describing what actions it exposes, how to call them, and what to expect as return values. LimaCharlie automatically interprets this to generate a custom user interface, making it easy to expose new functionality without building any UI

### Public/Private Limitations

Anyone can build Extensions for LimaCharlie. The only limit is on making an Extension public. Private extensions require the owner to have the `billing.ctrl` and `user.ctrl` permission on an organization to subscribe the organization to the private extension.

If you'd like to make your extension public (and/or monetize it), reach out to `answers@limacharlie.io`. Once public, an extension is visible by everyone and can be subscribed by everyone.

### High Level Structure

Extensions are small services that receive webhooks from LimaCharlie. This means building an extension requires exposing a small HTTPS service to the internet. We recommend using something like [Google Cloud Run](https://cloud.google.com/run/), but you could also use AWS Lambdas or host on your own hardware.

This HTTPS server communicates with the LimaCharlie cloud according to a simple protocol using JSON. However, you don't need to know the underlying extension protocol as long as you're comfortable with our public implementations.

### Getting Started

We recommend using one of the following frameworks to get started:

- **Golang**: <https://github.com/refractionPOINT/lc-extension>
- **Python**: <https://github.com/refractionPOINT/lc-extension/tree/master/python>

### Extension Definition

To create an extension, start by creating a definition - accessible through the [web interface for your personal add-ons](https://app.limacharlie.io/add-ons/published).

Required aspects of your definition:

- **Destination URL**: The HTTPS URL where your extension will be reachable
- **Required Extensions**: List of other extensions your extension assumes it will have access to. When an org subscribes and is missing one of those, the user will be prompted to subscribe to these
- **Shared Secret**: An arbitrary string (at least 32 characters and random) used by LimaCharlie and your extension to sign webhooks, allowing verification of authenticity
- **Extension Flairs**: Modifiers applied to your extension. The `segment` flair isolates the resources the extension can access so it can only see and modify things (like rules) that it has created—great for extensions needing narrow scope (enable unless you know you need it off). The `bulk` flair tells LimaCharlie to expect many API calls to the LC cloud, increasing the API quota for the extension
- **Permissions**: The list of permissions this extension requires on each organization subscribed to it. Use the least amount of permissions possible

### Schema

The Extension Schema describes what your extension can do and helps define the GUI. Here's an example high-level structure:

```json
{
  "config_schema": {
    "fields": { ... },
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
    }
  },
  "required_events": [
    "subscribe",
    "unsubscribe"
  ]
}
```

#### The Field Configuration

For both `config_schema` and `request_schema`, there is a recurring object structure:

```json
"fields": { .. }, // key-value pair
"requirements": [[]]
```

Each `field` key-value pair shares the same structure with a minimal implementation:

```json
field_name: {
  data_type: "string",
  description: ""
}
```

The `requirements` field references field keys to define whether certain fields individually or as a set are required. Think of the first array as joining elements with AND, while the nested array serves as OR.

Examples:
- `[['denominator'], ['numerator']]` means: (denominator AND numerator)
- `[['denominator'], ['numerator', 'default']]` means: (denominator AND (one of numerator OR default))

When getting started, we recommend using the simplest data type applicable (`string`, `boolean`, `json`, etc.). Afterwards, define the data_type and other optional fields further so the UI may adapt to your defined data types. For more details, see the page on data types or review the code definitions [here](https://github.com/refractionPOINT/lc-extension/blob/master/common/config_schema.go).

#### Config Schema (optional)

The config schema describes what the extension's config should look like when stored as a Hive record in the `extension_configuration` Hive for convenience. Not all extensions will have a configuration.

#### Request Schema

Every Request Schema exists as a key-value pair of the request name and corresponding schema contents. Critical contents include:

- **is_impersonated**: Whether the request impersonates the user through its authentication
- **is_user_facing**: Whether this request should be visible to the user in the UI. It does not prevent this request from being used through the API or as a `supported_action`
- **parameters**: Contains the data_type and other fields (same fields format as the config schema)

Optional fields to facilitate user experience:
- **short_description**
- **long_description**
- **messages**: Includes 3 nested fields—`in_progress`, `success`, `error`—to provide additional context for each case

#### Response Schema (optional)

Each request schema may optionally contain a response schema in the same fields format as a config schema and the request parameters. When getting started, skip this until you are ready to refine the extension's GUI or wish to clarify what kind of response a user should expect.

### Callbacks

Callbacks are functionality that an extension can specify whenever some type of event occurs.

#### Configuration Validation Callback

This callback is used by LimaCharlie to check the validity of a configuration change done in Hive. If the configuration is valid, return success; otherwise, return an error.

#### Event Callback

Events are generated by the LimaCharlie platform outside your control. Currently, these 3 events are supported:

- **subscribe**: Called when an organization subscribes to an extension
- **unsubscribe**: Called when an organization unsubscribes from an extension
- **update**: Called once a day per organization subscribed to the extension. A convenient way to perform updates to an organization like when needing to update D&R rules used by the extension

Your extension will only receive these events if they were specified as of-interest in the extension's Schema.

#### Request Callback

Requests are the core way users, D&R rules, or other extensions can interact with your extension. You can define one callback per `action`. It is common for an extension to have multiple actions, some public (for user-generated requests) and some private (to be used internally by the extension).

### Simplified Frameworks

The Golang implementation of Extensions provides 3 different simplified frameworks to make producing a new extension more straightforward in specific cases: <https://github.com/refractionPOINT/lc-extension/tree/master/simplified>

#### D&R

This simplified framework (found in `dr.go`) allows you to package D&R rules as an extension, making it easy to distribute and update D&R rules to many orgs. Its core mechanism is based on defining the `GetRules()` function and returning a structure like `map[DR-Namespace]map[RuleName]RuleContent`. The simplified framework takes care of recurring updates and everything else.

#### Lookup

Similar to the D&R simplified framework, but used to package Lookups. Example: <https://github.com/refractionPOINT/lc-extension/blob/master/examples/lookup/main.go>

#### CLI

This simplified framework streamlines the integration of 3rd party Command Line Interface tools so they can be automated using LimaCharlie, often bringing bi-directionality to the platform.

## Understanding Organizations

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.