# Output Troubleshooting Guide

Comprehensive troubleshooting guide for LimaCharlie output configurations organized by issue type.

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [No Data Appearing](#no-data-appearing)
3. [Authentication Failures](#authentication-failures)
4. [High Costs](#high-costs)
5. [Intermittent Failures](#intermittent-failures)
6. [Performance Issues](#performance-issues)
7. [Data Format Issues](#data-format-issues)
8. [Destination-Specific Issues](#destination-specific-issues)

---

## Connection Issues

### Symptom: Output shows as failed/disabled

**Check Platform Logs**:
1. Navigate to **Platform Logs** > **Errors**
2. Filter by key: `outputs/<output-name>`
3. Review error messages

**Common Causes**:

#### Network Connectivity
- Destination endpoint not accessible from internet
- Firewall blocking LimaCharlie IP ranges
- DNS resolution failure
- Port not open

**Solution**:
```bash
# Test connectivity from external machine
curl -v https://destination-host.com:port

# Check DNS resolution
nslookup destination-host.com

# Test with telnet
telnet destination-host.com port
```

#### Invalid Endpoint URL
- Typo in `dest_host`
- Missing protocol (`https://`)
- Wrong port
- Invalid path

**Solution**:
- Verify URL format: `https://host:port/path`
- Test endpoint manually with curl
- Check destination documentation for correct endpoint

#### SSL/TLS Certificate Issues
- Self-signed certificate
- Expired certificate
- Certificate hostname mismatch

**Solution**:
For testing (not production):
```yaml
is_strict_tls: "false"
```

For production:
- Use valid SSL certificate
- Ensure certificate includes correct hostname
- Check certificate expiration date

### Symptom: Output fails immediately after creation

**Checklist**:
1. Verify destination system is online
2. Check credentials are correct
3. Ensure required ports are open
4. Test authentication manually

**Quick Test**:
1. Change output to `audit` stream
2. Make any configuration change
3. Wait 1-2 minutes
4. Check Platform Logs
5. Verify event at destination

---

## No Data Appearing

### Symptom: Output status green, but no data at destination

**Step 1: Verify Events Are Being Generated**

Check LimaCharlie Timeline:
1. Navigate to **Timeline**
2. Select time range
3. Verify events exist for selected stream type

**For event stream**:
- Should see process creation, network connections, etc.
- If no events, check sensor connectivity

**For detection stream**:
- Should see detection alerts
- If no detections, verify D&R rules are enabled and firing

**For audit stream**:
- Make configuration change to generate audit event

**Step 2: Check Output Filters**

Review output configuration for overly restrictive filters:

**Tag filter**:
```yaml
tag: production
```
- Verify sensors have the specified tag
- Check: **Sensors** > Select sensor > View tags

**Sensor filter**:
```yaml
sensor: <sensor-id>
```
- Verify sensor ID is correct
- Check sensor is online and sending events

**Event type filters**:
```yaml
detection_categories:
  - NEW_PROCESS
  - NETWORK_CONNECTIONS
```
- Verify events match allowed types
- Check if list is too restrictive

**Step 3: Check Batching Interval**

For batched outputs (S3, GCS, webhook_bulk):
```yaml
sec_per_file: 300
```
- Wait full duration before expecting data
- Default: 5 minutes (300 seconds)
- Events accumulated before sending

**Solution**: Wait full `sec_per_file` duration, then check destination.

**Step 4: Check Destination System**

**For cloud storage (S3, GCS)**:
- List files/objects in bucket
- Verify correct path/prefix
- Check for recent upload timestamps

**For SIEM (Splunk, Elastic)**:
- Search with wide time range
- Check correct index
- Verify no ingestion errors in destination logs

**For webhooks**:
- Check receiver access logs
- Verify endpoint is accessible
- Check for firewall blocks

### Symptom: Some events missing, not all

**Possible Causes**:

#### Rate Limiting at Destination
- Destination rejecting some requests
- HTTP 429 Too Many Requests errors

**Solution**:
- Use bulk webhook instead of individual
- Increase `sec_per_file` to reduce request frequency
- Check destination rate limits

#### Event Type Filtering
- Only specific event types sent
- Filters excluding expected events

**Solution**:
- Review `detection_categories` and `disallowed_detection_categories`
- Check if expected events match filters

#### Sensor Tag/Filter
- Only events from specific sensors sent
- Tags not applied to all sensors

**Solution**:
- Verify sensor tags in **Sensors** view
- Consider removing tag filter for testing

---

## Authentication Failures

### Symptom: 401 Unauthorized or 403 Forbidden errors

**Common Authentication Issues by Destination**:

### AWS S3

**Check IAM Credentials**:
```bash
# Test credentials with AWS CLI
aws configure set aws_access_key_id AKIAIOSFODNN7EXAMPLE
aws configure set aws_secret_access_key wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
aws configure set region us-east-1

# Test S3 access
aws s3 ls s3://bucket-name
aws s3 cp test.txt s3://bucket-name/test.txt
```

**Common Issues**:
- Access key disabled or deleted
- Secret key incorrect
- IAM policy doesn't include `s3:PutObject`
- Bucket policy doesn't allow IAM user
- Wrong region specified

**Solution**:
1. Verify credentials in AWS Console
2. Check IAM policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": "s3:PutObject",
    "Resource": "arn:aws:s3:::bucket-name/*"
  }]
}
```
3. Verify bucket policy allows IAM user

### GCP (GCS, BigQuery, Pub/Sub)

**Check Service Account**:
```bash
# Test service account
gcloud auth activate-service-account \
  --key-file=key.json

# Test GCS access
gsutil ls gs://bucket-name
gsutil cp test.txt gs://bucket-name/

# Test BigQuery access
bq ls --project_id=my-project
```

**Common Issues**:
- Service account key revoked
- JSON key format incorrect
- Missing required roles
- Project ID mismatch

**Required Roles**:
- GCS: "Storage Object Creator"
- BigQuery: "BigQuery Data Editor"
- Pub/Sub: "Pub/Sub Publisher"

**Solution**:
1. Verify service account in GCP Console
2. Check roles assigned to service account
3. Regenerate key if necessary
4. Ensure entire JSON key copied to `secret_key` field

### Splunk HEC

**Check HEC Token**:
```bash
# Test HEC endpoint
curl -k https://splunk-host.com:8088/services/collector/raw \
  -H "Authorization: Splunk EA12XXXX-XXXX-XXXX-XXXX-XXXXXXXXXX34" \
  -d '{"test": "event"}'
```

**Expected Response**: `{"text":"Success","code":0}`

**Common Issues**:
- HEC token disabled
- Token not found
- HEC endpoint not configured
- Wrong endpoint path

**Solution**:
1. Verify token in Splunk: **Settings > Data Inputs > HTTP Event Collector**
2. Ensure token is enabled
3. Use `/services/collector/raw` for raw JSON
4. Check HEC is globally enabled

### Elastic

**Check Authentication**:
```bash
# Test with username/password
curl -u elastic_user:password https://elastic-host:9200/_cluster/health

# Test with API key
curl -H "Authorization: ApiKey base64-encoded-key" \
  https://elastic-host:9200/_cluster/health
```

**Common Issues**:
- Wrong username/password
- API key expired or revoked
- User doesn't have write permissions
- Index doesn't exist

**Solution**:
1. Verify credentials in Elasticsearch
2. Check user has appropriate role
3. Create index if missing
4. Regenerate API key if necessary

### Slack

**Check Bot Token**:
```bash
# Test Slack API
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer xoxb-token" \
  -H "Content-Type: application/json" \
  -d '{"channel":"#test","text":"Test message"}'
```

**Common Issues**:
- Token starts with `xoxp-` instead of `xoxb-` (wrong token type)
- Bot not installed to workspace
- Bot not invited to channel
- Token revoked

**Solution**:
1. Verify token starts with `xoxb-`
2. Reinstall app to workspace if needed
3. Invite bot to channel: `/invite @bot-name`
4. Check app has `chat:write` scope

---

## High Costs

### Symptom: Unexpected output billing charges

**Understand Output Billing**:
- LimaCharlie bills outputs at cost (see https://limacharlie.io/pricing)
- Exception: GCP outputs in same region as LimaCharlie datacenter are FREE

**Check Current Usage**:
1. Navigate to **Billing** in LimaCharlie console
2. View output bandwidth usage
3. Identify high-volume outputs

**Cost Optimization Strategies**:

### 1. Use Free GCP Outputs

Configure GCP outputs in matching region:

LimaCharlie regions:
- USA: `us-central1`
- Canada: `northamerica-northeast1`
- Europe: `europe-west4`
- UK: `europe-west2`
- India: `asia-south1`
- Australia: `australia-southeast1`

**Example - GCS in matching region**:
```yaml
# Create GCS bucket in us-central1
bucket: my-security-archive
# Location: us-central1 (FREE for USA org)
```

**Savings**: 100% output cost reduction

### 2. Enable Compression

For S3 and GCS outputs:
```yaml
is_compression: "true"
```

**Savings**: ~70% reduction in data transfer and storage costs

**Before**: 100 GB/month uncompressed
**After**: 30 GB/month compressed
**Cost reduction**: 70 GB × $0.05/GB = $3.50/month per output

### 3. Exclude Routing Metadata

Routing labels add significant overhead:
```yaml
is_no_routing: true
```

**Typical savings**: 20-30% size reduction

**Before**:
```json
{
  "routing": {
    "oid": "org-id",
    "sid": "sensor-id",
    "hostname": "host",
    "event_type": "NEW_PROCESS",
    "tags": ["prod", "web", "linux"],
    ...
  },
  "event": {...}
}
```

**After**:
```json
{
  "event": {...}
}
```

### 4. Use Event Type Filters

Reduce volume by filtering unnecessary events:

**Allow only critical events**:
```yaml
detection_categories:
  - NEW_PROCESS
  - NETWORK_CONNECTIONS
  - FILE_CREATE
```

**Exclude high-volume, low-value events**:
```yaml
disallowed_detection_categories:
  - DNS_REQUEST
  - FILE_GET_REP
  - FILE_READ
```

**Savings**: 50-80% volume reduction depending on filters

### 5. Use Tailored Streams

Most cost-effective for specific monitoring:

```yaml
stream: tailored
```

Forward only specific events via D&R rules:
```yaml
respond:
  - action: output
    name: output-name
```

**Savings**: 90-99% volume reduction for targeted use cases

### 6. Increase Batch Intervals

For storage outputs, reduce file frequency:
```yaml
sec_per_file: 600  # 10 minutes instead of 5
```

**Savings**: Reduces API call overhead costs

**Trade-off**: Longer delay before data available

### 7. Use Multiple Targeted Outputs

Instead of single full event stream, use multiple filtered outputs:

**Approach 1: Single output, full event stream**
- Cost: High (all events)
- Use: Data lake

**Approach 2: Multiple outputs**
- Output 1: Detections to SIEM (low volume)
- Output 2: Critical events to S3 (filtered, compressed)
- Output 3: Audit events to Slack (very low volume)
- Cost: Low (only necessary events)

### Volume Estimation Tool

Calculate expected costs:

**Formula**:
```
Monthly GB = Endpoints × MB per endpoint per day × 30 days / 1024
Monthly Cost = Monthly GB × $0.05 per GB
```

**Example**:
- 500 endpoints
- 20 MB per endpoint per day (event stream)
- Uncompressed

```
Monthly GB = 500 × 20 × 30 / 1024 = 293 GB
Monthly Cost = 293 × $0.05 = $14.65
```

**With optimization**:
- Enable compression (70% reduction): 88 GB
- Use GCP in matching region: $0

---

## Intermittent Failures

### Symptom: Output sometimes works, sometimes fails

**Common Causes**:

### 1. Destination Rate Limiting

**Symptoms**:
- HTTP 429 errors in Platform Logs
- Success during low traffic, failures during high traffic

**Solution**:
- Use bulk webhooks to reduce request frequency
- Increase `sec_per_file` interval
- Contact destination provider for rate limit increase

**Example - Switch to bulk**:
```yaml
# Before: Individual webhook (high request rate)
destination: webhook

# After: Bulk webhook (batched requests)
destination: webhook_bulk
sec_per_file: 300
```

### 2. Destination Capacity Issues

**Symptoms**:
- HTTP 503 Service Unavailable errors
- Timeouts during high load

**Solution**:
- Scale destination infrastructure
- Use batching to smooth out load
- Implement queuing at destination

### 3. Network Instability

**Symptoms**:
- Connection timeout errors
- Intermittent DNS resolution failures

**Solution**:
- Check destination network status
- Use multiple destination addresses (e.g., Elastic cluster)
- Contact destination network team

### 4. Credential Expiration

**Symptoms**:
- Works for days/weeks, then suddenly fails
- Authentication errors after period of success

**Solution**:
- Check for expiring credentials:
  - AWS IAM keys
  - GCP service account keys
  - API tokens
  - OAuth tokens
- Implement credential rotation schedule
- Set up expiration alerts

### 5. Quota Limits

**Symptoms**:
- Works at beginning of period
- Fails later in period
- Errors mentioning quota or limits

**Solution**:

**AWS S3**:
- Check S3 service quotas
- Request quota increase if needed

**GCP**:
- Check BigQuery streaming quotas
- Monitor Pub/Sub quotas

**Elastic**:
- Check index write quotas
- Monitor disk space

### 6. Auto-Scaling Issues

**Symptoms**:
- Failures during traffic spikes
- Success during normal load

**Solution**:
- Pre-warm destination infrastructure
- Configure auto-scaling appropriately
- Use load balancer with health checks

---

## Performance Issues

### Symptom: Delays in data delivery

**Check Batch Settings**:

For batched outputs:
```yaml
sec_per_file: 300  # 5 minute delay expected
```

**Expected Delays**:
- Individual webhook: <1 second
- Bulk webhook: `sec_per_file` seconds
- S3/GCS: `sec_per_file` seconds
- BigQuery: `sec_per_file` seconds

**Solutions**:

### Reduce Batch Time
```yaml
sec_per_file: 60  # 1 minute instead of 5
```
**Trade-off**: More API calls, higher costs

### Use Individual Webhook
For low-volume, time-sensitive streams:
```yaml
destination: webhook  # Instead of webhook_bulk
```

### Symptom: Destination processing slow

**Common Causes**:

#### Large Events
- Events with large payloads
- Many nested fields

**Solution**:
- Use `flatten: true` to simplify structure
- Filter unnecessary fields with custom_transform

#### High Volume
- Destination can't keep up with event rate

**Solution**:
- Scale destination infrastructure
- Use batching to smooth load
- Implement buffering at destination

---

## Data Format Issues

### Symptom: Data format incorrect at destination

**Common Issues**:

### 1. BigQuery Schema Mismatch

**Error**: "Field X does not match schema"

**Solution**:
1. Verify schema string matches table EXACTLY:
```yaml
schema: field1:TYPE1, field2:TYPE2, field3:TYPE3
```

2. Check custom_transform maps all schema fields:
```yaml
custom_transform: |
  {
    "field1": "routing.hostname",
    "field2": "routing.event_type",
    "field3": "cat"
  }
```

3. Verify field types match:
- STRING, INTEGER, FLOAT, BOOLEAN, TIMESTAMP

### 2. JSON Structure Issues

**Issue**: Nested JSON not supported by destination

**Solution**:
```yaml
flatten: true
```

**Before**:
```json
{
  "routing": {
    "hostname": "HOST",
    "oid": "org-id"
  }
}
```

**After**:
```json
{
  "routing.hostname": "HOST",
  "routing.oid": "org-id"
}
```

### 3. Missing Fields

**Issue**: Expected fields not in output

**Solution**:
Check if `is_no_routing: true` removed necessary metadata:
```yaml
# Remove is_no_routing if routing fields needed
is_no_routing: false
```

### 4. Custom Transform Not Applied

**Issue**: Events not formatted as expected

**Solution**:
1. Verify Go template syntax correct
2. Check field paths match event structure
3. Test template with sample event

**Example**:
```yaml
custom_transform: |
  {
    "host": "{{ .routing.hostname }}",
    "type": "{{ .routing.event_type }}",
    "time": "{{ .routing.this_ts }}"
  }
```

---

## Destination-Specific Issues

### Splunk Issues

#### Issue: Events not appearing in Splunk

**Check**:
1. HEC globally enabled: **Settings > Data Inputs > HTTP Event Collector > Global Settings**
2. Token enabled for specific input
3. Index exists and not frozen
4. Source type set to `_json`

**Debug**:
```bash
# Check Splunk HEC logs
tail -f /opt/splunk/var/log/splunk/splunkd.log | grep HEC
```

#### Issue: Parsing errors in Splunk

**Solution**:
Use `/services/collector/raw` endpoint (not `/services/collector/event`)

```yaml
dest_host: https://splunk.com:8088/services/collector/raw
```

### Elastic Issues

#### Issue: Index creation errors

**Solution**:
Pre-create index with correct mapping:
```bash
curl -X PUT "https://elastic-host:9200/limacharlie" \
  -H "Content-Type: application/json" \
  -d '{
    "mappings": {
      "properties": {
        "routing": {"type": "object"},
        "event": {"type": "object"}
      }
    }
  }'
```

#### Issue: Cloud ID connection fails

**Solution**:
Verify Cloud ID format:
```yaml
cloud_id: "deployment-name:base64-encoded-string"
```

Get from Elastic Cloud deployment page.

### S3 Issues

#### Issue: Access Denied errors

**Check**:
1. IAM user has `s3:PutObject` permission
2. Bucket policy allows IAM user
3. Bucket exists
4. Region matches configuration

**Debug**:
```bash
# Test with AWS CLI
aws s3 cp test.txt s3://bucket-name/test.txt \
  --region us-east-1
```

#### Issue: Files not compressed

**Solution**:
Ensure compression enabled:
```yaml
is_compression: "true"  # Must be string, not boolean
```

### GCS Issues

#### Issue: Service account authentication fails

**Check**:
1. Service account has "Storage Object Creator" role
2. JSON key format correct (entire JSON in `secret_key`)
3. Project ID matches bucket project

**Debug**:
```bash
# Test with gcloud
gcloud auth activate-service-account --key-file=key.json
gsutil ls gs://bucket-name
```

### BigQuery Issues

#### Issue: Schema errors

**Solution**:
1. Schema must match table EXACTLY
2. Custom transform must map ALL schema fields
3. Field types must match

**Verify**:
```bash
# Check table schema
bq show --schema my-project:dataset.table

# Compare with output configuration
```

### Slack Issues

#### Issue: Bot not posting messages

**Check**:
1. Token starts with `xoxb-` (not `xoxp-`)
2. Bot invited to channel: `/invite @bot-name`
3. Bot has `chat:write` scope
4. Channel name includes `#`

**Test**:
```bash
curl -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer xoxb-token" \
  -H "Content-Type: application/json" \
  -d '{"channel":"#test","text":"Test"}'
```

#### Issue: Too many messages / rate limiting

**Solution**:
1. Add stricter filters
2. Use detection_categories to limit
3. Consider webhook with custom formatting instead

---

## Diagnostic Checklist

When troubleshooting any output issue, follow this checklist:

### Step 1: Check Platform Logs
1. Navigate to **Platform Logs** > **Errors**
2. Filter by `outputs/<output-name>`
3. Note specific error messages

### Step 2: Verify Output Configuration
1. Check destination endpoint URL
2. Verify authentication credentials
3. Confirm stream type is correct
4. Review filters (tag, sensor, event types)

### Step 3: Test with Audit Stream
1. Temporarily change to `audit` stream
2. Make configuration change to trigger audit event
3. Wait 1-2 minutes
4. Check if event arrives at destination
5. If works, switch back to original stream

### Step 4: Check Destination System
1. Verify destination is online and accessible
2. Check destination logs for errors
3. Confirm network connectivity
4. Test authentication manually

### Step 5: Verify Events Exist
1. Check LimaCharlie Timeline for events
2. Confirm sensors are online
3. Verify D&R rules are enabled (for detection stream)
4. Check filters aren't too restrictive

### Step 6: Test Manually
1. Use curl to test endpoint
2. Verify authentication with destination CLI
3. Check network connectivity with telnet/nc
4. Review destination documentation

### Step 7: Simplify Configuration
1. Remove all filters temporarily
2. Use simplest authentication method
3. Test with minimal configuration
4. Add complexity incrementally

### Step 8: Get Help
If still stuck:
1. Collect Platform Logs errors
2. Document configuration (redact credentials)
3. Note troubleshooting steps attempted
4. Contact LimaCharlie support: support@limacharlie.io
5. Join Community Slack: https://slack.limacharlie.io

---

## Common Error Messages

### "Connection refused"
- Destination not listening on specified port
- Firewall blocking connection
- Wrong port in configuration

### "Connection timeout"
- Network connectivity issue
- Destination not responding
- Firewall blocking outbound connection

### "SSL certificate verify failed"
- Self-signed certificate
- Expired certificate
- Certificate hostname mismatch
- Solution: Set `is_strict_tls: "false"` (testing only)

### "401 Unauthorized" / "403 Forbidden"
- Invalid credentials
- Expired token
- Insufficient permissions
- Wrong authentication method

### "404 Not Found"
- Wrong endpoint URL
- Incorrect path
- Destination resource doesn't exist

### "429 Too Many Requests"
- Rate limit exceeded
- Solution: Use bulk output, increase `sec_per_file`

### "500 Internal Server Error"
- Destination system error
- Check destination logs
- Contact destination support

### "Schema mismatch" (BigQuery)
- Schema string doesn't match table
- Custom transform missing fields
- Field type mismatch
- Solution: Verify schema and transform

### "Access Denied" (AWS/GCP)
- Insufficient IAM/service account permissions
- Bucket/resource policy doesn't allow access
- Wrong project/account ID
- Solution: Review and update permissions

---

## Preventing Issues

### Configuration Best Practices

1. **Always Test First**
   - Start with audit stream
   - Verify configuration before switching to production stream
   - Test authentication manually before configuring output

2. **Use Descriptive Names**
   ```yaml
   name: splunk-production-detections
   # Better than: name: output1
   ```

3. **Document Configuration**
   - Keep records of output purposes
   - Document credential sources
   - Note any special configuration

4. **Implement Monitoring**
   - Regularly check Platform Logs
   - Set up alerts for output failures
   - Monitor destination system health

5. **Rotate Credentials**
   - Establish rotation schedule
   - Use service accounts over user credentials
   - Set expiration reminders

6. **Filter Appropriately**
   - Start broad, narrow down
   - Use tag filters to limit scope
   - Implement event type filters for volume control

7. **Enable Compression**
   - Always use for storage outputs
   - Reduces costs and transfer time
   ```yaml
   is_compression: "true"
   ```

8. **Use HMAC for Webhooks**
   - Always set `secret_key`
   - Implement signature verification at receiver
   - Protects against unauthorized events

9. **Plan for Scale**
   - Estimate data volumes before enabling event stream
   - Use bulk outputs for high volume
   - Monitor bandwidth usage

10. **Have Backup Plan**
    - Configure multiple outputs for critical data
    - Document recovery procedures
    - Keep destination credentials secure and backed up

---

## Getting Help

If you're unable to resolve the issue:

**LimaCharlie Support**:
- Email: support@limacharlie.io
- Community Slack: https://slack.limacharlie.io
- Documentation: /home/maxime/goProject/github.com/refractionPOINT/documentation/limacharlie/doc/Outputs/

**Destination Vendor Support**:
- Splunk: https://docs.splunk.com
- AWS: https://aws.amazon.com/support
- GCP: https://cloud.google.com/support
- Elastic: https://www.elastic.co/support

**Information to Provide**:
1. Output configuration (redact credentials)
2. Platform Logs errors
3. Destination system errors
4. Troubleshooting steps attempted
5. Expected vs. actual behavior
6. Timeline of issue (always failing vs. started recently)
