# How can I add LimaCharlie traffic to an allow list?

The tables below show the hostnames and IPs used to connect to LimaCharlie. All connections use TCP port 443 and TLS 1.2+

## What Hostnames and IPs does LimaCharlie use for each region?

### Canada (Quebec)

Hostname| IP| Use  
---|---|---  
aae67d7e76570ec1.lc.limacharlie.io| 35.203.33.203| Windows, Mac, & Linux EDR Agent

> Note: Pinned SSL certificates (SSL interception unsupported)  
  
aae67d7e76570ec1.edr.limacharlie.io| 35.201.82.57| Windows, Mac, & Linux EDR Agent

> Note: Non-Pinned SSL certificates (SSL interception supported)  
  
aae67d7e76570ec1.wss.limacharlie.io| 35.201.96.199| Chrome, Edge and Adapters  
aae67d7e76570ec1.ingest.limacharlie.io| 34.149.216.238| Logs and Artifacts  
aae67d7e76570ec1.replay.limacharlie.io| 142.250.115.121| Replay  
aae67d7e76570ec1.live.limacharlie.io| 34.120.175.14| Live feed  
aae67d7e76570ec1.hook.limacharlie.io| 142.250.115.121| Webhooks  
  
### US (Iowa)

Hostname| IP| Use  
---|---|---  
9157798c50af372c.lc.limacharlie.io| 35.194.62.236| Windows, Mac, & Linux EDR Agent

> Note: Pinned SSL certificates (SSL interception unsupported)  
  
9157798c50af372c.edr.limacharlie.io| 34.149.165.165| Windows, Mac, & Linux EDR Agent

> Note: Non-Pinned SSL certificates (SSL interception supported)  
  
9157798c50af372c.wss.limacharlie.io| 34.102.223.182| Chrome, Edge and Adapters  
9157798c50af372c.ingest.limacharlie.io| 34.120.157.194| Logs and Artifacts  
9157798c50af372c.replay.limacharlie.io| 142.250.115.121| Replay  
9157798c50af372c.live.limacharlie.io| 34.120.123.4| Live feed  
9157798c50af372c.hook.limacharlie.io| 142.250.115.121| Webhooks  
  
### India (Mumbai)

Hostname| IP| Use  
---|---|---  
4d897015b0815621.lc.limacharlie.io| 35.200.151.24| Windows, Mac, & Linux EDR Agent

> Note: Pinned SSL certificates (SSL interception unsupported)  
  
4d897015b0815621.edr.limacharlie.io| 34.102.207.18| Windows, Mac, & Linux EDR Agent

> Note: Non-Pinned SSL certificates (SSL interception supported)  
  
4d897015b0815621.wss.limacharlie.io| 34.98.108.101| Chrome, Edge and Adapters  
4d897015b0815621.ingest.limacharlie.io| 34.149.161.19| Logs and Artifacts  
4d897015b0815621.replay.limacharlie.io| 142.250.115.121| Replay  
4d897015b0815621.live.limacharlie.io| 35.244.221.119| Live feed  
4d897015b0815621.hook.limacharlie.io| 142.250.115.121| Webhooks  
  
### UK (London)

Hostname| IP| Use  
---|---|---  
70182cf634c346bd.lc.limacharlie.io| 35.242.152.114| Windows, Mac, & Linux EDR Agent

> Note: Pinned SSL certificates (SSL interception unsupported)  
  
70182cf634c346bd.edr.limacharlie.io| 34.107.134.233| Windows, Mac, & Linux EDR Agent

> Note: Non-Pinned SSL certificates (SSL interception supported)  
  
70182cf634c346bd.wss.limacharlie.io| 35.244.147.201| Chrome, Edge and Adapters  
70182cf634c346bd.ingest.limacharlie.io| 34.149.56.238| Logs and Artifacts  
70182cf634c346bd.replay.limacharlie.io| 142.250.115.121| Replay  
70182cf634c346bd.live.limacharlie.io| 35.244.146.102| Live feed  
70182cf634c346bd.hook.limacharlie.io| 142.250.115.121| Webhooks  
  
### Europe (Emshaven)

Hostname| IP| Use  
---|---|---  
b76093c3662d5b4f.lc.limacharlie.io| 35.204.142.125| Windows, Mac, & Linux EDR Agent

> Note: Pinned SSL certificates (SSL interception unsupported)  
  
b76093c3662d5b4f.edr.limacharlie.io| 34.111.194.87| Windows, Mac, & Linux EDR Agent

> Note: Non-Pinned SSL certificates (SSL interception supported)  
  
b76093c3662d5b4f.wss.limacharlie.io| 130.211.22.248| Chrome, Edge and Adapters  
b76093c3662d5b4f.ingest.limacharlie.io| 34.120.5.160| Logs and Artifacts  
b76093c3662d5b4f.replay.limacharlie.io| 142.250.115.121| Replay  
b76093c3662d5b4f.live.limacharlie.io| 34.120.64.23| Live feed  
b76093c3662d5b4f.hook.limacharlie.io| 142.250.115.121| Webhooks  
  
### Australia (Sydney)

Hostname| IP| Use  
---|---|---  
abc32764762fce67.lc.limacharlie.io| 34.151.84.52| Windows, Mac, & Linux EDR Agent

> Note: Pinned SSL certificates (SSL interception unsupported)  
  
abc32764762fce67.edr.limacharlie.io| 34.54.253.51| Windows, Mac, & Linux EDR Agent

> Note: Non-Pinned SSL certificates (SSL interception supported)  
  
abc32764762fce67.wss.limacharlie.io| 34.96.104.54| Chrome, Edge and Adapters  
abc32764762fce67.ingest.limacharlie.io| 35.241.63.128| Logs and Artifacts  
abc32764762fce67.replay.limacharlie.io| 34.49.249.16| Replay  
abc32764762fce67.live.limacharlie.io| 34.8.102.215| Live feed  
abc32764762fce67.hook.limacharlie.io| 34.49.185.177| Webhooks  
  
## How much data does the LimaCharlie Sensor produce per day?

The amount of data that is produced by the sensor is dependent on how much, and what kind of activity is taking place on the endpoint. That being said, the average data produced per endpoint across thousands of deployments is approximately 1MB per day.

## What resources does the LimaCharlie agent consume?

The total footprint of the agent on disk combined with what is in memory is approximately 50MB. The agent typically runs under 1% CPU.

Depending on what actions you may be performing it may increase (e.g. if you’re doing a full YARA scan it’s expected that the CPU usage will increase). When you use our YARA trickle scan, that also keeps CPU usage within reasonable bounds. You’ll only see YARA scans spike CPU when you do a full manual scan.

Depending on the configuration of the agent (it’s fully customizable), the network bandwidth will vary, but we typically see approximately 2MB per day on Windows hosts.

## Why does my sensor initially connect successfully but then disappear?

Sometimes we see the agent connect to the LimaCharlie cloud, enrolls, then disconnects (which is normal the first time after enrollment) and never connects again, or it doesn't show that kernel has been acquired.

This behavior is typical with SSL interception. Sometimes it's a network device, but at other times some security products on the host can do that without being very obvious.

You can confirm if there is SSL interception by performing the following steps to check the SSL fingerprint of the LimaCharlie cloud from the host.

**Confirm the region of your** Organization

If you already know where your organization's region is located, you can move to the next step. To verify the organization's region where the data is processed and stored, click `Add Sensor` from the `Sensors` view. You will then see the region listed under `Sensor Connectivity`.  
![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/installation(1).png)

**Open the test URL**  
Via web browser, navigate to one of the below test URLs that corresponds to the correct region:

[Test URL - US Region](https://9157798c50af372c.lc.limacharlie.io/)  
[Test URL - UK Region](https://70182cf634c346bd.lc.limacharlie.io/)  
[Test URL - India Region](https://4d897015b0815621.lc.limacharlie.io/)  
[Test URL - Europe Region](https://b76093c3662d5b4f.lc.limacharlie.io/)  
[Test URL - Canada Region](https://aae67d7e76570ec1.lc.limacharlie.io/)

No website will open; you should get a "Your connection is not private" type of message instead.

**Display the SSL Certificate**

By clicking near the URL bar on the exclamation mark, you will open a small menu and you can click "Certificate status"/"Certificate validity"/"Certificate is not valid" which will display the certificate information.

![certifricate](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/certifricate.png)

![certificate-1](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/certificate-1.png)

**Confirm the SHA-1 and SHA-256 fingerprints**

The SHA-1 and SHA-256 fingerprints should match the values below that correspond to the region your organization is in.

If the SHA-1 and SHA-256 fingerprints you are seeing do not match what's listed below, that's an indicator of the SSL interception.

Region| SHA-256 Fingerprint| SHA-1 Fingerprint  
---|---|---  
US| 14 44 8C B6 A1 19 A5 BE 18 AE 28 07 E3 D6 BD 55 B8 7A 5E 0C 3F 2D 78 03 6E 7C 6A 2A AA 45 8F 60| 1A 72 67 08 D0 83 7D A9 62 85 39 55 A1 12 1B 10 B0 F4 56 1A  
UK| 49 49 B0 41 D6 14 F3 3B 86 BF DF 14 24 F8 BD 2F E1 98 39 41 5A 99 E6 F1 C7 A2 C8 AB 34 0C FE 1D| 2E 49 00 DB F8 3A 2A 88 E0 15 76 D5 C5 4F 8F F3 7D 27 77 DD  
India| 68 6F 08 3D 53 3F 08 E0 22 EB F6 67 0C 3C 41 08 75 D6 0E 67 03 88 D9 B6 E1 F8 19 6B DA 54 5A A3| 37 57 DD 4E CF 2B 25 0B CA EA E2 E6 E3 B2 98 48 29 19 F3 6B  
Europe| EF B3 FA A7 78 AB F0 B0 41 00 CF A3 5F 44 3F 9A 4D 16 28 B9 83 22 85 E3 36 44 D5 DC F9 5C 78 5B| 07 72 B3 31 1A 89 D6 54 1D 71 C3 07 AD B5 8A 26 FD 30 7E 5D  
Canada| D3 40 8B 59 AE 5A 28 75 D1 65 71 50 52 2E 6F 45 26 EE E8 19 3A 9A 74 39 C1 64 60 B8 6A 92 15 47| E3 EF AE 6A 0E 7F 18 83 15 FE F2 02 6C F3 2D 4E 59 95 4D 0A  
  
## What happens if a host is offline?

When the host is offline, the Sensor will keep collecting telemetry and store it locally in a "ring buffer" (which limits the total possible size). The buffer is ~60mb, so the amount of time it will cover will vary based on how much telemetry the individual endpoint generates. e.g. A domain controller will likely be generating many more events than a regular end user workstation.

When the host is back online, the content of this buffer will be flushed to the cloud where [detection and response](../Detection and Response/detection-and-response-examples.md) rules will apply as usual.

The same ring buffer is used when the Sensor runs normally, even if data is not sent to the cloud in real-time. The cloud can then retroactively request the full or partial content of the ring buffer, bringing your telemetry current.

## How can I tell which Installation Key was used to enroll a sensor?

On occasion you may need to check which installation key was used to enroll a sensor. You can do so by comparing the sensors `Installer ID` with the Installation Key's `Adapter Key` value.

  1. Go to the Sensors section and click into the sensor in question to view its details page. Take note of the `Installer ID`.

  2. Go to the Install Sensors section. Click the copy icon under the `Adapter Key`.

  3. Compare these two values; the Installer ID on a sensor should be the same as the Adapter Key of the installation key used.




If you need to check a large list of sensors, you can perform an export of all sensors from the main sensors list page, or use the LimaCharlie API.


