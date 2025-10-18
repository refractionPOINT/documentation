---
title: Elastic
slug: outputs-destinations-elastic
breadcrumb: Outputs > Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-elastic
articleId: a0bb76e6-4a7e-44a3-b3a9-b731b845130e
---

* * *

Elastic

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Elastic

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

Output events and detections to [Elastic](https://www.elastic.co/).

  * `addresses`: the IPs or DNS where to send the data to.

  * `index`: the index name to send data to.

  * `username`: user name if using username/password auth. (use either username/password -or- API key)

  * `password`: password if using username/password auth.

  * `cloud_id`: Cloud ID from Elastic.

  * `api_key`: API key; if using it for auth. (use either username/password -or- API key)




Example:
    
    
    addresses: 11.10.10.11,11.10.11.11
    username: some
    password: pass1234
    index: limacharlie
    

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

  * [ OpenSearch ](/docs/outputs-destinations-opensearch)



* * *

###### What's Next

  * [ Google Cloud BigQuery ](/docs/outputs-destinations-google-cloud-bigquery) __



Tags

  * [ outputs ](/docs/en/tags/outputs)


