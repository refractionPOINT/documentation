# Detection Logic Operators

Operators are used in the Detection part of a Detection & Response rule. Operators may also be accompanied by other available parameters, such as transforms, times, and others, referenced later in this page.

> For more information on how to use operators, read [Detection & Response Rules](../writing-and-testing-rules.md).

## Operators

### and, or

The standard logical boolean operations to combine other logical operations. Takes a single `rules:` parameter that contains a list of other operators to "AND" or "OR" together.

Example:
    
    
    op: or
    rules:
      - ...rule1...
      - ...rule2...
      - ...
    

### is

Tests for equality between the value of the `"value": <>` parameter and the value found in the event at the `"path": <>` parameter.

Supports the file name and sub domain transforms.

Example rule:
    
    
    event: NEW_PROCESS
    op: is
    path: event/PARENT/PROCESS_ID
    value: 9999
    

### exists

Tests if any elements exist at the given path (regardless of its value).

Example rule:
    
    
    event: NEW_PROCESS
    op: exists
    path: event/PARENT
    

The `exists` operator also supports an optional `truthy` parameter. When `true`, this parameter indicates the `exists` should treat `null` and `""` (empty string) values as if they were non-existent like:

The rule:
    
    
    op: exists
    path: some/path
    truthy: true
    

applied to:
    
    
    {
      "some": {
        "path": ""
      }
    }
    

would NOT match.

### contains

The `contains` checks if a substring can be found in the value at the path.

An optional parameter `count: 3` can be specified to only match if the given  
substring is found _at least_ 3 times in path.

Supports the file name and sub domain transforms.

Example rule:
    
    
    event: NEW_PROCESS
    op: contains
    path: event/COMMAND_LINE
    value: reg
    count: 2
    

### ends with, starts with

The `starts with` checks for a prefix match and `ends with` checks for a suffix match.

They both check if the value found at `path` matches the given `value`, based on the operator.

Supports the file name and sub domain transforms.

### is greater than, is lower than

Check to see if a value is greater or lower (numerically) than a value in the event.

They both use the `path` and `value` parameters. They also both support the `length of` parameter as a boolean (true or false). If set to true, instead of comparing  
the value at the specified path, it compares the length of the value at that path.

### matches

The `matches` op compares the value at `path` with a regular expression supplied in the `re` parameter. Under the hood, this uses the Golang's `regexp` [package](https://golang.org/pkg/regexp/), which also enables you to apply the regexp to log files.

Supports the file name and sub domain transforms.

Example:
    
    
    event: FILE_TYPE_ACCESSED
    op: matches
    path: event/FILE_PATH
    re: .*\\system32\\.*\.scr
    case sensitive: false
    

### not

The `not` operator inverts the result of its rule. For example, when applied to an `is` operator, it changes the logic from "equals" to "does not equal". When applied to an or operator, it changes the logic from "any of these conditions are true" to "none of these conditions are true"

Example:
    
    
    event: NEW_PROCESS
    op: is
    not: true
    path: event/PARENT/PROCESS_ID
    value: 9999

### string distance

The `string distance` op looks up the [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance) between two strings. In other words it generates the minimum number of character changes required for one string to become equal to another.

For example, the Levenshtein Distance between `google.com` and `googlr.com` (`r` instead of `e`) is 1.

This can be used to find variations of file names or domain names that could be used for phishing, for example.

Suppose your company is `onephoton.com`. Looking for the Levenshtein Distance between all `DOMAIN_NAME` in `DNS_REQUEST` events, compared to `onephoton.com` it could detect an attacker using `onephot0n.com` in a phishing email domain.

The operator takes a `path` parameter indicating which field to compare, a `max` parameter indicating the maximum Levenshtein Distance to match and a `value` parameter that is either a string or a list of strings that represent the value(s) to compare to. Note that although `string distance` supports the `value` to be a list, most other operators do not.

Supports the file name and sub domain transforms.

Example:
    
    
    event: DNS_REQUEST
    op: string distance
    path: event/DOMAIN_NAME
    value:
      - onephoton.com
      - www.onephoton.com
    max: 2
    

This would match `onephotom.com` and `0nephotom.com` but NOT `0neph0tom.com`.

Using the file name transform to apply to a file name in a path:
    
    
    event: NEW_PROCESS
    op: string distance
    path: event/FILE_PATH
    file name: true
    value:
      - svchost.exe
      - csrss.exe
    max: 2
    

This would match `svhost.exe` and `csrss32.exe` but NOT `csrsswin32.exe`.

### is 32 bit, is 64 bit, is arm

All of these operators take no additional arguments, they simply match if the relevant Sensor characteristic is correct.

Example:
    
    
    op: is 64 bit
    

### is platform

Checks if the event under evaluation is from a sensor of the given platform.

Takes a `name` parameter for the platform name. The current platforms are:

  * `windows`

  * `linux`

  * `macos`

  * `ios`

  * `android`

  * `chrome`

  * `vpn`

  * `text`

  * `json`

  * GCP

  * AWS

  * `carbon_black`

  * `crowdstrike`

  * `1password`

  * `office365`

  * `msdefender`




Example:
    
    
    op: is platform
    name: 1password
    

### is tagged

Determines if the Tag supplied in the `tag` parameter is already associated with the sensor that the event under evaluation is from.

### lookup

Looks up a value against a [lookup add-on](https://app.limacharlie.io/add-ons/category/lookup) (a.k.a. resource) such as a threat feed.
    
    
    event: DNS_REQUEST
    op: lookup
    path: event/DOMAIN_NAME
    resource: hive://lookups/malwaredomains
    case sensitive: false
    

This rule will get the `event/DOMAIN_NAME` of a `DNS_REQUEST` event and check if it's a member of the `lookup` named `malwaredomains`. If it is, then the rule is a match.

The value is supplied via the `path` parameter and the lookup is defined in the `resource` parameter. Resources are of the form `hive://lookups/RESOURCE_NAME`. In order to access a lookup, your Organization must be subscribed to it.

Supports the file name and sub domain transforms.

> API-based lookups, like VirusTotal and IP Geolocation, work a little bit differently. For more information, see the API Integrations documentation in Add-Ons.

> You can create your own lookups and optionally publish them in the add-on marketplace. To learn more, see [Lookups](../../Platform Management/Config Hive/config-hive-lookups.md) and [Lookup Manager](../../Add-Ons/Extensions/LimaCharlie Extensions/ext-lookup-manager.md).

### scope

In some cases, you may want to limit the scope of the matching and the `path` you use to be within a specific part of the event. The `scope` operator allows you to do just that, reset the root of the `event/` in paths to be a sub-path of the event.

This comes in as very useful for example when you want to test multiple values of a connection in a `NETWORK_CONNECTIONS` event but always on a per-connection. If you were to do a rule like:
    
    
    event: NETWORK_CONNECTIONS
    op: and
    rules:
      - op: starts with
        path: event/NETWORK_ACTIVITY/?/SOURCE/IP_ADDRESS
        value: '10.'
      - op: is
        path: event/NETWORK_ACTIVITY/?/DESTINATION/PORT
        value: 445
    

you would hit on events where _any_ connection has a source IP prefix of `10.` and _any_ connection has a destination port of `445`. Obviously this is not what we had in mind, we wanted to know if a _single_ connection has those two characteristics.

The solution is to use the `scope` operator. The `path` in the operator will become the new `event/` root path in all operators found under the `rule`. So the above would become

Example:
    
    
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
    

### cidr

The `cidr` checks if an IP address at the path is contained within a given  
[CIDR network mask](https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing).

Example rule:
    
    
    event: NETWORK_CONNECTIONS
    op: cidr
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
    cidr: 10.16.1.0/24
    

### is private address

The `is private address` checks if an IP address at the path is a private address  
as defined by [RFC 1918](https://en.wikipedia.org/wiki/Private_network).

Example rule:
    
    
    event: NETWORK_CONNECTIONS
    op: is private address
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
    

### is public address

The `is public address` checks if an IP address at the path is a public address  
as defined by [RFC 1918](https://en.wikipedia.org/wiki/Private_network).

Example rule:
    
    
    event: NETWORK_CONNECTIONS
    op: is public address
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
    

## Transforms

Transforms are transformations applied to the value being evaluated in an event, prior to the evaluation.

### file name

Sample: `file name: true`

The `file name` transform takes a `path` and replaces it with the file name component of the `path`. This means that a `path` of `c:\windows\system32\wininet.dll` will become `wininet.dll`.

### sub domain

Sample: `sub domain: "-2:"`

The `sub domain` extracts specific components from a domain name. The value of `sub domain` is in [slice notation](https://stackoverflow.com/questions/509211/understanding-slice-notation). It looks like `startIndex:endIndex`, where the index is 0-based and indicates which parts of the domain to keep.

Some examples:

  * `0:2` means the first 2 components of the domain: `aa.bb` for `aa.bb.cc.dd`.

  * `-1` means the last component of the domain: `cc` for `aa.bb.cc`.

  * `1:` means all components starting at 1: `bb.cc` for `aa.bb.cc`.

  * `:` means to test the operator to every component individually.




### is older than

Test if a value in event at the `"path": <>` parameter, assumed to be either a second-based epoch or a millisecond-based epoch is older than a number of seconds as specified by the `seconds` parameter, centered in time at "now" during evaluation.

Example rule:
    
    
    event: login-attempt
    op: is older than
    path: routing/event_time
    seconds: 3600
    

where the example above would match on a `login-attempt` event that occurred more than 1h ago.

## Times

All operators support an optional parameter named `times`. When specified, it must contain a list of Time Descriptors when the accompanying operator is valid. Your rule can mix-and-match multiple Time Descriptors as part of a single rule on per-operator basis.

Here's an example rule that matches a Chrome process starting between 11PM and 5AM, Monday through Friday, Pacific Time:
    
    
    event: NEW_PROCESS
    op: ends with
    path: event/FILE_PATH
    value: chrome.exe
    case sensitive: false
    times:
      - day_of_week_start: 2     # 1 - 7
        day_of_week_end: 6       # 1 - 7
        time_of_day_start: 2200  # 0 - 2359
        time_of_day_end: 2359    # 0 - 2359
        tz: America/Los_Angeles  # time zone
      - day_of_week_start: 2
        day_of_week_end: 6
        time_of_day_start: 0
        time_of_day_end: 500
        tz: America/Los_Angeles
    

#### Time Zone

The `tz` should match a TZ database name from the [Time Zones Database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).