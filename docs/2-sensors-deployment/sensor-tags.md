# Sensor Tags

Tags in LimaCharlie are strings that you can associate with any number of sensors. A Sensor can also have any number of tags.

Tags appear in each event that comes from a sensor, in the `routing` component of the event. This makes it much easier to write detection and response rules that test for specific tags. The cost is more non-unique data in each event.
You can use tags for many purposes:

- to classify endpoints
- automate detection and response
- create workflows
- trigger automations

## Use Cases for Sensor Tags

### Classification

You can classify an endpoint with tags in many ways, based on what is important to you. The examples below show some classifications.

#### Departments

Create tags that classify endpoints by their business department. For example: sales, finance, operations, development, support, legal, executives.

#### Usage Type

You can also tag endpoints by their type of usage. For example: workstation, server, production, staging.

Tags of this type help you identify endpoints and decide which actions to take. For example, an endpoint has the tags `workstation` and `executives`. If you see suspicious activity on that endpoint, give the response a higher priority.

### Automating detection and response

You can use tags to automate detection and response.

For example, create a detection & response rule for the login of a specific user on a device. The rule tags the device as `VIP-sales`. The sensor then collects an extended list of events from that device.

### Creating workflows

You can use tags to create workflows and automations. For example, configure an output (forwarder) that sends all detections with the `VIP-sales` tag to Slack for immediate review. Send the detections with the `sales` tag to an email address.

### Trigger Automations

Create a Yara scanning rule that scans the endpoints with the 'sales' tag continuously against specific sets of Yara signatures.

## Adding Tags

You can add tags to a sensor in these ways:

1. Enrollment: an installation key can have an optional list of Tags. The cloud applies these tags to the sensors that use the key.
2. Manually: use the API as described below, either by a person or through another integration.
3. Detection & Response: automated detection and response rules can add a tag programmatically, and can check for tags.

### Manual API

Issue a `POST` to the `/{sid}/tags` REST endpoint

### Detection & Response

In detection and response rules. In the response part of the detection & response rule, specify the add tag action. For example, to tag a device as DESKTOP, write:

```yaml
- action: add tag
tag: DESKTOP
```

## Removing Tags

### Manual API

Issue a `DELETE` to the `/{sid}/tags` REST endpoint

### Detection & Response

In detection and response rules

### Manual in the web app

In the web app, click the sensor to expand it. The web app shows the list of tags that you can add, edit, or remove.

## Checking Tags

### Manual API

Issue a `GET` to the `/{sid}/tags` REST endpoint

### Detection & Response

In detection and response rules

## System Tags

LimaCharlie gives system level functionality with some system tags. The list below is for reference:

### lc:latest

When you tag a sensor with `lc:latest`, that sensor ignores the sensor version that is assigned to the Organization. It uses the latest version of the sensor instead. Tag a representative set of computers in the Organization with the `lc:latest` tag. You can then test-deploy the latest version and confirm that it has no negative effects.

### lc:stable

When you tag a sensor with `lc:stable`, that sensor ignores the sensor version that is assigned to the Organization. It uses the *stable* version of the sensor instead. You can upgrade an organization as a whole, but keep a few specific sensors behind with the lc:stable tag.

### lc:experimental

When you tag a sensor with `lc:experimental`, that sensor ignores the sensor version that is assigned to the Organization. It uses an experimental version of the sensor instead. Use this tag when you work with the LimaCharlie team to troubleshoot a problem in a sensor.

### lc:no_kernel

When you tag a sensor with `lc:no_kernel`, the sensor does not load the kernel component on the host.

### lc:debug

When you tag a sensor with `lc:debug`, that sensor uses the debug version of the sensor version that is assigned to the Organization.

### lc:limit-update

When you tag a sensor with lc:limit-update, the sensor does not update its version at run-time. The sensor loads the version only when it starts from scratch, for example after a reboot.

### lc:sleeper

When you tag a sensor with *lc:sleeper*, the sensor keeps its connection to the LimaCharlie Cloud. It disables all other functionality so that it has no impact on the system. To wake sensors from sleeper mode, set the Quota of your organization for the number of sensors that you want to activate. Then remove the `lc:sleeper` tag from those sensors. For more details, see [Sleeper Deployments](endpoint-agent/sleeper.md).

Similar to agents, Sensors send telemetry to the LimaCharlie platform as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless solution that connects the endpoints of an organization to the cloud securely.

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives you complete control of security operations. This structure supports flexible, multi-tenant setups for managed security providers, and for enterprises that manage many departments or clients.

## Programmatic Management

!!! info "Prerequisites"
    All programmatic examples need an API key with `sensor.tag` permissions. See [API Keys](../7-administration/access/api-keys.md) for setup instructions.

### List All Organization Tags

=== "REST API"

    ```bash
    curl -s -X GET "https://api.limacharlie.io/v1/tags/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    tags = org.get_all_tags()
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    tags, err := org.GetAllTags()
    ```

=== "CLI"

    ```bash
    limacharlie tag list
    ```

### List Tags for a Sensor

=== "REST API"

    ```bash
    curl -s -X GET "https://api.limacharlie.io/v1/YOUR_SID/tags" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.sensor import Sensor

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    sensor = Sensor(org, "YOUR_SID")
    tags = sensor.get_tags()
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    sensor := org.GetSensor("YOUR_SID")
    tags, err := sensor.GetTags()
    ```

=== "CLI"

    ```bash
    limacharlie tag list --sid YOUR_SID
    ```

### Add a Tag to a Sensor

=== "REST API"

    ```bash
    curl -s -X POST "https://api.limacharlie.io/v1/YOUR_SID/tags" \
      -H "Authorization: Bearer $LC_JWT" \
      -d "tags=my-tag&ttl=3600"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.sensor import Sensor

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    sensor = Sensor(org, "YOUR_SID")
    sensor.add_tag("my-tag", ttl=3600)
    ```

=== "Go"

    ```go
    import (
        "time"
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    sensor := org.GetSensor("YOUR_SID")
    err := sensor.AddTag("my-tag", time.Hour)
    ```

=== "CLI"

    ```bash
    limacharlie tag add --sid YOUR_SID --tag my-tag --ttl 3600
    ```

### Remove a Tag from a Sensor

=== "REST API"

    ```bash
    curl -s -X DELETE "https://api.limacharlie.io/v1/YOUR_SID/tags" \
      -H "Authorization: Bearer $LC_JWT" \
      -d "tag=my-tag"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.sensor import Sensor

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    sensor = Sensor(org, "YOUR_SID")
    sensor.remove_tag("my-tag")
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    sensor := org.GetSensor("YOUR_SID")
    err := sensor.RemoveTag("my-tag")
    ```

=== "CLI"

    ```bash
    limacharlie tag remove --sid YOUR_SID --tag my-tag
    ```

### Find Sensors by Tag

=== "REST API"

    ```bash
    curl -s -X GET "https://api.limacharlie.io/v1/tags/YOUR_OID/my-tag" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    sensors = org.find_sensors_by_tag("my-tag")
    ```

=== "Go"

    ```go
    import limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"

    client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
        OID:    "YOUR_OID",
        APIKey: "YOUR_API_KEY",
    }, nil)
    org, _ := limacharlie.NewOrganization(client)

    sensors, err := org.GetSensorsWithTag("my-tag")
    ```

=== "CLI"

    ```bash
    limacharlie tag find --tag my-tag
    ```

### Mass Add Tag by Selector

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    result = org.mass_tag('plat == "windows"', "my-tag", ttl=3600)
    ```

=== "CLI"

    ```bash
    limacharlie tag mass-add --selector 'plat == "windows"' --tag my-tag
    ```

### Mass Remove Tag by Selector

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    result = org.mass_untag('plat == "windows"', "my-tag")
    ```

=== "CLI"

    ```bash
    limacharlie tag mass-remove --selector 'plat == "windows"' --tag my-tag
    ```

---

## See Also

- [D&R Rules with Tags](../3-detection-response/index.md)
- [Sensor Selectors](../8-reference/sensor-selector-expressions.md)
- [Python SDK](../6-developer-guide/sdks/python-sdk.md)
- [Go SDK](../6-developer-guide/sdks/go-sdk.md)
- [Compliance Frameworks](../9-ai-sessions/compliance/frameworks.md) -- Scope-tag conventions for each framework (`cde` for PCI, `ephi-host` for HIPAA, `cui` for CMMC, `fisma-scope` for NIST 800-53, and others). The compliance reviewer agents use these tags for their in-scope check.
