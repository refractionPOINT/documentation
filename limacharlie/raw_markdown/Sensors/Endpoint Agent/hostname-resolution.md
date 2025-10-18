---
title: Hostname Resolution
slug: hostname-resolution
breadcrumb: Sensors > Endpoint Agent
source: https://docs.limacharlie.io/docs/hostname-resolution
articleId: 0e5acae8-bc2b-4003-855e-3937a6b96974
---

* * *

Hostname Resolution

  *  __29 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Hostname Resolution

  *  __Updated on 29 Oct 2024
  *  __ 1 Minute to read 



  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




* * *

Article summary

 __

Did you find this summary helpful? __ __ __ __

__

Thank you for your feedback!

The Endpoint Agent reports its hostname to the LimaCharlie cloud where it shows up as the `hostname` field for the Sensor.

The resolution of that hostname is done in a few different ways:

  1. The main local interface is detected by looking for the route to `8.8.8.8`.

  2. A `getnameinfo()` with `NI_NAMEREQD` is performed to resolve the FQDN of the box.

  3. If the above hostname resolved is valid (no failure, and it is not equal to the static hostname of a few VPN and virtualization providers), this is the hostname we use.

  4. If the FQDN could not be resolved, the local hostname of the box is used.




This method allows the endpoint agent to better resolve its hostname in large environments where different regions re-use the same hostname.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

* * *

Was this article helpful?

__Yes __No

 __

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change  


Please enter a valid email

Cancel

* * *

###### What's Next

  * [ Detecting Sensors No Longer Sending Data ](/docs/non-responding-sensors) __


