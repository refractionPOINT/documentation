# Updating Sensors to the Newest Version

LimaCharlie releases a new version of the Sensor frequently - often every few weeks. You control which sensor version runs in your Organization. Sensors do not update by default.

There are two methods to update the sensors in your organization to the latest version.

## Manual Update

Click the "Update to Latest" button at `Sensors > Deployed Versions`. LimaCharlie then upgrades the sensors for you.

![Manual sensor update via the Update to Latest button](../../assets/images/image(316).png)

The new version is in effect across the organization in about 20 minutes.

## Automated Update

You can also configure the sensors in your organization to auto-update when LimaCharlie releases a new version. Tag some or all of the sensors in your fleet with the `lc:stable` tag. The `lc:stable` tag means that the package that it supplies rarely changes.

![Automated sensor update settings](../../assets/images/image(315).png)

When LimaCharlie releases a new sensor version, it is in effect across the organization in about 20 minutes.
