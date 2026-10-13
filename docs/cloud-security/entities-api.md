# Entities API Reference

This page is the field-level reference for the [Entities](entity-pivot.md) REST
API. The CLI and MCP tools return the same responses; see
[MCP and CLI](entity-pivot.md#mcp-and-cli). Read [Entities](entity-pivot.md) first
for what the confidence levels, permissions and readiness states mean.

## API routes

Routes below are relative to `https://api.limacharlie.io/v1`.
`{oid}` is your organization ID and `{entity_id}` is the opaque ID returned by
resolution or search. Treat entity IDs as opaque strings. Every route needs
`cloudsec.get` and a Cloud Security subscription; without the subscription it
returns HTTP 403.

| Method and route | Inputs and response |
|---|---|
| `POST /cloudsec/{oid}/entities/resolve` | JSON body: `identifiers` (1–100 objects with `value`, optional `type`), optional `at` in Unix seconds, optional `observation_selectors` (at most 4, see [Look up a device with selectors](#look-up-a-device-with-selectors)). Each value is at most 1024 bytes and cannot be blank. Returns per-input `detected_types`, confirmed `matches`, unconfirmed `possible` and `ambiguous`, plus readiness and source freshness. With selectors, or with `insight.evt.get` and an explicit `hostname` the inventory does not know, it also returns `observed_matches` and `observations`. Omit `type` to detect plausible identifier types. |
| `GET /cloudsec/{oid}/entities/search` | Required `q` prefix; optional `kind` (`user` or `host`), `limit` (1–100, default 50), `cursor`. Returns `entities` with the matched identifier and optional `next_cursor`. |
| `GET /cloudsec/{oid}/entities/{entity_id}` | Optional `sightings_days` (1–365, default 30). Returns `card`, `index_ready` and optional `redirect_to` or `sightings` restriction. With `insight.evt.get` the card can carry `also_seen_as` and `cloud_sign_ins`, and the response `observations`. |
| `GET /cloudsec/{oid}/entities/{entity_id}/sightings` | Optional `kind` (`user`, `logon`, `int_ip`, `ext_ip`, `hostname`), `since`, `until`, `limit` (1–500, default 100), `cursor`. Without `since` and `until`, the window is the last 30 days; the window can span at most 365 days. Returns `sightings`, optional `next_cursor`, and `best_effort: true`. A row is returned when its observed interval overlaps the window, so rows that began shortly before `since` can appear. A User's sightings are only `user` and `logon` rows; address and hostname rows belong to Hosts. |
| `GET /cloudsec/{oid}/entities/{entity_id}/activity` | Optional `since`, `until`, `sources` (comma-separated `email,detections,sensor,cloud`; default all). An unknown or repeated source returns HTTP 400. Default window is the last 30 days; maximum window is 30 days. Returns per-source status, bounded items, truncation and full-view links. |

All timestamps are Unix **seconds**.

### IP resolution

- Without `at`, an `ip` input returns its current holders: sensors that reported
  the address and were alive in the last 7 days. With `insight.evt.get`, it also
  returns sensors whose sightings held the address in the last 30 days.
- With `at` and `insight.evt.get`, resolution uses only sightings that held the
  address in the two hours up to `at`.
- Matches derived from sightings are always `approximate` and carry the `sid`
  that reported the address.
- Without `insight.evt.get`, only current holders are available and `at` is
  ignored for addresses.

### Ambiguity and bounds

`ambiguous: true` means multiple **confirmed** entities matched. Possible-only
results, or one confirmed entity plus possible candidates, can have
`ambiguous: false`; that does not confirm the possible candidates.

Resolution never silently drops candidates. When one request would read more than
2,000 candidates across all its inputs, it fails with HTTP 400 and
`error_code: "entity_bounds"`. Send fewer identifiers per request or narrow the
time range.

See the [API reference](api-reference.md) for authentication and the wider Cloud
Security API.

## Response reference

All timestamps are Unix seconds. Fields described as optional are omitted when
they have no value. Ignore unknown fields: responses can gain fields over time.

### Resolve

The response has `results` (one object per input, in input order), `index_ready`
and `sources` (see [Readiness and freshness fields](#readiness-and-freshness-fields)).
`sightings: "forbidden"` appears when the caller lacks `insight.evt.get`; see
[Permissions](entity-pivot.md#permissions). When observation selectors were sent,
or an explicit `hostname` input was looked up in adapter events, it also has
`observed_matches` and `observations`.

| Top-level field | Meaning |
|---|---|
| `observed_matches` | Optional. One entry per selector: `selector`, `devices` and optional `truncated`. Leads, never inventory matches; see [Device leads](#device-leads). |
| `observations` | Optional. Completeness of the observed lookups; see [Reading observations](#reading-observations). |

| Result field | Meaning |
|---|---|
| `input` | The `value` and optional `type` you submitted. |
| `detected_types` | The identifier types tried. With an explicit `type` it contains only that type; otherwise the types the value's shape could be. |
| `matches` | Confirmed candidates, with confidence `authoritative` or `corroborated`. |
| `possible` | Unconfirmed candidates. Never select one automatically. |
| `ambiguous` | `true` when `matches` holds more than one entity. See [Ambiguity and bounds](#ambiguity-and-bounds). |

A match (in `matches`, `possible` or a card's `possible_matches`) has:

| Match field | Meaning |
|---|---|
| `entity_id` | The entity's opaque ID. |
| `kind` | `user` or `host`. |
| `display_name` | Human-readable name. |
| `confidence` | `authoritative`, `corroborated` or `possible`. |
| `via` | The identifier that produced the match: `type`, `value` and the `sources` that assert it. |
| `approximate` | Optional, `true` for an IP match derived from endpoint sightings, whose interval endpoints are approximate. |
| `sid` | Optional, the sensor whose sighting produced an approximate IP match. |

### Cards

`GET .../entities/{entity_id}` returns `card`, `index_ready`, optional
`redirect_to`, optional `sightings` and optional `observations` (see
[Reading observations](#reading-observations)). For `card: null` and
`redirect_to`, see [Readiness](entity-pivot.md#readiness-history-and-incomplete-results).
The card has:

| Card field | Meaning |
|---|---|
| `entity` | `id`, `kind`, `display_name` and `attrs` (see below). |
| `identifiers` | Every identifier of the entity: `type`, `value`, `display`, `confidence`, the `sources` that assert it, and `first_seen` and `last_seen`. A `0` timestamp means unknown. |
| `relationships` | Links to other entities: `rel` (such as `owns`), `direction`, the related `entity` (`id`, `kind`, `display_name`), `confidence` and the `source` that reported it. `direction` is `out` when this entity is the subject (a User that `owns` a Host) and `in` when the other entity is. |
| `recent_activity` | Optional, omitted without `insight.evt.get`. Account observations on sensors within the `sightings_days` window; see [Recent activity rows](#recent-activity-rows). |
| `possible_matches` | Unconfirmed candidates, shaped like a [match](#resolve). |
| `telemetry_sources` | Optional attached adapter and [Chrome browser profile](entity-pivot.md#chrome-browser-profiles) sensors: objects with `sid`, `platform`, `identity_type`, `hostname` and optional `identity_source` (`parser` or `mapping`). See [Adapter identities](entity-pivot.md#adapter-identities-and-external-actors). |
| `cloud` | Cloud or identity records linked to the entity: `urn` and `type` (the resource type from the URN). `name`, `exposed` and `open_findings` are optional and omitted when unknown; read open findings with the `cloud` [activity source](#activity). |
| `pivots` | Links, not data: `product`, `label`, `route`, `params` and the `permission` needed. A sensor identifier yields a sensor-timeline pivot (`product: "edr"`, permission `sensor.get`). |
| `sources` | Freshness of each source behind the card; see [Readiness and freshness fields](#readiness-and-freshness-fields). |
| `also_seen_as` | Optional, Host cards, needs `insight.evt.get`. [Device leads](#device-leads) from other security products. Absent does not mean none: read `observations`. |
| `cloud_sign_ins` | Optional, Host and User cards, needs `insight.evt.get`. [Sampled sign-ins](#sign-in-leads) and the Hosts that shared their source address. Absent does not mean none: read `observations`. |

`entity.attrs` is a small summary object. Keys that can appear:

| `attrs` key | Meaning |
|---|---|
| `external` | `true` for a User with no internal directory record: known only through an adapter, or flagged by its provider as outside the organization. Removed when a directory record joins the entity. See [Adapter identities](entity-pivot.md#adapter-identities-and-external-actors). |
| `human` | On a User from a directory or identity provider: `true` for a person, `false` for a known non-human principal such as a service account. Absent when the source does not say. |
| `platform` | On a Host: the platform reported by its sensor, such as `windows`. |
| `os` | On a Host built from a managed-device or third-party asset record: the operating system the source reported. |
| `posture` | On such a Host, device-posture facts the source reported (for example `encryption`, `screen_lock`, `managed_state`, `ownership`, `os_version`, `model`, `manufacturer`). Only reported facts appear. |
| `last_alive_day` | On a Host with a sensor: the latest known UTC day (`YYYY-MM-DD`) the sensor manager saw it alive. With several sensors, the latest day. Absent when unknown. |
| `sources` | The sorted, de-duplicated list of sources that contributed to the entity. |
| `joins_stale` | `true` when the sensor-to-cloud link data was unavailable at the last refresh and the entity kept its earlier cloud links. Treat the card's source freshness as stale. |
| `split_from` | List of earlier entity IDs: this entity was created when the identifiers of an earlier entity no longer formed one group. The earlier ID stays with the group that kept most of its identifiers. |
| `recent_activity_incomplete`, `possible_matches_incomplete`, `projection_catching_up`, `cloud_context_incomplete` | Incompleteness markers; see [Readiness and freshness fields](#readiness-and-freshness-fields). |

#### Recent activity rows

| Field | Meaning |
|---|---|
| `rel` | `active_on` (processes ran as the account) or `logged_on` (an interactive logon). |
| `kind` | Optional, the sighting kind: `user` or `logon`. |
| `sid` | The sensor the account was observed on. |
| `sensor` | Optional, that sensor's `sid`, `hostname`, `platform`, `int_ip` and `ext_ip`. Absent when the sensor is no longer inventoried. |
| `value`, `account` | The normalized account, and its spelling as observed (for example `CORP\alice`). |
| `first_ts`, `last_ts`, `days` | First and last observation in the window, and the number of distinct UTC days observed. |
| `sources` | Optional, up to 8 event types the account was observed through. A hint, not an exhaustive list. |
| `confidence`, `approximate` | The row's confidence, and whether its interval is approximate. |
| `entity` | Optional. The other entity, when exactly one confirmed match exists; otherwise the candidates appear in `possible_matches`. |
| `confidence_reason` | Optional, why a row is `possible`: `sensor_not_linked_to_host`, `sensor_on_multiple_hosts`, `sensor_link_possible`, `account_not_linked`, `account_matches_multiple_users`, `account_matches_other_user` or `account_link_possible`. |

### Sightings

`GET .../sightings` returns `sightings`, optional `next_cursor` and
`best_effort: true`. Rows are daily buckets, newest day first:

| Row field | Meaning |
|---|---|
| `sid` | Sensor that observed it. |
| `kind` | `user`, `logon`, `int_ip`, `ext_ip` or `hostname`. |
| `value`, `value_display` | The normalized value, and its display form. |
| `day` | UTC date, `YYYY-MM-DD`. |
| `first_ts`, `last_ts` | First and last observation in that bucket. |
| `host_entity_id` | Optional. The Host entity: the entity itself for a Host, or for a User the single Host that has this sensor. |
| `user_entity_id` | Optional. Set on `user` and `logon` rows when exactly one confirmed User matches the account. |

Sightings follow merges silently and do not return `redirect_to`; use the card to
learn the survivor's ID. An unknown entity returns an empty list.

### Search

`GET .../entities/search` returns `entities`, `index_ready` and optional
`next_cursor`. Each entity has `id`, `kind`, `display_name` and `matched` (the
identifier `type` and `value` that matched the prefix). Directory-backed entities
come before external actors.

### Activity

`GET .../activity` returns `entity_id`, `index_ready`, `since`, `until`,
`sources` (one object per requested source) and optional `redirect_to` and
`sightings`. Each source object has `source`, `status`, `items`, `truncated` and
`link`, where `link` is the route of the full view. Each source returns at most
100 items. When the index is not ready or the entity has no card, the route
returns the card response shape (`card: null`) instead.

| Source | Items |
|---|---|
| `email` | Users only. Flagged mail to or from the User's confirmed email addresses: mail the engine judged malicious or suspicious, or that was dispositioned malicious or spam. Other mail is not listed, so an empty preview does not mean the User received no mail. |
| `detections` | Detections from the entity's sensors, including attached adapter sensors and, for a User, owned Hosts. |
| `sensor` | `sid` with live state for each sensor. |
| `cloud` | Open cloud findings on the linked cloud records. |

For the `status` values, see
[Readiness](entity-pivot.md#readiness-history-and-incomplete-results).

### Readiness and freshness fields

Each entry of `sources` (on resolve and on cards) has:

| Field | Meaning |
|---|---|
| `source` | The source name. |
| `last_success` | Optional, the last successful collection in Unix seconds. Missing means unknown. |
| `last_alive_day` | Optional, for telemetry sources that have no collection run: the newest UTC day (`YYYY-MM-DD`) an attached sensor reported alive. |
| `stale` | `true` when the source has not supplied fresh verified evidence. |
| `detail` | Optional explanation. |

Incompleteness markers in `entity.attrs`:

| Marker | Meaning |
|---|---|
| `recent_activity_incomplete` | The card's recent activity is a partial summary. Use paged sightings for history. |
| `possible_matches_incomplete` | Not every possible match is listed. Use resolve for identifier candidates. |
| `projection_catching_up` | Some projected information may be out of date. |
| `cloud_context_incomplete` | Cloud names or resource details could not all be read. |

## Leads in responses

These fields carry the [leads from adapter events](entity-pivot.md#leads-from-adapter-events).

### Reading observations

Responses that carry observed pivots add `observations`. Read it before
interpreting an empty list.

| `observations` field | Meaning |
|---|---|
| `status` | `ok`: every bounded read completed. `incomplete`: results are present but a bound cut some evidence, so they are not "no other devices". `unavailable`: the lookup could not run, so it is not "no sign-ins". `forbidden`: the caller lacks `insight.evt.get` and no observation query ran. |
| `reason` | Optional, set when `status` is `unavailable`: `schema_missing`, `deadline`, `query_budget`, `bounds` or `error`. |
| `queries`, `rows` | The number of logical queries run and rows read to answer. |
| `truncated` | Optional, `true` when a bound cut the rows returned. |

`incomplete`, `unavailable` and `forbidden` never mean "none".

### Device leads

| Field | Meaning |
|---|---|
| `origin_sid`, `platform`, `vendor_device_id` | The collector sensor that delivered the record, the product (`sophos`, `crowdstrike`, `entraid` or `duo`) and, when present, its device ID. A device seen by two collectors is two entries, never fused. |
| `day` | The UTC date (`YYYY-MM-DD`) of this daily record. |
| `names`, `local_ips` | The hostnames and endpoint-local addresses the product reported that day. |
| `first_ts`, `last_ts` | First and last time the product reported it that day. |
| `recipes` | `id` and `version` of the built-in reader that produced the evidence. |
| `confidence` | `corroborated`, `possible`, `unlinked` (no Host qualified) or `unknown` (evidence was missing or inconsistent). A Host card's `also_seen_as` can carry all four: it lists every record that names the Host as a candidate. |
| `approximate` | Always `true` for a `corroborated` lead. |
| `reason` | Why: see below. |
| `conflicting_names`, `incomplete` | Optional flags: the device reported conflicting names; some evidence was missing or cut. |
| `candidates` | The Hosts it may be: `entity` (`id`, `kind`, `display_name`), `confidence`, `reason`, the matching sensors in `sids`, and optional `hostname_range` and `ip_range` (`first_ts`, `last_ts`) of the sensor-side evidence. |

| Device `reason` | Meaning |
|---|---|
| `hostname_internal_ip_same_day` | Exactly one Host had a sensor that reported the same hostname and the same internal IP that UTC day. This is the only `corroborated` case. A public address never counts. |
| `multiple_hosts_same_day` | Several Hosts qualify. All are listed as `possible`; `conflicting_names` is set when the device also reported conflicting names. |
| `conflicting_names` | Exactly one Host qualifies, but the device reported conflicting names. It is listed as `possible`. |
| `no_qualifying_host` | No Host had both the hostname and the internal IP that day (`unlinked`). Hosts that matched only by name are still listed in `candidates` as `possible`. |
| `no_name_or_address` | The record has no usable name or address (`unlinked`). |
| `incomplete_facts`, `inconsistent_facts` | Evidence was missing or contradictory (`unknown`). Any Hosts found are listed as `possible`; it is never presented as a unique match. |

A candidate's own `reason` is `hostname_internal_ip_same_day`, or, for a Host
that matched only by name, `hostname_same_day` (a sensor reported the name that
day) or `current_hostname_only` (no name history exists for that day, so only a
sensor's current name matched).

### Sign-in leads

| Field | Meaning |
|---|---|
| `origin_sid`, `platform`, `day`, `recipes` | As for device leads. `platform` is `office365`, `entraid`, `okta` or `duo`. |
| `principal_type`, `principal` | The account the product recorded. |
| `outcome`, `successful` | The product's outcome and whether it is a success. |
| `first_ts`, `last_ts` | First and last sign-in time recorded that day. |
| `user` | On User cards, how the principal links to existing Users: `confidence` (`corroborated`, `possible`, `unlinked` or `unknown`), `reason` and `candidates` (Users). |
| `samples` | The retained sign-in times: `ts`, `label` (`first`, `last` or `only`), `hosts` (candidate Hosts that shared the source address near that time) and optional `no_observed_match`. |
| `hosts_skipped` | `outcome_not_successful` when no endpoint was correlated because the sign-in did not succeed. |
| `incomplete` | Optional, some evidence was cut. |

- **Sign-in Host candidates are always `possible`** (reason `shared_ip_near_time`), even when
  there is only one. Shared NAT, VPN or proxy egress identifies an office, not an endpoint.
  `no_observed_match` means no sensor was seen, not that none was involved.
- A daily record keeps only its first and last times. They are samples; no sign-in is
  inferred between them. Use the product's own events for the full timeline.
- Failed and unknown outcomes are listed apart and correlate no endpoint.
- A principal never creates or merges a User.

| `user.reason` | Meaning |
|---|---|
| `entra_object_id`, `okta_user_id` | The provider's user ID matched. `corroborated` when the User's identifier is strong, otherwise `possible`. |
| `email` | The address matched a strong identifier on an Office 365 or Entra ID sign-in (`corroborated`). |
| `email_possible`, `username`, `username_local_part`, `conflicting_exact_matches` | Weaker or conflicting matches (`possible`). |
| `no_known_user` | No User matched (`unlinked`). |
| `incomplete_facts`, `inconsistent_facts` | Evidence was missing or contradictory (`unknown`). |

### Look up a device with selectors

The resolve route accepts up to four `observation_selectors`:

| Selector | Fields |
|---|---|
| Vendor device ID | `{"type": "vendor_device_id", "platform": "sophos", "value": "<device id>"}`. `platform` is required (`sophos`, `crowdstrike`, `office365`, `entraid`, `okta` or `duo`; only `sophos`, `crowdstrike`, `entraid` and `duo` report devices). Optional `origin_sid` (a sensor ID in lower-case UUID form) restricts it to one collector; without it every collector's record is returned. The value is at most 128 bytes. |
| Foreign hostname | `{"type": "foreign_hostname", "value": "WEB-01"}`: a hostname as another product reports it, at most 512 bytes. Takes no `platform` or `origin_sid`. |

Selectors are read selectors, not identifier types, and an invalid one fails the
request with HTTP 400. `at` pins one UTC day; without it the newest days, up to
31, are examined. Answers appear only in the top-level `observed_matches`, never in
`matches`: each entry has the `selector`, its `devices` (the
[device lead](#device-leads) shape, with `candidates`) and optional `truncated`.
`observations` reports completeness.

With `insight.evt.get`, an input explicitly typed `hostname` that the inventory
does not know is also looked up as a foreign hostname, while the selector bound
has room. Untyped inputs are not. Without `insight.evt.get`, selectors return
`observations.status: "forbidden"`.

=== "CLI"

    ```bash
    # resolve still needs one --identifier.
    limacharlie cloudsec entity resolve --identifier web-01 --type hostname \
      --foreign-hostname WEB-01 --oid $OID
    limacharlie cloudsec entity resolve --identifier web-01 \
      --observation-selector '{"type":"vendor_device_id","platform":"sophos","value":"<device id>"}' \
      --oid $OID
    ```

=== "MCP"

    ```text
    cloudsec_entity_resolve {"identifiers": [{"value": "web-01"}],
      "observation_selectors": [{"type": "foreign_hostname", "value": "WEB-01"}]}
    ```

=== "API"

    ```bash
    curl -s -X POST "https://api.limacharlie.io/v1/cloudsec/$OID/entities/resolve" \
      -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
      -d '{"identifiers": [{"value": "web-01"}],
           "observation_selectors": [{"type": "foreign_hostname", "value": "WEB-01"}]}'
    ```
