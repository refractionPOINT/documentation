# D&R Rule Troubleshooting

Comprehensive guide for testing, debugging, validating, and optimizing Detection & Response rules.

## Table of Contents

- [Testing Rules](#testing-rules)
- [Using the Replay Service](#using-the-replay-service)
- [Unit Testing](#unit-testing)
- [Debugging Rules](#debugging-rules)
- [Common Issues](#common-issues)
- [Performance Tuning](#performance-tuning)
- [False Positive Management](#false-positive-management)
- [Validation Best Practices](#validation-best-practices)

## Testing Rules

### Rule Development Lifecycle

1. **Draft**: Write rule in YAML format
2. **Validate**: Check syntax with replay service
3. **Unit Test**: Create test cases for expected matches
4. **Replay**: Test against historical data
5. **Deploy**: Add to test environment first
6. **Monitor**: Watch for false positives/negatives
7. **Iterate**: Refine based on results

### Quick Validation

Before deploying any rule, always validate syntax:

```bash
limacharlie replay --validate --rule-content my-rule.yaml
```

**Success output:**
```
Rule validation successful
```

**Failure output:**
```
Error: line 5: invalid operator 'containz'
```

### Testing Against Sample Events

Create a test event file (`test-event.json`):

```json
{
  "routing": {
    "sid": "test-sensor-id",
    "hostname": "test-host",
    "event_type": "NEW_PROCESS",
    "event_time": 1234567890
  },
  "event": {
    "FILE_PATH": "C:\\Windows\\System32\\calc.exe",
    "COMMAND_LINE": "calc.exe",
    "PROCESS_ID": 1234
  }
}
```

Test the rule:

```bash
limacharlie replay --rule-content my-rule.yaml --events test-event.json
```

**Expected output if match:**
```
Detection: calculator-launched
Event matched rule at line 1
```

**Expected output if no match:**
```
No detections
```

## Using the Replay Service

The replay service allows you to test rules against real historical data without deploying them to production.

### Validate Rule Syntax

```bash
limacharlie replay --validate --rule-content my-rule.yaml
```

This checks:
- YAML syntax
- Operator validity
- Required parameters
- Path formatting

### Test Against Single Sensor

```bash
# Using Unix timestamps
limacharlie replay \
  --sid SENSOR_ID \
  --start 1556568500 \
  --end 1556568600 \
  --rule-content my-rule.yaml
```

```bash
# Using relative time (last N seconds)
limacharlie replay \
  --sid SENSOR_ID \
  --last-seconds 3600 \
  --rule-content my-rule.yaml
```

**Output:**
```
Replaying 1000 events...
Matches: 3
- Detection at 2025-10-23 14:23:45: suspicious-process
- Detection at 2025-10-23 14:24:12: suspicious-process
- Detection at 2025-10-23 14:25:33: suspicious-process
```

### Test Against Entire Organization

```bash
# Last 7 days across all sensors
limacharlie replay \
  --entire-org \
  --last-seconds 604800 \
  --rule-content my-rule.yaml
```

**Warning:** This can be resource-intensive. Start with shorter time periods.

### Test Against Specific Event Type

```bash
limacharlie replay \
  --sid SENSOR_ID \
  --last-seconds 3600 \
  --event-type NEW_PROCESS \
  --rule-content my-rule.yaml
```

This filters events before testing, making replay faster.

### Using Event Files

Create a file with multiple events:

```json
[
  {
    "routing": {"event_type": "NEW_PROCESS", "hostname": "host1"},
    "event": {"FILE_PATH": "C:\\Windows\\calc.exe"}
  },
  {
    "routing": {"event_type": "NEW_PROCESS", "hostname": "host2"},
    "event": {"FILE_PATH": "C:\\Temp\\evil.exe"}
  }
]
```

Test:

```bash
limacharlie replay --rule-content my-rule.yaml --events test-events.json
```

### Trace Mode

Enable detailed trace output to see exactly where rules succeed or fail:

```bash
limacharlie replay \
  --rule-content my-rule.yaml \
  --events test-event.json \
  --trace
```

**Trace output:**
```
Event 1:
  op: and [PASS]
    op: is platform [PASS]
      name: windows
      actual: windows
    op: ends with [FAIL]
      path: event/FILE_PATH
      value: evil.exe
      actual: calc.exe
  Result: NO MATCH
```

This shows:
- Each operator evaluated
- Pass/fail status
- Expected vs actual values
- Final result

## Unit Testing

Add unit tests directly in your rule to catch regressions.

### Basic Unit Test Structure

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: calc.exe
  case sensitive: false
respond:
  - action: report
    name: calculator-launched
tests:
  match:
    # Tests that should trigger detection
    - - event:
          FILE_PATH: C:\Windows\System32\calc.exe
          PROCESS_ID: 1234
        routing:
          event_type: NEW_PROCESS
          hostname: testhost
    - - event:
          FILE_PATH: C:\temp\CALC.EXE
          PROCESS_ID: 5678
        routing:
          event_type: NEW_PROCESS
          hostname: testhost
  non_match:
    # Tests that should NOT trigger detection
    - - event:
          FILE_PATH: C:\Windows\System32\notepad.exe
          PROCESS_ID: 9999
        routing:
          event_type: NEW_PROCESS
          hostname: testhost
    - - event:
          FILE_PATH: C:\Windows\System32\calc.exe
        routing:
          event_type: CODE_IDENTITY
          hostname: testhost
```

### Unit Test Components

**tests.match**: Array of test cases that should trigger the detection
**tests.non_match**: Array of test cases that should NOT trigger

Each test case is an array of events (to support stateful rules).

### Testing Stateful Rules

For stateful rules, provide multiple events in sequence:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: cmd.exe
  with child:
    op: ends with
    event: NEW_PROCESS
    path: event/FILE_PATH
    value: calc.exe
respond:
  - action: report
    name: cmd-spawning-calc
tests:
  match:
    # Parent and child events
    - - event:
          FILE_PATH: C:\Windows\System32\cmd.exe
          PROCESS_ID: 1000
        routing:
          event_type: NEW_PROCESS
          this: atom-1000
      - event:
          FILE_PATH: C:\Windows\System32\calc.exe
          PROCESS_ID: 1001
          PARENT:
            PROCESS_ID: 1000
        routing:
          event_type: NEW_PROCESS
          parent: atom-1000
  non_match:
    # Only parent, no child
    - - event:
          FILE_PATH: C:\Windows\System32\cmd.exe
          PROCESS_ID: 1000
        routing:
          event_type: NEW_PROCESS
```

### Running Unit Tests

Unit tests run automatically when you:
- Create a rule via CLI: `limacharlie dr add`
- Update a rule via CLI: `limacharlie dr update`
- Use the web UI to create/update rules

**Success:**
```
Rule validation successful
Unit tests passed: 4/4
```

**Failure:**
```
Rule validation successful
Unit tests failed: 2/4
  match test 2 failed: expected detection but got none
  non_match test 1 failed: expected no detection but got: my-detection
```

### Unit Test Best Practices

1. **Cover Edge Cases**: Test boundary conditions
2. **Test Case Sensitivity**: Include mixed-case variations
3. **Test Path Variations**: Different file locations
4. **Test Negatives**: Ensure similar but different events don't match
5. **Test Stateful Sequences**: For stateful rules, test various event orders

## Debugging Rules

### Rule Not Matching

**Symptom:** Rule doesn't trigger when you expect it to.

**Debugging steps:**

1. **Verify event structure** - Use Historic View to examine actual events:
   - Go to Timeline in LimaCharlie web UI
   - Find relevant event
   - Examine exact structure and field names

2. **Check path syntax** - Common mistakes:
   ```yaml
   # Wrong
   path: event.FILE_PATH
   path: event\FILE_PATH

   # Correct
   path: event/FILE_PATH
   ```

3. **Verify case sensitivity**:
   ```yaml
   # Add this to operators comparing strings
   case sensitive: false
   ```

4. **Check event type**:
   ```yaml
   # Make sure event type matches
   event: NEW_PROCESS  # Must match routing/event_type
   ```

5. **Use trace mode** to see where rule fails:
   ```bash
   limacharlie replay --rule-content rule.yaml --events event.json --trace
   ```

6. **Simplify the rule** - Remove conditions one by one to find the failing operator:
   ```yaml
   # Start simple
   detect:
     event: NEW_PROCESS
     op: exists
     path: event/FILE_PATH

   # Then add conditions incrementally
   ```

### Rule Matching Too Much

**Symptom:** Rule triggers on events it shouldn't.

**Debugging steps:**

1. **Review matched events** - Check what's actually triggering:
   - Look at recent detections
   - Examine the event data in each detection

2. **Add exclusions**:
   ```yaml
   op: and
   rules:
     - op: contains
       path: event/FILE_PATH
       value: suspicious
     - op: matches
       path: event/FILE_PATH
       re: ^C:\\Windows\\System32\\
       not: true  # exclude System32
   ```

3. **Increase specificity**:
   ```yaml
   # Too broad
   op: contains
   path: event/COMMAND_LINE
   value: cmd

   # More specific
   op: and
   rules:
     - op: contains
       path: event/COMMAND_LINE
       value: cmd.exe
     - op: contains
       path: event/COMMAND_LINE
       value: /c
   ```

4. **Use suppression** to reduce noise:
   ```yaml
   - action: report
     name: my-detection
     suppression:
       max_count: 1
       period: 1h
       is_global: false
   ```

### Stateful Rule Not Working

**Common issues:**

1. **Event correlation not set up** - Ensure events have proper atom IDs:
   - Check `routing/this` and `routing/parent` in events
   - These are auto-populated by LimaCharlie sensors

2. **Time window too short**:
   ```yaml
   with child:
     op: ...
     count: 5
     within: 30  # Increase if needed
   ```

3. **Wrong stateful operator** - Choose correct type:
   - `with child` - Direct children only
   - `with descendant` - Any descendant
   - `with events` - Event repetition

4. **Need stateless mode** - Use when conditions must match same event:
   ```yaml
   with child:
     op: and
     is stateless: true  # All conditions on same child
     rules:
       - op: ...
       - op: ...
   ```

## Common Issues

### Issue: "Path not found in event"

**Cause:** Path doesn't exist in the event structure.

**Solution:**
1. Examine actual event in Historic View
2. Verify path uses correct separator (`/`)
3. Use `exists` operator to check:
   ```yaml
   op: and
   rules:
     - op: exists
       path: event/FILE_PATH
     - op: contains
       path: event/FILE_PATH
       value: suspicious
   ```

### Issue: "Invalid operator"

**Cause:** Typo in operator name or unsupported operator.

**Solution:**
1. Check operator spelling
2. Verify operator exists in [REFERENCE.md](REFERENCE.md)
3. Common typos:
   - `containz` → `contains`
   - `equal` → `is`
   - `greater_than` → `is greater than`

### Issue: "Template rendering failed"

**Cause:** Invalid Go template syntax in action fields.

**Solution:**
1. Check template syntax:
   ```yaml
   # Wrong
   "{{ .event.FILE_PATH }"  # Missing closing }}
   "{{ event.FILE_PATH }}"  # Missing dot prefix

   # Correct
   "{{ .event.FILE_PATH }}"
   ```

2. Access nested fields correctly:
   ```yaml
   # Wrong
   "{{ .event.NETWORK_ACTIVITY.0.IP_ADDRESS }}"

   # Correct
   "{{ index (index .event.NETWORK_ACTIVITY 0) \"IP_ADDRESS\" }}"
   ```

3. Test templates with replay:
   ```bash
   limacharlie replay --rule-content rule.yaml --events event.json
   ```

### Issue: "Suppression not working"

**Cause:** Suppression keys not set correctly.

**Solution:**
1. Verify keys are specified:
   ```yaml
   suppression:
     max_count: 1
     period: 1h
     is_global: false
     keys:  # Must specify keys!
       - '{{ .event.FILE_PATH }}'
   ```

2. Check key rendering with trace mode

3. Understand scope:
   - `is_global: true` - Across entire org
   - `is_global: false` - Per sensor

### Issue: "Rule syntax valid but doesn't execute"

**Cause:** Rule might be disabled or has conditions that never match.

**Solution:**
1. Check rule is enabled in web UI
2. Verify event type exists in your org
3. Test with known good event:
   ```bash
   limacharlie replay --rule-content rule.yaml --events known-good-event.json
   ```

## Performance Tuning

### Optimize Detection Logic

**1. Filter by event type immediately**

```yaml
# Good - filters events early
event: NEW_PROCESS
op: and
rules:
  - op: contains
    path: event/COMMAND_LINE
    value: suspicious

# Bad - processes all events
op: and
rules:
  - op: is
    path: routing/event_type
    value: NEW_PROCESS
  - op: contains
    path: event/COMMAND_LINE
    value: suspicious
```

**2. Put most restrictive conditions first**

```yaml
# Good - most events fail fast
op: and
rules:
  - op: is platform
    name: windows  # Quick check
  - op: ends with
    path: event/FILE_PATH
    value: .exe  # Quick check
  - op: matches
    path: event/COMMAND_LINE
    re: complex.*regex.*here  # Expensive, last

# Bad - expensive check first
op: and
rules:
  - op: matches
    path: event/COMMAND_LINE
    re: complex.*regex.*here  # Runs on every event!
  - op: is platform
    name: windows
```

**3. Use simple operators over complex ones**

```yaml
# Better - simple string comparison
op: ends with
path: event/FILE_PATH
value: .exe

# Worse - regex overhead
op: matches
path: event/FILE_PATH
re: .*\.exe$
```

**4. Minimize regex complexity**

```yaml
# Good - specific pattern
re: ^C:\\Windows\\System32\\[a-z]+\.exe$

# Bad - catastrophic backtracking risk
re: (a+)+b
```

**5. Use scope for arrays**

```yaml
# Good - scope ensures efficient matching
op: scope
path: event/NETWORK_ACTIVITY/
rule:
  op: and
  rules:
    - op: is
      path: event/DESTINATION/PORT
      value: 443

# Bad - might check across different array elements
op: and
rules:
  - op: is
    path: event/NETWORK_ACTIVITY/?/DESTINATION/PORT
    value: 443
```

### Monitor Rule Performance

1. **Use replay metrics** to measure execution time:
   ```bash
   limacharlie replay --entire-org --last-seconds 3600 --rule-content rule.yaml
   ```

   Note processing time in output.

2. **Start with limited scope**:
   - Test on single sensor first
   - Expand to sensor group
   - Finally deploy org-wide

3. **Watch for slow rules** in web UI:
   - Check D&R rule statistics
   - Look for rules with high execution time

### Suppression for Performance

**Always suppress sensor commands:**

```yaml
- action: task
  command: yara_scan hive://yara/rule --pid "{{ .event.PROCESS_ID }}"
  suppression:
    is_global: false
    keys:
      - '{{ .event.PROCESS_ID }}'
    max_count: 1
    period: 1m
```

**Prevent alert storms:**

```yaml
- action: report
  name: high-volume-detection
  suppression:
    max_count: 10  # Limit to 10 alerts
    period: 1h  # Per hour
    is_global: true
```

## False Positive Management

### Identify False Positives

1. **Review detections regularly** - Check detection page daily
2. **Analyze patterns** - Are certain hosts/processes always triggering?
3. **Gather feedback** - Ask analysts which alerts are noise

### Create False Positive Rules

False Positive rules filter detections before they create alerts:

```yaml
# In False Positive Rules section (separate from D&R rules)
op: and
rules:
  - op: is
    path: detect/name
    value: my-detection-name
  - op: is
    path: detect/routing/hostname
    value: dev-server-1
```

This suppresses "my-detection-name" alerts from "dev-server-1".

### Exclude Known Good Paths

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: suspicious-string
    - op: matches
      path: event/FILE_PATH
      re: ^C:\\Program Files\\TrustedApp\\
      not: true  # Exclude trusted application
```

### Tag-Based Exclusions

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: admin-tool
    - op: is tagged
      tag: admin-workstation
      not: true  # Don't alert on admin workstations
```

### Threshold-Based Filtering

```yaml
respond:
  - action: report
    name: potential-threat
    suppression:
      min_count: 3  # Only alert after 3 occurrences
      max_count: 3
      period: 1h
```

### Case-by-Case Tuning

```yaml
# Too sensitive - single occurrence
op: contains
path: event/COMMAND_LINE
value: admin

# Better - multiple indicators
op: and
rules:
  - op: contains
    path: event/COMMAND_LINE
    value: admin
  - op: is public address
    path: event/NETWORK_ACTIVITY/SOURCE/IP_ADDRESS
  - op: matches
    path: event/FILE_PATH
    re: ^C:\\Users\\.*\\Downloads\\
```

## Validation Best Practices

### Pre-Deployment Checklist

- [ ] Syntax validation passes
- [ ] Unit tests pass (if applicable)
- [ ] Tested against historical data
- [ ] Reviewed for false positive potential
- [ ] Suppression configured appropriately
- [ ] Metadata includes MITRE ATT&CK, description
- [ ] Response actions won't cause disruption
- [ ] Tested in dev/test environment first

### Rule Review Questions

1. **Is the event type correct?**
   - Does this event type exist in my environment?
   - Is it the most specific event type available?

2. **Are paths correct?**
   - Verified against actual event structure?
   - Using `/` separators?
   - Array indices handled with `scope`?

3. **Is case sensitivity handled?**
   - File paths: `case sensitive: false`
   - Domain names: `case sensitive: false`
   - Hashes: `case sensitive: true`

4. **Are operators optimized?**
   - Most restrictive first?
   - Simple operators preferred?
   - Event type filtered at top level?

5. **Is suppression appropriate?**
   - Sensor commands suppressed?
   - Alert volume acceptable?
   - Keys specific enough?

6. **Are response actions safe?**
   - Won't cause false positive impact?
   - Tested in controlled environment?
   - Can be rolled back?

7. **Is documentation complete?**
   - Clear detection name?
   - Metadata with context?
   - MITRE ATT&CK mapping?

### Testing Strategy

**1. Unit Testing Phase**
- Create positive test cases (should match)
- Create negative test cases (should not match)
- Test edge cases (boundary conditions)

**2. Replay Testing Phase**
- Test against 1 hour of single sensor data
- Expand to 24 hours
- Test against multiple sensors
- Finally test against org (limited time)

**3. Deployment Phase**
- Deploy to test/dev sensors first
- Monitor for 24-48 hours
- Review all detections
- Adjust based on results
- Deploy to production sensors
- Continue monitoring

**4. Maintenance Phase**
- Review detection volume weekly
- Tune based on false positive rate
- Update for new attack techniques
- Retire obsolete rules

### Common Validation Mistakes

**Mistake 1: Not testing with real data**
```yaml
# Rule looks good but...
detect:
  event: DNS_REQUEST
  op: contains
  path: event/DOMAIN_NAME
  value: evil
```
...when tested with real data, matches "medieval.com", "bedevil.com", etc.

**Solution:** Always test with real historical data.

**Mistake 2: Forgetting case sensitivity**
```yaml
# Won't match "CALC.EXE" or "Calc.exe"
op: ends with
path: event/FILE_PATH
value: calc.exe
```

**Solution:** Add `case sensitive: false` for paths and domains.

**Mistake 3: Not using scope for arrays**
```yaml
# Might match across different array elements
op: and
rules:
  - op: is
    path: event/NETWORK_ACTIVITY/?/PORT
    value: 443
  - op: is public address
    path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
```

**Solution:** Use `scope` to ensure conditions match same element.

**Mistake 4: Over-broad detection**
```yaml
# Matches too much
op: contains
path: event/FILE_PATH
value: temp
```

**Solution:** Add more specificity or exclusions.

**Mistake 5: No suppression on sensor commands**
```yaml
# Could run same command hundreds of times
- action: task
  command: yara_scan ...
```

**Solution:** Always add suppression to task actions.

### Tools and Commands Summary

```bash
# Validate syntax
limacharlie replay --validate --rule-content rule.yaml

# Test with sample events
limacharlie replay --rule-content rule.yaml --events events.json

# Test with trace (debugging)
limacharlie replay --rule-content rule.yaml --events events.json --trace

# Test against single sensor (1 hour)
limacharlie replay --sid SENSOR_ID --last-seconds 3600 --rule-content rule.yaml

# Test against entire org (1 day)
limacharlie replay --entire-org --last-seconds 86400 --rule-content rule.yaml

# List current rules
limacharlie dr list

# Add rule
limacharlie dr add --rule-name my-rule --rule-file rule.yaml

# Delete rule
limacharlie dr delete --rule-name my-rule

# Get rule details
limacharlie dr get --rule-name my-rule
```

---

[Back to SKILL.md](SKILL.md) | [Reference](REFERENCE.md) | [Examples](EXAMPLES.md)
