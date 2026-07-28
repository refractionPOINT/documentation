# Replay

Replay runs Detection & Response (D&R) rules against historical traffic.
 You can combine these sources:

Rule Source:

- An existing rule in the organization, by name.
- A rule in the replay request.

Traffic:

- Historical traffic from a sensor.
- Local events that you supply in the request.

## Using

The Replay API needs an [API key](../../7-administration/access/api-keys.md) with these permissions:

- `insight.evt.get`

The API returns this data:

- `responses`: a list of the actions that the rule would take (such as `report` or `task`).
- `num_evals`: the number of evaluation operations that the rule did. This number is a rough estimate of the performance of the rule.
- `num_events`: the number of events that Replay replayed.
- `eval_time`: the number of seconds to replay the data.

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

The REST interface also accepts LCQL Mode (LimaCharlie Query Language). Put your query in the `query` parameter of the Replay Request that is defined below. You can also use the [query interface](https://github.com/refractionPOINT/python-limacharlie/blob/master/limacharlie/Query.py) of the LimaCharlie Python SDK and CLI: `limacharlie search --help`.

### Python CLI

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) replays data. For a large dataset, the CLI splits your query into many queries that run in parallel.

Sample command line to query one sensor:

```bash
limacharlie replay run --detect-file ./test_detect.yaml --respond-file ./test_respond.yaml --start 1556568500 --end 1556568600
```

Sample command line to query an entire organization:

```bash
limacharlie replay run --name my-rule-name --start 1555359000 --end 1556568600
```

When you specify a rule with `--detect-file` and `--respond-file`, use the `JSON` or `YAML` format for each file. For example, a detect file:

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

You can use events from a local file instead of an entire organization. Use the `limacharlie dr test` command with the `--events` flag.

The tool changes over time. Look at the command line usage itself for the current options.

### REST API

The Replay API is available in all DataCenter locations. Each location has its own URL.
 To get the correct URL for your organization, use the [`getOrgURLs` REST endpoint](https://api.limacharlie.io/static/swagger/#/Organizations/getOrgURLs) and look for the URL named `replay`.

A URL for each location keeps the processing inside the geographical area that you chose. Some locations are NOT in the same area, because LimaCharlie uses the Google Cloud Run product, which is not available in all areas. For these locations, the processing is done in the United States. When Google Cloud Run becomes available in your area, the processing moves there transparently.

Authentication to this API works with the same JWTs as the main limacharlie.io API.

This example uses the URL of the experimental datacenter:

```python
https://0651b4f82df0a29c.replay.limacharlie.io/
```

The API works mainly for one sensor and for a limited period of time. To replay many sensors, an entire organization, or a longer period, make many parallel API calls. The Python CLI above makes these parallel calls for you.

To query Replay, send a `POST` request with a `Content-Type` header of `application-json` and a JSON body like this:

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
  "query": ""            // optional alternative way to describe a replay query as a LimaCharlie Query Language (LCQL) query.
}
```

Like the other endpoints, you can also put a `rule_name` in the URL query
 to use an existing organization rule.

You can also give the `limit_event` and `limit_eval` parameters as integers. They limit the approximate number of events that Replay evaluates and the approximate number of rule evaluations. If Replay reaches the limits, the response contains an item named `limit_eval_reached: true` and `limit_event_reached: true`.

You can also set `trace` to `true` in the request to get a detailed trace of the rule evaluation. The trace helps you find where a new rule fails.

## Billing

The Replay service is billed for each event that it evaluates.
