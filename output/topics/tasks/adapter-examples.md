# Stdin

This example is similar to the Syslog example above, except it uses the CLI Adapter and receives the data from the CLI's STDIN interface. This method is perfect for ingesting arbitrary logs on disk or from other applications locally.

```
./lc_adapter stdin client_options.identity.installation_key=e9a3bcdf-efa2-47ae-b6df-579a02f3a54d \
      client_options.identity.oid=8cbe27f4-bfa1-4afb-ba19-138cd51389cd \
      client_options.platform=text \
      "client_options.mapping.parsing_grok.message=%{DATESTAMP:date} %{HOSTNAME:host} %{WORD:exe}\[%{INT:pid}\]: %{GREEDYDATA:msg}" \
      client_options.sensor_seed_key=testclient3 \
      client_options.mapping.event_type_path=exe
```

Here's a breakdown of the above example:

* `lc_adapter`: simply the CLI Adapter.
* `stdin`: the method the Adapter should use to collect data locally. The `stdin` value will simply ingest from the Adapter's STDIN.
* `client_options.identity.installation_key=....`: the Installation Key value from LimaCharlie.
* `client_options.identity.oid=....`: the Organization ID from LimaCharlie the installation key above belongs to.
* `client_options.platform=text`: this indicates the type of data that will be received from this adapter. In this case it's `text` lines.
* `client_options.mapping.parsing_grok.message=....`: this is the grok expression describing how to interpret the text lines and how to convert them to JSON.
* `client_options.sensor_seed_key=....`: this is the value that identifies this instance of the Adapter. Record it to re-use the Sensor ID generated for this Adapter later if you have to re-install the Adapter.
* `client_options.mapping.event_type_path=....`: specifies the field that should be interpreted as the "event\_type" in LimaCharlie.

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Installation keys are Base64-encoded strings provided to Sensors and Adapters in order to associate them with the correct Organization. Installation keys are created per-organization and offer a way to label and control your deployment population.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.