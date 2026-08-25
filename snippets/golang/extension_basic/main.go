// A complete, minimal LimaCharlie Extension.
//
// It exposes one user-facing action, "list_sensors", which uses the
// pre-authenticated SDK handed to every callback to list the sensors matching
// a selector. It also stores a small configuration and reports a billing
// metric for each call.
package main

import (
	"context"
	"fmt"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
	"github.com/refractionPOINT/lc-extension/common"
	"github.com/refractionPOINT/lc-extension/core"
	"github.com/refractionPOINT/lc-extension/server/webserver"
)

// listSensorsRequest is the typed form of the "list_sensors" parameters. The
// framework unmarshals the incoming request data into a copy of this struct,
// so the fields here must match the parameter names in the schema below.
type listSensorsRequest struct {
	Selector string `json:"selector"`
}

// extensionConfig is the typed form of the extension's configuration.
type extensionConfig struct {
	MaxResults int `json:"max_results"`
}

// buildExtension returns the extension, ready to Init. Keeping construction in
// a function (rather than inline in main) is what lets the tests build the
// same extension the server runs.
func buildExtension(secretKey string) *core.Extension {
	logger := &limacharlie.LCLoggerGCP{}

	ext := &core.Extension{
		ExtensionName: "my-extension",
		SecretKey:     secretKey,

		// Describes the extension's configuration. LimaCharlie renders this as
		// a form and stores the result in the extension_configuration hive.
		ConfigSchema: common.SchemaObject{
			Fields: map[common.SchemaKey]common.SchemaElement{
				"max_results": {
					Label:        "Maximum results",
					Description:  "Largest number of sensors to return in one call.",
					DataType:     common.SchemaDataTypes.Integer,
					DefaultValue: 100,
					DisplayIndex: 1,
				},
			},
			Requirements: [][]common.SchemaKey{},
		},

		// Describes the actions the extension exposes. LimaCharlie enforces
		// this schema before a request ever reaches the callbacks below.
		RequestSchema: common.RequestSchemas{
			"list_sensors": {
				Label:            "List sensors",
				IsUserFacing:     true,
				IsImpersonated:   false,
				ShortDescription: "list sensors matching a selector",
				LongDescription:  "Lists the sensors in this organization that match the given sensor selector.",
				Messages: common.StatusMessages{
					InProgressMessage: "Listing sensors...",
					SuccessMessage:    "Sensors listed.",
					ErrorMessage:      "Could not list sensors.",
				},
				ParameterDefinitions: common.SchemaObject{
					Fields: map[common.SchemaKey]common.SchemaElement{
						"selector": {
							Label:        "Sensor selector",
							Description:  "Selector expression, or * for every sensor.",
							DataType:     common.SchemaDataTypes.SensorSelector,
							DefaultValue: "*",
							DisplayIndex: 1,
						},
					},
					// "selector" always has a value because it has a default,
					// but declaring it required documents the contract and
					// makes the UI mark the field.
					Requirements: [][]common.SchemaKey{{"selector"}},
				},
				ResponseDefinition: &common.SchemaObject{
					Fields: map[common.SchemaKey]common.SchemaElement{
						"count": {
							Label:       "Count",
							Description: "Number of sensors matched.",
							DataType:    common.SchemaDataTypes.Integer,
						},
						"hostnames": {
							Label:       "Hostnames",
							Description: "Hostnames of the sensors matched.",
							DataType:    common.SchemaDataTypes.String,
							IsList:      true,
						},
					},
				},
			},
		},
	}

	ext.Callbacks = core.ExtensionCallbacks{
		// Called whenever a user changes this extension's configuration.
		// Returning an error rejects the change.
		ValidateConfig: func(ctx context.Context, org *limacharlie.Organization, config limacharlie.Dict) common.Response {
			conf := extensionConfig{}
			if err := config.UnMarshalToStruct(&conf); err != nil {
				return errorResponse(err)
			}
			if conf.MaxResults < 0 {
				return errorResponse(fmt.Errorf("max_results cannot be negative"))
			}
			return common.Response{}
		},

		RequestHandlers: map[common.ActionName]core.RequestCallback{
			"list_sensors": {
				RequestStruct: &listSensorsRequest{},
				Callback:      onListSensors,
			},
		},

		// Registering a handler is what subscribes the extension to an event:
		// the Go framework advertises exactly the events named here.
		EventHandlers: map[common.EventName]core.EventCallback{
			common.EventTypes.Subscribe: func(ctx context.Context, params core.EventCallbackParams) common.Response {
				logger.Info(fmt.Sprintf("subscribed: %s", params.Org.GetOID()))
				return common.Response{}
			},
			common.EventTypes.Unsubscribe: func(ctx context.Context, params core.EventCallbackParams) common.Response {
				logger.Info(fmt.Sprintf("unsubscribed: %s", params.Org.GetOID()))
				return common.Response{}
			},
		},

		// Required. The framework calls this directly, without a nil check, on
		// paths such as an invalid webhook signature. Leaving it unset will
		// panic the extension on the first malformed request it receives.
		ErrorHandler: func(err *common.ErrorReportMessage) {
			logger.Error(fmt.Sprintf("error reported for %s: %s", err.Oid, err.Error))
		},
	}

	return ext
}

func onListSensors(ctx context.Context, params core.RequestCallbackParams) common.Response {
	request := params.Request.(*listSensorsRequest)

	conf := extensionConfig{}
	if err := params.Config.UnMarshalToStruct(&conf); err != nil {
		return errorResponse(err)
	}

	// params.Org is the LimaCharlie SDK, already authenticated for the
	// organization this request belongs to. The extension never stores or
	// handles organization credentials itself.
	sensors, err := params.Org.ListSensorsFromSelector(request.Selector)
	if err != nil {
		// Transient failures should be retriable so the platform tries again.
		return common.Response{Error: err.Error()}
	}

	hostnames := []string{}
	for _, sensor := range sensors {
		if conf.MaxResults > 0 && len(hostnames) >= conf.MaxResults {
			break
		}
		hostnames = append(hostnames, sensor.Hostname)
	}

	return common.Response{
		Data: limacharlie.Dict{
			"count":     len(hostnames),
			"hostnames": hostnames,
		},
		// Optional. Metrics are namespaced as "<extension-name>:<sku>" and
		// deduplicated on the idempotency key.
		Metrics: &common.MetricReport{
			IdempotentKey: params.IdempotentKey,
			Metrics: []common.Metric{
				{Sku: "sensor_listings", Value: 1},
			},
		},
	}
}

// errorResponse marks an error as permanent so the platform stops retrying it.
// Anything the extension cannot succeed at on a later attempt -- bad
// configuration, invalid input -- belongs here.
func errorResponse(err error) common.Response {
	notRetriable := false
	return common.Response{Error: err.Error(), Retriable: &notRetriable}
}

func main() {
	ext := buildExtension("YOUR_SHARED_SECRET")
	if err := ext.Init(); err != nil {
		panic(err)
	}
	webserver.RunExtension(ext)
}
