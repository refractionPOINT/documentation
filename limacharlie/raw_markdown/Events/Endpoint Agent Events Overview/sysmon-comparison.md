System Monitor, or "Sysmon", is a Windows server and device driver that monitors and logs operating system activity. It is part of the Sysinternals toolkit. More information on Sysmon can be found [here](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon).

Many organizations deploy Sysmon and structure their detection events around Sysmon-specific event logs, which can offer granular insight into operating system changes. LimaCharlie's EDR telemetry can offer similar events, allowing you to write detections against these events directly.

A comparison of LimaCharlie vs. Sysmon is as follows:

Sysmon Event| LimaCharlie Event  
---|---  
Event ID 1 (Process Creation)| NEW_PROCESS  
Event ID 3 (Network Connection)| NEW_*_CONNECTION  
Event ID 5 (Process terminated)| TERMINATE_PROCESS  
Event ID 6 (Driver Loaded)| MODULE_LOAD, CODE_IDENTITY, DRIVER_CHANGE  
Event ID 7 (Image loaded)| MODULE_LOAD, CODE_IDENTITY  
Event ID 8 (Create remote thread)| NEW_REMOTE_THREAD  
Event ID 10 (ProcessAccess)| REMOTE_PROCESS_HANDLE  
Event ID 11 (FileCreate)| FILE_CREATE  
Event ID 12 (RegistryEvent object create and delete)| REGISTRY_CREATE, REGISTRY_DELETE  
Event ID 13 (RegisterEvent value set)| REGISTRY_WRITE  
Event ID 14 (RegistryEvent rename)| REGISTRY_CREATE  
Event ID 17 (PipeEvent Created)| NEW_NAMED_PIPE  
Event ID 18 (PipeEvent Connected)| OPEN_NAMED_PIPE  
  
Why not both? ¯\_(ツ)_ /¯

Note, LC's Endpoint Agent is easily able to [consume Sysmon events](/v2/docs/ingesting-sysmon-event-logs) as well.

## Executable Tracking

Recent updates to Sysmon also include the ability to capture and store information about binaries identified on a system. You can replicate this functionality with LimaCharlie with BinLib. More information on that can be found [here](/v2/docs/binlib).

