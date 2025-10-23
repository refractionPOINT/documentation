# Troubleshooting Guide

Common issues, error messages, and solutions for LimaCharlie API integrations.

## Table of Contents

1. [Authentication Errors](#authentication-errors)
2. [Permission Errors](#permission-errors)
3. [Rate Limiting](#rate-limiting)
4. [Connection Issues](#connection-issues)
5. [Sensor Issues](#sensor-issues)
6. [SDK-Specific Issues](#sdk-specific-issues)
7. [Detection Rule Issues](#detection-rule-issues)
8. [Event Streaming Issues](#event-streaming-issues)

---

## Authentication Errors

### Error: 401 Unauthorized

**Symptoms:**
```
HTTP 401: Unauthorized
Authentication failed
```

**Common Causes:**
1. Invalid API key or Organization ID
2. Expired JWT token
3. Incorrect credentials format

**Solutions:**

**Verify credentials:**
```python
# Python
import limacharlie

try:
    manager = limacharlie.Manager(
        oid='YOUR_ORG_ID',
        secret_api_key='YOUR_API_KEY'
    )
    org_info = manager.getOrgInfo()
    print(f"Successfully authenticated: {org_info['name']}")
except Exception as e:
    print(f"Authentication failed: {e}")
```

```go
// Go
client := limacharlie.NewClientFromLoader(
    limacharlie.ClientOptions{
        OID:    "YOUR_ORG_ID",
        APIKey: "YOUR_API_KEY",
    },
)
org := client.Organization(limacharlie.ClientOptions{})
info, err := org.GetInfo()
if err != nil {
    log.Printf("Authentication failed: %v", err)
} else {
    log.Printf("Successfully authenticated: %s", info.Name)
}
```

**Check API key in web interface:**
1. Log into https://app.limacharlie.io
2. Navigate to: Organization > Access Management > REST API
3. Verify the API key exists and has correct permissions

**Test JWT generation manually:**
```bash
curl -X POST "https://jwt.limacharlie.io" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "oid=YOUR_ORG_ID&secret=YOUR_API_KEY"
```

Expected response:
```json
{
  "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Error: JWT Token Too Large (413)

**Symptoms:**
```
HTTP 413: Request Entity Too Large
JWT token exceeds size limit
```

**Cause:** User API key has access to too many organizations

**Solution:** Scope the JWT to a specific organization:

```bash
curl -X POST "https://jwt.limacharlie.io" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "oid=SPECIFIC_ORG_ID&uid=YOUR_USER_ID&secret=YOUR_USER_API_KEY"
```

**Better solution:** Use organization-scoped API keys instead of user API keys.

---

## Permission Errors

### Error: 403 Forbidden

**Symptoms:**
```
HTTP 403: Forbidden
Insufficient permissions
Permission denied
```

**Common Causes:**
1. API key missing required permissions
2. Trying to access resources in different organization
3. API key has [segment] flair limiting visibility

**Solutions:**

**Check required permissions:**

| Operation | Required Permission |
|-----------|-------------------|
| List sensors | `sensor.get` |
| Task sensors | `sensor.task` |
| Tag sensors | `sensor.tag` |
| List D&R rules | `dr.list` |
| Create D&R rules | `dr.set` |
| Delete D&R rules | `dr.del` |
| Event streaming | `output.*` |
| Manage ingestion | `ingestkey.ctrl` |

**Update API key permissions:**
1. Go to: Organization > Access Management > REST API
2. Click on your API key
3. Add required permissions
4. Save changes

**Python - Handle permission errors:**
```python
from limacharlie.utils import LcApiException

try:
    manager.add_output('output_name', config)
except LcApiException as e:
    if '403' in str(e):
        print("Permission denied. API key needs 'output.*' permission")
        print("Add permission in: Organization > Access Management > REST API")
    else:
        raise
```

**Go - Handle permission errors:**
```go
err := org.DRRuleAdd(rule, false)
if err != nil {
    if strings.Contains(err.Error(), "403") {
        log.Println("Permission denied. API key needs 'dr.set' permission")
    } else {
        log.Fatal(err)
    }
}
```

---

## Rate Limiting

### Error: 429 Too Many Requests

**Symptoms:**
```
HTTP 429: Too Many Requests
Rate limit exceeded
```

**Common Causes:**
1. Too many API requests in short time
2. Not using `[bulk]` flair for high-volume operations
3. Missing retry logic

**Solutions:**

**Use `[bulk]` flair for high-volume:**
When creating API key, name it: `automation-key[bulk]`

**Python - Auto-retry on rate limits:**
```python
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    isRetryQuotaErrors=True  # Automatically retry on 429
)
```

**Python - Manual retry with exponential backoff:**
```python
import time
from limacharlie.utils import LcApiException

def retry_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except LcApiException as e:
            if e.http_code == 429:
                if attempt < max_retries - 1:
                    wait = 2 ** attempt
                    retry_after = e.headers.get('Retry-After', wait)
                    print(f"Rate limited. Waiting {retry_after}s...")
                    time.sleep(int(retry_after))
                else:
                    raise
            else:
                raise
    raise Exception("Max retries exceeded")

# Usage
result = retry_with_backoff(lambda: manager.sensors())
```

**Go - Retry with backoff:**
```go
func taskWithRetry(sensor *limacharlie.Sensor, task []byte, maxRetries int) ([]byte, error) {
    var response []byte
    var err error

    for i := 0; i < maxRetries; i++ {
        response, err = sensor.Task(task, nil)
        if err == nil {
            return response, nil
        }

        if strings.Contains(err.Error(), "429") && i < maxRetries-1 {
            wait := time.Duration(1<<uint(i)) * time.Second
            log.Printf("Rate limited. Waiting %v...", wait)
            time.Sleep(wait)
        } else {
            return nil, err
        }
    }

    return nil, fmt.Errorf("max retries exceeded: %w", err)
}
```

**Add delays between requests:**
```python
for sensor_id in sensor_ids:
    sensor = manager.sensor(sensor_id)
    sensor.task('os_processes')
    time.sleep(0.5)  # 500ms delay
```

---

## Connection Issues

### Error: Connection Timeout

**Symptoms:**
```
Connection timeout
Request timeout
ReadTimeoutError
```

**Common Causes:**
1. Network connectivity issues
2. Firewall blocking connections
3. Sensor offline or unresponsive

**Solutions:**

**Check network connectivity:**
```bash
# Test API endpoint
curl -I https://api.limacharlie.io

# Test JWT endpoint
curl -I https://jwt.limacharlie.io
```

**Increase timeout values:**

**Python:**
```python
# For interactive requests
result = sensor.simpleRequest('os_processes', timeout=60)  # 60 seconds
```

**Go:**
```go
import "context"

ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
defer cancel()

// Use context in operations
```

**Check sensor status before tasking:**
```python
if sensor.isOnline():
    result = sensor.task('os_processes')
else:
    print(f"Sensor {sensor.getHostname()} is offline")
```

### Error: SSL Certificate Verification Failed

**Symptoms:**
```
SSL: CERTIFICATE_VERIFY_FAILED
SSL verification error
```

**Cause:** System missing CA certificates or clock skew

**Solutions:**

**Update CA certificates:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ca-certificates

# CentOS/RHEL
sudo yum update ca-certificates

# macOS
brew install openssl
```

**Check system time:**
```bash
date
# Ensure time is correct and synced
```

**Temporary workaround (NOT recommended for production):**
```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
```

---

## Sensor Issues

### Issue: Sensor Not Found

**Symptoms:**
```
HTTP 404: Not Found
Sensor ID not found
```

**Solutions:**

**Verify sensor ID:**
```python
# List all sensors
sensors = manager.sensors()
for sid, info in sensors.items():
    print(f"SID: {sid} - Hostname: {info['hostname']}")
```

**Search by hostname:**
```python
matches = manager.getHostnames(['web-*'])
for hostname, sensor_info in matches.items():
    print(f"{hostname}: {sensor_info}")
```

### Issue: Sensor Offline

**Symptoms:**
- Sensor not responding to tasks
- Last seen time is old
- Tasks timing out

**Check sensor status:**
```python
sensor = manager.sensor('SENSOR_ID')
is_online = sensor.isOnline()
hostname = sensor.getHostname()

if not is_online:
    info = sensor.getInfo()
    last_seen = info.get('last_seen')
    print(f"{hostname} last seen: {last_seen}")
```

**Common causes:**
1. Agent stopped or crashed
2. Network connectivity issues
3. Host powered off

**Solutions:**
1. Check host is powered on and accessible
2. Verify LimaCharlie agent service is running
3. Check network connectivity from host
4. Review agent logs on the endpoint

### Issue: Task Not Responding

**Symptoms:**
- Task sent but no response
- Timeout errors
- Empty results

**Debug steps:**

1. **Verify sensor is online:**
```python
if not sensor.isOnline():
    print("Sensor is offline")
```

2. **Use interactive mode:**
```python
manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    is_interactive=True
)

sensor = manager.sensor('SENSOR_ID')
result = sensor.simpleRequest('os_info', timeout=60)
print(result)
```

3. **Check task syntax:**
```python
# Correct
sensor.task('os_processes')

# Incorrect
sensor.task('os_processes()')  # No parentheses needed
```

---

## SDK-Specific Issues

### Python SDK Issues

#### ImportError: No module named 'limacharlie'

**Solution:**
```bash
pip install limacharlie
# Or for specific version
pip install limacharlie==3.0.0
```

#### AttributeError: 'Manager' object has no attribute 'X'

**Cause:** Outdated SDK version

**Solution:**
```bash
pip install --upgrade limacharlie
```

#### Environment variables not loading

**Check environment variables:**
```python
import os
print(f"LC_OID: {os.environ.get('LC_OID')}")
print(f"LC_API_KEY: {os.environ.get('LC_API_KEY')}")
```

**Set environment variables:**
```bash
export LC_OID="your-org-id"
export LC_API_KEY="your-api-key"
```

### Go SDK Issues

#### Package import error

**Solution:**
```bash
go get github.com/refractionPOINT/go-limacharlie/limacharlie
go mod tidy
```

#### Environment variables not loading

**Check in code:**
```go
import "os"

oid := os.Getenv("LC_OID")
apiKey := os.Getenv("LC_API_KEY")
fmt.Printf("OID: %s\n", oid)
fmt.Printf("API Key: %s\n", apiKey)
```

---

## Detection Rule Issues

### Issue: Rule Not Triggering

**Common causes:**
1. Rule is disabled
2. Incorrect event type
3. Logic error in detection conditions
4. Rule namespace issue

**Debug steps:**

**1. Verify rule is enabled:**
```python
from limacharlie import Hive

hive = Hive(manager)
rule = hive.get('dr-general', manager.oid, 'rule-name')
print(f"Enabled: {rule.get('enabled', False)}")
```

**2. Test with simple rule:**
```python
rule_data = {
    'detect': {
        'event': 'NEW_PROCESS',
        'op': 'is',
        'path': 'event/FILE_PATH',
        'value': 'C:\\Windows\\System32\\notepad.exe'
    },
    'respond': [
        {
            'action': 'report',
            'name': 'test-detection'
        }
    ]
}
```

**3. Check event type:**
Common event types:
- `NEW_PROCESS`
- `NETWORK_CONNECT`
- `FILE_CREATE`
- `DNS_REQUEST`
- `REG_KEY_CREATE`

**4. Verify path syntax:**
```python
# Correct
'path': 'event/FILE_PATH'

# Incorrect
'path': 'FILE_PATH'  # Missing 'event/' prefix
```

### Issue: Too Many False Positives

**Solutions:**

**Add more conditions:**
```python
rule_data = {
    'detect': {
        'event': 'NEW_PROCESS',
        'op': 'and',  # Require all conditions
        'rules': [
            {
                'op': 'contains',
                'path': 'event/FILE_PATH',
                'value': 'powershell.exe'
            },
            {
                'op': 'contains',
                'path': 'event/COMMAND_LINE',
                'value': '-encodedcommand'
            },
            {
                'op': 'is',
                'path': 'event/USER',
                'not': True,
                'value': 'SYSTEM'
            }
        ]
    }
}
```

**Use regex for precision:**
```python
{
    'op': 'matches',
    'path': 'event/FILE_PATH',
    're': '^C:\\\\Users\\\\.*\\\\AppData\\\\Local\\\\Temp\\\\.*\\.exe$'
}
```

**Add tag filters:**
```python
{
    'detect': {
        'target': 'tag',
        'tags': ['production', 'critical'],  # Only these tags
        # ... rest of detection logic
    }
}
```

---

## Event Streaming Issues

### Spout Not Receiving Events

**Common causes:**
1. No events matching filter
2. API key missing `output.*` permission
3. Network connectivity issues

**Debug steps:**

**1. Remove filters:**
```python
# Start with no filters
spout = limacharlie.Spout(
    manager,
    data_type='event',
    is_parse=True
)

# Add filters gradually
spout = limacharlie.Spout(
    manager,
    data_type='event',
    is_parse=True,
    tag='production'  # Add tag filter
)
```

**2. Check permissions:**
API key needs `output.*` permission for streaming.

**3. Test with tailored events:**
```python
# Specific event types
spout = limacharlie.Spout(
    manager,
    data_type='tailored',
    event_type=['NEW_PROCESS'],  # Most common
    is_parse=True
)

for event in spout:
    print(f"Received: {event['event_type']}")
    break  # Test that events are flowing
```

### Firehose Connection Issues

**Common causes:**
1. Port not accessible from internet
2. Firewall blocking incoming connections
3. Incorrect public IP/port

**Debug steps:**

**1. Verify port is open:**
```bash
# On your server
netstat -ln | grep 4443

# Test from external
nc -zv YOUR_PUBLIC_IP 4443
```

**2. Check firewall:**
```bash
# Allow port through firewall
sudo ufw allow 4443/tcp

# Or on cloud provider (AWS example)
# Add security group rule: TCP 4443 from LimaCharlie IPs
```

**3. Verify public IP:**
```bash
curl ifconfig.me
```

**4. Test Firehose creation:**
```python
try:
    firehose = limacharlie.Firehose(
        manager,
        listen_on='0.0.0.0:4443',
        data_type='event',
        name='test_firehose',
        public_dest='YOUR_PUBLIC_IP:4443',
        is_parse=True
    )
    firehose.start()
    print("Firehose started successfully")
except Exception as e:
    print(f"Firehose failed: {e}")
```

**Alternative:** Use Spout if Firehose is problematic:
```python
# Spout works through NAT/firewalls
spout = limacharlie.Spout(manager, data_type='event', is_parse=True)
```

---

## Common Error Messages and Solutions

### "Invalid API key format"

**Solution:** API keys should be UUID format:
```
12345678-1234-1234-1234-123456789012
```

### "Organization not found"

**Solution:** Verify organization ID (OID) is correct UUID format.

### "Sensor is busy"

**Cause:** Sensor already processing a task

**Solution:** Wait and retry, or use queue:
```python
import time

for i in range(3):
    try:
        sensor.task('os_processes')
        break
    except Exception as e:
        if 'busy' in str(e).lower():
            time.sleep(5)
        else:
            raise
```

### "Maximum task queue size reached"

**Cause:** Too many tasks queued for sensor

**Solution:** Implement rate limiting:
```python
for sensor_id in sensor_ids:
    sensor = manager.sensor(sensor_id)
    sensor.task('os_processes')
    time.sleep(1)  # 1 second between tasks
```

### "Invalid detection rule syntax"

**Solution:** Validate rule structure:
```python
# Minimum required fields
rule_data = {
    'detect': {
        'event': 'NEW_PROCESS',  # Required
        'op': 'contains',         # Required
        'path': 'event/FILE_PATH', # Required
        'value': 'malware.exe'    # Required
    },
    'respond': [                  # Required
        {
            'action': 'report',
            'name': 'detection-name'
        }
    ]
}
```

---

## Getting Help

### Check SDK Documentation

- **Python SDK**: https://github.com/refractionPOINT/python-limacharlie
- **Go SDK**: https://github.com/refractionPOINT/go-limacharlie
- **REST API**: https://api.limacharlie.io/openapi

### Enable Debug Logging

**Python:**
```python
import logging

logging.basicConfig(level=logging.DEBUG)

manager = limacharlie.Manager(
    oid='ORG_ID',
    secret_api_key='API_KEY',
    print_debug_fn=lambda msg: print(f"DEBUG: {msg}")
)
```

**Go:**
```go
import "log"

log.SetFlags(log.LstdFlags | log.Lshortfile)
log.SetOutput(os.Stdout)
```

### Contact Support

- **Email**: support@limacharlie.io
- **Community Slack**: https://slack.limacharlie.io
- **GitHub Issues**: Report SDK bugs on GitHub repositories

### Report Issues

When reporting issues, include:
1. SDK version
2. Error message (full stack trace)
3. Minimal code to reproduce
4. Expected vs actual behavior
5. Environment (OS, Python/Go version)

**Get SDK version:**
```python
# Python
import limacharlie
print(limacharlie.__version__)
```

```bash
# Go
go list -m github.com/refractionPOINT/go-limacharlie
```

---

## Additional Resources

- [SKILL.md](SKILL.md) - Main skill documentation
- [PYTHON.md](PYTHON.md) - Python SDK reference
- [GO.md](GO.md) - Go SDK reference
- [EXAMPLES.md](EXAMPLES.md) - Complete code examples
