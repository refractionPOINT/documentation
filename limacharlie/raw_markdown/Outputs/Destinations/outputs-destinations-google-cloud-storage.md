---
title: Google Cloud Storage
slug: outputs-destinations-google-cloud-storage
breadcrumb: Outputs > Destinations
source: https://docs.limacharlie.io/docs/outputs-destinations-google-cloud-storage
articleId: ffde2f56-79b4-4b38-bc5e-85e5f293e4e6
---

* * *

Google Cloud Storage

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Google Cloud Storage

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

Output events and detections to a GCS bucket.

Looking for Google Chronicle?

If you already use Google Chronicle, we make it easy to send telemetry you've collected in LimaCharlie to Chronicle. You can get that set up by creating an Output in LimaCharlie to a GCS bucket.

  * `bucket`: the path to the GCS bucket.

  * `secret_key`: the secret json key identifying a service account.

  * `sec_per_file`: the number of seconds after which a file is cut and uploaded.

  * `is_compression`: if set to "true", data will be gzipped before upload.

  * `is_indexing`: if set to "true", data is uploaded in a way that makes it searchable.

  * `dir`: the directory prefix where to output the files on the remote host.




Example:
    
    
    bucket: my-bucket-name
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
    is_indexing: "true"
    is_compression: "true"
    

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
  * [ Google Cloud BigQuery ](/docs/outputs-destinations-google-cloud-bigquery)
  * [ Google Workspace ](/docs/adapter-types-google-workspace)
  * [ Google Cloud Storage ](/docs/adapter-types-google-cloud-storage)
  * [ Google Cloud Pubsub ](/docs/adapter-types-google-cloud-pubsub)
  * [ Tutorial: Ingesting Google Cloud Logs ](/docs/tutorial-ingesting-google-cloud-logs)
  * [ Google Cloud ](/docs/ext-cloud-cli-google-cloud)



* * *

###### What's Next

  * [ Humio ](/docs/outputs-destinations-humio) __



Tags

  * [ gcp ](/docs/en/tags/gcp)
  * [ outputs ](/docs/en/tags/outputs)


