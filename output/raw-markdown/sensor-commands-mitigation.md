[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v1

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Telemetry](telemetry-sensors)
* [Detection and Response](detecting-related-events)
* [Platform Management](platform-configuration-limacharlie-sdk)
* [Outputs](output-whitelisting)
* [Add-Ons](developer-grant-program)
* [FAQ](faq-privacy)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Mitigation

* 08 Feb 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

This documentation version is deprecated, please click here for the latest version.

# Mitigation

* Updated on 08 Feb 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

The following sensor commands perform mitigation actions against EDR sensors.

## deny\_tree

Tells the sensor that all activity starting at a specific process (and its children) should be denied and killed. This particular command is excellent for ransomware mitigation.

**Platforms:**

**Usage:**

```
usage: deny_tree [-h] atom [atom ...]

positional arguments:
  atom        atoms to deny from
```

## rejoin\_network

Tells the sensor to allow network connectivity again (after it was segregated).

**Platforms:**

**Return Event:**
 [REJOIN\_NETWORK](/v1/docs/reference-events-responses-mitigation#REJOIN_NETWORK)

**Usage:**

```
usage: rejoin_network [-h]
```

## segregate\_network

Tells the sensor to stop all network connectivity on the host except LC comms to the backend. So it's network isolation, great to stop lateral movement.

Note that you should never upgrade a sensor version while the network is isolated through this mechanism. Doing so may result in the agent not regaining connectivity to the cloud, requiring a reboot to undo.

This command primitive is NOT persistent, meaning a sensor you segregate from the network using this command alone, upon reboot will rejoin the network. To achieve isolation from the network in a persistent way, see the `isolate network` and `rejoin network` [Detection & Response rule actions](/v1/docs/detection-and-response).

**Platforms:**

**Return Event:**
 [SEGREGATE\_NETWORK](/v1/docs/reference-events-responses-mitigation#SEGREGATE_NETWORK)

**Usage:**

```
usage: segregate_network [-h]
```

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

* [Network](/v1/docs/sensor-commands-network)

Table of contents

+ [deny\_tree](#deny_tree)
+ [rejoin\_network](#rejoin_network)
+ [segregate\_network](#segregate_network)
