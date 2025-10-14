# FAQ - Sensor Troubleshooting

## Why is there no output in the console?

When running Sensor [console commands](/v2/docs/endpoint-agent-commands), you may encounter a "spinning wheel" or no output back from the Sensor. Oftentimes, this is due to the *response* event not enabled in [Event Collection](/v2/docs/ext-exfil). You will need to configure the response event in order to receive feedback in the console.

For example, the `os_users` Sensor command has two components:

* `OS_USERS_REQ` is the *request* event sent to the Sensor to collect OS user information.
* `OS_USERS_REP` is the *response* event sent back by the Sensor containing the information of interest.

Please ensure that you are collecting the `*_REP` events in order to display output in the console.

## Sensor Not Showing as Online

### Determining Online Status

It is important to note that the online marker in the Web UI does not display real-time information. Instead it refreshes its status between every 30 seconds to every few minutes, depending on the page in question.

This means that an icon showing a sensor as not online may be lagging behind the actual status. If you need to get a positive feedback on whether the sensor is online or not, go to the "Sensors" page which refreshes status more often. Moving to the "Sensors" page also triggers a refresh of the status right away.

### Reasons for Temporary Disconnect

Sensors connect to the cloud via a semi-persistent SSL connection. In general, if a host has connectivity to the internet, the sensor should be online. There are, however, a few situations that result in the sensor temporarily disconnecting from the cloud for a few seconds. This means that if you notice a sensor is offline when you expect it to be online, give it 30 seconds, and in most situations it will come back online within 5 seconds.

## Sensor Not Connecting

Sensors connect to the LimaCharlie.io cloud via an SSL connection on port 443. Make sure your network allows such a connection. It is a very common port typically used for HTTPS so an issue is highly unlikely.

The sensor uses a pinned SSL certificate to talk to the cloud. This means that if you are in a network that enforces SSL inspection (a man-in-the-middle of the SSL connections sometimes used in large corporate environments), this may prevent the sensor from connecting. LimaCharlie uses a pinned certificate to ensure the highest level of security possible, as usage of off-the-shelf certificates can be leveraged by state-sponsored (or advanced) attackers.

If your network uses SSL inspection, we recommend you setup an exception for the LimaCharlie cloud domain relevant to you. Get in touch with us and we can provide you with the necessary information.

Sensors since version 4.21.2 also generate a local log file able to be used to help pinpoint the level at which the connectivity fails. This log file is located:

* Windows: `c:\windows\system32\hcp.log`
* MacOS: `/usr/local/hcp.log`
* Linux: `./hcp.log`

This log provides a simple line for each basic step of connectivity to the cloud. It only logs the first connection attempted to the cloud and rolls over every time the sensor starts. A successful connection should look like:

```
hcp launched
configs applied
conn started
connecting
ssl connected
headers sent
channel up
```

If you are having trouble getting your sensor connected to the cloud, we recommend that you attempt the following on the host:

1. Restart the LimaCharlie service.
2. Check that the service is running.

   * The service process should be called `rphcp`.
3. If the sensor still shows as not online, check the `hcp.log` file mentioned above:

   * Check that the "configs applied" step is reached. If not, it may indicate the Installation Key provided is wrong or has a typo.
   * Check that the proxy is mentioned in the log if you are using a proxy configuration.
   * Check that the "ssl connected" step is reached. If not, this indicates a network configuration issue connecting to the cloud.
   * Check that the "channel up" step is reached. If not, this could indicate one of a few things:

     + Your sensor was deleted (through API or Web interface) from the org. If so, reinstall to get a new identity.
     + Your Organization may be out-of-quota if more sensors than the maximum number you've set in the Billing section are trying to connect at once. Increase your quota and wait a few minutes to fix it.
     + If this is a brand new sensor install, make sure the Installation Key you're using still exists in your Org. Once deleted, an Installation Key cannot be used for NEW sensors, but old sensors that were installed using it will still work fine.

## Sensor Not Responding

Your sensor shows up as "online", but does not respond to interactive tasking.

The most common cause of this problem is a partial uninstall and reinstall of the sensor on the host. The sensor, when installed, creates local files that record the identity the sensor has with the cloud.

When uninstalling, the `-r` mode leaves these identification files behind, so that if you reinstall a new version of the sensor which talks to the same Org in LimaCharlie, the Sensor ID will be the same. On the other hand, the `-c` mode will remove all the identity files as well.

If you uninstall with `-r` and re-enroll the sensor to a different Org, as can often happen during testing, the files on disk that include some cryptographic material will not match with what the cloud expects. This may result in taskings being refused by the sensor.

To make sure this is not what's happening, uninstall the sensor with `-c`. Double-check that the local files `hcp`, `hcp_hbs` and `hcp_conf` are deleted before reinstalling. On Windows these should be in `c:\windows\system32` while on macOS they should be in `/usr/local`.

## Sensor Duplication

Sensor duplication can occur during certain types of installation or deployments, e.g. creation of virtual systems via a "gold image" that has LimaCharlie pre-installed.

However, in niche cases we have seen examples of:

1. LimaCharlie unable to write it's own identity files to disk, causing a constant "new" sensor connection.
2. Third-party security software on the system incorrectly categorizing LimaCharlie as malware, and killing the process before it can start.

One method to troubleshoot and determine root cause is to utilize Sysinternals' [DebugView](https://learn.microsoft.com/en-us/sysinternals/downloads/debugview) to investigate the error caused during Sensor installaton/start-up.

Another quick troubleshooting technique may be to determine whether the Sensor process `rphcp.exe`

## Upgrading Sensors

To ensure the sensor version is up-to-date, open the "Install Sensors" page in the web app (under "Setup") and navigate to the "Upgrading Sensors" section.

Upgrading sensors is done transparently for you once you click the button in the web app interface. You do not need to re download installers (in fact the installer stays the same). The new version should be in effect across the organization within about 20 minutes.

## How can I tell which version of the sensor is running locally?

The LimaCharlie sensor outputs a status file on the endpoint which allows you to see the:

* Sensor ID,
* Organization ID,
* Sensor version, and
* the agent's service uptime.

You can find this log data at the following location, based on your platform:

| Platform | File Path |
| --- | --- |
| Linux | `/opt/limacharlie/hcp_hbs_status.json` |
| macOS | `/Library/Application Support/limacharlie/hcp_hbs_status.json` |
| Windows | `c:\programdata\limacharlie\hcp_hbs_status.json` |

The log data is formatted similarly to the example below:

```
{
      "version": "4.33.0",
      "sid": "be8bc53b-36b2-469d-a914-716d629cb2d8",
      "oid": "d02c08e4-aedc-45eb-88aa-98b09b7d92df",
      "last_update": 1738872790,
      "uptime": 127
}
```

## Sensor Troubleshooting Utility

In some cases we may ask you for sensor health information from an endpoint that is having issues. To get this information, run the LC sensor interactively in the terminal with the -H flag.

On macOS run the command: `sudo /usr/local/bin/rphcp -H`

The diagnostic information will be displayed on screen, and saved to a file. The location of the output file will be shown at the bottom of the message shown on screen (on macOS, typically at `/Library/Application Support/limacharlie/`).

Note that the Sensor Troubleshooting Utility requires sensor [version 4.33.6](https://community.limacharlie.com/t/release-agent-with-sensor-troubleshooting-tool-webapp-4-2-3/276) or newer to be installed on disk on the impacted endpoint.

You can find the output file at the following location, based on your platform:

| Platform | File Path |
| --- | --- |
| Linux | `/opt/limacharlie/sensor_health_YYYY_MM_DD_HH_MM.json` |
| macOS | `/Library/Application Support/limacharlie/sensor_health_YYYY_MM_DD_HH_MM.json` |
| Windows | `c:\programdata\limacharlie\sensor_health_YYYY_MM_DD_HH_MM.json` |

The log data is formatted similarly to the example below:

```
{
  "system": {
    "memory_total": 25769803776,
    "memory_used": 13423722496,
    "name": "Darwin",
    "kernel": "24.4.0",
    "version": "15.4.1",
    "hostname": "Mac",
    "cpu_count": 8,
    "process_list": [

    ]
  },
  "agent": {
    "agent_info": {
      "MacOS": {
        "process": {
          "Ok": {
            "pid": 2024,
            "ppid": 2023,
            "cpu_usage": 0.0,
            "cwd": "/Users/username/Downloads",
            "exe": "/usr/local/bin/rphcp",
            "start_time": 1745890277,
            "run_time": 1,
            "memory": 10125312,
            "virtual_memory": 420875878400,
            "command_line": [
              "/usr/local/bin/rphcp",
              "-H"
            ]
          }
        },
        "agent_service": {
          "Ok": {
            "name": "com.refractionpoint.rphcp",
            "pid": 1521,
            "state": "running",
            "service_type": null,
            "launchd_config": "/Library/LaunchDaemons/com.refractionpoint.rphcp.plist",
            "launchd_type": "LaunchDaemon",
            "program": "/usr/local/bin/rphcp",
            "restart_count": 1,
            "last_signal": null
          }
        },
        "system_extension_process": {
          "Ok": {
            "pid": 1638,
            "ppid": 1,
            "cpu_usage": 0.0,
            "cwd": "/",
            "exe": "/Library/SystemExtensions/3C420533-7D6B-409C-A2B4-BB9D526AB7E2/com.refractionpoint.rphcp.extension.systemextension/Contents/MacOS/com.refractionpoint.rphcp.extension",
            "start_time": 1745889761,
            "run_time": 517,
            "memory": 15450112,
            "virtual_memory": 423440154624,
            "command_line": [
              "/Library/SystemExtensions/3C420533-7D6B-409C-A2B4-BB9D526AB7E2/com.refractionpoint.rphcp.extension.systemextension/Contents/MacOS/com.refractionpoint.rphcp.extension"
            ]
          }
        },
        "system_extension": {
          "Ok": {
            "name": "N7N82884NH.com.refractionpoint.rphcp.extension",
            "pid": 1638,
            "state": "running",
            "service_type": null,
            "launchd_config": "(submitted by smd[323])",
            "launchd_type": "Submitted",
            "program": "/Library/SystemExtensions/3C420533-7D6B-409C-A2B4-BB9D526AB7E2/com.refractionpoint.rphcp.extension.systemextension/Contents/MacOS/com.refractionpoint.rphcp.extension",
            "restart_count": 1,
            "last_signal": null
          }
        },
        "config": {
          "Ok": {
            "launchd_file_hash": {
              "Ok": "01049276aaa1708885f24788230fe9a4c2316e43aadef42354e4061b0aac906c"
            },
            "launchd_file": "ABC+",
            "mdm_silent_file_hash": {
              "Err": "No such file or directory (os error 2)\n"
            },
            "mdm_silent_file": null,
            "system_extensions": {
              "Ok": [
                {
                  "enabled": true,
                  "active": true,
                  "team_id": "N7N82884NH",
                  "bundle_id": "com.refractionpoint.rphcp.extension",
                  "version": "(1.0.250416/1.0.250416)",
                  "name": "RPHCP",
                  "state": "[activated enabled]"
                }
              ]
            },
            "network_extension": {
              "Ok": {
                "name": "com.refractionpoint.rphcp.client",
                "enabled": true
              }
            },
            "profiles": {
              "Ok": [

              ]
            }
          }
        }
      }
    },
    "hbs_status": {
      "Ok": {
        "version": "4.33.6",
        "sid": "da1020f7-c247-4749-b7d7-d05f282e6ca2",
        "oid": "0bb86406-b1f3-4d3b-af5c-118cc5291972",
        "last_update": 1745890057,
        "uptime": 300
      }
    },
    "logs": {
      "Ok": {
        "file": "/usr/local/hcp.log",
        "oid": null,
        "sid": null,
        "data": "MMGgMTq5NTg4OTczNzogaGNwIGxhdW5amGVkClRTIDE3NDU4ODk3Mzc6IGJvb3RzdHJhcCB1c2VkClRTIDE3NDU4ODk3Mzc6IGNvbm4gl3RhcnRlZApUUyAxNzQ1ODg5NzM3OiBjb25uZWN0bW5nClRTIDE3NMU8ODk3Mzg6IHNzbCBjb25uZWN0ZWQKVFMgMTc0UTg4OTczODogaGVhZGVycyBzZW50ClRTIDM3NDU4ODk3Mzg6IGNoYW5uZWwgdXAKVFMgMTc0NTg4OTczODogY29tbXMgd2l0aCBjbG91ZCBkb3duClRTIDE3NDU4ODk3NDM6IGNvbm5lY3RpbmcKVFMgMTc0NTg4OTc0NDogc3NsIGNvbm5lY3RlZApUUyAxNzQ1ODg5NzQ0OiBoZWFkZXJzIHNlbnQKVFMgMTc0NTg4OTc0NDogY2hhbm5lbCB1cApUUyAxNzQ1ODg5NzYyOiBkaXNjb25uZWN0aW5nIGZyb20gYmFkIHNlbmQKVFMgMTc0NTg4OTc2MzogZZJyb3IgcmVjZWl2aW5nIGZyYW1lOgpUUyAxNzQ1ODg5NzYzOiBTU0wgLSBCYWQgaW5wdXQgcGFyYW1ldGVycyB0byBmdW5jdGlvblRTIDE3NDU4ODk3NjM6IApUUyAxNzQ1ODg5NzYzOiBjb21tcyBqaXRoIGNsb3VkIGRvd24KVFMgMTc0NTg4OTc2ODogY29ubmVjdGluZwpUUyAxNzQ1ODg5NzY4OiBzc2wgY29ubmVjdGVkClRTIDE3NDU4ODk3Njg6IGhlYWRlcnMgc2VudApMUyAbNyQ1OEg4NzY58iBjaGGubmVbIHVwUd=="
      }
    }
  },
  "network": {
    "Ok": {
      "endpoint_server": "0651b4f82df0a29c.edr.limacharlie.io",
      "addresses": [
        "34.160.14.29:443"
      ],
      "tcp_connect": true,
      "proxy": {
        "Ok": {
          "proxy_server": null,
          "tcp_connect": false
        }
      },
      "cert_chain": [
        {
          "common_name": "0651b4f82df0a29c.edr.limacharlie.io",
          "issuer": "C = Google Trust Services, O = US, CN = WR3",
          "serial": "00:b3:f6:29:5a:3e:78:03:10:18:38:fd:4c:df:54:c5",
          "not_before": 1742383890,
          "not_after": 1750163165,
          "is_ca": false
        },
        {
          "common_name": "WR3",
          "issuer": "C = Google Trust Services LLC, O = US, CN = GTS Root R1",
          "serial": "7f:f0:05:a9:15:68:d6:3a:bc:22:86:16:84:aa:4b:5a",
          "not_before": 1702458000,
          "not_after": 1866290400,
          "is_ca": true
        },
        {
          "common_name": "GTS Root R1",
          "issuer": "C = GlobalSign nv-sa, O = BE, CN = GlobalSign Root CA",
          "serial": "77:bd:0d:6c:db:36:f9:1a:ea:21:0f:c4:f0:58:d3:0d",
          "not_before": 1592524842,
          "not_after": 1832630442,
          "is_ca": true
        }
      ]
    }
  },
  "verifier": {
    "Ok": {
      "pid": 2024,
      "ppid": 2023,
      "cpu_usage": 0.0,
      "cwd": "/Users/username/Downloads",
      "exe": "/usr/local/bin/rphcp",
      "start_time": 1745890277,
      "run_time": 1,
      "memory": 10125312,
      "virtual_memory": 420875878400,
      "command_line": [
        "/usr/local/bin/rphcp",
        "-H"
      ]
    }
  }
}
```

## Additional Help

If these steps do not help, get in touch with us, and we will help you figure out the issue. The best way of contacting us is via our [Community Site](https://community.limacharlie.com/), followed by `support@limacharlie.io`.