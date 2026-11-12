# Cloud-Managed Adapters (External Adapters)

A cloud-managed adapter runs on a host you control, like any on-prem adapter, but reads its configuration from LimaCharlie instead of from a local file or command line. You keep the configuration in an **External Adapter** record in your organization. The adapter on the host only needs two values to start: your Organization ID and the record's GUID.

After that, you change the adapter from the web app, the CLI, the API or Infrastructure as Code. The running adapter picks up the change within about a minute, with nobody logging in to the host.

This is the best way to run adapters that you need to deploy once and then manage remotely, for example on a customer network you don't have shell access to, or on many sites that share the same settings.

## Choosing how to run an adapter

LimaCharlie adapters run in one of three ways. The adapter code and the configuration format are the same in all three. What changes is where the adapter runs and where its configuration lives.

| | Local configuration | Cloud-managed (External Adapter) | Cloud Adapter |
| --- | --- | --- | --- |
| Where the adapter runs | Your host | Your host | LimaCharlie's cloud |
| Where the configuration lives | A file or command line on the host | An `external_adapter` record in LimaCharlie | A `cloud_sensor` record in LimaCharlie |
| How you change it | Edit the file on the host, restart the adapter | Edit the record; the adapter applies it within about a minute | Edit the record |
| Reaches private networks and local files | Yes | Yes | No, only sources reachable from the internet |
| Configuration checked when you save it | No, errors show when the adapter starts | Yes, LimaCharlie rejects an invalid record | Yes |
| Credentials | On the host | In the record, see [Security](#security) | Can reference [Hive secrets](../../7-administration/config-hive/secrets.md) |
| Needs LimaCharlie reachable to load its configuration | No | Yes, when the adapter starts | Not applicable |

Use a **Cloud Adapter** when the source is a cloud service that LimaCharlie can reach directly, such as Microsoft 365, Okta or an S3 bucket. Nothing runs on your side.

Use a **cloud-managed adapter** when the adapter has to run inside a network: a syslog listener for firewalls, a file or Windows Event Log collector, or an API that is only reachable from inside. It is the right default for service providers and for anyone deploying to more than a handful of hosts.

Use a **local configuration** when the host must not depend on LimaCharlie for its configuration, or when you want the configuration to live only on the host.

## How it works

1. You create an External Adapter record. LimaCharlie validates it against the schema of the adapter type and gives it a GUID.
2. You start the adapter on the host with the `cloud` method, your Organization ID and the GUID.
3. At startup the adapter fetches the record from LimaCharlie and starts the adapter type named by `sensor_type`, with that configuration.
4. Every minute the adapter asks LimaCharlie whether the record changed. When it has, the adapter stops the running collector and starts a new one with the new configuration. The logs show `conf update received`, `stopping previous adapter` and `starting new adapter`.

If LimaCharlie can't be reached during step 4, the adapter logs the error and keeps running with the configuration it already has. If it can't fetch the record during step 3, it exits with an error, so run it as a service that restarts on failure.

The adapter fetches its record from a public endpoint with the Organization ID and GUID only, without an API key. This is why the host needs nothing else to start, and why you should treat the GUID as a secret.

## Set up a cloud-managed adapter

You need the `externaladapter.get` and `externaladapter.set` permissions to create the record, and an [Installation Key](../installation-keys.md) for the adapter to enroll with.

### 1. Create the External Adapter record

The record holds the same configuration as an adapter configuration file, with one extra required field. `sensor_type` names the adapter type, and a block with the same name holds its configuration. For a syslog listener:

```yaml
sensor_type: syslog
syslog:
  port: 514
  is_udp: true
  iface: 0.0.0.0
  client_options:
    identity:
      oid: <ORG ID>
      installation_key: <INSTALLATION KEY>
    hostname: branch-office-fw
    platform: text
    sensor_seed_key: branch-office-fw
```

All the options of each adapter type are on its page under [Adapter Types](index.md#adapter-types), and the options shared by all types are in [Usage & Configuration](usage.md).

In the web app, open **Sensors > External Adapters**, click **Add External Adapter**, name the record and paste the YAML.

With the CLI:

```bash
limacharlie external-adapter set --key branch-office-fw --input-file branch-office-fw.yaml
```

`limacharlie external-adapter list-types` lists the adapter types you can use in a record, and `limacharlie external-adapter schema --type <type>` describes the options of one type.

LimaCharlie checks the record when you save it. A missing `sensor_type`, a misspelled option or a value the adapter type rejects fails the save with an error, instead of failing later on the host.

### 2. Get the record's GUID

The web app shows it as **Record GUID** on the right of the record. With the CLI, it is `sys_mtd.guid` in:

```bash
limacharlie external-adapter get --key branch-office-fw --output yaml
```

The GUID doesn't change when you edit the record. Deleting a record and creating it again under the same name gives it a new GUID, and adapters using the old one stop receiving changes.

### 3. Start the adapter on the host

Download the [adapter binary](deployment.md#adapter-binaries) for the host and start it with the `cloud` method:

```bash
./lc_adapter cloud conf_guid=<RECORD GUID> oid=<ORG ID>
```

With Docker, publish the ports your configuration listens on:

```bash
docker run -d --restart unless-stopped -p 514:514/udp refractionpoint/lc-adapter \
  cloud conf_guid=<RECORD GUID> oid=<ORG ID>
```

To keep it running across reboots, install it as a service with the same arguments, as described in [Adapters as a Service](as-a-service.md). On Windows:

```powershell
.\lc_adapter.exe -install:branch-office-fw cloud conf_guid=<RECORD GUID> oid=<ORG ID>
```

On Linux with systemd, use `cloud conf_guid=<RECORD GUID> oid=<ORG ID>` as the adapter arguments in `ExecStart`, and set `Restart=always`.

Because the configuration is not on the host, the same command deploys any adapter type. Only the GUID differs between hosts.

### 4. Check that it works

The adapter logs `starting adapter: <type>` and `watching for conf updates` once it has its configuration. It does not print the configuration, because the configuration can contain credentials. Add `show_config=true` to the command line to print it while you debug.

The adapter's sensor appears in the sensor list with its first event. `limacharlie external-adapter sensors --key branch-office-fw` lists the sensors an adapter created.

## Change the configuration

Edit the record in the web app, or run `limacharlie external-adapter set` again with the new YAML. The adapter applies the change within about a minute.

Keep `client_options.sensor_seed_key` and `client_options.hostname` the same when you edit, so events keep going to the same sensor. Changing the seed key creates a new sensor. See [Sensor IDs](usage.md#sensor-ids).

Restart the adapter process after you change `sensor_type` or remove an option from the record. A running adapter applies changes to the options of its type, but it doesn't switch to another type until it restarts.

## Move an existing adapter to cloud management

1. Take the adapter's current configuration file, or turn its command line into YAML. Each `a.b=c` argument is a nested `a: b: c` key under the block of the adapter type.
2. Add `sensor_type: <type>` at the top if the file doesn't have it, and save it as an External Adapter record.
3. Keep the same `sensor_seed_key` and `hostname`, so the adapter keeps reporting to its existing sensor.
4. Replace the adapter's arguments on the host with `cloud conf_guid=<RECORD GUID> oid=<ORG ID>` and restart it.
5. Delete the local configuration file, which may hold credentials.

## Manage many adapters

Create one record per adapter. Several hosts can use the same record if they should run the identical configuration, but each host then reports to the same sensor unless the configuration makes them differ, so a record per host or per site is usually clearer.

External Adapter records are Hive records, so they work with the tools you use for the rest of your organization's configuration:

- [Infrastructure as Code](../../5-integrations/extensions/limacharlie/infrastructure.md) and [Git Sync](../../5-integrations/extensions/limacharlie/git-sync.md) manage them under `hives: external_adapter:`. With the CLI, `limacharlie sync pull` and `limacharlie sync push` take `--hive-external-adapter`.
- Tags and comments on the record (`usr_mtd`) help you find adapters by customer, site or owner.
- The [permissions](../../8-reference/permissions.md#external-adapters) `externaladapter.get`, `externaladapter.set` and `externaladapter.del` control who can read, change and delete them.

Example Infrastructure as Code entry:

```yaml
hives:
  external_adapter:
    branch-office-fw:
      data:
        sensor_type: syslog
        syslog:
          port: 514
          is_udp: true
          client_options:
            identity:
              oid: <ORG ID>
              installation_key: <INSTALLATION KEY>
            hostname: branch-office-fw
            platform: text
            sensor_seed_key: branch-office-fw
      usr_mtd:
        enabled: true
        tags: [customer-a, firewall]
```

## Security

Anyone who has your Organization ID and a record's GUID can read that record, without logging in. That's what lets the adapter start with nothing else on the host. So:

- Treat the GUID like a password. Don't paste it in tickets or chat, and don't commit it to a repository.
- The record holds the full adapter configuration, including the installation key and any credentials the adapter type needs, such as API tokens. Anyone with `externaladapter.get` in the organization can read them too.
- `hive://secret/...` references are not resolved for External Adapters. Put the credential in the record itself.
- To rotate a GUID that leaked, create a new record with the same configuration, point the adapter at the new GUID and delete the old record. If the record held credentials, rotate them at the source as well.
- Don't add an `acl:` scope tag to an External Adapter record. The public endpoint refuses restricted records, and the adapter keeps its last configuration. See [Resource ACLs](../../7-administration/access/resource-acls.md).

## Stop or remove a cloud-managed adapter

Disabling or deleting the record does not stop an adapter that is already running. The adapter keeps its last configuration and logs an error each minute when the record is gone.

To stop collecting, stop or uninstall the adapter on the host (see [Service Uninstallation](as-a-service.md#service-uninstallation)), then delete the record.

## Limits

- A record can be up to 1 MB.
- The adapter checks for changes every minute.
- The host needs outbound HTTPS to `api.limacharlie.io` for the configuration, in addition to the usual [adapter connectivity](../../8-reference/faq/adapter-troubleshooting.md#network-access).

## Troubleshooting

See [An adapter in cloud mode does not pick up my changes](../../8-reference/faq/adapter-troubleshooting.md#an-adapter-in-cloud-mode-does-not-pick-up-my-changes) and the rest of [Adapter Troubleshooting](../../8-reference/faq/adapter-troubleshooting.md).
