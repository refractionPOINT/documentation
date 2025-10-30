# External Telemetry Onboarding Troubleshooting

This guide helps you diagnose and fix common issues when onboarding external data sources to LimaCharlie.

## Table of Contents

1. [General Troubleshooting Workflow](#general-troubleshooting-workflow)
2. [Authentication and Permission Errors](#authentication-and-permission-errors)
3. [Connection and Network Issues](#connection-and-network-issues)
4. [Data Not Appearing](#data-not-appearing)
5. [Parsing and Mapping Errors](#parsing-and-mapping-errors)
6. [Adapter Not Starting](#adapter-not-starting)
7. [Platform-Specific Issues](#platform-specific-issues)
8. [Validation Checklist](#validation-checklist)

---

## General Troubleshooting Workflow

When experiencing issues, follow this systematic approach:

### Step 1: Check Adapter/Sensor Status

```bash
# List all sensors and look for your adapter
limacharlie sensor list

# Check specific sensor status
limacharlie sensor info --sensor-id <SID>
```

**Sensor States**:
- **Online/Active**: Adapter is connected and working
- **Offline**: Adapter disconnected (check if process is running)
- **Error**: Connection or configuration issue
- **Not showing up**: Adapter never connected (check logs)

### Step 2: Review Adapter Logs

**For on-prem adapters**:
```bash
# If running as systemd service
sudo journalctl -u limacharlie-adapter -n 100 -f

# If running in foreground
# Check stdout/stderr output
```

**For cloud-to-cloud adapters**:
```bash
# Check via MCP
limacharlie sensor logs --sensor-id <SID>

# Or via web UI
# Navigate to Sensors → [Your Adapter] → Logs tab
```

### Step 3: Look for Common Error Patterns

| Error Pattern | Likely Cause | Jump To |
|---------------|--------------|---------|
| "authentication failed", "invalid credentials" | Wrong API key/secret | [Authentication Errors](#authentication-and-permission-errors) |
| "permission denied", "access denied", "forbidden" | Insufficient permissions | [Permission Errors](#aws-iam-permissions) |
| "connection refused", "timeout", "unreachable" | Network/firewall issue | [Connection Issues](#connection-and-network-issues) |
| "no events", "empty", "no data" | Data source not configured | [Data Not Appearing](#data-not-appearing) |
| "parse error", "invalid format", "unmarshal" | Parsing configuration wrong | [Parsing Errors](#parsing-and-mapping-errors) |
| "invalid configuration", "missing required field" | Config file error | [Configuration Errors](#adapter-not-starting) |

### Step 4: Enable Verbose Logging

For on-prem adapters, add debug output:

```bash
# Add to your adapter command
lc_adapter <type> <config> --debug

# Or set environment variable
export LC_ADAPTER_DEBUG=1
```

---

## Authentication and Permission Errors

### AWS: "Access Denied" or "InvalidAccessKeyId"

**Symptoms**:
- Error: `Access Denied`
- Error: `The AWS Access Key Id you provided does not exist in our records`
- Error: `SignatureDoesNotMatch`

**Solutions**:

1. **Verify credentials are correct**:
   ```bash
   # Test AWS credentials directly
   aws s3 ls s3://YOUR_BUCKET_NAME --profile test-profile

   # Configure test profile with your adapter credentials
   aws configure --profile test-profile
   # Enter Access Key ID and Secret Access Key
   ```

2. **Check IAM policy**:
   - Go to AWS IAM → Users → [Your User] → Permissions
   - Verify policy includes `s3:GetObject` and `s3:ListBucket`
   - Confirm bucket ARN matches exactly (case-sensitive)

3. **Validate bucket name**:
   - Bucket names are case-sensitive
   - No `s3://` prefix in config (just bucket name)
   - Check for typos

4. **Check key expiration**:
   - Access keys don't expire by default, but can be disabled
   - Verify key is "Active" in IAM console

**Correct IAM policy**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::your-exact-bucket-name/*",
        "arn:aws:s3:::your-exact-bucket-name"
      ]
    }
  ]
}
```

### Microsoft 365: "Unauthorized" or "Forbidden"

**Symptoms**:
- Error: `401 Unauthorized`
- Error: `403 Forbidden`
- Error: `AADSTS700016: Application not found`
- Events not appearing despite successful connection

**Solutions**:

1. **Grant admin consent**:
   - Azure Portal → App Registrations → [Your App] → API Permissions
   - Click **"Grant admin consent for [Organization]"**
   - All permissions should show green checkmarks
   - **This is the #1 missed step**

2. **Verify permission type**:
   - Must use **Application permissions** (not Delegated)
   - Required: `ActivityFeed.Read`
   - Optional: `ActivityFeed.ReadDlp` for DLP events

3. **Check client secret expiration**:
   - Azure Portal → App Registrations → [Your App] → Certificates & secrets
   - Verify secret hasn't expired
   - If expired, create new secret and update adapter config

4. **Verify tenant ID and client ID**:
   - App Registration → Overview page
   - Copy **Application (client) ID** (not Object ID)
   - Copy **Directory (tenant) ID**
   - For single-tenant apps, Publisher ID = Tenant ID

5. **Check M365 audit logging is enabled**:
   - Microsoft 365 Admin Center → Settings → Org settings → Security & privacy
   - Enable "Audit log search"
   - Can take up to 24 hours to activate initially

### Okta: "Invalid token" or "Unauthorized"

**Symptoms**:
- Error: `401 Unauthorized`
- Error: `Invalid API token`

**Solutions**:

1. **Regenerate API token**:
   - Okta Admin → Security → API → Tokens
   - Old tokens may be deactivated
   - Create new token, update adapter config

2. **Check token format**:
   - No extra spaces before/after token
   - No quotes around token in YAML (unless escaped)
   - Token is ~40 characters alphanumeric

3. **Verify Okta URL**:
   - Must include `https://`
   - Format: `https://your-domain.okta.com`
   - No trailing slash

### Azure: "Connection string invalid"

**Symptoms**:
- Error: `failed to parse connection string`
- Error: `EntityPath not found`

**Solutions**:

1. **Add EntityPath to connection string**:
   - Azure connection strings often don't include EntityPath
   - Manually append: `;EntityPath=YOUR_EVENT_HUB_NAME`
   - Full format:
     ```
     Endpoint=sb://namespace.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=KEY_HERE;EntityPath=hub-name
     ```

2. **Verify hub name is correct**:
   - EntityPath must match the Event Hub name (not namespace)
   - Case-sensitive

3. **Check access policy**:
   - Event Hub Namespace → Shared access policies
   - Policy must have "Listen" permission

### CrowdStrike: "Invalid client credentials"

**Symptoms**:
- Error: `invalid client credentials`
- Error: `access_denied`

**Solutions**:

1. **Verify API client is active**:
   - CrowdStrike Falcon → Support → API Clients and Keys
   - Client must be enabled (not disabled)

2. **Check API scope**:
   - Required scope: **Event streams: Read**
   - Edit client and verify scope is selected

3. **Regenerate credentials if needed**:
   - If client secret was lost, create new API client
   - Can't retrieve secret after initial creation

---

## Connection and Network Issues

### On-Prem Adapter: "Connection refused" or "Timeout"

**Symptoms**:
- Error: `dial tcp: connection refused`
- Error: `i/o timeout`
- Adapter can't reach LimaCharlie

**Solutions**:

1. **Check firewall rules**:
   - Adapter needs outbound HTTPS (port 443) to `*.limacharlie.io`
   - Test connectivity:
     ```bash
     curl -v https://api.limacharlie.io
     telnet api.limacharlie.io 443
     ```

2. **Verify proxy settings**:
   - If behind corporate proxy, adapter must support it
   - Standard `HTTP_PROXY`, `HTTPS_PROXY` environment variables:
     ```bash
     export HTTPS_PROXY=http://proxy.company.com:8080
     lc_adapter <config>
     ```

3. **Check SSL certificate pinning**:
   - Default: adapters use pinned certificates
   - If proxy does SSL inspection, create key with `use_public_root_ca: true`

### Syslog: No data from firewall/device

**Symptoms**:
- Adapter listening but no data received
- Firewall logs say syslog delivered but adapter sees nothing

**Solutions**:

1. **Test connectivity from firewall**:
   ```bash
   # From firewall or another device
   echo "test message" | nc -u <adapter_ip> 1514
   ```
   - Should see message in adapter logs

2. **Check port/protocol**:
   - Verify TCP vs UDP matches firewall config
   - Common mistake: firewall sends UDP, adapter listens TCP
   - In config: `is_udp: true` for UDP

3. **Verify firewall allows outbound syslog**:
   - Firewall rules on sending device may block syslog
   - Check firewall admin logs for denied connections

4. **Check adapter is listening**:
   ```bash
   sudo netstat -tulpn | grep 1514
   # Should show lc_adapter listening
   ```

5. **Firewall requires specific source interface**:
   - Some firewalls need syslog configured on specific interface
   - Check firewall syslog configuration

---

## Data Not Appearing

### Adapter Connected but No Events

**Symptoms**:
- Sensor shows "Online"
- No errors in logs
- But timeline is empty

**Common Causes**:

#### 1. Data Source Not Configured

**AWS CloudTrail**:
- CloudTrail is enabled but not logging
- Check AWS Console → CloudTrail → Trails → [Your Trail]
- Verify "Logging" is ON
- Check S3 bucket has recent files (logs have 5-15 min delay)

**Microsoft 365**:
- Audit logging not enabled
- M365 Admin Center → Settings → Org settings → Security & privacy
- Enable "Audit log search"
- Can take 12-24 hours to activate initially
- Subscription can take up to 12 hours to start flowing

**Okta**:
- No user activity = no logs
- Generate test event: log in to Okta admin
- Logs appear within 1-2 minutes

#### 2. Content Types/Filters Too Restrictive

**Microsoft 365**:
- Check `content_types` in config includes desired logs
- Default includes all, but if specified, must include categories you want
- Example: If you only specified `Audit.Exchange`, you won't see SharePoint events

**AWS**:
- CloudTrail must be logging the types of events you expect
- Read-only vs read/write events
- Management events vs data events

#### 3. Polling/Delay Normal

Many sources have expected delays:

| Source | Expected Delay |
|--------|----------------|
| AWS CloudTrail | 5-15 minutes |
| Microsoft 365 | 5-30 minutes (up to 12 hours for initial subscription) |
| Azure Event Hub | 2-5 minutes |
| Okta | 1-2 minutes |
| CrowdStrike | Real-time to 1 minute |
| Syslog | Real-time (seconds) |

**Solution**: Wait appropriate time after configuration, then generate test activity.

#### 4. Time Range in Query

If querying via MCP/API, check time range:

```bash
# Query last 24 hours (default may be shorter)
limacharlie events query \
  --sensor-id <SID> \
  --start "$(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%SZ)"
```

### Sensor Not Showing Up at All

**Symptoms**:
- Adapter deployed but doesn't appear in sensor list
- No sensor ID generated

**Solutions**:

1. **Check adapter is running**:
   ```bash
   # For systemd service
   sudo systemctl status limacharlie-adapter

   # For Docker
   docker ps | grep lc-adapter
   ```

2. **Verify Installation Key is valid**:
   ```bash
   limacharlie installation_key list
   # Confirm your key exists and matches config
   ```

3. **Check OID matches**:
   - Installation Key created in Org A
   - Config specifies OID for Org B
   - **Solution**: OID and Installation Key must be from same org

4. **Review adapter startup logs**:
   - Look for "usp-client connecting", "usp-client connected"
   - If stuck at "connecting", check network/firewall

---

## Parsing and Mapping Errors

### Events Arriving as Raw Text

**Symptoms**:
- Events appear in timeline
- But all data in single "message" field
- Fields not extracted

**Solutions**:

1. **Check platform type**:
   - Platform `text` doesn't parse JSON
   - Change to `json` if data is JSON

2. **Verify parsing_grok or parsing_re**:
   - Get sample log line from source
   - Test grok pattern at https://grokdebugger.com
   - Or test regex at https://regex101.com (use Golang flavor)

**Example grok troubleshooting**:

Sample log:
```
2024-01-15 10:30:45 firewall ACCEPT 192.168.1.100 10.0.0.5
```

Test patterns:
```yaml
# Too specific - will fail if format changes
parsing_grok:
  message: '%{TIMESTAMP_ISO8601:time} %{WORD:device} %{WORD:action} %{IP:src} %{IP:dst}'

# More flexible - handles variations
parsing_grok:
  message: '%{TIMESTAMP_ISO8601:time} %{WORD:device} %{WORD:action} %{DATA:src_ip} %{GREEDYDATA:remaining}'
```

3. **Check grok pattern must start with "message:"**:
   ```yaml
   # WRONG
   parsing_grok: '%{TIMESTAMP:time}...'

   # CORRECT
   parsing_grok:
     message: '%{TIMESTAMP:time}...'
   ```

### Fields Not Extracted Correctly

**Symptoms**:
- Events parse but event_type or timestamp is wrong
- Hostname not set correctly

**Solutions**:

1. **Verify field paths**:
   ```bash
   # Get sample event
   limacharlie events query --sensor-id <SID> --limit 1
   # Examine JSON structure
   ```

2. **Check path syntax**:
   ```yaml
   # If event structure is:
   # {
   #   "event": {
   #     "type": "Login",
   #     "time": "2024-01-15T10:30:00Z"
   #   }
   # }

   # Paths should be:
   mapping:
     event_type_path: "event/type"    # NOT "event.type"
     event_time_path: "event/time"    # Use / separator
   ```

3. **Timestamp format issues**:
   - LimaCharlie expects ISO8601 or Unix timestamp
   - Custom formats may not parse
   - Consider using parsing_re to convert to ISO8601 first

---

## Adapter Not Starting

### "Invalid configuration" or "Missing required field"

**Symptoms**:
- Adapter exits immediately with error
- Error about missing fields

**Solutions**:

1. **Validate YAML syntax**:
   ```bash
   # Check for YAML errors
   python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"
   ```

2. **Check required fields present**:
   Every adapter needs:
   - `client_options.identity.oid`
   - `client_options.identity.installation_key`
   - `client_options.platform`
   - `client_options.sensor_seed_key`
   - Adapter-specific fields (e.g., `bucket_name` for S3)

3. **Check indentation**:
   ```yaml
   # WRONG - mapping not indented under client_options
   client_options:
     identity:
       oid: "..."
   mapping:
     event_type_path: "type"

   # CORRECT
   client_options:
     identity:
       oid: "..."
     mapping:
       event_type_path: "type"
   ```

### "Permission denied" on Port

**Symptoms**:
- Error: `bind: permission denied`
- Syslog adapter can't listen on port

**Solutions**:

1. **Ports < 1024 require root**:
   ```bash
   # Option 1: Run as root
   sudo lc_adapter syslog config.yaml

   # Option 2: Use port >= 1024
   # Change config to port: 1514 instead of port: 514
   ```

2. **Port already in use**:
   ```bash
   sudo netstat -tulpn | grep <PORT>
   # If another process is using it, choose different port
   ```

---

## Platform-Specific Issues

### AWS: SQS Messages Not Deleting

**Symptoms**:
- Same CloudTrail events appearing repeatedly
- SQS queue depth growing

**Cause**: Adapter may not have `sqs:DeleteMessage` permission

**Solution**:
```json
{
  "Effect": "Allow",
  "Action": [
    "sqs:ReceiveMessage",
    "sqs:DeleteMessage",
    "sqs:GetQueueAttributes"
  ],
  "Resource": "arn:aws:sqs:REGION:ACCOUNT:QUEUE_NAME"
}
```

### Microsoft 365: Only Seeing Old Events

**Symptoms**:
- Events from weeks/months ago appearing
- No recent events

**Cause**: Adapter starting from beginning of available history

**Solution**: Specify `start_time` in config:
```yaml
office365:
  start_time: "2024-01-01T00:00:00Z"  # Start from this date
  # ... rest of config
```

### Okta: Rate Limiting

**Symptoms**:
- Error: `429 Too Many Requests`
- Events delayed

**Cause**: Okta API rate limits (600 requests/min)

**Solution**:
- Adapter handles this automatically with exponential backoff
- If persistent, contact Okta to increase rate limit
- Or reduce polling frequency (not configurable in adapter currently)

### Azure: Event Hub Consumer Group

**Symptoms**:
- Multiple adapters reading same Event Hub
- Events duplicated or missing

**Cause**: All adapters using same consumer group

**Solution**:
- Create separate consumer group for each adapter
- Azure Portal → Event Hub → Consumer groups → Add
- Update connection string or specify consumer group in config

### CrowdStrike: "Offset" Issues

**Symptoms**:
- Events from far in past appearing
- Or missing recent events

**Solution**: Don't use offset unless you know what you're doing
```yaml
falconcloud:
  is_using_offset: false  # Default, recommended
  # ... rest of config
```

---

## Validation Checklist

Use this checklist to systematically verify your adapter configuration.

### Pre-Deployment Checklist

- [ ] Installation Key created and copied
- [ ] Organization ID verified
- [ ] API credentials tested independently (via curl, aws cli, etc.)
- [ ] Required permissions/scopes granted
- [ ] For cloud sources: Admin consent granted (if required)
- [ ] For on-prem: Network connectivity tested
- [ ] Configuration YAML validated (no syntax errors)
- [ ] All required fields present in config

### Post-Deployment Checklist

- [ ] Adapter process is running (ps, systemctl, docker ps)
- [ ] Adapter logs show "connected" (not stuck at "connecting")
- [ ] Sensor appears in `limacharlie sensor list`
- [ ] Sensor status is "Online" or "Active"
- [ ] No errors in adapter logs
- [ ] Test event generated at source
- [ ] Event appears in timeline within expected delay
- [ ] Event fields parsed correctly (not all in "message")
- [ ] Event type extracted correctly
- [ ] Timestamp parsed correctly

### Ongoing Monitoring

- [ ] Set up alert for sensor offline
- [ ] Monitor adapter error logs
- [ ] Check event volume matches expectations
- [ ] Verify no repeated/duplicate events
- [ ] Ensure latency within acceptable range

---

## Getting Help

If you've gone through this guide and still have issues:

1. **Gather diagnostic information**:
   - Adapter logs (last 100 lines)
   - Configuration file (redact secrets)
   - Error messages (exact text)
   - Sensor ID
   - Steps to reproduce

2. **Check LimaCharlie documentation**:
   - https://docs.limacharlie.io/docs/adapter-usage
   - Adapter-specific docs for your type

3. **Contact support**:
   - LimaCharlie Slack community
   - support@limacharlie.io
   - Include diagnostic info above

4. **Ask me for help**:
   - Describe the issue in detail
   - Share relevant error messages
   - I can help interpret errors and suggest fixes
