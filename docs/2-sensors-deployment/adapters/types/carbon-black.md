# VMWare Carbon Black

## Overview

LimaCharlie can ingest Carbon Black events from many storage locations. An organization usually exports Carbon Black data through the API to a storage location, such as an S3 bucket. LimaCharlie then ingests the data from that location.

You see Carbon Black events in Detection & Response rules through the `carbon_black` platform.

## Deployment Configurations

All adapters support the same `client_options`. Always specify them when you use the binary adapter or create a webhook adapter. If you use an adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter uses.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, such as `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name that you choose for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name. See below.

## Config File

You can export VMWare Carbon Black data through the API to an S3 bucket, then ingest it with LimaCharlie. This command uses a CLI adapter to ingest these events

```bash
./lc_adapter s3 client_options.identity.installation_key=<INSTALLATION_KEY> \
client_options.identity.oid=<OID> \
client_options.platform=carbon_black \
client_options.sensor_seed_key=tests3 \
bucket_name=lc-cb-test \
access_key=YYYYYYYYYY \
secret_key=XXXXXXXX  \
"prefix=events/org_key=NKZAAAEM/"
```

This is an explanation of the example above:

- `lc_adapter`: the CLI adapter.
- `s3`: the adapter collects the data from an AWS S3 bucket.
- `client_options.identity.installation_key=....`: the Installation Key value from LimaCharlie.
- `client_options.identity.oid=....`: the LimaCharlie Organization ID that owns the installation key above.
- `client_options.platform=carbon_black`: this value shows that the received data is Carbon Black events from the Carbon Black API.
- `client_options.sensor_seed_key=....`: the value that identifies this instance of the adapter. Record it. If you re-install the adapter, this value lets you re-use the Sensor IDs that LimaCharlie generated for the Carbon Black sensors.
- `bucket_name:....`: the name of the S3 bucket holding the data.
- `access_key:....`: the AWS Access Key for the API key below.
- `secret_key:....`: the API key for AWS that has access to this bucket.
- `prefix=....`: the file/directory name prefix that holds the Carbon Black data within the bucket.
