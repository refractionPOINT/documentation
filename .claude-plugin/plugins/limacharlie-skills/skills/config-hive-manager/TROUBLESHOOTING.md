# Config Hive Troubleshooting Guide

Solutions to common issues when working with the LimaCharlie Config Hive including access problems, ARL issues, and Infrastructure as Code integration challenges.

## Access and Permission Issues

### Issue: "Permission denied" when accessing hive

**Symptoms:**
- Unable to list, get, or set hive records
- Error message: "Permission denied" or "Insufficient permissions"

**Possible Causes:**
1. User lacks necessary hive permissions
2. API key has insufficient permissions
3. Accessing wrong organization

**Solutions:**

**Check user permissions:**
```bash
# View current user permissions
limacharlie user get --user-email your-email@example.com

# Check for required permissions:
# - secret.get, secret.set for secrets
# - dr.list, dr.set for D&R rules
# - yara.get, yara.set for YARA rules
# - lookup.get, lookup.set for lookups
```

**Verify organization access:**
```bash
# Confirm you're accessing the correct organization
limacharlie whoami

# Specify organization explicitly
limacharlie -o your-org-name hive list secret
```

**Check API key permissions:**
```bash
# If using API key, verify it has the required permissions
# API keys need specific hive permissions granted when created
```

**Grant permissions (requires admin access):**
```bash
# Grant secret permissions to user
limacharlie user add-permission --user-email user@example.com --permission secret.get
limacharlie user add-permission --user-email user@example.com --permission secret.set

# Grant D&R permissions
limacharlie user add-permission --user-email user@example.com --permission dr.list
limacharlie user add-permission --user-email user@example.com --permission dr.set
```

### Issue: "Hive record not found"

**Symptoms:**
- Error when getting a specific hive record
- Record appears in list but cannot be retrieved

**Possible Causes:**
1. Key name is case-sensitive and doesn't match
2. Wrong hive type specified
3. Record was deleted
4. Accessing wrong organization/partition

**Solutions:**

**List available records to verify name:**
```bash
# List all records in the hive
limacharlie hive list secret

# Look for the exact key name (case matters!)
```

**Check hive type:**
```bash
# Ensure you're using the correct hive type
limacharlie hive get secret --key my-key      # Correct
limacharlie hive get dr-general --key my-key  # Wrong hive type
```

**Verify organization:**
```bash
# Confirm organization
limacharlie whoami

# Try with explicit organization
limacharlie -o your-org hive get secret --key my-key
```

**Check metadata to see if disabled:**
```bash
# Get metadata only
limacharlie hive get_mtd secret --key my-key

# Look for "enabled": false
```

### Issue: Can see metadata but not actual data

**Symptoms:**
- `hive get_mtd` works but `hive get` fails
- Can list records but cannot retrieve values

**Possible Causes:**
1. User has metadata permissions but not data permissions
2. Intentional security restriction

**Solutions:**

**Check permissions:**
```bash
# You may have:
# - secret.get.mtd (metadata only)
# But need:
# - secret.get (full data access)
```

**Request appropriate permissions:**
```bash
# Admin needs to grant data access permission
limacharlie user add-permission --user-email user@example.com --permission secret.get
```

This is by design for security - some users should only see that a secret exists without seeing its value.

## ARL (Authentication Resource Locator) Issues

### Issue: "Invalid ARL format"

**Symptoms:**
- Configuration fails to save
- Error message about invalid ARL syntax
- Resources not loading

**Possible Causes:**
1. Incorrect ARL syntax
2. Missing components
3. Wrong hive type or key name

**Solutions:**

**Verify hive ARL format:**
```bash
# Correct hive ARL format
hive://HIVE_TYPE/KEY_NAME

# Examples:
hive://secret/my-api-key          # Correct
hive://secrets/my-api-key         # Wrong (should be 'secret' not 'secrets')
hive://secret/my api key          # Wrong (no spaces in key names)
hive://secret/my-api-key/value    # Wrong (no extra path components)
```

**Verify external ARL format:**
```bash
# Format: [method,destination,authType,authData]

# Correct examples:
[https,api.example.com/data]                                    # Public HTTPS
[https,api.example.com/data,bearer,token123]                   # HTTPS with bearer token
[https,api.example.com/data,bearer,hive://secret/api-token]    # HTTPS with hive secret
[github,username/repo/path/file.json]                           # Public GitHub
[github,username/repo/path/file.json,token,ghp_abc123]         # Private GitHub

# Wrong examples:
[http://api.example.com/data]                    # Don't include protocol in method
[https,api.example.com,bearer]                   # Missing auth data
[github,username,repo,path,file.json]            # Wrong format (use slashes)
```

**Test ARL resolution:**
```bash
# Create a test lookup or D&R rule to verify ARL works
# This helps identify if the ARL is the problem
```

### Issue: "Secret not decrypting in output/adapter"

**Symptoms:**
- Output or adapter shows error about credentials
- Secret appears as literal string instead of value
- Connection failures

**Possible Causes:**
1. Incorrect ARL format
2. Secret doesn't exist
3. Output/adapter lacks permission to access secret
4. Wrong secret key in hive

**Solutions:**

**Verify secret exists:**
```bash
# Check if secret exists
limacharlie hive get_mtd secret --key my-api-key

# List all secrets
limacharlie hive list secret
```

**Check ARL format in configuration:**
```yaml
# Correct
outputs:
  my-output:
    secret_key: hive://secret/my-api-key

# Wrong
outputs:
  my-output:
    secret_key: hive://secrets/my-api-key  # Wrong hive type
    secret_key: my-api-key                 # Missing hive:// prefix
    secret_key: "hive://secret/my-api-key" # Don't quote ARLs in YAML
```

**Verify secret data structure:**
```bash
# For secrets, data should be under "secret" key
# Correct:
{
  "secret": "the-actual-value"
}

# When setting, use --data-key secret:
echo "value" | limacharlie hive set secret --key my-key --data - --data-key secret
```

### Issue: "YARA rule not found"

**Symptoms:**
- `yara_scan` command fails
- Error about missing rule
- D&R rule with YARA scan doesn't work

**Possible Causes:**
1. YARA rule not stored with correct data key
2. Wrong rule name in ARL
3. YARA rule has syntax errors

**Solutions:**

**Verify YARA rule exists:**
```bash
# List YARA rules
limacharlie hive list yara

# Get specific rule
limacharlie hive get yara --key my-yara-rule
```

**Check data key when storing:**
```bash
# YARA rules MUST use --data-key rule
limacharlie hive set yara --key my-rule --data rule.yara --data-key rule

# Verify structure:
{
  "rule": "rule content here..."
}
```

**Test YARA rule syntax:**
```bash
# Ensure YARA rule has valid syntax before storing
# Test locally if possible:
yara my-rule.yara /path/to/test/file
```

**Verify ARL in command:**
```bash
# Correct YARA scan command
yara_scan hive://yara/my-rule --pid 1234

# Wrong
yara_scan hive://yara/my-rule.yara --pid 1234  # No extension in key name
```

### Issue: "Lookup not matching expected values"

**Symptoms:**
- D&R rule with lookup operator not triggering
- Lookup seems to have data but doesn't match
- Unexpected match results

**Possible Causes:**
1. Case sensitivity mismatch
2. Wrong lookup data format
3. Incorrect lookup path in D&R rule
4. Whitespace or encoding issues

**Solutions:**

**Check case sensitivity:**
```yaml
# Make lookup case-insensitive
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/threat-domains
  case sensitive: false  # Add this line
```

**Verify lookup data format:**
```bash
# Get lookup and check format
limacharlie hive get lookup --key threat-domains

# Ensure it matches expected format:
{
  "lookup_data": {
    "key1": {},
    "key2": {}
  }
}

# NOT:
{
  "key1": {},
  "key2": {}
}
```

**Test with known values:**
```bash
# Create test lookup with known value
cat <<EOF | limacharlie hive set lookup --key test-lookup --data -
{
  "lookup_data": {
    "test.com": {"test": true}
  }
}
EOF

# Create simple D&R rule to test
# If this works, your lookup structure is correct
```

**Check for whitespace issues:**
```bash
# Ensure lookup keys don't have trailing/leading spaces
# JSON formatting can sometimes introduce unexpected whitespace
```

## Infrastructure as Code Issues

### Issue: "IaC push failing"

**Symptoms:**
- `infra push` command fails
- Error messages about invalid configuration
- Some resources update but others don't

**Possible Causes:**
1. YAML syntax errors
2. Invalid configuration structure
3. Permission issues
4. Conflicting resources

**Solutions:**

**Use dry-run first:**
```bash
# Always test before applying
limacharlie infra push -f config.yaml --dry-run

# Review what would change
# Look for errors in output
```

**Validate YAML syntax:**
```bash
# Use YAML validator
yamllint config.yaml

# Or Python
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Common issues:
# - Incorrect indentation
# - Missing colons
# - Unquoted strings with special characters
```

**Check version number:**
```yaml
# Must start with version number
version: 3

hives:
  secret:
    # ...
```

**Verify permissions:**
```bash
# Ensure you have permissions for all hive types in config
# Check error message for specific permission requirements
```

**Push incrementally:**
```bash
# If some resources work and others fail, split the config
# Create separate files for different hive types
# Push one at a time to identify the problem

limacharlie infra push -f secrets-only.yaml --dry-run
limacharlie infra push -f rules-only.yaml --dry-run
```

### Issue: "Configuration not syncing as expected"

**Symptoms:**
- Changes don't appear after push
- Some resources sync but others don't
- Unexpected resource deletion

**Possible Causes:**
1. Using wrong sync mode (additive vs force)
2. Not using sync flags for specific resources
3. Caching issues

**Solutions:**

**Understand sync modes:**
```bash
# Additive push (merges with existing config)
limacharlie infra push -f config.yaml

# Force push (exact copy - DELETES unspecified resources)
limacharlie infra push -f config.yaml --force

# Be careful with --force!
```

**Use specific sync flags:**
```bash
# Sync only D&R rules
limacharlie infra push -f config.yaml --sync-dr

# Sync D&R rules and outputs
limacharlie infra push -f config.yaml --sync-dr --sync-outputs

# Available flags:
# --sync-dr, --sync-outputs, --sync-resources
# --sync-artifacts, --sync-integrity, --sync-fp
# --sync-exfil, --sync-org-values
```

**Verify changes applied:**
```bash
# Fetch current config after push
limacharlie infra fetch > current.yaml

# Compare with what you pushed
diff config.yaml current.yaml
```

**Check for conflicts:**
```bash
# If multiple people are managing config, use version control
# Fetch latest before making changes
limacharlie infra fetch > latest.yaml
git diff latest.yaml  # Compare with your last fetch
```

### Issue: "Secrets appearing in IaC export"

**Symptoms:**
- Secret values visible in exported config
- Concerns about security when storing in Git

**Possible Causes:**
1. This is expected behavior - IaC exports include secret values
2. Need to sanitize before committing to version control

**Solutions:**

**Never commit actual secret values:**
```bash
# After fetching config, replace secret values with placeholders
limacharlie infra fetch > config.yaml

# Manually edit or use script to replace secret values:
# Change:
#   data:
#     secret: "actual-secret-value"
# To:
#   data:
#     secret: "PLACEHOLDER"

# Or remove secrets entirely from versioned config
```

**Use separate secret management:**
```bash
# Option 1: Keep secrets in separate file not in version control
cat config-without-secrets.yaml
cat secrets.yaml  # In .gitignore

# Deploy both:
limacharlie infra push -f config-without-secrets.yaml
limacharlie infra push -f secrets.yaml

# Option 2: Use environment-specific secret files
# Store template in Git, actual values elsewhere
```

**Secret rotation workflow:**
```bash
# 1. Update secret value only
echo "new-secret-value" | limacharlie hive set secret --key my-key --data - --data-key secret

# 2. Don't need to update IaC config file
# Secret reference stays the same: hive://secret/my-key
```

## CLI and Command Issues

### Issue: "Command not found or syntax error"

**Symptoms:**
- CLI command fails
- Unrecognized flags or options
- Unexpected command behavior

**Possible Causes:**
1. Outdated CLI version
2. Wrong command syntax
3. Missing required parameters

**Solutions:**

**Update CLI:**
```bash
# Check current version
limacharlie version

# Update to latest
pip install --upgrade limacharlie

# Or for specific version
pip install limacharlie==X.Y.Z
```

**Verify command syntax:**
```bash
# Get help for hive commands
limacharlie hive --help
limacharlie hive set --help
limacharlie hive get --help

# Common mistakes:
limacharlie hive set secret my-key --data file.txt     # Wrong order
limacharlie hive set secret --key my-key --data file.txt  # Correct
```

**Check required parameters:**
```bash
# Most hive commands require:
# - Hive type (secret, dr-general, etc.)
# - --key parameter
# - --data parameter for set/update

# Some hive types need --data-key:
# - secret requires --data-key secret
# - yara requires --data-key rule
```

### Issue: "Data not reading from stdin correctly"

**Symptoms:**
- Using `-` for stdin but data not accepted
- Empty or incomplete data stored
- Command hangs waiting for input

**Possible Causes:**
1. Not piping data correctly
2. Missing data-key parameter
3. Incorrect JSON/YAML format

**Solutions:**

**Verify pipe syntax:**
```bash
# Correct ways to use stdin:
echo "value" | limacharlie hive set secret --key my-key --data - --data-key secret

cat file.json | limacharlie hive set lookup --key my-lookup --data -

cat <<EOF | limacharlie hive set secret --key my-key --data - --data-key secret
secret-value-here
EOF
```

**Check data format:**
```bash
# For secrets, need proper JSON structure
cat <<EOF | limacharlie hive set secret --key my-key --data - --data-key secret
my-secret-value
EOF

# NOT:
cat <<EOF | limacharlie hive set secret --key my-key --data -
{"secret": "my-secret-value"}
EOF
# (Don't include the wrapper when using --data-key)
```

**Test with file first:**
```bash
# If stdin isn't working, try with file
echo "value" > temp.txt
limacharlie hive set secret --key my-key --data temp.txt --data-key secret
rm temp.txt

# If file works but stdin doesn't, it's a piping issue
```

## D&R Rule Issues

### Issue: "D&R rule not triggering"

**Symptoms:**
- Rule stored in hive but not firing
- Events matching criteria but no detections
- Rule appears in web UI but inactive

**Possible Causes:**
1. Rule disabled in metadata
2. Wrong event type
3. Syntax errors in detection logic
4. Lookup/ARL issues in rule

**Solutions:**

**Check if rule is enabled:**
```bash
# Get rule metadata
limacharlie hive get_mtd dr-general --key my-rule

# Look for:
# "enabled": false
# Change to:
# "enabled": true
```

**Verify rule in D&R Rules UI:**
```bash
# Rules in hive are NOT automatically active
# They need to be enabled in the D&R Rules section
# Navigate to: Automation > D&R Rules
# Ensure rule is listed and enabled
```

**Test detection logic:**
```bash
# Use the replay service to test rule against historical events
# In web UI: Automation > D&R Rules > Test/Replay

# Or create simplified rule to test basic detection
```

**Check for ARL errors:**
```bash
# If rule uses lookups or other ARLs, verify they exist:
limacharlie hive get_mtd lookup --key referenced-lookup

# Test with hardcoded values first, then add ARL
```

### Issue: "Rule syntax errors"

**Symptoms:**
- Rule won't save
- Validation errors
- YAML parsing failures

**Possible Causes:**
1. Invalid YAML syntax
2. Wrong operator usage
3. Incorrect event paths

**Solutions:**

**Validate YAML:**
```bash
# Use YAML validator
yamllint rule.yaml

# Check indentation (use spaces, not tabs)
# Ensure colons have space after them
# Quote strings with special characters
```

**Verify operator syntax:**
```yaml
# Common operators:
detect:
  event: NEW_PROCESS
  op: and  # Combining multiple conditions
  rules:
    - op: is          # Exact match
      path: event/PLATFORM
      value: windows
    - op: contains    # Substring match
      path: event/FILE_PATH
      value: powershell
    - op: matches     # Regex match
      path: event/COMMAND_LINE
      re: ".*-enc.*"
    - op: lookup      # Lookup table
      path: event/HASH
      resource: hive://lookup/threat-hashes
```

**Check event paths:**
```bash
# Event paths are case-sensitive
# Use correct event field names
# Example: event/FILE_PATH not event/file_path

# Reference LimaCharlie docs for event schemas
```

## Performance and Resource Issues

### Issue: "Large lookups causing performance problems"

**Symptoms:**
- Slow rule evaluation
- High memory usage
- Detection delays

**Possible Causes:**
1. Lookup table too large
2. Inefficient lookup structure
3. Too many lookup operations

**Solutions:**

**Optimize lookup size:**
```bash
# Keep lookups focused
# Split large lookups into multiple smaller ones
# Remove stale/unused entries regularly
```

**Use appropriate format:**
```bash
# For simple lists, use newline format (more efficient):
{
  "newline_content": "value1\nvalue2\nvalue3"
}

# For metadata-rich data, use JSON:
{
  "lookup_data": {
    "key1": {"field": "value"}
  }
}
```

**Monitor lookup updates:**
```bash
# If using Lookup Manager with frequent updates:
# - Increase sync interval if possible
# - Use incremental updates instead of full replace
# - Cache external feeds locally
```

**Limit lookup scope in rules:**
```yaml
# Add additional conditions before lookup
detect:
  event: DNS_REQUEST
  op: and
  rules:
    - op: is
      path: event/PLATFORM
      value: windows
    - op: lookup  # Only check Windows DNS requests
      path: event/DOMAIN_NAME
      resource: hive://lookup/threat-domains
```

## Debugging Tips

### Enable detailed logging

```bash
# Use verbose mode for CLI commands
limacharlie -v hive set secret --key my-key --data file.txt --data-key secret

# Check organization event logs
# Web UI: Logs > Organization Events
```

### Test in isolation

```bash
# Create test hive records to validate behavior
limacharlie hive set secret --key test-secret --data - --data-key secret <<< "test-value"

# Use in simple test configuration
# If test works, issue is with actual config
```

### Incremental changes

```bash
# When troubleshooting complex configs:
# 1. Start with minimal working config
# 2. Add one component at a time
# 3. Test after each addition
# 4. Identify exact component causing issue
```

### Use metadata-only operations

```bash
# When troubleshooting access issues, try metadata first
limacharlie hive list_mtd secret
limacharlie hive get_mtd secret --key my-key

# If metadata works but data doesn't, it's a permission issue
```

### Verify organization context

```bash
# Always confirm which org you're working with
limacharlie whoami

# Explicitly specify org if uncertain
limacharlie -o specific-org hive list secret
```

## Getting Additional Help

### Resources

1. **LimaCharlie Documentation**: Check official docs for latest information
2. **Community Slack**: Ask questions in LimaCharlie Slack workspace
3. **Support**: Contact support@limacharlie.io for assistance
4. **GitHub**: Check LimaCharlie GitHub for CLI issues

### Information to Provide When Asking for Help

When reporting issues, include:

1. **Command or operation attempted**
```bash
limacharlie hive set secret --key my-key --data file.txt --data-key secret
```

2. **Error message received** (full text)

3. **Environment information**
```bash
limacharlie version
python --version
```

4. **Organization context** (without sensitive info)
```bash
limacharlie whoami
```

5. **Relevant configuration** (redact secrets)
```yaml
# Example of what you're trying to configure
```

6. **Steps to reproduce**
- What you did
- What you expected
- What actually happened
