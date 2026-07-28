# Reference: ID Schema

## Agent IDs

An AgentID is a 5-tuple that describes a Sensor fully. A Sensor ID is the smallest single identifier that can identify a sensor.

The components of the AgentID are: `OID.IID.SID.PLATFORM.ARCHITECTURE`.

For all components, a value of `0` is a wildcard. The wildcard matches any value when you compare AgentIDs as masks.

## Architecture

The architecture is an 8 bit integer that identifies the exact architecture that the sensor runs on. The important values are:

- `1`: 32 bit (`x86`)
- `2`: 64 bit (`x64`)
- `3`: ARM (`arm`)
- `4`: ARM64 (`arm64`)
- `5`: Alpine 64 (`alpine64`)
- `6`: Chrome (`chromium`)
- `7`: Wireguard (`wireguard`)
- `8`: ARML (`arml`)
- `9`: lc-adapter (`usp_adapter`)

Operating System Specifics

For more detailed version information about a specific operating system, see these vendor guides:

- [Microsoft Windows](https://learn.microsoft.com/en-us/windows/win32/sysinfo/operating-system-version)
- [RHEL](https://access.redhat.com/articles/3078)
- [Ubuntu](https://wiki.ubuntu.com/Releases)

## Device IDs

LimaCharlie supports many platforms. Thus, more than one sensor can see the same "device" (laptop, server, mobile etc). A basic example is:

- A laptop uses macOS as its operating system, and runs a macOS sensor
- The laptop also runs a Windows Virtual Machine, which runs a Windows sensor

In this example, there is one piece of hardware, but two different sensors.

To give a full view of the activity, LimaCharlie has the Device ID. This ID shows in the basic info of the sensor, and in the `routing` component of sensor events with the name `did` (Device ID).

LimaCharlie generates and assigns the Device ID automatically. It correlates specific low level events that are common to all the sensors. If two sensors have the same `did: 1234-5678...` ID, they are on the same device, or they have the same visibility. Sensors with the same visibility see the same activity from two angles.

## Installer ID

The Installer ID (IID) is a UUID that identifies a unique Installation Key. The IID makes it possible to cycle installation keys and to repudiate old keys if a key leaks.

## Organization ID

The Organization ID (OID) is a UUID which identifies a unique organization.

## Platform

The platform is a 32-bit integer (in its hex format) that identifies the exact platform that the sensor runs on. Sensor telemetry shows the `plat` value in decimal format. The platform has a major part and a minor part, but the important values are:

| Hex ID     | Decimal    | API Name                     | Platform Name                |
|------------|------------|------------------------------|------------------------------|
| 0x01000000 | 16777216   | crowdstrike                  | CrowdStrike                  |
| 0x02000000 | 33554432   | xml                          | XML                          |
| 0x03000000 | 50331648   | wel                          | Windows Event Logs           |
| 0x04000000 | 67108864   | msdefender                   | Microsoft Defender           |
| 0x05000000 | 83886080   | duo                          | Duo                          |
| 0x06000000 | 100663296  | okta                         | Okta                         |
| 0x07000000 | 117440512  | sentinel_one                 | SentinelOne                  |
| 0x08000000 | 134217728  | github                       | GitHub                       |
| 0x09000000 | 150994944  | slack                        | Slack                        |
| 0x0A000000 | 167772160  | cef                          | Common Event Format (CEF)    |
| 0x0B000000 | 184549376  | lc_event                     | LimaCharlie Events           |
| 0x0C000000 | 201326592  | azure_ad                     | Azure Active Directory       |
| 0x0D000000 | 218103808  | azure_monitor                | Azure Monitor                |
| 0x0E000000 | 234881024  | canary_token                 | Canary Token                 |
| 0x0F000000 | 251658240  | guard_duty                   | Guard Duty                   |
| 0x11000000 | 285212672  | itglue                       | IT Glue                      |
| 0x12000000 | 301989888  | k8s_pods                     | Kubernetes Pods              |
| 0x13000000 | 318767104  | zeek                         | Zeek                         |
| 0x14000000 | 335544320  | mac_unified_logging          | Macos Unified Logging        |
| 0x15000000 | 352321536  | azure_event_hub_namespace    | Azure Event Hub Namespace    |
| 0x16000000 | 369098752  | azure_key_vault              | Azure Key Vault              |
| 0x17000000 | 385875968  | azure_kubernetes_service     | Azure Kubernetes Service     |
| 0x18000000 | 402653184  | azure_network_security_group | Azure Network Security Group |
| 0x19000000 | 419430400  | azure_sql_audit              | Azure SQL Audit              |
| 0x1A000000 | 436207616  | email                        | Email                        |
| 0x1B000000 | 452984832  | fortigate                    | Fortigate                    |
| 0x1C000000 | 469762048  | trend_worryfree              | Trend Worry Free             |
| 0x1D000000 | 486539264  | netscaler                    | Netscaler                    |
| 0x1E000000 | 503316480  | paloalto_fw                  | Palo Alto Firewall           |
| 0x1F000000 | 520093696  | iis                          | Internet Information Services|
| 0x21000000 | 553648128  | hubspot                      | HubSpot                      |
| 0x22000000 | 570425344  | zendesk                      | Zendesk                      |
| 0x23000000 | 587202560  | pandadoc                     | PandaDoc                     |
| 0x24000000 | 603979776  | falconcloud                  | FalconCloud                  |
| 0x25000000 | 620756992  | mimecast                     | Mimecast                     |
| 0x26000000 | 637534208  | sublime                      | Sublime                      |
| 0x27000000 | 654311424  | box                          | Box                          |
| 0x28000000 | 671088640  | cylance                      | Cylance                      |
| 0x29000000 | 687865856  | proofpoint                   | Proofpoint                   |
| 0x2A000000 | 704643072  | entraid                      | EntraID                      |
| 0x2B000000 | 721420288  | wiz                          | Wiz                          |
| 0x2C000000 | 738197504  | bitwarden                    | Bitwarden                    |
| 0x2D000000 | 754974720  | trend_micro                  | Trend Micro                  |
| 0x2E000000 | 771751936  | otel                         | OpenTelemetry                |
| 0x2F000000 | 788529152  | cortex_xdr                   | Cortex XDR                   |
| 0x31000000 | 822083584  | harmony                      | Check Point Harmony          |
| 0x32000000 | 838860800  | threatlocker                 | ThreatLocker                 |
| 0x33000000 | 855638016  | halopsa                      | HaloPSA                      |
| 0x10000000 | 268435456  | windows                      | Windows                      |
| 0x20000000 | 536870912  | linux                        | Linux                        |
| 0x30000000 | 805306368  | macos                        | MacOS                        |
| 0x40000000 | 1073741824 | ios                          | iOS                          |
| 0x50000000 | 1342177280 | android                      | Android                      |
| 0x60000000 | 1610612736 | chrome                       | ChromeOS                     |
| 0x70000000 | 1879048192 | vpn                          | VPN                          |
| 0x80000000 | 2147483648 | text                         | Text (external telemetry)    |
| 0x90000000 | 2415919104 | json                         | JSON (external telemetry)    |
| 0xA0000000 | 2684354560 | gcp                          | GCP (external telemetry)     |
| 0xB0000000 | 2952790016 | aws                          | AWS (external telemetry)     |
| 0xC0000000 | 3221225472 | carbon_black                 | VMWare Carbon Black          |
| 0xD0000000 | 3489660928 | 1password                    | 1Password                    |
| 0xE0000000 | 3758096384 | office365                    | Microsoft/Office 365         |
| 0xF0000000 | 4026531840 | sophos                       | Sophos                       |

Tip: In a rule that targets a specific platform, use the `is platform` operator and not the decimal value. The rule is then easier to read.

## Sensor ID

The Sensor ID (SID) is a UUID that identifies a unique sensor.

Like agents, Sensors send telemetry to the LimaCharlie platform as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless method to connect the endpoints of an organization to the cloud securely.

In LimaCharlie, a Sensor ID is a unique identifier for each deployed endpoint agent (sensor). It distinguishes individual sensors across the infrastructure of an organization. It lets LimaCharlie track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as commands, telemetry collection, and activity monitoring. It links actions and data accurately to a specific device or endpoint.

Installation keys are Base64-encoded strings that you give to Sensors and Adapters to connect them to the correct Organization. You create installation keys for each organization. The keys let you label and control your deployment population.

In LimaCharlie, an Organization ID is a unique identifier for each tenant or customer account. It distinguishes the organizations in the platform. It lets LimaCharlie manage resources, permissions, and the separation of data securely. The Organization ID keeps all telemetry, configurations, and operations isolated and specific to each organization. This gives multi-tenant support and a clear separation between customer environments.

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives full control of security operations. This structure supports multi-tenant setups for managed security providers, and for enterprises that manage many departments or clients.

In LimaCharlie, an Organization ID (OID) is a unique identifier for each tenant or customer account. It distinguishes the organizations in the platform. It lets LimaCharlie manage resources, permissions, and the separation of data securely. The Organization ID keeps all telemetry, configurations, and operations isolated and specific to each organization. This gives multi-tenant support and a clear separation between customer environments.

In LimaCharlie, a Sensor ID (SID) is a unique identifier for each deployed endpoint agent (sensor). It distinguishes individual sensors across the infrastructure of an organization. It lets LimaCharlie track, manage, and communicate with each endpoint. The Sensor ID is critical for operations such as commands, telemetry collection, and activity monitoring. It links actions and data accurately to a specific device or endpoint.
