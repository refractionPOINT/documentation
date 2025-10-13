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

The Pangea API key (known as a token within the Pangea platform) is added via the [integrations](/v2/docs/add-ons-api-integrations#configuration) menu within LimaCharlie.

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

```
event: DNS_REQUEST
op: lookup
path: event/DOMAIN_NAME
resource: hive://lookup/pangea-domain-reputation
```

### API Response Data

```
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

```
event: NEW_PROCESS
op: lookup
path: event/HASH
resource: hive://lookup/pangea-file-reputation
```

### API Response Data

```
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

```
event: DNS_REQUEST
op: lookup
path: routing/ext_ip
resource: hive://lookup/pangea-ip-reputation
```

### API Response Data

```
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

```
event: DNS_REQUEST
op: lookup
path: author
resource: hive://lookup/pangea-user-reputation
```

### API Response Data

## User

The User Intel service allows you to check a large repository of breach data to see if a user’s Personally Identifiable Data (PII) or credentials have been compromised.

### D&R Rule

```
event: DNS_REQUEST
op: lookup
path: author
resource: hive://lookup/pangea-user-reputation
```
