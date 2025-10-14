I'll analyze these two documents to determine if they should be merged or kept separate.

These documents are related but cover different scenarios of the same broader topic: ingesting external data into LimaCharlie. The first is a specific, detailed tutorial for Google Cloud logs, while the second is a general overview of cloud-based ingestion with multiple options. They should be kept as separate sections since they serve different purposes, but I'll organize them under a common theme.

```markdown
# Ingesting Telemetry from External Sources

LimaCharlie provides flexible options for ingesting logs and telemetry from external sources in real-time. This can be accomplished through two primary methods:

* Run the [LimaCharlie Adapter](/v2/docs/adapters) on premises or on your cloud infrastructure
* Provide credentials for cloud-based sources and allow LimaCharlie cloud to connect directly (available for cloud-based Adapters)

## Cloud-Based External Sources

LimaCharlie includes built-in parsing for popular log formats, with the option to define your own for custom sources.

### Prerequisites

Ensure you have the appropriate `cloudsensor.*` permissions enabled before beginning.

### Setup Process

1. Navigate to the `Sensors` page of the web app and click `Add Sensor`
2. Choose an external source you would like to ingest logs or telemetry from, or filter the list to only include `Cloud & External Sources` to see available options
3. Select the Sensor type
4. Choose or create an [Installation Key](/v2/docs/installation-keys)
5. Enter the name for the sensor
6. Provide method-specific credentials for connection
7. If the sensor is cloud-based, you will see the call to action `Complete Cloud Installation`

**Note:** If there is an external source you wish to connect that is not listed, you can still ingest via the LimaCharlie Adapter with self-defined parsing. Alternatively, contact LimaCharlie to discuss adding this source to the platform.

**Note:** Sensors that support cloud-to-cloud communication can also be installed by running an adapter on-premise or on cloud infrastructure hosted by the customer. While this is a rare scenario, some customers prefer this option when they do not want to share the sensor's API credentials with LimaCharlie.

### How Adapters Work

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments. Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

---

## Tutorial: Ingesting Google Cloud Logs

This tutorial demonstrates how to ship logs from Google Cloud Platform (GCP) into LimaCharlie using the Pub/Sub adapter method.

### Overview

The process involves the following steps:

1. Create a Log Sink to Pub/Sub in GCP
2. Create a Subscription for the Topic
3. Create a Service Account with the required permissions
4. [Optional] Create a GCE instance to run the Adapter
5. Create an Installation Key in LimaCharlie
6. Run the LC Adapter to ingest the logs

**Note:** This tutorial is a synthesized version of this [official GCP article](https://cloud.google.com/logging/docs/export/configure_export_v2).

### Step 1: Create a Log Sink

1. In your GCP Project or Organization, go to the **Logging** product and the **Logs Router** section

   ![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28145%29.png)

2. Click the **Create Sink** button, give it a Name and Description

3. In the **Sink Destination** choose **Cloud Pub/Sub Topic** as a sink service

4. Select **Create a Topic**

   ![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28146%29.png)

5. Give the Topic an ID and click **Create Topic**

6. The Topic will be created (this can take a few seconds)

7. Click **Next**

8. Choose which logs you want included. **Be careful selecting exactly what you want as GCP logs can get very verbose.**

   ![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28147%29.png)

9. Click the **Preview Logs** button in the top right to be taken to the main logging interface where you can experiment with selecting the right logs

#### Example Log Filter

For this example, the following log filter will include all cloudaudit logs, except some GKE and GCE logs:

```
logName:cloudaudit.googleapis.com
protoPayload.serviceName!="k8s.io"
protoPayload.serviceName!="compute.googleapis.com"
```

10. Click **Next**. You can optionally define an exclusion filter. For this tutorial, skip this step.

11. Click **Create Sink**. You should get a confirmation the sink was created.

    ![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28148%29.png)

### Step 2: Create a Subscription

1. Go to the **Pub/Sub** product

   ![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28149%29.png)

2. Click on your new Topic

3. Click on the **Create Subscription** button and select **Create Subscription**

   ![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28150%29.png)

4. Give this Subscription a name. **You will need this name later when configuring the Adapter.**

5. Leave all other options to their default

6. Click **Create**

### Step 3: Create a Service Account

1. Navigate to the **IAM & Admin** product, then the **Service Accounts** section

   ![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28151%29.png)

2. Click **Create Service Account**

3. Give the new Service Account a Name and Description

4. Click **Create and Continue**

5. Select a Role: **Pub/Sub Subscriber**

   ![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28152%29.png)

6. Click **Continue**

7. Click **Done**

This new Service Account now has access to the Topic created.

### Step 4: Create a GCE Instance [OPTIONAL]

This step is optional. If you already have a machine you want to run the collector from, you can skip this step.

1. Navigate to the **Compute Engine** product

   ![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28153%29.png)

2. Click the **Create Instance** button

3. Configure the instance:
   * Give the instance a name
   * Select a zone nearby the LimaCharlie datacenter you're using
   * As a **Machine Type**, select **e2-micro** (the smallest and cheapest machine type)
   * In the **Identity and API access** section, select the Service Account you created earlier. This will set this service account as the default identity of the machine, which means you won't have to specify your credentials to the LimaCharlie Adapter

4. Click **Create**. This may take a minute.

5. Once created, click the **SSH** button to log on to the machine

   ![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image%28154%29.png)

This will bring you to a console on the machine, ready to install the Adapter.

### Step 5: Create an Installation Key in LimaCharlie

1. In your Org in LimaCharlie, go to the **Sensors > Installation Keys** section

2. Click the **Create Installation Key** button

3. Enter a name for the key. This name will not impact the name given to the source of the logs.

4. Click on the copy-to-clipboard button next to the **Adapter Key** column. **The value should be a UUID. Keep note of it, you'll need it in the next step.**

   ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(309).png)

### Step 6: Run the Adapter

#### Download the Adapter

First, download the latest adapter for Linux:

```bash
curl -L https://downloads.limacharlie.io/adapter/linux/64 -o lc_adapter
chmod +x lc_adapter
```

#### Verify the Adapter

Confirm the adapter is running as expected:

```bash
./lc_adapter
```

You should see all the options available to all the collection methods being printed to the console.

#### Configure and Run

Now run the adapter with all the relevant configurations, replacing the values with your specific information:

```bash
./lc_adapter pubsub \
client_options.identity.installation_key=YOUR_INSTALLATION_KEY \
client_options.identity.oid=YOUR_LC_OID \
client_options.platform=gcp \
sub_name=YOUR_SUBSCRIPTION_NAME \
project_name=YOUR_GCP_PROJECT_NAME \
client_options.sensor_seed_key=SOME_ARBITRARY_ADAPTER_NAME
```

**Parameters:**
* `YOUR_INSTALLATION_KEY`: The UUID from Step 5
* `YOUR_LC_OID`: Your LimaCharlie Organization ID
* `YOUR_SUBSCRIPTION_NAME`: The subscription name from Step 2
* `YOUR_GCP_PROJECT_NAME`: Your GCP project name
* `SOME_ARBITRARY_ADAPTER_NAME`: An arbitrary name for this adapter instance

#### Verification

You should see text letting you know the adapter is connecting to LimaCharlie, and if any errors occur fetching data from Pub/Sub.

* Within a few seconds you should see the new Sensor in your Sensor List in LimaCharlie
* Within a minute or two you should see the events flowing in the Timeline section of this new sensor

### Production Deployment

For production use, consider the following options:

* Run the Adapter as a service
* Run within tmux/screen on the Linux host
* Use the [Docker container](https://hub.docker.com/r/refractionpoint/lc-adapter) with a serverless platform like Cloud Run

For more documentation on configuring Adapters, see the [Adapters documentation](/v2/docs/adapters).
```