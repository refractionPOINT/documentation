# Dumper

The Dumper Extension dumps several forensic artifacts on Windows hosts. It supports one action, which is to dump.

It supports two targets. `memory` dumps the memory of the host. `mft` dumps the MFT of the file system to CSV. The extension then sends the dump and the dump metadata to the LimaCharlie [Artifact Ingestion system](artifact.md). There you can download or analyze the dump. You can also create rules that detect characteristics of those dumps.

## Usage

When you enable dumper, LimaCharlie adds it to the Extensions view in your Organization. It accepts these parameters:

- `sid` - a Sensor ID for the host to do the memory dump
- `target` - memory or mft
- `retention` - the number of days to keep the memory dump (default is 30)
- `ignore_cert` - ignore certificate errors for payloads and collection (default `false`)

After you submit a request, the extension does a full memory dump of the host. It uploads the dumps to the LimaCharlie artifact ingestion system. It then deletes the local dumps.

You can also make Dumper requests with D&R rules. This example shows a D&R rule action that makes a request to Dumper:

```yaml
- action: extension request
  extension name: ext-dumper
  extension action: request_dump
  extension request:
    target: memory
    sid: <<routing.sid>>
    retention: 30 #default 30
    ignore_cert: true # default false
```

**Notes:**

The dumper extension does not check that the host has enough free disc space for the memory dump. The dumper extension is free, but the memory dumps that you upload to LimaCharlie are subject to external logs pricing. This add-on uses other paid resources (payloads) that are billed based on usage.
