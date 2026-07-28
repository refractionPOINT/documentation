# GreyNoise

GreyNoise collects, analyzes, and labels data on IP addresses that scan the Internet. These IP addresses often saturate security tools with noise. When you query IP addresses against GreyNoise, your team spends less time on irrelevant or harmless activity. The team can then focus on targeted threats and new threats.

LimaCharlie has integrations with two GreyNoise API lookups:

- [IP Context](https://docs.greynoise.io/reference/noisecontextip-1)

  - Gets more information about an IP address. Returns time ranges, IP metadata (network owner, ASN, reverse DNS pointer, country), associated actors, activity tags, and raw data about port scans and web requests.
- [RIOT IP Lookups](https://docs.greynoise.io/reference/riotip)

  - RIOT identifies IPs from known benign services and companies. These IPs often cause false positives in products for network security and threat intelligence. The collection of IPs in RIOT is continually curated and verified for accurate results.

## IP Context

```json
{
  "api_greynoise-noise-context": {
    "ip": "35.184.178.65",
    "seen": false
  }
}
```

## RIOT IP Lookup

```json
{
  "ip": "8.8.8.8",
  "noise": false,
  "riot": true,
  "classification": "benign",
  "name": "Google Public DNS",
  "link": "https://viz.greynoise.io/riot/8.8.8.8",
  "last_seen": "2023-08-02",
  "message": "Success"
}
```
