# Output Billing

LimaCharlie aims to bill outputs at cost. This means that as a default outputs are billed accordingly to the [published pricing](https://limacharlie.io/pricing).

An exception to this is outputs that use Google Cloud Platform mechanism where the destination region is the same as the one the relevant LimaCharlie datacenter lives in. In those cases, outputs are not billed.

Here is a list of the relevant regions for the various LimaCharlie datacenter.

  * USA: `us-central1`

  * Canada: `northamerica-northeast1`

  * Europe: `europe-west4`

  * UK: `europe-west2`

  * India: `asia-south1`

  * Australia: `australia-southeast1`




The supported GCP mechanism for free output are:

  * `gcs`

  * `pubsub`

  * `bigquery`




Google Cloud Platform general region list: <https://cloud.google.com/about/locations>

IP ranges of GCP resources per region change over time. Google publishes these ranges as a JSON file here: <https://www.gstatic.com/ipranges/cloud.json>


