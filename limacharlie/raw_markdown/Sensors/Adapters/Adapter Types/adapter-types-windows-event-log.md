---
title: Windows Event Log
slug: adapter-types-windows-event-log
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-windows-event-log
articleId: 62ab9efe-3ad1-4f99-9229-1a70dbce1257
---

* * *

Windows Event Log

  *  __30 Jul 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Windows Event Log

  *  __Updated on 30 Jul 2025
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

## Overview

This Adapter allows you to connect to the local Windows Event Logs API on Windows. This means this Adapter is only available from Windows builds and only works locally (will not connect to remote Windows instances).

## Configurations

Adapter Type: `wel`

  * `client_options`: common configuration for adapter as defined [here](/v2/docs/adapters#usage).

  * `evt_sources`: a comma separated list of elements in the format `SOURCE:FILTER`, where `SOURCE` is an Event Source name like `Application`, `System` or `Security` and `FILTER` is an `XPath` filter value as described in the documentation linked below.




### Infrastructure as Code Deployment
    
    
    # Windows Event Log (WEL) Specific Docs: https://docs.limacharlie.io/docs/adapter-types-windows-event-log
    
    # Basic Event Sources:
    # evt_sources: "Security,System,Application"
    
    # With XPath Filters:
    # evt_sources: "Security:'*[System[(Level=1 or Level=2 or Level=3)]]',System:'*[System[Provider[@Name=\"Microsoft-Windows-Kernel-General\"]]]'"
    
    # File-Based Sources:
    # evt_sources: "C:\\Windows\\System32\\winevt\\Logs\\Security.evtx:'*[System[(EventID=4624)]]'"
    
      wel:
        evt_sources: "Security:'*[System[(Level=1 or Level=2 or Level=3)]]',System,Application"
        client_options:
          identity:
            oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            installation_key: "YOUR_LC_INSTALLATION_KEY_WEL"
          hostname: "prod-dc01.example.local"
          platform: "windows"
          sensor_seed_key: "wel-collector"
        write_timeout_sec: 30
    

### XPath Filter Examples

Security Events (High Priority):
    
    
      Security:'*[System[(Level=1 or Level=2 or Level=3)]]'

Logon Events Only:
    
    
      Security:'*[System[(EventID=4624 or EventID=4625 or EventID=4634)]]'

System Errors:
    
    
      System:'*[System[(Level=1 or Level=2)]]'

Specific Provider:
    
    
      Application:'*[System[Provider[@Name="Microsoft-Windows-ApplicationError"]]]'

## API Doc

See the [official documentation](https://learn.microsoft.com/en-us/windows/win32/wes/consuming-events).

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

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

  * [ Windows Event Logs ](/docs/adapter-examples-windows-event-logs)
  * [ Ingesting Windows Event Logs ](/docs/ingesting-windows-event-logs)
  * [ Hayabusa ](/docs/ext-hayabusa)



* * *

###### What's Next

  * [ Zendesk ](/docs/adapter-types-zendesk) __



Table of contents

    * Overview 
    * Configurations 
    * API Doc 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ sensors ](/docs/en/tags/sensors)
  * [ windows ](/docs/en/tags/windows)


