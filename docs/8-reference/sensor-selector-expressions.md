# Reference: Sensor Selector Expressions

Many components in LimaCharlie must select a set of Sensors by their characteristics. The selector expression is a text field that describes the characteristics that the selector matches.

These fields are available in this evaluation:

- `sid`: the Sensor ID
- `oid`: the Organization ID
- `iid`: the Installation Key ID
- `plat`: the Platform name (see [platforms](id-schema.md#platform))
- `ext_plat`: the Extended Platform name (see [platforms](id-schema.md#platform))
- `arch`: the Architecture name (see [architectures](id-schema.md#architecture))
- `enroll`: the Enrollment as a second epoch timestamp
- `hostname`: the hostname
- `mac_addr`: the latest MAC address
- `alive`: second epoch timestamp of the last time the Sensor connected to the cloud
- `ext_ip`: the last external IP
- `int_ip` the last internal IP
- `isolated`: a boolean True if the sensor's network is isolated
- `should_isolate`: a boolean True if the sensor is marked to be isolated
- `kernel`: a boolean True if the sensor has some sort of "kernel" enhanced visibility
- `did`: the Device ID that the sensor belongs to
- `tags`: the list of tags that the sensor has now

These operators are available:

- `==`: equals
- `!=`: not equal
- `in`: element in list, or substring in string
- `not in`: element not in list, or substring not in string
- `matches`: element matches regular expression
- `not matches`: element does not match regular expression
- `contains`: string is contained within element

Here are some examples:

- all sensors with the test tag: `test in tags`
- all windows hosts with an internal IP that starts with 10.3.x.x: `` plat == windows and int_ip matches `^10\.3\..*` ``
- all 1password sensors; you must put a backtick around a string that starts with a number: `` plat == `1password` ``
- all linux with network isolation or evil tag: `plat == linux or (isolated == true or evil in tags)`
- all azure related platforms: `plat contains "azure"`

In LimaCharlie, a Sensor ID is a unique identifier for each deployed sensor. It separates individual sensors across the infrastructure of an organization, and lets LimaCharlie track, manage, and communicate with each endpoint. The Sensor ID is critical when LimaCharlie sends commands, collects telemetry, and monitors activity. It links actions and data to a specific device or endpoint.

In LimaCharlie, an Organization ID is a unique identifier for each tenant or customer account. It separates the organizations in the platform, and lets LimaCharlie manage resources, permissions, and data segregation securely. The Organization ID keeps all telemetry, configurations, and operations isolated and specific to each organization. It gives multi-tenant support and a clear separation between customer environments.

Installation keys are Base64-encoded strings that you give to Sensors and Adapters to associate them with the correct Organization. You create installation keys for each organization. Use them to label and control your deployment population.

Sensors send telemetry to the LimaCharlie platform as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless solution that connects the endpoints of an organization to the cloud securely.
