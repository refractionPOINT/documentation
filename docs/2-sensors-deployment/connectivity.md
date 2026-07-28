# Sensor Connectivity

The network connection that the LimaCharlie Sensor needs is simple. The sensor needs one TCP connection over port 443 to a specific domain. Optionally, it also needs another destination for the [Artifact Collection](../4-data-queries/events/index.md) service.

The Sensor Downloads section of the dashboard for your Organization lists the specific domains. The domains change with the datacenter that you chose for your organization. To find your domains, see the screenshots below.

Web proxies are not supported at this time. LimaCharlie needs one connection to one dedicated domain, so you can add one safe exception.

## Proxy Tunneling

The LimaCharlie sensor supports unauthenticated proxy tunneling through [HTTP CONNECT](https://en.wikipedia.org/wiki/HTTP_tunnel).

The LimaCharlie connection goes through the proxy in an opaque way, because the sensor does not support SSL interception.

To enable this feature, set the `LC_PROXY` environment variable to the DNS name or the hostname of the proxy. For example: `LC_PROXY=proxy.corp.com:8080`.

### Windows

On Windows, you can use a simple auto-detection of a global, unauthenticated proxy.

To enable this, set the same environment variable to the `-` value, like `LC_PROXY=-`. The sensor then reads the registry key `HKLM\Software\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\ProxyServer` and uses its value as the proxy destination.

Also on Windows, changes to an environment variable sometimes do not propagate to all processes. A reboot of the machine usually corrects this. If you cannot reboot the machine, set the `LC_PROXY` variable to `!` (exclamation mark). This value disables the proxy. Deletion of the variable is usually problematic, but a new value works.

## Certificate Revocation Checks on Restricted Networks (Windows)

On Windows, the sensor does certificate revocation checks when it verifies code signatures. These checks can try to reach CRL/OCSP endpoints on the network. On air-gapped or tightly restricted networks, these lookups can stall or fail.

Set the `LC_LOCAL_CACHE_ONLY_REVOCATION_CHECK` environment variable to `1` (or `true`) on the sensor process. The revocation checks then use only the local cache and do not use the network.

Like agents, Sensors send telemetry to the LimaCharlie platform as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless method to connect the endpoints of an organization to the cloud in a secure way.

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives full control of security operations. This structure supports multi-tenant setups for managed security providers, or for enterprises that manage many departments or clients.
