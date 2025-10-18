---
title: Integrity
slug: ext-integrity
breadcrumb: Add-Ons > Extensions > LimaCharlie Extensions
source: https://docs.limacharlie.io/docs/ext-integrity
articleId: 6a95d0b2-944e-401e-9210-6ea09f9ff144
---

* * *

Integrity

  *  __10 Oct 2025
  *  __ 3 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Integrity

  *  __Updated on 10 Oct 2025
  *  __ 3 Minutes to read 



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

The Integrity Extension helps you manage all aspects of file or registry integrity monitoring (FIM and RIM, respectively). This extension automates integrity checks of file system and registry values through pattern-based rules.

## Enabling the Integrity Extension

To enable the Integrity extension, navigate to the [Integrity extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-integrity) in the marketplace. Select the Organization you wish to enable the extension for, and select **Subscribe**.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/integrity-1\(1\).png)

After clicking **Subscribe** , the Infrastructure extension should be available almost immediately.

## Using the Integrity Extension

Once enabled, you will see an **File/Reg Integrity** option under **Automation** within the LimaCharlie web UI.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/integrity-2.png)

Selecting this option allows you to customize **File & Registry Integrity Monitoring** rules, as seen in the screenshot below.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/integrity-3.png)

Selecting **Add Monitoring Rule** will allow you to create a FIM or RIM rule, specifying a platform, Tag(s), and pattern(s).

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/integrity-4.png)

### Rule Patterns

Patterns are file or registry patterns and support wildcards (*, ?, +). Windows directory separators (backslash, `”\”`) must be escape with a double-slash `”\\”`.

When a FIM or RIM rule is tripped, you will see a `FIM_HIT` event in the Sensor(s) timeline.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/integrity-5.png)

### Example Rule Patterns

#### Windows **File Monitoring**

**Monitor a specific directory on all drives**| **Monitor a specific file on a specific drive**  
---|---  
?:\\\Windows\\\System32\\\drivers| C:\\\Windows\\\System32\\\specialfile.exe  
?:\\\inetpub\\\wwwroot|   
  
#### Windows Registry Monitoring

> All registry monitoring patterns MUST begin with **\\\REGISTRY** , followed by the hive and then the path or value to monitor.

Monitor for changes to system Run and RunOnce| Monitor all users for additions to a user’s Run  
---|---  
\\\REGISTRY\\\MACHINE\\\Software\\\Microsoft\\\Windows\\\CurrentVersion\\\Run*| \\\REGISTRY\\\USER\S-*\\\Software\\\Microsoft\\\Windows\\\CurrentVersion\\\Run*  
\\\REGISTRY\\\MACHINE\\\Software\\\Microsoft\\\Windows\\\CurrentVersion\\\RunOnce*|   
  
#### Linux

**Monitor for changes to root’s authorized_keys**| **Monitor for changes to all user private ssh directories**  
---|---  
/root/.ssh/authorized_keys| /home/*/.ssh/*  
  
#### macOS

Monitor for changes to user keychains| Monitor for changes to system keychains  
---|---  
/Users/*/Library/Keychains/*| /Library/Keychains  
  
### Linux Support

FIM is supported on Linux systems, however, support may vary based on Linux distribution and software.

#### Linux with eBPF Support

Linux hosts capable of running with [eBPF](https://ebpf.io/) have file notification and FIM capabilities on par with Windows and macOS.

#### Legacy Support

FIM is partially supported on systems without eBPF. Specified file expressions are actively monitored via `inotify` (as opposed to macOS and Windows, which utilize passive kernel monitoring). Due to [inotify](https://man7.org/linux/man-pages/man7/inotify.7.html) limitations, paths with wildcards are less efficient and only support monitoring up to 20 sub-directories covered by the wildcard. In addition to this, the path expressions should specify a final wildcard of _when all files under a directory need to be monitored. Omitting the final_`*` will result in only the top-level directory being monitoring.

## Actions via REST API

The following REST API actions can be sent to interact with the Integrity extension:

**List Rules**
    
    
    {
      "action": "list_rules"
    }

**Add Rule**
    
    
    {
      "action": "add_rule",
      "name": "linux-root-ssh-configs",
      "patterns": [
        "/root/.ssh/*"
      ],
      "tags": [
        "vip",
        "workstation"
      ],
      "platforms": [
        "linux"
      ]
    }

**Remove Rule**
    
    
    {
      "action": "remove_rule",
      "name": "linux-ssh-configs"
    }

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Tags in LimaCharlie are strings linked to sensors for classifying endpoints, automating detection and response, and triggering workflows. Tags appear in every event under the `routing` component and help simplify rule writing. Tags can be added manually, via API, or through detection & response rules. System tags like `lc:latest`, `lc:stable`, and `lc:debug` offer special functionality. Tags can be checked, added, or removed through the API or web app, streamlining device management.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

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

  * [ Reference: Endpoint Agent Commands ](/docs/reference-endpoint-agent-commands)
  * [ Detection and Response Examples ](/docs/detection-and-response-examples)



* * *

###### What's Next

  * [ Lookup Manager ](/docs/ext-lookup-manager) __



Table of contents

    * Enabling the Integrity Extension 
    * Using the Integrity Extension 
    * Actions via REST API 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)


