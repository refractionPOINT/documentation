# Reference: Sensor Selector Expressions

Many components in LimaCharlie require selecting a set of Sensors based on some characteristics. The selector expression is a text field that describe what matching characteristics the selector is looking for.

The following fields are available in this evaluation:

* `sid`: the Sensor ID
* `oid`: the Organization ID
* `iid`: the Installation Key ID
* `plat`: the Platform name (see [platforms](./reference-id-schema.md#platform))
* `ext_plat`: the Extended Platform name (see [platforms](./reference-id-schema.md#platform))
* `arch`: the Architecture name (see [architectures](./reference-id-schema.md#architecture))
* `enroll`: the Enrollment as a second epoch timestamp
* `hostname`: the hostname
* `mac_addr`: the latest MAC address
* `alive`: second epoch timestamp of the last time the Sensor connected to the cloud
* `ext_ip`: the last external IP
* `int_ip` the last internal IP
* `isolated`: a boolean True if the sensor's network is isolated
* `should_isolate`: a boolean True if the sensor is marked to be isolated
* `kernel`: a boolean True if the sensor has some sort of "kernel" enhanced visibility
* `did`: the Device ID the sensor belongs to
* `tags`: the list of tags the sensor currently has

The following are the available operators:

* `==`: equals
* `!=`: not equal
* `in`: element in list, or substring in string
* `not in`: element not in list, or substring not in string
* `matches`: element matches regular expression
* `not matches`: element does not match regular expression
* `contains`: string is contained within element

Here are some examples:

* all sensors with the test tag: `test in tags`
* all windows boxes with an internal IP starting in 10.3.x.x: `` plat == windows and int_ip matches `^10\.3\..*` ``
* all 1password sensors, strings starting with a number need to be quoted with a backtick: `` plat == `1password` ``
* all linux with network isolation or evil tag: `plat == linux or (isolated == true or evil in tags)`
* all azure related platforms: `plat contains "azure"`
