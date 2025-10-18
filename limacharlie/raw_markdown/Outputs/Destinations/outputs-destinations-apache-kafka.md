---
title: Apache Kafka
slug: outputs-destinations-apache-kafka
breadcrumb: Outputs > Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-apache-kafka
articleId: 9ea649d6-690e-4694-9ba3-a102c324618c
---

* * *

Apache Kafka

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Apache Kafka

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

Output events and detections to a Kafka target.

  * `dest_host`: the IP or DNS and port to connect to, format `kafka.myorg.com`.

  * `is_tls`: if `true` will output over TCP/TLS.

  * `is_strict_tls`: if `true` will enforce validation of TLS certs.

  * `username`: if specified along with `password`, use for Basic authentication.

  * `password`: if specified along with `username`, use for Basic authentication.

  * `routing_topic`: use the element with this name from the `routing` of the event as the Kafka topic name.

  * `literal_topic`: use this specific value as a topic.




**Note on authentication:** if you specify `username` and `password`, the authentication mechanism assumed is SASL_SSL + SCRAM-SHA-512, which should be compatible with services like [AWS Manages Streaming Kafka](https://aws.amazon.com/msk/). If you require different paramaters around authentication please contact us at [support@limacharlie.io](mailto:support@limacharlie.io).

Example:
    
    
    dest_host: kafka.corp.com
    is_tls: "true"
    is_strict_tls: "true"
    username: lc
    password: letmein
    literal_topic: telemetry
    

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

  * [ Azure Event Hub ](/docs/outputs-destinations-azure-event-hub) __



Tags

  * [ outputs ](/docs/en/tags/outputs)


