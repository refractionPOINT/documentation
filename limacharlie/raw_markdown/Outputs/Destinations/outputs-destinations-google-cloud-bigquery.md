---
title: Google Cloud BigQuery
slug: outputs-destinations-google-cloud-bigquery
breadcrumb: Outputs > Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-google-cloud-bigquery
articleId: a7c8cd6a-5f3b-4af5-9b29-c00a2c6e4a3e
---

* * *

Google Cloud BigQuery

  *  __10 Dec 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Google Cloud BigQuery

  *  __Updated on 10 Dec 2024
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

Output events and detections to a Google Cloud BigQuery Table.

For a practical use case of this output, see this [tutorial on pushing Velociraptor data to BigQuery](/v2/docs/velociraptor-to-bigquery).

  * `schema`: describes the column names, data types, and other information; should match the text-formatted schema from bigquery

  * `table`: the table name where to send data.

  * `dataset`: the dataset name where to send data.

  * `project`: the project name where to send the data.

  * `secret_key`: the secret json key identifying a service account.

  * `sec_per_file`: the number of seconds after which a batch of data is loaded.

  * `custom_transform`: should align with the schema fields/formats




Example:
    
    
    schema: event_type:STRING, oid:STRING, sid:STRING
    table: alerts
    dataset: limacharlie_data
    project: lc-example-analytics
    secret_key: {
      "type": "service_account",
      "project_id": "my-lc-data",
      "private_key_id": "11b6f4173dedabcdefb779e4afae6d88ddce3cc1",
      "private_key": "-----BEGIN PRIVATE KEY-----\n.....\n-----END PRIVATE KEY-----\n",
      "client_email": "my-service-writer@my-lc-data.iam.gserviceaccount.com",
      "client_id": "102526666608388828174",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/my-service-writer%40my-lc-data.iam.gserviceaccount.com"
    }
    custom_transform: |-
      {
        "oid":"routing.oid",
        "sid":"routing.sid",
        "event_type":"routing.event_type"
      }
    

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

  * [ Building Reports with BigQuery + Looker Studio ](/docs/tutorials-reporting-building-reports-with-bigquery-looker-studio)
  * [ Google Cloud Pubsub ](/docs/outputs-destinations-google-cloud-pubsub)
  * [ Google Cloud Storage ](/docs/outputs-destinations-google-cloud-storage)
  * [ Google Workspace ](/docs/adapter-types-google-workspace)
  * [ Google Cloud Storage ](/docs/adapter-types-google-cloud-storage)
  * [ Tutorial: Ingesting Google Cloud Logs ](/docs/tutorial-ingesting-google-cloud-logs)
  * [ Google Cloud ](/docs/ext-cloud-cli-google-cloud)



* * *

###### What's Next

  * [ Google Cloud Pubsub ](/docs/outputs-destinations-google-cloud-pubsub) __



Tags

  * [ gcp ](/docs/en/tags/gcp)
  * [ outputs ](/docs/en/tags/outputs)


