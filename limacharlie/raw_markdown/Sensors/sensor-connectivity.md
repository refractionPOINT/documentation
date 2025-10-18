---
title: Sensor Connectivity
slug: sensor-connectivity
breadcrumb: Sensors
source: https://docs.limacharlie.io/docs/sensor-connectivity
articleId: b46bb3f6-d6b5-4647-929c-4b372b26eb49
---

* * *

Sensor Connectivity

  *  __25 Apr 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Sensor Connectivity

  *  __Updated on 25 Apr 2025
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

The network connection required by the LimaCharlie Sensor is very simple. It requires a single TCP connection over port 443 to a specific domain, and optionally another destination for the [Artifact Collection](/v2/docs/artifacts) service.

The specific domains are listed in the Sensor Downloads section of your Organization's dashboard. They will vary depending on the datacenter you chose to create your organization in. To find yours, see the screenshots below.

  1. ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image\(312\).png)

  2. ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image\(313\).png)




Currently, web proxies are not supported, but since LimaCharlie requires a single connection to a single dedicated domain, it makes creating a single exception safe and easy.

## Proxy Tunneling

The LimaCharlie sensor supports unauthenticated proxy tunneling through [HTTP CONNECT](https://en.wikipedia.org/wiki/HTTP_tunnel).

This allows the LimaCharlie connection to go through the proxy in an opaque way (since the sensor does not support SSL interception).

To activate this feature, set the `LC_PROXY` environment variable to the DNS or hostname of the proxy to use. For example you could use: `LC_PROXY=proxy.corp.com:8080`.

### Windows

On Windows, you may use a light auto-detection of a globally-configured, unauthenticated proxy.

To enable this, set the same environment variable to the `-` value, like `LC_PROXY=-`. This will make the sensor query the registry key `HKLM\Software\Policies\Microsoft\Windows\CurrentVersion\Internet Settings\ProxyServer` and use its value as the proxy destination.

Also on Windows, in some cases the environment variable changes do not propagate to all processes in the expected way. Usually a reboot of the machine will fix it, but for machines that cannot be rebooted you have the ability to set a special value to the environment variable (deletion is usually problematic but setting a var works) that will disable the proxy specifically: `!`. So if you set the `LC_PROXY` variable to `!` (exclamation mark), the proxy will be disabled.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

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

###### Related articles

  * [ Endpoint Agent ](/docs/endpoint-agent)
  * [ macOS Agent Installation via Jamf Now ](/docs/installing-macos-agents-via-jamf-now)
  * [ Chrome Agent Installation ](/docs/chrome-agent-installation)
  * [ Windows Agent Installation ](/docs/windows-agent-installation)
  * [ Linux Agent Installation ](/docs/linux-agent-installation)
  * [ Endpoint Agent Installation ](/docs/endpoint-agent-installation)
  * [ Edge Agent Installation ](/docs/edge-agent-installation)
  * [ macOS Agent Installation - Older Versions (macOS 10.15 Catalina to macOS 14 Sonoma) ](/docs/macos-agent-installation-latest-os-versions)
  * [ macOS Agent Installation - Older Versions (macOS 10.14 and prior) ](/docs/macos-agent-installation-older-versions)
  * [ Docker Agent Installation ](/docs/docker-agent-installation)
  * [ macOS Agent Installation ](/docs/macos-agent-installation)



* * *

###### What's Next

  * [ Endpoint Agent ](/docs/endpoint-agent) __



Table of contents

    * Proxy Tunneling 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ endpoint agent ](/docs/en/tags/endpoint%20agent)
  * [ sensors ](/docs/en/tags/sensors)


