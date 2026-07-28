# FAQ - Sensor Removal

## How do I verify the LimaCharlie agent was uninstalled from macOS systems?

After you [uninstall the LimaCharlie Sensor for macOS](../../2-sensors-deployment/endpoint-agent/macos/installation.md#uninstallation-flow), check the items below on the endpoint manually. These checks show that the uninstallation was successful.

## Verify the LimaCharlie processes are not running

1. Open Activity Monitor (`/Applications/Utilities/Activity Monitor.app`).
2. In the View menu, select "All Processes".
3. In the Search box, type: `rphcp`
4. Make sure that these two processes do not appear:

    `rphcp`

    `com.refractionpoint.rphcp.extension`

If one of the two processes appears, the uninstallation was not successful. Do the uninstallation again.

## Verify all files on disk were removed

These files of the LimaCharlie sensor must not be on disk:

/Applications/RPHCP.app

/usr/local/bin/rphcp

/usr/local/hcp

/usr/local/hcp_conf

/usr/local/hcp_hbs

You can also remove the log file at: /usr/local/hcp.log

## Verify LimaCharlie Network Extension was removed

1. Open System Settings
2. Go to Network
3. Select VPN & Filters
4. Check if "RPHCP" appears in the list.

✅ If it does not appear, the Network Extension was removed.

❌ If RPHCP appears in the list, the Network Extension was not removed. Do the uninstallation again.

## Verify LimaCharlie Security Extension was removed

Open the Terminal and run the commands below.

### Run Command #1

`sudo systemextensionsctl list | grep rphcp`

✅ No result shows that the uninstall was successful.

❌ This result shows that the uninstall was not successful:

```text
* * N7N82884NH com.refractionpoint.rphcp.extension (1.0.241204/1.0.241204) RPHCP [activated enabled]
```

### Run Command #2

`sudo cat /Library/SystemExtensions/db.plist | grep rphcp`

✅ If there is no result, the security extension was removed.

❌ If you see a similar result, the extension was not removed. More steps are then necessary to remove it, for example a manual removal after you start the host in Recovery mode.
