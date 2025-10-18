---
title: Mac Unified Logging
slug: adapter-types-mac-unified-logging
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-mac-unified-logging
articleId: 3b292e09-6f4c-4578-a85a-d613cfb75881
---

* * *

Mac Unified Logging

  *  __16 Jul 2025
  *  __ 2 Minutes to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Mac Unified Logging

  *  __Updated on 16 Jul 2025
  *  __ 2 Minutes to read 



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

This Adapter allows you to collect events from MacOS Unified Logging.

## Deployment Configurations

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

  * `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
  * `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
  * `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
  * `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.



**Optional Arguments:**

  * `predicate`: example, `predicate='subsystem=="com.apple.TimeMachine"'`




## CLI Deployment

Adapter downloads can be found [here](/v2/docs/adapter-deployment).
    
    
    chmod +x /path/to/lc_adapter
    
    /path/to/lc_adapter mac_unified_logging client_options.identity.installation_key=$INSTALLATION_KEY \
    client_options.identity.oid=$OID \
    client_options.platform=json \
    client_options.sensor_seed_key=$SENSOR_NAME \
    client_options.hostname=$SENSOR_NAME
    

### Infrastructure as Code Deployment
    
    
    # macOS Unified Logging Specific Docs: https://docs.limacharlie.io/docs/adapter-types-macos-unified-logging
    
    sensor_type: "mac_unified_logging"
      mac_unified_logging:
        client_options:
          identity:
            oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            installation_key: "YOUR_LC_INSTALLATION_KEY_MACOSUL"
          hostname: "user-macbook-pro"
          platform: "mac_unified_logging"
          sensor_seed_key: "macos-unified-logging-sensor"
        # Optional configuration
        write_timeout_sec: 600                           # Default: 600 seconds
        predicate: 'processImagePath endswith "/usr/sbin/sshd" OR subsystem == "com.apple.security"'

## Service Creation

If you want this adapter to run as a service, you can run the following script to add a plist file to the endpoint **with your variables replaced**. Please note that this example also has an example predicate, so if you do not wish to use a predicate, remove that line.
    
    
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
    

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

Command-line Interface

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

  * [ macOS Agent Installation ](/docs/macos-agent-installation)
  * [ Ingesting MacOS Unified Logs ](/docs/ingesting-macos-unified-logs)
  * [ macOS Agent Installation via Jamf Now ](/docs/installing-macos-agents-via-jamf-now)
  * [ macOS Agent Installation - Older Versions (macOS 10.15 Catalina to macOS 14 Sonoma) ](/docs/macos-agent-installation-latest-os-versions)
  * [ macOS Agent Installation - Older Versions (macOS 10.14 and prior) ](/docs/macos-agent-installation-older-versions)



* * *

###### What's Next

  * [ Microsoft Defender ](/docs/adapter-types-microsoft-defender) __



Table of contents

    * Overview 
    * Deployment Configurations 
    * {{glossary.CLI}} Deployment 
    * Service Creation 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ macos ](/docs/en/tags/macos)
  * [ sensors ](/docs/en/tags/sensors)


