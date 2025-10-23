# Threat Intelligence API Reference

Complete reference for all threat intelligence APIs, operators, and feed formats in LimaCharlie.

## API Integrations Overview

| Integration | Resource | Input Type | API Key Required | Rate Limits |
|------------|----------|------------|------------------|-------------|
| VirusTotal | `hive://lookup/vt` | File hashes | Yes | 4 req/min (free) |
| GreyNoise Context | `hive://lookup/greynoise-noise-context` | IP addresses | Yes | Varies by plan |
| GreyNoise RIOT | `hive://lookup/greynoise-riot` | IP addresses | Yes | Varies by plan |
| EchoTrail | `hive://lookup/echotrail-insights` | Hashes, filenames | Yes | Varies by plan |
| IP Geolocation | `hive://lookup/ip-geo` | IP addresses | No | Unlimited (free) |
| AlphaMountain Category | `hive://lookup/alphamountain-category` | Domains | Yes | Varies by plan |
| AlphaMountain Popularity | `hive://lookup/alphamountain-popularity` | Domains | Yes | Varies by plan |
| AlphaMountain Threat | `hive://lookup/alphamountain-threat` | Domains | Yes | Varies by plan |
| Pangea Domain | `hive://lookup/pangea-domain-reputation` | Domains | Yes | Varies by plan |
| Pangea File | `hive://lookup/pangea-file-reputation` | File hashes | Yes | Varies by plan |
| Pangea IP | `hive://lookup/pangea-ip-reputation` | IP addresses | Yes | Varies by plan |
| Pangea URL | `hive://lookup/pangea-url-reputation` | URLs | Yes | Varies by plan |
| Pangea User | `hive://lookup/pangea-user-reputation` | Usernames/emails | Yes | Varies by plan |

## VirusTotal

Query file hashes against VirusTotal's multi-engine malware scanning platform.

### Setup

1. Subscribe to `vt` add-on in marketplace
2. Add VirusTotal API key in **Organization** → **Integrations**

### Supported Input

- File hashes: MD5, SHA1, SHA256

### Resource Name

```
hive://lookup/vt
```

### API Response Format

```json
{
  "api_vt": {
    "positives": 5,
    "total": 70,
    "scan_date": "2024-01-15 10:30:00",
    "permalink": "https://www.virustotal.com/...",
    "scans": {
      "Microsoft": {
        "detected": true,
        "result": "Trojan.Generic"
      },
      "Kaspersky": {
        "detected": true,
        "result": "HEUR:Trojan.Win32.Generic"
      }
    }
  }
}
```

### Key Fields

- `positives` (int): Number of AV engines that flagged as malicious
- `total` (int): Total number of AV engines that scanned
- `scan_date` (string): Date of last scan
- `permalink` (string): URL to VirusTotal report
- `scans` (object): Individual scanner results

### Example Rules

**Basic Detection:**
```yaml
detect:
  event: CODE_IDENTITY
  op: lookup
  path: event/HASH
  resource: hive://lookup/vt
  metadata_rules:
    op: is greater than
    value: 1
    path: /positives

respond:
  - action: report
    name: vt-malware-detected
```

**Threshold-Based:**
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
    name: high-confidence-malware
    metadata:
      hash: '{{ .event.HASH }}'
      vt_positives: '{{ .lookup.positives }}'
      vt_total: '{{ .lookup.total }}'
  - action: task
    command: deny_tree <<PARENT>>
```

**Specific Scanner Check:**
```yaml
detect:
  event: CODE_IDENTITY
  op: lookup
  path: event/HASH
  resource: hive://lookup/vt
  metadata_rules:
    op: is
    value: true
    path: /scans/Microsoft/detected

respond:
  - action: report
    name: microsoft-defender-detection
```

### Rate Limiting

- **Free tier**: 4 requests per minute
- **LimaCharlie caching**: 3-day global cache to reduce API calls
- **Best practice**: Use local lookups first, then query VT

### Caching Behavior

LimaCharlie maintains a global 3-day cache for VirusTotal lookups across all organizations. This means:
- First lookup triggers API call
- Subsequent lookups within 3 days use cached result
- Reduces API costs significantly
- Cache is shared globally (all LimaCharlie users)

## GreyNoise

GreyNoise identifies internet noise from mass scanners and benign services to reduce false positives.

### Setup

1. Subscribe to GreyNoise add-on in marketplace
2. Add GreyNoise API key in **Organization** → **Integrations**

### Two API Endpoints

#### 1. IP Context (Noise Analysis)

Identifies scanning activity and malicious behavior from IPs.

**Resource**: `hive://lookup/greynoise-noise-context`

**API Response:**
```json
{
  "api_greynoise-noise-context": {
    "ip": "35.184.178.65",
    "seen": true,
    "classification": "malicious",
    "tags": ["RDP Scanner", "SSH Scanner"],
    "first_seen": "2024-01-01",
    "last_seen": "2024-01-15",
    "actor": "unknown",
    "spoofable": false
  }
}
```

**Key Fields:**
- `seen` (bool): Whether GreyNoise has observed this IP scanning
- `classification` (string): "malicious", "benign", or "unknown"
- `tags` (array): Behavior tags (e.g., "SSH Scanner", "Web Scanner")
- `first_seen` / `last_seen` (string): Observation period
- `actor` (string): Known threat actor if identified

**Example Rule:**
```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
  resource: hive://lookup/greynoise-noise-context
  metadata_rules:
    op: and
    rules:
      - op: is
        value: true
        path: /seen
      - op: is
        value: "malicious"
        path: /classification

respond:
  - action: report
    name: known-malicious-scanner
    metadata:
      ip: '{{ index .event.NETWORK_ACTIVITY 0 "IP_ADDRESS" }}'
      classification: '{{ .lookup.classification }}'
      tags: '{{ .lookup.tags }}'
```

#### 2. RIOT IP Lookup (Benign Service Identification)

Identifies known benign services that commonly trigger false positives.

**Resource**: `hive://lookup/greynoise-riot`

**API Response:**
```json
{
  "ip": "8.8.8.8",
  "riot": true,
  "classification": "benign",
  "name": "Google Public DNS",
  "description": "Google's public DNS service",
  "trust_level": "1",
  "category": "public_dns"
}
```

**Key Fields:**
- `riot` (bool): True if IP is known benign service
- `classification` (string): Always "benign" if riot=true
- `name` (string): Service name
- `trust_level` (string): Confidence level
- `category` (string): Service category

**False Positive Filtering:**
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
        path: /riot  # Only alert if NOT a benign service
    - op: is public address
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS

respond:
  - action: report
    name: suspicious-external-connection
```

**Benign Service Identification:**
```yaml
detect:
  event: NETWORK_CONNECTIONS
  op: lookup
  path: event/NETWORK_ACTIVITY/?/IP_ADDRESS
  resource: hive://lookup/greynoise-riot
  metadata_rules:
    op: is
    value: true
    path: /riot

respond:
  - action: report
    name: benign-service-detected
    metadata:
      service_name: '{{ .lookup.name }}'
      category: '{{ .lookup.category }}'
```

## EchoTrail

EchoTrail provides statistical insights on process behavior to identify anomalies.

### Setup

1. Subscribe to EchoTrail add-on in marketplace
2. Add EchoTrail API key in **Organization** → **Integrations**

### Supported Input

- MD5 hash
- SHA256 hash
- Windows filename with extension (e.g., `svchost.exe`)

### Resource Name

```
hive://lookup/echotrail-insights
```

### API Response Format

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
  "children": [
    ["powershell.exe", "80.00"],
    ["cmd.exe", "20.00"]
  ],
  "description": "svchost.exe is a system process...",
  "intel": "It is normal to see multiple instances..."
}
```

### Key Fields

- `rank` (int): Popularity rank (lower = more common, 1-50000+)
- `host_prev` (string): Host prevalence percentage (0.00-100.00)
- `eps` (string): Endpoint prevalence score (0.00-1.00)
- `paths` (array): Common file paths with percentages
- `parents` (array): Common parent processes with percentages
- `children` (array): Common child processes with percentages
- `description` (string): Process description
- `intel` (string): Behavioral intelligence

### Example Rules

**Rare Process Detection:**
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

respond:
  - action: report
    name: rare-process-execution
    metadata:
      file_path: '{{ .event.FILE_PATH }}'
      host_prev: '{{ .lookup.host_prev }}'
      rank: '{{ .lookup.rank }}'
```

**Anomalous Parent-Child Relationship:**
```yaml
detect:
  event: NEW_PROCESS
  op: and
  rules:
    - op: is
      path: event/FILE_PATH
      value: "svchost.exe"
      file name: true
    - op: lookup
      path: event/FILE_PATH
      resource: hive://lookup/echotrail-insights
      metadata_rules:
        op: is greater than
        value: 50000
        path: /rank  # Very rare

respond:
  - action: report
    name: suspicious-svchost-execution
```

**Low Prevalence with Suspicious Behavior:**
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

## IP Geolocation

LimaCharlie provides free IP geolocation using MaxMind GeoLite2 data.

### Setup

**No subscription or API key required** - Available to all users.

### Resource Name

```
hive://lookup/ip-geo
```

### API Response Format

```json
{
  "country": {
    "geoname_id": 2750405,
    "iso_code": "NL",
    "is_in_european_union": true,
    "names": {
      "en": "Netherlands",
      "de": "Niederlande",
      "fr": "Pays-Bas"
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
    "geoname_id": 6255148,
    "names": {
      "en": "Europe"
    }
  },
  "city": {
    "geoname_id": 2759794,
    "names": {
      "en": "Amsterdam"
    }
  },
  "postal": {
    "code": "1012"
  }
}
```

### Key Fields

- `country.iso_code` (string): Two-letter country code
- `country.is_in_european_union` (bool): EU membership status
- `location.latitude` / `longitude` (float): Geographic coordinates
- `location.time_zone` (string): IANA timezone
- `continent.code` (string): Continent code
- `city.names.en` (string): City name

### Example Rules

**Geofencing - Block Sanctioned Countries:**
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
            path: /country/iso_code
          - op: is
            value: "CN"
            path: /country/iso_code
          - op: is
            value: "KP"
            path: /country/iso_code
    - op: is public address
      path: event/NETWORK_ACTIVITY/?/IP_ADDRESS

respond:
  - action: report
    name: connection-to-sanctioned-country
    metadata:
      ip: '{{ index .event.NETWORK_ACTIVITY 0 "IP_ADDRESS" }}'
      country: '{{ .lookup.country.iso_code }}'
  - action: add tag
    tag: geo-alert
    ttl: 86400
```

**EU Data Compliance:**
```yaml
detect:
  event: CONNECTED
  op: lookup
  path: routing/ext_ip
  resource: hive://lookup/ip-geo
  metadata_rules:
    op: is
    value: false
    path: /country/is_in_european_union

respond:
  - action: report
    name: non-eu-connection
```

**Timezone-Based Detection:**
```yaml
detect:
  event: USER_LOGIN
  op: and
  rules:
    - op: lookup
      path: routing/ext_ip
      resource: hive://lookup/ip-geo
      metadata_rules:
        op: contains
        value: "Asia"
        path: /location/time_zone
    - op: is
      path: event/USER_NAME
      value: "administrator"

respond:
  - action: report
    name: suspicious-timezone-admin-login
```

## AlphaMountain

AlphaMountain provides AI-driven domain categorization, popularity, and threat ratings.

### Setup

1. Subscribe to AlphaMountain add-on in marketplace
2. Add AlphaMountain API key in **Organization** → **Integrations**

### Three API Services

#### 1. Category

Returns domain categorization based on AI analysis.

**Resource**: `hive://lookup/alphamountain-category`

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

**Category IDs:**
- `34` - Malware
- `12` - Phishing
- `18` - Spam
- `14` - Adult Content
- (See AlphaMountain documentation for complete list)

**Example:**
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/alphamountain-category
  metadata_rules:
    op: contains
    value: 34  # Malware category
    path: /categories

respond:
  - action: report
    name: malware-domain-category
```

#### 2. Popularity

Returns domain popularity metrics (useful for detecting DGA domains).

**Resource**: `hive://lookup/alphamountain-popularity`

**API Response:**
```json
{
  "api_alphamountain-popularity": {
    "rank": 150000,
    "scope": "domain"
  }
}
```

**Key Fields:**
- `rank` (int): Popularity rank (1 = most popular, higher = less popular)

**DGA Detection:**
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/alphamountain-popularity
  metadata_rules:
    op: is greater than
    value: 100000
    path: /rank  # Low popularity

respond:
  - action: report
    name: unpopular-domain-query
```

#### 3. Threat

Returns threat rating based on AI models and threat intelligence.

**Resource**: `hive://lookup/alphamountain-threat`

**API Response:**
```json
{
  "api_alphamountain-threat": {
    "verdict": "malicious",
    "score": 85,
    "scope": "domain"
  }
}
```

**Key Fields:**
- `verdict` (string): "malicious", "suspicious", "benign"
- `score` (int): Threat score 0-100

**Example:**
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/alphamountain-threat
  metadata_rules:
    op: and
    rules:
      - op: is
        value: "malicious"
        path: /verdict
      - op: is greater than
        value: 70
        path: /score

respond:
  - action: report
    name: high-confidence-threat-domain
  - action: isolate_network
```

## Pangea

Pangea provides multiple security intelligence APIs for domain, file, IP, URL, and user reputation.

### Setup

Add Pangea API key in format: `domain/token`

Example: `aws.us.pangea.cloud/pts_7kb33fyz313372vuu5zg...`

### Five API Services

#### 1. Domain Reputation

**Resource**: `hive://lookup/pangea-domain-reputation`

**API Response:**
```json
{
  "api_pangea-domain-reputation": {
    "category": ["malware"],
    "score": 95,
    "verdict": "malicious"
  }
}
```

**Key Fields:**
- `category` (array): Categories (e.g., "malware", "phishing", "spam")
- `score` (int): Reputation score 0-100
- `verdict` (string): "malicious", "suspicious", "benign", "unknown"

**Example:**
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

respond:
  - action: report
    name: pangea-malicious-domain
```

#### 2. File Reputation

**Resource**: `hive://lookup/pangea-file-reputation`

**API Response:**
```json
{
  "api_pangea-file-reputation": {
    "category": ["malware"],
    "score": 90,
    "verdict": "malicious"
  }
}
```

**Example:**
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

respond:
  - action: report
    name: pangea-suspicious-file
  - action: task
    command: deny_tree <<PARENT>>
```

#### 3. IP Reputation

**Resource**: `hive://lookup/pangea-ip-reputation`

**API Response:**
```json
{
  "api_pangea-ip-reputation": {
    "category": ["scanner"],
    "score": 85,
    "verdict": "malicious"
  }
}
```

**Example:**
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

respond:
  - action: report
    name: pangea-malicious-ip
```

#### 4. URL Reputation

**Resource**: `hive://lookup/pangea-url-reputation`

**API Response:**
```json
{
  "api_pangea-url-reputation": {
    "category": ["phishing"],
    "score": 92,
    "verdict": "malicious"
  }
}
```

**Example:**
```yaml
detect:
  event: HTTP_REQUEST
  op: lookup
  path: event/URL
  resource: hive://lookup/pangea-url-reputation
  metadata_rules:
    op: contains
    value: "phishing"
    path: /category

respond:
  - action: report
    name: pangea-phishing-url
```

#### 5. User Intelligence (Breach Data)

**Resource**: `hive://lookup/pangea-user-reputation`

**API Response:**
```json
{
  "api_pangea-user-reputation": {
    "breaches": [
      {
        "name": "Example Breach 2023",
        "date": "2023-06-15",
        "data_classes": ["email", "password"]
      }
    ],
    "breach_count": 1,
    "verdict": "suspicious"
  }
}
```

**Example:**
```yaml
detect:
  event: USER_LOGIN
  op: lookup
  path: event/USER_NAME
  resource: hive://lookup/pangea-user-reputation
  metadata_rules:
    op: is greater than
    value: 0
    path: /breach_count

respond:
  - action: report
    name: user-in-breach-database
    metadata:
      user: '{{ .event.USER_NAME }}'
      breach_count: '{{ .lookup.breach_count }}'
```

## Binary Library (BinLib)

Build a private library of observed executables for analysis, searching, and threat hunting.

### Setup

1. Subscribe to `ext-reliable-tasking` extension
2. Subscribe to `binlib` extension

### What is BinLib?

BinLib collects and stores binaries observed in your environment, creating your own private "VirusTotal-like" repository.

**Capabilities:**
- Store metadata and binaries from CODE_IDENTITY events
- Search by hash (MD5, SHA1, SHA256)
- Download observed binaries for analysis
- Tag binaries with MITRE ATT&CK techniques
- Run YARA scans across your binary collection
- Historical binary analysis

### BinLib Operations

#### check_hash

Check if a hash exists in your library.

**Request:**
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

Retrieve detailed metadata about a binary.

**Request:**
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

Download the binary file.

**Request:**
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

**WARNING**: Exercise extreme caution when downloading binaries. LimaCharlie does not filter malicious files. Download only to isolated analysis systems.

#### search

Search for binaries by various criteria.

**Request:**
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

**Searchable Fields:**
- `file_name` (string)
- `is_signed` (bool)
- `sig_issuer` (string)
- `sig_subject` (string)
- `imp_hash` (string)

#### yara_scan

Run YARA rules across your binary collection.

**Request:**
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

## Lookup Operator Reference

### Basic Syntax

```yaml
op: lookup
path: <PATH_TO_VALUE>
resource: <RESOURCE_URI>
case sensitive: <true|false>  # Optional, default true
file name: <true|false>       # Optional, extract filename only
sub domain: <SLICE>           # Optional, sub-domain slicing
metadata_rules:               # Optional, for API lookups
  <EVALUATION_RULES>
```

### Parameters

#### path (required)

JSON path to value in event:
- `event/HASH` - Direct field access
- `event/FILE_PATH` - Nested field
- `event/NETWORK_ACTIVITY/?/IP_ADDRESS` - Array with wildcard
- `routing/ext_ip` - Routing metadata

#### resource (required)

URI to lookup resource:
- API: `hive://lookup/vt`
- Custom feed: `hive://lookup/my-feed`

#### case sensitive (optional)

Boolean, default `true`. Set to `false` for case-insensitive matching:
```yaml
op: lookup
path: event/DOMAIN_NAME
resource: hive://lookup/malware-domains
case sensitive: false
```

#### file name (optional)

Boolean, default `false`. Extract filename from path before lookup:
```yaml
op: lookup
path: event/FILE_PATH
file name: true
resource: hive://lookup/malware-filenames
```

Transforms:
- `C:\Users\admin\malware.exe` → `malware.exe`
- `/usr/bin/suspicious` → `suspicious`

#### sub domain (optional)

String, slice notation for domain components:

**Slice Notation:**
- `0:2` - First two components: `aa.bb` from `aa.bb.cc.dd`
- `-1` - Last component: `dd` from `aa.bb.cc.dd`
- `1:` - All starting at 1: `bb.cc.dd` from `aa.bb.cc.dd`
- `-2:` - Last two: `cc.dd` from `aa.bb.cc.dd`
- `:` - Test each component individually

**Example:**
```yaml
op: lookup
path: event/DOMAIN_NAME
sub domain: "-2:"  # Last two components
resource: hive://lookup/malware-domains
```

Transforms:
- `mail.google.com` → `google.com`
- `www.example.co.uk` → `co.uk`

#### metadata_rules (optional)

Evaluation rules for API responses. Uses standard D&R operators.

**Supported Operators:**
- `is`, `is not`
- `is greater than`, `is lower than`
- `contains`, `starts with`, `ends with`
- `matches` (regex)
- `exists`
- `and`, `or`, `not`
- `length of`

**Examples:**

Threshold:
```yaml
metadata_rules:
  op: is greater than
  value: 5
  path: /positives
```

String match:
```yaml
metadata_rules:
  op: is
  value: "malicious"
  path: /verdict
```

Boolean:
```yaml
metadata_rules:
  op: is
  value: true
  path: /seen
```

Array contains:
```yaml
metadata_rules:
  op: contains
  value: 34
  path: /categories
```

Exists:
```yaml
metadata_rules:
  op: exists
  path: /
```

Length check:
```yaml
metadata_rules:
  op: is greater than
  value: 0
  path: /
  length of: true
```

Complex logic:
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

### Response Enrichment

Access lookup results in response actions using template syntax:

**Metadata Access:**
```yaml
respond:
  - action: report
    name: detection-with-intel
    metadata:
      hash: '{{ .event.HASH }}'
      vt_positives: '{{ .lookup.positives }}'
      vt_total: '{{ .lookup.total }}'
      country_code: '{{ .lookup.country.iso_code }}'
```

**Nested Fields:**
```yaml
metadata:
  scanner_result: '{{ .lookup.scans.Microsoft.result }}'
  geo_city: '{{ .lookup.location.names.en }}'
```

## Feed Formats

### Lookup Data Structure

All lookups must be key-value dictionaries:
- **Key**: Indicator (string) - IP, domain, hash, etc.
- **Value**: Metadata (dictionary) - can be empty `{}`

### Format 1: JSON (lookup_data)

Full control with metadata.

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
    "evil.com": {
      "category": "malware",
      "family": "ransomware",
      "severity": "critical",
      "first_seen": "2024-01-01"
    },
    "abc123def456...": {
      "hash_type": "sha256",
      "file_name": "malware.exe",
      "detection_date": "2024-01-15"
    }
  }
}
```

**Usage in D&R:**
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/my-domains
  metadata_rules:
    op: is
    value: "malware"
    path: /category

respond:
  - action: report
    name: malware-domain
    metadata:
      domain: '{{ .event.DOMAIN_NAME }}'
      category: '{{ .lookup.category }}'
      severity: '{{ .lookup.severity }}'
```

### Format 2: Newline (newline_content)

Simple list, one indicator per line. No metadata.

```json
{
  "newline_content": "8.8.8.8\n1.1.1.1\n192.168.1.1\nevil.com\nmalware.exe\nabc123def456..."
}
```

Each indicator automatically gets empty metadata `{}`.

**Usage:**
```yaml
detect:
  event: DNS_REQUEST
  op: lookup
  path: event/DOMAIN_NAME
  resource: hive://lookup/simple-blocklist
  # No metadata_rules needed for simple presence check

respond:
  - action: report
    name: blocklist-match
```

Or with existence check:
```yaml
metadata_rules:
  op: exists
  path: /
```

### Format 3: YAML (yaml_content)

YAML string with indicators and metadata.

```json
{
  "yaml_content": "8.8.8.8:\n  category: dns\n  provider: google\n1.1.1.1:\n  category: dns\n  provider: cloudflare\nevil.com:\n  category: malware\n  severity: high"
}
```

Equivalent to:
```yaml
8.8.8.8:
  category: dns
  provider: google
1.1.1.1:
  category: dns
  provider: cloudflare
evil.com:
  category: malware
  severity: high
```

### Infrastructure as Code Format

```yaml
hives:
  lookup:
    <lookup-name>:
      data:
        lookup_data:
          <indicator1>:
            <metadata>
          <indicator2>:
            <metadata>
      usr_mtd:
        enabled: true
        expiry: 0
        tags:
          - <tag1>
          - <tag2>
        comment: "<description>"
```

**Example:**
```yaml
hives:
  lookup:
    malware-domains:
      data:
        lookup_data:
          evil.com:
            category: malware
            first_seen: "2024-01-01"
            source: "internal-analysis"
          phishing.net:
            category: phishing
            first_seen: "2024-01-15"
            source: "threat-feed"
      usr_mtd:
        enabled: true
        expiry: 0
        tags:
          - malware
          - custom-feed
          - domains
        comment: "Custom malware domain list from internal analysis"
```

## Lookup Manager Configuration

### Pre-configured Lookups

Select from dropdown in web UI or use predefined ARLs:

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
```

### Public URL Lookups

```yaml
- name: custom-feed
  predefined: ""
  format: json
  tags:
    - custom
  arl: "[https,example.com/threat-feeds/malware-ips.json]"
```

### Private Repository Lookups

GitHub ARL format:
```
[github,org-name/repo-name/path/to/feed.json,token,ghp_abc123...]
```

**Example:**
```yaml
- name: private-iocs
  predefined: ""
  format: json
  tags:
    - private
    - iocs
  arl: "[github,myorg/threat-intel/feeds/iocs.json,token,ghp_abc123def456...]"
```

### Complete Configuration Example

```yaml
hives:
  extension_config:
    ext-lookup-manager:
      data:
        lookup_manager_rules:
          # Pre-configured public feed
          - name: alienvault
            predefined: '[https,storage.googleapis.com/lc-lookups-bucket/alienvault-ip-reputation.json]'
            format: json
            tags:
              - alienvault
              - ip-reputation
            arl: ""

          # Public URL feed
          - name: custom-malware-domains
            predefined: ""
            format: json
            tags:
              - domains
              - malware
            arl: "[https,example.com/feeds/malware-domains.json]"

          # Private GitHub feed
          - name: private-iocs
            predefined: ""
            format: json
            tags:
              - private
              - iocs
            arl: "[github,myorg/threat-intel/feeds/iocs.json,token,ghp_...]"
      usr_mtd:
        enabled: true
        expiry: 0
        tags: []
        comment: "Automated threat feed management"
```

## Rate Limiting and Caching

### VirusTotal

**Free Tier**: 4 requests per minute

**Caching**: 3-day global cache
- First lookup triggers API call
- Subsequent lookups within 3 days use cache
- Cache shared globally across all LimaCharlie users
- Reduces API costs significantly

**Best Practices**:
- Use local known-good hash list first
- Implement suppression on hash
- Apply only to unsigned binaries

### GreyNoise

**Rate Limits**: Vary by subscription plan

**Best Practices**:
- Check account settings for current limits
- Use RIOT API for benign service filtering (reduces noise API calls)
- Cache results in custom lookups for frequently-seen IPs

### EchoTrail

**Rate Limits**: Vary by subscription plan

**Best Practices**:
- Apply to suspicious processes only
- Combine with other indicators
- Use for anomaly detection, not every process

### IP Geolocation

**Rate Limits**: None (free service)

**Performance**: Fast, no caching needed

### AlphaMountain

**Rate Limits**: Vary by subscription plan

**Best Practices**:
- Use popularity API for DGA detection
- Combine category + threat APIs for high confidence
- Cache results for known-good domains

### Pangea

**Rate Limits**: Vary by subscription plan

**Best Practices**:
- Check Pangea dashboard for current limits
- Use appropriate API (domain/file/IP/URL/user) for context
- Combine with other sources for validation

## Summary

LimaCharlie provides comprehensive threat intelligence integration through:

1. **7+ API Integrations**: VirusTotal, GreyNoise, EchoTrail, IP Geo, AlphaMountain, Pangea
2. **Flexible Lookup Operator**: Query APIs and feeds with metadata evaluation
3. **Multiple Feed Formats**: JSON, newline, YAML
4. **Automatic Feed Management**: Lookup Manager for sync from public/private sources
5. **Binary Library**: Private repository for file analysis
6. **Response Enrichment**: Access lookup results in detections

**Key Capabilities**:
- Real-time API lookups during detection evaluation
- Custom threat feed creation and management
- Multi-source intelligence correlation
- False positive reduction with benign service filtering
- Cost optimization with caching and suppression
- Infrastructure as Code support

For implementation examples, see [EXAMPLES.md](./EXAMPLES.md).
For troubleshooting, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md).
