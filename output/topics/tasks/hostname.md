# Hostname Resolution

The Endpoint Agent reports its hostname to the LimaCharlie cloud where it shows up as the `hostname` field for the Sensor.

The resolution of that hostname is done in a few different ways:

1. The main local interface is detected by looking for the route to `8.8.8.8`.
2. A `getnameinfo()` with `NI_NAMEREQD` is performed to resolve the FQDN of the box.
3. If the above hostname resolved is valid (no failure, and it is not equal to the static hostname of a few VPN and virtualization providers), this is the hostname we use.
4. If the FQDN could not be resolved, the local hostname of the box is used.

This method allows the endpoint agent to better resolve its hostname in large environments where different regions re-use the same hostname.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.