# Adapters as a Service

Sometimes you must install the LimaCharlie Adapter with persistence. Persistence keeps data collection active after a reboot or another disruption.

You can install the LimaCharlie adapter as a service.

## Service Installation

### Windows

To install the Windows LimaCharlie adapter as a service, use the `-install:<service_name>` flag. Put the flag after the name of the adapter executable.

For example, replace this command:

`./lc_adapter.exe azure_event_hub client_options.identity.installation_key=...`

with this command:

`./lc_adapter.exe -install:azure_collection azure_event_hub client_options.identity.installation_key=...`

The second command creates a service named `azure_collection` with the adapter config.

You can give adapter configurations in two ways:

- In the command line, as a list of flags
- In a YAML config file

**Note:** The service points to `lc_adapter.exe` at the path that the file has when you create the service. Move the adapter to its permanent location before you create the service.

### Linux / systemd

On a Linux system with systemd, you need a service file, the adapter binary, and your adapter command.

#### Adapter Binary

Download one of the [adapter binaries](deployment.md). Then set the necessary permissions:

```bash
wget -O /path/to/adapter-directory/lc-adapter $ADAPTER_BINARY_URL
chmod +x /path/to/adapter-directory/lc-adapter
```

#### Service File - /etc/systemd/system/limacharlie-adapter-name.service

In the service file, replace `$ADAPTER_COMMAND` with your own adapter command.

```bash
[Unit]
Description=LC Adapter Name
After=network.target

[Service]
Type=simple
ExecStart=$ADAPTER_COMMAND
WorkingDirectory=/path/to/adapter-directory
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=lc-adapter-name

[Install]
WantedBy=multi-user.target
```

#### Adapter Command

Your adapter command changes with your use case. This example uses a [file](types/file.md) adapter to ingest logs from a JSON file.

```bash
/path/to/adapter-directory/lc-adapter file file_path=/path/to/logs.json client_options.identity.installation_key=<INSTALLATION KEY> client_options.identity.oid=<ORG ID> client_options.platform=json client_options.sensor_seed_key=<SENSOR SEED KEY> client_options.mapping.event_type_path=<EVENT TYPE FIELD> client_options.hostname=<HOSTNAME>
```

#### Enable and Start the Service

```bash
sudo systemctl enable lc-adapter-name
sudo systemctl start lc-adapter-name
sudo systemctl status lc-adapter-name
```

## Service Uninstallation

### Windows

To remove a Windows LimaCharlie Adapter service, use the `-remove:<service_name>` flag.

### Linux

If a systemd script runs your service, disable and remove it with these commands:

```bash
sudo systemctl stop lc-adapter-name
sudo systemctl disable lc-adapter-name
sudo rm /etc/systemd/system/lc-adapter-name.service
sudo rm /path/to/adapter-directory/lc-adapter
```
