---
title: Google Cloud
slug: ext-cloud-cli-google-cloud
breadcrumb: Add-Ons > Extensions > Third-Party Extensions > Cloud CLI
source: https://docs.limacharlie.io/docs/ext-cloud-cli-google-cloud
articleId: 0a9b95ca-fd8b-4f4d-a217-868e27795a6b
---

* * *

Google Cloud

  *  __05 Oct 2024
  *  __ 1 Minute to read 



Share this __

  * __ Print

  *  __ Share

  *  __ Dark

 __ Light




 __Contents

# Google Cloud

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

The Google Cloud command line interface, or gcloud CLI, allows you to create and manage Google Cloud resources and services directly on the command line. With this component of the Cloud CLI Extension, you can interact with Google Cloud directly from LimaCharlie.

This extension makes use of Google Cloud's native CLI tool, which can be found [here](https://cloud.google.com/cli).

## Example

The following example stops the specified GCP compute instance.
    
    
    - action: extension request
      extension action: run
      extension name: ext-cloud-cli
      extension request:
        cloud: '{{ "gcloud" }}' 
        command_tokens:
          - compute
          - instances
          - stop
          - '{{ .routing.hostname }}'
        credentials: '{{ "hive://secret/secret-name" }}'
    

## Credentials

To utilize Google Cloud CLI capabilities, you will need:

  * A GCP service account JSON key. More information on service account keys can be found [here](https://cloud.google.com/iam/docs/keys-create-delete).

  * Create a secret in the secrets manager in the following format:
    
        {
        "type": "",
        "project_id": "",
        "private_key_id": "",
        "private_key": "",
        "client_email": "",
        "client_id": "",
        "auth_uri": "",
        "token_uri": "",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "",
        "universe_domain": "googleapis.com"
    }
    




Command-line Interface

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Google Cloud Platform

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

  * [ Google Cloud Storage ](/docs/outputs-destinations-google-cloud-storage)
  * [ Building Reports with BigQuery + Looker Studio ](/docs/tutorials-reporting-building-reports-with-bigquery-looker-studio)
  * [ Google Cloud Pubsub ](/docs/outputs-destinations-google-cloud-pubsub)
  * [ Google Cloud BigQuery ](/docs/outputs-destinations-google-cloud-bigquery)
  * [ Google Workspace ](/docs/adapter-types-google-workspace)
  * [ Google Cloud Storage ](/docs/adapter-types-google-cloud-storage)
  * [ Google Cloud Pubsub ](/docs/adapter-types-google-cloud-pubsub)
  * [ Tutorial: Ingesting Google Cloud Logs ](/docs/tutorial-ingesting-google-cloud-logs)



* * *

###### What's Next

  * [ Microsoft 365 ](/docs/ext-cloud-cli-microsoft365) __



Table of contents

    * Example 
    * Credentials 



Tags

  * [ add-ons ](/docs/en/tags/add-ons)
  * [ extensions ](/docs/en/tags/extensions)
  * [ gcp ](/docs/en/tags/gcp)


