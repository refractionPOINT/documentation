---
title: Duo
slug: adapter-types-duo
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-duo
articleId: 529583d1-d0a0-418c-b50c-ea4b4dab7ea7
---

* * *

Duo

  *  __16 Jul 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Duo

  *  __Updated on 16 Jul 2025
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

This Adapter allows you to connect to the Duo Admin API and fetch logs from it.

## Configurations

Adapter Type: `duo`

  * `client_options`: common configuration for adapter as defined [here](/v2/docs/adapters#usage).

  * `integration_key`: an integration key created from within Duo that associated with your "app".

  * `secret_key`: the secret key for your "app".

  * `api_hostname`: the DNS for your "app", a value given to you by Duo.




### Infrastructure as Code Deployment
    
    
    # Duo Security Specific Docs: https://docs.limacharlie.io/docs/adapter-types-duo
    
    # For cloud sensor deployment, store credentials as hive secrets:
    #   integration_key: "hive://secret/duo-integration-key"
    #   secret_key: "hive://secret/duo-secret-key"
    
    sensor_type: "duo"
      duo:
        integration_key: "YOUR_DUO_INTEGRATION_KEY_DIXXXXXXXXXXXXXXXXXX"
        secret_key: "YOUR_DUO_SECRET_KEY_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        api_hostname: "api-xxxxxxxx.duosecurity.com"
        client_options:
          identity:
            oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            installation_key: "YOUR_LC_INSTALLATION_KEY_DUO"
          hostname: "duo-security-adapter"
          platform: "duo"
          sensor_seed_key: "duo-sensor-prod"

## API Doc

See the [official documentation](https://duo.com/docs/adminapi).

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

###### What's Next

  * [ EVTX ](/docs/adapter-types-evtx) __



Table of contents

    * Overview 
    * Configurations 
    * API Doc 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ sensors ](/docs/en/tags/sensors)


