# Query Console

Query and analyze your security telemetry using LimaCharlie Query Language (LCQL).

## Overview

The Query Console enables you to:

- Search historical telemetry
- Analyze security events
- Investigate incidents
- Build detection logic
- Export query results

## LimaCharlie Query Language (LCQL)

LCQL is a powerful query language designed for security data:

```sql
SELECT *
FROM events
WHERE event.EVENT_TYPE = 'NEW_PROCESS'
  AND event.FILE_PATH LIKE '%powershell%'
LIMIT 100
```

## Key Features

- SQL-like syntax familiar to analysts
- Filter by event type, time range, sensor tags
- Join data from multiple sources
- Aggregate and group results
- Export to CSV or JSON

## Query Examples

### Process Creation Events
```sql
SELECT event.TIMESTAMP, event.COMMAND_LINE
FROM events
WHERE event.EVENT_TYPE = 'NEW_PROCESS'
  AND routing.tags CONTAINS 'production'
```

### Network Connections
```sql
SELECT event.IP_ADDRESS, event.PORT, COUNT(*) as conn_count
FROM events
WHERE event.EVENT_TYPE = 'NETWORK_CONNECTIONS'
GROUP BY event.IP_ADDRESS, event.PORT
ORDER BY conn_count DESC
```

## Resources

- [Query with CLI](query-with-cli.md) - Use LCQL from the command line
- [Web Console](https://app.limacharlie.io) - Interactive query interface
- API access for programmatic queries
