# Hostname Resolution

The Endpoint Agent reports its hostname to the LimaCharlie cloud, where it shows in the `hostname` field for the Sensor.

The Endpoint Agent resolves that hostname in these steps:

1. The Endpoint Agent finds the main local interface. It looks for the route to `8.8.8.8`.
2. The Endpoint Agent calls `getnameinfo()` with `NI_NAMEREQD` to resolve the FQDN of the box.
3. If that hostname is valid, the Endpoint Agent uses it. The hostname is valid if the call does not fail, and if the hostname is not the static hostname of one of a few VPN and virtualization providers.
4. If the Endpoint Agent cannot resolve the FQDN, it uses the local hostname of the box.

This method helps the Endpoint Agent to resolve its hostname in large environments where different regions use the same hostname.

## Disabling Reverse DNS Resolution

In some environments, the reverse DNS lookup is not wanted. For example, the lookup is slow, or it is unreliable, or it gives a hostname that has no meaning for the deployment. To disable the reverse DNS step, set this environment variable on the host before the Endpoint Agent starts:

```text
LC_DISABLE_REVERSE_DNS_HOSTNAME=1
```

Set the variable to `1` or `true` (case-insensitive). A variable with an empty value or a different value is not enough, and the Endpoint Agent treats it as disabled. When the variable is enabled, the Endpoint Agent skips steps 2 and 3 above and uses the local hostname of the box (step 4).

For an Endpoint Agent that is installed and runs as a service, set the variable in the service manager (launchd plist, systemd unit, or the Windows service). Then restart the service. For the procedure for each platform, see [Setting Environment Variables for an Installed Service](cli-reference.md#setting-environment-variables-for-an-installed-service).
