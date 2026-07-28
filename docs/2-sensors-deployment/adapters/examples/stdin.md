# Stdin

This example uses the CLI Adapter to receive data from STDIN. Use this method to ingest logs on disk, or to pipe the output of another application.

```bash
./lc_adapter stdin client_options.identity.installation_key=e9a3bcdf-efa2-47ae-b6df-579a02f3a54d \
      client_options.identity.oid=8cbe27f4-bfa1-4afb-ba19-138cd51389cd \
      client_options.platform=text \
      "client_options.mapping.parsing_grok.message=%{DATESTAMP:date} %{HOSTNAME:host} %{WORD:exe}\[%{INT:pid}\]: %{GREEDYDATA:msg}" \
      client_options.sensor_seed_key=testclient3 \
      client_options.mapping.event_type_path=exe \
      client_options.hostname=testclient3
```

The example uses these options:

- `stdin`: the method that the Adapter uses to collect data locally. The `stdin` value ingests from the STDIN of the Adapter.
- `client_options.identity.installation_key=....`: the Installation Key value from LimaCharlie.
- `client_options.identity.oid=....`: the Organization ID in LimaCharlie that owns the installation key above.
- `client_options.platform=text`: the type of data that this adapter receives. In this example, the data is `text` lines.
- `client_options.mapping.parsing_grok.message=....`: the grok expression that describes how to interpret the text lines and how to convert them to JSON.
- `client_options.sensor_seed_key=....`: the value that identifies this instance of the Adapter. Keep this value. It lets you re-use the Sensor ID of this Adapter if you re-install the Adapter.
- `client_options.mapping.event_type_path=....`: specifies the field that LimaCharlie interprets as the "event_type".
- `client_options.hostname=....`: specifies the sensor hostname for the adapter.
