# FAQ - General & Privacy

## Data Security & Infrastructure

### Is my data secure with LimaCharlie?

LimaCharlie data is secured starting at the endpoint all the way through your infrastructure. The LimaCharlie platform is hosted on the Google Cloud Platform, leveraging multiple capabilities from credentials management to compute isolation in order to limit the attack surface.

Data access is managed through Google Cloud IAM which is used to isolate various components and customer data. Processing is done in Google Kubernetes Engine which provides an additional layer of container isolation.

Each LimaCharlie data center uses independent cryptographic keys at all layers. Key management uses industry best practices such as key encryption at rest.

LimaCharlie is SOC 2 Type 2 and PCI-DSS compliant. Our infrastructure is housed in ISO 27001 compliant data centres.

### Where will my data be processed and stored?

The LimaCharlie global infrastructure is built on the Google Cloud Platform (GCP). Currently, computing resources are available in the USA, Canada, Europe, India, and the United Kingdom. New data centers can be spun up anywhere GCP is available upon request.

When you set up an Organization for the first time, you can select the Data Residency Region of your choice:

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/new org.png)

This provides you with the benefit of being able to select which GCP region you want your data in, and have assurance that it will always be processed in this location and never moved outside. This can be important for data residency requirements as it relates to regulatory compliance. For example, if you want to keep all of your information in the US, you can simply select the US region and know that your data will be both processed and stored there.

> **Need to change the Data Residency Region?**
> 
> Please note that once a region has been selected for an organization, it cannot be changed later.

### Can LimaCharlie be deployed on-premises?

LimaCharlie is a cloud-based solution. The LimaCharlie platform is hosted on the Google Cloud Platform (GCP). There are no limits between AWS & GCP but LimaCharlie is not available on premises; if you configure the sensor on the endpoint, it will connect to the cloud.

## Access Control & Privacy

### Can LimaCharlie staff access my data?

LimaCharlie staff only access your private data when you contact us and give us permission to do so. We will always ask for your permission before we access your private telemetry data.

We consider your sensors and telemetry data to be private and confidential. We understand the tremendous power that is being entrusted to us while we have access to this data. We promise to only access your organization for the exclusive purpose of providing you with the assistance you request from us. We treat your private and confidential information with at least the same due care as we do with our own confidential information, as outlined in our privacy policy.

### Will third parties get access to my data?

The only time we provide your data to a third party is with your explicit consent. (e.g. when you set up an Output in LimaCharlie, you're explicitly telling us to send your data to a 3rd party).

### What control measures do you have in place to ensure that my data won't be accessed without proper authorizations?

We use transparency as a mitigating control against insider threats. In particular, when we access your organization data, an entry is made to the audit log in your organization. You can access the audit log in the web interface and via the API. We also provide the ability for you to send audit log data out of LimaCharlie immediately to a write-only bucket that you control in your own environment.

We use a break-glass system, meaning that LimaCharlie personnel do not have access to customer data by default. This requires an explicit programmatic action (internal to LimaCharlie) that includes its own audit trail that cannot be modified by LimaCharlie staff. This audit trail is regularly reviewed.

LimaCharlie staff access to customer data is restricted to only those who need it to perform their official duties.

LimaCharlie staff must explicitly request permission from the customer before granting access to any data or systems (other than in emergency cases where infrastructure is at risk).

We use role-based access control systems to provide granular control over the type of data access granted.

Access to customer organizations is granted programmatically as to provide a security control.

We require that our staff undergo a background check and take training, including privacy training, prior to being allowed to access customer data.

We are SOC 2 (Type 2) compliant and a copy of our audit report can be provided upon request.

## Data Collection & Privacy

### Collection of personally identifiable information (PII)

The LimaCharlie platform focuses on the collection of machine telemetry. This type of telemetry does not generally contain personally identifiable information. The LimaCharlie Sensor does not typically monitor PII-heavy areas such as the contents of email messages or documents. Consequently, manually stripping PII generally is not necessary. Users may choose to ingest their own sources of information. In those cases where LimaCharlie does not have knowledge of the nature of the ingested data, configuration mechanisms are available to users to specify fields they wish to drop or transform in order to better preserve privacy.

We urge users to take a thoughtful approach to the types of data they collect, as they play a crucial role in preserving the privacy of their users. This sense of responsibility is key to maintaining a secure environment.

### Types of data LimaCharlie collects

The LimaCharlie Sensor gathers telemetry from endpoints. The type of data collected is user-configurable and controlled behind role-based access controls. This telemetry contains basic details about endpoints, such as IP address, platform name, OS & package version numbers, IP addresses, etc.

Core sensor telemetry is collected and presented in JSON format.

*Example telemetry:*

```json
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

### Examples of LimaCharlie Sensor Data

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

## Detection & Configuration

### What is detected by LimaCharlie after it's initially installed?

When the Sensor is installed, LimaCharlie will start recording the telemetry. It will not, however, generate detections or take actions to protect the endpoints automatically. As an infrastructure company, we recognize that each environment is different, and one size fits all approach rarely works well. By default, we take the AWS approach - any new organization starts empty, without any pre-configured settings, add-ons, or rules.

### Does LimaCharlie detect variants of the latest malware?

When the sensor is installed, LimaCharlie will start recording telemetry. It will not, however, generate detections or take actions to protect the endpoints automatically. As an infrastructure company, we recognize that each environment is different, and one size fits all approach rarely works well. By default, any new organization starts empty, without any pre-configured settings, add-ons, or D&R rules.

LimaCharlie makes it easy to add a detection & response rule as soon as new variants of malware are discovered. This way, you are in a full control of your coverage and there is no need to wait for a vendor to come up with a new detection rule.

## Performance & Integration

### What latency can I expect in LimaCharlie?

LimaCharlie Detection & Response (D&R) engine has very low latency and you can expect that responses are almost instantaneous (e.g. 100ms).

You may notice some latency as it relates to outputs. Some of our outputs are done in batches, such as Amazon S3, SFTP, Google Cloud Storage. You can configure the maximum size and maximum time for these outputs. We also offer live outputs, such as Syslog.

### How can I integrate LimaCharlie with my existing SIEM?

The most common use case we see is sending detections and events data from LimaCharlie into the SIEM.

To do it, you will need to configure outputs. Here are some examples for configuring outputs to go to an email or to Chronicle.

Remember to select the type of data forwarded by this configuration (stream). The available options are as follows:

* **event**: Contains all events coming back from sensors (not cloud detections). It is very verbose.
* **detect**: Contains all detections reported from D&R rules or subscriptions. This is the option you would choose if you want detections to generate emails (you would also need to ensure that D&R rules are configured to generate detections).
* **audit**: Contains auditing events about activity around the management of the platform in the cloud.
* **deployment**: Contains all "deployment" events like sensor enrollment, cloned sensors etc.
* **artifact**: Contains all "artifact" events of files collected through the Artifact Collection mechanism.

While sending detections and events data from LimaCharlie into the SIEM is the most common way we see our users set up the integration between these two systems, you can also bring in the data into LimaCharlie from SIEM or build other custom workflows. Contact our support team if you need help with your use case or if you have further questions.

### Does LimaCharlie offer reporting capabilities?

It is very common for users to bring different log, network and endpoint data into the LimaCharlie to leverage our detection and response, advanced correlation and storage. If you wish to leverage data visualization capabilities, we make it easy to send the data you need to Splunk, Tableau or any other solution of your choice via public API.

In LimaCharlie web app, you can track information such as detections and events over time and number of sensors online.

![](https://cdn.document360.io/84ec2311-0e05-4c58-90b9-baa9c041d22b/Images/Documentation/dashboard.png)

## Data Retention & Management

### What is the retention policy for management/audit logs?

LimaCharlie stores management/audit logs for one year.

We suggest you set up an [Output](/v2/docs/outputs) to send logs to an external destination if you are looking to have your logs stored for over one year.

## Key Concepts

### Organizations

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

### Sensors

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.