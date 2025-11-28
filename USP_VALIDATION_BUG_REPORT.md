# USP Validation API Bug Report

## ✅ STATUS: FIXED (2025-11-24)

## Summary
The `validate_usp_mapping` API endpoint was always returning unparsed events with `json_payload: {"text": "..."}` instead of applying the parsing rules, even when the mapping configuration was syntactically correct.

**Root Cause Identified:** Missing msgpack struct tags in `go-uspclient/protocol/mapping.go`

**Fix Applied:** Added msgpack tags to all fields in `protocol.MappingDescriptor` and related structs.

## Root Cause
Type mismatch in the request pipeline:

**SDK Layer** (`go-limacharlie/limacharlie/validation.go:34`):
```go
Mapping Dict `json:"mapping,omitempty"`
```
Sends: `map[string]interface{}`

**Backend Layer** (`legion_usp_proxy/service/validation.go:55`):
```go
Mapping *protocol.MappingDescriptor `json:"opt_mapping" msgpack:"opt_mapping"`
```
Expects: `*protocol.MappingDescriptor` struct

When the SDK sends a `Dict` (generic map) through JSON → RPC → msgpack, the automatic conversion to the typed struct pointer appears to be failing silently, causing `req.Mapping` to remain `nil`.

## Evidence

### 1. All Validation Attempts Fail to Parse

Test input:
```json
{
  "platform": "text",
  "mapping": {
    "parsing_re": "<(?P<pri>\\d+)>(?P<rest>.*)"
  },
  "text_input": "<38>Nov 12 18:45:33 localhost sshd[2978160]: test"
}
```

Expected result:
```json
{
  "json_payload": {
    "pri": "38",
    "rest": "Nov 12 18:45:33 localhost sshd[2978160]: test"
  }
}
```

Actual result:
```json
{
  "json_payload": {
    "text": "<38>Nov 12 18:45:33 localhost sshd[2978160]: test"
  }
}
```

The `{"text": "..."}` fallback is created by the GenericTextParser when `JsonPayload` is empty (mapping.go:37-41 in legion_usp_proxy).

### 2. Both Regex and Grok Parsing Fail

Tested:
- `parsing_re` with named capture groups
- `parsing_grok` with standard patterns
- Simple patterns (e.g., `<%{WORD:pri}>%{GREEDYDATA:rest}`)
- Complex patterns matching the actual auth.log format

All return unparsed `{"text": "..."}`.

### 3. Unit Tests Work Correctly

The validation tests in `legion_usp_proxy/service/validation_test.go` all pass, including:
- `TestValidateMappingTextInput` (line 14-44)
- `TestValidateMappingGrokPattern` (line 127-154)

These tests call the handler directly with a properly typed struct:
```go
req := &ValidateMappingRequest{
    Platform: "text",
    Mapping: &protocol.MappingDescriptor{
        ParsingRE: `...`,
    },
    TextInput: "...",
}
```

This proves the backend parsing logic works correctly when given a proper struct.

### 4. API Layer Passes Data Unchanged

The API endpoint (`lc_api-go/service/endpoint_usp_validation.go:127-164`) receives JSON, parses it as a generic `Dict`, and passes it straight through to the RPC backend:

```go
var rpcRequest Dict
validateRequestBody(&request.r.Body, &rpcRequest, 10*1024*1024)
request.getSiteForOrg(oid).Query("usp", "validate_mapping", rpcRequest, ...)
```

No type conversion happens at the API layer.

### 5. RPC Framework Handles opt_ Prefix Correctly

The IronLegion RPC framework (`go-ironlegionprotocol/ilp/Actor.go`) strips the `opt_` prefix from field tags and maps incoming data:

```go
k := strings.TrimPrefix(argKey, "opt_")  // "opt_mapping" → "mapping"
v, found := request.Data[k]               // Find "mapping" in incoming data
if found {
    inArgsDict[argKey] = v                // Set inArgsDict["opt_mapping"] = v
}
```

Then it marshals and unmarshals via msgpack. The issue is likely in this msgpack step where `map[string]interface{}` → `*protocol.MappingDescriptor` conversion fails.

## Impact

The validation API cannot be used to test USP configurations before deployment. Users must:
1. Deploy configs blindly to production
2. Check telemetry to see if parsing worked
3. Fix and redeploy if it didn't

This makes USP development significantly slower and error-prone.

## Workaround

None currently available. The MCP tool and SDK both use the same broken API path.

## Reproduction Steps

1. Use any LimaCharlie SDK or MCP tool
2. Call `validate_usp_mapping` with any mapping configuration
3. Observe that all events return unparsed with `{"text": "..."}`

## Proposed Solution

### Option 1: Fix SDK Type (Recommended)

Change SDK to send the mapping as proper struct fields instead of a generic Dict:

**Current** (`go-limacharlie/limacharlie/validation.go`):
```go
type USPMappingValidationRequest struct {
    Platform  string `json:"platform"`
    Mapping   Dict   `json:"mapping,omitempty"`  // ← Problem
    TextInput string `json:"text_input,omitempty"`
}
```

**Fixed**:
```go
type USPMappingValidationRequest struct {
    Platform  string              `json:"platform"`
    Mapping   *MappingDescriptor  `json:"mapping,omitempty"`  // ← Use proper struct
    TextInput string              `json:"text_input,omitempty"`
}

type MappingDescriptor struct {
    ParsingRE          string            `json:"parsing_re,omitempty"`
    ParsingGrok        map[string]string `json:"parsing_grok,omitempty"`
    SensorKeyPath      string            `json:"sensor_key_path,omitempty"`
    SensorHostnamePath string            `json:"sensor_hostname_path,omitempty"`
    EventTypePath      string            `json:"event_type_path,omitempty"`
    EventTimePath      string            `json:"event_time_path,omitempty"`
    // ... other fields from protocol.MappingDescriptor
}
```

This ensures proper type safety and automatic struct marshaling.

### Option 2: Fix Backend Unmarshaling

Add custom unmarshaling logic in the RPC handler to convert `Dict` to struct before processing.

### Option 3: Add Logging

At minimum, add debug logging in `validateMapping` to log `req.Mapping` so we can confirm if it's nil or if the issue is elsewhere.

## Files Involved

- SDK: `/home/maxime/goProject/github.com/refractionPOINT/go-limacharlie/limacharlie/validation.go`
- API: `/home/maxime/goProject/github.com/refractionPOINT/lc_api-go/service/endpoint_usp_validation.go`
- Backend: `/home/maxime/goProject/github.com/refractionPOINT/legion_usp_proxy/service/validation.go`
- RPC: `/home/maxime/goProject/github.com/refractionPOINT/go-ironlegionprotocol/ilp/Actor.go`
- MCP: `/home/maxime/goProject/github.com/refractionPOINT/lc-mcp-server/internal/tools/rules/usp_validation.go`

## Additional Notes

The raw API response format is correct - it returns `ParsedEventResult` structs with all the right fields. The issue is just that parsing never happens, so we get the fallback `{"text": "..."}` payload.
