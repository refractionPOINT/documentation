# FAQ - Large and Incomplete Results

Some lists are too big to return in one answer, and some answers are built from several [Config Hives](../../7-administration/config-hive/index.md) of which one could not be read. LimaCharlie then refuses to hand you a result that looks complete but is not, and tells you why. This page is keyed by what you see: an error code, an HTTP status, a message in the web app or a message in the CLI. Each entry says what it means, why it happens and what to do.

## Quick Reference

| You see | Where | What to do |
|---------|-------|------------|
| [`HIVE_LISTING_TOO_LARGE`](#hive_listing_too_large), HTTP `413` | API, CLI, SDKs | Page through the hive with `limit` and `cursor`, or list names only with `mtd_only=true`. |
| [`INVALID_CURSOR`](#invalid_cursor), HTTP `400` | API, CLI, SDKs | Pass `next_cursor` back unchanged, or start again without a cursor. |
| [`INCOMPLETE_RESULT`](#incomplete_result), HTTP `503` | Stories, access-control resources | Retry. Or accept the partial result with `allow_partial=true`. |
| [`INCOMPLETE_RESULT`](#incomplete_result), HTTP `413` | Stories, access-control resources | Retrying does not help. Reduce the records in the named hives, or accept the partial result with `allow_partial=true`. |
| [`FP_LISTING_TOO_LARGE`](#fp_listing_too_large) | `GET /v1/fp/{oid}` | Use the paged hive API: `GET /v1/hive/fp/{oid}?limit=100`. |
| [Web app notices](#web-app-notices): "Couldn't load the complete result", "This list is incomplete" | Web app | **Retry** when the notice says the problem is temporary ("Try again"). **Show what could be read** to see the partial result. |
| [HTTP 504 on a hive listing](#http-504-on-a-hive-listing) | API | Page through the hive with `limit`, or use `mtd_only=true`. |

## HIVE_LISTING_TOO_LARGE

**HTTP `413`.** Example answer:

```json
{
  "error": "lc_error_code:HIVE_LISTING_TOO_LARGE - listing of hive 'lookup' is too large to return in one response ...",
  "error_code": "HIVE_LISTING_TOO_LARGE",
  "retry": false
}
```

**What it means.** The hive holds more data than one answer can carry, so listing all of it in one call was refused.

**Why it happens.** A whole-hive listing (`GET /v1/hive/{hive}/{oid}` without `limit` or `cursor`) has a size limit of about 8 MiB of stored data. A hive reaches it with many records or a few very large ones, for example big lookup tables. A metadata-only whole listing is refused the same way past roughly 100,000 records. The exact limits are server settings and can change.

**What to do.** Retrying returns the same answer. Read the hive one page at a time, or ask for names and metadata only.

=== "CLI"

    ```bash
    # One page of 100 records, then the next
    limacharlie hive list --hive-name lookup --limit 100 --output json
    limacharlie hive list --hive-name lookup --limit 100 --cursor "NEXT_CURSOR_FROM_PREVIOUS_PAGE" --output json

    # Names and metadata only, no record data
    limacharlie hive list --hive-name lookup --metadata-only
    ```

    The same flags work on `limacharlie dr list` and every hive shortcut (`lookup list`, `secret list`, `fp list`, ...). Without `--limit` or `--cursor` the CLI already pages by itself when the API answers `413`, so this error reaches you through `limacharlie api` or a script that calls the API directly. See [Paging in the CLI](#paging-in-the-cli).

=== "Python"

    ```python
    from limacharlie.sdk.hive import Hive

    hive = Hive(org, "lookup")
    for page in hive.iter_pages(limit=100):   # {name: HiveRecord} per page
        for name, record in page.items():
            ...

    records = hive.list_mtd()                 # names and metadata only
    ```

    `hive.list()` and `hive.list_mtd()` read a too-large hive page by page by themselves. A `413` reaches your code only from a call that cannot page, and the exception's `suggestion` names the fix.

=== "REST API"

    ```bash
    curl -s -G "https://api.limacharlie.io/v1/hive/lookup/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT" \
      --data-urlencode "limit=100" --data-urlencode "cursor=NEXT_CURSOR"
    ```

    See [Listing Records](../../7-administration/config-hive/index.md#listing-records) for the full set of parameters.

## INVALID_CURSOR

**HTTP `400`.** The `cursor` you sent is not one the listing returned, or it was modified.

**Why it happens.** A cursor is an opaque value. It is only valid as returned in `next_cursor`: editing it, truncating it (for example in a copy and paste or a URL that was not encoded) or using one from another hive gives this error.

**What to do.** Pass `next_cursor` back exactly as received, URL-encoded if it goes in a query string. To start over, repeat the call without a cursor.

=== "CLI"

    ```bash
    limacharlie hive list --hive-name lookup --limit 100 --cursor "NEXT_CURSOR_EXACTLY_AS_PRINTED"
    limacharlie hive list --hive-name lookup --limit 100    # from the first page again
    ```

=== "Python"

    ```python
    from limacharlie.errors import ApiError

    try:
        page, cursor = hive.list_page(limit=100, cursor=saved_cursor)
    except ApiError as err:
        if err.error_code == "INVALID_CURSOR":
            page, cursor = hive.list_page(limit=100)   # start again
        else:
            raise
    ```

=== "REST API"

    ```bash
    curl -s -G "https://api.limacharlie.io/v1/hive/lookup/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT" \
      --data-urlencode "limit=100" --data-urlencode "cursor=$CURSOR"
    ```

## INCOMPLETE_RESULT

An answer that is built by reading several hives (the [Stories](../story-tags.md#incomplete-results) catalog and each story, and the list of [access-control scope resources](../../7-administration/access/resource-acls.md)) would look complete while missing records if one of those hives could not be read. LimaCharlie refuses to return it unless you accept the partial result. The error names the hives it left out:

```json
{
  "error": "the result is incomplete: the hives [lookup, query] could not be read. Retry, or pass allow_partial=true to accept a partial result",
  "error_code": "INCOMPLETE_RESULT",
  "skipped_hives": { "lookup": "BACKEND_ERROR", "query": "BACKEND_ERROR" }
}
```

`skipped_hives` maps each hive name to the reason it was left out. Hives you have no permission to read are never listed there: they are not an incomplete result.

### HTTP 503: a hive could not be read right now

**Why it happens.** A temporary failure, for example a backend that was restarting or busy.

**What to do.** Retry in a moment. If you would rather have what could be read than wait, add `allow_partial=true`.

### HTTP 413: a hive is too large to read

**Why it happens.** The records of the named hive that matter to this answer are more than one answer can hold (`HIVE_LISTING_TOO_LARGE` in `skipped_hives`). This does not go away by itself.

**What to do.** Retrying returns the same answer. Reduce the number of records in the named hives (delete records you no longer use), or add `allow_partial=true` to accept a result without them.

### Accepting a partial result

With `allow_partial=true` the call succeeds (HTTP `200`) and the body carries `"partial": true` and `skipped_hives`. Treat it as a lower bound: records from the skipped hives are missing. Any other value than `true` or `false` is a `400`.

=== "CLI"

    There is no dedicated CLI command for Stories or access-control resources. Use `limacharlie api` and keep the parameter in the URL (`-f` on its own turns the call into a POST):

    ```bash
    limacharlie api 'orgs/{oid}/stories?allow_partial=true'
    limacharlie api 'orgs/{oid}/stories/my-story?allow_partial=true'
    limacharlie api 'orgs/{oid}/acl/mailsec/resources?allow_partial=true'
    ```

    When the API answers `INCOMPLETE_RESULT`, `limacharlie api` prints the response body unchanged and a `Hint:` line on stderr.

=== "REST API"

    ```bash
    curl -s "https://api.limacharlie.io/v1/orgs/YOUR_OID/stories?allow_partial=true" \
      -H "Authorization: Bearer $LC_JWT"
    ```

## FP_LISTING_TOO_LARGE

**What it means.** The legacy false positive endpoint `GET /v1/fp/{oid}` returns every rule in one answer, and the organization has more rules than that can hold (about 16 MiB of JSON).

**What to do.** Page through the `fp` hive instead. The CLI and SDKs already read the `fp` hive page by page.

=== "CLI"

    ```bash
    limacharlie fp list --limit 100 --output json
    limacharlie fp list --metadata-only
    ```

=== "Python"

    ```python
    from limacharlie.sdk.hive import Hive

    for page in Hive(org, "fp").iter_pages(limit=100):
        ...
    ```

=== "REST API"

    ```bash
    curl -s -G "https://api.limacharlie.io/v1/hive/fp/YOUR_OID" \
      -H "Authorization: Bearer $LC_JWT" --data-urlencode "limit=100"
    ```

## HTTP 504 on a hive listing

A whole-hive listing that did not finish in time answers `504`. Do not repeat the same call: it is the heavy one. Page through the hive with `limit` and `cursor`, or use `mtd_only=true`. A paged call that times out can be retried shortly.

## Web App Notices

The web app shows these notices when a Story, the list of Stories or a list of access-control resources is built from hives that could not all be read. Nothing is shown rather than a result that silently misses records.

| Notice | Meaning | What to do |
|--------|---------|------------|
| "Couldn't load the complete result" with "Part of what this story is built from couldn't be read right now ..." (or "Some of your configuration couldn't be read right now ...") and "This is usually temporary" | The `503` case: a hive could not be read right now. | Click **Retry**. If it keeps failing, click **Show what could be read** and treat the result as incomplete. |
| "Couldn't load the complete result" with "... is too large to read ... Trying again won't help" | The `413` case: a hive is too large to read. There is no **Retry** button. | Click **Show what could be read** to see the partial result, and reduce the records in the hives the notice names. |
| "Showing an incomplete result", "This story is incomplete" or "This list is incomplete. ... couldn't be read, so some stories, or parts of them, may be missing" | You chose **Show what could be read**. The result is shown, and the hives named in the notice are missing from it. | Use it as a lower bound. Fix the cause (retry later, or reduce the records) and reload. |
| "The full list could not be loaded, so nothing is shown rather than a partial list. Reload to try again." | A list of records could not be read completely. | Reload the page. If it persists, page through the hive with the [CLI](#paging-in-the-cli) or API. |

The hives the notice names ("Lookups", "Secrets", "Detection & Response rules", ...) are the ones to look at: they are the `skipped_hives` of the API answer.

## Paging in the CLI

`limacharlie hive list`, `limacharlie dr list` and every hive shortcut `list` command accept:

| Option | Effect |
|--------|--------|
| `--limit N` | One page of at most `N` records, in record name order. The server caps it at 500 and also bounds a page by size, so a page can hold fewer records than `N`. |
| `--cursor C` | Continue from the `next_cursor` of the previous page. |
| `--max-bytes N` | With `--limit` or `--cursor`: stop a page before it exceeds `N` bytes. |
| `--tag-prefix P` | Only records with a tag starting with `P`. |
| `--metadata-only` | Names and metadata, no record data. |

A paged listing prints where the next page starts. With `--output json`, `yaml` or `toon` the result is `{"records": {...}, "next_cursor": "..."}`, and `next_cursor` is empty on the last page. With `table`, `csv` or `jsonl` the records are printed as usual and `next_cursor: ...` is printed on stderr, so a script reading stdout is not disturbed. Keep going until there is no `next_cursor`:

```bash
CURSOR=""
while :; do
  PAGE=$(limacharlie lookup list --limit 100 ${CURSOR:+--cursor "$CURSOR"} --output json)
  echo "$PAGE" | jq -r '.records | keys[]'
  CURSOR=$(echo "$PAGE" | jq -r '.next_cursor')
  [ -z "$CURSOR" ] && break
done
```

## CLI Messages

The CLI prints the API's error as it received it, so scripts can still read the code, and adds a `Suggestion:` line that names the fix and links back to this page. For example:

```text
Error: API error (400): {'error': 'lc_error_code:INVALID_CURSOR - cursor is not valid', 'error_code': 'INVALID_CURSOR', ...}
Suggestion: The cursor was not accepted: it is not one this listing returned, or it was changed. Pass the 'next_cursor' of the previous page unchanged, or drop '--cursor' (API 'cursor') to start again from the first page. See https://docs.limacharlie.io/8-reference/faq/large-and-incomplete-results/#invalid_cursor
```

`limacharlie api` leaves the response body untouched on stdout and prints the same advice as a `Hint:` line on stderr. In the Python SDK the exception is an `ApiError` with `status_code`, `error_code`, `response_body` and, for `INCOMPLETE_RESULT`, `skipped_hives`; `suggestion` holds the same advice.

## MCP Server

The MCP list tools are paged, so they do not hit `HIVE_LISTING_TOO_LARGE`. See [Listing Configuration Records](../../6-developer-guide/mcp-server.md#listing-configuration-records) for `limit`, `cursor` and `metadata_only`.
