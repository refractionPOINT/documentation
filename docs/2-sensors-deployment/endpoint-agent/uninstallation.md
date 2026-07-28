# Endpoint Agent Uninstallation

You can uninstall the LimaCharlie Sensor in more than one way. The method depends on the operating system and on the installation method. On macOS and Windows, you can uninstall with sensor commands or with rules. Linux systems can need more steps, as described below.

## Manually Uninstalling the Endpoint Agent

To uninstall macOS and Windows Sensors, use a method that is similar to the deployment method. For example, if you deployed the sensors with a package manager, the same package manager can have uninstall options. This keeps software inventories up to date.

The installation procedure for each operating system gives details about manual uninstallation at the end.

## Uninstalling Endpoint Agents from the Platform

### Sensor Commands

For macOS and Windows operating systems, you can uninstall a sensor with the `uninstall` command. See the [endpoint commands reference](../../8-reference/endpoint-commands.md#uninstall) for more detail.

On Windows, the command uninstalls the sensor as if you installed it from the direct installer exe. If you installed the sensor with an MSI, add the `--msi` flag to the `uninstall` command. The flag starts an uninstallation that is compatible with MSI.

#### Native vs Legacy Uninstall

By default, the `uninstall` command uses the legacy procedure. The sensor runs a shell command that calls the uninstaller of the on-disk agent. This works on every sensor version.

The `--native` flag tells the sensor to uninstall itself with its built-in (native) uninstall procedure. The sensor does not start a shell command:

```bash
uninstall --is-confirmed --native
```

!!! note
    The `--native` flag needs sensor version **5.3.3 or later**. A sensor with an older version ignores the native uninstall request without a message. The task looks successful, but nothing occurs on the endpoint. If you do not know the version of a sensor, omit `--native` to use the legacy procedure.

The `--msi` flag takes precedence over `--native`. The native procedure does not unregister the MSI product. For sensors that you installed with an MSI, continue to use `--msi`.

### SDK

To run the uninstall command against *all* Sensors, use a loop with the Python SDK:

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.sensor import Sensor

client = Client()
org = Organization(client)
for sensor_info in org.list_sensors():
    sensor = Sensor(org, sensor_info["sid"])
    sensor.task("uninstall")
```

### Using a D&R Rule

You can also use a Detection & Response (D&R) rule to start an uninstall of the LimaCharlie sensor automatically. The rule runs when a sensor connects to the LimaCharlie cloud. The example rule below is for Windows endpoints, but you can change it for your needs:

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

For Package Management tools, and other enterprise tools that manage applications, use the integrated options that remove programs, and not an installation from LimaCharlie. This keeps software inventories up to date.
