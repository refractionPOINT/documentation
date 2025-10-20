# FAQ - Privacy

LimaCharlie is a highly configurable security infrastructure-as-a-service platform. It allows users to control which data they ingest into the platform from various locations, including endpoints and cloud services.

## Collection of personally identifiable information (PII)

The LimaCharlie platform focuses on the collection of machine telemetry. This type of telemetry does not generally contain personally identifiable information. The LimaCharlie Sensor does not typically monitor PII-heavy areas such as the contents of email messages or documents. Consequently, manually stripping PII generally is not necessary. Users may choose to ingest their own sources of information. In those cases where LimaCharlie does not have knowledge of the nature of the ingested data, configuration mechanisms are available to users to specify fields they wish to drop or transform in order to better preserve privacy.

We urge users to take a thoughtful approach to the types of data they collect, as they play a crucial role in preserving the privacy of their users. This sense of responsibility is key to maintaining a secure environment.

## Types of data LimaCharlie collects

The LimaCharlie Sensor gathers telemetry from endpoints. The type of data collected is user-configurable and controlled behind role-based access controls. This telemetry contains basic details about endpoints, such as IP address, platform name, OS & package version numbers, IP addresses, etc.

Core sensor telemetry is collected and presented in JSON format.

*Example telemetry:*

```
{
  "event": {
    "COMMAND_LINE": "C:\\WINDOWS\\system32\\svchost.exe -k NetworkService -p",
    "CREATION_TIME": 1726927583937,
    "FILE_IS_SIGNED": 1,
    "FILE_PATH": "C:\\WINDOWS\\system32\\svchost.exe",
    "HASH": "0ad27dc6b692903c4e129b1ad75ee8188da4b9ce34c309fed34a25fe86fb176d",
    "NETWORK_ACTIVITY": [
      {
        "DESTINATION": {
          "IP_ADDRESS": "ff02::fb",
          "PORT": 5353
        },
        "IS_OUTGOING": 1,
        "PROTOCOL": "udp6",
        "SOURCE": {
          "IP_ADDRESS": "fe80::77d6:f691:a738:9c7d",
          "PORT": 5353
        },
        "TIMESTAMP": 1727414615732
      },
      {
        "DESTINATION": {
          "IP_ADDRESS": "192.168.3.1",
          "PORT": 53
        },
        "IS_OUTGOING": 1,
        "PROTOCOL": "udp4",
        "SOURCE": {
          "IP_ADDRESS": "192.168.3.40",
          "PORT": 62283
        },
        "TIMESTAMP": 1727414631067
      }
    ],
    "PARENT_PROCESS_ID": 888,
    "PROCESS_ID": 2384,
    "USER_NAME": "NT AUTHORITY\\NETWORK SERVICE"
  },
  "routing": {
    "arch": 2,
    "did": "",
    "event_id": "68ff82ba-c580-4a19-990e-4455effb7255",
    "event_time": 1727414635585,
    "event_type": "NETWORK_CONNECTIONS",
    "ext_ip": "172.16.162.191",
    "hostname": "workstation",
    "iid": "c4cd7ab1-630d-40b4-b46c-2b817183117d",
    "int_ip": "192.168.3.40",
    "moduleid": 2,
    "oid": "e946c975-2f02-4044-be5f-945b9c43d061",
    "parent": "55f56dc5e19c460042d8179f66eed2f2",
    "plat": 268435456,
    "sid": "a8f8ca97-8614-438d-qb26-19100e8c90e3",
    "tags": [
      "workstations"
    ],
    "this": "4fef24a89ce77af24365721066f6416b"
  },
  "ts": "2024-09-27 05:23:55"
}
```

By default, the following types of telemetry are collected on Windows-based systems:

AUTORUN_CHANGE
 CODE_IDENTITY
 CONNECTED
 DIR_FINDHASH_REP
 DIR_LIST_REP
 DNS_REQUEST
 DRIVER_CHANGE
 EXEC_OOB
 EXISTING_PROCESS
 FILE_DEL_REP
 FILE_GET_REP
 FILELHASHLREP
 FILE_INFO_REP
 FILE_MOV_REP
 FILE_TYPE_ACCESSED
 FIM_HIT
 FIM_LIST_REP
 GET_DOCUMENT_REP
 GET_EXFIL_EVENT_REP
 HIDDEN_MODULE_DETECTED
 HISTORY_DUMP_REP
 LOG_GET_REP
 LOG_LIST_REP
 MEM_FIND_HANDLE_REP
 MEM_FIND_STRING_REP
 MEM_HANDLES_REP
 MEM_MAP_REP
 MEM_READ_REP
 MEM_STRINGS_REP
 MODULE_MEM_DISK_MISMATCH
 NETSTAT_REP
 NETWORK_CONNECTIONS
 NEW_DOCUMENT
 NEW_PROCESS
 OS_AUTORUNS_REP
 OS_DRIVERS_REP
 OS_KILL_PROCESS_REP
 OS_PACKAGES_REP
 0S_PROCESSES_REP
 0S_RESUME_REP
 OS_SERVICES_REP
 OS_SUSPEND_REP
 OS_USERS_REP
 OS_VERSION_REP
 POSSIBLE_DOC_EXPLOIT
 RECEIPT
 RECON_BURST
 REGISTRY_LIST_REP
 SELF_TEST_RESULT
 SENSITIVE_PROCESS_ACCESS
 SERVICE_CHANGE
 TERMINATE_PROCESS
 THREAD_INJECTION
 USER_OBSERVED
 VOLUME_MOUNT
 VOLUME_UNMOUNT
 WEL
 YARA_DETECTION

Users can opt in / out of collection of event types on a per-platform basis. The default list varies based on OS platform and may change over time. For a full list of events, along with descriptions and samples, please see [Events](/v2/docs/events).

## Examples of LimaCharlie Sensor Data

1. Sensor Overview
   ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-01.png)
2. Artifacts
   ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-03.png)
3. Autoruns
   ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-04.png)
4. Console
   ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-05.png)
5. Detections
   ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-06a.png)
6. Drivers
   ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-07.png)
7. File System
   ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-08.png)
8. File Integrity Monitoring
   ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-09(1).png)
9. Network Connections
   ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-10.png)
10. Packages
    ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-11.png)
11. Processes
    ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-12.png)
12. Services
    ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-13.png)
13. Timeline with Event Details
    ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-14.png)
14. Users
    ![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/sensor-15.png)

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.
