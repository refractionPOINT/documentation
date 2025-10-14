# Adapter Deployment and Usage

Adapters serve as flexible data ingestion mechanisms that can be deployed in two ways:

* **On-prem**: Adapters utilize the LC Adapter binary to ingest a data source and forward it to LimaCharlie.
* **Cloud-to-cloud**: Connects the LimaCharlie cloud directly with your cloud source and automatically ingests data.

## Choosing Between On-Prem and Cloud-to-Cloud for Cloud Data

You can use on-prem adapters to forward cloud data, or acquire the same data with a cloud-to-cloud connection. The choice depends on *how* you want to send your data to LimaCharlie. Are you OK with configuring a connector from the platform, or would you rather use a bastion box in between? Either approach works.

The data ingested from adapters is parsed/mapped into JSON by LimaCharlie, according to the parameters you provided, unless using a pre-defined format.

## Adapter Binaries

Software-based, or "on-prem" adapters are available in the following formats:

* **Binaries:**

  + **\*nix**
    - [AIX ppc64](https://downloads.limacharlie.io/adapter/aix/ppc64)
    - [Linux (Generic) 64-bit](https://downloads.limacharlie.io/adapter/linux/64)
    - [Linux (Generic) arm](https://downloads.limacharlie.io/adapter/linux/arm)
    - [Linux (Generic) arm64](https://downloads.limacharlie.io/adapter/linux/arm64)
    - [FreeBSD 64-bit](https://downloads.limacharlie.io/adapter/freebsd/64)
    - [OpenBSD 64-bit](https://downloads.limacharlie.io/adapter/openbsd/64)
    - [NetBSD 64-bit](https://downloads.limacharlie.io/adapter/netbsd/64)
    - [Solaris 64-bit](https://downloads.limacharlie.io/adapter/solaris/64)
  + **macOS**
    - [macOS x64](https://downloads.limacharlie.io/adapter/mac/64)
    - [macOS arm64](https://downloads.limacharlie.io/adapter/mac/arm64)
  + **Windows**
    - [Windows x64](https://downloads.limacharlie.io/adapter/windows/64)

* **Docker:**
  + <https://hub.docker.com/r/refractionpoint/lc-adapter>

> **Another platform?**
>
> If you need support for a specific platform, or require more information about supported platforms, please [let us know](https://www.limacharlie.io/contact).

## On-Prem Adapters with Cloud Management

LimaCharlie Adapters deployed manually (on-prem) support cloud-based management. This makes deployment extremely easy while also making it easy to update the configs remotely after the fact. This is particularly critical for service providers that may be deploying adapters on customer networks where gaining access to the local adapter may be difficult.

To accomplish this, you need the `externaladapter.*` permissions.

### Preparing Cloud-Managed Deployment

The first step is to create a new External Adapter record. These are found in the `external_adapter` Hive or under the Sensors section of the web app.

The content of an external adapter is exactly the same as a traditional adapter configuration in YAML. It describes what you want your external adapter to do, like collect from file, operate as a syslog server etc. For example:

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

Once your external adapter record is created, take note of the `GUID` (Globally Unique ID) found under the `sys_mtd` section of the JSON record, or on the right-hand side of the record view in the web app.

![External Adapter GUID location](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(308).png)

This `GUID` is a shared secret value you will use in the deployed adapter to reference it to the record it should update and operate from.

### Deploying with Cloud Management

Now that the configuration of the adapter is ready, you can deploy the adapter on-prem. Instead of running it with the full configuration locally, you can run it with the `cloud` collection method like this:

```bash
./lc_adapter cloud conf_guid=XXXXXXXXXXXXXXXXXXXXx oid=YYYYYYYYYYYYYYYYYYY
```

This will start the adapter telling it to fetch the configuration it requires from the cloud based on the Organization ID (your tenant in LC) and the `GUID` of the record it should use.

From this point on, updating the record in LimaCharlie will automatically reconfigure the adapter on-prem, within about 1 minute of the change.

## Adapter Examples

### Stdin

This example uses the CLI Adapter and receives data from the CLI's STDIN interface. This method is perfect for ingesting arbitrary logs on disk or from other applications locally.

```bash
./lc_adapter stdin client_options...
```

### Stdin JSON

This example is similar to Stdin, except it assumes the data being read is JSON, not just text. If your data source is already JSON, it's much simpler to let LimaCharlie do the JSON parsing directly.

```bash
./lc_adapter stdin client_options...
```

### Windows Event Logs

This example shows collecting Windows Event Logs (wel) from a Windows box natively (and therefore is only available using the Windows Adapter). This is useful for cases where you'd like to collect WEL without running the LimaCharlie Windows Agent.

## Tutorials

### Tutorial: Creating a Webhook Adapter

LimaCharlie supports webhooks as a telemetry ingestion method. Webhooks are technically cloud Adapters, as they cannot be deployed on-prem or through the downloadable Adapter binary. Webhook adapters are created by enabling a webhook through the platform.

[Link to full tutorial](/docs/tutorial-creating-a-webhook-adapter)

### Tutorial: Ingesting Google Cloud Logs

With LimaCharlie, you can easily ingest Google Cloud logs for further processing and automation. This article covers the following high-level steps of shipping logs from GCP into LimaCharlie:

- Create a Log Sink to Pubsub in GCP
- Create a Subscription in LimaCharlie

[Link to full tutorial](/docs/tutorial-ingesting-google-cloud-logs)

### Tutorial: Ingesting Telemetry from Cloud-Based External Sources

LimaCharlie allows for ingestion of logs or telemetry from any external source in real-time. It includes built-in parsing for popular formats, with the option to define your own for custom sources.

[Link to full tutorial](/docs/tutorial-ingesting-telemetry-from-cloud-based-external-sources)