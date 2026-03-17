# Stdin JSON

This example is similar to the [Stdin](stdin.md) example, except it assumes the data being read is JSON, not text. If your data source is already JSON, it's simpler to let LimaCharlie handle the JSON parsing directly.

```bash
./lc_adapter stdin client_options.identity.installation_key=e9a3bcdf-efa2-47ae-b6df-579a02f3a54d \
    client_options.identity.oid=8cbe27f4-bfa1-4afb-ba19-138cd51389cd \
    client_options.platform=json \
    client_options.sensor_seed_key=testclient3 \
    client_options.mapping.event_type_path=type \
    client_options.hostname=testclient3
```

Here's a breakdown of the above example:

* `stdin`: the method the Adapter should use to collect data locally. The `stdin` value will ingest from the Adapter's STDIN.
* `client_options.identity.installation_key=....`: the Installation Key value from LimaCharlie.
* `client_options.identity.oid=....`: the Organization ID from LimaCharlie the installation key above belongs to.
* `client_options.platform=json`: this indicates that the data read is already JSON, so just parse it as-is.
* `client_options.sensor_seed_key=....`: this is the value that identifies this instance of the Adapter. Record it to re-use the Sensor ID generated for this Adapter later if you have to re-install the Adapter.
* `client_options.mapping.event_type_path=....`: specifies the field that should be interpreted as the "event_type" in LimaCharlie.
* `client_options.hostname=....`: specifies the sensor hostname for the adapter.

Note that we did not need to specify a `parsing_re` or `parsing_grok` because the data ingested is not text, but already JSON, so the parsing step is already done for us by setting `platform=json`.
