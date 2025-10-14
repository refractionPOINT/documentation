# File

## Overview

This Adapter allows you to ingest logs from a file, either as a one time operation or by following its output (like `tail -f`). A more detailed guide to file collection can be found in the [Log Collection Guide](../tasks/logcollectionguide.md).

### Configuration

All adapters support the same `client_options`, which you should always specify if using the binary adapter or creating a webhook adapter. If you use any of the Adapter helpers in the web app, you will not need to specify these values.

* `client_options.identity.oid`: the LimaCharlie Organization ID (OID) this adapter is used with.
* `client_options.identity.installation_key`: the LimaCharlie Installation Key this adapter should use to identify with LimaCharlie.
* `client_options.platform`: the type of data ingested through this adapter, like `text`, `json`, `gcp`, `carbon_black`, etc.
* `client_options.sensor_seed_key`: an arbitrary name for this adapter which Sensor IDs (SID) are generated from, see below.

Adapter type `file`:

* `file_path`: simple file pattern like `./files_*.txt`
* `no_follow`: if `true`, the file content will be sent, but additions to the file will not be reported
* `inactivity_threshold`: the number of seconds after which an unmodified file becomes ignored
* `backfill`: if `true`, a single pass at all the matching files will be made to ingest them, useful for historical ingestion
* `serialize_files`: if `true`, files will be ingested one at a time, useful for very large number of files that could blow up memory

### CLI Deployment

Adapter downloads can be found [here](../tasks/adapter-deployment.md).

```
chmod +x /path/to/lc_adapter

/path/to/lc_adapter file client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=text \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
file_path=/path/to/file
```

Adapters serve as flexible data ingestion mechanisms for both on-premise and cloud environments.