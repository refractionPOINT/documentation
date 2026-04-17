# Hostname Resolution

The Endpoint Agent reports its hostname to the LimaCharlie cloud where it shows up as the `hostname` field for the Sensor.

The resolution of that hostname is done in a few different ways:

1. The main local interface is detected by looking for the route to `8.8.8.8`.
2. A `getnameinfo()` with `NI_NAMEREQD` is performed to resolve the FQDN of the box.
3. If the above hostname resolved is valid (no failure, and it is not equal to the static hostname of a few VPN and virtualization providers), this is the hostname we use.
4. If the FQDN could not be resolved, the local hostname of the box is used.

This method allows the endpoint agent to better resolve its hostname in large environments where different regions re-use the same hostname.

## Disabling Reverse DNS Resolution

In some environments the reverse DNS lookup is undesirable (for example, when it is slow, unreliable, or returns a hostname that is not meaningful for the deployment). The reverse DNS step can be disabled by setting the following environment variable on the host before the Endpoint Agent starts:

```
LC_DISABLE_REVERSE_DNS_HOSTNAME=1
```

The variable must be explicitly set to `1` or `true` (case-insensitive) — simply defining the variable with an empty or other value is not enough and will be treated as disabled. When enabled, the agent skips steps 2 and 3 above and directly uses the local hostname of the box (step 4).
