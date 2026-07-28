# PagerDuty

The PagerDuty Extension lets you trigger events in PagerDuty. First, set the PagerDuty access token in the Integrations section of your Organization.

For more information, see the PagerDuty [Events API v2 trigger reference](https://developer.pagerduty.com/docs/events-api-v2/trigger-events/).

## REST

### Trigger Event

```json
{
  "summary": "Critical credentials theft alert.",
  "source": "limacharlie.io",
  "severity": "critical",
  "component": "dr-creds-theft",
  "group": "lc-alerts",
  "class": "dr-rules"
}
```

### PagerDuty Configuration

In PagerDuty, configure your PagerDuty service to receive the API notifications:

1. In your Service, go to the "Integrations" tab.
2. Click "Add a new integration".
3. Give it a name, like "LimaCharlie".
4. In the "Integration Type" section, select the radio button "Use our API directly" and select "Events API v2" from the dropdown.
5. Click "Add integration".
6. Go back to the "Integrations" page. The new integration is in the list. Copy the "Integration Key". Add the key in the "Integrations" section of LimaCharlie for PagerDuty.

You can now use a rule to trigger a PagerDuty event. This example shows a rule "response":

```yaml
- action: extension request
  extension action: run
  extension name: ext-pagerduty
  extension request:
       class: '{{ "dr-rules" }}'
       group: '{{ "lc-alerts" }}'
       severity: '{{ "critical" }}'
       source: '{{ "LimaCharlie" }}'
       component: '{{ "dr-creds-theft" }}'
       summary: '{{ .routing.hostname }} - {{ .routing.sid }} - {{ .cat }}'
       details: '{{ .event }}'
```

> **Important — put literal strings in `{{ "..." }}`.**
> The extension evaluates the values under `extension request` as templates. A bare string without `{{ }}` is a [gjson](https://github.com/tidwall/gjson) path into the event. If the path does not resolve, the extension removes the key from the payload without a message. For this reason, each literal above is written as `'{{ "..." }}'`. The required fields (`summary`, `source`, `severity`) are the most important. If one of these keys is removed, PagerDuty rejects the request with `missing one of <field>`.

### Pass-through `parameters` block

To add more detail to a PagerDuty incident, supply an optional `parameters` block with the flat fields. The extension puts each known key in its correct place in the [V2 event payload](https://developer.pagerduty.com/docs/events-api-v2/trigger-events/). It merges each unknown key into `custom_details`, so no data is lost.

| Key | Type | Where it goes |
| --- | --- | --- |
| `custom_details` | object | `payload.custom_details` |
| `links` | list of `{ href, text }` | top-level `links` |
| `images` | list | top-level `images` |
| `timestamp` | string (ISO 8601) | `payload.timestamp` |
| `client` | string | top-level `client` |
| `client_url` | string | top-level `client_url` |
| `dedup_key` | string | top-level `dedup_key` |

This example has a link back to LimaCharlie and a dedup key that uses the detection:

```yaml
- action: extension request
  extension action: run
  extension name: ext-pagerduty
  extension request:
    severity: '{{ "warning" }}'
    source: '{{ "limacharlie.io" }}'
    summary: '{{ .cat }} - {{ .routing.hostname }} - Threat level {{ .detect_mtd.level }}'
    parameters:
      custom_details:
        oid:   '{{ .routing.oid }}'
        sid:   '{{ .routing.sid }}'
        event: '{{ .detect.event }}'
      links:
        - href: '{{ .link }}'
          text: '{{ "Open in LimaCharlie" }}'
      client:     '{{ "LimaCharlie" }}'
      client_url: '{{ .link }}'
      dedup_key:  '{{ .cat }}-{{ .routing.sid }}'
  suppression:
    is_global: true
    keys:
      - '{{ .cat }}'
    max_count: 30
    period: 1h
```

### Migrating D&R Rule from legacy Service to new Extension

***Note: LimaCharlie moved from Services to Extensions. Legacy services are not supported.***

Use the [Python CLI](https://github.com/refractionPOINT/python-limacharlie) to find the rules that reference the legacy PagerDuty service. The CLI also shows a preview of the change and does the conversion in the rule "response".

Command line to preview PagerDuty rule conversion:

```bash
limacharlie extension convert_rules --name ext-pagerduty
```

A dry run is the default. It shows the name of the rule that changes, a JSON of the service request rule, and a JSON of the new extension request.

To do the change in the rule, set the `--dry-run` flag to `--no-dry-run`.

Command line to execute PagerDuty rule conversion:

```bash
limacharlie extension convert_rules --name ext-pagerduty --no-dry-run
```

LimaCharlie Extensions let users expand and customize their security environments. Extensions integrate third-party tools, automate workflows, and add new capabilities. Organizations subscribe to Extensions, and each Extension gets specific permissions to interact with the infrastructure of the organization. An Extension can be private or public, for use in one organization or for the full community. This framework supports scale, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization is a tenant in the SecOps Cloud Platform. It gives a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives full control of security operations. This structure supports flexible, multi-tenant setups for managed security providers, and for enterprises that manage many departments or clients.
