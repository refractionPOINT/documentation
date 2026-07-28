# Adapter Deployment

You can deploy adapters in two ways:

- **On-prem**, adapters use the LC Adapter binary to ingest a data source and send it to LimaCharlie.
- **Cloud-to-cloud**, connects the LimaCharlie cloud directly with your cloud source and ingests data automatically.

Adapter choice for cloud data.

You can use an on-prem adapter to send cloud data to LimaCharlie. You can also get the same data with a cloud-to-cloud connection.

The choice depends on _how_ you want to send your data to LimaCharlie. A cloud-to-cloud connection is configured in the LimaCharlie cloud. An on-prem adapter puts a bastion box between the source and LimaCharlie. Both methods work.

LimaCharlie parses and maps the data from adapters into JSON. It uses the parameters that you supply, unless you use a pre-defined format.

## Adapter Binaries

Software-based, or "on-prem", adapters are available in these formats:

### POSIX-compliant

- [AIX ppc64](https://downloads.limacharlie.io/adapter/aix/ppc64)
- [Linux (Generic) 64-bit](https://downloads.limacharlie.io/adapter/linux/64)
- [Linux (Generic) arm](https://downloads.limacharlie.io/adapter/linux/arm)
- [Linux (Generic) arm64](https://downloads.limacharlie.io/adapter/linux/arm64)
- [FreeBSD 64-bit](https://downloads.limacharlie.io/adapter/freebsd/64)
- [OpenBSD 64-bit](https://downloads.limacharlie.io/adapter/openbsd/64)
- [NetBSD 64-bit](https://downloads.limacharlie.io/adapter/netbsd/64)
- [Solaris 64-bit](https://downloads.limacharlie.io/adapter/solaris/64)

### macOS

- [macOS x64](https://downloads.limacharlie.io/adapter/mac/64)
- [macOS arm64](https://downloads.limacharlie.io/adapter/mac/arm64)

### Windows

- [Windows x64](https://downloads.limacharlie.io/adapter/windows/64)

### Docker

- <https://hub.docker.com/r/refractionpoint/lc-adapter>

Other platforms.

If you need support for a specific platform, or more information about supported platforms, [contact LimaCharlie](https://www.limacharlie.io/contact).

## On-Prem + Cloud Management

LimaCharlie Adapters that you deploy manually (on-prem) also support cloud-based management. With cloud-based management, you can update the configs remotely after the deployment. This is important for service providers that deploy adapters on customer networks, where access to the local adapter is difficult.

To do this, you need the `externaladapter.*` permissions.

### Preparing

First, create a new External Adapter record. These records are in the `external_adapter` Hive, or under the Sensors section of the web app.

The content of an external adapter is the same as a traditional [adapter configuration](usage.md) in YAML. It describes what your external adapter does, such as collection from a file or operation as a syslog server. For example:

```yaml
sensor_type: syslog
syslog:
    client_options:
        buffer_options: {}
        hostname: test-syslog
        identity:
            installation_key: aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
            oid: bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb
        mapping: {}
        platform: text
        sensor_seed_key: test-syslog
    port: 4242
```

After you create the external adapter record, find the `GUID` (Globally Unique ID). It is under the `sys_mtd` section of the JSON record, or on the right side of the record view in the web app

.

The `GUID` is a shared secret. The deployed adapter uses the `GUID` to point to the record that it must update and operate from.

### Deploying

After the adapter configuration is ready, deploy the adapter on-prem with the [normal process](usage.md). Run the adapter with the `cloud` collection method instead of the full local configuration:

```bash
./lc_adapter cloud conf_guid=XXXXXXXXXXXXXXXXXXXXx oid=YYYYYYYYYYYYYYYYYYY
```

The adapter starts and fetches the configuration that it needs from the cloud. It uses the Organization ID (your tenant in LC) and the `GUID` of the record.

After this, an update to the record in LimaCharlie reconfigures the on-prem adapter automatically, in about 1 minute.

Adapters ingest data in on-premise and cloud environments.
