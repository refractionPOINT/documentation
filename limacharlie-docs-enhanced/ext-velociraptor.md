# Detection
op: is
path: routing/log_type
target: artifact_event
value: velociraptor

# Response
- action: output
  name: artifacts-tailored
  suppression:
    is_global: false
    keys:
        - '{{ .event.original_path }}'
        - '{{ .routing.log_id }}'
    max_count: 1
    period: 1m
- action: report
  name: VR artifact ingested
```

To see how you could use something like this to automate post-processing of Velociraptor triage collections, check out this [open source example](https://github.com/shortstack/lcvr-to-timesketch) which sends KAPE Triage acquisitions to a webhook which then retrieves the collection for processing via [Plaso](https://github.com/log2timeline/plaso/) and into [Timesketch](https://github.com/google/timesketch).

To see how you can send Velociraptor data to BigQuery for further analysis, see this [tutorial](/v2/docs/velociraptor-to-bigquery).

## Using Velociraptor in D&R Rules

If you want to trigger a Velociraptor collection as a response to one of your detections, you can configure an extension request in the respond block of a rule.

This example will kick off the KAPE files Velociraptor artifact to collect event logs from the system involved in the detection.

```
- action: extension request
  extension action: collect
  extension name: ext-velociraptor
  extension request:
    artifact_list: ['Windows.KapeFiles.Targets']
    sid: '{{ .routing.sid }}' # Use a sensor selector OR a sid, **not both**
    sensor_selector: '' # Use a sensor selector OR a sid, **not both**
    args: '{{ "EventLogs=Y" }}'
    collection_ttl: 3600 # 1 hour - collection_ttl is specified in seconds
    retention_ttl: 7 # retention_ttl is specified in days
    ignore_cert: false
```

### Migrating D&R Rule from legacy Service to new Extension

***LimaCharlie is migrating away from Services to a new capability called Extensions. Support of legacy services will end on June 30, 2024.***

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a direct way to assess if any rules reference legacy Velociraptor service, preview the change and execute the conversion required in the rule "response".

Command line to preview Velociraptor rule conversion:

```
limacharlie extension convert_rules --name ext-velociraptor
```

A dry-run response (default) will display the rule name being changed, a JSON of the service request rule and a JSON of the incoming extension request change.

To execute the change in the rule, explicitly set `--dry-run` flag to `--no-dry-run`

Command line to execute Velociraptor rule conversion:

```
limacharlie extension convert_rules --name ext-velociraptor --no-dry-run
```

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

In LimaCharlie, a Sensor ID is a unique identifier assigned to each deployed endpoint agent (sensor). It distinguishes individual sensors across an organization's infrastructure, allowing LimaCharlie to track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as sending commands, collecting telemetry, and monitoring activity, ensuring that actions and data are accurately linked to specific devices or endpoints.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.