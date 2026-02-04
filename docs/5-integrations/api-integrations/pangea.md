# Pangea

Pangea is a collection of API-based security services that can quickly be added to enrich data. Pangea is designed make it easy to add security into an application, but also perform lookups for various data types.

LimaCharlie supports the following Pangea lookups:

* [Domain](https://pangea.cloud/docs/api/domain-intel#reputation)
  + Check malicious behavior on a domain
* [File](https://pangea.cloud/docs/api/file-intel#reputation)
  + Check for malicious behavior on a file
* [IP](https://pangea.cloud/docs/api/ip-intel#reputation)
  + Check for malicious behavior on an IP
* [URL](https://pangea.cloud/docs/api/url-intel#reputation)
  + Retrieve an intelligence report
* [User](https://pangea.cloud/docs/user-intel/)
  + Checks to see if any PII data or credentials have been exposed by an attack.

## API Keys

> Subscription Required
>
> A Pangea subscription is required to utilize this service. Pangea offers a $5 monthly credit for development purposes, provided the account balance is not negative.

The Pangea API key (known as a token within the Pangea platform) is added via the integrations menu within LimaCharlie.

The API key follows this format:

```
domain/token
```

Example:

```
aws.us.pangea.cloud/pts_7kb33fyz313372vuu5zgnotarealtoken
```

## Domain

The Domain Intel service allows you to retrieve intelligence about known domain names, giving you insight into the reputation of a domain.

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

The File Intel service enables you to submit a file's hash and get the file's attributes back - giving you insight into the disposition of the file.

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

The IP Intel service allows you to retrieve security information about known IP addresses that have been collected across the internet for several decades, giving you insight into the reputation of an IP.

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

The URL Intel service allows you to retrieve intelligence about known URLs, giving you insight into the reputation of a URL.

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

The User Intel service allows you to check a large repository of breach data to see if a user's Personally Identifiable Data (PII) or credentials have been compromised.

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
