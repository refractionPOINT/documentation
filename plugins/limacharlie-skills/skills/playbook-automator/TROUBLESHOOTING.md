# Playbook Troubleshooting Guide

Comprehensive guide for testing, debugging, and troubleshooting LimaCharlie playbooks.

## Table of Contents

- [Testing Playbooks](#testing-playbooks)
- [Debugging Techniques](#debugging-techniques)
- [Common Errors](#common-errors)
- [Development Workflow](#development-workflow)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)

## Testing Playbooks

### Local Development

Develop and test playbooks locally before deploying:

```python
# playbook_local_test.py
import limacharlie
import json

def playbook(sdk, data):
    """Your playbook code here."""
    # ... playbook logic ...
    return {"data": {"result": "success"}}

# Test locally
if __name__ == "__main__":
    # Initialize SDK with your credentials
    sdk = limacharlie.Manager()

    # Test data
    test_cases = [
        # Test case 1: Valid input
        {
            "sid": "test-sensor-id",
            "process_id": 1234,
            "hostname": "test-host"
        },
        # Test case 2: Missing required field
        {
            "sid": "test-sensor-id"
            # Missing process_id
        },
        # Test case 3: Offline sensor
        {
            "sid": "offline-sensor-id",
            "process_id": 5678
        }
    ]

    for i, test_data in enumerate(test_cases):
        print(f"\n=== Test Case {i+1} ===")
        print(f"Input: {json.dumps(test_data, indent=2)}")

        result = playbook(sdk, test_data)

        print(f"Output: {json.dumps(result, indent=2)}")

        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✓ Success")
```

### Unit Testing

Create unit tests for your playbooks:

```python
# test_playbook.py
import unittest
from unittest.mock import Mock, MagicMock
import sys

# Import your playbook
from playbook import playbook

class TestPlaybook(unittest.TestCase):

    def setUp(self):
        """Set up mock SDK for testing."""
        self.mock_sdk = Mock()

    def test_valid_input(self):
        """Test playbook with valid input."""
        data = {
            "sid": "test-sensor",
            "process_id": 1234
        }

        # Mock sensor
        mock_sensor = Mock()
        mock_sensor.getInfo.return_value = {
            "sid": "test-sensor",
            "hostname": "test-host",
            "is_online": True,
            "tags": []
        }
        self.mock_sdk.sensor.return_value = mock_sensor

        result = playbook(self.mock_sdk, data)

        # Assertions
        self.assertIn("data", result)
        self.assertNotIn("error", result)
        self.mock_sdk.sensor.assert_called_with("test-sensor")

    def test_missing_sid(self):
        """Test playbook with missing sid."""
        data = {
            "process_id": 1234
        }

        result = playbook(self.mock_sdk, data)

        # Should return error
        self.assertIn("error", result)
        self.assertIn("sid", result["error"].lower())

    def test_offline_sensor(self):
        """Test playbook with offline sensor."""
        data = {
            "sid": "offline-sensor",
            "process_id": 1234
        }

        # Mock offline sensor
        mock_sensor = Mock()
        mock_sensor.getInfo.return_value = {
            "sid": "offline-sensor",
            "hostname": "offline-host",
            "is_online": False
        }
        self.mock_sdk.sensor.return_value = mock_sensor

        result = playbook(self.mock_sdk, data)

        # Should handle offline sensor gracefully
        self.assertIn("error", result)
        self.assertIn("offline", result["error"].lower())

    def test_no_sdk(self):
        """Test playbook without SDK (no credentials)."""
        data = {"sid": "test-sensor"}

        result = playbook(None, data)

        # Should return error about credentials
        self.assertIn("error", result)
        self.assertIn("credential", result["error"].lower())

if __name__ == '__main__':
    unittest.main()
```

### Interactive Testing

Test playbooks interactively from the LimaCharlie web interface:

1. **Navigate to Playbook Extension**:
   - Go to **Extensions** > **Playbook**
   - Select your playbook from the list

2. **Provide Test Data**:
   ```json
   {
     "sid": "your-test-sensor-id",
     "process_id": 1234,
     "test_mode": true
   }
   ```

3. **Review Output**:
   - Check return data
   - Verify no errors occurred
   - Confirm expected actions were taken

4. **Iterate**:
   - Modify playbook based on results
   - Re-upload to Hive
   - Test again

### Testing via SDK

Test programmatically using the Python SDK:

```python
import limacharlie
import json

# Initialize
lc = limacharlie.Manager()
ext = limacharlie.Extension(lc)

# Test scenarios
test_scenarios = {
    "success_case": {
        "name": "my-playbook",
        "credentials": "hive://secret/test-api-key",
        "data": {
            "sid": "valid-sensor-id",
            "process_id": 1234
        }
    },
    "error_case": {
        "name": "my-playbook",
        "credentials": "hive://secret/test-api-key",
        "data": {
            # Missing required fields
            "process_id": 1234
        }
    }
}

for scenario_name, scenario in test_scenarios.items():
    print(f"\n=== Testing: {scenario_name} ===")

    try:
        response = ext.request("ext-playbook", "run_playbook", scenario)

        print(f"Response: {json.dumps(response, indent=2)}")

        # Validate response
        if "error" in response:
            print(f"❌ Playbook returned error: {response['error']}")
        else:
            print(f"✓ Playbook succeeded")
            if "data" in response:
                print(f"  Data: {response['data']}")

    except Exception as e:
        print(f"❌ Exception: {str(e)}")
```

## Debugging Techniques

### Debug Logging

Add debug logging to your playbooks:

```python
import limacharlie

def playbook(sdk, data):
    """Playbook with comprehensive debug logging."""

    debug_log = []

    try:
        debug_log.append({
            "stage": "init",
            "timestamp": time.time(),
            "input_data": data
        })

        if not sdk:
            debug_log.append({"stage": "validation", "error": "no_sdk"})
            return {
                "error": "API credentials required",
                "data": {"debug_log": debug_log}
            }

        debug_log.append({"stage": "validation", "status": "sdk_ok"})

        sid = data.get("sid")
        if not sid:
            debug_log.append({"stage": "validation", "error": "missing_sid"})
            return {
                "error": "sid parameter required",
                "data": {"debug_log": debug_log}
            }

        debug_log.append({"stage": "validation", "status": "sid_ok", "sid": sid})

        # Get sensor
        debug_log.append({"stage": "sensor_lookup", "sid": sid})
        sensor = sdk.sensor(sid)

        info = sensor.getInfo()
        debug_log.append({
            "stage": "sensor_info",
            "hostname": info.get("hostname"),
            "online": info.get("is_online"),
            "platform": info.get("plat")
        })

        # Check if online
        if not info.get("is_online"):
            debug_log.append({"stage": "sensor_check", "error": "offline"})
            return {
                "error": "Sensor is offline",
                "data": {"debug_log": debug_log}
            }

        debug_log.append({"stage": "sensor_check", "status": "online"})

        # Perform actions
        debug_log.append({"stage": "action", "type": "task_sensor"})
        sensor.task("history_dump", investigationId="debug-test")

        debug_log.append({"stage": "complete", "status": "success"})

        return {
            "data": {
                "success": True,
                "hostname": info.get("hostname"),
                "debug_log": debug_log
            }
        }

    except Exception as e:
        debug_log.append({
            "stage": "exception",
            "error": str(e),
            "error_type": type(e).__name__
        })

        return {
            "error": str(e),
            "data": {"debug_log": debug_log}
        }
```

### Conditional Debug Mode

Enable verbose logging only in debug mode:

```python
import limacharlie
import time

def playbook(sdk, data):
    """Playbook with conditional debug mode."""

    debug_mode = data.get("debug", False)
    debug_log = [] if debug_mode else None

    def log(message):
        if debug_mode:
            debug_log.append({
                "timestamp": time.time(),
                "message": message
            })

    log("Playbook started")

    if not sdk:
        log("Error: No SDK credentials")
        result = {"error": "API credentials required"}
        if debug_mode:
            result["data"] = {"debug_log": debug_log}
        return result

    log("SDK credentials validated")

    # ... rest of playbook logic with log() calls ...

    result = {"data": {"success": True}}
    if debug_mode:
        result["data"]["debug_log"] = debug_log

    return result
```

### Exception Handling with Context

Capture full exception context:

```python
import limacharlie
import traceback
import sys

def playbook(sdk, data):
    """Playbook with detailed exception handling."""

    try:
        # Playbook logic here
        if not sdk:
            raise ValueError("API credentials required")

        sid = data.get("sid")
        if not sid:
            raise ValueError("sid parameter required")

        sensor = sdk.sensor(sid)
        # ... rest of logic ...

        return {"data": {"success": True}}

    except ValueError as e:
        # Handle validation errors
        return {
            "error": f"Validation error: {str(e)}",
            "data": {
                "error_type": "validation",
                "input_data": data
            }
        }

    except limacharlie.LcApiException as e:
        # Handle LimaCharlie API errors
        return {
            "error": f"LimaCharlie API error: {str(e)}",
            "data": {
                "error_type": "api_error",
                "api_response": getattr(e, 'response', None)
            }
        }

    except Exception as e:
        # Handle unexpected errors with full traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)

        return {
            "error": f"Unexpected error: {str(e)}",
            "data": {
                "error_type": "unexpected",
                "error_class": type(e).__name__,
                "traceback": tb_lines
            }
        }
```

### Testing with Mock Data

Create mock sensors and data for testing:

```python
import limacharlie

def playbook(sdk, data):
    """Playbook that can use mock data for testing."""

    # Check if in test mode
    test_mode = data.get("test_mode", False)

    if test_mode:
        # Use mock data instead of real API calls
        mock_sensor_info = {
            "sid": data.get("sid", "mock-sensor"),
            "hostname": "mock-hostname",
            "is_online": True,
            "plat": "windows",
            "tags": ["test"]
        }

        # Simulate playbook logic
        result = {
            "data": {
                "test_mode": True,
                "mock_sensor": mock_sensor_info,
                "actions": ["would_task_sensor", "would_tag_sensor"]
            }
        }

        return result

    # Real playbook logic
    if not sdk:
        return {"error": "API credentials required"}

    # ... actual implementation ...
```

## Common Errors

### Error: "API credentials required"

**Cause**: Playbook requires SDK but no credentials were provided.

**Solution**:
```yaml
# In D&R rule, provide credentials:
extension request:
  name: '{{ "my-playbook" }}'
  credentials: '{{ "hive://secret/lc-api-key" }}'  # Add this
  data:
    sid: "{{ .routing.sid }}"
```

### Error: "Missing required parameter"

**Cause**: Required input parameter not provided.

**Solution**:
```python
# Validate inputs early
def playbook(sdk, data):
    required_fields = ["sid", "process_id"]
    for field in required_fields:
        if field not in data:
            return {"error": f"Missing required parameter: {field}"}

    # Continue with logic...
```

### Error: "Sensor is offline"

**Cause**: Attempting to task an offline sensor.

**Solution**:
```python
def playbook(sdk, data):
    sensor = sdk.sensor(data["sid"])
    info = sensor.getInfo()

    # Check before tasking
    if not info.get("is_online"):
        return {
            "error": f"Sensor {data['sid']} is offline",
            "data": {
                "sensor_status": "offline",
                "last_seen": info.get("last_seen")
            }
        }

    # Safe to task sensor
    sensor.task("history_dump")
```

### Error: "Hive key not found"

**Cause**: Referenced secret or data doesn't exist in Hive.

**Solution**:
```python
def playbook(sdk, data):
    try:
        secret = limacharlie.Hive(sdk, "secret").get("my-key").data["secret"]
    except Exception as e:
        return {
            "error": f"Failed to retrieve secret 'my-key': {str(e)}",
            "data": {
                "hint": "Create secret with: limacharlie hive set secret --key my-key --data 'value' --data-key secret"
            }
        }
```

### Error: "Execution timeout"

**Cause**: Playbook exceeded 10-minute execution limit.

**Solution**:
```python
def playbook(sdk, data):
    # Break large operations into batches
    sensors = list(sdk.sensors())
    batch_size = 10

    for i in range(0, len(sensors), batch_size):
        batch = sensors[i:i + batch_size]

        for sensor in batch:
            # Process sensor
            pass

        # Brief pause between batches
        time.sleep(0.5)
```

### Error: "Invalid return value"

**Cause**: Playbook returned invalid format.

**Solution**:
```python
def playbook(sdk, data):
    # Must return a dictionary
    return {
        "data": {...},      # Optional
        "error": "...",     # Optional
        "detection": {...}, # Optional
        "cat": "..."        # Optional (required with detection)
    }

    # ❌ Invalid returns:
    # return None
    # return "success"
    # return True
    # return [...]
```

## Development Workflow

### 1. Local Development

```bash
# Create playbook file
cat > playbook.py << 'EOF'
import limacharlie

def playbook(sdk, data):
    if not sdk:
        return {"error": "API credentials required"}

    # Your logic here

    return {"data": {"success": True}}
EOF

# Test locally
python playbook.py
```

### 2. Upload to Hive

```bash
# Upload playbook
limacharlie hive set playbook --key my-playbook --data playbook.py --data-key python

# Verify upload
limacharlie hive get playbook my-playbook
```

### 3. Interactive Testing

Test from web interface with various inputs.

### 4. Integration Testing

Test with D&R rule or SDK invocation.

### 5. Monitor and Iterate

```bash
# Check playbook executions in timeline
# Review any errors or unexpected behavior
# Update playbook
limacharlie hive set playbook --key my-playbook --data playbook.py --data-key python
```

### Version Control

```bash
# .gitignore
secrets.yaml
*.key
.limacharlie

# Store playbooks in git
git add playbooks/
git commit -m "Update incident response playbook"
git push

# Deploy via CI/CD
limacharlie configs push config.yaml
```

## Performance Optimization

### Batch Operations

Process multiple items efficiently:

```python
def playbook(sdk, data):
    """Efficient batch processing."""

    # ❌ Inefficient: Process one at a time
    for sensor in sdk.sensors():
        sensor.task("history_dump")
        time.sleep(5)  # Wait for each

    # ✓ Efficient: Batch and parallel
    sensors = list(sdk.sensors())
    batch_size = 20

    for i in range(0, len(sensors), batch_size):
        batch = sensors[i:i + batch_size]

        # Task all in batch
        for sensor in batch:
            sensor.task("history_dump")

        # Brief pause between batches
        time.sleep(1)
```

### Minimize API Calls

```python
def playbook(sdk, data):
    """Minimize redundant API calls."""

    # ❌ Inefficient: Multiple calls for same data
    for i in range(10):
        sensor = sdk.sensor("same-sensor-id")
        info = sensor.getInfo()  # Called 10 times

    # ✓ Efficient: Cache sensor info
    sensor = sdk.sensor("same-sensor-id")
    info = sensor.getInfo()  # Called once

    for i in range(10):
        # Use cached info
        hostname = info.get("hostname")
```

### Early Exit on Errors

```python
def playbook(sdk, data):
    """Exit early on validation errors."""

    # ✓ Good: Validate first
    if not sdk:
        return {"error": "API credentials required"}

    if not data.get("sid"):
        return {"error": "sid required"}

    # Only proceed if validation passed
    sensor = sdk.sensor(data["sid"])
    # ... rest of logic ...
```

### Limit Data Collection

```python
def playbook(sdk, data):
    """Collect only necessary data."""

    # ❌ Inefficient: Get all detections
    detections = sdk.getDetections(limit=10000)

    # ✓ Efficient: Limit to what you need
    detections = sdk.getDetections(limit=100)

    # ✓ Better: Filter what you need
    critical_detections = [
        d for d in sdk.getDetections(limit=100)
        if "critical" in d.get("detect", {}).get("cat", "")
    ]
```

## Best Practices

### 1. Input Validation

Always validate inputs at the start:

```python
def playbook(sdk, data):
    # Validate SDK
    if not sdk:
        return {"error": "API credentials required"}

    # Validate required fields
    required = ["sid", "process_id"]
    for field in required:
        if field not in data:
            return {"error": f"Missing required parameter: {field}"}

    # Validate field types
    if not isinstance(data["process_id"], int):
        return {"error": "process_id must be an integer"}

    # Validate field values
    if data["process_id"] < 1:
        return {"error": "process_id must be positive"}

    # All validated - proceed
    # ...
```

### 2. Error Handling

Handle all potential errors:

```python
def playbook(sdk, data):
    try:
        sensor = sdk.sensor(data["sid"])
        info = sensor.getInfo()

        # Check sensor state
        if not info.get("is_online"):
            return {"error": "Sensor offline"}

        # Perform action
        sensor.task("history_dump")

        return {"data": {"success": True}}

    except limacharlie.LcApiException as e:
        return {"error": f"API error: {str(e)}"}

    except KeyError as e:
        return {"error": f"Missing data: {str(e)}"}

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
```

### 3. Consistent Return Format

Use consistent return structure:

```python
def playbook(sdk, data):
    # Success
    return {
        "data": {
            "success": True,
            "sensor": "hostname",
            "actions": ["action1", "action2"]
        }
    }

    # Error (with context)
    return {
        "error": "Sensor offline",
        "data": {
            "sensor_id": "sid",
            "last_seen": 1234567890
        }
    }

    # Detection
    return {
        "detection": {
            "title": "Threat detected",
            "details": {...}
        },
        "cat": "threat-category",
        "data": {
            "additional": "info"
        }
    }
```

### 4. Documentation

Document your playbooks:

```python
def playbook(sdk, data):
    """
    Investigate suspicious process and collect evidence.

    Required Parameters:
        sid (str): Sensor ID
        process_id (int): Process ID to investigate

    Optional Parameters:
        full_dump (bool): Collect full memory dump (default: False)
        isolate (bool): Isolate sensor if malicious (default: True)

    Returns:
        On success:
            data: {
                "success": True,
                "evidence_collected": [...],
                "actions_taken": [...]
            }

        On error:
            error: Error message string
            data: {
                "context": "Additional error context"
            }

    Example:
        {
            "sid": "sensor-123",
            "process_id": 1234,
            "full_dump": true
        }
    """

    # Implementation...
```

### 5. Test Before Deploy

Always test thoroughly:

```bash
# 1. Test locally with mock data
python playbook_test.py

# 2. Upload to dev/test organization
limacharlie -o test-org hive set playbook --key my-playbook --data playbook.py --data-key python

# 3. Test interactively
# Use web interface to test with various inputs

# 4. Test with real D&R rule (in test org)
# Monitor results

# 5. Deploy to production
limacharlie -o prod-org hive set playbook --key my-playbook --data playbook.py --data-key python
```

---

For complete examples, see [EXAMPLES.md](./EXAMPLES.md).

For SDK reference, see [REFERENCE.md](./REFERENCE.md).

For getting started, see [SKILL.md](./SKILL.md).
