# VirusTotal

## API Keys

The VirusTotal API key is added via the [integrations](https://docs.limacharlie.io/v2/docs/add-ons-api-integrations#configuration) menu within LimaCharlie.

## Usage

With the `vt` [add-on](https://app.limacharlie.io/add-ons/detail/vt) subscribed and a VirusTotal API Key configured in the Integrations page, VirusTotal can be used as an API-based lookup.

```
event: CODE_IDENTITY
op: lookup
path: event/HASH
resource: hive://lookup/vt
metadata_rules:
  op: is greater than
  value: 1
  path: /
  length of: true
```

Step-by-step, this rule will do the following:

* Upon seeing a `CODE_IDENTITY` event, retrieve the `event/HASH` value and send it to VirusTotal via the `api/vt` resource.
* Upon receiving a response from `api/vt`, evaluate it using `metadata_rules` to see if the length of the response is greater than 1 (in this case meaning that more than 1 vendor reporting a hash is bad).