# Sysmon Comparison

System Monitor, or "Sysmon", is a Windows server and device driver that monitors and logs operating system activity. It is part of the Sysinternals toolkit. More information on Sysmon can be found [here](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon).

Many organizations deploy Sysmon and structure their detection events around Sysmon-specific event logs, which can offer granular insight into operating system changes. LimaCharlie's EDR telemetry can offer similar events, allowing you to write detections against these events directly.

A comparison of LimaCharlie vs. Sysmon is as follows:

| Sysmon Event | LimaCharlie Event |
| --- | --- |
| Event ID 1 (Process Creation) | NEW\_PROCESS |
| Event ID 3 (Network Connection) | NEW\_\*\_CONNECTION |
| Event ID 5 (Process terminated) | TERMINATE\_PROCESS |
| Event ID 6 (Driver Loaded) | MODULE\_LOAD, CODE\_IDENTITY, DRIVER\_CHANGE |
| Event ID 7 (Image loaded) | MODULE\_LOAD, CODE\_IDENTITY |
| Event ID 8 (Create remote thread) | NEW\_REMOTE\_THREAD |
| Event ID 10 (ProcessAccess) | REMOTE\_PROCESS\_HANDLE |
| Event ID 11 (FileCreate) | FILE\_CREATE |
| Event ID 12 (RegistryEvent object create and delete) | REGISTRY\_CREATE, REGISTRY\_DELETE |
| Event ID 13 (RegisterEvent value set) | REGISTRY\_WRITE |
| Event ID 14 (RegistryEvent rename) | REGISTRY\_CREATE |
| Event ID 17 (PipeEvent Created) | NEW\_NAMED\_PIPE |
| Event ID 18 (PipeEvent Connected) | OPEN\_NAMED\_PIPE |

Why not both? ¯\*(ツ)*/¯

Note, LC's Endpoint Agent is easily able to [consume Sysmon events](../../Sensors/Endpoint_Agent/Tutorials/ingesting-sysmon-event-logs.md) as well.

## Executable Tracking

Recent updates to Sysmon also include the ability to capture and store information about binaries identified on a system. You can replicate this functionality with LimaCharlie with BinLib. More information on that can be found [here](../../Add-Ons/Extensions/LimaCharlie_Extensions/binlib.md).
