# Pangea

Pangea is a collection of API-based security services that you can add to enrich data. Pangea helps you add security to an application, and also do lookups for many data types.

LimaCharlie supports these Pangea lookups:

- [Domain](https://pangea.cloud/docs/api/domain-intel#reputation)
  - Check malicious behavior on a domain
- [File](https://pangea.cloud/docs/api/file-intel#reputation)
  - Check for malicious behavior on a file
- [IP](https://pangea.cloud/docs/api/ip-intel#reputation)
  - Check for malicious behavior on an IP
- [URL](https://pangea.cloud/docs/api/url-intel#reputation)
  - Get an intelligence report
- [User](https://pangea.cloud/docs/user-intel/)
  - Check if an attack exposed PII data or credentials.

## API Keys

> Subscription Required
>
> You need a Pangea subscription to use this service. Pangea gives a $5 monthly credit for development if the account balance is not negative.

Add the Pangea API key (Pangea calls it a token) in the integrations menu in LimaCharlie.

The API key has this format:

```text
domain/token
```

Example:

```text
aws.us.pangea.cloud/pts_7kb33fyz313372vuu5zgnotarealtoken
```

## Domain

The Domain Intel service gets intelligence about known domain names. It shows you the reputation of a domain.

### Rule

```yaml
event: DNS_REQUEST
op: lookup
path: event/DOMAIN_NAME
resource: lcr://api/pangea-domain-reputation
```

### API Response Data

```json
{
  "api_pangea-domain-reputation": {
    "category": [
      "zerolist"
    ],
    "score": 0,
    "verdict": "benign"
  }
}
```

## File Reputation

The File Intel service lets you submit the hash of a file and get the attributes of the file. It shows you the disposition of the file.

### D&R Rule

```yaml
event: NEW_PROCESS
op: lookup
path: event/HASH
resource: lcr://api/pangea-file-reputation
```

### API Response Data

```json
{
  "api_pangea-file-reputation": {
    "category": [
      ""
    ],
    "score": 0,
    "verdict": "benign"
  }
}
```

## IP Reputation

The IP Intel service gets security information about known IP addresses. Pangea collected this information across the internet for several decades. The service shows you the reputation of an IP.

### D&R Rule

```yaml
event: DNS_REQUEST
op: lookup
path: routing/ext_ip
resource: lcr://api/pangea-ip-reputation
```

### API Response Data

```json
{
  "api_pangea-ip-reputation": {
    "category": [],
    "score": -1,
    "verdict": "unknown"
  }
}
```

## URL Reputation

The URL Intel service gets intelligence about known URLs. It shows you the reputation of a URL.

### D&R Rule

```yaml
event: HTTP_REQUEST
op: lookup
path: event/URL
resource: lcr://api/pangea-url-reputation
```

### API Response Data

```json
{
  "api_pangea-url-reputation": {
    "category": [],
    "score": 0,
    "verdict": "benign"
  }
}
```

## User

The User Intel service checks a large repository of breach data. It shows you if an attacker compromised the Personally Identifiable Data (PII) or the credentials of a user.

### D&R Rule

```yaml
event: USER_OBSERVED
op: lookup
path: event/USER_NAME
resource: lcr://api/pangea-user-reputation
```

### API Response Data

```json
{
  "api_pangea-user-reputation": {
    "breach_count": 0,
    "found_in_breach": false
  }
}
```
