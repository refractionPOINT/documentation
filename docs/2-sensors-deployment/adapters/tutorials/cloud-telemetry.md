# Tutorial: Ingesting Telemetry from Cloud-Based External Sources

LimaCharlie ingests logs or telemetry from any external source in real-time. It has built-in parsing for common formats. For a custom source, you can define your own parsing.

There are two ways to ingest logs or telemetry from external sources:

- Run the [LimaCharlie Adapter](../usage.md) on premises or on your cloud
- Give the credentials for the destination and let the LimaCharlie cloud connect directly (available for cloud-based Adapters)

To connect to a cloud-based external source, first make sure that you have the necessary `cloudsensor.*` permissions.

After you enable the permissions, do these steps:

1. In the web app, go to the `Sensors` page.
2. Click `Add Sensor`.
3. Choose the external source that you want to ingest logs or telemetry from. To see the available options, filter the list to `Cloud & External Sources`.

    If an external source is not in the list, you can ingest it with the LimaCharlie Adapter and your own parsing. You can also contact LimaCharlie to discuss support for that source.

4. Choose or create an Installation Key.
5. Enter the name for the sensor.
6. Enter the method-specific credentials for the connection.

If the sensor that you selected is cloud-based, the `Complete Cloud Installation` action is shown.

*Note: You can also install a sensor that supports cloud to cloud communication with an adapter on-prem, or on a cloud that the customer hosts. This scenario is rare. Some customers prefer this option because they do not want to share the API credentials of the sensor with LimaCharlie.*
