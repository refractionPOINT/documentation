# Testing Extensions

An extension is a webhook service that only makes sense in the presence of a LimaCharlie backend calling it, and a LimaCharlie API it calls back into. Both halves can be simulated locally, so a full lifecycle — schema, subscribe, request, unsubscribe — runs in an ordinary unit test with no cloud resources and no test organization.

Two pieces do this:

| | Simulator | MockServer |
| --- | --- | --- |
| Simulates | LimaCharlie calling **in** to your extension | The LimaCharlie API your extension calls **out** to |
| Package | `lc-extension/simulator` | `go-limacharlie/limacharlie` |
| Use it for | Webhook signing, lifecycle, continuations, metrics | D&R rules, Hive, sensors, secrets |

Most extensions need both, and the simulator wires them together.

## Structuring an Extension for Testing

The single change that makes an extension testable is building it in a function rather than inline, so that tests can construct the same extension the server runs:

```go
func buildExtension(secretKey string) *core.Extension {
    ext := &core.Extension{ /* ... */ }
    ext.Callbacks = core.ExtensionCallbacks{ /* ... */ }
    return ext
}

func main() {
    ext := buildExtension(os.Getenv("LC_SHARED_SECRET"))
    if err := ext.Init(); err != nil {
        panic(err)
    }
    webserver.RunExtension(ext)
}
```

The complete extension used by the tests on this page is the one from [Getting Started](building-extensions.md#a-complete-extension).

## A Lifecycle Test

This is the test worth writing first. It walks the extension through the same sequence the platform does, and catches the two failures that are otherwise only visible in production: an action missing from the advertised schema, and an event you thought you had subscribed to.

```go title="main_test.go"
--8<-- "snippets/golang/extension_basic/main_test.go:lifecycle"
```

A few things are being pinned down here beyond "it does not crash":

- **The schema actually advertises the action.** If `list_sensors` is not in the schema response, no user and no D&R rule can call it, however correct the handler is.
- **The event list is what you expect.** In the Go SDK the advertised events come from the `EventHandlers` map, not from `RequiredEvents`, so this assertion is the one that catches a missing handler.
- **Invalid configuration is rejected.** A validation callback that accepts everything is a common accident, and it silently disables the only guard the platform offers users against a broken config.
- **Billing happens once.** Metrics are how an extension gets paid; asserting the count catches both double-billing and silently billing nothing.

## Testing Error Classification

Whether a failure is retried is a decision your extension makes, and it is worth asserting rather than assuming — an error wrongly left retriable is attempted three times with backoff, repeating whatever partial work the handler already did.

```go title="main_test.go"
--8<-- "snippets/golang/extension_basic/main_test.go:errors"
```

## Testing the Signature Check

Every extension is a public HTTPS endpoint, so it is worth one test that unsigned traffic is refused.

```go title="main_test.go"
--8<-- "snippets/golang/extension_basic/main_test.go:signature"
```

## Testing Continuations

Continuations are the mechanism for work spanning multiple calls, and the simulator can either record them for inspection or run the whole chain synchronously.

```go
// Record only (the default): inspect what the extension asked for.
resp, err := sim.SendRequest(oid, "scan", lc.Dict{}, nil)
require.NoError(t, err)

conts := sim.Continuations()
require.Len(t, conts, 1)
require.Equal(t, "check_results", conts[0].Request.Action)
require.Equal(t, uint64(30), conts[0].Request.InDelaySeconds)

// Run one by hand, ignoring its delay.
resp, err = sim.ExecuteContinuation(conts[0])

// Or run the entire chain synchronously.
sim.SetContinuationMode(simulator.ContinuationModeImmediate)
resp, err = sim.SendRequest(oid, "scan", lc.Dict{}, nil)
```

!!! note "The simulator's chain limit is stricter than production"
    The simulator stops a continuation chain at 10 levels; the platform allows 100. A chain that runs in production may stop early under test. Assert on the shape of the chain rather than on running it to exhaustion.

## Testing Against the LimaCharlie API

When a handler calls back into LimaCharlie — creating D&R rules on subscribe, reading a secret, listing sensors — pair the simulator with a `MockServer`:

```go
ms := lc.NewMockServer(oid)
defer ms.Close()

// Seed whatever the extension expects to find.
ms.SensorStore["sid-1"] = &lc.Sensor{OID: oid, SID: "sid-1", Hostname: "web-01"}
ms.HiveStore["secret/"+oid] = map[string]lc.HiveData{
    "vendor-api-key": {Data: map[string]interface{}{"secret": "sk-test-12345"}},
}

sim := simulator.New(ext, simulator.WithMockServer(oid, ms))
defer sim.Close()

sim.SendSubscribe(oid, nil)

// Assert on what the extension did through the SDK.
require.Contains(t, ms.DRRules, "my-rule")
```

`sim.MockServer(oid)` and `sim.NewOrganization(oid)` reach the mock from outside a handler, for setup or verification. `AddMockServer` registers one after construction, which is useful in subtests.

Multiple organizations can be simulated at once, each with its own mock and config, which is the cheapest way to check that an extension is genuinely multi-tenant and is not leaking state between organizations:

```go
sim := simulator.New(ext,
    simulator.WithMockServer("oid-1", ms1),
    simulator.WithMockServer("oid-2", ms2),
    simulator.WithConfig("oid-1", lc.Dict{"env": "prod"}),
    simulator.WithConfig("oid-2", lc.Dict{"env": "staging"}),
)
```

## What the Simulator Does Not Cover

The simulator reproduces the transport and the lifecycle faithfully — HMAC signing, gzip, protocol version, idempotency keys, continuation limits, config injection — but it is not the extension manager, and two gaps matter:

- **It does not enforce your schema.** `SendRequest` delivers whatever data you pass straight to the handler. In production, unknown parameters, wrong types and unsatisfied `requirements` are rejected before your extension is called. A test can therefore pass with a payload that production would reject.
- **It does not resolve secrets.** `secret` parameters arrive verbatim rather than substituted with the referenced secret's value.

For both, the check is that your handler and your schema agree. Deriving the request struct's fields from the same names the schema declares, as the example does, keeps them from drifting.

## Running the Tests

```bash
go test ./...
```

No credentials, no network, and no test organization: the simulator runs the extension in-process against an `httptest` server, and the mock replaces the API.

## Python

The Python SDK does not currently ship a simulator. Extensions written with `lcextension` can still be tested by posting signed payloads at the Flask app returned by `getApp()`, computing the `lc-ext-sig` header as an HMAC-SHA256 of the request body keyed with the shared secret. The [Runtime Contract](runtime-contract.md#transport) describes the exact format.
