# EVTX

## Overview

This Adapter allows you to ingest and convert a `.evtx` file into LimaCharlie. The `.evtx` files are the binary format used by Microsoft for Windows Event Logs. This is useful to ingest historical Windows Event Logs, for example during an Incident Response (IR) engagement.

For real-time collection of Windows Event Logs, see the [Windows Event Logs](../../Tutorials/ingesting-windows-event-logs.md) documentation.

## Configurations

Adapter Type: `evtx`

  * `client_options`: common configuration for adapter as defined [here](../../adapters.md#usage).

  * `file_path`: path to the `.evtx` file to ingest.




## API Doc

See the [unofficial documentation on EVTX](https://www.giac.org/paper/gcia/2999/evtx-windows-event-logging/115806).
