# Config Hive

The Config Hive is LimaCharlie's hierarchical configuration store. It provides a centralized way to manage configurations that can be referenced across the platform.

## Hive Types

- [D&R Rules](dr-rules.md) - Detection and response rule storage
- [Lookups](lookups.md) - Key-value lookup tables for enrichment
- [Secrets](secrets.md) - Secure credential management
- [YARA](yara.md) - YARA rule storage and management
- [Cloud Sensors](cloud-sensors.md) - Cloud sensor configurations
- [Application Control Policies](app-control-policy.md) - Which sensors Application Control covers, and in which mode
- [Application Control Rules](app-control-rule.md) - Allow and deny rules for Application Control
- [Apps](apps.md) - User-authored, AI-generated mini web applications
- [SOPs](../../9-ai-sessions/sops.md) - Standard Operating Procedures that AI agents read and follow
- [Organization Notes](../../9-ai-sessions/org-notes.md) - Free-form reference documents about the organization, read by analysts and AI agents

## Restricting Records

Tag a record `acl:<scope>` to restrict its `data` to members of that scope. Other users still see the record's name and metadata. See [Resource ACLs](../access/resource-acls.md).

## Usage

Hive records can be:

- Referenced in D&R rules using the `hive://` prefix
- Managed via the web interface, CLI, or API
- Version controlled using the Git Sync extension

!!! warning "New records are disabled by default"
    Every new Hive record — D&R rules, FP rules, secrets, lookups, YARA sources, cloud sensors, AI skills, playbooks, etc. — is created **disabled** unless the request explicitly sets `usr_mtd.enabled: true`. A disabled record is stored normally but is skipped by every consumer that respects the flag (rules don't fire, lookups aren't queried, AI skills aren't enumerated). When debugging "the record exists but nothing happens", check `usr_mtd.enabled` first.

    Enable a record at creation time by either:

    1. Passing `--enabled` on the CLI `set` command (e.g. `limacharlie secret set --key … --input-file … --enabled`).
    2. Including `usr_mtd.enabled: true` in the request body / input file.
    3. Setting `enabled=True` (Python SDK) or `Enabled: &enabled` (Go SDK) on the record before calling `set` / `Add`.

    Or call the matching `enable` subcommand after creation (`limacharlie <hive> enable --key …`).

## Listing Records

`GET /v1/hive/{hive}/{oid}` lists the records of a hive. `{hive}` is the hive name (for example `dr-general`, `lookup` or `secret`) and `{oid}` is your organization ID.

Without any parameter, the call returns the whole hive as one map of record name to record. Add `limit` or `cursor` to read it one page at a time instead.

| Parameter | Description |
|-----------|-------------|
| `limit` | Page size. Sending `limit` or `cursor` selects the paged response. Default `50`, maximum `500`. |
| `cursor` | The `next_cursor` of the previous page. Omit it for the first page. |
| `mtd_only` | `true` returns metadata only: the record `data` is not loaded or returned. It works with or without paging. |
| `tag_prefix` | Only return records with at least one tag starting with this prefix. |
| `max_bytes` | Paged form only. Soft cap on the size of a page, in bytes. A page stops before exceeding it but always holds at least one record. The server applies its own default and maximum. |

A paged response has this shape:

```json
{
  "records": {
    "record-a": { "data": {}, "usr_mtd": {}, "sys_mtd": {} },
    "record-b": { "data": {}, "usr_mtd": {}, "sys_mtd": {} }
  },
  "next_cursor": "opaque-cursor"
}
```

Records come in record name order. `next_cursor` is empty on the last page. A page can hold fewer records than `limit`, because a page is also bounded by size, so always continue until `next_cursor` is empty rather than stopping at a short page. With `mtd_only=true`, records have no `data`.

### Page Through a Hive

=== "REST API"

    ```bash
    OID=YOUR_OID
    CURSOR=""
    while :; do
      PAGE=$(curl -s -G "https://api.limacharlie.io/v1/hive/lookup/$OID" \
        -H "Authorization: Bearer $LC_JWT" \
        --data-urlencode "limit=100" \
        --data-urlencode "cursor=$CURSOR")
      echo "$PAGE" | jq -r '.records | keys[]'
      CURSOR=$(echo "$PAGE" | jq -r '.next_cursor')
      [ -z "$CURSOR" ] && break
    done
    ```

=== "Python"

    ```python
    --8<-- "snippets/python/hive_pages.py"
    ```

=== "Go"

    ```go
    --8<-- "snippets/golang/hive_pages/main.go"
    ```

### List Names Only

Metadata-only listing returns each record's name, tags, enabled state and system metadata without loading its data. It is much cheaper than a full listing, and the right way to get an index of a large hive.

=== "REST API"

    ```bash
    curl -s -G "https://api.limacharlie.io/v1/hive/lookup/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT" \
      --data-urlencode "mtd_only=true" | jq -r 'keys[]'
    ```

=== "Python"

    ```python
    --8<-- "snippets/python/hive_names.py"
    ```

=== "Go"

    ```go
    --8<-- "snippets/golang/hive_names/main.go"
    ```

=== "CLI"

    ```bash
    limacharlie hive list --hive-name lookup --metadata-only
    ```

    The `list` command of every hive shortcut (`secret`, `lookup`, `playbook`, `fp`, `sop`, ...) and `limacharlie dr list` accept `--metadata-only` too.

### Large Hives

A whole-hive listing (no `limit` or `cursor`) has a size limit. A hive whose stored records add up to more than about 8 MiB is refused with HTTP `413` and the error code `HIVE_LISTING_TOO_LARGE`. The limit applies to the stored, compressed size, so the JSON you would receive is considerably larger. A metadata-only whole-hive listing is refused the same way past roughly 100,000 records. The exact limits are server settings and can change.

Retrying the same request does not help. Do one of these instead:

- Page through the hive with `limit` and `cursor`. Each page is bounded in size, whatever the hive holds.
- Use `mtd_only=true` if you only need names and metadata, then fetch the records you need one by one.

The Python and Go SDKs and the `limacharlie` CLI do this for you. See the [Python SDK](../../6-developer-guide/sdks/python-sdk.md#hive-operations) and the [Go SDK](../../6-developer-guide/sdks/go-sdk.md#list-hive-records) pages.

### Errors

| Status | Error code | Meaning |
|--------|------------|---------|
| `400` | `INVALID_CURSOR` | The `cursor` is not one returned by a previous page of this listing. Restart from the first page. |
| `400` | none | `limit` or `max_bytes` is not a positive integer, or `mtd_only` is not `true` or `false`. |
| `413` | `HIVE_LISTING_TOO_LARGE` | A whole-hive listing is over the size limit. Page through the hive or use `mtd_only=true`. Not retriable. |
| `504` | none | The hive did not answer in time. Retry a paged call shortly. For a whole-hive listing, page or use `mtd_only=true` instead of retrying. |

---

## See Also

- [D&R Rules](dr-rules.md)
- [Secrets Manager](secrets.md)
- [Lookups](lookups.md)
- [Application Control Policies](app-control-policy.md)
- [Application Control Rules](app-control-rule.md)
