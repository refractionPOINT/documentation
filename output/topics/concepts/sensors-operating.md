# macOS

LimaCharlie's Mac sensor interfaces with the kernel to acquire deep visibility into the host's activity while taking measures to preserve the host's performance. The Mac sensor currently supports all versions of MacOS 10.7 and up.

## Installation Instructions

Basic sensor installation instructions can be found [here](/v1/docs/sensor-installation).

Looking for alternative installation methods?

* macOS Sensor Installation - [Latest OS Versions](/v1/docs/macos-sensor-installation-latest-os-versions)
* macOS Sensor Installation - [Older OS Versions](/v1/docs/macos-sensor-installation-older-versions)
* macOS Sensor Installation - [MDM Configuration profiles](/v1/docs/macos-sensor-installation-mdm-configuration-profiles)

## Supported Events

* [`AUTORUN_CHANGE`](../reference/reference-events.md)
* [`CLOUD_NOTIFICATION`](../reference/reference-events.md)
* [`CODE_IDENTITY`](../reference/reference-events.md)
* [`CONNECTED`](../reference/reference-events.md)
* [`DATA_DROPPED`](../reference/reference-events.md)
* [`DNS_REQUEST`](../reference/reference-events.md)
* [`EXEC_OOB`](../reference/reference-events.md)
* [`FILE_CREATE`](../reference/reference-events.md)
* [`FILE_DELETE`](../reference/reference-events.md)
* [`FILE_MODIFIED`](../reference/reference-events.md)
* [`FILE_TYPE_ACCESSED`](../reference/reference-events.md)
* [`FIM_HIT`](../reference/reference-events.md)
* [`HIDDEN_MODULE_DETECTED`](../reference/reference-events.md)
* [`MODULE_LOAD`](../reference/reference-events.md) -- *temporarily disabled*
* [`MODULE_MEM_DISK_MISMATCH`](../reference/reference-events.md)
* [`NETWORK_CONNECTIONS`](../reference/reference-events.md)
* [`NETWORK_SUMMARY`](../reference/reference-events.md)
* [`NEW_DOCUMENT`](../reference/reference-events.md)
* [`NEW_PROCESS`](../reference/reference-events.md)
* [`NEW_TCP4_CONNECTION`](../reference/reference-events.md)
* [`NEW_UDP4_CONNECTION`](../reference/reference-events.md)
* [`NEW_TCP6_CONNECTION`](../reference/reference-events.md)
* [`NEW_UDP6_CONNECTION`](../reference/reference-events.md)
* [`RECEIPT`](../reference/reference-events.md)
* [`SERVICE_CHANGE`](../reference/reference-events.md)
* [`SHUTTING_DOWN`](../reference/reference-events.md)
* `SSH_LOGIN`
* `SSH_LOGOUT`
* [`STARTING_UP`](../reference/reference-events.md)
* [`TERMINATE_PROCESS`](../reference/reference-events.md)
* [`TERMINATE_TCP4_CONNECTION`](../reference/reference-events.md)
* [`TERMINATE_UDP4_CONNECTION`](../reference/reference-events.md)
* [`TERMINATE_TCP6_CONNECTION`](../reference/reference-events.md)
* [`TERMINATE_UDP6_CONNECTION`](../reference/reference-events.md)
* `USER_LOGIN`
* `USER_LOGOUT`
* [`USER_OBSERVED`](../reference/reference-events.md)
* [`VOLUME_MOUNT`](../reference/reference-events.md)
* [`VOLUME_UNMOUNT`](../reference/reference-events.md)
* [`YARA_DETECTION`](../reference/reference-events.md)

## Supported Commands

* [`artifact_get`](/v1/docs/reference-sensor-commands#artifact_get)
* [`deny_tree`](/v1/docs/reference-sensor-commands#deny_tree)
* [`dir_find_hash`](/v1/docs/reference-sensor-commands#dir_find_hash)
* [`dir_list`](/v1/docs/reference-sensor-commands#dir_list)
* [`dns_resolve`](/v1/docs/reference-sensor-commands#dns_resolve)
* [`doc_cache_get`](/v1/docs/reference-sensor-commands#doc_cache_get)
* [`exfil_add`](/v1/docs/reference-sensor-commands#exfil_add)
* [`exfil_del`](/v1/docs/reference-sensor-commands#exfil_del)
* [`exfil_get`](/v1/docs/reference-sensor-commands#exfil_get)
* [`file_del`](/v1/docs/reference-sensor-commands#file_del)
* [`file_get`](/v1/docs/reference-sensor-commands#file_get)
* [`file_hash`](/v1/docs/reference-sensor-commands#file_hash)
* [`file_info`](/v1/docs/reference-sensor-commands#file_info)
* [`file_mov`](/v1/docs/reference-sensor-commands#file_mov)
* [`fim_add`](/v1/docs/reference-sensor-commands#fim_add)
* [`fim_del`](/v1/docs/reference-sensor-commands#fim_del)
* [`fim_get`](/v1/docs/reference-sensor-commands#fim_get)
* [`hidden_module_scan`](/v1/docs/reference-sensor-commands#hidden_module_scan)
* [`history_dump`](/v1/docs/reference-sensor-commands#history_dump)
* [`mem_find_handle`](/v1/docs/reference-sensor-commands#mem_find_handle)
* [`mem_find_string`](/v1/docs/reference-sensor-commands#mem_find_string)
* [`mem_handles`](/v1/docs/reference-sensor-commands#mem_handles)
* [`mem_map`](/v1/docs/reference-sensor-commands#mem_map)
* [`mem_read`](/v1/docs/reference-sensor-commands#mem_read)
* [`mem_strings`](/v1/docs/reference-sensor-commands#mem_strings)
* [`netstat`](/v1/docs/reference-sensor-commands#netstat)
* [`os_autoruns`](/v1/docs/reference-sensor-commands#os_autoruns)
* [`os_kill_process`](/v1/docs/reference-sensor-commands#os_kill_process)
* [`os_processes`](/v1/docs/reference-sensor-commands#os_processes)
* [`os_resume`](/v1/docs/reference-sensor-commands#os_resume)
* [`os_services`](/v1/docs/reference-sensor-commands#os_services)
* [`os_suspend`](/v1/docs/reference-sensor-commands#os_suspend)
* [`os_version`](/v1/docs/reference-sensor-commands#os_version)
* [`put`](/v1/docs/reference-sensor-commands#put)
* [`reg_list`](/v1/docs/reference-sensor-commands#reg_list)
* [`rejoin_network`](/v1/docs/reference-sensor-commands#rejoin_network)
* [`restart`](/v1/docs/reference-sensor-commands#restart)
* [`run`](/v1/docs/reference-sensor-commands#run)
* [`segregate_network`](/v1/docs/reference-sensor-commands#segregate_network)
* [`set_performance_mode`](/v1/docs/reference-sensor-commands#set_performance_mode)
* [`uninstall`](/v1/docs/reference-sensor-commands#uninstall)
* [`yara_scan`](/v1/docs/reference-sensor-commands#yara_scan)
* [`yara_update`](/v1/docs/reference-sensor-commands#yara_update)

## Artifacts

Given configured paths to collect from, the Mac sensor can batch upload logs / artifacts directly from the host.

Learn more about collecting Artifacts [here](artifacts.md).

## Payloads

For more complex needs not supported by [Events](/v1/docs/detecting-related-events), [Artifacts](artifacts.md), or [Commands](/v1/docs/sensor-commands), it's possible to execute payloads on hosts via the Mac sensor.

Learn more about executing Payloads [here](../reference/payloads.md).