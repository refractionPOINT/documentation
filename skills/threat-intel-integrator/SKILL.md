---
name: threat-intel-integrator
description: Activate when the user needs help integrating threat intelligence feeds, configuring API-based lookups, creating custom threat feeds, or enriching detections with threat intelligence data in LimaCharlie.
---

# Threat Intelligence Integrator

You are an expert in integrating and leveraging threat intelligence within LimaCharlie. Help users configure API-based threat intel integrations, create custom lookup tables, import threat feeds, enrich detections with threat intelligence data, and implement best practices for threat intelligence operations.

## Overview

LimaCharlie provides comprehensive threat intelligence capabilities through:

1. **Built-in API Integrations**: Pre-configured integrations with major threat intel providers
2. **Lookup Operator**: Query threat feeds and APIs directly from D&R rules
3. **Metadata Rules**: Evaluate and act on threat intelligence responses
4. **Custom Lookups**: Create and maintain your own threat intelligence feeds
5. **Lookup Manager**: Automatically sync and update threat feeds
6. **BinLib**: Private binary library for file reputation and analysis
7. **Event Enrichment**: Enrich telemetry with threat intelligence context

## Built-in API Integrations

LimaCharlie offers seamless integrations with leading threat intelligence providers. These integrations perform real-time API lookups during detection evaluation.

### VirusTotal

Query file hashes against VirusTotal's multi-engine malware scanning platform.

**Setup:**
1. Subscribe to the `vt` add-on in the marketplace
2. Add your VirusTotal API key in Organization > Integrations

**Supported Input:**
- File hashes (MD5, SHA1, SHA256)

**Example D&R Rule:**
```yaml
detect:
  event: CODE_IDENTITY
  op: lookup
  path: event/HASH
  resource: hive://lookup/vt
  metadata_rules:
    op: is greater than
    value: 1
    path: /
    length of: true
```

**Explanation:**
- Looks up file hash from CODE_IDENTITY events
- Checks if more than 1 AV engine flagged the file as malicious
- Uses `metadata_rules` to evaluate the response

**API Response Format:**
```json
{
  "api_vt": {
    "positives": 5,
    "total": 70,
    "scan_date": "2024-01-15 10:30:00",
    "permalink": "https://www.virustotal.com/..."
  }
}
```

**Rate Limiting:**
- Free tier: 4 lookups per minute
- LimaCharlie caches requests globally for 3 days to reduce costs

**Response Action Example:**
```yaml
detect:
  event: CODE_IDENTITY
  op: lookup
  path: event/HASH
  resource: hive://lookup/vt
  metadata_rules:
    op: is greater than
    value: 2
    path: /positives

respond:
  - action: report
    name: vt-malware-detected
  - action: task
    command: deny_tree <<PARENT>>
```

### GreyNoise

GreyNoise identifies internet noise from mass scanners and benign services to reduce false positives.

**Two API Endpoints:**

#### 1. IP Context (Noise Analysis)
Get detailed information about scanning activity from an IP.

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
  resource: hive://lookup/greynoise-noise-context
  metadata_rules:
    op: is
    value: true
    path: /seen
```

**API Response:**
```json
{
  "api_greynoise-noise-context": {
    "ip": "35.184.178.65",
    "seen": true,
    "classification": "malicious",
    "tags": ["RDP Scanner", "SSH Scanner"],
    "first_seen": "2024-01-01",
    "last_seen": "2024-01-15"
  }
}
```

#### 2. RIOT IP Lookup (Benign Service Identification)
Identify known benign services that commonly trigger false positives.

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: routing/ext_ip
  resource: hive://lookup/greynoise-riot
  metadata_rules:
    op: is
    value: true
    path: /riot
```

**API Response:**
```json
{
  "ip": "8.8.8.8",
  "riot": true,
  "classification": "benign",
  "name": "Google Public DNS",
  "trust_level": "1"
}
```

**Use Case - Filter Out Benign Services:**
```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/greynoise-riot
      metadata_rules:
        op: is
        value: false
        path: /riot
    - op: is public address
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS

respond:
  - action: report
    name: suspicious-external-connection
```

### EchoTrail

EchoTrail provides statistical insights on process behavior to identify anomalies.

**Supported Input:**
- MD5 hash
- SHA256 hash
- Windows filename with extension

**Example D&R Rule:**
```yaml
detect:
  event: NEW_PROCESS
  op: lookup
  path: event/FILE_PATH
  resource: hive://lookup/echotrail-insights
  metadata_rules:
    op: is lower than
    value: 0.1
    path: /host_prev
```

**API Response:**
```json
{
  "rank": 24,
  "host_prev": "0.05",
  "eps": "0.02",
  "paths": [
    ["C:\\Users\\...", "100.00"],
    ["C:\\Windows\\System32", "0.00"]
  ],
  "parents": [
    ["cmd.exe", "95.00"],
    ["explorer.exe", "5.00"]
  ],
  "description": "svchost.exe is...",
  "intel": "It is normal to see..."
}
```

**Key Fields:**
- `rank`: Popularity rank (lower = more common)
- `host_prev`: Host prevalence percentage
- `eps`: Endpoint prevalence score
- `paths`: Common file paths with percentages
- `parents`: Common parent processes

**Anomaly Detection Example:**
```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: lookup
      path: event/FILE_PATH
      resource: hive://lookup/echotrail-insights
      metadata_rules:
        op: or
        rules:
          - op: is lower than
            value: 1.0
            path: /host_prev
          - op: is greater than
            value: 50000
            path: /rank
    - op: contains
      path: event/COMMAND_LINE
      value: powershell

respond:
  - action: report
    name: rare-process-with-powershell
```

### IP Geolocation

LimaCharlie provides free IP geolocation using MaxMind GeoLite2 data.

**No Subscription Required** - Available to all users.

```yaml
detect:
  event: CONNECTED
  op: lookup
  path: routing/ext_ip
  resource: hive://lookup/ip-geo
  metadata_rules:
    op: is
    value: true
    path: country/is_in_european_union
```

**API Response:**
```json
{
  "country": {
    "geoname_id": 2750405,
    "iso_code": "NL",
    "is_in_european_union": true,
    "names": {
      "en": "Netherlands"
    }
  },
  "location": {
    "latitude": 52.3824,
    "longitude": 4.8995,
    "time_zone": "Europe/Amsterdam",
    "accuracy_radius": 100
  },
  "continent": {
    "code": "EU",
    "names": {
      "en": "Europe"
    }
  }
}
```

**Geofencing Example:**
```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/ip-geo
      metadata_rules:
        op: or
        rules:
          - op: is
            value: "RU"
            path: country/iso_code
          - op: is
            value: "CN"
            path: country/iso_code
          - op: is
            value: "KP"
            path: country/iso_code
    - op: is public address
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS

respond:
  - action: report
    name: connection-to-sanctioned-country
  - action: add tag
    tag: geo-alert
    ttl: 86400
```

### AlphaMountain

AlphaMountain provides AI-driven domain categorization, popularity, and threat ratings.

**Three API Services:**

#### 1. Category
Returns domain categorization (e.g., malware, phishing, adult content).

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/alphamountain-category
  metadata_rules:
    op: contains
    value: 34
    path: /categories
```

**API Response:**
```json
{
  "api_alphamountain-category": {
    "categories": [34, 12],
    "confidence": 0.90371,
    "scope": "domain",
    "threatyeti_url": "https://www.threatyeti.com/search?q=example.com"
  }
}
```

#### 2. Popularity
Returns domain popularity metrics (useful for detecting DGA domains).

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/alphamountain-popularity
  metadata_rules:
    op: is lower than
    value: 100000
    path: /rank
```

#### 3. Threat
Returns threat rating based on AI models and threat intelligence.

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/alphamountain-threat
  metadata_rules:
    op: is
    value: "malicious"
    path: /verdict
```

### Pangea

Pangea provides multiple security intelligence APIs for domain, file, IP, URL, and user reputation.

**Setup:**
Add Pangea API key in format: `domain/token`
Example: `aws.us.pangea.cloud/pts_7kb33fyz313372vuu5zg...`

**Five API Services:**

#### 1. Domain Reputation
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/pangea-domain-reputation
  metadata_rules:
    op: is
    value: "malicious"
    path: /verdict
```

**Response:**
```json
{
  "api_pangea-domain-reputation": {
    "category": ["malware"],
    "score": 95,
    "verdict": "malicious"
  }
}
```

#### 2. File Reputation
```yaml
detect:
  event: NEW_PROCESS
  op: lookup
  path: event/HASH
  resource: hive://lookup/pangea-file-reputation
  metadata_rules:
    op: is greater than
    value: 70
    path: /score
```

#### 3. IP Reputation
```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
  resource: hive://lookup/pangea-ip-reputation
  metadata_rules:
    op: is
    value: "malicious"
    path: /verdict
```

#### 4. URL Reputation
```yaml
detect:
  event: HTTP_REQUEST
  op: lookup
  path: event/URL
  resource: hive://lookup/pangea-url-reputation
```

#### 5. User Intelligence (Breach Data)
```yaml
detect:
  event: USER_LOGIN
  op: lookup
  path: event/USER_NAME
  resource: hive://lookup/pangea-user-reputation
```

## The Lookup Operator

The `lookup` operator is the core mechanism for querying threat intelligence in LimaCharlie D&R rules.

### Basic Syntax

```yaml
detect:
  event: <EVENT_TYPE>
  op: lookup
  path: <PATH_TO_VALUE>
  resource: hive://lookup/<LOOKUP_NAME>
  case sensitive: false  # Optional
```

### How Lookups Work

1. **Extract Value**: Get the value from the event at the specified `path`
2. **Query Resource**: Send the value to the lookup resource (API or local feed)
3. **Evaluate Response**: Use `metadata_rules` to evaluate the response
4. **Take Action**: If metadata_rules match, execute response actions

### Resource Types

**API-based Lookups:**
```
hive://lookup/vt
hive://lookup/greynoise-noise-context
hive://lookup/greynoise-riot
hive://lookup/echotrail-insights
hive://lookup/ip-geo
hive://lookup/alphamountain-category
hive://lookup/pangea-domain-reputation
```

**Custom/Feed Lookups:**
```
hive://lookup/<your-custom-lookup-name>
hive://lookup/tor-exit-nodes
hive://lookup/malware-domains
hive://lookup/crimeware-ips
```

### Path Syntax

Use JSON path notation to access event fields:

```
event/HASH                          # Direct field
event/FILE_PATH                     # File path
event/NETWORK_ACTIVITY/?/IP_ADDRESS # Array wildcard
event/PARENT/FILE_PATH              # Nested field
routing/ext_ip                      # Routing metadata
```

### Case Sensitivity

By default, lookups are case-sensitive. Disable with:

```yaml
op: lookup
path: event/DOMAIN_NAME
resource: hive://lookup/malware-domains
case sensitive: false
```

### Transforms with Lookups

Apply transforms before lookup:

#### File Name Transform
```yaml
detect:
  event: NEW_PROCESS
  op: lookup
  path: event/FILE_PATH
  file name: true  # Extract filename only
  resource: hive://lookup/malware-filenames
```

Transforms `C:\Users\admin\malware.exe` to `malware.exe` before lookup.

#### Sub Domain Transform
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  sub domain: "-2:"  # Last two domain components
  resource: hive://lookup/malware-domains
```

Transforms `mail.google.com` to `google.com` before lookup.

**Sub Domain Slice Notation:**
- `0:2` - First two components: `aa.bb` from `aa.bb.cc.dd`
- `-1` - Last component: `cc` from `aa.bb.cc`
- `1:` - All components starting at 1: `bb.cc` from `aa.bb.cc`
- `-2:` - Last two components: `cc.dd` from `aa.bb.cc.dd`
- `:` - Test each component individually

## Metadata Rules

Metadata rules evaluate the response from API-based lookups to determine if the detection should match.

### Basic Structure

```yaml
detect:
  event: <EVENT_TYPE>
  op: lookup
  path: <PATH>
  resource: <RESOURCE>
  metadata_rules:
    op: <OPERATOR>
    path: <JSON_PATH_IN_RESPONSE>
    value: <EXPECTED_VALUE>
```

### Supported Operators

All standard D&R operators work in metadata_rules:

- `is`, `is not`
- `is greater than`, `is lower than`
- `contains`, `starts with`, `ends with`
- `matches` (regex)
- `exists`
- `and`, `or`, `not`

### Common Patterns

#### Check if Field Exists
```yaml
metadata_rules:
  op: exists
  path: /positives
```

#### Threshold Check
```yaml
metadata_rules:
  op: is greater than
  value: 5
  path: /positives
```

#### Boolean Check
```yaml
metadata_rules:
  op: is
  value: true
  path: /riot
```

#### String Match
```yaml
metadata_rules:
  op: is
  value: "malicious"
  path: /verdict
```

#### Array Contains
```yaml
metadata_rules:
  op: contains
  value: "malware"
  path: /categories
```

#### Complex Logic
```yaml
metadata_rules:
  op: or
  rules:
    - op: is greater than
      value: 10
      path: /positives
    - op: is
      value: "malicious"
      path: /verdict
```

#### Length Check
```yaml
metadata_rules:
  op: is greater than
  value: 0
  path: /
  length of: true
```

This checks if the response has any content (useful for simple lookup lists).

### Accessing Nested Fields

Use `/` to access nested JSON:

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

```yaml
metadata_rules:
  op: is
  value: true
  path: /scans/Microsoft/detected
```

### Multiple Metadata Rules

Combine multiple conditions:

```yaml
metadata_rules:
  op: and
  rules:
    - op: is greater than
      value: 3
      path: /positives
    - op: is lower than
      value: 70
      path: /total
    - op: exists
      path: /permalink
```

## Creating Custom Lookups

Create your own threat intelligence feeds for indicators like malicious IPs, domains, hashes, or file paths.

### Lookup Format

Lookups are key-value dictionaries where:
- **Key**: The indicator (IP, domain, hash, etc.) - must be a string
- **Value**: Metadata associated with the indicator - must be a dictionary (can be empty `{}`)

### Three Input Formats

#### 1. JSON Format (lookup_data)

Full control with metadata:

```json
{
  "lookup_data": {
    "8.8.8.8": {
      "category": "dns",
      "provider": "google",
      "severity": "low"
    },
    "1.1.1.1": {
      "category": "dns",
      "provider": "cloudflare",
      "severity": "low"
    },
    "malware.exe": {
      "hash": "abc123...",
      "family": "ransomware",
      "severity": "critical"
    }
  }
}
```

#### 2. Newline Format (newline_content)

Simple list, one indicator per line (no metadata):

```json
{
  "newline_content": "8.8.8.8\n1.1.1.1\n192.168.1.1\nmalware.exe\nevil.com"
}
```

Each indicator automatically gets empty metadata `{}`.

#### 3. YAML Format (yaml_content)

YAML string with indicators and metadata:

```json
{
  "yaml_content": "8.8.8.8:\n  category: dns\n  provider: google\n1.1.1.1:\n  category: dns\n  provider: cloudflare"
}
```

### Creating Lookups in the Web UI

1. Navigate to **Automation** → **Lookups**
2. Click **Add Lookup**
3. Enter lookup name (e.g., `my-malware-hashes`)
4. Select format (JSON, Newline, or YAML)
5. Paste your lookup data
6. Click **Save**

### Creating Lookups via Infrastructure as Code

```yaml
hives:
  lookup:
    malware-domains:
      data:
        lookup_data:
          evil.com:
            category: malware
            first_seen: "2024-01-01"
          phishing.net:
            category: phishing
            first_seen: "2024-01-15"
      usr_mtd:
        enabled: true
        expiry: 0
        tags:
          - malware
          - custom-feed
        comment: "Custom malware domain list"
```

### Using Custom Lookups

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malware-domains
  case sensitive: false

respond:
  - action: report
    name: malware-domain-detected
```

### Lookup with Metadata Evaluation

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malware-domains
  metadata_rules:
    op: is
    value: "phishing"
    path: /category

respond:
  - action: report
    name: phishing-domain-detected
  - action: isolate_network
```

### Simple List Lookup (No Metadata)

For simple presence checks:

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
  resource: hive://lookup/tor-exit-nodes
  metadata_rules:
    op: exists
    path: /

respond:
  - action: report
    name: tor-connection-detected
```

Or even simpler, omit metadata_rules for any match:

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
  resource: hive://lookup/blocked-ips

respond:
  - action: report
    name: blocked-ip-connection
```

## Threat Feed Management

LimaCharlie provides curated public threat feeds and the ability to auto-sync custom feeds.

### Public Threat Feeds

Available in the Add-ons marketplace under "Lookups" category:

**Popular Feeds:**
- `crimeware-ips` - Known malicious IP addresses
- `malware-domains` - Malicious domains
- `tor-exit-nodes` - Tor exit node IPs
- `alienvault-ip-reputation` - AlienVault OTX IP reputation
- `talos-ip-blacklist` - Cisco Talos IP blacklist
- `loldrivers` - Living Off the Land (LOL) vulnerable drivers

**Subscribing to Public Feeds:**

1. Navigate to **Add-ons** → **Marketplace**
2. Filter by category: **Lookups**
3. Click on a feed (e.g., `crimeware-ips`)
4. Click **Subscribe**

The feed is immediately available as:
```
hive://lookup/crimeware-ips
```

**Example Usage:**
```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
  resource: hive://lookup/crimeware-ips

respond:
  - action: report
    name: crimeware-ip-detected
  - action: isolate_network
```

### Lookup Manager Extension

Automatically sync and update threat feeds from external sources.

**Features:**
- Auto-sync every 24 hours
- Support for public and private feeds
- URL or ARL (Authentication Resource Locator) sources
- Manual sync on-demand
- Pre-configured feed templates

**Setup:**

1. Subscribe to **ext-lookup-manager** in Add-ons marketplace
2. Navigate to **Extensions** → **Lookup Manager**
3. Configure lookup sources

#### Option 1: Pre-configured Lookups

LimaCharlie provides curated public threat feeds:

- AlienVault OTX IP Reputation
- Tor Exit Nodes
- Talos IP Blacklist
- LOLDrivers
- And many more...

Simply select from the dropdown and click **Add**.

#### Option 2: Public URL Lookups

Add any publicly accessible JSON threat feed:

```
Name: custom-malware-ips
URL: https://example.com/threat-feeds/malware-ips.json
Format: json
Tags: malware, ips
```

#### Option 3: Private Repository Lookups

Use ARLs to access private GitHub repositories:

**GitHub ARL Format:**
```
[github,org-name/repo-name/path/to/feed.json,token,ghp_abc123...]
```

**Example:**
```
Name: private-iocs
ARL: [github,myorg/threat-intel/feeds/iocs.json,token,ghp_abc123def456...]
Format: json
Tags: private, iocs
```

**Creating GitHub Token:**
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token with `repo` permissions
3. Copy token and use in ARL

#### Manual Sync

Click **Manual Sync** button to immediately refresh all configured feeds.

#### Infrastructure as Code

```yaml
hives:
  extension_config:
    ext-lookup-manager:
      data:
        lookup_manager_rules:
          - name: alienvault
            predefined: '[https,storage.googleapis.com/lc-lookups-bucket/alienvault-ip-reputation.json]'
            format: json
            tags:
              - alienvault
              - ip-reputation
            arl: ""
          - name: tor
            predefined: '[https,storage.googleapis.com/lc-lookups-bucket/tor-ips.json]'
            format: json
            tags:
              - tor
            arl: ""
          - name: custom-feed
            predefined: ""
            format: json
            tags:
              - custom
            arl: "[github,myorg/feeds/custom.json,token,ghp_...]"
      usr_mtd:
        enabled: true
        expiry: 0
        tags: []
        comment: "Automated threat feed management"
```

## Binary Library (BinLib)

Build a private library of observed executables for analysis, searching, and threat hunting.

### What is BinLib?

BinLib collects and stores binaries observed in your environment, creating your own private "VirusTotal-like" repository.

**Capabilities:**
- Store metadata and binaries from CODE_IDENTITY events
- Search by hash (MD5, SHA1, SHA256)
- Download observed binaries for analysis
- Tag binaries with MITRE ATT&CK techniques
- Run YARA scans across your binary collection
- Historical binary analysis

### Setup

**Requirements:**
1. Subscribe to `ext-reliable-tasking` extension
2. Subscribe to `binlib` extension

### BinLib Operations

#### check_hash

Check if a hash exists in your library:

```json
{
  "request": {
    "operation": "check_hash",
    "hash": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb"
  }
}
```

**Response:**
```json
{
  "data": {
    "found": true,
    "md5": "e977bded5d4198d4895ac75150271158",
    "sha1": "9e2b05f142c35448c9bc48c40a732d632485c719",
    "sha256": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb"
  }
}
```

#### get_hash_metadata

Retrieve detailed metadata:

```json
{
  "request": {
    "operation": "get_hash_metadata",
    "hash": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb"
  }
}
```

**Response:**
```json
{
  "data": {
    "found": true,
    "md5": "e977bded5d4198d4895ac75150271158",
    "metadata": {
      "imp_hash": "c105252faa9163fd63fb81bb334c61bf",
      "res_company_name": "Google LLC",
      "res_file_description": "Google Chrome Installer",
      "res_product_name": "Google Chrome Installer",
      "res_product_version": "113.0.5672.127",
      "sha256": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb",
      "sig_issuer": "US, DigiCert Trusted G4 Code Signing RSA4096 SHA384 2021 CA1",
      "sig_serial": "0e4418e2dede36dd2974c3443afb5ce5",
      "sig_subject": "US, California, Mountain View, Google LLC, Google LLC",
      "size": 5155608,
      "type": "pe"
    },
    "sha1": "9e2b05f142c35448c9bc48c40a732d632485c719",
    "sha256": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb"
  }
}
```

#### get_hash_data

Download the binary file:

```json
{
  "request": {
    "operation": "get_hash_data",
    "hash": "2f5d0c6159b194d6f0f2eae0b7734708368a23aebf9af4db9293865b57ffcaeb"
  }
}
```

**Response:**
```json
{
  "data": {
    "download_url": "https://storage.googleapis.com/lc-library-bin/b_2f5d0c...",
    "found": true
  }
}
```

**WARNING:** Exercise extreme caution when downloading binaries. LimaCharlie does not filter malicious files. Download only to isolated analysis systems.

#### search

Search for binaries by various criteria:

```json
{
  "request": {
    "operation": "search",
    "query": {
      "file_name": "svchost.exe",
      "is_signed": true
    }
  }
}
```

#### yara_scan

Run YARA rules across your binary collection:

```json
{
  "request": {
    "operation": "yara_scan",
    "yara_rule": "rule malware { strings: $a = \"malicious\" condition: $a }"
  }
}
```

### BinLib with D&R Rules

Enrich detections with BinLib data:

```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: contains
      path: event/COMMAND_LINE
      value: suspicious
    - op: exists
      path: event/HASH

respond:
  - action: extension request
    extension: binlib
    extension_action: get_hash_metadata
    extension_data:
      hash: '{{ .event.HASH }}'
  - action: report
    name: suspicious-process-with-binlib-data
```

### Threat Hunting with BinLib

1. **Historical Analysis**: Search for previously-seen malicious hashes
2. **Signature Analysis**: Find unsigned binaries in sensitive locations
3. **Tagging**: Tag binaries with MITRE ATT&CK techniques for enrichment
4. **YARA Scanning**: Run malware signatures across your entire binary collection
5. **Incident Response**: Quickly identify scope of compromise by hash

## Event Enrichment Patterns

Enrich detections with contextual threat intelligence before taking action.

### Pattern 1: Lookup and Report

Basic enrichment with threat intel context:

```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malware-domains
  metadata_rules:
    op: is
    value: "malware"
    path: /category

respond:
  - action: report
    name: malware-domain-detected
    metadata:
      domain: '{{ .event.DOMAIN_NAME }}'
      category: '{{ .lookup.category }}'
      first_seen: '{{ .lookup.first_seen }}'
      sensor: '{{ .routing.hostname }}'
```

### Pattern 2: Multi-Lookup Enrichment

Combine multiple threat intel sources:

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/ip-geo
      metadata_rules:
        op: is
        value: "CN"
        path: /country/iso_code
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/greynoise-noise-context
      metadata_rules:
        op: is
        value: true
        path: /seen

respond:
  - action: report
    name: suspicious-chinese-ip-with-scanning-activity
    metadata:
      ip: '{{ index .event.NETWORK_ACTIVITY 0 "IP_ADDRESS" }}'
      country: '{{ .lookup.country.names.en }}'
      greynoise_classification: '{{ .lookup.classification }}'
      greynoise_tags: '{{ .lookup.tags }}'
```

### Pattern 3: Conditional Enrichment

Enrich only when specific conditions are met:

```yaml
detect:
  event: CODE_IDENTITY
  op: and
  rules:
    - op: is
      value: 0
      path: event/SIGNATURE/FILE_IS_SIGNED
    - op: lookup
      path: event/HASH
      resource: hive://lookup/vt
      metadata_rules:
        op: is greater than
        value: 5
        path: /positives

respond:
  - action: report
    name: unsigned-malware-detected
    metadata:
      hash: '{{ .event.HASH }}'
      file_path: '{{ .event.FILE_PATH }}'
      vt_positives: '{{ .lookup.positives }}'
      vt_total: '{{ .lookup.total }}'
  - action: task
    command: deny_tree <<PARENT>>
```

### Pattern 4: Enrichment with External Action

Enrich and take external action:

```yaml
detect:
  event: DNS_REQUEST
  op: and
  rules:
    - op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/pangea-domain-reputation
      metadata_rules:
        op: is
        value: "malicious"
        path: /verdict
    - op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/alphamountain-category
      metadata_rules:
        op: contains
        value: 34  # Malware category
        path: /categories

respond:
  - action: report
    name: high-confidence-malware-domain
    metadata:
      domain: '{{ .event.DOMAIN_NAME }}'
      pangea_score: '{{ .lookup.score }}'
      alphamountain_confidence: '{{ .lookup.confidence }}'
  - action: isolate_network
  - action: add tag
    tag: malware-infection
    ttl: 86400
```

### Pattern 5: False Positive Reduction

Use threat intel to filter out benign activity:

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: is public address
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/greynoise-riot
      metadata_rules:
        op: is
        value: false
        path: /riot
    - op: not
      op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/known-good-ips

respond:
  - action: report
    name: unknown-external-connection
```

## Best Practices

### 1. API Rate Limiting

**Challenge:** API-based lookups have rate limits and costs.

**Best Practices:**
- Use LimaCharlie's global caching (3-day cache for VirusTotal)
- Apply lookups only to high-fidelity events
- Use suppression to limit lookup frequency
- Combine with local lookups before expensive API calls
- Monitor your API usage and billing

**Example - Rate-Limited Lookup:**
```yaml
detect:
  event: CODE_IDENTITY
  op: and
  rules:
    - op: is
      value: 0
      path: event/SIGNATURE/FILE_IS_SIGNED
    - op: not
      op: lookup
      path: event/HASH
      resource: hive://lookup/known-good-hashes
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
    suppression:
      max_count: 1
      period: 24h
      is_global: true
      keys:
        - '{{ .event.HASH }}'
```

This approach:
1. Checks local known-good list first (free, fast)
2. Only queries VirusTotal if not known-good
3. Suppresses duplicate alerts for same hash (24h)
4. Reduces API calls significantly

### 2. Caching Strategy

**Use local lookups as first-tier cache:**

```yaml
# Create a lookup of previously-validated hashes
hives:
  lookup:
    validated-hashes:
      data:
        lookup_data:
          abc123...:
            validation_date: "2024-01-15"
            status: "clean"
```

**Rule with caching:**
```yaml
detect:
  event: CODE_IDENTITY
  op: and
  rules:
    - op: not
      op: lookup
      path: event/HASH
      resource: hive://lookup/validated-hashes
    - op: lookup
      path: event/HASH
      resource: hive://lookup/vt  # Only called if not in cache
```

### 3. False Positive Management

**Use RIOT to filter benign services:**

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: and
  rules:
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/malware-ips
    - op: lookup
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
      resource: hive://lookup/greynoise-riot
      metadata_rules:
        op: is
        value: false
        path: /riot  # Filter out known benign services
```

**Create custom whitelist:**

```yaml
hives:
  lookup:
    corporate-infrastructure:
      data:
        lookup_data:
          proxy.corp.com: {}
          mail.corp.com: {}
          vpn.corp.com: {}
```

**Use in rules:**
```yaml
detect:
  event: DNS_REQUEST
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

### 4. Lookup Performance

**Optimize path selectors:**
- Use specific paths instead of broad wildcards
- Apply filters before lookups when possible
- Use scoped operators for array fields

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
      - op: is public address
        path: event/IP_ADDRESS
      - op: lookup
        path: event/IP_ADDRESS  # Only checks public IPs
        resource: hive://lookup/malware-ips
```

### 5. Threat Intel Hygiene

**Keep feeds updated:**
- Use Lookup Manager for automatic updates
- Set appropriate refresh intervals (24h default)
- Monitor feed health and availability
- Remove stale indicators periodically

**Version control your custom feeds:**
- Store custom feeds in Git
- Use Infrastructure as Code for reproducibility
- Document feed sources and update procedures
- Tag feeds with metadata (source, date, confidence)

### 6. Tiered Intelligence Approach

**Structure lookups by confidence:**

**Tier 1 - High Confidence (Block/Alert):**
- Known malware hashes
- Active C2 infrastructure
- Confirmed malicious IPs

**Tier 2 - Medium Confidence (Alert/Investigate):**
- Suspicious domains
- Low-prevalence indicators
- Behavioral anomalies

**Tier 3 - Low Confidence (Log/Enrich):**
- Geolocation data
- Popularity metrics
- Historical context

**Example:**
```yaml
# High confidence - immediate action
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/known-malware-c2

respond:
  - action: isolate_network
  - action: report
    name: malware-c2-contact

---
# Medium confidence - alert and tag
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/suspicious-domains

respond:
  - action: report
    name: suspicious-domain-query
  - action: add tag
    tag: suspicious-activity
    ttl: 3600
```

### 7. Enrichment vs. Detection

**Separate concerns:**

**Enrichment Rules** (target: artifact, no alerts):
```yaml
detect:
  event: DNS_REQUEST
  op: exists
  path: event/DOMAIN_NAME
  target: artifact

respond:
  - action: extension request
    extension: ip-geo
    # Enrich all DNS requests with geolocation
```

**Detection Rules** (target: event, generate alerts):
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/malware-domains

respond:
  - action: report
    name: malware-domain-detected
```

### 8. Testing and Validation

**Test lookups before deployment:**

1. **Use Rule Tester** in web UI
2. **Replay historical events** against new rules
3. **Create unit tests** for lookup logic
4. **Monitor suppression effectiveness**

**Example test event:**
```json
{
  "event": "DNS_REQUEST",
  "data": {
    "DOMAIN_NAME": "evil.com"
  }
}
```

### 9. Monitoring and Metrics

**Track key metrics:**
- Lookup success/failure rates
- API response times
- False positive rates
- Detection volume by feed
- Coverage gaps

**Create monitoring rules:**
```yaml
detect:
  event: billing_record
  op: is
  path: event/record/k
  value: api-vt:requests

respond:
  - action: report
    name: vt-api-usage-tracking
    suppression:
      max_count: 1
      period: 1h
```

### 10. Documentation

**Document your threat intel infrastructure:**
- Feed sources and update schedules
- API key ownership and rotation
- Custom lookup purposes and maintenance
- Response action rationale
- False positive handling procedures

## Complete Threat Intelligence Workflow Examples

### Example 1: Multi-Stage Malware Detection

Detect and respond to multi-stage malware using threat intelligence:

```yaml
# Stage 1: Initial payload download
detect:
  event: DNS_REQUEST
  op: and
  rules:
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

respond:
  - action: report
    name: high-confidence-malware-domain
    metadata:
      domain: '{{ .event.DOMAIN_NAME }}'
      pangea_verdict: '{{ .lookup.verdict }}'
      alpha_score: '{{ .lookup.score }}'
  - action: add tag
    tag: malware-download-attempt
    ttl: 86400

---
# Stage 2: Malicious file execution
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is tagged
      tag: malware-download-attempt
    - op: lookup
      path: event/HASH
      resource: hive://lookup/vt
      metadata_rules:
        op: is greater than
        value: 5
        path: /positives
    - op: is
      value: 0
      path: event/SIGNATURE/FILE_IS_SIGNED

respond:
  - action: report
    name: malware-execution-confirmed
    metadata:
      hash: '{{ .event.HASH }}'
      file_path: '{{ .event.FILE_PATH }}'
      vt_positives: '{{ .lookup.positives }}'
  - action: isolate_network
  - action: task
    command: deny_tree <<PARENT>>
  - action: task
    command: mem_dump
```

### Example 2: APT-Style Lateral Movement Detection

Detect lateral movement using multiple intelligence sources:

```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: scope
  path: event/NETWORK_ACTIVITY/
  rule:
    op: and
    rules:
      - op: is
        value: 445
        path: event/DESTINATION/PORT
      - op: contains
        path: event/FILE_PATH
        value: "psexec"
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
      - op: lookup
        path: event/DESTINATION/IP_ADDRESS
        resource: hive://lookup/corporate-infrastructure

respond:
  - action: report
    name: suspected-apt-lateral-movement
    metadata:
      source_ip: '{{ index .event.NETWORK_ACTIVITY 0 "SOURCE" "IP_ADDRESS" }}'
      dest_ip: '{{ index .event.NETWORK_ACTIVITY 0 "DESTINATION" "IP_ADDRESS" }}'
      country: '{{ .lookup.country.iso_code }}'
      tool: "psexec"
      mitre_technique: "T1021.002"
  - action: add tag
    tag: apt-activity
    ttl: 604800  # 7 days
```

### Example 3: Phishing Detection with URL Analysis

Comprehensive phishing detection using multiple threat intel APIs:

```yaml
detect:
  event: HTTP_REQUEST
  op: and
  rules:
    - op: lookup
      path: event/URL_DOMAIN
      resource: hive://lookup/alphamountain-popularity
      metadata_rules:
        op: is greater than
        value: 100000
        path: /rank  # Low popularity
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
    - op: string distance
      path: event/URL_DOMAIN
      value:
        - microsoft.com
        - office365.com
        - google.com
        - dropbox.com
      max: 2  # Possible typosquatting

respond:
  - action: report
    name: potential-phishing-site
    metadata:
      url: '{{ .event.URL }}'
      domain: '{{ .event.URL_DOMAIN }}'
      popularity_rank: '{{ .lookup.rank }}'
      reputation: '{{ .lookup.verdict }}'
      user: '{{ .event.USER_NAME }}'
  - action: task
    command: deny_tree <<PARENT>>
```

### Example 4: Data Exfiltration Detection

Detect data exfiltration using DNS tunneling with threat intelligence:

```yaml
detect:
  event: DNS_REQUEST
  op: and
  rules:
    - op: matches
      path: event/DOMAIN_NAME
      re: '^[a-f0-9]{32,}\.'  # Hex-encoded data
    - op: lookup
      path: event/DOMAIN_NAME
      sub domain: "-1"  # TLD only
      resource: hive://lookup/dynamic-dns-providers
    - op: lookup
      path: event/DOMAIN_NAME
      sub domain: "-2:"  # Last two components
      resource: hive://lookup/alphamountain-popularity
      metadata_rules:
        op: is greater than
        value: 500000
        path: /rank  # Very unpopular
    - op: not
      op: lookup
      path: event/DOMAIN_NAME
      resource: hive://lookup/corporate-domains

respond:
  - action: report
    name: potential-dns-tunneling
    metadata:
      domain: '{{ .event.DOMAIN_NAME }}'
      query_type: '{{ .event.DNS_TYPE }}'
      sensor: '{{ .routing.hostname }}'
      mitre_technique: "T1048.003"
  - action: isolate_network
  - action: add tag
    tag: data-exfiltration-suspected
    ttl: 86400
```

### Example 5: Ransomware Early Detection

Early ransomware detection using behavioral indicators and threat intel:

```yaml
detect:
  event: CODE_IDENTITY
  op: and
  rules:
    - op: contains
      path: event/FILE_PATH
      value: "\\Users\\"
    - op: is
      value: 0
      path: event/SIGNATURE/FILE_IS_SIGNED
    - op: lookup
      path: event/HASH
      resource: hive://lookup/vt
      metadata_rules:
        op: and
        rules:
          - op: is greater than
            value: 3
            path: /positives
          - op: contains
            path: /scan_results
            value: "ransom"
    - op: lookup
      path: event/FILE_PATH
      file name: true
      resource: hive://lookup/echotrail-insights
      metadata_rules:
        op: is greater than
        value: 10000
        path: /rank  # Rare binary

respond:
  - action: report
    name: ransomware-detected
    metadata:
      hash: '{{ .event.HASH }}'
      file_path: '{{ .event.FILE_PATH }}'
      vt_positives: '{{ .lookup.positives }}'
      echotrail_rank: '{{ .lookup.rank }}'
      mitre_technique: "T1486"
  - action: isolate_network
  - action: task
    command: deny_tree <<PARENT>>
  - action: task
    command: os_kill_process -p <<PID>>
```

## Troubleshooting

### Common Issues

#### 1. Lookup Not Matching

**Problem:** Lookup operator not matching expected indicators.

**Debugging Steps:**
1. Verify lookup is subscribed/exists
2. Check case sensitivity setting
3. Verify path extracts correct value
4. Test with rule tester in web UI
5. Check lookup format (JSON structure)

**Example Debug Rule:**
```yaml
detect:
  event: DNS_REQUEST
  op: exists
  path: event/DOMAIN_NAME

respond:
  - action: report
    name: debug-domain-value
    metadata:
      domain: '{{ .event.DOMAIN_NAME }}'
      # Use this to verify extracted value
```

#### 2. Metadata Rules Not Evaluating

**Problem:** Metadata rules not matching API responses.

**Debugging:**
- Use `op: exists` on root path first to verify response
- Check API response format in documentation
- Verify JSON path syntax (`/field/nested/value`)
- Test with permissive rules first, then narrow

**Example:**
```yaml
# First, verify API responds
metadata_rules:
  op: exists
  path: /

# Then verify specific field exists
metadata_rules:
  op: exists
  path: /positives

# Finally, check value
metadata_rules:
  op: is greater than
  value: 0
  path: /positives
```

#### 3. API Rate Limiting

**Problem:** Hitting API rate limits or incurring unexpected costs.

**Solutions:**
- Use local lookups as first-tier filters
- Implement suppression on lookup results
- Leverage LimaCharlie's caching
- Apply lookups only to high-confidence events

#### 4. Lookup Manager Not Syncing

**Problem:** Feeds not updating via Lookup Manager.

**Check:**
- Verify URL/ARL is accessible
- Check feed format (JSON valid)
- Verify authentication (GitHub token)
- Click "Manual Sync" to test
- Check extension logs for errors

#### 5. Performance Issues

**Problem:** Rules with lookups running slowly.

**Optimization:**
- Reduce lookup frequency with filters
- Use scoped operators for arrays
- Combine multiple conditions with `and`
- Apply lookups late in rule logic

## Summary

LimaCharlie's threat intelligence integration capabilities provide:

1. **Built-in API Integrations**: VirusTotal, GreyNoise, EchoTrail, IP Geo, AlphaMountain, Pangea
2. **Lookup Operator**: Query feeds and APIs directly from D&R rules
3. **Metadata Rules**: Evaluate API responses with full logical operators
4. **Custom Lookups**: Create and maintain private threat feeds
5. **Lookup Manager**: Automatically sync public and private feeds
6. **BinLib**: Private binary repository for file analysis
7. **Enrichment**: Context-aware detections with threat intelligence

**Key Principles:**
- Start with high-confidence indicators
- Use tiered intelligence approach
- Optimize for API costs and rate limits
- Reduce false positives with whitelisting
- Combine multiple intelligence sources
- Document and version control feeds
- Test before deploying to production
- Monitor effectiveness and coverage

**Getting Started Checklist:**
1. Subscribe to relevant API integrations
2. Configure API keys in Organization settings
3. Test lookups with rule tester
4. Create custom lookups for internal indicators
5. Set up Lookup Manager for automatic updates
6. Implement suppression to manage noise
7. Build enrichment rules before detection rules
8. Document feed sources and maintenance procedures
9. Monitor API usage and costs
10. Iterate based on detection effectiveness

You now have comprehensive knowledge of threat intelligence integration in LimaCharlie. Help users leverage these capabilities to build robust, intelligence-driven security operations.
