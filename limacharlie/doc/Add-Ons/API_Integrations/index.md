# API Integrations

Connect LimaCharlie to external threat intelligence, enrichment, and security services.

## Overview

API Integrations enable you to leverage third-party services directly within your detection rules and response actions.

## Available Integrations

### Threat Intelligence
- [VirusTotal](api-integrations-virustotal.md) - File and URL reputation
- [Hybrid Analysis](api-integrations-hybrid-analysis.md) - Malware sandbox analysis
- [AlphaMountain](api-integrations-alphamountain.md) - Threat intelligence

### IP & Network Analysis
- [GreyNoise](api-integrations-greynoise.md) - IP reputation and internet scanning context
- [IP Geolocation](api-integrations-ip-geolocation.md) - Geographic IP information

### Security Services
- [EchoTrail](api-integrations-echotrail.md) - Process reputation and insights
- [Pangea](api-integrations-pangea.md) - Security services

## Using Integrations

API integrations can be used in detection rules for real-time enrichment:

```yaml
# Detection
op: is
event: NEW_PROCESS
path: event/FILE_PATH
value: suspicious.exe

# Response
- action: service request
  name: virustotal
  task: hash
```

## Configuration

1. Navigate to Add-Ons in the web console
2. Select the desired API integration
3. Configure API credentials
4. Set usage limits and quotas (optional)
5. Test the integration
6. Use in detection rules
