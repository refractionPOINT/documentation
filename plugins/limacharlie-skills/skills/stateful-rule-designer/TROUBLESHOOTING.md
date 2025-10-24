# Stateful Rule Designer - Troubleshooting & Testing

This document provides comprehensive guidance for testing, debugging, and optimizing stateful detection rules.

## Table of Contents

- [Testing Stateful Rules](#testing-stateful-rules)
- [Common Issues](#common-issues)
- [Performance Problems](#performance-problems)
- [Debugging Techniques](#debugging-techniques)
- [Best Practices Checklist](#best-practices-checklist)

## Testing Stateful Rules

Testing stateful rules requires special consideration because they track state over time.

### Important Testing Caveats

1. **Forward-Looking Only**: Stateful rules only track events that occur **after** the rule is active
2. **State Reset**: Changing a rule resets all state
3. **Parent Must Occur First**: For `cmd.exe -> calc.exe` detection, CMD must launch **after** the rule is active
4. **Process Tree Requirements**: Parent processes must be running when the rule becomes active

### Testing Workflow

#### Step 1: Validate Syntax

Always validate syntax before deploying:

```bash
limacharlie replay --validate --rule-content my-stateful-rule.yaml
```

**Common syntax errors**:
- Missing `event:` field in child rules
- Incorrect indentation in YAML
- Missing required parameters (e.g., `count` without `within`)
- Invalid operator names

#### Step 2: Add Unit Tests to Your Rule

Unit tests are the most reliable way to test stateful rules. Add them directly to your rule file:

```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: cmd.exe
  case sensitive: false
  with child:
    op: ends with
    event: NEW_PROCESS
    path: event/FILE_PATH
    value: calc.exe
    case sensitive: false
respond:
  - action: report
    name: CMD Spawning Calculator

# Unit tests
tests:
  match:
    # Should match: cmd.exe -> calc.exe
    - - event:
          FILE_PATH: C:\Windows\System32\cmd.exe
          PROCESS_ID: 1234
        routing:
          event_type: NEW_PROCESS
          this: parent-1
          hostname: testhost
          sid: test-sensor
      - event:
          FILE_PATH: C:\Windows\System32\calc.exe
          PROCESS_ID: 5678
        routing:
          event_type: NEW_PROCESS
          this: child-1
          parent: parent-1
          hostname: testhost
          sid: test-sensor

  non_match:
    # Should NOT match: notepad.exe -> calc.exe
    - - event:
          FILE_PATH: C:\Windows\System32\notepad.exe
          PROCESS_ID: 1234
        routing:
          event_type: NEW_PROCESS
          this: parent-2
          hostname: testhost
          sid: test-sensor
      - event:
          FILE_PATH: C:\Windows\System32\calc.exe
          PROCESS_ID: 5678
        routing:
          event_type: NEW_PROCESS
          this: child-2
          parent: parent-2
          hostname: testhost
          sid: test-sensor
```

**Run unit tests**:
```bash
limacharlie replay --validate --rule-content my-rule.yaml
```

#### Step 3: Test with Synthetic Events

Create JSON files with test events that simulate the attack chain.

**Example: Testing cmd.exe -> calc.exe**

Create `test-events.json`:
```json
[
  {
    "routing": {
      "event_type": "NEW_PROCESS",
      "this": "parent-atom-id",
      "hostname": "testhost",
      "sid": "test-sid"
    },
    "event": {
      "FILE_PATH": "C:\\Windows\\System32\\cmd.exe",
      "PROCESS_ID": 1234,
      "COMMAND_LINE": "cmd.exe"
    }
  },
  {
    "routing": {
      "event_type": "NEW_PROCESS",
      "this": "child-atom-id",
      "parent": "parent-atom-id",
      "hostname": "testhost",
      "sid": "test-sid"
    },
    "event": {
      "FILE_PATH": "C:\\Windows\\System32\\calc.exe",
      "PROCESS_ID": 5678,
      "COMMAND_LINE": "calc.exe"
    }
  }
]
```

**Test**:
```bash
limacharlie replay --rule-content my-rule.yaml --events test-events.json
```

**Expected output**:
```
Detection: CMD Spawning Calculator
Matched: 1 event
```

#### Step 4: Test with_events Rules

For `with events` rules, create multiple events on the same sensor:

**Example: Testing brute force detection**

Create `brute-force-test.json`:
```json
[
  {
    "routing": {
      "event_type": "WEL",
      "sid": "test-sensor",
      "hostname": "testhost"
    },
    "event": {
      "EVENT": {
        "System": {
          "EventID": "4625",
          "Channel": "Security"
        },
        "EventData": {
          "TargetUserName": "admin"
        }
      }
    }
  },
  {
    "routing": {
      "event_type": "WEL",
      "sid": "test-sensor",
      "hostname": "testhost"
    },
    "event": {
      "EVENT": {
        "System": {
          "EventID": "4625",
          "Channel": "Security"
        },
        "EventData": {
          "TargetUserName": "admin"
        }
      }
    }
  },
  ...  // Repeat 5+ times for count: 5
]
```

#### Step 5: Live Testing on Non-Production Sensors

**Critical**: Always test on non-production systems first.

1. **Create Test Organization**:
   - Use a separate LimaCharlie organization for testing
   - Deploy test sensors to safe systems

2. **Deploy Rule**:
   ```bash
   limacharlie dr add --rule-file my-rule.yaml
   ```

3. **Trigger Behavior Safely**:
   - Manually execute the behavior pattern
   - For `cmd.exe -> calc.exe`: Launch CMD, then launch calc from CMD
   - Monitor detections in real-time

4. **Verify Detection**:
   - Check that detection fired
   - Verify correct event is reported
   - Confirm response actions executed as expected

5. **Refine and Redeploy**:
   - Modify rule based on test results
   - Remember: Modifying rule resets all state
   - Re-trigger behavior to test again

#### Step 6: Replay Against Historical Data

**Warning**: Historical replay has limitations for stateful rules.

```bash
# Replay last 7 days of events
limacharlie replay --entire-org --last-seconds 604800 --rule-content my-rule.yaml
```

**Limitations**:
- Historical data is replayed "as-is" without rebuilding process trees
- Parent-child relationships may not be preserved
- `with events` may work better than `with child`/`with descendant`
- Best used for validating stateless parts of the rule

**Best for**:
- Testing `with events` rules (brute force, scanning)
- Validating parent event matching logic
- Estimating detection volume

**Not reliable for**:
- Testing `with child`/`with descendant` rules
- Verifying complete attack chains
- Final validation before production

## Common Issues

### Issue 1: Rule Not Matching

**Symptoms**: Expected detection doesn't fire when behavior occurs.

**Possible Causes**:

1. **Parent process started before rule was active**
   - **Solution**: Restart parent process after deploying rule
   - **Why**: Stateful rules are forward-looking only

2. **Missing event type in child rule**
   ```yaml
   # Bad: Missing event type
   with child:
     op: ends with
     path: event/FILE_PATH
     value: calc.exe

   # Good: Event type specified
   with child:
     event: NEW_PROCESS
     op: ends with
     path: event/FILE_PATH
     value: calc.exe
   ```

3. **Incorrect path in stateful context**
   ```yaml
   # Bad: Wrong path
   with child:
     op: ends with
     path: routing/FILE_PATH  # Wrong!
     value: calc.exe

   # Good: Correct path
   with child:
     op: ends with
     path: event/FILE_PATH  # Correct
     value: calc.exe
   ```

4. **Case sensitivity issues**
   ```yaml
   # Add case sensitive: false for file paths
   op: ends with
   path: event/FILE_PATH
   value: cmd.exe
   case sensitive: false  # Important on Windows!
   ```

5. **is stateless preventing match**
   ```yaml
   # If is stateless: true, all conditions must match SAME event
   with child:
     op: and
     is stateless: true  # Remove if conditions should match different events
     rules:
       - op: ends with
         path: event/FILE_PATH
         value: evil.exe
       - op: contains
         path: event/COMMAND_LINE
         value: malicious-flag
   ```

### Issue 2: Too Many False Positives

**Symptoms**: Rule triggers on legitimate activity.

**Solutions**:

1. **Add more specific parent filtering**:
   ```yaml
   # Before: Too broad
   detect:
     event: NEW_PROCESS
     op: exists
     path: event/FILE_PATH

   # After: More specific
   detect:
     event: NEW_PROCESS
     op: and
     rules:
       - op: ends with
         path: event/FILE_PATH
         value: outlook.exe
         case sensitive: false
       - op: is platform
         name: windows
   ```

2. **Use is stateless for atomic conditions**:
   ```yaml
   with child:
     op: and
     is stateless: true  # Both must be on same event
     rules:
       - op: ends with
         path: event/FILE_PATH
         value: powershell.exe
       - op: contains
         path: event/COMMAND_LINE
         value: -enc
   ```

3. **Increase count threshold**:
   ```yaml
   # Before: Too sensitive
   count: 3
   within: 60

   # After: Higher threshold
   count: 10
   within: 60
   ```

4. **Add exclusions**:
   ```yaml
   detect:
     event: NEW_PROCESS
     op: and
     rules:
       - op: ends with
         path: event/FILE_PATH
         value: outlook.exe
       - op: contains
         path: event/FILE_PATH
         value: C:\Program Files\Microsoft Office\
         not: true  # Exclude legitimate Office installations
   ```

### Issue 3: Rule Stopped Working After Modification

**Symptoms**: Rule worked, then stopped after changes.

**Cause**: Modifying a rule resets all state.

**Solution**:
1. Restart parent processes after rule modification
2. Wait for new process launches
3. Remember: Existing process trees won't be tracked

**Example**:
```
1. Deploy rule: outlook.exe -> cmd.exe
2. Outlook is already running
3. Modify rule (change count from 1 to 2)
4. ALL STATE RESET - Outlook must restart
5. Restart Outlook
6. Now rule will track new Outlook process
```

### Issue 4: Wrong Event Reported

**Symptoms**: Detection fires but reports parent instead of child (or vice versa).

**Solution**: Use `report latest event` parameter:

```yaml
# Report child/descendant event
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe
  report latest event: true  # Report chrome.exe
  with child:
    event: NEW_PROCESS
    op: ends with
    path: event/FILE_PATH
    value: chrome.exe
```

**Note**: Response actions always use latest event, regardless of this setting.

### Issue 5: Response Action Killed Wrong Process

**Symptoms**: `deny_tree` killed parent instead of child (or vice versa).

**Solution**: Use correct routing reference:

```yaml
respond:
  # Kill the child/descendant (latest in chain)
  - action: task
    command: deny_tree <<routing/this>>

  # Kill the parent (initiator)
  - action: task
    command: deny_tree <<routing/parent>>
```

## Performance Problems

### Problem 1: High Memory Usage

**Symptoms**: Memory consumption increases after deploying stateful rules.

**Diagnosis**:
1. Check number of active stateful rules
2. Review parent event matching criteria
3. Examine time window durations

**Solutions**:

1. **Filter parent events more restrictively**:
   ```yaml
   # Before: Matches all processes
   detect:
     event: NEW_PROCESS
     op: exists
     path: event/FILE_PATH

   # After: Specific process only
   detect:
     event: NEW_PROCESS
     op: ends with
     path: event/FILE_PATH
     value: outlook.exe
     case sensitive: false
   ```

2. **Reduce time windows**:
   ```yaml
   # Before: 24 hours (holds state too long)
   within: 86400

   # After: 5 minutes (sufficient for most attacks)
   within: 300
   ```

3. **Use with_child instead of with_descendant**:
   ```yaml
   # Higher memory: Tracks entire tree
   with descendant:
     event: NEW_PROCESS
     op: ends with
     path: event/FILE_PATH
     value: calc.exe

   # Lower memory: Tracks only direct children
   with child:
     event: NEW_PROCESS
     op: ends with
     path: event/FILE_PATH
     value: calc.exe
   ```

4. **Add platform filters early**:
   ```yaml
   detect:
     event: NEW_PROCESS
     op: and
     rules:
       - op: is platform
         name: windows  # Filter immediately
       - op: ends with
         path: event/FILE_PATH
         value: outlook.exe
   ```

### Problem 2: High CPU Usage

**Symptoms**: Increased CPU consumption on sensors or backend.

**Causes**:
- Missing event type in child rules (checks all events)
- Too many active stateful rules
- Deep nesting (3+ levels)

**Solutions**:

1. **Always specify event type**:
   ```yaml
   # Before: Checks all child events
   with child:
     op: ends with
     path: event/FILE_PATH
     value: calc.exe

   # After: Checks only NEW_PROCESS events
   with child:
     event: NEW_PROCESS  # Critical for performance
     op: ends with
     path: event/FILE_PATH
     value: calc.exe
   ```

2. **Reduce nesting depth**:
   ```yaml
   # Avoid: 4 levels
   with child:
     with descendant:
       with descendant:
         with events:

   # Better: 2 levels
   with child:
     with descendant:
   ```

3. **Consolidate rules**:
   - Merge similar rules where possible
   - Use `or` operators instead of multiple rules

### Problem 3: Runaway Response Actions

**Symptoms**: Same sensor command triggered repeatedly.

**Cause**: Missing or incorrect suppression.

**Solution**: Always use suppression with sensor commands:

```yaml
respond:
  - action: task
    command: history_dump
    investigation: attack-chain
    suppression:
      is_global: false
      keys:
        - '{{ .routing.sid }}'  # Per-sensor
        - '{{ .event.PROCESS_ID }}'  # Per-process
      max_count: 1  # Only once
      period: 5m  # Per 5 minutes
```

**Best practices**:
- Use `is_global: false` for sensor-specific actions
- Include sensor ID in suppression keys
- Include process ID for process-specific actions
- Set reasonable period (5m to 1h)

## Debugging Techniques

### Technique 1: Progressive Complexity

Build rules incrementally:

**Step 1**: Test parent matching only
```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe
  case sensitive: false
respond:
  - action: report
    name: Outlook Launched
```

**Step 2**: Add child matching
```yaml
detect:
  event: NEW_PROCESS
  op: ends with
  path: event/FILE_PATH
  value: outlook.exe
  case sensitive: false
  with child:
    event: NEW_PROCESS
    op: ends with
    path: event/FILE_PATH
    value: chrome.exe
    case sensitive: false
respond:
  - action: report
    name: Outlook -> Chrome
```

**Step 3**: Add complexity (counting, nesting, etc.)

### Technique 2: Enable Verbose Logging

Use metadata to track detection details:

```yaml
respond:
  - action: report
    name: "Detection: {{ .event.FILE_PATH }}"
    metadata:
      parent_process: '{{ .routing.parent }}'
      process_id: '{{ .event.PROCESS_ID }}'
      command_line: '{{ .event.COMMAND_LINE }}'
      detection_time: '{{ .routing.event_time }}'
```

### Technique 3: Test Both Match and Non-Match Cases

Always include both positive and negative test cases:

```yaml
tests:
  match:
    # Should detect: outlook -> chrome
    - - event: { FILE_PATH: "outlook.exe" }
        routing: { event_type: NEW_PROCESS, this: p1 }
      - event: { FILE_PATH: "chrome.exe" }
        routing: { event_type: NEW_PROCESS, this: c1, parent: p1 }

  non_match:
    # Should NOT detect: notepad -> chrome
    - - event: { FILE_PATH: "notepad.exe" }
        routing: { event_type: NEW_PROCESS, this: p2 }
      - event: { FILE_PATH: "chrome.exe" }
        routing: { event_type: NEW_PROCESS, this: c2, parent: p2 }

    # Should NOT detect: outlook -> firefox
    - - event: { FILE_PATH: "outlook.exe" }
        routing: { event_type: NEW_PROCESS, this: p3 }
      - event: { FILE_PATH: "firefox.exe" }
        routing: { event_type: NEW_PROCESS, this: c3, parent: p3 }
```

### Technique 4: Isolate Variables

Test one stateful operator at a time:

1. Test `with child` alone
2. Test `with descendant` alone
3. Test `with events` alone
4. Combine only after individual testing succeeds

### Technique 5: Use Test Sensors

Deploy test sensors that generate controlled behavior:

```bash
# Windows test sensor
# Launch controlled process chains
cmd.exe
  -> calc.exe  (should match)
  -> notepad.exe (should not match)

# Monitor detections in LimaCharlie console
```

## Best Practices Checklist

Before deploying a stateful rule to production, verify:

### Rule Design
- [ ] Parent event criteria is as specific as possible
- [ ] Event type specified in all child/descendant rules
- [ ] `is stateless: true` used for atomic conditions
- [ ] Platform filters applied early
- [ ] Time windows are as short as possible
- [ ] Nesting limited to 2-3 levels maximum

### Testing
- [ ] Syntax validated with `limacharlie replay --validate`
- [ ] Unit tests added to rule (both match and non-match)
- [ ] Tested with synthetic events
- [ ] Tested on non-production sensors
- [ ] Verified correct event is reported
- [ ] Verified response actions target correct process

### Performance
- [ ] Parent matching is restrictive (not overly broad)
- [ ] Event types specified (avoid matching all events)
- [ ] Time windows minimized
- [ ] Suppression added to all sensor commands
- [ ] Memory/CPU impact estimated

### Documentation
- [ ] Rule name is descriptive
- [ ] MITRE ATT&CK techniques tagged in metadata
- [ ] Description explains detection logic
- [ ] Comments added for complex logic

### Response Actions
- [ ] Appropriate priority level (3-5)
- [ ] Correct routing reference (`<<routing/this>>` vs `<<routing/parent>>`)
- [ ] Suppression configured
- [ ] Investigation name set for forensics
- [ ] Network isolation used for critical threats

### Monitoring
- [ ] Plan for monitoring false positive rate
- [ ] Alert fatigue considered
- [ ] Escalation process defined
- [ ] Rule review schedule established

## Getting Help

If you encounter issues not covered here:

1. **Check Rule Syntax**: Validate with `limacharlie replay --validate`
2. **Review Examples**: See [EXAMPLES.md](EXAMPLES.md) for working rules
3. **Consult Reference**: Check [REFERENCE.md](REFERENCE.md) for operator details
4. **Community Support**: LimaCharlie Slack channel
5. **Professional Services**: Contact LimaCharlie support for complex cases

## Common Pitfalls Summary

| Issue | Cause | Solution |
|-------|-------|----------|
| Rule not matching | Parent started before rule deployed | Restart parent process |
| Too many false positives | Parent criteria too broad | Filter parent more specifically |
| Wrong event reported | Missing `report latest event` | Add `report latest event: true` |
| Wrong process killed | Using wrong routing reference | Use `<<routing/this>>` or `<<routing/parent>>` |
| High memory usage | Broad parent matching or long time windows | Filter earlier, reduce time windows |
| High CPU usage | Missing event type in child rules | Always specify `event:` in child rules |
| Runaway actions | Missing suppression | Add suppression to all sensor commands |
| Rule stopped working | Rule was modified | Restart parent processes after modification |

---

This troubleshooting guide covers common issues and testing strategies for stateful rules. For complete operator reference, see [REFERENCE.md](REFERENCE.md). For working examples, see [EXAMPLES.md](EXAMPLES.md).
