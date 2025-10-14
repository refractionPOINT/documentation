# Endpoint Agent Uninstallation

There are multiple options available to uninstall the LimaCharlie Sensor, depending on the operating system and/or method of installation. macOS and Windows systems allow for easy uninstallation via sensor commands or rules. Linux systems may require additional steps, as detailed below.

## Manually Uninstalling the Endpoint Agent

When uninstalling macOS and Windows Sensors, please attempt to utilize a method similar to sensor deployment. For example, if sensors were deployed via a package manager, then the same package manager may have uninstall options as well. This will help keep software inventories up to date.

Details on manual uninstallation is found at the bottom of each respective OS' installation procedures.

## Uninstalling Endpoint Agents from the Platform

### Sensor Commands

For macOS and Windows operating systems, you can uninstall a sensor with the `uninstall` command. More information on that can be found [here](/v2/docs/endpoint-agent-commands#uninstall).

On Windows, the command defaults to uninstalling the sensor as if installed from the direct installer exe. If an MSI was used for installation, you can add a `--msi` flag to the `uninstall` command to trigger an uninstallation that is compatible with MSI.

### SDK

To run the uninstall command against *all* Sensors, a simple loop with the SDK in Python would work:

```python
import limacharlie
lc = limacharlie.Manager()
for sensor in lc.sensors():
  sensor.task( 'uninstall' )
```

### Using a D&R Rule

As an alternative approach, you can also use a Detection & Response (D&R) rule to automatically trigger an uninstall of the LimaCharlie sensor when a sensor connects to the LimaCharlie cloud. Below is an example of the rule you can use for this purpose. This example is specific to Windows-based endpoints, but can be modified based on your needs:

```yaml
# Detect
event: SYNC
op: is windows

# Respond
- action: task
  command: uninstall --is-confirmed
- action: add tag
  tag: uninstalled
```

## Package Management Tools

For Package Management tools, and other enterprise application-management tools, we recommend utilizing the integrated program removal options, rather than installing from LimaCharlie. This will help keep software inventories up to date.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.