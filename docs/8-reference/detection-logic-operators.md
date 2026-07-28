# Detection Logic Operators

You use operators in the Detection part of a Detection & Response rule. An operator can also have other parameters, such as transforms and times. This page describes these parameters below.

> For more information on how to use operators, read [Detection & Response Rules](../3-detection-response/index.md).

## Operators

### and, or

These are the standard boolean operations that combine other logical operations. Each takes one `rules:` parameter that contains a list of other operators to combine with "AND" or "OR".

Example:

```yaml
op: or
rules:
  - ...rule1...
  - ...rule2...
  - ...
```

### is

Tests if the value of the `"value": <>` parameter is equal to the value in the event at the `"path": <>` parameter.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms, [lookbacks](#lookbacks), and [sensor variables](../3-detection-response/sensor-variables.md).

Example rule:

```yaml
event: NEW_PROCESS
op: is
path: event/PARENT/PROCESS_ID
value: 9999
```

### exists

Tests if any element exists at the given path, whatever its value.

Example rule:

```yaml
event: NEW_PROCESS
op: exists
path: event/PARENT
```

The `exists` operator also supports an optional `truthy` parameter. If it is `true`, `exists` treats `null` and `""` (empty string) values as values that do not exist. For example:

The rule:

```yaml
op: exists
path: some/path
truthy: true
```

applied to:

```json
{
  "some": {
    "path": ""
  }
}
```

would NOT match.

### contains

The `contains` operator checks if a substring is in the value at the path.

Add the optional parameter `count: 3` to match only if the substring is in the
path *at least* 3 times.

Add the optional parameter `case sensitive: false` for case-insensitive matching. The default is `true`.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

Example rule:

```yaml
event: NEW_PROCESS
op: contains
path: event/COMMAND_LINE
value: reg
count: 2
```

### ends with, starts with

The `starts with` operator checks for a prefix match. The `ends with` operator checks for a suffix match.

Both operators check the value at `path` against the given `value`.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

### is greater than, is lower than

Check if a value is numerically greater or lower than a value in the event.

Both operators use the `path` and `value` parameters. Both also support the `length of` parameter as a boolean (true or false). If it is true, the operator
compares the length of the value at the path instead of the value.

### matches

The `matches` operator compares the value at `path` with a regular expression from the `re` parameter. It uses the Golang [`regexp` package](https://golang.org/pkg/regexp/), which also lets you apply the regexp to log files.

**Note**: Unlike other operators, `matches` uses **case-insensitive** matching by default. To change this, set `case sensitive: true`.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

Example:

```yaml
event: FILE_TYPE_ACCESSED
op: matches
path: event/FILE_PATH
re: .*\\system32\\.*\.scr
case sensitive: false
```

### not

The `not` operator inverts the result of its rule. With an `is` operator, it changes the logic from "equals" to "does not equal". With an or operator, it changes the logic from "any of these conditions are true" to "none of these conditions are true"

Example:

```yaml
event: NEW_PROCESS
op: is
not: true
path: event/PARENT/PROCESS_ID
value: 9999
```

### string distance

The `string distance` operator calculates the [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance) between two strings. This is the minimum number of character changes that make one string equal to the other.

For example, the Levenshtein Distance between `google.com` and `googlr.com` (`r` instead of `e`) is 1.

Use this operator to find variations of file names or domain names that an attacker can use for phishing.

For example, your company is `onephoton.com`. The operator compares each `DOMAIN_NAME` in `DNS_REQUEST` events to `onephoton.com`. It can then detect an attacker that uses `onephot0n.com` as a phishing email domain.

The `path` parameter gives the field to compare. The `max` parameter gives the maximum Levenshtein Distance to match. The `value` parameter is a string, or a list of strings, to compare against. `string distance` allows `value` to be a list, but most other operators do not.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

Example:

```yaml
event: DNS_REQUEST
op: string distance
path: event/DOMAIN_NAME
value:
  - onephoton.com
  - www.onephoton.com
max: 2
```

This would match `onephotom.com` and `0nephotom.com` but NOT `0neph0tom.com`.

This example uses the [file name](#file-name) transform on a file name in a path:

```yaml
event: NEW_PROCESS
op: string distance
path: event/FILE_PATH
file name: true
value:
  - svchost.exe
  - csrss.exe
max: 2
```

This would match `svhost.exe` and `csrss32.exe` but NOT `csrsswin32.exe`.

### is 32 bit, is 64 bit, is arm

These operators take no more arguments. They match if the relevant Sensor characteristic is correct.

Example:

```yaml
op: is 64 bit
```

### is platform

Checks if the event under evaluation is from a sensor of the given platform.

Takes a `name` parameter for the platform name. The current platforms are:

**Endpoint Platforms:**

- `windows`
- `linux`
- `macos`
- `ios`
- `android`
- `chrome`

**Cloud & Service Platforms:**

- `gcp` (Google Cloud Platform)
- `aws` (Amazon Web Services)
- `azure_ad` (Azure Active Directory)
- `azure_event_hub_namespace`
- `azure_key_vault`
- `azure_kubernetes_service`
- `azure_monitor`
- `azure_network_security_group`
- `azure_sql_audit`
- `guard_duty` (AWS GuardDuty)
- `k8s_pods` (Kubernetes)

**Identity & Access Management:**

- `1password`
- `bitwarden`
- `duo`
- `entraid` (Microsoft Entra ID)
- `okta`
- `sublime`

**Security Products:**

- `carbon_black`
- `cortex_xdr` (Palo Alto Cortex XDR)
- `crowdstrike`
- `cylance`
- `falconcloud`
- `harmony` (Check Point Harmony)
- `msdefender` (Microsoft Defender)
- `sentinel_one`
- `sophos`
- `threatlocker`
- `trend_micro`
- `trend_worryfree`
- `wiz`

**Communication & Collaboration:**

- `box`
- `github`
- `office365`
- `slack`
- `email`

**IT & Business Services:**

- `halopsa` (HaloPSA)
- `hubspot`
- `itglue`
- `mimecast`
- `pandadoc`
- `proofpoint`
- `zendesk`

**Network & Infrastructure:**

- `canary_token`
- `fortigate`
- `iis` (Internet Information Services)
- `netscaler`
- `paloalto_fw` (Palo Alto Firewall)
- `zeek`

**Data Formats:**

- `vpn`
- `text`
- `json`
- `xml`
- `cef` (Common Event Format)
- `wel` (Windows Event Log)
- `mac_unified_logging`
- `otel` (OpenTelemetry)

**Other:**

- `lc_event` (LimaCharlie internal events)

Example:

```yaml
op: is platform
name: 1password
```

Note: Platform names are case-sensitive and should be lowercase.

### is tagged

Checks if the sensor that sent the event under evaluation already has the Tag from the `tag` parameter.

### lookup

Looks up a value against a [lookup add-on](https://app.limacharlie.io/add-ons/category/lookup) (also called a resource), such as a threat feed.

```yaml
event: DNS_REQUEST
op: lookup
path: event/DOMAIN_NAME
resource: hive://lookup/malwaredomains
case sensitive: false
```

This rule gets the `event/DOMAIN_NAME` of a `DNS_REQUEST` event. It then checks if that value is a member of the `lookup` named `malwaredomains`. If it is, the rule is a match.

The `path` parameter gives the value, and the `resource` parameter defines the lookup. A resource has the form `hive://lookup/RESOURCE_NAME`. To access a lookup, your Organization must be subscribed to it.

Supports the [file name](#file-name) and [sub domain](#sub-domain) transforms.

> API-based lookups, such as VirusTotal and IP Geolocation, operate differently. For more information, see [Using API-based lookups](../5-integrations/api-integrations/index.md).
>
> You can create your own lookups, and you can publish them in the add-on marketplace. For more information, see [Lookups](../7-administration/config-hive/lookups.md) and [Lookup Manager](../5-integrations/extensions/limacharlie/lookup-manager.md).

### scope

Sometimes you want to limit the matching and the `path` that you use to one part of the event. The `scope` operator does this. It resets the root of the `event/` in paths to a sub-path of the event.

This is useful when you test many values of a connection in a `NETWORK_CONNECTIONS` event, but always for each connection. Look at this rule:

```yaml
event: NETWORK_CONNECTIONS
op: and
rules:
  - op: starts with
    path: event/NETWORK_ACTIVITY/?/SOURCE/IP_ADDRESS
    value: '10.'
  - op: is
    path: event/NETWORK_ACTIVITY/?/DESTINATION/PORT
    value: 445
```

It matches events where *any* connection has a source IP prefix of `10.` and *any* connection has a destination port of `445`. This is not the intent. The rule must match if a *single* connection has these two characteristics.

Use the `scope` operator. The `path` in the operator becomes the new `event/` root path in all operators under the `rule`. The rule above then becomes

Example:

```yaml
event: NETWORK_CONNECTIONS
op: scope
path: event/NETWORK_ACTIVITY/
rule:
  op: and
  rules:
    - op: starts with
      path: event/SOURCE/IP_ADDRESS
      value: '10.'
    - op: is
      path: event/DESTINATION/PORT
      value: 445
```

### cidr

The `cidr` operator checks if an IP address at the path is in a given
[CIDR network mask](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing).

Example rule:

```yaml
event: NETWORK_CONNECTIONS
op: cidr
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
cidr: 10.16.1.0/24
```

### is private address

The `is private address` operator checks if an IP address at the path is a private/non-routable address. Supports both IPv4 and IPv6.

**IPv4 ranges matched:**

| Range | Description | RFC |
|-------|-------------|-----|
| `10.0.0.0/8` | Private | [RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918) |
| `172.16.0.0/12` | Private | [RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918) |
| `192.168.0.0/16` | Private | [RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918) |
| `100.64.0.0/10` | CGNAT/Shared Address Space | [RFC 6598](https://datatracker.ietf.org/doc/html/rfc6598) |

**IPv6 ranges matched:**

| Range | Description | RFC |
|-------|-------------|-----|
| `fc00::/7` | Unique Local Address (ULA) | [RFC 4193](https://datatracker.ietf.org/doc/html/rfc4193) |

Note: This operator does **not** match loopback (`127.0.0.0/8`, `::1`) or link-local (`169.254.0.0/16`, `fe80::/10`) addresses. To match those addresses, use `cidr`.

Example rule:

```yaml
event: NETWORK_CONNECTIONS
op: is private address
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

### is private ipv4 address

The `is private ipv4 address` operator checks if an IP address at the path is a private IPv4 address. Returns false for IPv6 addresses.

**Ranges matched:**

| Range | Description | RFC |
|-------|-------------|-----|
| `10.0.0.0/8` | Private | [RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918) |
| `172.16.0.0/12` | Private | [RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918) |
| `192.168.0.0/16` | Private | [RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918) |
| `100.64.0.0/10` | CGNAT/Shared Address Space | [RFC 6598](https://datatracker.ietf.org/doc/html/rfc6598) |

Example rule:

```yaml
event: NETWORK_CONNECTIONS
op: is private ipv4 address
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

### is private ipv6 address

The `is private ipv6 address` operator checks if an IP address at the path is a private IPv6 address (ULA). Returns false for IPv4 addresses.

**Ranges matched:**

| Range | Description | RFC |
|-------|-------------|-----|
| `fc00::/7` | Unique Local Address (ULA) | [RFC 4193](https://datatracker.ietf.org/doc/html/rfc4193) |

Example rule:

```yaml
event: NETWORK_CONNECTIONS
op: is private ipv6 address
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

### is public address

The `is public address` operator checks if an IP address at the path is a publicly routable unicast address. Supports both IPv4 and IPv6.

**IPv4 ranges excluded (will NOT match as public):**

| Range | Description | RFC |
|-------|-------------|-----|
| `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | Private | [RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918) |
| `100.64.0.0/10` | CGNAT/Shared Address Space | [RFC 6598](https://datatracker.ietf.org/doc/html/rfc6598) |
| `127.0.0.0/8` | Loopback | [RFC 1122](https://datatracker.ietf.org/doc/html/rfc1122) |
| `169.254.0.0/16` | Link-Local | [RFC 3927](https://datatracker.ietf.org/doc/html/rfc3927) |
| `224.0.0.0/4` | Multicast | [RFC 5771](https://datatracker.ietf.org/doc/html/rfc5771) |
| `0.0.0.0` | Unspecified | [RFC 1122](https://datatracker.ietf.org/doc/html/rfc1122) |

**IPv6 ranges excluded (will NOT match as public):**

| Range | Description | RFC |
|-------|-------------|-----|
| `fc00::/7` | Unique Local Address (ULA) | [RFC 4193](https://datatracker.ietf.org/doc/html/rfc4193) |
| `::1` | Loopback | [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) |
| `fe80::/10` | Link-Local | [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) |
| `ff00::/8` | Multicast | [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) |
| `fec0::/10` | Site-Local (deprecated) | [RFC 3879](https://datatracker.ietf.org/doc/html/rfc3879) |
| `::` | Unspecified | [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) |

Example rule:

```yaml
event: NETWORK_CONNECTIONS
op: is public address
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

### is public ipv4 address

The `is public ipv4 address` operator checks if an IP address at the path is a publicly routable IPv4 address. Returns false for IPv6 addresses.

**Ranges excluded (will NOT match as public):**

| Range | Description | RFC |
|-------|-------------|-----|
| `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` | Private | [RFC 1918](https://datatracker.ietf.org/doc/html/rfc1918) |
| `100.64.0.0/10` | CGNAT/Shared Address Space | [RFC 6598](https://datatracker.ietf.org/doc/html/rfc6598) |
| `127.0.0.0/8` | Loopback | [RFC 1122](https://datatracker.ietf.org/doc/html/rfc1122) |
| `169.254.0.0/16` | Link-Local | [RFC 3927](https://datatracker.ietf.org/doc/html/rfc3927) |
| `224.0.0.0/4` | Multicast | [RFC 5771](https://datatracker.ietf.org/doc/html/rfc5771) |
| `0.0.0.0` | Unspecified | [RFC 1122](https://datatracker.ietf.org/doc/html/rfc1122) |

Example rule:

```yaml
event: NETWORK_CONNECTIONS
op: is public ipv4 address
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

### is public ipv6 address

The `is public ipv6 address` operator checks if an IP address at the path is a publicly routable IPv6 address. Returns false for IPv4 addresses.

**Ranges excluded (will NOT match as public):**

| Range | Description | RFC |
|-------|-------------|-----|
| `fc00::/7` | Unique Local Address (ULA) | [RFC 4193](https://datatracker.ietf.org/doc/html/rfc4193) |
| `::1` | Loopback | [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) |
| `fe80::/10` | Link-Local | [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) |
| `ff00::/8` | Multicast | [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) |
| `fec0::/10` | Site-Local (deprecated) | [RFC 3879](https://datatracker.ietf.org/doc/html/rfc3879) |
| `::` | Unspecified | [RFC 4291](https://datatracker.ietf.org/doc/html/rfc4291) |

Example rule:

```yaml
event: NETWORK_CONNECTIONS
op: is public ipv6 address
path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
```

## Transforms

A transform changes the value in an event before the evaluation of that value.

### file name

Sample: `file name: true`

The `file name` transform replaces a `path` with the file name component of that `path`. A `path` of `c:\windows\system32\wininet.dll` becomes `wininet.dll`.

### sub domain

Sample: `sub domain: "-2:"`

The `sub domain` transform extracts components from a domain name. The value of `sub domain` uses [slice notation](https://stackoverflow.com/questions/509211/understanding-slice-notation). The form is `startIndex:endIndex`. The index is 0-based and shows which parts of the domain to keep.

Some examples:

- `0:2` means the first 2 components of the domain: `aa.bb` for `aa.bb.cc.dd`.
- `-1` means the last component of the domain: `cc` for `aa.bb.cc`.
- `1:` means all components starting at 1: `bb.cc` for `aa.bb.cc`.
- `:` means to test the operator against every component separately.

### is older than

Tests if a value in the event at the `"path": <>` parameter is older than the number of seconds in the `seconds` parameter. The value must be a second-based epoch or a millisecond-based epoch. The comparison is centered in time at "now" during the evaluation.

Example rule:

```yaml
event: login-attempt
op: is older than
path: routing/event_time
seconds: 3600
```

The example above matches a `login-attempt` event that occurred more than 1h ago.

## Times

All operators support an optional parameter named `times`. If you use it, it must contain a list of Time Descriptors that give when the operator is valid. One rule can use different Time Descriptors for each operator.

This example rule matches a Chrome process that starts between 11PM and 5AM, Monday to Friday, Pacific Time:

```yaml
event: NEW_PROCESS
op: ends with
path: event/FILE_PATH
value: chrome.exe
case sensitive: false
times:
  - day_of_week_start: 2     # 1 - 7 (1 = Sunday, 7 = Saturday)
    day_of_week_end: 6       # 1 - 7 (1 = Sunday, 7 = Saturday)
    time_of_day_start: 2200  # 0 - 2359
    time_of_day_end: 2359    # 0 - 2359
    tz: America/Los_Angeles  # time zone
  - day_of_week_start: 2
    day_of_week_end: 6
    time_of_day_start: 0
    time_of_day_end: 500
    tz: America/Los_Angeles
```

### Time Zone

The `tz` should match a TZ database name from the [Time Zones Database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).

## Value Modifiers

Several operators (`is`, `contains`, `starts with`, `ends with`, `is greater than`, `is lower than`) support a special syntax in the `value` parameter. This syntax resolves values at the time of the evaluation.

### Lookbacks

Use `<<path>>` to compare against a value from elsewhere in the same event:

```yaml
op: is
path: event/DESTINATION/IP_ADDRESS
value: <<event/SOURCE/IP_ADDRESS>>
```

### Sensor Variables

Use `[[variable_name]]` to compare against values stored in a [sensor variable](../3-detection-response/sensor-variables.md). You set a variable with the [`add var` response action](response-actions.md#add-var-del-var), and a variable can hold many values. The operator checks if the value at `path` matches **any** value in the variable.

```yaml
op: is
path: event/FILE_PATH
value: '[[known-good-processes]]'
```

If the variable is empty or does not exist, the operator returns `false`. With `not: true`, a rule can match only when a variable is not set. For detailed usage and examples, see [Sensor Variables](../3-detection-response/sensor-variables.md).

---

## See Also

- [D&R Rules Overview](../3-detection-response/index.md)
- [Response Actions](response-actions.md)
- [Sensor Variables](../3-detection-response/sensor-variables.md)
- [Writing Rules](../3-detection-response/tutorials/writing-testing-rules.md)
