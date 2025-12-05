# add_output

Create a new output configuration to export data to external systems.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| oid | UUID | Yes | Organization ID ([Core Concepts](../../../CALLING_API.md#core-concepts)) |
| name | string | Yes | Unique output name |
| module | string | Yes | Output type (syslog, s3, webhook, slack, gcs, elastic, kafka) |
| output_type | string | Yes | Data type: event, detect, audit, deployment, artifact |

### Module-Specific Required Parameters

| Module | Required | Optional |
|--------|----------|----------|
| syslog | dest_host | dest_port, is_tls |
| s3 | bucket | region_name, secret_key |
| webhook | dest_host (URL) | auth_header_name, auth_header_value |
| slack | slack_api_token, slack_channel | - |
| gcs | bucket, key_id | - |
| elastic | dest_host, username, password | index |
| kafka | addresses, topic | - |

### Optional Filtering

| Parameter | Description |
|-----------|-------------|
| tag | Filter by sensor tag |
| tag_black_list | Exclude specific tags |
| sid | Filter by sensor ID |
| cat | Filter detections by category |
| event_white_list | Include specific event types |
| event_black_list | Exclude specific event types |

## Returns

```json
{
  "name": "prod-syslog",
  "module": "syslog",
  "for": "event",
  "dest_host": "10.0.1.50"
}
```

## Examples

**Syslog output:**
```
lc_call_tool(tool_name="add_output", parameters={
  "oid": "c7e8f940-...",
  "name": "prod-syslog",
  "module": "syslog",
  "output_type": "event",
  "dest_host": "10.0.1.50",
  "dest_port": "514",
  "is_tls": "true"
})
```

**S3 archive:**
```
lc_call_tool(tool_name="add_output", parameters={
  "oid": "c7e8f940-...",
  "name": "detection-archive",
  "module": "s3",
  "output_type": "detect",
  "bucket": "lc-detections",
  "region_name": "us-west-2",
  "tag": "production"
})
```

**Webhook with auth:**
```
lc_call_tool(tool_name="add_output", parameters={
  "oid": "c7e8f940-...",
  "name": "alert-webhook",
  "module": "webhook",
  "output_type": "detect",
  "dest_host": "https://api.example.com/alerts",
  "auth_header_name": "X-API-Key",
  "auth_header_value": "[secret:webhook-api-key]"
})
```

## Notes

- Outputs become active immediately
- Cannot modify outputs - delete and recreate to change
- Boolean fields must be strings: `"true"` or `"false"`
- Use `[secret:name]` for credentials
- Related: `list_outputs`, `delete_output`
