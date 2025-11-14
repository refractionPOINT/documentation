
# Set Cloud Sensor

Create a new cloud sensor or update an existing cloud sensor configuration for cloud platform and SaaS integrations.

## When to Use

Use this skill when the user needs to:
- Configure a new cloud sensor for AWS, Azure, GCP, or SaaS platforms
- Update an existing cloud sensor's configuration or credentials
- Enable or disable a cloud sensor
- Modify cloud sensor tags for organization
- Update connection parameters for cloud integrations
- Reconfigure cloud sensor after credential rotation

Common scenarios:
- Initial setup of cloud data source integrations
- Updating expired or rotated credentials
- Changing cloud sensor regions or scopes
- Enabling previously disabled cloud sensors
- Adding tags to organize cloud sensors
- Fixing configuration errors in cloud integrations

## What This Skill Does

This skill creates or updates a cloud sensor configuration in the organization's Hive storage. Cloud sensors are virtual sensors that collect telemetry from cloud platforms and SaaS services without requiring endpoint agents. The configuration includes the sensor type, connection parameters (credentials, regions, tenants), and metadata. The skill calls the LimaCharlie Hive API to store the sensor configuration with automatic enablement. If a sensor with the same name exists, it will be updated; otherwise, a new sensor is created.

## Required Information

Before calling this skill, gather:

**⚠️ IMPORTANT**: The Organization ID (OID) is a UUID (like `c1ffedc0-ffee-4a1e-b1a5-abc123def456`), **NOT** the organization name. If you don't have the OID, use the `list-user-orgs` skill first to get the OID from the organization name.
- **oid**: Organization ID (required for all API calls)
- **sensor_name**: Name for the cloud sensor (required, alphanumeric with hyphens/underscores)
- **sensor_config**: Complete configuration object (required, structure varies by sensor type)

The sensor_config structure depends on the cloud platform or service:
- **AWS CloudTrail**: aws_region, s3_bucket, role_arn, external_id
- **Azure Activity Logs**: subscription_id, tenant_id, client_id, client_secret
- **GCP Audit Logs**: project_id, service_account_json
- **Office 365**: tenant_id, client_id, client_secret, content_types
- **Okta**: domain, api_token
- Other platforms have their own specific requirements

## How to Use

### Step 1: Validate Parameters

Ensure you have:
1. Valid organization ID (oid)
2. Unique sensor name (or name of existing sensor to update)
3. Complete sensor configuration with all required fields for the sensor type
4. Valid credentials and connection parameters
5. Understanding of the cloud platform's authentication requirements

### Step 2: Call the API

Use the `lc_api_call` MCP tool from the `limacharlie` server:

```
mcp__limacharlie__lc_api_call(
  oid="[organization-id]",
  endpoint="api",
  method="POST",
  path="/hive/cloud_sensor/global/[sensor-name]/data",
  body={
    "gzdata": "[base64-gzip-encoded-json]",
    "usr_mtd": {
      "enabled": true,
      "tags": ["tag1", "tag2"],
      "comment": "Sensor description",
      "expiry": 0
    }
  }
)
```

**Note**: The body requires `gzdata` which is a gzip-compressed, base64-encoded JSON string of the sensor configuration. For simplicity in this documentation, we show the uncompressed structure. The MCP tool handles compression automatically.

**Simplified API call** (MCP tool handles encoding):
```
The actual implementation uses the Hive Add method which:
1. Takes the sensor_config as a Dict
2. Automatically gzip-compresses and base64-encodes it
3. Sets usr_mtd with enabled=true by default
4. Posts to /hive/cloud_sensor/global/{sensor-name}/data
```

**API Details:**
- Endpoint: `api`
- Method: `POST`
- Path: `/hive/cloud_sensor/global/{sensor-name}/data`
- Body fields:
  - `gzdata`: Compressed and encoded sensor configuration
  - `usr_mtd`: User metadata (enabled, tags, comment, expiry)
  - `etag` (optional): For optimistic concurrency control during updates

### Step 3: Handle the Response

The API returns a response with:
```json
{
  "status_code": 200,
  "status": "200 OK",
  "body": {
    "guid": "unique-sensor-guid",
    "hive": {
      "name": "cloud_sensor",
      "partition": "global"
    },
    "name": "sensor-name"
  }
}
```

**Success (200-299):**
- The cloud sensor has been created or updated successfully
- The response contains the sensor's GUID and hive information
- The sensor is automatically enabled unless specified otherwise
- The sensor will begin collecting data based on its configuration

**Common Errors:**
- **400 Bad Request**: Missing required fields, invalid configuration structure, or malformed sensor_config
- **401 Unauthorized**: Authentication token is invalid or expired
- **403 Forbidden**: Insufficient permissions to manage cloud sensors (requires fleet_management role)
- **409 Conflict**: ETag mismatch if updating existing sensor with concurrent modifications
- **500 Server Error**: Internal server error, retry the request

### Step 4: Format the Response

Present the result to the user:
- Confirm successful creation or update of the cloud sensor
- Display the sensor name and type
- Show the enabled status
- List any tags applied
- Provide guidance on verifying data collection
- Suggest checking the sensor after a few minutes to confirm data ingestion
- For updates, note what changed

## Example Usage

### Example 1: Create AWS CloudTrail cloud sensor

User request: "Set up a cloud sensor for our AWS CloudTrail logs in the production environment"

Steps:
1. Extract organization ID from context
2. Prepare sensor name: "prod-aws-cloudtrail"
3. Gather AWS configuration: region, S3 bucket, role ARN, external ID
4. Call API:
```
mcp__limacharlie__lc_api_call(
  oid="c7e8f940-1234-5678-abcd-1234567890ab",
  endpoint="api",
  method="POST",
  path="/hive/cloud_sensor/global/prod-aws-cloudtrail/data",
  body={
    "gzdata": "[base64-encoded-gzipped-json-of-config]",
    "usr_mtd": {
      "enabled": true,
      "tags": ["aws", "production", "cloudtrail"],
      "comment": "Production AWS CloudTrail integration",
      "expiry": 0
    }
  }
)
```

Where the config (before encoding) is:
```json
{
  "sensor_type": "aws_cloudtrail",
  "aws_region": "us-east-1",
  "s3_bucket": "my-cloudtrail-logs",
  "role_arn": "arn:aws:iam::123456789012:role/LCCloudTrail",
  "external_id": "lc-ext-id-12345"
}
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "guid": "abc-123-def-456",
    "hive": {
      "name": "cloud_sensor",
      "partition": "global"
    },
    "name": "prod-aws-cloudtrail"
  }
}
```

Present to user:
```
Successfully created AWS CloudTrail cloud sensor!

Sensor Name: prod-aws-cloudtrail
Type: AWS CloudTrail
Status: Enabled
Tags: aws, production, cloudtrail

Configuration:
- AWS Region: us-east-1
- S3 Bucket: my-cloudtrail-logs
- Role ARN: arn:aws:iam::123456789012:role/LCCloudTrail

The sensor will begin collecting CloudTrail logs from your S3 bucket.
Check back in a few minutes to verify data is flowing.
```

### Example 2: Update Office 365 sensor with new credentials

User request: "Update the office365-audit sensor with the new client secret after rotation"

Steps:
1. Get existing sensor configuration (use get-cloud-sensor skill)
2. Update only the client_secret field
3. Call API with updated configuration:
```
The sensor_config would include:
{
  "sensor_type": "office365",
  "tenant_id": "abc-123-def",
  "client_id": "client-id-456",
  "client_secret": "new-secret-789",
  "content_types": ["Audit.General", "Audit.Exchange"]
}
```

Expected response:
```json
{
  "status_code": 200,
  "body": {
    "guid": "existing-guid",
    "name": "office365-audit"
  }
}
```

Present to user:
```
Successfully updated Office 365 cloud sensor!

Sensor Name: office365-audit
Status: Enabled
Changes: Updated client secret

The sensor should now authenticate successfully and resume data collection.
Monitor the sensor for the next few minutes to confirm no authentication errors.
```

### Example 3: Enable a disabled cloud sensor

User request: "Enable the azure-activity-logs sensor"

Steps:
1. Get existing configuration
2. Update with enabled=true in usr_mtd
3. Call API

Present to user:
```
Successfully enabled cloud sensor 'azure-activity-logs'.

The sensor is now active and will resume collecting Azure Activity Logs.
```

## Additional Notes

- Cloud sensors use the Hive storage system under `cloud_sensor` hive with `global` partition
- Sensor names must be unique within the organization
- The sensor_config structure is specific to each cloud platform or SaaS service
- Required fields vary by sensor type - consult platform-specific documentation
- Credentials in sensor configurations are sensitive - handle securely
- The sensor is automatically enabled unless explicitly disabled in usr_mtd
- Tags are useful for organizing sensors by environment, platform, or team
- Use meaningful sensor names that indicate the platform and purpose
- When updating, the entire configuration is replaced - include all fields
- For credential rotation, update the sensor configuration with new credentials
- The `etag` field can be used for concurrent update protection
- After creating or updating, allow a few minutes for data collection to begin
- Check the sensor's last_error field if data isn't appearing (use get-cloud-sensor)
- Common sensor types and their key configuration fields:
  - **AWS CloudTrail**: sensor_type, aws_region, s3_bucket, role_arn, external_id
  - **AWS GuardDuty**: sensor_type, aws_region, role_arn, external_id
  - **Azure Activity Logs**: sensor_type, subscription_id, tenant_id, client_id, client_secret
  - **GCP Audit Logs**: sensor_type, project_id, service_account_json
  - **Office 365**: sensor_type, tenant_id, client_id, client_secret, content_types
  - **Okta**: sensor_type, domain, api_token
- Use list-cloud-sensors to verify the sensor was created
- Use get-cloud-sensor to inspect the configuration after creation
- Use delete-cloud-sensor to remove sensors that are no longer needed

## Reference

For more details on using `lc_api_call`, see [CALLING_API.md](../../CALLING_API.md).

For the Go SDK implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/go-limacharlie/limacharlie/hive.go`
For the MCP tool implementation, check: `/home/maxime/goProject/github.com/refractionPOINT/lc-mcp-server/internal/tools/hive/cloud_sensors.go`
