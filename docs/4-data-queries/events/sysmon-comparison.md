# Sysmon Comparison

System Monitor, or "Sysmon", is a Windows server and device driver that monitors and logs operating system activity. It is part of the Sysinternals toolkit. See Microsoft's [Sysmon download and reference page](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon).

Many organizations deploy Sysmon and build their detection events around Sysmon event logs. These logs give detailed information about changes to the operating system. The EDR telemetry of LimaCharlie gives similar events, and you can write detections against these events directly.

The table below compares Sysmon events to LimaCharlie events:

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

You can also use both.

The LimaCharlie sensor can also [consume Sysmon events](../../2-sensors-deployment/tutorials/sysmon-logs.md).

## Executable Tracking

Recent updates to Sysmon can also capture and store information about binaries found on a system. You can do the same in LimaCharlie with the [BinLib extension](../../5-integrations/extensions/limacharlie/binlib.md).
