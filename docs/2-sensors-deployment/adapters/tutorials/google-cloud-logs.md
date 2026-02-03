# Tutorial: Ingesting Google Cloud Logs

With LimaCharlie, you can easily ingest Google Cloud logs for further processing and automation. This article covers the following high-level steps of shipping logs from GCP into LimaCharlie:

1. Create a Log Sink to Pubsub in GCP
2. Create a Subscription for the Topic
3. Create a Service Account with the required permissions.
4. [Optional] Create a GCE instance to run the Adapter.
5. Create an Installation Key in LimaCharlie
6. Run the LC Adapter to ingest the logs.

Note: This tutorial is a synthesized version of this [official GCP article](https://cloud.google.com/logging/docs/export/configure_export_v2).

## Step 1: Create a Log Sink

In your GCP Project, or Organization, go to the Logging product and the Logs Router section.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(145).png)

Click the Create Sink button, give it a Name and Description.

In the Sink Destination choose Cloud Pub/Sub Topic as a sink service.

Below, select Create a Topic.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(146).png)

Give the Topic an ID and click Create Topic.

The Topic should now be creating, which can take a few seconds.

Click Next.

Now you need to choose which logs you want included. Be careful selecting exactly what you want as GCP logs can get very verbose.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(147).png)

Click the Preview Logs button in the top right to be taken to the main logging interface where you can experiment with selecting the right logs.

For this example, let's use the following log filter:

```
logName:cloudaudit.googleapis.com
protoPayload.serviceName!="k8s.io"
protoPayload.serviceName!="compute.googleapis.com"
```

This filter will include all cloudaudit logs, except some GKE and GCE logs.

Click Next. You can optionally define an exclusion filter. Let's skip this step.

Click Create Sink. You should get a confirmation the sink was created.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(148).png)

## Step 2: Create a Subscription

Go to the Pubsub product.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(149).png)

Click on your new Topic.

Click on the Create Subscription button and select Create Subscription.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(150).png)

Give this Subscription a name, you will need this name later when configuring the Adapter.

You can leave all other options to their default. Click Create.

## Step 3: Create a Service Account

Head over to the IAM & Admin product. Then the Service Accounts section.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(151).png)

Click Create Service Account.

Give the new Service Account a Name and Description. Click Create and Continue.

Select a Role. You want to select Pub/Sub Subscriber.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(152).png)

Click Continue. And finally click Done.

This new Service Account has access to the Topic created.

## [OPTIONAL] Step 4: Create a GCE Instance

This step is optional. You may already have a machine you want to run the collector from, in which case you can skip this step.

Head over to the Compute Engine product.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(153).png)

Click the Create Instance button.

There is a lot you can customize here, but we'll skip over the more complex aspects you don't need to worry about here.

* Give the instance a name.
* Select a zone nearby the LimaCharlie datacenter you're using.
* As a Machine Type, select e2-micro (the smallest and cheapest machine type).
* In the Identity and API access section, select the Service Account you created earlier. This will set this service account as the default identity of the machine, which in turn means you won't have to specify your credentials to the LimaCharlie Adapter we're about to run.

Click Create. This may take a minute.

Once created, click the SSH button to log on the machine.

![image.png](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(154).png)

This will bring you to a console on the machine, ready to install the Adapter.

## Step 5: Create an Installation Key in LimaCharlie

In your Org in LimaCharlie, go to the Sensors > Installation Keys section.

Click the Create Installation Key button. Enter a name for the key. This name will not impact the name given to the source of the logs.

Click on the copy-to-clipboard button next to the Adapter Key column. **The value should be a UUID, keep note of it, you'll need it in the next step.**

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/image(309).png)

## Step 6: Run the Adapter

First let's download the latest adapter for Linux.

```python
curl -L https://downloads.limacharlie.io/adapter/linux/64 -o lc_adapter
chmod +x lc_adapter
```

We can confirm the adapter is running as expected:

```bash
./lc_adapter
```

You should see all the options available to all the collection methods being printed to the console.

Now let's run the adapter with all the relevant configurations, replacing the various values necessary.

```bash
./lc_adapter pubsub \
client_options.identity.installation_key=YOUR_INSTALLATION_KEY \
client_options.identity.oid=YOUR_LC_OID \
client_options.platform=gcp \
sub_name=YOUR_SUBSCRIPTION_NAME \
project_name=YOUR_GCP_PROJECT_NAME \
client_options.sensor_seed_key=SOME_ARBITRARY_ADAPTER_NAME
```

You should see some text letting you know the adapter is connecting to LimaCharlie, and if any errors occur fetching data from pubsub.

Within a few seconds you should see the new Sensor in your Sensor List in LimaCharlie.

Within a minute or two you should see the events flowing in the Timeline section of this new sensor.

That's it, you're good to go!

The next step towards production would be to run the Adapter as a service, or within tmux/screen on the Linux host. Alternatively you could also replicate the above setup using the [Docker container](https://hub.docker.com/r/refractionpoint/lc-adapter) and a serverless platform like Cloud Run.

For more documentation on configuring Adapters, see [here](../usage.md).
