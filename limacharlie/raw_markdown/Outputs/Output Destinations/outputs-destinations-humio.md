---
title: Humio
slug: outputs-destinations-humio
breadcrumb: Outputs > Output Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-humio
articleId: 64197276-a1b0-4d05-8007-29b213a4e2e9
---

* * *

Humio

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Humio

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

Output events and detections to the [Humio.com](https://humio.com) service.

  * `humio_repo`: the name of the humio repo to upload to.

  * `humio_api_token`: the humio ingestion token.

  * `endpoint_url`: optionally specify a custom endpoint URL, if you have Humio deployed on-prem use this to point to it, otherwise it defaults to the Humio cloud.




Example:
    
    
    humio_repo: sandbox
    humio_api_token: fdkoefj0erigjre8iANUDBFyfjfoerjfi9erge
    

Note: You may need to [create a new parser in Humio](https://docs.humio.com/docs/parsers/creating-a-parser/) to correctly [parse timestamps](https://docs.humio.com/reference/query-functions/functions/parsetimestamp/). You can use the following JSON parser:
    
    
    parseJson() | parseTimestamp(field=@timestamp,format="unixTimeMillis",timezone="Etc/UTC")
    

For the Community Edition of Humio, the `endpoint_url` is: `https://cloud.community.humio.com`.

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

  * [ OpenSearch ](/docs/outputs-destinations-opensearch) __



Tags

  * [ outputs ](/docs/en/tags/outputs)


