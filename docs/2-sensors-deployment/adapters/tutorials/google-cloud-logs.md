# Tutorial: Ingesting Google Cloud Logs

With LimaCharlie, you can ingest Google Cloud logs for more processing and automation. This article gives the high-level steps to send logs from GCP into LimaCharlie:

1. Create a Log Sink to Pubsub in GCP
2. Create a Subscription for the Topic
3. Create a Service Account with the required permissions.
4. [Optional] Create a GCE instance to run the Adapter.
5. Create an Installation Key in LimaCharlie
6. Run the LC Adapter to ingest the logs.

Note: This tutorial is a synthesized version of the [official GCP article](https://cloud.google.com/logging/docs/export/configure_export_v2).

## Step 1: Create a Log Sink

1. In your GCP Project, or Organization, go to the Logging product and the Logs Router section.

    ![image.png](../../../assets/images/image(145).png)

2. Click the Create Sink button.
3. Give the sink a Name and Description.
4. In the Sink Destination, choose Cloud Pub/Sub Topic as a sink service.
5. Below, select Create a Topic.

    ![image.png](../../../assets/images/image(146).png)

6. Give the Topic an ID.
7. Click Create Topic. The creation of the Topic takes a few seconds.
8. Click Next.
9. Choose the logs to include. Select only the logs that you want, because GCP logs can be verbose.

    ![image.png](../../../assets/images/image(147).png)

    To open the main logging interface, click the Preview Logs button in the top right. In that interface you can test different log selections.

    This example uses this log filter:

    ```text
    logName:cloudaudit.googleapis.com
    protoPayload.serviceName!="k8s.io"
    protoPayload.serviceName!="compute.googleapis.com"
    ```

    This filter includes all cloudaudit logs, except some GKE and GCE logs.

10. Click Next. You can also define an exclusion filter. This example does not use one.
11. Click Create Sink. A confirmation shows that the sink was created.

    ![image.png](../../../assets/images/image(148).png)

## Step 2: Create a Subscription

1. Go to the Pubsub product.

    ![image.png](../../../assets/images/image(149).png)

2. Click your new Topic.
3. Click the Create Subscription button.
4. Select Create Subscription.

    ![image.png](../../../assets/images/image(150).png)

5. Give this Subscription a name. You need this name later, when you configure the Adapter.
6. Keep the default value of all other options.
7. Click Create.

## Step 3: Create a Service Account

1. Go to the IAM & Admin product, then to the Service Accounts section.

    ![image.png](../../../assets/images/image(151).png)

2. Click Create Service Account.
3. Give the new Service Account a Name and Description.
4. Click Create and Continue.
5. Select the Pub/Sub Subscriber role.

    ![image.png](../../../assets/images/image(152).png)

6. Click Continue.
7. Click Done.

The new Service Account has access to the Topic that you created.

## [OPTIONAL] Step 4: Create a GCE Instance

This step is optional. If you already have a machine that can run the collector, go to the next step.

1. Go to the Compute Engine product.

    ![image.png](../../../assets/images/image(153).png)

2. Click the Create Instance button.
3. Set these options. You can customize more options, but this tutorial does not use them.

    - Give the instance a name.
    - Select a zone near the LimaCharlie datacenter that you use.
    - As a Machine Type, select e2-micro (the smallest and cheapest machine type).
    - In the Identity and API access section, select the Service Account that you created earlier. This sets the service account as the default identity of the machine. You then do not give your credentials to the LimaCharlie Adapter.

4. Click Create. This can take a minute.
5. After the instance is created, click the SSH button to log on to the machine.

    ![image.png](../../../assets/images/image(154).png)

A console opens on the machine. You can now install the Adapter.

## Step 5: Create an Installation Key in LimaCharlie

1. In your Org in LimaCharlie, go to the Sensors > Installation Keys section.
2. Click the Create Installation Key button.
3. Enter a name for the key. This name does not change the name of the source of the logs.
4. Click the copy-to-clipboard button next to the Adapter Key column. **The value is a UUID. Keep it, because you need it in the next step.**

    ![Click the Create Installation Key button](../../../assets/images/image(309).png)

## Step 6: Run the Adapter

1. Download the latest adapter for Linux.

    ```bash
    curl -L https://downloads.limacharlie.io/adapter/linux/64 -o lc_adapter
    chmod +x lc_adapter
    ```

2. Check that the adapter runs.

    ```bash
    ./lc_adapter
    ```

    The console prints all the options that are available to all the collection methods.

3. Run the adapter with the necessary configuration. Replace each value with your own.

    ```bash
    ./lc_adapter pubsub \
    client_options.identity.installation_key=YOUR_INSTALLATION_KEY \
    client_options.identity.oid=YOUR_LC_OID \
    client_options.platform=gcp \
    sub_name=YOUR_SUBSCRIPTION_NAME \
    project_name=YOUR_GCP_PROJECT_NAME \
    client_options.sensor_seed_key=SOME_ARBITRARY_ADAPTER_NAME
    ```

The adapter prints text about the connection to LimaCharlie. It also prints the errors that occur when it fetches data from pubsub.

The new Sensor is shown in your Sensor List in LimaCharlie after a few seconds.

The events are shown in the Timeline section of the new sensor after one or two minutes.

For production, run the Adapter as a service, or in tmux or screen on the Linux host. You can also repeat this setup with the [Docker container](https://hub.docker.com/r/refractionpoint/lc-adapter) and a serverless platform such as Cloud Run.

For more documentation, see [Configuring Adapters](../usage.md).
