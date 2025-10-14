# Replay

Replay allows you to run [Detection & Response (D&R) rules](/v2/docs/detection-and-response) against historical traffic. This can be done in a few combinations of sources:

Rule Source:

* Existing rule in the organization, by name.
* Rule in the replay request.

Traffic:

* Sensor historical traffic.
* Local events provided during request.

## Using

Using the Replay API requires the [API key](../reference/api-keys.md) to have the following permissions:

* `insight.evt.get`

The returned data from the API contains the following:

* `responses`: a list of the actions that would have been taken by the rule (like `report`, `task`, etc).
* `num_evals`: a number of evaluation operations performed by the rule. This is a rough estimate of the performance of the rule.
* `num_events`: the number of events that were replayed.
* `eval_time`: the number of seconds it took to replay the data.

```
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

To use Replay in [LCQL Mode](lcql.md) (LimaCharlie Query Language), you can specify your query in the `query` parameter of the Replay Request (defined below) when using the REST interface, or you can use the LimaCharlie Python SDK/CLI's [query interface](https://github.com/refractionPOINT/python-limacharlie/blob/master/limacharlie/Query.py): `limacharlie query --help`.

### Python CLI

The [Python CLI](https://github.com/refractionPOINT/python-limacharlie) gives you a friendly way to replay data, and to do so across larger datasets by automatically splitting up your query into multiple queries that can run in parallel.

Sample command line to query one sensor:

```
limacharlie-replay --sid 9cbed57a-6d6a-4af0-b881-803a99b177d9 --start 1556568500 --end 1556568600 --rule-content ./test_rule.txt
```

Sample command line to query an entire organization:

```
limacharlie-replay --entire-org --start 1555359000 --end 1556568600 --rule-name my-rule-name
```

If specifying a rule as content with the `--rule-content`, the format should be in `JSON` or `YAML` like:

```
detect:
  event: DNS_REQUEST
  op: is
  path: event/DOMAIN_NAME
  value: www.dilbert.com
respond:
  - action: report
    name: dilbert-is-here
```

Instead of specifying the `--entire-org` or `--sid` flags, you may use events from a local file via the `--events` flag.

We invite you to look at the command line usage itself, as the tool evolves.

### REST API

The Replay API is available to all DataCenter locations using a per-location URL. To get the appropriate URL for your organization, use the REST endpoint to retrieve the URLs found [here](https://api.limacharlie.io/static/swagger/#/Organizations/getOrgURLs) named `replay`.

Having per-location URLs will allow us to guarantee that processing occurs within the geographical area you chose. Currently, some locations are NOT guaranteed to be in the same area due to the fact we are using the Google Cloud Run product which is not available globally. For these cases, processing is currently done in the United States, but as soon as it becomes available in your area, the processing will be moved transparently.

Authentication to this API works with the same JWTs as the main limacharlie.io API.

For this example, we will use the experimental datacenter's URL:

```
https://0651b4f82df0a29c.replay.limacharlie.io/
```

The API mainly works on a per-sensor basis, on a limited amount of time. Replaying for multiple sensors (or entire org), or longer time period is done through multiple parallel API calls. This multiplexing is taken care of by the Python CLI above.

To query Replay, do a `POST` with a `Content-Type` header of `application-json` and with a JSON body like:

```
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
      "start_time": 0,   // start second epoch time to replay from
      "end_time": 0      // end second epoch time to replay to
    },
    "events": [{}]       // literal list of events to replay
    "stream": "" // defaults to events, can also be "audit" or "detect"
  },
  "limit_event": 0,      // optional approximate number of events to process
  "limit_eval": 0,       // optional approximate number of operator evaluations to perform
  "trace": false,        // optional, if true add trace information to response, VERY VERBOSE
  "is_dry_run": false,   // optional, if true, an estimate of the total cost of the query will be returned
  "query": ""            // optional alternative way to describe a replay query as a LimaCharlie Query Language (LCQL) query.
}
```

Like the other endpoints you can also submit a `rule_name` in the URL query if you want to use an existing organization rule.

You may also specify a `limit_event` and `limit_eval` parameter as integers. They will limit the number of events evaluated and the number of rule evaluations performed (approximately). If the limits are reached, the response will contain an item named `limit_eval_reached: true` and `limit_event_reached: true`.

Finally, you may also set `trace` to `true` in the request to receive a detailed trace of the rule evaluation. This is useful in the development of new rules to find where rules are failing.

## Billing

The Replay service is billed on a per event evaluated.