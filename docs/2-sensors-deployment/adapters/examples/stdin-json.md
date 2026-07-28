# Stdin JSON

This example is similar to the [Stdin](stdin.md) example, but the data is JSON, not text. If your data source is already JSON, let LimaCharlie parse the JSON directly.

```bash
./lc_adapter stdin client_options.identity.installation_key=e9a3bcdf-efa2-47ae-b6df-579a02f3a54d \
    client_options.identity.oid=8cbe27f4-bfa1-4afb-ba19-138cd51389cd \
    client_options.platform=json \
    client_options.sensor_seed_key=testclient3 \
    client_options.mapping.event_type_path=type \
    client_options.hostname=testclient3
```

The example uses these options:

- `stdin`: the method that the Adapter uses to collect data locally. The `stdin` value ingests from the STDIN of the Adapter.
- `client_options.identity.installation_key=....`: the Installation Key value from LimaCharlie.
- `client_options.identity.oid=....`: the Organization ID in LimaCharlie that owns the installation key above.
- `client_options.platform=json`: shows that the data is already JSON, so LimaCharlie parses it as-is.
- `client_options.sensor_seed_key=....`: the value that identifies this instance of the Adapter. Keep this value. It lets you re-use the Sensor ID of this Adapter if you re-install the Adapter.
- `client_options.mapping.event_type_path=....`: specifies the field that LimaCharlie interprets as the "event_type".
- `client_options.hostname=....`: specifies the sensor hostname for the adapter.

The example does not specify `parsing_re` or `parsing_grok`. The ingested data is already JSON, and `platform=json` completes the parsing step.
