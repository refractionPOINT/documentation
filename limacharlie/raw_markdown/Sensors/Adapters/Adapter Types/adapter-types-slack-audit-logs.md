---
title: Slack Audit Logs
slug: adapter-types-slack-audit-logs
breadcrumb: Sensors > Adapters > Adapter Types
source: https://docs.limacharlie.io/docs/adapter-types-slack-audit-logs
articleId: 1096e9e3-e09a-497e-88f8-c8c8a8929b99
---

* * *

Slack Audit Logs

  *  __25 Apr 2025
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Slack Audit Logs

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

[Slack audit logs](https://api.slack.com/admins/audit-logs) allow for ingestion of audit events in a Slack Enterprise Grid organization. Events can be ingested directly from the Slack API via a cloud-to-cloud or CLI Adapter.

Slack telemetry can be addressed via the `slack` platform.

**Note** : Audit Logs via API are only available to Slack workspaces on the Enterprise Grid plan.

## Adapter Deployment

Slack Audit Logs can be collected directly from the Slack API, via a cloud-to-cloud Adapter, or via the CLI Adapter. You will need a Slack App OAuth token prior to deploying this Adapter. More information on generating Slack OAuth tokens can be found [at this link](https://api.slack.com/authentication/token-types).

### Cloud-to-Cloud Adapter

Slack API telemetry can be configured directly from the LimaCharlie web application. Under `Sensors List`, select `+ Add Sensor > Slack Audit Logs`. After providing an Installation Key will be prompted to provide an Adapter Name and a Slack App OAuth Token.

### Deploying via the CLI Adapter

The LimaCharlie CLI Adapter can also be used to ingest Slack events, if you do not wish to create a cloud-to-cloud connector. The following sample configuration can be used to create a Slack CLI Adapter:
    
    
    slack:
      client_options:
        hostname: slack-audit
        identity:
          installation_key: <INSTALLATION_KEY>
          oid: <OID>
        platform: slack
        sensor_seed_key: super-special-seed-key
      token: <SLACK OAUTH TOKEN>
    

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. 

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

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

  * [ Slack ](/docs/outputs-destinations-slack)



* * *

###### What's Next

  * [ SentinelOne ](/docs/sentinelone) __



Table of contents

    * Adapter Deployment 



Tags

  * [ adapters ](/docs/en/tags/adapters)
  * [ sensors ](/docs/en/tags/sensors)


