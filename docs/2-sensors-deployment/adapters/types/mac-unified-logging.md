# Mac Unified Logging

## Overview

This Adapter lets you collect events from MacOS Unified Logging.

## Deployment Configurations

All adapters support the same `client_options`. Always specify these options if you use the binary adapter or create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself with LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, for example `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: an arbitrary name for this adapter. Sensor IDs (SID) are generated from this name, see below.

**Optional Arguments:**

- `predicate`: an [NSPredicate](https://developer.apple.com/documentation/foundation/nspredicate) filter string that limits which log entries the adapter collects. Example: `predicate='subsystem=="com.apple.TimeMachine"'`
- `write_timeout_sec`: number of seconds before a write to LimaCharlie times out (default: 600).

## CLI Deployment

[Adapter downloads](../deployment.md) are available on the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter mac_unified_logging client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=json \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME
```

### Configuration File Example

```yaml
mac_unified_logging:
  client_options:
    identity:
      oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
      installation_key: "YOUR_LC_INSTALLATION_KEY_MACOSUL"
    hostname: "user-macbook-pro"
    platform: "mac_unified_logging"
    sensor_seed_key: "macos-unified-logging-sensor"
  # Optional configuration
  write_timeout_sec: 600                           # Default: 600 seconds
  predicate: 'processImagePath endswith "/usr/sbin/sshd" OR subsystem == "com.apple.security"'
```

## Service Creation

To run this adapter as a service, run the script below. It adds a plist file to the endpoint **with your variables replaced**. This example also contains an example predicate. If you do not want to use a predicate, remove that line.

```bash
sudo -i

curl https://downloads.limacharlie.io/adapter/mac/64 -o /usr/local/bin/lc_adapter
chmod +x /usr/local/bin/lc_adapter

tee -a /Library/LaunchDaemons/io.limacharlie.adapter.macunifiedlogging.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>io.limacharlie.adapter.macunifiedlogging</string>
    <key>UserName</key>
 <string>root</string>
    <key>RunAtLoad</key>
    <true/>
    <key>WorkingDirectory</key>
    <string>/usr/local/bin</string>
    <key>KeepAlive</key>
    <true/>
    <key>EnvironmentVariables</key>
    <dict>
      <key>PATH</key>
      <string>/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin</string>
    </dict>
    <key>Program</key>
    <string>/usr/local/bin/lc_adapter</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/lc_adapter</string>
        <string>mac_unified_logging</string>
        <string>client_options.identity.installation_key=$INSTALLATION_KEY</string>
        <string>client_options.identity.oid=$OID</string>
        <string>client_options.hostname=$SENSOR_NAME</string>
        <string>client_options.platform=json</string>
        <string>client_options.sensor_seed_key=$SENSOR_NAME</string>
        <string>predicate=eventMessage CONTAINS[c] "corp.sap.privileges"</string>
    </array>
  </dict>
</plist>
EOF

launchctl load -w /Library/LaunchDaemons/io.limacharlie.adapter.macunifiedlogging.plist
```
