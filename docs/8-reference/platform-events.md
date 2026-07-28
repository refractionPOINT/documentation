# Reference: Platform Events

## Event Details

### ACK_MESSAGES

Some LimaCharlie Sensors use the acknowledge messages event (e.g. USP). The EDR does not use it.

### BACKOFF

Used for flow control. Gives the number of seconds that the Sensor must wait before it sends events to the cloud.

### billing_record

This event is emitted for every kind of billable record in the Organization.

**Sample Event:**

```json
{
  "record": {
    "cat": "extension",
    "k": "ext-strelka:bytes_scanned",
    "oid": "8cbe27f4-aaaa-bbbb-cccc-138cd51389cd",
    "record_id": "3bbbe4d9-925b-4538-bcad-e2e1ba2be923-0",
    "ts": "2024-05-30 00:44:37",
    "v": 2797
  }
}
```

### CLOUD_ADAPTER_DISABLED

This event is emitted when a Cloud Adapter is disabled. A Cloud Adapter is disabled because it gives errors for a long time.

**Sample Event:**

```json
{
  "event":{
    "error": "invalid api key"
  },
  "routing": {
    "event_time": 1644444297696,
    "event_type": "cloud_adapter_disabled",
    "oid": "8cbe27f4-aaaa-cccc-bbbb-138cd51389cd"
  }
}
```

### DATA_DROPPED

The Sensor generates this event when it is offline and the events that it generates overflow its internal buffer. The Sensor drops these events before it can send them to the cloud.

### DELETED_SENSOR

Deleted Sensor deployment events are produced when a sensor tries to connect to the LimaCharlie cloud after it is deleted from an Org.

**Sample Event:**

```json
{
  "routing": {
    "oid": "d9ae5c17-d519-4ef5-a4ac-c454a95d31ca",
    "iid": "ca812425-5a36-4c73-a0a0-935a8ace6451",
    "sid": "a75cc927-bf28-4178-a42d-25ecc8a6be81",
    "plat": 536870912,
    "arch": 2,
    "ext_ip": "104.196.34.101",
    "int_ip": "172.17.0.2",
    "hostname": "linux-server-1",
    "event_type": "deleted_sensor",
    "event_time": 1561741553230
  },
  "event": {
    "denied_for": "720h0m0s"
  }
}
```

### DISCONNECTED

The LimaCharlie cloud generates this platform event when a sensor disconnects from the cloud. The event applies to all sensor types (Windows, macOS, Linux, Chrome, Edge). The cloud generates it on the server side, not on the endpoint.

**Sample Event:**

```json
{
  "routing": {
    "oid": "d9ae5c17-d519-4ef5-a4ac-c454a95d31ca",
    "sid": "a75cc927-bf28-4178-a42d-25ecc8a6be81",
    "event_type": "disconnected",
    "event_time": 1561741553230
  },
  "event": {}
}
```

### ENROLLMENT

Enrollment deployment events are produced when a sensor enrolls into the Organization for the first time.

**Sample Event:**

```json
{
  "routing": {
    "oid": "d9ae5c17-d519-4ef5-a4ac-c454a95d31ca",
    "iid": "ca812425-5a36-4c73-a0a0-935a8ace6451",
    "sid": "a75cc927-bf28-4178-a42d-25ecc8a6be81",
    "plat": 536870912,
    "arch": 2,
    "event_type": "enrollment",
    "event_time": 1561741553230
  },
  "event": {
    "public_ip": "104.196.34.101",
    "internal_ip": "172.17.0.2",
    "host_name": "linux-server-1"
  }
}
```

### EXPORT_COMPLETE

An export of artifact data is complete and ready for download.

**Sample Event:**

```json
{
  "routing" : {
    "log_id" : "ca812425-5a36-4c73-a0a0-935a8ace6451",
    "event_type" : "export_complete",
    "log_type" : "pcap",
    "oid" : "ca812425-5a36-4c73-a0a0-935a8ace6451",
    "event_time" : 1561741553230
  },
  "event" : {
    "size" : 2048,
    "source" : "a75cc927-bf28-4178-a42d-25ecc8a6be81",
    "original_path" : "/data/pcap/dat.pcap",
    "export_id" : "d9ae5c17-d519-4ef5-a4ac-c454a95d31ca"
  }
}
```

### INGEST

A new artifact is ingested.

**Sample Event:**

```json
{
  "routing" : {
    "log_id" : "ca812425-5a36-4c73-a0a0-935a8ace6451",
    "event_type" : "ingest",
    "log_type" : "pcap",
    "oid" : "ca812425-5a36-4c73-a0a0-935a8ace6451",
    "event_time" : 1561741553230
  },
  "event" : {
    "size" : 2048,
    "source" : "a75cc927-bf28-4178-a42d-25ecc8a6be81",
    "original_path" : "/data/pcap/dat.pcap",
    "original_md5" : "adjfnwonefowrnfowef"
  }
}
```

### QUOTA_CHANGED

Quota changed events are emitted when the quota for an Organization changes.

**Sample Event:**

```json
{
  "event":{
    "new_quota": 30,
    "old_quota": 25
  },
  "routing": {
    "event_time": 1644444297696,
    "event_type": "quota_changed",
    "oid": "8cbe27f4-aaaa-cccc-bbbb-138cd51389cd"
  }
}
```

### RUN

Emitted after a run command is issued (e.g. to run a payload, shell command, etc.).

### SELF_TEST_RESULT

Internal event used during a power-on-self-test (POST) of the sensor.

### SENSOR_CLONE

Sensor clone events are generated when the LimaCharlie Cloud detects that a specific Sensor ID is possibly cloned.

**Sample Event:**

```json
{
  "routing": {
    "oid": "d9ae5c17-d519-4ef5-a4ac-c454a95d31ca",
    "iid": "ca812425-5a36-4c73-a0a0-935a8ace6451",
    "sid": "a75cc927-bf28-4178-a42d-25ecc8a6be81",
    "plat": 536870912,
    "arch": 2,
    "event_type": "sensor_clone",
    "event_time": 1561741553230
  },
  "event": {
    "previous_hostname" : "server-1",
    "new_hostname" : "server-2"
  }
}
```

### SENSOR_CRASH

This event is generated when a Sensor crashes. It includes telemetry that helps LimaCharlie troubleshoot the crash.

**Sample Event:**

```json
{
  "routing": {
    "arch": 2,
    "event_time": 1670861698000,
    "event_type": "sensor_crash",
    "hostname": "linux-server-1",
    "ext_ip": "104.196.34.101",
    "int_ip": "172.17.0.2",
    "oid": "8cbe27f4-aaaa-cccc-bbbb-138cd51389cd",
    "plat": 268435456,
    "iid": "ca812425-5a36-4c73-a0a0-935a8ace6451",
    "sid": "a75cc927-bf28-4178-a42d-25ecc8a6be81"
  },
  "event": {
    "crash_context": {
      "FILE_ID": 63,
      "LINE_NUMBER": 1216,
      "THREAD_ID": 7808
    }
  }
}
```

### SENSOR_OVER_QUOTA

Over quota deployment events are produced when a Sensor tries to connect but the Organization quota is already reached.

To read the usage value that enforcement compares against the quota, use `GET https://api.limacharlie.io/v1/quota_usage/{oid}`. This value can be higher than the online sensor count that `GET /v1/online/{oid}` reports. Sensor categories have different weights for the quota, and the online count omits some categories that count toward enforcement. For details, see [the billing FAQ](faq/billing.md#how-do-i-check-my-sensor-quota-usage).

**Sample Event:**

```json
{
  "routing": {
    "oid": "d9ae5c17-d519-4ef5-a4ac-c454a95d31ca",
    "iid": "ca812425-5a36-4c73-a0a0-935a8ace6451",
    "sid": "a75cc927-bf28-4178-a42d-25ecc8a6be81",
    "plat": 536870912,
    "arch": 2,
    "ext_ip": "104.196.34.101",
    "int_ip": "172.17.0.2",
    "hostname": "linux-server-1",
    "event_type": "sensor_over_quota",
    "event_time": 1561741553230
  },
  "event": {
    "public_ip": "104.196.34.101",
    "internal_ip": "172.17.0.2",
    "host_name": "linux-server-1"
  }
}
```

### SET_PERFORMANCE_MODE

Enables performance mode in the kernel (e.g., disables file tracking on Windows).

### SYNC

Internal event used as a heartbeat to the cloud. Sent by default every 10 minutes.

### UNLOAD_KERNEL

Lets you unload the kernel component manually.

### UPDATE

Internal event used to update the configuration of a specific collector within the endpoint.

### *_per_cloud_adapter

Events that are emitted once per period per cloud adapter. See [Schedule Events Reference](schedule-events.md) for more details.

**Sample Event:**

```json
{
  "event": {
    "frequency": 1800,
    "adapter_name": "office-audit",
    "runtime_mtd": {
      "entity_name": "81c72a07-9540-4341-9c35-66f6cfe1b9d7",
      "entity_type": "adapter",
      "mtd": {
        "platform": "office365",
        "hostname": "office-365-audit",
        "adapter_type": "office365"
      },
      "published_at": 1689858693935
    }
  }
}
```

### *_per_org

Events that are emitted once per period per org. See [Schedule Events Reference](schedule-events.md) for more details.

**Sample Event:**

```json
{
  "event": {
    "frequency": 86400
  },
  "routing": {
    "event_id": "0f236fbb-31df-4d11-b6ab-c6b71a63a072",
    "event_time": 1673298756512,
    "event_type": "1h_per_org",
    "oid": "8cbe27f4-bfa1-4afb-ba19-138cd51389cd",
    "sid": "00000000-0000-0000-0000-000000000000",
    "tags": []
  }
}
```

### *_per_sensor

Events that are emitted once per period per Sensor. See [Schedule Events Reference](schedule-events.md) for more details.

**Sample Event:**

```json
{
  "event": {
    "frequency": 1800,
    "runtime_mtd": {
      "entity_name": "81c72a07-9540-4341-9c35-66f6cfe1b9d7",
      "entity_type": "sensor",
      "mtd": {
        "bytes_recv": 6202524,
        "conn_at": 1689819872,
        "eps_in": 1,
        "eps_out": 0,
        "q_size": 0
      },
      "published_at": 1689858693935
    }
  }
}
```

Sensors send telemetry to the LimaCharlie platform as EDR telemetry or as forwarded logs. Sensors are a scalable, serverless solution that connects the endpoints of an organization to the cloud securely.

Endpoint Detection & Response

In LimaCharlie, an Organization is a tenant in the Agentic SecOps Workspace. It is a self-contained environment where you manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, and gives complete control over security operations. This structure supports multi-tenant setups for managed security providers, and for enterprises that manage many departments or clients.

Adapters ingest data from on-premise environments and from cloud environments.

In LimaCharlie, a Sensor ID is a unique identifier for each deployed sensor. It separates individual sensors across the infrastructure of an organization, and lets LimaCharlie track, manage, and communicate with each endpoint. The Sensor ID is critical when LimaCharlie sends commands, collects telemetry, and monitors activity. It links actions and data to a specific device or endpoint.
