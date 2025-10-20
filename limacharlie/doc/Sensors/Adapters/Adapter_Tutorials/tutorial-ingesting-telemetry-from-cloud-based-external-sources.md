# Tutorial: Ingesting Telemetry from Cloud-Based External Sources

LimaCharlie allows for ingestion of logs or telemetry from any external source in real-time. It includes built-in parsing for popular formats, with the option to define your own for custom sources.

There are two ways to ingest logs or telemetry from external sources:

* Run the LimaCharlie Adapter on premises or on your cloud
* Provide credentials for the destination and allow LimaCharlie cloud to connect directly (available for cloud-based Adapters)

To connect with the cloud-based external source, first ensure you have the appropriate `cloudsensor.*` permissions.

After the permissions have been enabled, navigate to the `Sensors` page of the web app and click `Add Sensor`.

Choose an external source you would like to ingest logs or telemetry from, or filter the list to only include `Cloud & External Sources` to see available options.

If there is an external source you wish to connect that is not listed, you can still ingest via the LimaCharlie Adapter with self-defined parsing. Alternatively, please contact us to discuss adding this source in LimaCharlie.

After selecting the Sensor type, choose or create an Installation Key. Then, enter the name for the sensor and provide method-specific credentials for connection.

If the sensor you selected is cloud-based, you will see the call to action `Complete Cloud Installation`.

*Note: Sensors that support cloud to cloud communication, can also be installed by running an adapter on-prem or on cloud hosted by the customer. While it is a rare scenario, some customers might prefer that option when they do not want to share the sensor's API credentials with LimaCharlie.*

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.
