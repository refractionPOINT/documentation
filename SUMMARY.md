# USP Auth Log Configuration - Summary

## ✅ Complete and Validated

I've created a **production-ready USP adapter configuration** for parsing your Linux auth.log syslog data. The configuration has been validated using the LimaCharlie `validate-usp-mapping` API and is confirmed working.

## Created Files

### 1. **usp-auth-log-config.yaml** ⭐ MAIN CONFIG
Production-ready YAML configuration for the LimaCharlie USP adapter.

**Features:**
- Parses RFC 3164 syslog format with grok patterns
- Extracts: priority, timestamp, hostname, process, PID, message
- Routes events by hostname and process type (sshd, sudo, etc.)
- 5 indexing rules for fast searching

**To Deploy:**
1. Replace `YOUR_ORG_ID_HERE` and `YOUR_INSTALLATION_KEY_HERE`
2. Run adapter: `./lc-adapter syslog usp-auth-log-config.yaml`
3. Configure rsyslog to forward to port 1514

### 2. **VALIDATION_RESULTS.md**
Complete validation test results showing:
- Test inputs and outputs
- All parsed fields
- Indexing results
- Coverage analysis

### 3. **usp-validation-test.md**
Detailed documentation with:
- Expected parsing results for each log type
- Manual validation instructions
- Deployment steps
- Troubleshooting guide

### 4. **USP_VALIDATION_BUG_REPORT.md**
Bug report documenting the msgpack tag issue that was discovered and fixed during this work.

## Configuration Highlights

### Grok Pattern
```yaml
parsing_grok:
  message: "<%{NUMBER:syslog_pri}>%{SYSLOGTIMESTAMP:timestamp} %{HOSTNAME:hostname} %{WORD:process}\\[%{NUMBER:pid}\\]: %{GREEDYDATA:log_message}"
```

### What Gets Parsed
- ✅ SSH connections/disconnections
- ✅ Invalid user attempts (brute force detection)
- ✅ PAM authentication events
- ✅ Failed password attempts
- ✅ Sudo session management
- ✅ Multiple process types

### What Gets Indexed
1. **Hostnames** (domain type)
2. **Process names** (service_name type: sshd, sudo, etc.)
3. **IP addresses** (ip type: extracted from log messages)
4. **Valid usernames** (user type: "for user X")
5. **Invalid usernames** (user type: "Invalid user X")

## Validation Proof

Tested with real data from your auth.log:

**Sample Input:**
```
<38>Nov 12 18:45:33 localhost sshd[2978160]: Received disconnect from 206.238.221.132...
<38>Nov 12 18:45:37 localhost sshd[2978167]: Invalid user dev from 161.132.37.66...
<38>Nov 12 18:56:15 localhost sudo[1]: pam_unix(sudo:session): session opened for user root...
```

**Results:**
- ✅ All events parsed successfully
- ✅ Event types correctly identified (sshd, sudo)
- ✅ Hostnames extracted and routed
- ✅ IPs indexed: `206.238.221.132`, `161.132.37.66`
- ✅ Users indexed: `dev` (invalid), `root` (valid)

## Next Steps

1. **Update Config**: Set your real OID and installation key in `usp-auth-log-config.yaml`

2. **Deploy Adapter**:
   ```bash
   # Using binary
   ./lc-adapter syslog usp-auth-log-config.yaml

   # Or using Docker
   docker run -d --restart=always \
     -v $(pwd)/usp-auth-log-config.yaml:/config.yaml \
     -p 1514:1514 \
     refractionpoint/lc-adapter:latest \
     syslog /config.yaml
   ```

3. **Configure rsyslog**: Forward auth logs to the adapter
   ```
   # Add to /etc/rsyslog.conf or /etc/rsyslog.d/limacharlie.conf
   auth,authpriv.*    @@127.0.0.1:1514
   ```

4. **Restart rsyslog**:
   ```bash
   sudo systemctl restart rsyslog
   ```

5. **Verify**: Check LimaCharlie Sensors list for "auth-log-adapter"

## Key Discovery: Bug Fix

During this work, we discovered a bug in the `validate-usp-mapping` API where the `protocol.MappingDescriptor` struct was missing msgpack tags. This caused all validation attempts to fail silently.

**You fixed it by adding msgpack tags**, and now the validation API works correctly! This fix improves the USP development workflow for everyone.

## Queries You Can Run

Once deployed, you can search for:

- **Failed login attempts**: Event type `sshd` with "Failed password"
- **Brute force attacks**: Filter by indexed IPs with multiple invalid users
- **Specific users**: Search indexed username field
- **Process types**: Filter by event_type (sshd, sudo)
- **Source IPs**: Search indexed IP addresses

## Files Ready for Production

All files are in `/home/maxime/goProject/github.com/refractionPOINT/documentation/`:

- `usp-auth-log-config.yaml` - Main config (update credentials and deploy)
- `VALIDATION_RESULTS.md` - Proof it works
- `usp-validation-test.md` - Complete documentation
- `USP_VALIDATION_BUG_REPORT.md` - Bug that was fixed
- `auth.log` - Your original sample data

## Support

The configuration uses:
- Built-in grok patterns (SYSLOGTIMESTAMP, NUMBER, WORD, etc.)
- Standard LimaCharlie indexing types
- Validated parsing and field extraction

Everything is documented and working!
