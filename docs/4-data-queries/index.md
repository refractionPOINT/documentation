# Query Console

Query and analyze your security telemetry using LimaCharlie Query Language (LCQL).

## Documentation

- [LCQL Examples](lcql-examples.md) - Example queries for common use cases
- [Query Console UI](query-console-ui.md) - Using the web-based query interface
- [Query with CLI](query-cli.md) - Running queries from the command line

---

## Running Queries Programmatically

!!! info "Prerequisites"
    All API examples require an API key with the `insight` permission. See [API Keys](../7-administration/access/api-keys.md) for setup.

### Run an LCQL Query

=== "REST API"

    ```bash
    # Start and end times are unix epoch seconds
    START=$(date -d '1 hour ago' +%s)
    END=$(date +%s)

    curl -s -X POST \
      "https://search.limacharlie.io/v1/search" \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/json" \
      -d '{
        "oid": "YOUR_OID",
        "query": "event.FILE_PATH ends with .exe",
        "startTime": "'"$START"'",
        "endTime": "'"$END"'",
        "stream": "event"
      }'
    ```

=== "Python"

    ```python
    import time
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.search import Search

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)

    end = int(time.time())
    start = end - 3600  # 1 hour ago

    for result in Search(org).execute(
        query="event.FILE_PATH ends with .exe",
        start_time=start,
        end_time=end,
        stream="event",
        limit=100,
    ):
        print(result)
    ```

=== "Go"

    ```go
    package main

    import (
        "fmt"
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)

        resp, _ := org.Query(limacharlie.QueryRequest{
            Query:      "-1h | * | * | event.FILE_PATH ends with '.exe'",
            Stream:     "event",
            LimitEvent: 1000,
        })
        for _, r := range resp.Results {
            fmt.Println(r)
        }
    }
    ```

=== "CLI"

    ```bash
    START=$(date -d '1 hour ago' +%s)
    END=$(date +%s)

    limacharlie search run \
      --query "event.FILE_PATH ends with .exe" \
      --start "$START" \
      --end "$END" \
      --stream event \
      --limit 100
    ```

### Validate Query Syntax

=== "REST API"

    ```bash
    curl -s -X POST \
      "https://search.limacharlie.io/v1/search/validate" \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/json" \
      -d '{
        "oid": "YOUR_OID",
        "query": "event.FILE_PATH ends with .exe",
        "startTime": "'"$(date -d '1 hour ago' +%s)"'",
        "endTime": "'"$(date +%s)"'"
      }'
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.search import Search

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    result = Search(org).validate("event.FILE_PATH ends with .exe")
    print(result)
    ```

=== "Go"

    There is no dedicated Go SDK method for query validation. Use the REST API directly.

=== "CLI"

    ```bash
    limacharlie search validate \
      --query "event.FILE_PATH ends with .exe"
    ```

### Estimate Query Cost

=== "REST API"

    ```bash
    START=$(date -d '1 hour ago' +%s)
    END=$(date +%s)

    curl -s -X POST \
      "https://search.limacharlie.io/v1/search/validate" \
      -H "Authorization: Bearer $LC_JWT" \
      -H "Content-Type: application/json" \
      -d '{
        "oid": "YOUR_OID",
        "query": "event.FILE_PATH ends with .exe",
        "startTime": "'"$START"'",
        "endTime": "'"$END"'"
      }'
    ```

=== "Python"

    ```python
    import time
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.search import Search

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)

    end = int(time.time())
    start = end - 3600

    result = Search(org).estimate(
        query="event.FILE_PATH ends with .exe",
        start_time=start,
        end_time=end,
    )
    print(result)
    ```

=== "Go"

    There is no dedicated Go SDK method for query cost estimation. Use the REST API directly.

=== "CLI"

    ```bash
    START=$(date -d '1 hour ago' +%s)
    END=$(date +%s)

    limacharlie search estimate \
      --query "event.FILE_PATH ends with .exe" \
      --start "$START" \
      --end "$END"
    ```

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
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    queries = Hive(org, "query").list()
    print(queries)
    ```

=== "Go"

    ```go
    package main

    import (
        "fmt"
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        hive := limacharlie.NewHiveClient(org)
        queries, _ := hive.List(limacharlie.HiveArgs{
            HiveName:     "query",
            PartitionKey: "YOUR_OID",
        })
        fmt.Println(queries)
    }
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
      -d data='{"query": "event.FILE_PATH ends with .exe", "stream": "event"}' \
      -d usr_mtd='{"enabled": true}'
    ```

=== "Python"

    ```python
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive, HiveRecord

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    Hive(org, "query").set(HiveRecord(
        name="my-saved-query",
        data={
            "query": "event.FILE_PATH ends with .exe",
            "stream": "event",
        },
        enabled=True,
    ))
    ```

=== "Go"

    ```go
    package main

    import (
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        hive := limacharlie.NewHiveClient(org)
        enabled := true
        hive.Add(limacharlie.HiveArgs{
            HiveName:     "query",
            PartitionKey: "YOUR_OID",
            Key:          "my-saved-query",
            Data: limacharlie.Dict{
                "query":  "event.FILE_PATH ends with .exe",
                "stream": "event",
            },
            Enabled: &enabled,
        })
    }
    ```

=== "CLI"

    ```bash
    limacharlie search saved-create \
      --name my-saved-query \
      --input-file query.yaml
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
    import time
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive
    from limacharlie.sdk.search import Search

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)

    saved = Hive(org, "query").get("my-saved-query")
    end = int(time.time())
    start = end - 3600

    for result in Search(org).execute(
        query=saved.data["query"],
        start_time=start,
        end_time=end,
        stream=saved.data.get("stream", "event"),
    ):
        print(result)
    ```

=== "Go"

    ```go
    package main

    import (
        "fmt"
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        hive := limacharlie.NewHiveClient(org)

        saved, _ := hive.Get(limacharlie.HiveArgs{
            HiveName:     "query",
            PartitionKey: "YOUR_OID",
            Key:          "my-saved-query",
        })
        query := saved.Data["query"].(string)

        resp, _ := org.Query(limacharlie.QueryRequest{
            Query:  query,
            Stream: "event",
        })
        for _, r := range resp.Results {
            fmt.Println(r)
        }
    }
    ```

=== "CLI"

    ```bash
    limacharlie search saved-run \
      --name my-saved-query \
      --start "$(date -d '1 hour ago' +%s)" \
      --end "$(date +%s)"
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
    from limacharlie.client import Client
    from limacharlie.sdk.organization import Organization
    from limacharlie.sdk.hive import Hive

    client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
    org = Organization(client)
    Hive(org, "query").delete("my-saved-query")
    ```

=== "Go"

    ```go
    package main

    import (
        limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
    )

    func main() {
        client, _ := limacharlie.NewClient(limacharlie.ClientOptions{
            OID:    "YOUR_OID",
            APIKey: "YOUR_API_KEY",
        })
        org := limacharlie.NewOrganization(client)
        hive := limacharlie.NewHiveClient(org)
        hive.Remove(limacharlie.HiveArgs{
            HiveName:     "query",
            PartitionKey: "YOUR_OID",
            Key:          "my-saved-query",
        })
    }
    ```

=== "CLI"

    ```bash
    limacharlie search saved-delete --name my-saved-query
    ```

---

## See Also

- [LCQL Examples](lcql-examples.md)
- [Query Console UI](query-console-ui.md)
- [D&R Rules](../3-detection-response/index.md)
