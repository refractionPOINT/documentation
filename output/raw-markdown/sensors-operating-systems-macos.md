[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v1

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Telemetry](telemetry-sensors)
* [Detection and Response](detecting-related-events)
* [Platform Management](platform-configuration-limacharlie-sdk)
* [Outputs](output-whitelisting)
* [Add-Ons](developer-grant-program)
* [FAQ](faq-privacy)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

macOS

* 13 Aug 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

This documentation version is deprecated, please click here for the latest version.

# macOS

* Updated on 13 Aug 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

LimaCharlie's Mac sensor interfaces with the kernel to acquire deep visibility into the host's activity while taking measures to preverse the host's performance. The Mac sensor currently supports all versions of MacOS 10.7 and up.

## Installation Instructions

Basic sensor installation instructions can be found [here](/v1/docs/sensor-installation).

Looking for alternative installation methods?

* macOS Sensor Installation - [Latest OS Versions](/v1/docs/macos-sensor-installation-latest-os-versions)
* macOS Sensor Installation - [Older OS Versions](/v1/docs/macos-sensor-installation-older-versions)
* macOS Sensor Installation - [MDM Configuration profiles](/v1/docs/macos-sensor-installation-mdm-configuration-profiles)

## Supported Events

* [`AUTORUN_CHANGE`](/v1/docs/reference-events#autorun_change)
* [`CLOUD_NOTIFICATION`](/v1/docs/reference-events#cloud_notification)
* [`CODE_IDENTITY`](/v1/docs/reference-events#code_identity)
* [`CONNECTED`](/v1/docs/reference-events#connected)
* [`DATA_DROPPED`](/v1/docs/reference-events#data_dropped)
* [`DNS_REQUEST`](/v1/docs/reference-events#dns_request)
* [`EXEC_OOB`](/v1/docs/reference-events#exec_oob)
* [`FILE_CREATE`](/v1/docs/reference-events#file_create)
* [`FILE_DELETE`](/v1/docs/reference-events#file_delete)
* [`FILE_MODIFIED`](/v1/docs/reference-events#file_modified)
* [`FILE_TYPE_ACCESSED`](/v1/docs/reference-events#file_type_accessed)
* [`FIM_HIT`](/v1/docs/reference-events#fim_hit)
* [`HIDDEN_MODULE_DETECTED`](/v1/docs/reference-events#hidden_module_detected)
* [`MODULE_LOAD`](/v1/docs/reference-events#module_load) -- *temporarily disabled*
* [`MODULE_MEM_DISK_MISMATCH`](/v1/docs/reference-events#module_mem_disk_mismatch)
* [`NETWORK_CONNECTIONS`](/v1/docs/reference-events#network_connections)
* [`NETWORK_SUMMARY`](/v1/docs/reference-events#network_summary)
* [`NEW_DOCUMENT`](/v1/docs/reference-events#new_document)
* [`NEW_PROCESS`](/v1/docs/reference-events#new_process)
* [`NEW_TCP4_CONNECTION`](/v1/docs/reference-events#new_tcp4_connection)
* [`NEW_UDP4_CONNECTION`](/v1/docs/reference-events#new_udp4_connection)
* [`NEW_TCP6_CONNECTION`](/v1/docs/reference-events#new_tcp6_connection)
* [`NEW_UDP6_CONNECTION`](/v1/docs/reference-events#new_udp6_connection)
* [`RECEIPT`](/v1/docs/reference-events#receipt)
* [`SERVICE_CHANGE`](/v1/docs/reference-events#service_change)
* [`SHUTTING_DOWN`](/v1/docs/reference-events#shutting_down)
* `SSH_LOGIN`
* `SSH_LOGOUT`
* [`STARTING_UP`](/v1/docs/reference-events#starting_up)
* [`TERMINATE_PROCESS`](/v1/docs/reference-events#terminate_process)
* [`TERMINATE_TCP4_CONNECTION`](/v1/docs/reference-events#terminate_tcp4_connection)
* [`TERMINATE_UDP4_CONNECTION`](/v1/docs/reference-events#terminate_udp4_connection)
* [`TERMINATE_TCP6_CONNECTION`](/v1/docs/reference-events#terminate_tcp6_connection)
* [`TERMINATE_UDP6_CONNECTION`](/v1/docs/reference-events#terminate_udp6_connection)
* `USER_LOGIN`
* `USER_LOGOUT`
* [`USER_OBSERVED`](/v1/docs/reference-events#user_observed)
* [`VOLUME_MOUNT`](/v1/docs/reference-events#volume_mount)
* [`VOLUME_UNMOUNT`](/v1/docs/reference-events#volume_unmount)
* [`YARA_DETECTION`](/v1/docs/reference-events#yara_detection)

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

Learn more about collecting Artifacts [here](/v1/docs/artifacts).

## Payloads

For more complex needs not supported by [Events](/v1/docs/detecting-related-events), [Artifacts](/v1/docs/artifacts), or [Commands](/v1/docs/sensor-commands), it's possible to execute payloads on hosts via the Mac sensor.

Learn more about executing Payloads [here](/v1/docs/payloads).

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### What's Next

* [macOS Sensor Installation - Latest OS Versions](/v1/docs/macos-sensor-installation-latest-os-versions)

Table of contents

+ [Installation Instructions](#installation-instructions)
+ [Supported Events](#supported-events)
+ [Supported Commands](#supported-commands)
+ [Artifacts](#artifacts)
+ [Payloads](#payloads)
