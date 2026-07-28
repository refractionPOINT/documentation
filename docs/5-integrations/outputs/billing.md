# Output Billing

LimaCharlie aims to bill outputs at cost. By default, LimaCharlie bills outputs at the [published pricing](https://limacharlie.io/pricing).

There is one exception. If an output uses a Google Cloud Platform mechanism, and the destination region is the same as the region of the relevant LimaCharlie datacenter, LimaCharlie does not bill the output.

These are the relevant regions for each LimaCharlie datacenter.

- USA: `us-central1`
- Canada: `northamerica-northeast1`
- Europe: `europe-west4`
- UK: `europe-west2`
- India: `asia-south1`
- Australia: `australia-southeast1`

These GCP mechanisms support free output:

- `gcs`
- `pubsub`
- `bigquery`

Google Cloud Platform general region list: <https://cloud.google.com/about/locations>

The IP ranges of GCP resources for each region change over time. Google publishes these ranges as a JSON file: <https://www.gstatic.com/ipranges/cloud.json>
