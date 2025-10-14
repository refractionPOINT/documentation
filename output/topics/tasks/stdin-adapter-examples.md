# Stdin Adapter

The stdin adapter provides a method for ingesting arbitrary logs on disk or from other applications locally using the CLI Adapter's STDIN interface. This approach is similar to the Syslog adapter but allows for direct piping of data into the adapter.

## Example Configuration

```bash
./lc_adapter stdin client_options.identity.installation_key=e9a3bcdf-efa2-47ae-b6df-579a02f3a54d \
      client_options.identity.oid=8cbe27f4-bfa1-4afb-ba19-138cd51389cd \
      client_options.platform=text \
      "client_options.mapping.parsing_grok.message=%{DATESTAMP:date} %{HOSTNAME:host} %{WORD:exe}\[%{INT:pid}\]: %{GREEDYDATA:msg}" \
      client_options.sensor_seed_key=testclient3 \
      client_options.mapping.event_type_path=exe
```

## Parameter Breakdown

* **`lc_adapter`**: The CLI Adapter executable
* **`stdin`**: The collection method specifying that the adapter should ingest data from its STDIN interface
* **`client_options.identity.installation_key`**: The Installation Key value from LimaCharlie. Installation keys are Base64-encoded strings provided to Sensors and Adapters to associate them with the correct Organization. They are created per-organization and offer a way to label and control your deployment population.
* **`client_options.identity.oid`**: The Organization ID from LimaCharlie that the installation key belongs to
* **`client_options.platform`**: Indicates the type of data that will be received from this adapter. In this case, `text` specifies line-based text data.
* **`client_options.mapping.parsing_grok.message`**: The grok expression that describes how to interpret the text lines and convert them to JSON format. The example pattern `%{DATESTAMP:date} %{HOSTNAME:host} %{WORD:exe}\[%{INT:pid}\]: %{GREEDYDATA:msg}` extracts structured fields from log entries.
* **`client_options.sensor_seed_key`**: A value that uniquely identifies this instance of the Adapter. This should be recorded to re-use the same Sensor ID if you need to re-install the Adapter later.
* **`client_options.mapping.event_type_path`**: Specifies which field should be interpreted as the "event_type" in LimaCharlie. In this example, the `exe` field is used as the event type.

## How It Works

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

The stdin adapter reads data line-by-line from standard input, parses it according to the specified grok pattern, and forwards the structured data to the LimaCharlie platform where it can be analyzed, searched, and used to trigger detection and response rules.