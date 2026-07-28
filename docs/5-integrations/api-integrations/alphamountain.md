# alphaMountain

There are [three alphaMountain API integrations](https://app.limacharlie.io/add-ons/category/api). You subscribe to each one with the correct API key. After you enable and configure an integration, you can use the alphaMountain resource as an API lookup.

## alphaMountain Category

Returns the category of an Internet URI. alphaMountain generates the category with its own statistical and neural network models. For more about the categories, see the [alphaMountain web protection categories](https://alphamountain.freshdesk.com/support/solutions/articles/66000280079-a9-web-protection-categories-grouped-).

### alphaMountain Popularity

Returns the popularity of a domain. alphaMountain measures the popularity with a combination of page-rank, daily traffic bandwidth, the total number of requests, and passive DNS activity for the hostname. For more information, see the [alphaMountain domain popularity API](https://www.alphamountain.ai/api/#tag/Domain/paths/~1popularity~1domain/post).

#### alphaMountain Threat

Returns threat ratings for Internet URIs. alphaMountain generates the ratings with its own statistical and neural network models, and cross-validates them with other sources when applicable. For more information, see the [alphaMountain threat intelligence feeds API](https://www.alphamountain.ai/threat-intelligence-feeds-api/).

## Detection & Response Rule

This example rule takes the domain name from a DNS_REQUEST event. It then does a lookup with the alphaMountain category API.

```yaml
event: DNS_REQUEST
op: lookup
path: event/DOMAIN_NAME
resource: lcr://api/alphamountain-category
```

The returned data is in JSON format. It includes the API response and a threatYeti URL that LimaCharlie adds. For example:

```json
{
  "api_alphamountain-category": {
    "categories": [
      34
    ],
    "confidence": 0.90371,
    "scope": "domain",
    "threatyeti_url": "https://www.threatyeti.com/search?q=logging-alv.googleapis.com"
  }
}
```
