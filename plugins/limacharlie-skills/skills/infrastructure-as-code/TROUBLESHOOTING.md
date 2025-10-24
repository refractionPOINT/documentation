# Infrastructure as Code - Troubleshooting Guide

This document provides solutions to common issues when working with LimaCharlie Infrastructure as Code.

## Table of Contents

- [Git Sync Issues](#git-sync-issues)
- [Deployment Problems](#deployment-problems)
- [Validation Errors](#validation-errors)
- [Configuration Issues](#configuration-issues)
- [Performance Problems](#performance-problems)
- [Authentication and Permissions](#authentication-and-permissions)

## Git Sync Issues

### SSH Connection Failed

**Symptoms**:
- Git Sync extension shows "Connection failed" error
- Unable to push or pull from repository
- SSH authentication errors in extension sensor logs

**Solutions**:

1. **Verify SSH URL Format**:
   ```
   Correct:   git@github.com:username/repo.git
   Incorrect: https://github.com/username/repo.git
   Incorrect: git@github.com/username/repo.git
   ```

2. **Check Deploy Key Configuration**:
   - Navigate to GitHub repository > Settings > Deploy keys
   - Verify the deploy key exists and matches your public key
   - Ensure "Allow write access" is checked (required for exports)
   - Verify the key hasn't expired or been revoked

3. **Verify Private Key in Secret Manager**:
   ```bash
   # Your private key should look like this:
   -----BEGIN OPENSSH PRIVATE KEY-----
   b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
   ...
   -----END OPENSSH PRIVATE KEY-----
   ```
   - Ensure the entire key (including BEGIN/END lines) is stored in Secret Manager
   - No extra spaces or line breaks
   - The key should match the public key added to GitHub

4. **Test SSH Connection Manually**:
   ```bash
   # Test connection to GitHub
   ssh -T git@github.com -i ~/.ssh/gitsync/id_ed25519

   # Expected output:
   # Hi username! You've successfully authenticated, but GitHub does not provide shell access.
   ```

5. **Check Git Sync Extension Configuration**:
   - User Name: Should be `git` (not your GitHub username)
   - SSH Key Source: Secret Manager
   - Select Secret: The secret containing your private key
   - Repository URL: Must use SSH format
   - Branch: Verify the branch exists in your repository

### Repository Not Found

**Symptoms**:
- Error: "Repository not found" or "fatal: Could not read from remote repository"
- Git Sync fails to connect despite correct SSH setup

**Solutions**:

1. **Verify Repository URL**:
   - Check for typos in username/organization name
   - Ensure repository name is correct (case-sensitive)
   - Verify repository exists and is accessible

2. **Check Repository Permissions**:
   - Deploy key must be added to the specific repository
   - For organization repos, verify you have appropriate access
   - Ensure repository is not archived or deleted

3. **Verify Branch Exists**:
   ```bash
   # List all branches in repository
   git ls-remote --heads git@github.com:username/repo.git

   # If branch doesn't exist, create it:
   git checkout -b main
   git push origin main
   ```

### No Changes Syncing

**Symptoms**:
- Git Sync completes without errors but no changes appear
- Configurations not updating despite commits to Git
- Export creates empty files or no files

**Solutions**:

1. **Verify Repository Structure**:
   ```
   Required structure:
   .
   └── orgs/
       └── [YOUR_ORGANIZATION_ID]/
           └── index.yaml
   ```
   - The organization ID must match exactly (use lowercase, include hyphens)
   - `index.yaml` must exist in the org directory

2. **Check index.yaml Content**:
   ```yaml
   version: 3
   include:
     - extensions.yaml
     - outputs.yaml
     # ... other files
   ```
   - Verify `version: 3` is present
   - Check that included files exist relative to index.yaml
   - Ensure file paths are correct (case-sensitive)

3. **Verify Sync Options**:
   - In Git Sync extension settings, check which components are selected
   - Pull from Git: Select components to sync TO LimaCharlie
   - Push to Git: Select components to export FROM LimaCharlie
   - If no components are selected, nothing will sync

4. **Check Git Sync Extension Sensor Logs**:
   - Navigate to Sensors > Find Git Sync sensor
   - Review recent events for error messages
   - Look for parsing errors or file not found errors

5. **Verify File Permissions**:
   - Ensure YAML files are valid and readable
   - Check for special characters or encoding issues
   - Use UTF-8 encoding for all YAML files

### Partial Sync

**Symptoms**:
- Some configurations sync but not others
- Only certain file types are syncing
- Inconsistent sync results

**Solutions**:

1. **Review Sync Component Selection**:
   - Check Git Sync extension settings
   - Ensure all desired components are checked:
     - D&R rules
     - False Positive rules
     - Outputs
     - Resources
     - Extensions
     - Artifacts
     - etc.

2. **Check for Locked or Segmented Resources**:
   - Some resources may be locked by organization policies
   - Use `ignore_inaccessible` flag:
     ```bash
     limacharlie configs push --config config.yaml --ignore-inaccessible --all
     ```
   - Or in Git Sync extension settings, enable "Ignore Inaccessible Resources"

3. **Verify File Paths in index.yaml**:
   ```yaml
   version: 3
   include:
     - rules/detection-rules.yaml  # Relative to index.yaml location
     - outputs.yaml                # In same directory as index.yaml
     - ../shared/common.yaml       # One level up, then shared directory
   ```

4. **Check for YAML Parsing Errors**:
   - Validate each YAML file:
     ```bash
     yamllint file.yaml
     # or
     python3 -c "import yaml; yaml.safe_load(open('file.yaml'))"
     ```

### Export Directory Issues

**Symptoms**:
- Exports overwrite working configurations
- Cannot find exported files
- Export conflicts with existing files

**Solutions**:

1. **Use Separate Export Directory**:
   - Git Sync exports to `exports/orgs/[oid]/` by default
   - Working configs should be in `orgs/[oid]/`
   - Keep these separate to avoid conflicts

2. **Configure Export Path**:
   ```
   Repository structure:
   .
   ├── orgs/
   │   └── [oid]/
   │       └── index.yaml          # Working configs (pulled from)
   └── exports/
       └── orgs/
           └── [oid]/
               └── index.yaml      # Exported configs (pushed to)
   ```

3. **Review Exported Files**:
   - After export, review files in `exports/` directory
   - Compare with working configs in `orgs/` directory
   - Merge changes as needed

## Deployment Problems

### Dry Run Shows Unexpected Changes

**Symptoms**:
- Dry run output shows configurations being deleted
- Unexpected modifications to existing rules
- Resources showing as changed when they shouldn't be

**Solutions**:

1. **Understand Additive vs Force Mode**:
   - **Additive** (default): Only adds/updates, never deletes
   - **Force**: Makes org exactly match config (DELETES unspecified items)
   - Use `--force` only when you intend to remove items

2. **Check Current Configuration**:
   ```bash
   # Export current org config to see what exists
   limacharlie configs fetch --oid YOUR_OID > current.yaml

   # Compare with your config file
   diff current.yaml your-config.yaml
   ```

3. **Review Dry Run Output Carefully**:
   ```bash
   limacharlie configs push --config config.yaml --dry-run --all | tee dry-run.log

   # Look for:
   # - [+] Adding new items
   # - [~] Modifying existing items
   # - [-] Deleting items (only in force mode)
   ```

4. **Use Selective Sync**:
   ```bash
   # Only sync specific components
   limacharlie configs push --config config.yaml --sync-dr --dry-run
   ```

### Configuration Not Applying

**Symptoms**:
- Push command succeeds but changes don't appear in organization
- Rules not showing up in web UI
- Outputs not configured despite successful push

**Solutions**:

1. **Verify Sync Flags**:
   ```bash
   # Use --all to sync everything
   limacharlie configs push --config config.yaml --all

   # Or specify components explicitly
   limacharlie configs push --config config.yaml --sync-dr --sync-outputs
   ```

2. **Check for Validation Errors**:
   - Review command output for error messages
   - Look for YAML parsing errors
   - Check for invalid field values

3. **Verify Organization ID**:
   ```bash
   # Ensure you're deploying to correct org
   limacharlie configs push --oid CORRECT_OID --config config.yaml --all
   ```

4. **Check API Key Permissions**:
   - Ensure API key has required permissions:
     - `dr.set` for D&R rules
     - `org.conf.set` for outputs
     - `org.installation_keys.set` for installation keys

5. **Review Locked Resources**:
   - Some resources may be locked by organization policies
   - Use `--ignore-inaccessible` flag:
     ```bash
     limacharlie configs push --config config.yaml --all --ignore-inaccessible
     ```

### Deployment Fails Midway

**Symptoms**:
- Push command fails partway through
- Some configurations applied, others not
- Error messages during deployment

**Solutions**:

1. **Check Error Message**:
   - Read the error message carefully
   - Note which component failed (rules, outputs, etc.)
   - Look for validation errors or permission issues

2. **Fix Issues Incrementally**:
   ```bash
   # Test components individually
   limacharlie configs push --config config.yaml --sync-dr --dry-run
   limacharlie configs push --config config.yaml --sync-outputs --dry-run
   ```

3. **Validate Configuration Files**:
   ```bash
   # Check YAML syntax
   yamllint config.yaml

   # Validate against schema
   limacharlie configs push --config config.yaml --dry-run --all
   ```

4. **Review Organization Limits**:
   - Check if you've hit organization limits (e.g., max rules)
   - Verify subscription includes required features
   - Ensure extensions are subscribed

5. **Retry with Smaller Changes**:
   - Break configuration into smaller files
   - Deploy incrementally
   - Use includes to manage complexity

## Validation Errors

### YAML Syntax Errors

**Symptoms**:
- "YAML parsing error" messages
- "Invalid YAML" errors
- Unexpected indentation errors

**Solutions**:

1. **Validate YAML Syntax**:
   ```bash
   # Use yamllint
   yamllint config.yaml

   # Use Python
   python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

   # Use yq
   yq eval '.' config.yaml
   ```

2. **Common YAML Mistakes**:
   ```yaml
   # Wrong: Mixed tabs and spaces
   rules:
   	- name: test    # Tab character
     detect:         # Spaces

   # Correct: Use spaces only
   rules:
     - name: test
       detect:

   # Wrong: Incorrect indentation
   rules:
   - name: test
     detect:
      event: NEW_PROCESS  # Inconsistent indentation

   # Correct: Consistent 2-space indentation
   rules:
     - name: test
       detect:
         event: NEW_PROCESS

   # Wrong: Missing quotes for special characters
   value: C:\Windows\System32

   # Correct: Quote paths with backslashes
   value: "C:\\Windows\\System32"
   # Or use forward slashes
   value: C:/Windows/System32
   ```

3. **Check for Hidden Characters**:
   ```bash
   # Display non-printing characters
   cat -A config.yaml | head -20

   # Look for:
   # - Tab characters (shown as ^I)
   # - Windows line endings (shown as ^M$)
   # - UTF-8 BOM (shown as special characters at start)
   ```

4. **Use Proper Text Editor**:
   - Use editors with YAML support (VSCode, Sublime, vim with YAML plugin)
   - Enable "show whitespace" feature
   - Configure editor to use spaces instead of tabs
   - Set indent width to 2 spaces

### Schema Validation Errors

**Symptoms**:
- "Invalid field" errors
- "Unknown property" errors
- "Required field missing" errors

**Solutions**:

1. **Check Required Fields**:
   ```yaml
   # Every config must have version
   version: 3

   # Rules must have name, detect, and respond
   rules:
     - name: rule-name       # Required
       detect:               # Required
         event: EVENT_TYPE
         op: OPERATOR
         path: event/FIELD
         value: VALUE
       respond:              # Required
         - action: report
           name: Detection Name

   # Outputs must have name, module, and for
   outputs:
     - name: output-name    # Required
       module: slack        # Required
       for: detection       # Required
       # module-specific fields
   ```

2. **Verify Field Names**:
   ```yaml
   # Wrong: Incorrect field names
   rules:
     - rule_name: test           # Should be 'name'
       detection:                # Should be 'detect'
         event_type: NEW_PROCESS # Should be 'event'

   # Correct:
   rules:
     - name: test
       detect:
         event: NEW_PROCESS
   ```

3. **Check Field Values**:
   ```yaml
   # Wrong: Invalid event type
   detect:
     event: INVALID_EVENT

   # Correct: Valid event type
   detect:
     event: NEW_PROCESS

   # Wrong: Invalid operator
   detect:
     op: INVALID_OP

   # Correct: Valid operator
   detect:
     op: contains
   ```

4. **Reference Documentation**:
   - See [REFERENCE.md](./REFERENCE.md) for complete field reference
   - Check LimaCharlie docs for event types
   - Verify operator names and syntax

### Include File Not Found

**Symptoms**:
- "File not found" errors
- "Cannot resolve include path" errors
- Include files not loading

**Solutions**:

1. **Verify File Paths**:
   ```yaml
   # Paths are relative to the file containing the include

   # If index.yaml is at: /orgs/customer-a/index.yaml
   # And you want to include: /orgs/customer-a/outputs.yaml
   include:
     - outputs.yaml           # Correct

   # If you want to include: /global/rules.yaml
   include:
     - ../../global/rules.yaml  # Correct
   ```

2. **Check File Existence**:
   ```bash
   # Verify file exists
   ls -la orgs/customer-a/outputs.yaml

   # Check relative path
   cd orgs/customer-a
   ls -la ../../global/rules.yaml
   ```

3. **Use Correct Path Separators**:
   ```yaml
   # Wrong: Backslashes (Windows style)
   include:
     - rules\detection-rules.yaml

   # Correct: Forward slashes (Unix style)
   include:
     - rules/detection-rules.yaml
   ```

4. **Test Path Resolution**:
   ```bash
   # Create test structure
   mkdir -p test/orgs/customer-a
   mkdir -p test/global
   echo "version: 3" > test/global/rules.yaml
   echo "version: 3" > test/orgs/customer-a/index.yaml
   echo "include:" >> test/orgs/customer-a/index.yaml
   echo "  - ../../global/rules.yaml" >> test/orgs/customer-a/index.yaml

   # Test
   cd test/orgs/customer-a
   limacharlie configs push --config index.yaml --dry-run
   ```

## Configuration Issues

### Rules Not Matching Expected Events

**Symptoms**:
- Detection rules not triggering
- Rules matching wrong events
- Unexpected detections

**Solutions**:

1. **Test Rules with Replay**:
   ```bash
   # Create test event
   cat > test-event.json <<EOF
   [
     {
       "event": {
         "FILE_PATH": "C:\\Windows\\System32\\calc.exe",
         "COMMAND_LINE": "calc.exe",
         "PROCESS_ID": 1234
       },
       "routing": {
         "event_type": "NEW_PROCESS"
       }
     }
   ]
   EOF

   # Extract rule
   yq eval '.rules[0]' config.yaml > rule.yaml

   # Test rule against event
   limacharlie replay --rule-content rule.yaml --events test-event.json
   ```

2. **Check Event Field Paths**:
   ```yaml
   # Wrong: Incorrect path
   detect:
     event: NEW_PROCESS
     path: COMMAND_LINE         # Missing event/ prefix

   # Correct: Full path
   detect:
     event: NEW_PROCESS
     path: event/COMMAND_LINE   # Correct path
   ```

3. **Verify Operators**:
   ```yaml
   # Case-sensitive by default
   detect:
     op: contains
     path: event/COMMAND_LINE
     value: PowerShell          # Won't match "powershell"

   # Use case insensitive
   detect:
     op: contains
     path: event/COMMAND_LINE
     value: powershell
     case sensitive: false      # Matches any case
   ```

4. **Test Against Historical Data**:
   ```bash
   # Test rule against last hour of data
   limacharlie replay --rule-content rule.yaml --entire-org --last-seconds 3600
   ```

5. **Use Unit Tests**:
   ```yaml
   rules:
     - name: test-rule
       detect:
         event: NEW_PROCESS
         op: contains
         path: event/COMMAND_LINE
         value: calc.exe
       respond:
         - action: report
           name: Calculator Launched
       tests:
         match:
           - - event:
                 COMMAND_LINE: calc.exe /c
               routing:
                 event_type: NEW_PROCESS
         non_match:
           - - event:
                 COMMAND_LINE: notepad.exe
               routing:
                 event_type: NEW_PROCESS
   ```

### Hive References Not Resolving

**Symptoms**:
- `hive://secret/name` not resolving
- "Secret not found" errors
- Empty values for hive references

**Solutions**:

1. **Verify Secret Exists**:
   - Navigate to Organization Settings > Secret Manager
   - Ensure secret with exact name exists
   - Check for typos or case sensitivity

2. **Use Correct Hive Syntax**:
   ```yaml
   # Correct: hive://secret/secret-name
   slack_api_token: hive://secret/slack-token

   # Wrong: Missing hive:// prefix
   slack_api_token: secret/slack-token

   # Wrong: Incorrect hive type
   slack_api_token: hive://lookup/slack-token
   ```

3. **Create Missing Secrets**:
   ```yaml
   # In your config, define secrets
   hive:
     secret:
       - name: slack-token
         enabled: true
         data: "xoxb-your-token-here"
   ```

4. **Reference Before Definition**:
   ```yaml
   # This works - secrets created before outputs
   hive:
     secret:
       - name: slack-token
         enabled: true
         data: "xoxb-token"

   outputs:
     - name: slack
       module: slack
       slack_api_token: hive://secret/slack-token
   ```

### Output Not Sending Data

**Symptoms**:
- Output configured but not receiving data
- No errors but data not appearing in destination
- Intermittent output failures

**Solutions**:

1. **Check Output Configuration**:
   ```yaml
   outputs:
     - name: slack-alerts
       module: slack
       for: detection        # Must match data type
       slack_api_token: hive://secret/slack-token
       slack_channel: "#security-alerts"
   ```

2. **Verify Output Filters**:
   ```yaml
   # If filters are too restrictive, nothing will send
   outputs:
     - name: filtered-output
       module: slack
       for: detection
       filters:
         min_priority: 5     # Only priority 5 detections
         tags:
           - production      # Only sensors with this tag
         platforms:
           - windows         # Only Windows sensors
   ```

3. **Test Output Manually**:
   - Navigate to Outputs in web UI
   - Click "Test" button on output
   - Verify test message is received

4. **Check Destination**:
   - Verify Slack channel exists and bot is invited
   - Test SIEM connectivity (telnet/nc to syslog port)
   - Check S3 bucket permissions
   - Verify webhook endpoint is accessible

5. **Review Output Logs**:
   - Check output status in web UI
   - Look for error messages
   - Verify authentication tokens are valid

## Performance Problems

### Slow Configuration Deployment

**Symptoms**:
- Push commands take a long time
- Timeouts during deployment
- Large configuration files

**Solutions**:

1. **Break Into Smaller Files**:
   ```yaml
   # Instead of one large file with 1000 rules
   # Use includes:
   version: 3
   include:
     - rules/malware-100-rules.yaml
     - rules/lateral-movement-50-rules.yaml
     - rules/exfil-75-rules.yaml
   ```

2. **Use Selective Sync**:
   ```bash
   # Only sync changed components
   limacharlie configs push --config config.yaml --sync-dr

   # Instead of
   limacharlie configs push --config config.yaml --all
   ```

3. **Optimize Large Rule Sets**:
   - Remove duplicate rules
   - Consolidate similar rules using OR logic
   - Disable unused rules instead of deleting

4. **Deploy Incrementally**:
   ```bash
   # Deploy rules in batches
   limacharlie configs push --config rules-batch-1.yaml --sync-dr
   limacharlie configs push --config rules-batch-2.yaml --sync-dr
   ```

### Git Sync Taking Too Long

**Symptoms**:
- Git Sync operations timeout
- Large repository causing sync delays
- Frequent sync conflicts

**Solutions**:

1. **Optimize Repository Size**:
   - Remove large binary files
   - Clean up old export directories
   - Use `.gitignore` for temporary files

2. **Adjust Sync Frequency**:
   ```yaml
   # Instead of every minute
   detect:
     target: schedule
     event: SCHEDULE_EVERY_1_MIN

   # Use less frequent schedule
   detect:
     target: schedule
     event: SCHEDULE_EVERY_15_MIN
   ```

3. **Use Shallow Clones**:
   - Git Sync uses shallow clones by default
   - Reduces repository size
   - Faster sync operations

4. **Separate Large Configurations**:
   - Use multiple repositories for different org groups
   - Split customer configs into separate repos
   - Keep global configs in dedicated repository

## Authentication and Permissions

### API Key Permission Denied

**Symptoms**:
- "Permission denied" errors
- "Insufficient permissions" messages
- Unable to modify configurations

**Solutions**:

1. **Check API Key Permissions**:
   ```yaml
   # Required permissions for IaC operations
   resources:
     api_keys:
       - name: iac-automation
         permissions:
           - dr.list          # List D&R rules
           - dr.set           # Modify D&R rules
           - org.conf.list    # List org config
           - org.conf.set     # Modify org config
           - org.installation_keys.list
           - org.installation_keys.set
   ```

2. **Use Correct API Key**:
   ```bash
   # Set API key in environment
   export LIMACHARLIE_API_KEY="your-api-key"

   # Or specify in command
   limacharlie --api-key YOUR_KEY configs push --config config.yaml
   ```

3. **Verify Organization Access**:
   - Ensure API key belongs to correct organization
   - Check that you have access to the target organization
   - Verify organization is not suspended or restricted

4. **Request Additional Permissions**:
   - Navigate to Resources > API Keys
   - Edit API key
   - Add required permissions
   - Or create new API key with full permissions

### Cannot Access Locked Resources

**Symptoms**:
- "Resource is locked" errors
- "Cannot modify segmented resource" messages
- Some configurations not syncing

**Solutions**:

1. **Use Ignore Inaccessible Flag**:
   ```bash
   # Skip locked resources
   limacharlie configs push --config config.yaml --all --ignore-inaccessible
   ```

2. **Identify Locked Resources**:
   ```bash
   # Dry run will show locked resources
   limacharlie configs push --config config.yaml --dry-run --all | grep -i "locked\|inaccessible"
   ```

3. **Contact Organization Administrator**:
   - Locked resources are set by org policies
   - Request unlock from org admin
   - Or work around locked resources

4. **Segment Resources Properly**:
   - Use organization segments for isolation
   - Apply policies appropriately
   - Document which resources are locked and why
