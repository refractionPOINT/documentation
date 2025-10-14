# Sensor Commands

Sensor commands offer a safe way to interact with a sensor's host either for investigation, management, or threat mitigation purposes. Commands are categorized by their overall functionality, and include the following:

* [Artifact Collection](/v1/docs/sensor-commands-artifact-collection)
  + `artifact_get`
* [Anomalies](../reference/sensor-commands-anomalies.md)
  + `hidden_module_scan`
* [Documents](../reference/sensor-commands-documents.md)
  + `doc_cache_get`
* [File and Registry Integrity Monitoring](/v1/docs/sensor-commands-fim)
  + `fim_add`
  + `fim_del`
  + `fim_get`
* [Files and Directories](/v1/docs/sensor-commands-files-and-directories)
  + `dir_find_hash`
  + `dir_list`
  + `file_del`
  + `file_get`
  + `file_hash`
  + `file_info`
  + `file_mov`
  + `log_get`
* [Management](/v1/docs/sensor-commands-management)
  + `exfil_add`
  + `exfil_del`
  + `exfil_get`
  + `history_dump`
  + `seal`
  + `set_performance_mode`
  + `restart`
  + `uninstall`
* [Memory](../reference/sensor-commands-memory.md)
  + `get_debug_data`
  + `mem_find_handle`
  + `mem_find_string`
  + `mem_handles`
  + `mem_map`
  + `mem_read`
  + `mem_strings`
* [Mitigation](../reference/sensor-commands-mitigation.md)
  + `deny_tree`
  + `rejoin_network`
  + `segregate_network`
* [Network](/v1/docs/sensor-commands-network)
  + `dns_resolve`
  + `netstat`
  + `pcap_ifaces`
* [Operating System](/v1/docs/sensor-commands-operating-system)
  + `os_autoruns`
  + `os_drivers`
  + `os_kill_process`
  + `os_packages`
  + `os_processes`
  + `os_resume`
  + `os_services`
  + `os_suspend`
  + `os_users`
* [Payloads](/v1/docs/sensor-commands-payloads)
  + `run`
  + `put`
* [Registry](../reference/sensor-commands-registry.md)
  + `reg_list`
* [System](/v1/docs/sensor-commands-system)
  + `logoff`
  + `reboot`
  + `shutdown`
* [YARA](/v1/docs/sensor-commands-yara)
  + `yara_scan`
  + `yara_update`

## Sending Commands

Commands can be sent to Sensors via:

* Manually using the Console of a sensor in the [web application](https://app.limacharlie.io).
* Manually using the [CLI](https://github.com/refractionPOINT/python-limacharlie)
* Programatically in the response action of a [Detection & Response](/v1/docs/detection-and-response) rule, via the `task` action.
* Programatically using the [REST API](https://doc.limacharlie.io/docs/api/b3A6MTk2NDI0OQ-task-sensor)

### Sensor Response Events

Regardless of which you choose, sent commands will be acknowledged immediately with an empty response, followed by a `CLOUD_NOTIFICATION` event being sent by the sensor. The content of command outputs are delivered as sensor [events](/v1/docs/reference-events-responses) suffixed with `_REP`, depending on the command.

**Please ensure that you have enabled the appropriate response event(s) in Event Collection to ensure that you will receive the Sensor response.**

This non-blocking approach makes responses accessible via the [event streams](sensors.md) passing through Detection & Response rules and Outputs.

## Structure

Commands follow typical CLI conventions using a mix of positional arguments and named optional arguments.

Here's `dir_list` as an example:

```
dir_list [-h] [-d DEPTH] rootDir fileExp

positional arguments:
    rootDir     the root directory where to begin the listing from
    fileExp     a file name expression supporting basic wildcards like * and ?

optional arguments:
    -h, --help      show this help message and exit
    -d DEPTH, --depth DEPTH     optional maximum depth of the listing, defaults to a single level
```

The Console in the web application will provide autocompletion hints of possible commands for a sensor and their parameters. For API users, commands and their usage details may be retrieved via the [`/tasks`](https://doc.limacharlie.io/docs/api/b3A6MTk2NDI1OQ-get-possible-tasks) and [`/task`](https://doc.limacharlie.io/docs/api/b3A6MTk2NDI3OA-autocomplete-task) REST API endpoints.

## Investigation IDs

To assist in finding the responses more easily, you may specify an arbitrary `investigation_id` string with a command. The response will then include that value under `routing/investigation_id`. Under the hood, this is exactly how the Console view in the web application works.

If an `investigation_id` is prefixed with `__` (double underscore) it will omit the resulting events from being forwarded to Outputs. This is primarily to allow Services to interact with sensors without spamming.

## Command Line Format

When issuing commands to sensors as a command line (versus a list of tokens), the quoting and escaping of arguments can be confusing. This is a short explanation:

The command line tasks are parsed as if they were issued to a shell like `sh` or `cmd.exe` with a few tweaks to make it easier and more intuitive to use.

Arguments are parsed as separated by spaces, like: `dir_list /home/user *` is equal to 2 arguments: `/home/user` and `*`.

If an argument contains spaces, for example a single directory like `/file/my files`, you must use either single (`'`) or double (`"`) quotes around the argument, like: `dir_list "/files/my files"`.

A backslash (`\`), like in Windows file paths does not need to be escaped. It is only interpreted as an escape character when it is followed by a single or double quote.

The difference between single quotes and double quotes is that double quotes support escaping characters within using `\`, while single quotes never interpret `\` as an escape character. For example:

* `log_get --file "c:\temp\my dir\" --type json` becomes `log_get`, `--file`, `c:\temp\my dir\`, `--type`, `json`
* `log_get --file 'c:\temp\my dir\' --type json` becomes `log_get`, `--file`, `c:\temp\my dir\`, `--type`, `json`
* `log_get --file 'c:\temp\my dir\' --type json` becomes `log_get`, `--file`, `c:\temp\my dir\`, `--type`, `json`
* `log_get --file "c:\temp\my dir\" --type json` becomes `log_get`, `--file`, `c:\temp\my dir\`, `--type`, `json`

This means that as a general statement, unless you want to embed quoted strings within specific arguments, it is easier to use single quotes around arguments and not worry about escaping `\`.