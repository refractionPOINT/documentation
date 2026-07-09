# Query Console

Query and analyze your security telemetry using LimaCharlie Query Language (LCQL).

## Documentation

- [LCQL Examples](lcql-examples.md) - Example queries for common use cases
- [Query Console UI](query-console-ui.md) - Using the web-based query interface
- [Query with CLI](query-cli.md) - Running queries from the command line
- [Query Limits & Performance](query-limits-and-performance.md) - Concurrency and timeout limits, and how to write efficient queries

---

## Running Queries Programmatically

!!! info "Prerequisites"
    All API examples require an API key with the `insight` permission. See [API Keys](../7-administration/access/api-keys.md) for setup.

### Search API Endpoint

There is no single search hostname. Each organization's search endpoint lives in the datacenter for the region where the organization was created, so you discover it from the API first and then send queries to that host. The Python SDK, Go SDK, and CLI do this automatically.

=== "REST API"

    ```bash
    # Returns a bare hostname such as 9157798c50af372c.replay-search.limacharlie.io
    SEARCH_HOST=$(curl -s "https://api.limacharlie.io/v1/orgs/YOUR_OID/url" \
      -H "Authorization: Bearer $LC_JWT" | jq -r '.url.search')
    ```

=== "Python"

    The Python SDK resolves the search endpoint automatically from your OID; no manual step is required.

=== "CLI"

    The CLI resolves the search endpoint automatically from your OID; no manual step is required.

The bootstrap API host `https://api.limacharlie.io` is the same for every region and routes to the correct datacenter based on your OID. The REST examples below reuse the `$SEARCH_HOST` variable for the discovered hostname. For reference, the current production search endpoints per region are:

| Region | Search endpoint |
|--------|-----------------|
| USA | `https://9157798c50af372c.replay-search.limacharlie.io` |
| Europe | `https://b76093c3662d5b4f.replay-search.limacharlie.io` |
| Canada | `https://aae67d7e76570ec1.replay-search.limacharlie.io` |
| UK | `https://70182cf634c346bd.replay-search.limacharlie.io` |
| Australia | `https://abc32764762fce67.replay-search.limacharlie.io` |
| India | `https://4d897015b0815621.replay-search.limacharlie.io` |

!!! tip "Use the bootstrap API, not a direct endpoint"
    Discovering your search endpoint through the bootstrap API (`https://api.limacharlie.io/v1/orgs/{oid}/url`, the `url.search` field) is the recommended approach. The direct per-region hostnames above can change over time, whereas the bootstrap API always returns the current endpoint for your organization. Treat the table as a convenience reference only, and do not hardcode a direct endpoint.

### Run an LCQL Query

=== "REST API"

    ```bash
    # Start and end times are unix epoch seconds
    START=$(date -d '1 hour ago' +%s)
    END=$(date +%s)

    # Discover your org's search endpoint (see "Search API Endpoint" above)
    SEARCH_HOST=$(curl -s "https://api.limacharlie.io/v1/orgs/YOUR_OID/url" \
      -H "Authorization: Bearer $LC_JWT" | jq -r '.url.search')

    curl -s -X POST \
      "https://$SEARCH_HOST/v1/search" \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/json" \
      -d '{
        "oid": "YOUR_OID",
        "query": "event/FILE_PATH ends with .exe",
        "startTime": "'"$START"'",
        "endTime": "'"$END"'",
        "stream": "event"
      }'
    ```

=== "Python"

    ```python
    --8<-- "snippets/python/run.py"
    ```

=== "Go"

    ```go
    --8<-- "snippets/golang/run/main.go"
    ```

=== "CLI"

    ```bash
    START=$(date -d '1 hour ago' +%s)
    END=$(date +%s)

    limacharlie search run \
      --query "event/FILE_PATH ends with .exe" \
      --start "$START" \
      --end "$END" \
      --stream event \
      --limit 100
    ```

### Validate Query Syntax

=== "REST API"

    ```bash
    curl -s -X POST \
      "https://$SEARCH_HOST/v1/search/validate" \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/json" \
      -d '{
        "oid": "YOUR_OID",
        "query": "event/FILE_PATH ends with .exe",
        "startTime": "'"$(date -d '1 hour ago' +%s)"'",
        "endTime": "'"$(date +%s)"'"
      }'
    ```

=== "Python"

    ```python
    --8<-- "snippets/python/validate.py"
    ```

=== "Go"

    ```go
    --8<-- "snippets/golang/validate/main.go"
    ```

=== "CLI"

    ```bash
    limacharlie search validate \
      --query "event/FILE_PATH ends with .exe"
    ```

### Estimate Query Cost

=== "REST API"

    ```bash
    START=$(date -d '1 hour ago' +%s)
    END=$(date +%s)

    curl -s -X POST \
      "https://$SEARCH_HOST/v1/search/validate" \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/json" \
      -d '{
        "oid": "YOUR_OID",
        "query": "event/FILE_PATH ends with .exe",
        "startTime": "'"$START"'",
        "endTime": "'"$END"'"
      }'
    ```

=== "Python"

    ```python
    --8<-- "snippets/python/estimate.py"
    ```

=== "Go"

    ```go
    --8<-- "snippets/golang/estimate/main.go"
    ```

=== "CLI"

    ```bash
    START=$(date -d '1 hour ago' +%s)
    END=$(date +%s)

    limacharlie search estimate \
      --query "event/FILE_PATH ends with .exe" \
      --start "$START" \
      --end "$END"
    ```

!!! note
    The validate response also includes query-size fields (`batchesInScope`, `eventsInScope`, `bytesInScope`) and a running search returns per-page progress and actual billing. See [Query Progress and Cost Reporting](query-limits-and-performance.md#query-progress-and-cost-reporting) for how to build a progress bar and read the real cost.

### Saved Queries

#### List Saved Queries

=== "REST API"

    ```bash
    curl -s -X GET \
      "https://api.limacharlie.io/v1/hive/query/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    --8<-- "snippets/python/saved_list.py"
    ```

=== "Go"

    ```go
    --8<-- "snippets/golang/saved_list/main.go"
    ```

=== "CLI"

    ```bash
    limacharlie search saved-list
    ```

#### Create Saved Query

=== "REST API"

    ```bash
    curl -s -X POST \
      "https://api.limacharlie.io/v1/hive/query/YOUR_OID/my-saved-query/data" \
      -H "Authorization: Bearer $LC_JWT" \
      -d data='{"query": "event/FILE_PATH ends with .exe", "stream": "event"}' \
      -d usr_mtd='{"enabled": true}'
    ```

=== "Python"

    ```python
    --8<-- "snippets/python/saved_create.py"
    ```

=== "Go"

    ```go
    --8<-- "snippets/golang/saved_create/main.go"
    ```

=== "CLI"

    ```bash
    limacharlie search saved-create \
      --name my-saved-query \
      --query "event/FILE_PATH ends with .exe" \
      --stream event
    ```

#### Run Saved Query

=== "REST API"

    ```bash
    START=$(date -d '1 hour ago' +%s)
    END=$(date +%s)

    # First retrieve the saved query definition
    curl -s -X GET \
      "https://api.limacharlie.io/v1/hive/query/YOUR_OID/my-saved-query/data" \
      -H "Authorization: Bearer $LC_JWT"

    # Then execute with the query string from the saved definition
    ```

=== "Python"

    ```python
    --8<-- "snippets/python/saved_run.py"
    ```

=== "Go"

    ```go
    --8<-- "snippets/golang/saved_run/main.go"
    ```

=== "CLI"

    ```bash
    limacharlie search saved-run --name my-saved-query
    ```

#### Delete Saved Query

=== "REST API"

    ```bash
    curl -s -X DELETE \
      "https://api.limacharlie.io/v1/hive/query/YOUR_OID/my-saved-query" \
      -H "Authorization: Bearer $LC_JWT"
    ```

=== "Python"

    ```python
    --8<-- "snippets/python/saved_delete.py"
    ```

=== "Go"

    ```go
    --8<-- "snippets/golang/saved_delete/main.go"
    ```

=== "CLI"

    ```bash
    limacharlie search saved-delete --name my-saved-query
    ```

---

## See Also

- [LCQL Examples](lcql-examples.md)
- [Query Console UI](query-console-ui.md)
- [Query Limits & Performance](query-limits-and-performance.md)
- [D&R Rules](../3-detection-response/index.md)
