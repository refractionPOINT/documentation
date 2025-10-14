[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v2

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

FAQ - Sensor Removal

* 26 Aug 2025
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# FAQ - Sensor Removal

* Updated on 26 Aug 2025
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

## How do I verify the LimaCharlie agent was uninstalled from macOS systems?

After [performing an uninstallation](https://docs.limacharlie.io/docs/macos-agent-installation-latest-os-versions#uninstallation-flow) of the LimaCharlie Sensor for macOS, you can verify that the process was successful by manually checking several items on the endpoint, as described below.

## Verify the LimaCharlie processes are not running

1. Open Activity Monitor (`/Applications/Utilities/Activity Monitor.app`).
2. From the View menu, ensure "All Processes" is selected.
3. In the Search box, type: `rphcp`
4. Ensure that neither of the following processes appear:

`rphcp`

`com.refractionpoint.rphcp.extension`

If either appear, the uninstallation likely did not complete successfully and it should be re-attempted.

## Verify all files on disk were removed

The following LimaCharlie sensor-related files should no longer exist on disk:

/Applications/RPHCP.app

/usr/local/bin/rphcp

/usr/local/hcp

/usr/local/hcp\_conf

/usr/local/hcp\_hbs

You may optionally remove the log file located at: /usr/local/hcp.log

## Verify LimaCharlie Network Extension was removed

1. Open System Settings
2. Navigate to Network
3. Select VPN & Filters
4. Check if. “RPHCP” appears in the list.

✅ If it does not appear, the Network Extension was successfully removed.

❌ If you see RPHCP in the list, the Network Extension was not properly removed and you should perform uninstallation again.

## Verify LimaCharlie Security Extension was removed

Open the Terminal and run the following commands

**Run Command #1**

`sudo systemextensionsctl list | grep rphcp`

✅ No result would indicate that the uninstall was successful.

❌ The following result would indicate that the uninstall was not successful:

```
*	*	N7N82884NH	com.refractionpoint.rphcp.extension (1.0.241204/1.0.241204)	RPHCP	[activated enabled]
```

**Run Command #2**

`sudo cat /Library/SystemExtensions/db.plist | grep rphcp`

✅ If no result is returned, the security extension was successfully removed.

❌ If instead you see something similar to the below, the extension was not properly removed and you may need to take some additional measures to do so (i.e. manual removal after booting into Recovery mode).

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### What's Next

* [FAQ - Sensor Troubleshooting](/docs/faq-troubleshooting)

Table of contents

+ [How do I verify the LimaCharlie agent was uninstalled from macOS systems?](#how-do-i-verify-the-limacharlie-agent-was-uninstalled-from-macos-systems-)
+ [Verify the LimaCharlie processes are not running](#verify-the-limacharlie-processes-are-not-running)
+ [Verify all files on disk were removed](#verify-all-files-on-disk-were-removed)
+ [Verify LimaCharlie Network Extension was removed](#verify-limacharlie-network-extension-was-removed)
+ [Verify LimaCharlie Security Extension was removed](#verify-limacharlie-security-extension-was-removed)
