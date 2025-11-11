# Updating Sensors to the Newest Version

LimaCharlie releases a new version of the Sensor frequently - often every few weeks. However, we give you full control over what sensor version is running in your Organization. Sensors are not updated by default.

There are two methods for updating sensors in your organization to the latest version.

## Manual Update

Upgrading sensors is done transparently for you once you click the "Update to Latest" button, located at `Sensors > Deployed Versions`.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(316).png)

The new version should be in effect across the organization within about 20 minutes.

## Automated Update

You can also configure sensors in your organization to auto-update to the new version when it's released. To do it, tag applicable (or all) sensors in your fleet with the `lc:stable` tag (`lc:stable` tag means that the package it provides rarely changes).

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(315).png)

This will ensure that when a new sensor version is released, it will be in effect across the organization within about 20 minutes.
