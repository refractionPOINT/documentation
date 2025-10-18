# PagerDuty

The PagerDuty Extension allows you to trigger events within PagerDuty. It requires you to setup the PagerDuty access token in the Integrations section of your Organization.

Some more detailed information is available [here](https://developer.pagerduty.com/docs/events-api-v2/trigger-events/).

### REST

#### Trigger Event


    {
      "summary": "Critical credentials theft alert.",
      "source": "limacharlie.io",
      "severity": "critical",
      "component": "dr-creds-theft",
      "group": "lc-alerts",
      "class": "dr-rules"
    }


### PagerDuty Configuration

On the PagerDuty side, you need to configure your PagerDuty service to receive the API notifications:

  1. In your Service, go to the "Integrations" tab.

  2. Click "Add a new integration".

  3. Give it a name, like "LimaCharlie".

  4. In the "Integration Type" section, select the radio button "Use our API directly" and select "Events API v2" from the dropdown.

  5. Click "Add integration".

  6. Back in the "Integrations" page, you should see your new integration in the list. Copy the "Integration Key" to your clipboard and add it in the "Integrations" section of LimaCharlie for PagerDuty.

From this point on, you may use a  rule to trigger a PagerDuty event. For example the following rule "response":


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


### Migrating D&R Rule from legacy Service to new Extension

** _LimaCharlie is migrating away from Services to a new capability called Extensions. Support of legacy services will end on June 30, 2024._**

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a direct way to assess if any rules reference legacy PagerDuty service, preview the change and execute the conversion required in the rule "response".

Command line to preview PagerDuty rule conversion:


    limacharlie extension convert_rules --name ext-pagerduty


A dry-run response (default) will display the rule name being changed, a JSON of the service request rule and a JSON of the incoming extension request change.

To execute the change in the rule, explicitly set `--dry-run` flag to `--no-dry-run`

Command line to execute PagerDuty rule conversion:


    limacharlie extension convert_rules --name ext-pagerduty --no-dry-run


LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.
