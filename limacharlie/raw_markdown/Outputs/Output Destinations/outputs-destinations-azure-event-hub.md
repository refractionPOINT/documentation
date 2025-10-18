# Azure Event Hub

Output events and detections to an Azure Event Hub (similar to PubSub and Kafka).

  * `connection_string`: the connection string provided by Azure.

Note that the connection string should end with `;EntityPath=your-hub-name` which is sometimes missing from the "Connection String" provided by Azure.

Example:


    connection_string: Endpoint=sb://lc-test.servicebus.windows.net/;SharedAccessKeyName=lc;SharedAccessKey=jidnfisnjfnsdnfdnfjd=;EntityPath=test-hub
