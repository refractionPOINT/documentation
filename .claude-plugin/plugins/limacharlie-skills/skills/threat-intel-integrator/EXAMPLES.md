# Threat Intelligence Workflow Examples

Complete detection workflows demonstrating threat intelligence integration in LimaCharlie.

## Example 1: Multi-Stage Malware Detection

Detect and respond to multi-stage malware using multiple threat intelligence sources.

### Scenario

1. Attacker visits malicious domain to download payload
2. Payload executes on system
3. Detection correlates domain reputation with file reputation
4. System isolates and terminates malicious process

### Detection Rules

#### Stage 1: Initial Payload Download

```yaml
detect:
  event: DNS_REQUEST
  op: and
  rules:
    # Check Pangea domain reputation
    - op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/pangea-domain-reputation
      metadata_rules:
        op: is
        value: "malicious"
        path: /verdict
    # Validate with AlphaMountain threat score
    - op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/alphamountain-threat
      metadata_rules:
        op: is greater than
        value: 70
        path: /score

respond:
  - action: report
    name: high-confidence-malware-domain
    metadata:
      domain: '{{ .event.DOMAIN_NAME }}'
      pangea_verdict: '{{ .lookup.verdict }}'
      pangea_score: '{{ .lookup.score }}'
      alpha_score: '{{ .lookup.score }}'
      sensor: '{{ .routing.hostname }}'
    suppression:
      max_count: 1
      period: 1h
      is_global: false
      keys:
        - '{{ .event.DOMAIN_NAME }}'
  # Tag sensor for correlation
  - action: add tag
    tag: malware-download-attempt
    ttl: 86400  # 24 hours
```

#### Stage 2: Malicious File Execution

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    # Sensor has recent malware download tag
    - op: is tagged
      tag: malware-download-attempt
    # Check VirusTotal for file reputation
    - op: lookup
      path: event/HASH
      resource: hive://lookup/vt
      metadata_rules:
        op: is greater than
        value: 5
        path: /positives
    # File is unsigned
    - op: is
      value: 0
      path: event/SIGNATURE/FILE_IS_SIGNED
    # Not in known-good list
    - op: not
      op: lookup
      path: event/HASH
      resource: hive://lookup/corporate-approved-software

respond:
  - action: report
    name: malware-execution-confirmed
    metadata:
      hash: '{{ .event.HASH }}'
      file_path: '{{ .event.FILE_PATH }}'
      command_line: '{{ .event.COMMAND_LINE }}'
      vt_positives: '{{ .lookup.positives }}'
      vt_total: '{{ .lookup.total }}'
      vt_permalink: '{{ .lookup.permalink }}'
      sensor: '{{ .routing.hostname }}'
  # Isolate network immediately
  - action: isolate_network
  # Terminate process tree
  - action: task
    command: deny_tree <<PARENT>>
  # Capture memory for forensics
  - action: task
    command: mem_dump
  # Persistent tagging
  - action: add tag
    tag: confirmed-malware-infection
    ttl: 604800  # 7 days
```

#### Stage 3: Incident Enrichment

```yaml
detect:
  event: NEW_PROCESS
  op: is tagged
  tag: confirmed-malware-infection

respond:
  # Enrich with BinLib data
  - action: extension request
    extension: binlib
    extension_action: get_hash_metadata
    extension_data:
      hash: '{{ .event.HASH }}'
  - action: report
    name: malware-infection-enrichment
    suppression:
      max_count: 10
      period: 1h
```

### Expected Outcome

1. First DNS query to malicious domain triggers alert and tags sensor
2. When malicious file executes, second rule matches due to tag + VT reputation
3. System immediately isolates network and terminates process
4. Memory dump captured for forensic analysis
5. Enrichment rule provides additional binary metadata
6. 7-day persistent tag enables correlation with other suspicious activity

### Suppression Strategy

- Stage 1: Suppress duplicate domain alerts per sensor (1 hour)
- Stage 2: No suppression - each execution is critical
- Stage 3: Limit enrichment noise (10 per hour)

## Example 2: APT-Style Lateral Movement Detection

Detect lateral movement using multiple intelligence sources and behavioral indicators.

### Scenario

1. Attacker uses PsExec-like tool to move laterally
2. Connection originates from high-risk country
3. Targets internal infrastructure
4. Detection correlates geolocation, tool signature, and destination

### Detection Rule

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: scope
  path: event/NETWORK_ACTIVITY/
  rule:
    op: and
    rules:
      # SMB connection (port 445)
      - op: is
        value: 445
        path: event/DESTINATION/PORT
      # PsExec-like tool in process path
      - op: or
        rules:
          - op: contains
            path: event/FILE_PATH
            value: "psexec"
          - op: contains
            path: event/FILE_PATH
            value: "paexec"
          - op: contains
            path: event/FILE_PATH
            value: "remcom"
      # Source IP from high-risk country
      - op: lookup
        path: event/SOURCE/IP_ADDRESS
        resource: hive://lookup/ip-geo
        metadata_rules:
          op: or
          rules:
            - op: is
              value: "RU"
              path: /country/iso_code
            - op: is
              value: "CN"
              path: /country/iso_code
            - op: is
              value: "KP"
              path: /country/iso_code
            - op: is
              value: "IR"
              path: /country/iso_code
      # Destination is internal infrastructure
      - op: lookup
        path: event/DESTINATION/IP_ADDRESS
        resource: hive://lookup/corporate-infrastructure
      # Filter out benign scanning tools
      - op: not
        op: lookup
        path: event/SOURCE/IP_ADDRESS
        resource: hive://lookup/greynoise-riot

respond:
  - action: report
    name: suspected-apt-lateral-movement
    metadata:
      source_ip: '{{ index .event.NETWORK_ACTIVITY 0 "SOURCE" "IP_ADDRESS" }}'
      dest_ip: '{{ index .event.NETWORK_ACTIVITY 0 "DESTINATION" "IP_ADDRESS" }}'
      dest_port: '{{ index .event.NETWORK_ACTIVITY 0 "DESTINATION" "PORT" }}'
      country: '{{ .lookup.country.iso_code }}'
      country_name: '{{ .lookup.country.names.en }}'
      tool_path: '{{ .event.FILE_PATH }}'
      process_name: '{{ .event.PROCESS_NAME }}'
      user: '{{ .event.USER_NAME }}'
      sensor: '{{ .routing.hostname }}'
      mitre_technique: "T1021.002"
      mitre_tactic: "Lateral Movement"
    suppression:
      max_count: 1
      period: 10m
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ index .event.NETWORK_ACTIVITY 0 "DESTINATION" "IP_ADDRESS" }}'
  # Tag sensor for tracking
  - action: add tag
    tag: apt-activity
    ttl: 604800  # 7 days
  # Isolate network to prevent further lateral movement
  - action: isolate_network
```

### Supporting Infrastructure

#### Corporate Infrastructure Lookup

```yaml
hives:
  lookup:
    corporate-infrastructure:
      data:
        lookup_data:
          192.168.10.5:
            hostname: "dc01.corp.local"
            role: "domain_controller"
            criticality: "high"
          192.168.10.10:
            hostname: "file01.corp.local"
            role: "file_server"
            criticality: "medium"
          192.168.20.5:
            hostname: "db01.corp.local"
            role: "database_server"
            criticality: "high"
```

### Expected Outcome

1. Lateral movement attempt detected in real-time
2. Geolocation identifies high-risk source country
3. Tool signature matches known lateral movement utilities
4. Network isolation prevents further spread
5. 7-day tag enables correlation with other suspicious activity
6. MITRE ATT&CK mapping enables framework-based analysis

## Example 3: Phishing Detection with URL Analysis

Comprehensive phishing detection using multiple threat intelligence APIs.

### Scenario

1. User receives phishing email with link
2. User clicks link, browser makes HTTP request
3. Detection analyzes domain popularity, reputation, and typosquatting
4. System blocks access and alerts security team

### Detection Rule

```yaml
detect:
  event: HTTP_REQUEST
  op: and
  rules:
    # Low domain popularity (potential DGA or new phishing site)
    - op: lookup
      path: event/URL_DOMAIN
      resource: hive://lookup/alphamountain-popularity
      metadata_rules:
        op: is greater than
        value: 100000
        path: /rank  # Higher rank = less popular
    # Suspicious or malicious reputation
    - op: lookup
      path: event/URL_DOMAIN
      resource: hive://lookup/pangea-domain-reputation
      metadata_rules:
        op: or
        rules:
          - op: is
            value: "suspicious"
            path: /verdict
          - op: is
            value: "malicious"
            path: /verdict
    # Possible typosquatting (similar to known brands)
    - op: string distance
      path: event/URL_DOMAIN
      value:
        - microsoft.com
        - office365.com
        - google.com
        - dropbox.com
        - amazon.com
        - paypal.com
        - apple.com
        - facebook.com
      max: 2  # Maximum edit distance
    # Not in corporate allowed domains
    - op: not
      op: lookup
      path: event/URL_DOMAIN
      resource: hive://lookup/corporate-allowed-domains
    # Filter out CDNs and known benign services
    - op: not
      op: lookup
        path: event/URL_DOMAIN
        resource: hive://lookup/known-cdn-domains

respond:
  - action: report
    name: potential-phishing-site
    metadata:
      url: '{{ .event.URL }}'
      domain: '{{ .event.URL_DOMAIN }}'
      popularity_rank: '{{ .lookup.rank }}'
      reputation: '{{ .lookup.verdict }}'
      reputation_score: '{{ .lookup.score }}'
      user: '{{ .event.USER_NAME }}'
      process: '{{ .event.PROCESS_NAME }}'
      sensor: '{{ .routing.hostname }}'
      mitre_technique: "T1566.002"
    suppression:
      max_count: 1
      period: 24h
      is_global: true
      keys:
        - '{{ .event.URL_DOMAIN }}'
  # Terminate browser process
  - action: task
    command: deny_tree <<PARENT>>
  # Tag user for phishing awareness training
  - action: add tag
    tag: phishing-victim
    ttl: 2592000  # 30 days
```

### Enhanced Detection with Category Analysis

```yaml
detect:
  event: HTTP_REQUEST
  op: and
  rules:
    # Base phishing detection (from above)
    - op: lookup
      path: event/URL_DOMAIN
      resource: hive://lookup/pangea-domain-reputation
      metadata_rules:
        op: or
        rules:
          - op: is
            value: "suspicious"
            path: /verdict
          - op: is
            value: "malicious"
            path: /verdict
    # AlphaMountain category confirms phishing
    - op: lookup
      path: event/URL_DOMAIN
      resource: hive://lookup/alphamountain-category
      metadata_rules:
        op: contains
        value: 12  # Phishing category ID
        path: /categories
    # High confidence score
    - op: lookup
      path: event/URL_DOMAIN
      resource: hive://lookup/alphamountain-category
      metadata_rules:
        op: is greater than
        value: 0.8
        path: /confidence

respond:
  - action: report
    name: confirmed-phishing-site
    metadata:
      url: '{{ .event.URL }}'
      domain: '{{ .event.URL_DOMAIN }}'
      user: '{{ .event.USER_NAME }}'
      alpha_confidence: '{{ .lookup.confidence }}'
  - action: task
    command: deny_tree <<PARENT>>
  - action: isolate_network
```

### Supporting Infrastructure

#### Corporate Allowed Domains

```yaml
hives:
  lookup:
    corporate-allowed-domains:
      data:
        newline_content: "corp.company.com\nmail.company.com\nintranet.company.com\nsharepoint.company.com"
```

#### Known CDN Domains

```yaml
hives:
  lookup:
    known-cdn-domains:
      data:
        lookup_data:
          cloudflare.com: {category: "cdn"}
          akamai.net: {category: "cdn"}
          amazonaws.com: {category: "cloud"}
          azureedge.net: {category: "cdn"}
```

### Expected Outcome

1. HTTP request to suspicious domain detected
2. Multiple intelligence sources confirm phishing threat
3. Browser process terminated before credentials entered
4. User tagged for security awareness training
5. Global suppression prevents duplicate alerts
6. Security team receives enriched alert with reputation data

## Example 4: Data Exfiltration Detection via DNS Tunneling

Detect data exfiltration using DNS tunneling with threat intelligence.

### Scenario

1. Malware exfiltrates data via DNS queries
2. Queries contain hex-encoded data in subdomain
3. Uses unpopular dynamic DNS provider
4. Detection correlates query pattern, domain popularity, and DNS provider

### Detection Rule

```yaml
detect:
  event: DNS_REQUEST
  op: and
  rules:
    # Hex-encoded data pattern in domain (32+ hex characters)
    - op: matches
      path: event/DOMAIN_NAME
      re: '^[a-f0-9]{32,}\.'
    # Domain uses dynamic DNS provider
    - op: lookup
      path: event/DOMAIN_NAME
      sub domain: "-1"  # TLD only
      resource: hive://lookup/dynamic-dns-providers
    # Very unpopular domain (possible tunneling endpoint)
    - op: lookup
      path: event/DOMAIN_NAME
      sub domain: "-2:"  # Last two components (domain + TLD)
      resource: hive://lookup/alphamountain-popularity
      metadata_rules:
        op: is greater than
        value: 500000
        path: /rank
    # Not in corporate approved domains
    - op: not
      op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/corporate-domains
    # Not GreyNoise benign service
    - op: not
      op: lookup
      path: event/DNS_SERVER
      resource: hive://lookup/greynoise-riot
    # High query frequency (multiple queries in short time)
    - op: is greater than
      path: event/QUERY_COUNT
      value: 10

respond:
  - action: report
    name: potential-dns-tunneling
    metadata:
      domain: '{{ .event.DOMAIN_NAME }}'
      query_type: '{{ .event.DNS_TYPE }}'
      dns_server: '{{ .event.DNS_SERVER }}'
      popularity_rank: '{{ .lookup.rank }}'
      query_count: '{{ .event.QUERY_COUNT }}'
      process: '{{ .event.PROCESS_NAME }}'
      user: '{{ .event.USER_NAME }}'
      sensor: '{{ .routing.hostname }}'
      mitre_technique: "T1048.003"
      mitre_tactic: "Exfiltration"
    suppression:
      max_count: 1
      period: 1h
      is_global: false
      keys:
        - '{{ .routing.sid }}'
        - '{{ .event.DOMAIN_NAME }}'
  # Isolate network immediately
  - action: isolate_network
  # Tag for investigation
  - action: add tag
    tag: data-exfiltration-suspected
    ttl: 86400  # 24 hours
  # Capture network traffic
  - action: task
    command: capture_network
```

### Enhanced Detection with Query Volume

```yaml
detect:
  event: DNS_REQUEST
  op: and
  rules:
    # Base DNS tunneling indicators
    - op: matches
      path: event/DOMAIN_NAME
      re: '^[a-f0-9]{32,}\.'
    - op: lookup
      path: event/DOMAIN_NAME
      sub domain: "-1"
      resource: hive://lookup/dynamic-dns-providers
    # Anomalous query volume from single process
    - op: is greater than
      path: event/QUERY_COUNT
      value: 50
      window: 300  # 5 minutes

respond:
  - action: report
    name: high-volume-dns-tunneling
  - action: isolate_network
  - action: task
    command: deny_tree <<PARENT>>
```

### Supporting Infrastructure

#### Dynamic DNS Providers Lookup

```yaml
hives:
  lookup:
    dynamic-dns-providers:
      data:
        lookup_data:
          duckdns.org: {category: "dynamic_dns", risk: "medium"}
          no-ip.com: {category: "dynamic_dns", risk: "medium"}
          ddns.net: {category: "dynamic_dns", risk: "medium"}
          afraid.org: {category: "dynamic_dns", risk: "medium"}
          dyndns.org: {category: "dynamic_dns", risk: "medium"}
```

#### Corporate Domains Lookup

```yaml
hives:
  lookup:
    corporate-domains:
      data:
        lookup_data:
          company.com: {}
          corp.company.com: {}
          mail.company.com: {}
```

### Expected Outcome

1. DNS tunneling detected through pattern analysis
2. Domain confirmed as unpopular via AlphaMountain
3. Dynamic DNS provider identified as common tunneling infrastructure
4. Network isolated to stop exfiltration
5. Network capture initiated for forensic analysis
6. Tag enables correlation with other exfiltration attempts

## Example 5: Ransomware Early Detection

Early ransomware detection using behavioral indicators and threat intelligence.

### Scenario

1. User executes ransomware payload
2. File is unsigned and located in user directory
3. VirusTotal identifies as malicious
4. EchoTrail confirms rarity
5. System terminates process before encryption begins

### Detection Rule

```yaml
detect:
  event: CODE_IDENTITY
  op: and
  rules:
    # File in user directory (common ransomware drop location)
    - op: contains
      path: event/FILE_PATH
      value: "\\Users\\"
    # File is unsigned
    - op: is
      value: 0
      path: event/SIGNATURE/FILE_IS_SIGNED
    # VirusTotal reputation check
    - op: lookup
      path: event/HASH
      resource: hive://lookup/vt
      metadata_rules:
        op: and
        rules:
          # Multiple AV detections
          - op: is greater than
            value: 3
            path: /positives
          # Scan results contain ransomware indicators
          - op: or
            rules:
              - op: matches
                path: /scans/Microsoft/result
                re: "(?i)(ransom|crypt|locker)"
              - op: matches
                path: /scans/Kaspersky/result
                re: "(?i)(ransom|crypt|locker)"
    # EchoTrail confirms rarity
    - op: lookup
      path: event/FILE_PATH
      file name: true
      resource: hive://lookup/echotrail-insights
      metadata_rules:
        op: is greater than
        value: 10000
        path: /rank
    # Not in known-good software list
    - op: not
      op: lookup
      path: event/HASH
      resource: hive://lookup/approved-software

respond:
  - action: report
    name: ransomware-detected
    metadata:
      hash: '{{ .event.HASH }}'
      file_path: '{{ .event.FILE_PATH }}'
      file_name: '{{ .event.FILE_NAME }}'
      vt_positives: '{{ .lookup.positives }}'
      vt_total: '{{ .lookup.total }}'
      vt_permalink: '{{ .lookup.permalink }}'
      echotrail_rank: '{{ .lookup.rank }}'
      echotrail_host_prev: '{{ .lookup.host_prev }}'
      sensor: '{{ .routing.hostname }}'
      user: '{{ .routing.user }}'
      mitre_technique: "T1486"
      mitre_tactic: "Impact"
    suppression:
      max_count: 1
      period: 24h
      is_global: true
      keys:
        - '{{ .event.HASH }}'
  # Immediate network isolation
  - action: isolate_network
  # Terminate process tree immediately
  - action: task
    command: deny_tree <<PARENT>>
  # Kill specific process
  - action: task
    command: os_kill_process -p <<PID>>
  # Capture memory for analysis
  - action: task
    command: mem_dump
  # Persistent tagging
  - action: add tag
    tag: ransomware-infection
    ttl: 604800  # 7 days
```

### Behavioral Detection for Active Encryption

```yaml
detect:
  event: FILE_MODIFIED
  op: and
  rules:
    # Sensor tagged with ransomware infection
    - op: is tagged
      tag: ransomware-infection
    # File extension change to common ransomware extensions
    - op: or
      rules:
        - op: ends with
          path: event/FILE_PATH
          value: ".encrypted"
        - op: ends with
          path: event/FILE_PATH
          value: ".locked"
        - op: ends with
          path: event/FILE_PATH
          value: ".crypto"
        - op: ends with
          path: event/FILE_PATH
          value: ".crypt"
    # High file modification rate
    - op: is greater than
      path: event/MODIFICATION_COUNT
      value: 100
      window: 60  # 1 minute

respond:
  - action: report
    name: ransomware-encryption-in-progress
    metadata:
      file_path: '{{ .event.FILE_PATH }}'
      process: '{{ .event.PROCESS_NAME }}'
      modification_count: '{{ .event.MODIFICATION_COUNT }}'
  # Additional isolation if not already isolated
  - action: isolate_network
  # Force system into recovery mode
  - action: task
    command: os_suspend
```

### Supporting Infrastructure

#### Approved Software Lookup

```yaml
hives:
  lookup:
    approved-software:
      data:
        lookup_data:
          abc123def456...:
            software: "Microsoft Office"
            version: "16.0.5"
            approved_by: "IT Security"
            approved_date: "2024-01-01"
          789ghi012jkl...:
            software: "Adobe Acrobat"
            version: "23.8"
            approved_by: "IT Security"
            approved_date: "2024-01-15"
```

### Expected Outcome

1. Ransomware binary identified immediately upon execution
2. Multiple intelligence sources (VT + EchoTrail) confirm threat
3. Process terminated before encryption begins
4. Network isolated to prevent spread
5. Memory dump captured for forensic analysis
6. 7-day tag enables correlation with other indicators
7. If encryption begins, secondary rule detects active encryption
8. System can be protected before significant data loss

## Best Practices for Workflow Development

### 1. Layered Detection

Use multiple intelligence sources for high-confidence detections:
- Primary indicator (e.g., VT detection)
- Secondary confirmation (e.g., EchoTrail rarity)
- Tertiary validation (e.g., unsigned file)

### 2. Suppression Strategy

- **Global suppression**: For indicator-based detections (hash, domain, IP)
- **Local suppression**: For behavioral detections (process patterns, user activity)
- **Time windows**: Balance alert volume vs. detection coverage

### 3. Response Escalation

- **Low confidence**: Report + tag
- **Medium confidence**: Report + tag + isolate network
- **High confidence**: Report + isolate + terminate + capture forensics

### 4. Correlation Tagging

Use tags to correlate multi-stage attacks:
- Short TTL (1-24h) for immediate correlation
- Long TTL (7-30d) for investigation and threat hunting

### 5. Metadata Enrichment

Always include relevant context in reports:
- Threat intelligence verdicts and scores
- MITRE ATT&CK mappings
- Sensor and user information
- Timestamps and suppression keys

### 6. False Positive Management

- Use whitelists (corporate infrastructure, approved software)
- Filter benign services (GreyNoise RIOT)
- Implement negative lookups (NOT in known-good)
- Test rules in monitoring mode before enforcement

### 7. Performance Optimization

- Apply expensive API lookups after cheap local checks
- Use suppressions to reduce duplicate API calls
- Leverage LimaCharlie's global caching
- Filter events before threat intel lookups

### 8. Incident Response Readiness

- Capture forensics artifacts (memory dumps, network traffic)
- Provide enriched metadata for analysts
- Enable rapid response (isolation, termination)
- Maintain audit trail with tags and reports

## Summary

These five examples demonstrate:

1. **Multi-stage detection**: Correlating activity across multiple events
2. **Multi-source validation**: Combining APIs for high confidence
3. **Behavioral analysis**: Identifying anomalies with EchoTrail and patterns
4. **Geographic intelligence**: Using IP geolocation for risk assessment
5. **Rapid response**: Automated isolation and termination

**Key Techniques**:
- Tagging for cross-event correlation
- Suppression for noise reduction
- Metadata enrichment for analyst context
- Layered detection for accuracy
- Automated response for speed

For API details, see [REFERENCE.md](./REFERENCE.md).
For troubleshooting, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).
