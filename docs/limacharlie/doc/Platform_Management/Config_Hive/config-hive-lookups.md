# Config Hive: Lookups

## Format

Lookups are dictionaries/maps/key-value-pairs where the key is a string. The lookup can then be queried by various parts of LimaCharlie (like rules). The value component of a lookup must be a dictionary and represents metadata associated with the given key, which will be returned to the rule using the lookup.

Lookup data can be ingested by specifying one of the following root keys indicating the format of the lookupd data:

* `lookup_data`: represented direct as parsed JSON.
* `newline_content`: a string where each key is separated by a newline, LimaCharlie will assume the metadata is empty.
* `yaml_content`: a string in YAML format that contains a dictionary with the string keys and dictionary metadata like the `lookup_data`.

## Permissions

* `lookup.get`
* `lookup.set`
* `lookup.del`
* `lookup.get.mtd`
* `lookup.set.mtd`

## Usage

### Infrastructure as Code

```
hives:
    lookup:                             # Example lookup in the lookup hive
        example-lookup:
            data:
                lookup_data:
                    8.8.8.8: {}
                    8.8.4.4: {}
                    1.1.1.1: {}
                optimized_lookup_data:
                    _LC_INDICATORS: null
                    _LC_METADATA: null
            usr_mtd:
                enabled: true
                expiry: 0
                tags:
                    - example-lookup
                comment: ""
    extension_config:                   # Example lookup manager extension config
        ext-lookup-manager:
            data:
                lookup_manager_rules:
                    - arl: ""
                      format: json
                      name: tor
                      predefined: '[https,storage.googleapis.com/lc-lookups-bucket/tor-ips.json]'
                      tags:
                        - tor
                    - arl: ""
                      format: json
                      name: talos
                      predefined: '[https,storage.googleapis.com/lc-lookups-bucket/talos-ip-blacklist.json]'
                      tags:
                        - talos
            usr_mtd:
                enabled: true
                expiry: 0
                tags: []
                comment: ""
```

### Manually in the GUI

Lookups can be added in the web interface by navigating to Automation --> Lookups. Name your lookup, choose the format, and copy paste the contents of your lookup in the `JSON data` field.

LimaCharlie also provides several publicly available lookups for use in your Organization. More information and the contents of these can be found on [GitHub](https://github.com/refractionpoint/lc-public-lookups). The contents of these lookups can be used here as well.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/lookups.png)

### Automatically via the Lookup Manager

If your lookups change frequently and you wish to keep them up to date, LimaCharlie offers the lookup manager extension as a mechanism to automatically update your lookups every 24 hours. Documentation on the lookup manager can be found [here](../../Add-Ons/Extensions/LimaCharlie_Extensions/ext-lookup-manager.md).

## Example Lookup

```
{
  "lookup_data": {
    "c:\\windows\\system32\\ping.exe": {
      "mtd1": "known_bin",
      "mtd2": 4
    },
    "c:\\windows\\system32\\sysmon.exe": {
      "mtd1": "good_val",
      "mtd2": 10
    }
  }
}
```

or

```
{
  "newline_content": "lvalue1\nlvalue2\nlvalue3"
}
```
