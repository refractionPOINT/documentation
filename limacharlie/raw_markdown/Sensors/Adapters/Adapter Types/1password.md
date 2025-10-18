---
title: 1Password
slug: 1password
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/1password
articleId: 6b9bc0ba-8c26-4f14-b0db-ae686b8383e8
---

* * *

1Password

  *  __15 Aug 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# 1Password

  *  __Updated on 15 Aug 2025
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

[1Password](https://1password.com/) provides an events API to fetch audit logs. Events can be ingested directly via a cloud-to-cloud or CLI Adapter.

See 1Password's official API documentation [here](https://developer.1password.com/docs/events-api/reference/).

1Password telemetry can be addressed via the `1password` platform.

## Adapter Deployment

1Password events can be collected directly from the 1Password API, via a cloud-to-cloud Adapter, or via the CLI Adapter. 1Password adapters require the following options:

  * `token`: the API token provisioned through 1password.

  * `endpoint`: the API endpoint to use, depending on your 1password plan, see their documentation below.




You can generate an access token from 1Password at [this link](https://support.1password.com/events-reporting/).

## Cloud-to-Cloud Adapter

LimaCharlie offers a 1Password guided configuration in the web UI. From your 1Password instance, you will need:

  * 1Password API Access Token

  * Endpoint; one of the following:

    * 1Password.com (Business)

    * 1Password.com (Enterprise)

    * 1Password.ca

    * 1Password.eu




After providing an [Installation Key](/v2/docs/installation-keys), provide the required values and LimaCharlie will establish a Cloud Adapter for 1Password events

### Infrastructure as Code Deployment

LimaCharlie IaC Adapter can also be used to ingest Slack events.
    
    
    # 1Password Specific Docs: https://docs.limacharlie.io/docs/adapter-types-1password
    
    sensor_type: "1password"
      1password:
        token: "hive://secret/your-1password-api-token-secret"
        endpoint: "business"  # or "enterprise", "ca", "eu"
        client_options:
          identity:
            oid: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            installation_key: "YOUR_LC_INSTALLATION_KEY_1PASSWORD"
          hostname: "1password-audit-adapter"
          platform: "json"
          sensor_seed_key: "1password-sensor-unique-name"
    

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.

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

  * [ 1Password ](/docs/ext-cloud-cli-1password)
  * [ Cloud CLI ](/docs/ext-cloud-cli)



* * *

###### What's Next

  * [ Atlassian ](/docs/atlassian) __



Table of contents

    * Adapter Deployment 
    * Cloud-to-Cloud Adapter 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ sensors ](/docs/en/tags/sensors)


