# Threat Intelligence Troubleshooting Guide

Solutions for common issues with threat intelligence integrations in LimaCharlie.

## Table of Contents

1. [Lookup Not Matching](#lookup-not-matching)
2. [Metadata Rules Not Evaluating](#metadata-rules-not-evaluating)
3. [API Rate Limiting](#api-rate-limiting)
4. [Lookup Manager Not Syncing](#lookup-manager-not-syncing)
5. [Performance Issues](#performance-issues)
6. [API Authentication Errors](#api-authentication-errors)
7. [False Positives](#false-positives)
8. [Missing Detections](#missing-detections)
9. [Cache Issues](#cache-issues)
10. [Feed Format Errors](#feed-format-errors)

## Lookup Not Matching

### Problem

Lookup operator not matching expected indicators in your custom feed.

### Symptoms

- Rule doesn't trigger when it should
- Detection works with some indicators but not others
- Lookup appears to return no results

### Debugging Steps

#### 1. Verify Lookup Exists

Check that the lookup is created and accessible:

```bash
# Via web UI
Navigate to: Automation > Lookups
Confirm lookup name appears in list
```

```yaml
# Via Infrastructure as Code
# Ensure lookup is defined in hives section
hives:
  lookup:
    my-lookup-name:
      data:
        lookup_data:
          ...
```

#### 2. Check Case Sensitivity

By default, lookups are case-sensitive. If your indicators use mixed case:

**Problem:**
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME  # Value: "EVIL.COM"
  resource: hive://lookup/malware-domains  # Contains: "evil.com"
  # Won't match - case mismatch
```

**Solution:**
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malware-domains
  case sensitive: false  # Add this
```

#### 3. Verify Path Extracts Correct Value

The `path` must point to the actual indicator in the event.

**Debug Rule to View Extracted Value:**
```yaml
detect:
  event: DNS_REQUEST
  op: exists
  path: event/DOMAIN_NAME

respond:
  - action: report
    name: debug-domain-value
    metadata:
      domain_value: '{{ .event.DOMAIN_NAME }}'
      full_event: '{{ .event }}'
```

Check the report metadata to see what value is actually being extracted.

#### 4. Verify Lookup Data Format

Ensure your lookup data is properly formatted:

**Correct - Key is string, value is dict:**
```json
{
  "lookup_data": {
    "evil.com": {},
    "8.8.8.8": {"category": "dns"}
  }
}
```

**Incorrect - Value is not a dict:**
```json
{
  "lookup_data": {
    "evil.com": "malware",  // Wrong - must be dict
    "8.8.8.8": null         // Wrong - must be dict
  }
}
```

#### 5. Test with Rule Tester

Use the rule tester in the web UI:

1. Navigate to **D&R Rules**
2. Click **Test Rule**
3. Paste your rule
4. Provide test event with known indicator
5. Check if lookup matches

**Test Event Example:**
```json
{
  "event": "DNS_REQUEST",
  "data": {
    "DOMAIN_NAME": "evil.com"
  }
}
```

#### 6. Check for Whitespace

Indicators with trailing/leading whitespace won't match:

**Problem in Newline Format:**
```
"evil.com \nmalware.net\n 8.8.8.8"
         ↑ trailing space    ↑ leading space
```

**Solution:**
Strip whitespace when creating feed, or normalize in rule with transforms.

### Common Solutions

**Solution 1: Case Insensitive**
```yaml
case sensitive: false
```

**Solution 2: Normalize Domain**
```yaml
op: lookup
path: event/DOMAIN_NAME
sub domain: "-2:"  # Get base domain only
resource: hive://lookup/domains
```

**Solution 3: Extract Filename**
```yaml
op: lookup
path: event/FILE_PATH
file name: true  # Extract filename from full path
resource: hive://lookup/malware-files
```

## Metadata Rules Not Evaluating

### Problem

Metadata rules on API lookups not matching expected responses.

### Symptoms

- Lookup appears to work but metadata rules never match
- Rules work without metadata rules but fail when added
- Inconsistent matching behavior

### Debugging Steps

#### 1. Verify API Response Structure

First, confirm the API is returning data:

**Test with Minimal Rule:**
```yaml
detect:
  event: CODE_IDENTITY
  op: lookup
  path: event/HASH
  resource: hive://lookup/vt
  # No metadata_rules - just verify lookup works

respond:
  - action: report
    name: vt-lookup-test
    metadata:
      hash: '{{ .event.HASH }}'
      lookup_result: '{{ .lookup }}'
```

Check the report to see the full API response structure.

#### 2. Verify JSON Path Syntax

Metadata rules use JSON path notation with `/` separators:

**Correct:**
```yaml
metadata_rules:
  op: is greater than
  value: 5
  path: /positives  # Leading slash
```

**Incorrect:**
```yaml
metadata_rules:
  op: is greater than
  value: 5
  path: positives  # Missing leading slash
```

#### 3. Check Nested Field Access

For nested fields, use `/` to traverse:

**API Response:**
```json
{
  "api_vt": {
    "scans": {
      "Microsoft": {
        "detected": true,
        "result": "Trojan"
      }
    }
  }
}
```

**Correct Path:**
```yaml
metadata_rules:
  op: is
  value: true
  path: /scans/Microsoft/detected
```

#### 4. Test with Existence Check First

Start with a simple existence check, then narrow:

**Step 1 - Verify response exists:**
```yaml
metadata_rules:
  op: exists
  path: /
```

**Step 2 - Verify field exists:**
```yaml
metadata_rules:
  op: exists
  path: /positives
```

**Step 3 - Check value:**
```yaml
metadata_rules:
  op: is greater than
  value: 0
  path: /positives
```

#### 5. Check Data Types

Ensure value type matches field type:

**String Field:**
```yaml
metadata_rules:
  op: is
  value: "malicious"  # String in quotes
  path: /verdict
```

**Integer Field:**
```yaml
metadata_rules:
  op: is greater than
  value: 5  # Integer without quotes
  path: /positives
```

**Boolean Field:**
```yaml
metadata_rules:
  op: is
  value: true  # Boolean without quotes
  path: /seen
```

### Common Solutions

**Solution 1: Check Response Format in Documentation**

Each API has different response formats. See [REFERENCE.md](./REFERENCE.md) for exact structures.

**Solution 2: Use Length Check for Simple Lookups**

For feeds that just return `{}`, check if response exists:

```yaml
metadata_rules:
  op: is greater than
  value: 0
  path: /
  length of: true
```

**Solution 3: Handle Missing Fields**

Some API responses may not include certain fields:

```yaml
metadata_rules:
  op: or
  rules:
    - op: not
      op: exists
      path: /positives
    - op: is greater than
      value: 0
      path: /positives
```

## API Rate Limiting

### Problem

Hitting API rate limits or incurring unexpected costs.

### Symptoms

- API errors in logs
- Missing detections
- High API billing
- Slow rule evaluation

### VirusTotal Rate Limits

**Free Tier**: 4 requests per minute

**Symptoms:**
- Lookups fail after 4 requests
- Some hashes not checked

**Solutions:**

#### 1. Use Global Caching

LimaCharlie caches VT results for 3 days globally:

```yaml
# First lookup triggers API call
# Subsequent lookups within 3 days use cache
# No action needed - automatic
```

#### 2. Local Cache First

Create local known-good hash list:

```yaml
detect:
  event: CODE_IDENTITY
  op: and
  rules:
    # Check local cache first (free, instant)
    - op: not
      op: lookup
      path: event/HASH
      resource: hive://lookup/known-good-hashes
    # Only query VT if not in cache
    - op: lookup
      path: event/HASH
      resource: hive://lookup/vt
      metadata_rules:
        op: is greater than
        value: 2
        path: /positives

respond:
  - action: report
    name: malware-detected
```

#### 3. Apply to High-Fidelity Events Only

Don't check every file - filter first:

```yaml
detect:
  event: CODE_IDENTITY
  op: and
  rules:
    # Filter: unsigned files only
    - op: is
      value: 0
      path: event/SIGNATURE/FILE_IS_SIGNED
    # Filter: not signed by Microsoft
    - op: not
      op: contains
      path: event/SIGNATURE/CERT_ISSUER
      value: "Microsoft"
    # Now query VT
    - op: lookup
      path: event/HASH
      resource: hive://lookup/vt
```

#### 4. Implement Suppression

Prevent duplicate lookups for same hash:

```yaml
respond:
  - action: report
    name: malware-detected
    suppression:
      max_count: 1
      period: 24h
      is_global: true
      keys:
        - '{{ .event.HASH }}'  # Suppress by hash
```

### GreyNoise / EchoTrail / Other APIs

**Rate Limits**: Vary by subscription plan

**Solutions:**

#### 1. Check Account Settings

Log into provider dashboard to view:
- Current rate limits
- Usage statistics
- Billing information

#### 2. Apply Only to Public IPs

For GreyNoise, filter private IPs first:

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    # Check if public IP first (free operation)
    - op: is public address
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
    # Then query GreyNoise
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/greynoise-noise-context
```

#### 3. Use RIOT for Filtering

GreyNoise RIOT is cheaper/faster than full context lookup:

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    # Use RIOT first (cheaper)
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/greynoise-riot
      metadata_rules:
        op: is
        value: false
        path: /riot  # Not a benign service
    # Only query full context if not RIOT
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/greynoise-noise-context
```

### Cost Optimization Summary

1. **Layer checks**: Free local lookups → Cheap APIs → Expensive APIs
2. **Filter first**: Apply business logic before API calls
3. **Suppress duplicates**: Use global suppression by indicator
4. **Leverage caching**: Trust LimaCharlie's global cache
5. **Monitor usage**: Track API consumption in provider dashboards

## Lookup Manager Not Syncing

### Problem

Feeds not updating via Lookup Manager extension.

### Symptoms

- Stale threat feed data
- Manual sync fails
- Extension shows errors
- New indicators not appearing

### Debugging Steps

#### 1. Check Extension Status

Verify extension is running:

```bash
# Via web UI
Navigate to: Extensions > Lookup Manager
Check status indicator (should be green/active)
```

#### 2. Verify URL/ARL Accessibility

Test if feed URL is accessible:

**Public URL Test:**
```bash
curl -I https://example.com/threat-feeds/malware-ips.json
# Should return 200 OK
```

**GitHub ARL Test:**
Verify:
- Repository exists
- File path is correct
- Token has `repo` permissions
- Token hasn't expired

#### 3. Check Feed Format

Feed must be valid JSON:

**Valid Feed:**
```json
{
  "lookup_data": {
    "8.8.8.8": {},
    "evil.com": {"category": "malware"}
  }
}
```

**Invalid Feed (will fail):**
```json
{
  "indicators": [  // Wrong structure
    "8.8.8.8",
    "evil.com"
  ]
}
```

#### 4. Review Extension Logs

Check extension logs for errors:

```bash
# Via web UI
Navigate to: Extensions > Lookup Manager > Logs
Look for:
- Authentication errors
- Network errors
- Parse errors
```

#### 5. Manual Sync Test

Try manual sync to see immediate errors:

```bash
# Via web UI
Navigate to: Extensions > Lookup Manager
Click: Manual Sync
Watch for error messages
```

### Common Issues and Solutions

#### Issue 1: GitHub Token Expired

**Error**: "Authentication failed" or "401 Unauthorized"

**Solution:**
1. Generate new GitHub personal access token
2. Update ARL with new token:
```
[github,org/repo/path.json,token,ghp_NEW_TOKEN_HERE]
```

#### Issue 2: Invalid JSON

**Error**: "Failed to parse feed" or "Invalid JSON"

**Solution:**
Validate feed JSON:
```bash
cat feed.json | jq .
# Should output formatted JSON without errors
```

#### Issue 3: Wrong File Path

**Error**: "404 Not Found" or "File not found"

**Solution:**
Verify GitHub path:
```
[github,org-name/repo-name/path/to/file.json,token,...]
         ↑        ↑         ↑
         org      repo      path from repo root
```

#### Issue 4: Network Restrictions

**Error**: "Connection timeout" or "Network error"

**Solution:**
- Check firewall rules
- Verify DNS resolution
- Test URL from external location
- Check GitHub status (status.github.com)

### Infrastructure as Code Troubleshooting

If using IaC, verify configuration:

```yaml
hives:
  extension_config:
    ext-lookup-manager:
      data:
        lookup_manager_rules:
          - name: my-feed
            predefined: ""  # Empty for custom URL
            format: json    # Must be "json"
            tags:
              - custom
            arl: "[https,example.com/feed.json]"  # Check URL
```

**Common IaC Mistakes:**
- Missing quotes around ARL
- Wrong format type (must be "json")
- Empty arl field when predefined is also empty
- Typo in extension name (`ext-lookup-manager`)

## Performance Issues

### Problem

Rules with lookups running slowly or causing delays.

### Symptoms

- Slow detection times
- Event backlog
- High CPU usage
- Detection delays

### Optimization Techniques

#### 1. Reduce Lookup Frequency

Apply lookups only when necessary:

**Inefficient:**
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malware-domains
  # Checks EVERY DNS request
```

**Efficient:**
```yaml
detect:
  event: DNS_REQUEST
  op: and
  rules:
    # Filter first
    - op: not
      op: contains
      path: event/DOMAIN_NAME
      value: ".local"
    - op: not
      op: ends with
      path: event/DOMAIN_NAME
      value: ".corp.com"
    # Then lookup (fewer events)
    - op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/malware-domains
```

#### 2. Use Scoped Operators

For arrays, use `scope` instead of wildcard:

**Less Efficient:**
```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: event/NETWORK_ACTIVITY/?/IP_ADDRESS  # Checks every IP
  resource: hive://lookup/malware-ips
```

**More Efficient:**
```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: scope
  path: event/NETWORK_ACTIVITY/
  rule:
    op: and
    rules:
      # Filter first
      - op: is public address
        path: event/IP_ADDRESS
      # Then lookup (only public IPs)
      - op: lookup
        path: event/IP_ADDRESS
        resource: hive://lookup/malware-ips
```

#### 3. Order Operations Efficiently

Put cheap operations first, expensive last:

**Inefficient Order:**
```yaml
op: and
rules:
  - op: lookup  # Expensive - API call
    path: event/HASH
    resource: hive://lookup/vt
  - op: is  # Cheap - local check
    value: 0
    path: event/SIGNATURE/FILE_IS_SIGNED
```

**Efficient Order:**
```yaml
op: and
rules:
  - op: is  # Cheap - local check first
    value: 0
    path: event/SIGNATURE/FILE_IS_SIGNED
  - op: lookup  # Expensive - only if first matches
    path: event/HASH
    resource: hive://lookup/vt
```

#### 4. Use Local Lookups as Filters

Local lookups are faster than APIs:

```yaml
detect:
  op: and
  rules:
    - op: not
      op: lookup  # Local lookup - fast
      path: event/HASH
      resource: hive://lookup/known-good
    - op: not
      op: lookup  # Local lookup - fast
      path: event/DOMAIN_NAME
      resource: hive://lookup/corporate-domains
    - op: lookup  # API lookup - slow, but fewer calls
      path: event/HASH
      resource: hive://lookup/vt
```

#### 5. Optimize Lookup Size

Large lookups slow down matching:

**Problem:** 1M+ indicator lookup with linear search

**Solution:** Split into multiple focused lookups:
- `malware-ips-critical` (100 indicators, high priority)
- `malware-ips-standard` (10K indicators, medium priority)
- `malware-ips-historical` (1M indicators, low priority)

Check critical list in high-priority rules, historical in low-priority rules.

## API Authentication Errors

### Problem

API key authentication failures.

### Symptoms

- "Unauthorized" errors
- "Invalid API key" errors
- Lookups work in web UI but fail in rules
- Intermittent authentication issues

### Debugging Steps

#### 1. Verify API Key Format

Different providers have different key formats:

**VirusTotal:**
```
abc123def456...  # Simple API key
```

**Pangea:**
```
aws.us.pangea.cloud/pts_7kb33fyz313372vuu5zg...  # domain/token format
```

**GreyNoise:**
```
key:abc123...  # May use "key:" prefix
```

#### 2. Check Key Location

Verify key is in correct integration settings:

```bash
# Via web UI
Navigate to: Organization > Integrations
Find provider (e.g., VirusTotal)
Verify API key is entered
Click "Test" if available
```

#### 3. Verify Subscription

Ensure you're subscribed to the add-on:

```bash
# Via web UI
Navigate to: Add-ons > Marketplace
Search for integration (e.g., "vt")
Verify "Subscribed" badge appears
```

#### 4. Check Key Permissions

Some APIs require specific permissions:

**GitHub Token:**
- Needs `repo` scope for private repositories
- Check token permissions at github.com/settings/tokens

**Pangea:**
- Needs appropriate service permissions enabled
- Check at Pangea dashboard

#### 5. Test API Key Externally

Test key outside LimaCharlie:

**VirusTotal:**
```bash
curl -H "x-apikey: YOUR_KEY" \
  "https://www.virustotal.com/api/v3/files/abc123..."
```

**GreyNoise:**
```bash
curl -H "key: YOUR_KEY" \
  "https://api.greynoise.io/v3/community/8.8.8.8"
```

### Common Solutions

#### Solution 1: Regenerate API Key

If key is expired or corrupted:
1. Log into provider dashboard
2. Generate new API key
3. Update key in LimaCharlie integrations
4. Test with simple lookup

#### Solution 2: Check Key Quotas

Some free tiers have monthly quotas:
- VirusTotal free: 500 requests/day
- Check provider dashboard for quota status
- Upgrade plan if exceeded

#### Solution 3: Whitelist LimaCharlie IPs

Some providers require IP whitelisting:
- Contact provider for required IPs
- Add LimaCharlie infrastructure IPs to allowlist

## False Positives

### Problem

Too many false positive alerts from threat intel lookups.

### Symptoms

- High alert volume
- Known benign services triggering alerts
- Corporate infrastructure flagged as suspicious
- Legitimate tools marked as malicious

### Solutions

#### 1. Use GreyNoise RIOT Filtering

Filter out known benign services:

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/malware-ips
    # Add RIOT filter
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/greynoise-riot
      metadata_rules:
        op: is
        value: false
        path: /riot  # Only alert if NOT benign service
```

#### 2. Create Corporate Whitelists

Maintain lists of known-good infrastructure:

```yaml
hives:
  lookup:
    corporate-infrastructure:
      data:
        lookup_data:
          192.168.10.5: {hostname: "dc01.corp.local"}
          10.0.0.100: {hostname: "fileserver.local"}
          proxy.corp.com: {type: "proxy"}
```

Use in rules:

```yaml
detect:
  op: and
  rules:
    - op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/suspicious-domains
    - op: not
      op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/corporate-infrastructure
```

#### 3. Adjust Thresholds

Increase confidence thresholds:

**Too Sensitive:**
```yaml
metadata_rules:
  op: is greater than
  value: 0  # Any detection
  path: /positives
```

**Better Threshold:**
```yaml
metadata_rules:
  op: is greater than
  value: 5  # 5+ detections
  path: /positives
```

#### 4. Multi-Source Validation

Require multiple sources to agree:

```yaml
detect:
  op: and
  rules:
    # Both Pangea and AlphaMountain must agree
    - op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/pangea-domain-reputation
      metadata_rules:
        op: is
        value: "malicious"
        path: /verdict
    - op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/alphamountain-threat
      metadata_rules:
        op: is greater than
        value: 70
        path: /score
```

#### 5. Context-Aware Detection

Add behavioral context:

```yaml
detect:
  op: and
  rules:
    - op: lookup
      path: event/FILE_PATH
      resource: hive://lookup/suspicious-files
    # Add context: unsigned file
    - op: is
      value: 0
      path: event/SIGNATURE/FILE_IS_SIGNED
    # Add context: unusual location
    - op: contains
      path: event/FILE_PATH
      value: "\\Users\\"
```

## Missing Detections

### Problem

Expected detections not triggering when they should.

### Symptoms

- Known malicious indicators not detected
- Rules work in testing but not in production
- Inconsistent detection behavior

### Debugging Steps

#### 1. Verify Indicator in Feed

Check if indicator exists in lookup:

```bash
# Via web UI
Navigate to: Automation > Lookups
Click on lookup name
Search for indicator
```

#### 2. Check Event Availability

Verify event type is being generated:

```yaml
# Create monitoring rule
detect:
  event: CODE_IDENTITY  # Event type you expect
  op: exists
  path: event/HASH

respond:
  - action: report
    name: debug-event-seen
    metadata:
      hash: '{{ .event.HASH }}'
```

#### 3. Test Rule Syntax

Use rule tester with known malicious indicator:

```bash
# Via web UI
Navigate to: D&R Rules > Test Rule
Paste detection rule
Create test event with known malicious indicator
Verify rule matches
```

#### 4. Check Rule Targeting

Ensure rule targets correct sensors/platforms:

```yaml
detect:
  target: windows  # Add if needed
  event: CODE_IDENTITY
  # ...
```

#### 5. Verify Rule is Enabled

Confirm rule is active:

```bash
# Via web UI
Navigate to: D&R Rules
Find your rule
Check status (should be "Enabled", not "Disabled")
```

### Common Solutions

#### Solution 1: Update Feed Data

Ensure latest threat data is loaded:

```bash
# Via Lookup Manager
Navigate to: Extensions > Lookup Manager
Click: Manual Sync
Wait for completion
```

#### Solution 2: Check Suppression

Verify detection isn't being suppressed:

```yaml
# Temporarily remove suppression for testing
respond:
  - action: report
    name: test-detection
    # suppression:  # Comment out
    #   max_count: 1
    #   period: 24h
```

#### Solution 3: Broaden Detection

Make rule less restrictive for testing:

```yaml
# Start broad
detect:
  event: CODE_IDENTITY
  op: lookup
  path: event/HASH
  resource: hive://lookup/vt
  # No metadata_rules - just test lookup works

# Then add restrictions
detect:
  event: CODE_IDENTITY
  op: lookup
  path: event/HASH
  resource: hive://lookup/vt
  metadata_rules:
    op: is greater than
    value: 0  # Any detection
    path: /positives
```

## Cache Issues

### Problem

Stale or incorrect cached data from API lookups.

### Symptoms

- Detection based on outdated threat intel
- Changes to feeds not reflected in detections
- API updates not appearing

### Understanding Caching

**VirusTotal**: 3-day global cache (all LimaCharlie users)

**Other APIs**: Caching varies by provider

**Local Lookups**: No caching (always up-to-date)

### Solutions

#### Solution 1: Wait for Cache Expiry

For VirusTotal:
- Cache expires after 3 days
- New lookup will refresh cache
- Can't force cache clear (global cache)

#### Solution 2: Use Different Indicator

If testing, use hash that hasn't been looked up:
- Generate new test file
- Use hash that's not in cache

#### Solution 3: Test with Local Lookup

Local lookups don't cache:

```yaml
# Create test lookup with known indicator
hives:
  lookup:
    test-malware:
      data:
        lookup_data:
          abc123...: {test: true}

# Test rule with local lookup (no cache)
detect:
  op: lookup
  path: event/HASH
  resource: hive://lookup/test-malware
```

#### Solution 4: Monitor Feed Updates

For Lookup Manager feeds:
- Check last sync time
- Manual sync to force update
- Verify new indicators appear immediately (no cache)

## Feed Format Errors

### Problem

Errors when creating or importing custom threat feeds.

### Symptoms

- "Invalid format" errors
- Feed creation fails
- Indicators don't appear after import
- Lookup returns no results

### Common Format Issues

#### Issue 1: Value Not a Dictionary

**Error:** "Lookup value must be a dictionary"

**Wrong:**
```json
{
  "lookup_data": {
    "evil.com": "malware"  // String, not dict
  }
}
```

**Correct:**
```json
{
  "lookup_data": {
    "evil.com": {"category": "malware"}  // Dict
  }
}
```

Or use empty dict:
```json
{
  "lookup_data": {
    "evil.com": {}  // Empty dict is valid
  }
}
```

#### Issue 2: Invalid JSON

**Error:** "Failed to parse JSON"

**Wrong:**
```json
{
  "lookup_data": {
    "evil.com": {category: "malware"}  // Missing quotes on key
  }
}
```

**Correct:**
```json
{
  "lookup_data": {
    "evil.com": {"category": "malware"}  // Quoted key
  }
}
```

Validate JSON:
```bash
cat feed.json | jq .
# Should output formatted JSON without errors
```

#### Issue 3: Wrong Top-Level Key

**Error:** "Missing lookup_data key"

**Wrong:**
```json
{
  "indicators": {  // Wrong key
    "evil.com": {}
  }
}
```

**Correct:**
```json
{
  "lookup_data": {  // Must be "lookup_data"
    "evil.com": {}
  }
}
```

#### Issue 4: Newline Format Issues

**Wrong:**
```json
{
  "newline_content": ["evil.com", "8.8.8.8"]  // Array, not string
}
```

**Correct:**
```json
{
  "newline_content": "evil.com\n8.8.8.8"  // String with newlines
}
```

### Validation Checklist

Before importing feed:

1. **Valid JSON**: Test with `jq` or JSON validator
2. **Correct structure**: `lookup_data` or `newline_content` or `yaml_content`
3. **Values are dicts**: Even empty `{}` is fine
4. **No trailing commas**: JSON doesn't allow trailing commas
5. **Proper escaping**: Escape special characters in strings
6. **UTF-8 encoding**: Use UTF-8 for international characters

## Summary

### Quick Troubleshooting Checklist

**Lookup not matching:**
- [ ] Verify lookup exists
- [ ] Check case sensitivity setting
- [ ] Verify path extracts correct value
- [ ] Test with rule tester

**Metadata rules not working:**
- [ ] Check JSON path syntax (leading `/`)
- [ ] Verify data types match
- [ ] Test with existence check first
- [ ] Review API response format

**Rate limiting:**
- [ ] Check API dashboard for quotas
- [ ] Implement local caching
- [ ] Add filtering before lookups
- [ ] Use suppression

**Lookup Manager issues:**
- [ ] Verify URL/ARL accessibility
- [ ] Check feed JSON format
- [ ] Review extension logs
- [ ] Test manual sync

**Performance:**
- [ ] Filter before lookups
- [ ] Order operations efficiently
- [ ] Use scoped operators
- [ ] Optimize lookup size

**False positives:**
- [ ] Use GreyNoise RIOT filtering
- [ ] Create corporate whitelists
- [ ] Adjust confidence thresholds
- [ ] Require multi-source validation

### Getting Help

If issues persist:

1. **Check documentation**: [REFERENCE.md](./REFERENCE.md) for API details
2. **Review examples**: [EXAMPLES.md](./EXAMPLES.md) for working patterns
3. **Community support**: LimaCharlie Slack channel
4. **Support ticket**: For platform-specific issues
5. **Provider support**: For API-specific problems

### Additional Resources

- LimaCharlie Documentation: https://doc.limacharlie.io
- D&R Rules Reference: https://doc.limacharlie.io/docs/documentation/docs/dr.md
- Community Slack: https://slack.limacharlie.io
