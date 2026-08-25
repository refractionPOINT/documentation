package main

import (
	"testing"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
	"github.com/refractionPOINT/lc-extension/simulator"
	"github.com/stretchr/testify/require"
)

const testOID = "11111111-2222-3333-4444-555555555555"

// --8<-- [start:lifecycle]
// TestLifecycle walks the extension through the sequence the platform actually
// puts it through: fetch the schema, heartbeat, validate a config, subscribe,
// serve a request, then unsubscribe.
func TestLifecycle(t *testing.T) {
	// MockServer stands in for the LimaCharlie API that the extension calls
	// out to. The simulator stands in for the platform calling in.
	ms := limacharlie.NewMockServer(testOID)
	defer ms.Close()

	ms.SensorStore["aaaaaaaa-0000-0000-0000-000000000001"] = &limacharlie.Sensor{
		OID: testOID, SID: "aaaaaaaa-0000-0000-0000-000000000001", Hostname: "web-01",
	}
	ms.SensorStore["aaaaaaaa-0000-0000-0000-000000000002"] = &limacharlie.Sensor{
		OID: testOID, SID: "aaaaaaaa-0000-0000-0000-000000000002", Hostname: "web-02",
	}

	ext := buildExtension("test-secret")
	require.NoError(t, ext.Init())

	sim := simulator.New(ext,
		simulator.WithGzip(), // The platform always compresses; so should the test.
		simulator.WithMockServer(testOID, ms),
		simulator.WithConfig(testOID, limacharlie.Dict{"max_results": 100}),
	)
	defer sim.Close()

	// The platform fetches the schema when the extension is registered.
	schema, err := sim.SendSchemaRequest()
	require.NoError(t, err)
	require.Contains(t, schema.Request, "list_sensors")
	// The Go framework advertises exactly the events that have handlers.
	require.Contains(t, schema.RequiredEvents, "subscribe")

	status, err := sim.SendHeartbeat()
	require.NoError(t, err)
	require.Equal(t, 200, status)

	// A user edits the configuration; the platform asks us to validate it.
	resp, err := sim.SendConfigValidation(testOID, limacharlie.Dict{"max_results": 10})
	require.NoError(t, err)
	require.Empty(t, resp.Error)

	// An invalid configuration must be rejected.
	resp, err = sim.SendConfigValidation(testOID, limacharlie.Dict{"max_results": -1})
	require.NoError(t, err)
	require.Contains(t, resp.Error, "cannot be negative")

	resp, err = sim.SendSubscribe(testOID, nil)
	require.NoError(t, err)
	require.Empty(t, resp.Error)

	// The action itself, against the mocked API.
	resp, err = sim.SendRequest(testOID, "list_sensors", limacharlie.Dict{"selector": "*"}, nil)
	require.NoError(t, err)
	require.Empty(t, resp.Error)

	data, ok := resp.Data.(map[string]interface{})
	require.True(t, ok)
	require.EqualValues(t, 2, data["count"])

	// The call should have been billed exactly once.
	metrics := sim.Metrics()
	require.Len(t, metrics, 1)
	require.Equal(t, "sensor_listings", metrics[0].Metrics[0].Sku)

	resp, err = sim.SendUnsubscribe(testOID, nil)
	require.NoError(t, err)
	require.Empty(t, resp.Error)
}
// --8<-- [end:lifecycle]

// --8<-- [start:errors]
// TestErrorClassification pins down which failures the platform will retry.
// A permanent error must be marked non-retriable so the platform stops after
// one attempt instead of backing off through three.
func TestErrorClassification(t *testing.T) {
	ms := limacharlie.NewMockServer(testOID)
	defer ms.Close()

	ext := buildExtension("test-secret")
	require.NoError(t, ext.Init())

	sim := simulator.New(ext, simulator.WithMockServer(testOID, ms))
	defer sim.Close()

	// Invalid configuration is permanent: retrying cannot help.
	resp, err := sim.SendConfigValidation(testOID, limacharlie.Dict{"max_results": -1})
	require.NoError(t, err)
	require.NotEmpty(t, resp.Error)
	require.False(t, resp.IsRetriable())

	// An action the extension does not implement is rejected by the framework
	// with HTTP 400, before any handler runs.
	res, err := sim.SendRequestFull(testOID, "no_such_action", limacharlie.Dict{}, nil)
	require.NoError(t, err)
	require.Equal(t, 400, res.StatusCode)
}
// --8<-- [end:errors]

// --8<-- [start:signature]
// TestSignatureRejection verifies the extension refuses unsigned traffic.
// Every extension is reachable on the public internet, so this is worth
// asserting rather than assuming.
func TestSignatureRejection(t *testing.T) {
	ext := buildExtension("test-secret")
	require.NoError(t, ext.Init())

	sim := simulator.New(ext)
	defer sim.Close()

	statusCode, err := sim.SendWithBadSignature()
	require.NoError(t, err)
	require.Equal(t, 401, statusCode)
}
// --8<-- [end:signature]
