# Payloads

## Overview

Payloads are executables or scripts that LimaCharlie's Endpoint Agent delivers and runs.

A payload can be any executable or script that the endpoint understands. Use a payload to run a function that LimaCharlie does not supply. Examples are custom executables from another vendor that clean a machine, forensic utilities, and firmware utilities.

Look at the native LimaCharlie functions first. They have these advantages:

- Performance is usually better.
- The data that they return is always well structured JSON.
- You can task them automatically, and you can create [Detection & Response Rules](../../3-detection-response/index.md) from their data.
- The data that they return is indexed and searchable.

To set the file extension of the Payload on the endpoint, end the Payload name with that extension. For example, if you name a Payload `extract_everything.bat`, LimaCharlie sends it as a batch file (`.bat`) and runs it as one. This also applies to PowerShell files (`.ps1`).

## Lifecycle

You upload Payloads to the LimaCharlie cloud and give each one a name. Then use the `run` task with `--payload-name MY-PAYLOAD --arguments "-v EulaAccepted"` to run the payload with optional arguments.

A related `RECEIPT` event returns the STDOUT and STDERR data, up to 1 MB. If your payload makes more data, send the data to a file on disk. Then use the `log_get` command to get the file.

The endpoint agent gets the payload over HTTPS from the Ingestion API DNS endpoint. If you must allow this DNS entry, find it in the Sensor Download section of the web app.

## Upload / Download via REST

LimaCharlie creates and gets Payloads asynchronously. The REST APIs return signed URLs, not the Payload. To get an existing payload, do an HTTP GET on the returned URL. To create a Payload, do an HTTP PUT on the returned URL:

```bash
curl -X PUT "THE-SIGNED-URL-HERE" -H "Content-Type: application/octet-stream" --upload-file your-file.exe
```

The signed URLs are valid for a few minutes only.

## Permissions

Two permissions manage Payloads:

- `payload.ctrl` lets you create and delete payloads.
- `payload.use` lets you run a payload.
