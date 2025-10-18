---
title: Slack
slug: outputs-destinations-slack
breadcrumb: Outputs > Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-slack
articleId: b4425f73-126c-43ec-9594-7b7426222be5
---

* * *

Slack

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Slack

  *  __Updated on 05 Oct 2024
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

Output detections and audit (only) to a Slack community and channel.

  * `slack_api_token`: the Slack provided API token used to authenticate.

  * `slack_channel`: the channel to output to within the community.




Example:
    
    
    slack_api_token: sample_api_token
    slack_channel: #detections
    

**Provisioning:**

To use this Output, you need to create a Slack App and Bot. This is very simple:

  1. Head over to https://api.slack.com/apps

  2. Click on "Create App" and select the workspace where it should go

  3. From the sidebar, click on OAuth & Permissions

  4. Go to the section "Bot Token Scope" and click "Add an OAuth Scope"

  5. Select the scope `chat:write`

  6. From the sidebar, click "Install App" and then "Install to Workspace"

  7. Copy token shown, this is the `slack_api_token` you need in LimaCharlie

  8. In your Slack workspace, go to the channel you want to receive messages in, and type the slash command: `/invite @limacharlie` (assuming the app name is `limacharlie`)




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

  * [ Slack Audit Logs ](/docs/adapter-types-slack-audit-logs)



* * *

###### What's Next

  * [ SMTP ](/docs/outputs-destinations-smtp) __



Tags

  * [ outputs ](/docs/en/tags/outputs)


