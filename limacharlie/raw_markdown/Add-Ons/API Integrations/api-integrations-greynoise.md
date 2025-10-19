# GreyNoise

GreyNoise collects, analyzes, and labels data on IP addresses that scan the Internet and often saturate security tools with noise. By querying IP addresses against GreyNoise, teams can spend less time on irrelevant or harmless activity and focus on targeted and/or emerging threats.

LimaCharlie offers integrations with two GreyNoise API lookups:

  * [IP Context](https://docs.greynoise.io/reference/noisecontextip-1)

    * Get more information about a given IP address. Returns time ranges, IP metadata (network owner, ASN, reverse DNS pointer, country), associated actors, activity tags, and raw port scan and web request information.

  * [RIOT IP Lookups](https://docs.greynoise.io/reference/riotip)

    * RIOT identifies IPs from known benign services and organizations that commonly cause false positives in network security and threat intelligence products. The collection of IPs in RIOT is continually curated and verified to provide accurate results.

## IP Context


    {
      "api_greynoise-noise-context": {
        "ip": "35.184.178.65",
        "seen": false
      }
    }


## RIOT IP Lookup


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
