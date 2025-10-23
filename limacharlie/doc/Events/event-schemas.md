# Event Schemas

Since LimaCharlie standardizes on JSON, including arbitrary sources of data, it means that Schema in LimaCharlie is generally dynamic.

To enable users to create schemas in external systems that expect more strictly typed data, LimaCharlie makes a Schema API available.

This Schema API exposes the "learned" schema from specific event types. As data comes into LimaCharlie, the Schema API will accumulate the list of fields and types observed for those specific events. In turn, the API allows you to retrieve this learned schema.

## API

### Listing Schemas

The list of all available schemas can get retrieved by doing a `GET` to `api.limacharlie.io/v1/orgs/YOUR-OID/schema`.

The returned data looks like:

```
{
  "event_types": [
    "evt:New-ExchangeAssistanceConfig",
    "det:00285-WIN-RDP_Connection_From_Non-RFC-1918_Address",
    "det:VirusTotal hit on DNS request",
    "evt:WEL",
    "evt:SHUTTING_DOWN",
    "evt:NETSTAT_REP",
    "evt:AdvancedHunting-DeviceEvents",
    "evt:NEW_DOCUMENT",
    "sched:12h_per_cloud_adapter",
    "sched:1h_per_sensor",
    "sched:3h_per_sensor",
    ...
}
```

Each element in the list of schema is composed of a prefix and a value.

Prefixes can be:

* `evt` for an Event.
* `dep` for a Deployment Event.
* `det` for a Detection.
* `art` for an Artifact Event.
* `sched` for Scheduling Events.

The value is generally the Event Type except for Detections where it is the `cat` (detection name).

### Retrieveing Schema Definition

Retrieving a specific schema definition can be done by doing a `GET` on `api.limacharlie.io/v1/orgs/YOUR-OID/schema/EVENT-TYPE`, where the `EVENT-TYPE` is one of the exact keys returned by the listing API above.

The returned data looks like:

```
{
  "schema": {
    "elements": [
      "i:routing/event_time",
      "s:routing/sid",
      "i:routing/moduleid",
      "i:event/PROCESS_ID",
      "s:routing/this",
      "i:event/DNS_TYPE",
      "s:routing/iid",
      "s:routing/did",
      "i:event/DNS_FLAGS",
      "i:routing/tags",
      "s:event/IP_ADDRESS",
      "s:routing/event_type",
      "i:event/MESSAGE_ID",
      "s:event/CNAME",
      "s:event/DOMAIN_NAME",
      "s:routing/ext_ip",
      "s:routing/parent",
      "s:routing/hostname",
      "s:routing/int_ip",
      "i:routing/plat",
      "s:routing/oid",
      "i:routing/arch",
      "s:routing/event_id"
    ],
    "event_type": "evt:DNS_REQUEST"
  }
}
```

The `schema.elements` data returned is composed of a prefix and a value.

The prefix is one of:

* `i` indicating the element is an Integer.
* `s` indicating the element is a String.
* `b` indicating the element is a Boolean.

The value is a path within the JSON. For example, the schema above would represent the following event:

```
{
  "event": {
    "CNAME": "cs9.wac.phicdn.net",
    "DNS_TYPE": 5,
    "DOMAIN_NAME": "ocsp.digicert.com",
    "MESSAGE_ID": 19099,
    "PROCESS_ID": 1224
  },
  "routing": {
    "arch": 2,
    "did": "b97e9d00-aaaa-aaaa-aaaa-27c3468d5901",
    "event_id": "8cec565d-14bd-4639-a1af-4fc8d5420b0c",
    "event_time": 1656959942437,
    "event_type": "DNS_REQUEST",
    "ext_ip": "35.1.1.1",
    "hostname": "demo-win-2016.c.lc-demo-infra.internal",
    "iid": "7d23bee6-aaaa-aaaa-aaaa-c8e8cca132a1",
    "int_ip": "10.1.1.1",
    "moduleid": 2,
    "oid": "8cbe27f4-aaaa-aaaa-aaaa-138cd51389cd",
    "parent": "42217cb0326ca254999554a862c3298e",
    "plat": 268435456,
    "sid": "bb4b30af-aaaa-aaaa-aaaa-f014ada33345",
    "tags": [
      "edr"
    ],
    "this": "a443f9c48bef700740ef27e062c333c6"
  }
}
```
