# Replay

Replay allows you to run Detection & Response (D&R) rules against historical traffic.
 This can be done in a few combinations of sources:

Rule Source:

- Existing rule in the organization, by name.
- Rule in the replay request.

Traffic:

- Sensor historical traffic.
- Local events provided during request.

## Using

Using the Replay API requires the [API key](../../7-administration/access/api-keys.md) to have the following permissions:

- `insight.evt.get`

The returned data from the API contains the following:

- `responses`: a list of the actions that would have been taken by the rule (like `report`, `task`, etc).
- `num_evals`: a number of evaluation operations performed by the rule. This is a rough estimate of the performance of the rule.
- `num_events`: the number of events that were replayed.
- `eval_time`: the number of seconds it took to replay the data.

```json
{
  "error": "",        // if an error occured.
  "stats": {
    "n_proc": 0,      // the number of events processed
    "n_shard": 0,     // the number of chunks the replay job was broken into
    "n_eval": 0,      // the number of operator evaluations performed
    "wall_time": 0    // the number of real-world seconds the job took
  },
  "did_match": false, // indicates if the rule matched any event at all
  "results": [],      // a list of dictionaries containing the details of actions the engine would have taken
  "traces": []        // a list of trace items to help you troubleshoot where a rule failed
}
```

### Query Language

To use Replay in LCQL Mode (LimaCharlie Query Language), you can specify your query in the `query` parameter of the Replay Request (defined below) when using the REST interface, or you can use the LimaCharlie Python SDK/CLI's [query interface](https://github.com/refractionPOINT/python-limacharlie/blob/master/limacharlie/sdk/search.py): `limacharlie search --help`.

### Python CLI

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a friendly way to replay data, and to do so across larger datasets by automatically splitting up your query into multiple queries that can run in parallel.

Sample command line to query one sensor:

```bash
limacharlie replay run --detect-file ./test_detect.yaml --respond-file ./test_respond.yaml --start 1556568500 --end 1556568600
```

Sample command line to query an entire organization:

```bash
limacharlie replay run --name my-rule-name --start 1555359000 --end 1556568600
```

When specifying a rule via `--detect-file` and `--respond-file`, each file should be in `JSON` or `YAML` format. For example, a detect file:

```yaml
event: DNS_REQUEST
op: is
path: event/DOMAIN_NAME
value: www.dilbert.com
```

And a respond file:

```yaml
- action: report
  name: dilbert-is-here
```

Instead of replaying against an entire organization, you may use events from a local file via the `limacharlie dr test` command with the `--events` flag.

We invite you to look at the command line usage itself, as the tool evolves.

### REST API

The Replay API is available to all DataCenter locations using a per-location URL.
 To get the appropriate URL for your organization, use the [`getOrgURLs` REST endpoint](https://api.limacharlie.io/static/swagger/#/Organizations/getOrgURLs) and look for the URL named `replay`.

Having per-location URLs will allow us to guarantee that processing occurs within the geographical area you chose. Currently, some locations are NOT guaranteed to be in the same area due to the fact we are using the Google Cloud Run product which is not available globally. For these cases, processing is currently done in the United States, but as soon as it becomes available in your area, the processing will be moved transparently.

Authentication to this API works with the same JWTs as the main limacharlie.io API.

For this example, we will use the experimental datacenter's URL:

```python
https://0651b4f82df0a29c.replay.limacharlie.io/
```

The API mainly works on a per-sensor basis, on a limited amount of time. Replaying for multiple sensors (or entire org), or longer time period is done through multiple parallel API calls. This multiplexing is taken care of by the Python CLI above.

To query Replay, do a `POST` with a `Content-Type` header of `application-json` and with a JSON body like:

```json
{
  "oid": "",             // OID this query relates to
  "rule_source": {       // rule source information (use one of "rule_name" or "rule")
    "rule_name": "",     // pre-existing rule name to run
    "namespace": "", // default: general namespace, can also be "managed" and "service"
    "rule": {            // literal rule to run
      "detect": {},
      "respond": []
    }
  },
  "event_source": {      // event source information (use one of "sensor_events" or "events")
    "sensor_events": {   // use historical events from sensors
      "sid": "",         // sensor id to replay from, or entire org if empty
      "selector": "", // a sensor selector
      "start_time": 0,   // start second epoch time to replay from
      "end_time": 0      // end second epoch time to replay to
    },
    "events": [{}],       // literal list of events to replay
    "stream": "" // defaults to events, can also be "audit" or "detect"
  },
  "limit_event": 0,      // optional approximate number of events to process
  "limit_eval": 0,       // optional approximate number of operator evaluations to perform
  "trace": false,        // optional, if true add trace information to response, VERY VERBOSE
  "is_dry_run": false,   // optional, if true, an estimate of the total cost of the query will be returned
  "query": "",           // optional alternative way to describe a replay query as a LimaCharlie Query Language (LCQL) query.
  "lookups": {}          // optional lookups used by rules with "op: lookup", see "Lookups in Replay" below
}
```

Like the other endpoints you can also submit a `rule_name` in the URL query if you want
 to use an existing organization rule.

You may also specify a `limit_event` and `limit_eval` parameter as integers. They will limit the number of events evaluated and the number of rule evaluations performed (approximately). If the limits are reached, the response will contain an item named `limit_eval_reached: true` and `limit_event_reached: true`.

Finally, you may also set `trace` to `true` in the request to receive a detailed trace of the rule evaluation. This is useful in the development of new rules to find where rules are failing.

### Lookups in Replay

Rules that use the [`lookup` operator](../../8-reference/detection-logic-operators.md#lookup) with a `hive://lookup/<name>` resource get their lookups from the Replay request itself. Supply them in the optional top-level `lookups` field: an object that maps each lookup name to its entries, where each entry maps an indicator to a metadata object. This is the same shape as a lookup's `lookup_data` in the [lookup Hive](../../7-administration/config-hive/lookups.md).

For example, this `lookups` field supplies a lookup named `suspicious-domains`, which a rule references as `hive://lookup/suspicious-domains`. It holds one indicator, `evil.example.com`, whose metadata is returned to the rule on a match:

```json
{
  "lookups": {
    "suspicious-domains": {
      "evil.example.com": {"category": "c2", "severity": "high"}
    }
  }
}
```

Replay never reads your Organization's lookups. A rule's `hive://lookup/<name>` always resolves to the lookup of that name in the request's `lookups`, used exactly as given, even when the Organization has a lookup with the same name. This lets you test a lookup rule against sample indicators without creating or changing a lookup in your Organization.

The lookups in a request are intentionally immutable: they are fixed when the request is received, and they do not change while the rule is evaluated, however long the replay runs or however many workers it is spread across. This makes a replay reproducible. The same rule with the same lookups over the same events always gives the same results, whatever happens to your Organization's lookups in the meantime. It also means you provide all the static data a rule needs up front, so you can test a rule against exact indicators and compare runs while you change the rule.

If the request has no `lookups` field, or the field does not contain a lookup the rule names, the rule fails to compile and the response's `error` contains:

```text
lookup "suspicious-domains" is not available in replay: supply it in the request's "lookups" field
```

An empty lookup, `{"suspicious-domains": {}}`, is valid. It lets a rule that names the lookup compile, which is useful to validate a rule's syntax, and it matches nothing.

#### Matching

Lookups in Replay match the same way lookups do in live D&R rules:

- The event's value must equal an indicator exactly. A value that is not an indicator in the lookup does not match, and neither does an indicator whose metadata is `null`.
- `case sensitive: false` lowercases the value from the event, never the lookup's indicators. For a case-insensitive rule, write the indicators in lowercase.
- The [`file name`](../../8-reference/detection-logic-operators.md#file-name) and [`sub domain`](../../8-reference/detection-logic-operators.md#sub-domain) transforms are applied to the event's value before the lookup.
- On a match, the detection's `mtd` contains the indicator's metadata under the lookup's name, for example `"mtd": {"suspicious-domains": {"category": "c2", "severity": "high"}}`.
- `metadata_rules` are evaluated against the matched indicator's metadata.

API-based lookups that use an `lcr://` resource, such as `lcr://api/vt`, are not supported in Replay.

#### Limits

The `lookups` field is meant for sample indicators and rule validation, not for uploading complete threat feeds. A request may carry:

- up to 32 lookups
- up to 20,000 indicators across all of its lookups
- a `lookups` field of at most 64 KiB, measured as sent

A request over any of these limits, or whose `lookups` field is not an object of objects, is rejected with HTTP status `400` and an `error` explaining why:

```json
{
  "error": "invalid lookups: too many lookups: 33 (max 32)"
}
```

#### Example: Domain Lookup Against Sample Events

This rule reports DNS requests for domains in the `suspicious-domains` lookup. Because it uses `case sensitive: false`, the indicators in the lookup are lowercase:

```yaml
event: DNS_REQUEST
op: lookup
path: event/DOMAIN_NAME
resource: hive://lookup/suspicious-domains
case sensitive: false
```

The request below carries the rule, two sample events in `event_source.events`, and the lookup:

```json
{
  "oid": "YOUR_OID",
  "rule_source": {
    "rule": {
      "detect": {
        "event": "DNS_REQUEST",
        "op": "lookup",
        "path": "event/DOMAIN_NAME",
        "resource": "hive://lookup/suspicious-domains",
        "case sensitive": false
      },
      "respond": [
        {"action": "report", "name": "suspicious-domain-lookup"}
      ]
    }
  },
  "event_source": {
    "events": [
      {
        "routing": {"event_type": "DNS_REQUEST", "event_time": 1700000000000},
        "event": {"DOMAIN_NAME": "Evil.Example.com"}
      },
      {
        "routing": {"event_type": "DNS_REQUEST", "event_time": 1700000001000},
        "event": {"DOMAIN_NAME": "www.example.net"}
      }
    ]
  },
  "lookups": {
    "suspicious-domains": {
      "evil.example.com": {"category": "c2", "severity": "high"},
      "phish.example.net": {"category": "phishing", "severity": "medium"}
    }
  }
}
```

Only the first event matches: its domain, lowercased, is an indicator in the lookup, while the second event's domain is not. The response reports one detection, whose `mtd` carries the indicator's metadata under the lookup's name. Abbreviated:

```json
{
  "did_match": true,
  "results": [
    {
      "action": "report",
      "data": {
        "cat": "suspicious-domain-lookup",
        "detect": {
          "event": {"DOMAIN_NAME": "Evil.Example.com"},
          "routing": {"event_type": "DNS_REQUEST", "event_time": 1700000000000}
        },
        "mtd": {
          "suspicious-domains": {"category": "c2", "severity": "high"}
        }
      }
    }
  ]
}
```

#### Example: IP Lookup With Metadata Rules

This rule looks up the destination IPs of `NETWORK_CONNECTIONS` events in the `ip-reputation` lookup, and uses `metadata_rules` to report a match only when the indicator's `score` is greater than 7:

```yaml
event: NETWORK_CONNECTIONS
op: lookup
path: event/NETWORK_ACTIVITY/?/DESTINATION/IP_ADDRESS
resource: hive://lookup/ip-reputation
metadata_rules:
  op: is greater than
  path: score
  value: 7
```

The request below replays the rule over one hour of a sensor's historical traffic with three sample indicators. A connection to `203.0.113.10` (score 9) is reported. Connections to `198.51.100.20` (score 4) and `192.0.2.30` (no score) are not:

```json
{
  "oid": "YOUR_OID",
  "rule_source": {
    "rule": {
      "detect": {
        "event": "NETWORK_CONNECTIONS",
        "op": "lookup",
        "path": "event/NETWORK_ACTIVITY/?/DESTINATION/IP_ADDRESS",
        "resource": "hive://lookup/ip-reputation",
        "metadata_rules": {
          "op": "is greater than",
          "path": "score",
          "value": 7
        }
      },
      "respond": [
        {"action": "report", "name": "high-risk-destination"}
      ]
    }
  },
  "event_source": {
    "sensor_events": {
      "sid": "YOUR_SENSOR_ID",
      "start_time": 1700000000,
      "end_time": 1700003600
    }
  },
  "lookups": {
    "ip-reputation": {
      "203.0.113.10": {"score": 9, "source": "sample-feed"},
      "198.51.100.20": {"score": 4, "source": "sample-feed"},
      "192.0.2.30": {}
    }
  }
}
```

#### Example: Validating a Lookup Rule

To check that a rule using a lookup compiles, without testing what it matches, supply each lookup it names with no entries. The rule compiles and matches nothing:

```json
{
  "oid": "YOUR_OID",
  "rule_source": {
    "rule": {
      "detect": {
        "event": "DNS_REQUEST",
        "op": "lookup",
        "path": "event/DOMAIN_NAME",
        "resource": "hive://lookup/suspicious-domains",
        "case sensitive": false
      },
      "respond": [
        {"action": "report", "name": "suspicious-domain-lookup"}
      ]
    }
  },
  "event_source": {
    "events": [
      {
        "routing": {"event_type": "DNS_REQUEST", "event_time": 1700000000000},
        "event": {"DOMAIN_NAME": "www.example.com"}
      }
    ]
  },
  "lookups": {
    "suspicious-domains": {}
  }
}
```

The same request without the `lookups` field fails with the `lookup "suspicious-domains" is not available in replay` error shown above.

## Billing

The Replay service is billed on a per event evaluated.
