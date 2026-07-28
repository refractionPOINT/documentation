# FAQ - Sensor Installation

## How can I add LimaCharlie traffic to an allow list?

The tables below list the hostnames and IPs for connections to LimaCharlie. All connections use TCP port 443 and TLS 1.2+

## What Hostnames and IPs does LimaCharlie use for each region?

### Canada (Quebec)

| Hostname | IP | Use |
| --- | --- | --- |
| aae67d7e76570ec1.lc.limacharlie.io | 35.203.33.203 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| aae67d7e76570ec1.edr.limacharlie.io | 35.201.82.57 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| aae67d7e76570ec1.wss.limacharlie.io | 35.201.96.199 | Chrome, Edge and Adapters |
| aae67d7e76570ec1.ingest.limacharlie.io | 34.149.216.238 | Logs and Artifacts |
| aae67d7e76570ec1.replay.limacharlie.io | 142.250.115.121 | Replay |
| aae67d7e76570ec1.live.limacharlie.io | 34.120.175.14 | Live feed |
| aae67d7e76570ec1.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### US (Iowa)

| Hostname | IP | Use |
| --- | --- | --- |
| 9157798c50af372c.lc.limacharlie.io | 35.194.62.236 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| 9157798c50af372c.edr.limacharlie.io | 34.149.165.165 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| 9157798c50af372c.wss.limacharlie.io | 34.102.223.182 | Chrome, Edge and Adapters |
| 9157798c50af372c.ingest.limacharlie.io | 34.120.157.194 | Logs and Artifacts |
| 9157798c50af372c.replay.limacharlie.io | 142.250.115.121 | Replay |
| 9157798c50af372c.live.limacharlie.io | 34.120.123.4 | Live feed |
| 9157798c50af372c.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### India (Mumbai)

| Hostname | IP | Use |
| --- | --- | --- |
| 4d897015b0815621.lc.limacharlie.io | 35.200.151.24 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| 4d897015b0815621.edr.limacharlie.io | 34.102.207.18 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| 4d897015b0815621.wss.limacharlie.io | 34.98.108.101 | Chrome, Edge and Adapters |
| 4d897015b0815621.ingest.limacharlie.io | 34.149.161.19 | Logs and Artifacts |
| 4d897015b0815621.replay.limacharlie.io | 142.250.115.121 | Replay |
| 4d897015b0815621.live.limacharlie.io | 35.244.221.119 | Live feed |
| 4d897015b0815621.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### UK (London)

| Hostname | IP | Use |
| --- | --- | --- |
| 70182cf634c346bd.lc.limacharlie.io | 35.242.152.114 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| 70182cf634c346bd.edr.limacharlie.io | 34.107.134.233 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| 70182cf634c346bd.wss.limacharlie.io | 35.244.147.201 | Chrome, Edge and Adapters |
| 70182cf634c346bd.ingest.limacharlie.io | 34.149.56.238 | Logs and Artifacts |
| 70182cf634c346bd.replay.limacharlie.io | 142.250.115.121 | Replay |
| 70182cf634c346bd.live.limacharlie.io | 35.244.146.102 | Live feed |
| 70182cf634c346bd.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### Europe (Emshaven)

| Hostname | IP | Use |
| --- | --- | --- |
| b76093c3662d5b4f.lc.limacharlie.io | 35.204.142.125 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| b76093c3662d5b4f.edr.limacharlie.io | 34.111.194.87 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| b76093c3662d5b4f.wss.limacharlie.io | 130.211.22.248 | Chrome, Edge and Adapters |
| b76093c3662d5b4f.ingest.limacharlie.io | 34.120.5.160 | Logs and Artifacts |
| b76093c3662d5b4f.replay.limacharlie.io | 142.250.115.121 | Replay |
| b76093c3662d5b4f.live.limacharlie.io | 34.120.64.23 | Live feed |
| b76093c3662d5b4f.hook.limacharlie.io | 142.250.115.121 | Webhooks |

### Australia (Sydney)

| Hostname | IP | Use |
| --- | --- | --- |
| abc32764762fce67.lc.limacharlie.io | 34.151.84.52 | Windows, Mac, & Linux EDR Agent  Note: Pinned SSL certificates (SSL interception unsupported) |
| abc32764762fce67.edr.limacharlie.io | 34.54.253.51 | Windows, Mac, & Linux EDR Agent  Note: Non-Pinned SSL certificates (SSL interception supported) |
| abc32764762fce67.wss.limacharlie.io | 34.96.104.54 | Chrome, Edge and Adapters |
| abc32764762fce67.ingest.limacharlie.io | 35.241.63.128 | Logs and Artifacts |
| abc32764762fce67.replay.limacharlie.io | 34.49.249.16 | Replay |
| abc32764762fce67.live.limacharlie.io | 34.8.102.215 | Live feed |
| abc32764762fce67.hook.limacharlie.io | 34.49.185.177 | Webhooks |

## How much data does the LimaCharlie Sensor produce per day?

The quantity of data depends on the quantity and the type of activity on the endpoint. Across thousands of deployments, the average is about 1MB for each endpoint each day.

## What resources does the LimaCharlie agent consume?

The agent uses about 50MB in total, on disk and in memory. The agent usually runs at less than 1% CPU.

Some actions increase the CPU usage. For example, a full YARA scan increases the CPU usage. The YARA trickle scan keeps the CPU usage low. Only a full manual scan causes a large increase in CPU usage.

The network bandwidth changes with the configuration of the agent, which you can customize. On Windows hosts, the bandwidth is usually about 2MB each day.

## Why does my sensor initially connect successfully but then disappear?

Sometimes the agent connects to the LimaCharlie cloud and enrolls. It then disconnects, which is normal the first time after enrollment. After that, it never connects again, or it does not show that it acquired the kernel.

SSL interception usually causes this behavior. A network device can do the interception. A security product on the host can also do it, and this is less obvious.

To find SSL interception, do the steps below. The steps check the SSL fingerprint of the LimaCharlie cloud from the host.

**Confirm the region of your** Organization

If you know the region of your organization, go to the next step. To find the region where the data is processed and stored, click `Add Sensor` in the `Sensors` view. The region shows under `Sensor Connectivity`.

**Open the test URL**
In a web browser, go to the test URL for your region:

[Test URL - US Region](https://9157798c50af372c.lc.limacharlie.io/)
[Test URL - UK Region](https://70182cf634c346bd.lc.limacharlie.io/)
[Test URL - India Region](https://4d897015b0815621.lc.limacharlie.io/)
[Test URL - Europe Region](https://b76093c3662d5b4f.lc.limacharlie.io/)
[Test URL - Canada Region](https://aae67d7e76570ec1.lc.limacharlie.io/)

No website opens. Instead, you get a message similar to "Your connection is not private".

### Display the SSL Certificate

Click the exclamation mark near the URL bar. A small menu opens. Click "Certificate status", "Certificate validity", or "Certificate is not valid" to show the certificate information.

### Confirm the SHA-1 and SHA-256 fingerprints

The SHA-1 and SHA-256 fingerprints must match the values below for the region of your organization.

If the fingerprints that you see do not match the values below, SSL interception occurs.

| Region | SHA-256 Fingerprint | SHA-1 Fingerprint |
| --- | --- | --- |
| US | 14 44 8C B6 A1 19 A5 BE 18 AE 28 07 E3 D6 BD 55 B8 7A 5E 0C 3F 2D 78 03 6E 7C 6A 2A AA 45 8F 60 | 1A 72 67 08 D0 83 7D A9 62 85 39 55 A1 12 1B 10 B0 F4 56 1A |
| UK | 49 49 B0 41 D6 14 F3 3B 86 BF DF 14 24 F8 BD 2F E1 98 39 41 5A 99 E6 F1 C7 A2 C8 AB 34 0C FE 1D | 2E 49 00 DB F8 3A 2A 88 E0 15 76 D5 C5 4F 8F F3 7D 27 77 DD |
| India | 68 6F 08 3D 53 3F 08 E0 22 EB F6 67 0C 3C 41 08 75 D6 0E 67 03 88 D9 B6 E1 F8 19 6B DA 54 5A A3 | 37 57 DD 4E CF 2B 25 0B CA EA E2 E6 E3 B2 98 48 29 19 F3 6B |
| Europe | EF B3 FA A7 78 AB F0 B0 41 00 CF A3 5F 44 3F 9A 4D 16 28 B9 83 22 85 E3 36 44 D5 DC F9 5C 78 5B | 07 72 B3 31 1A 89 D6 54 1D 71 C3 07 AD B5 8A 26 FD 30 7E 5D |
| Canada | D3 40 8B 59 AE 5A 28 75 D1 65 71 50 52 2E 6F 45 26 EE E8 19 3A 9A 74 39 C1 64 60 B8 6A 92 15 47 | E3 EF AE 6A 0E 7F 18 83 15 FE F2 02 6C F3 2D 4E 59 95 4D 0A |

## What happens if a host is offline?

If the host is offline, the Sensor continues to collect telemetry. It stores the telemetry locally in a "ring buffer", which limits the total size. The buffer is ~60mb. The period that the buffer covers changes with the quantity of telemetry from the endpoint. For example, a domain controller generates many more events than a normal workstation.

When the host is online again, the Sensor sends the content of the buffer to the cloud. The detection and response rules then apply as usual.

The Sensor uses the same ring buffer in normal operation, even if it does not send the data to the cloud in real time. The cloud can then request all or part of the content of the ring buffer to make your telemetry current.

## How can I tell which Installation Key was used to enroll a sensor?

To find the installation key that enrolled a sensor, compare the `Installer ID` of the sensor with the `Adapter Key` value of the installation key.

1. In the Sensors section, open the details page of the sensor. Record the `Installer ID`.
2. Go to the Install Sensors section. Click the copy icon below the `Adapter Key`.
3. Compare the two values. The `Installer ID` of a sensor is the same as the `Adapter Key` of the installation key that the sensor used.

To check many sensors, export all sensors from the main sensors list page, or use the LimaCharlie API.

Like agents, Sensors send telemetry to the LimaCharlie platform as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless method to connect the endpoints of an organization to the cloud securely.

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives full control of security operations. This structure supports multi-tenant setups for managed security providers, and for enterprises that manage many departments or clients.

Installation keys are Base64-encoded strings that you give to Sensors and Adapters to connect them to the correct Organization. You create installation keys for each organization. The keys let you label and control your deployment population.

Adapters ingest data from on-premise environments and from cloud environments.
