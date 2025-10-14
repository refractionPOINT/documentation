# Ingesting Linux Audit Logs

One data source of common interest on Linux systems is the `audit.log` file. By default, this file stores entries from the Audit system, which contains information about logins, privilege escalations, and other account-related events. You can find more information about Audit Log files [here](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/security_guide/sec-understanding_audit_log_files).

There are a few techniques to ingest Linux Audit logs into LimaCharlie:

1. Pull the raw logs using Artifacts and/or the File System navigator *(EDR sensors only)*
2. Collect the files using **Artifact Collection.**
3. Stream the raw audit log via a `file` adapter.

We will explore these techniques in this tutorial. Adapters can also be configured as syslog listeners; that will be covered in another tutorial.

## File System Browser

Our Windows, Linux, and macOS EDR sensors offer file system navigation capabilities. If you need a single, ad-hoc collection of the `auth.log`, you can use the File System capability to navigate to `/var/log`, and download `auth.log`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/audit-1.png)

## Artifact Collection

If you don't need to stream Linux Audit log(s), but instead want to maintain a copy of them for posterity, Artifact collection would be your best method. This is an automated collection technique, but won't stream the events to your **Timeline**.

**Step 1:** Within the Navigation Pane, select `Artifact Collection`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/audit-2.png)

**Step 2:** Create a simple artifact collection rule for `/var/log/auth.log`. In this example, we chose a retention period of 30 days; however, you should choose the correct retention period for your use case.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/audit-3.png)

click **Save**

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/audit-4.png)

**Step 3:** Saving the artifact rule will then populate to the appropriate sensor(s), and you should see the `auth.log` in the Artifacts menu, once it is collected by the Sensor.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/audit-5(1).png)

> **Want more logs?**
> 
> Want more than just the most recent `auth.log`? Specify a regular expression to capture all archived copies of the log files. However, be careful on retention and make sure you're not unnecessarily duplicating data!

## File Adapter Ingestion

It is also possible to deploy a LimaCharlie [Adapter](../concepts/adapters.md) pointed to `auth.log` to collect and stream the events in directly. Note that Adapters will create a separate telemetry "stream" - thus, it is recommended to combine file types where possible.

**Step 1:** Create an Installation Key for your adapter and download the appropriate binary.

**Step 2:** On the system(s) to collect logs from, deploy the adapter. We recommend utilizing a configuration file for adapter testing, to allow for tracking of changes. The following is a sample file that will ingest `auth.log` events as basic text.

```
file:
  client_options:
    identity:
      installation_key: <installation_key>
      oid: <oid>
    platform: text
    sensor_seed_key: audit-log-events
  file_path: /var/log/auth.log
  no_follow: false
```

More details on configuration files and adapter usage can be found [here](../reference/adapter-usage.md).

**Step 3:** Run the adapter, providing the `file` option and the appropriate config file.

`$ ./lc_adapter file /tmp/config.yml`

The adapter should load the config and display options to the terminal.

*Note: This is not a persistent install; utilize your operating system's init/systemctl capabilities to create a persistent adapter*

**Step 4:** Returning to the LimaCharlie web UI, you should start to see events flowing in almost instantaneously.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28115%29.png)

Note that a `text` platform will ingest data as basic text, however you could use formatting options to parse the fields respective to your `auth.log` format.