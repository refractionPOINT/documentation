---

Sysmon Comparison

* 12 Nov 2024
* 1 Minute to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Sysmon Comparison

* Updated on 12 Nov 2024
* 1 Minute to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

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

Note, LC's Endpoint Agent is easily able to [consume Sysmon events](/v2/docs/ingesting-sysmon-event-logs) as well.

## Executable Tracking

Recent updates to Sysmon also include the ability to capture and store information about binaries identified on a system. You can replicate this functionality with LimaCharlie with BinLib. More information on that can be found [here](/v2/docs/binlib).

Endpoint Detection & Response

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

---

Thank you for your feedback! Our team will get back to you

Your feedback

Need more information

Difficult to understand

Inaccurate or irrelevant content

Missing/broken link

Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

Notify me about change

Please enter a valid email

Cancel

---

###### Related articles

* [Ingesting Sysmon Event Logs](/docs/ingesting-sysmon-event-logs)
* [Reference: EDR Events](/docs/reference-edr-events)

---

###### What's Next

* [Reference: EDR Events](/docs/reference-edr-events)

Table of contents

+ [Executable Tracking](#executable-tracking)

Tags

* [detection and response](/docs/en/tags/detection%20and%20response)
* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [events](/docs/en/tags/events)
* [telemetry](/docs/en/tags/telemetry)
* [windows](/docs/en/tags/windows)
