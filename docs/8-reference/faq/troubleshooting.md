# FAQ - Sensor Troubleshooting

## Why is there no output in the console?

When you run Sensor [console commands](../endpoint-commands.md), you can see a "spinning wheel" or no output from the Sensor. Usually, the *response* event is not enabled in [Event Collection](../../5-integrations/extensions/limacharlie/exfil.md). Configure the response event to get feedback in the console.

For example, the `os_users` Sensor command has two components:

- `OS_USERS_REQ` is the *request* event sent to the Sensor to collect OS user information.
- `OS_USERS_REP` is the *response* event sent back by the Sensor containing the information of interest.

Collect the `*_REP` events to show output in the console.

## Sensor Not Showing as Online

### Determining Online Status

The online marker in the Web UI does not show real-time information. It refreshes the status every 30 seconds to every few minutes, and the interval depends on the page.

An icon that shows a sensor as not online can be behind the actual status. For an accurate status, go to the "Sensors" page, which refreshes the status more often. The "Sensors" page also refreshes the status immediately when you open it.

### Reasons for Temporary Disconnect

Sensors connect to the cloud with a semi-persistent SSL connection. If a host has a connection to the internet, the sensor is usually online. But some conditions disconnect the sensor from the cloud for a few seconds. If a sensor is offline when you expect it to be online, wait 30 seconds. In most conditions, the sensor comes back online in 5 seconds.

## Sensor Not Connecting

Sensors connect to the LimaCharlie.io cloud with an SSL connection on port 443. Make sure that your network allows this connection. Port 443 is a common port for HTTPS, so a problem is unlikely.

The sensor uses a pinned SSL certificate to communicate with the cloud. Some networks enforce SSL inspection, which is a man-in-the-middle of the SSL connections. Large corporate environments sometimes use SSL inspection, and it can stop the sensor from connecting. LimaCharlie uses a pinned certificate for the highest possible level of security, because state-sponsored or advanced attackers can use off-the-shelf certificates.

If your network uses SSL inspection, add an exception for your LimaCharlie cloud domain. Contact LimaCharlie for the necessary information.

Sensors from version 4.21.2 also write a local log file. This log file helps you find the level at which the connection fails. The log file is at:

- Windows: `c:\windows\system32\hcp.log`
- MacOS: `/usr/local/hcp.log`
- Linux: `./hcp.log`

The log has one line for each basic step of the connection to the cloud. It logs only the first connection attempt to the cloud, and it rolls over each time the sensor starts. A successful connection looks like this:

```text
hcp launched
configs applied
conn started
connecting
ssl connected
headers sent
channel up
```

If the sensor does not connect to the cloud, do these steps on the host:

1. Restart the LimaCharlie service.
2. Check that the service runs.

    - The name of the service process is `rphcp`.
3. If the sensor still shows as not online, examine the `hcp.log` file above:

    - Check that the log reaches the "configs applied" step. If it does not, the Installation Key is wrong or has a typo.
    - Check that the log shows the proxy, if you use a proxy configuration.
    - Check that the log reaches the "ssl connected" step. If it does not, there is a network configuration problem in the connection to the cloud.
    - Check that the log reaches the "channel up" step. If it does not, one of these causes is possible:

        - Your sensor was deleted from the org, through the API or the Web interface. Install the sensor again to get a new identity.
        - Your Organization is out of quota. This occurs if more sensors try to connect at the same time than the maximum number in the Billing section. Increase your quota and wait a few minutes.
        - For a new sensor install, make sure that the Installation Key still exists in your Org. After you delete an Installation Key, you cannot use it for NEW sensors, but the old sensors that used it continue to work.

## Sensor Not Responding

The sensor shows as "online", but does not respond to interactive tasking.

The most common cause of this problem is a partial uninstall and reinstall of the sensor on the host. At installation, the sensor creates local files that record the identity of the sensor with the cloud.

At uninstallation, the `-r` mode keeps these identification files. If you then install a new version of the sensor that communicates with the same Org in LimaCharlie, the Sensor ID stays the same. The `-c` mode removes all the identity files also.

If you uninstall with `-r` and enroll the sensor again to a different Org, the files on disk contain cryptographic material that does not match the material that the cloud expects. This occurs frequently during tests. The sensor can then refuse taskings.

To remove this cause, uninstall the sensor with `-c`. Check that the local files `hcp`, `hcp_hbs` and `hcp_conf` are deleted before you install again. On Windows, these files are in `c:\windows\system32`. On macOS, they are in `/usr/local`.

## Sensor Duplication

Sensor duplication can occur with some types of installation or deployment. For example, it occurs when you create virtual systems from a "gold image" that has LimaCharlie pre-installed.

In rare cases, these causes also occur:

1. LimaCharlie cannot write its own identity files to disk. This causes a constant "new" sensor connection.
2. Third-party security software on the system categorizes LimaCharlie as malware incorrectly, and stops the process before it starts.

To find the root cause, use the Sysinternals [DebugView](https://learn.microsoft.com/en-us/sysinternals/downloads/debugview) tool. It shows the error during the installation or the start-up of the Sensor.

Another troubleshooting method is to find whether the Sensor process `rphcp.exe`

## Upgrading Sensors

To make sure that the sensor version is current, open the "Install Sensors" page in the web app, under "Setup". Then go to the "Upgrading Sensors" section.

The upgrade of the sensors starts when you click the button in the web app. You do not need to download the installers again, because the installer stays the same. The new version is in effect across the organization in about 20 minutes.

## How can I tell which version of the sensor is running locally?

The LimaCharlie sensor writes a status file on the endpoint. The file shows the:

- Sensor ID,
- Organization ID,
- Sensor version, and
- the agent's service uptime.

The log data is at this location for each platform:

| Platform | File Path |
| --- | --- |
| Linux | `/opt/limacharlie/hcp_hbs_status.json` |
| macOS | `/Library/Application Support/limacharlie/hcp_hbs_status.json` |
| Windows | `c:\programdata\limacharlie\hcp_hbs_status.json` |

The log data has a format like this example:

```json
{
      "version": "4.33.0",
      "sid": "be8bc53b-36b2-469d-a914-716d629cb2d8",
      "oid": "d02c08e4-aedc-45eb-88aa-98b09b7d92df",
      "last_update": 1738872790,
      "uptime": 127
}
```

## Sensor Troubleshooting Utility

LimaCharlie can ask you for sensor health information from an endpoint that has problems. To get this information, run the LC sensor interactively in the terminal with the -H flag.

On macOS, run the command: `sudo /usr/local/bin/rphcp -H`

The sensor shows the diagnostic information on screen and saves it to a file. The location of the output file is at the bottom of the message on screen (on macOS, usually at `/Library/Application Support/limacharlie/``).

The Sensor Troubleshooting Utility needs sensor [version 4.33.6](https://community.limacharlie.com/t/release-agent-with-sensor-troubleshooting-tool-webapp-4-2-3/276) or newer on disk on the impacted endpoint.

The output file is at this location for each platform:

| Platform | File Path |
| --- | --- |
| Linux | `/opt/limacharlie/sensor_health_YYYY_MM_DD_HH_MM.json` |
| macOS | `/Library/Application Support/limacharlie/sensor_health_YYYY_MM_DD_HH_MM.json` |
| Windows | `c:\programdata\limacharlie\sensor_health_YYYY_MM_DD_HH_MM.json` |

The log data has a format like this example:

```json
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
        "data": "MMGgMTq5NTg4OTczNzogaGNwIGxhdW5amGVkClRTIDE3NDU4ODk3Mzc6IGJvb3RzdHJhcCB1c2VkClRTIDE3NDU4ODk3Mzc6IGNvbm4gl3RhcnRlZApUUyAxNzQ1ODg5NzM3OiBjb25uZWN0bW5nClRTIDE3NMU4ODk3Mzg6IHNzbCBjb25uZWN0ZWQKVFMgMTc0UTg4OTczODogaGVhZGVycyBzZW50ClRTIDM3NDU4ODk3Mzg6IGNoYW5uZWwgdXAKVFMgMTc0NTg4OTczODogY29tbXMgd2l0aCBjbG91ZCBkb3duClRTIDE3NDU4ODk3NDM6IGNvbm5lY3RpbmcKVFMgMTc0NTg4OTc0NDogc3NsIGNvbm5lY3RlZApUUyAxNzQ1ODg5NzQ0OiBoZWFkZXJzIHNlbnQKVFMgMTc0NTg4OTc0NDogY2hhbm5lbCB1cApUUyAxNzQ1ODg5NzYyOiBkaXNjb25uZWN0aW5nIGZyb20gYmFkIHNlbmQKVFMgMTc0NTg4OTc2MzogZZJyb3IgcmVjZWl2aW5nIGZyYW1lOgpUUyAxNzQ1ODg5NzYzOiBTU0wgLSBCYWQgaW5wdXQgcGFyYW1ldGVycyB0byBmdW5jdGlvblRTIDE3NDU4ODk3NjM6IApUUyAxNzQ1ODg5NzYzOiBjb21tcyBqaXRoIGNsb3VkIGRvd24KVFMgMTc0NTg4OTc2ODogY29ubmVjdGluZwpUUyAxNzQ1ODg5NzY4OiBzc2wgY29ubmVjdGVkClRTIDE3NDU4ODk3Njg6IGhlYWRlcnMgc2VudApMUyAbNyQ1OEg4NzY58iBjaGGubmVbIHVwUd=="
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

## Enabling Verbose and File Logging

By default, a released sensor logs almost nothing, to stay quiet on production
hosts. When you diagnose a problem, you can increase the verbosity and send the
output to a file with environment variables on the sensor process. Set the
variables in your systemd unit, your launchd plist, or the Windows service
environment, so that the running service inherits them:

| Variable | Effect |
| --- | --- |
| `LC_VERBOSE` | Set to `1`/`true` to enable verbose logging (same as the `-v` flag). |
| `RPAL_LOG_LEVEL` | Sets the verbosity. Accepted values: `off`, `error` (alias `critical`), `warning` (alias `warn`), `info`, `debug`. Defaults to `warning` in release builds. |
| `RPAL_LOG_FILE` | Path to a log file. This variable turns on logging for a release sensor: the output goes to the file at `RPAL_LOG_LEVEL`. Without it (and without `LC_VERBOSE`), a release sensor stays silent. |

!!! note
In released sensors, `warning` is the most verbose level with output. The release builds do not include the `info` and `debug` log statements. A value of `info` or `debug` for `RPAL_LOG_LEVEL` has no more effect than `warning`.

For example, to capture logs to a file when you reproduce a problem:

=== "Linux / macOS"

    ```bash
    sudo RPAL_LOG_FILE=/tmp/lc_sensor.log RPAL_LOG_LEVEL=warning ./rphcp -d -
    ```

=== "Windows"

    ```bat
    set RPAL_LOG_FILE=C:\Temp\lc_sensor.log
    set RPAL_LOG_LEVEL=warning
    rphcp.exe -d -
    ```

The log file can contain operational details about the host. Treat the file as sensitive and delete it after you complete the troubleshooting.

For the full list of supported options, see the
[Agent CLI & Environment Reference](../../2-sensors-deployment/endpoint-agent/cli-reference.md).

## Additional Help

If these steps do not solve the problem, contact LimaCharlie for help. The first method of contact is the [Community Site](https://community.limacharlie.com/). The second method is `support@limacharlie.io`.

Like agents, Sensors send telemetry to the LimaCharlie platform as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless method to connect the endpoints of an organization to the cloud securely.

Installation keys are Base64-encoded strings that you give to Sensors and Adapters to connect them to the correct Organization. You create installation keys for each organization. The keys let you label and control your deployment population.

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives full control of security operations. This structure supports multi-tenant setups for managed security providers, and for enterprises that manage many departments or clients.

In LimaCharlie, a Sensor ID is a unique identifier for each deployed endpoint agent (sensor). It distinguishes individual sensors across the infrastructure of an organization. It lets LimaCharlie track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as commands, telemetry collection, and activity monitoring. It links actions and data accurately to a specific device or endpoint.
