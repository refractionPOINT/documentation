# Entity Pivot

Entity Pivot connects identifiers from Cloud Security, endpoint security and
Email Security to **User** and **Host** entities. Start with an email address,
Windows account, GitHub user ID or login, hostname, IP address or sensor ID to find the known identities,
relationships and activity associated with it.

A User represents a principal, including a person, service account or shared
mailbox owner. A Host represents a machine, including an endpoint or cloud VM.
Ownership relates a User to a Host; they remain separate entities.

!!! note "Availability"
    The Entity Pivot API, the console page, the CLI and the MCP tools are available
    for organizations with Cloud Security. The CLI group `limacharlie cloudsec entity`
    is in python-limacharlie 5.7.0 and later; the `pivot` subcommand ships in the next
    CLI release. A `feature_disabled: true` response means the
    feature is unavailable; it does not mean the organization has no entities.

## Investigate an entity

Open **Entities** from the top level of the console sidebar and search with an
identifier prefix. Results are grouped into Users and Hosts. Search covers every identifier
type below, requires at least two characters and accepts up to 512 UTF-8 bytes.
You can also start from Identity 360, a sensor page or an Email Security message's
sender or mailbox address.

The entity page shows identifiers grouped by type with their confidence and
sources, ownership relationships, a recent activity timeline, possible matches,
cloud posture and activity previews from other products. Unknown exposure or
finding counts remain unknown. A source marked stale has not supplied fresh
verified evidence; its data may be out of date.

An identifier can belong to more than one entity. For example, several machines
can share a hostname or IP address. Inspect every candidate rather than choosing
the first result. Possible matches are displayed separately as **unconfirmed**.

## Identifiers and confidence

| Identifier type | Meaning |
|---|---|
| `email` | Mailbox address, user principal name, sign-in email or directory alias. An editable directory mail attribute (Entra `mail`, Okta secondary email) that matches no sign-in address on the same record is only a possible match. |
| `github_user_id` | GitHub's immutable numeric user ID, represented as a decimal string; authoritative identity evidence from a collected identity or built-in adapter parser. |
| `github_login` | Mutable GitHub login, normalized to lowercase with an App actor's terminal `[bot]` suffix preserved. Corroborated linking requires exactly one current GitHub identity holding the login; renamed or reclaimed logins do not override stable numeric IDs. |
| `entra_object_id` | Microsoft Entra user object ID. |
| `okta_user_id` | Okta user ID. |
| `gws_user_id` | Google Workspace user ID. |
| `aws_arn` | AWS principal ARN. |
| `windows_sid` | Windows security identifier. |
| `ad_account` | Domain-qualified Windows account, using the full directory domain. |
| `ad_account_short` | Windows account using a short domain label; confidence depends on confirmed directory evidence. |
| `username` | Bare account name; matches are possible, never sufficient alone to establish identity. |
| `sensor_id` | LimaCharlie sensor ID. |
| `device_id` | Device identity reported by a LimaCharlie sensor. |
| `cloud_instance_id` | Provider-qualified compute instance ID. |
| `graph_urn` | Canonical resource identifier for a collected cloud or identity record. |
| `serial` | Normalized device serial number. |
| `mac` | Normalized hardware MAC address; unsuitable virtual/local addresses are excluded. |
| `hostname` | Short hostname; collisions are kept distinct. |
| `fqdn` | Fully qualified host name, with collision and native-identity checks. |
| `ip` | Canonical IP address; shared addresses and historical holders remain separate candidates. |

| Confidence | Interpretation |
|---|---|
| `authoritative` | A source directly asserts the identity or a strong immutable identifier agrees. |
| `corroborated` | Independent evidence supports the identity, subject to collision checks. |
| `possible` | A weak or derived association. Unconfirmed; never merges entities or selects a candidate automatically. |

**Ownership** comes from a device source naming an owner, such as Intune's user
principal name. **Active on** means a process-owner account was observed on a
host. **Logged on** means a successful login was observed. Process-owner evidence
is not proof that someone logged in, and ownership is not proof of current use.

## Adapter identities and external actors

An adapter sensor can represent a user or device rather than an endpoint host.
Supported parsers declare this meaning automatically; a custom mapping can declare
`sensor_identity_type` alongside `sensor_key_path`. See
[Adapter usage](../2-sensors-deployment/adapters/usage.md)
for the vocabulary, parser defaults and raw-key limits.

- Built-in parser `email` declarations create Users and can join matching directory
  identities. GitHub parsers attach the immutable numeric `github_user_id` when
  available; matching this ID is authoritative. The mutable `github_login` is
  corroborated only under the uniqueness and stable-ID collision checks.
- `username` creates a User, but a shared bare name remains a possible match and
  never merges users.
- `device` creates a Host. A valid device hostname can corroborate a unique name
  from another source. Vendor identifiers remain evidence rather than device
  identifiers that link across providers; ID-shaped hostnames do not establish a
  name match.
- An undeclared adapter sensor does not become an entity based on its platform
  or hostname alone.

A customer mapping is a declaration about a free-form log field, which may be
influenced by an outside actor. **Every identifier from a mapping is possible
and unconfirmed**, including its sensor ID; it never merges entities. A built-in
parser declaration uses the confidence rules above. Declaring a mapping does not
prove that its sensor and a matching directory account are the same principal.

An adapter sensor is associated after it connects with a declaration and the
next entity refresh completes. Sensors that have not reconnected since their
declaration became available are not yet associated; absence is not evidence of
no adapter activity.

A User known only through an adapter is shown as an **External actor**
(`attrs.external: true`). This means no directory-backed observation has joined
that entity; it does not determine whether the actor is malicious. Directory-backed
users appear before external actors in search results. When directory evidence
joins the entity, the external designation is removed.

The entity page's **Telemetry sources** section lists attached adapter sensors,
including sensor ID, platform, identity type and hostname. The card API exposes
this optional section as `telemetry_sources`, containing objects with `sid`,
`platform`, `identity_type`, `hostname` and optional `identity_source`.
The declaration source is `parser` or `mapping`; mappings are shown as
**unconfirmed**. Missing or unknown provenance remains unknown rather than trusted.
Sensor timeline links require
`sensor.list`, `sensor.get` and either `insight.evt.get` or `insight.evt.get.simple`, matching the
destination timeline permissions.
An absent or empty section means no attached adapter sources were reported by that
response, not that the entity has never generated telemetry.

Detections activity includes the entity's attached adapter sensor IDs. The same
`insight.det.get` permission applies. Declarations are picked up on the next sensor
connection; existing events and sensor names are not backfilled. The sensor
identity metadata uses four additive fields: `identity_type`, raw `identity_key`,
optional immutable `identity_id` and declaration provenance `identity_source`.
Both raw key and stable ID are limited to 512 UTF-8 bytes and validated for their
declared type. Invalid or oversized declarations are dropped rather than
truncated, while telemetry continues to ingest.

## Permissions

Every entity route requires `cloudsec.get` and an enabled Cloud Security
subscription. Product links and previews use the caller's own permissions.

| Data | Additional permission or subscription |
|---|---|
| Endpoint sightings, recent endpoint activity, historical IP resolution | `insight.evt.get`. Without it, cards and resolution report `sightings: "forbidden"` and omit this evidence; the sightings route returns HTTP 403. |
| Email activity | `mailsec.get` and an enabled Email Security subscription. |
| Detections | `insight.det.get`. For a User without `insight.evt.get`, detections include attached adapter sensors and owned hosts, excluding hosts linked solely by endpoint activity. |
| Live sensor state | `sensor.get`. |
| Sensor timeline links | `sensor.list`, `sensor.get` and either `insight.evt.get` or `insight.evt.get.simple`. Simple event access does not grant entity sightings. |
| Cloud findings | `cloudsec.get`. |

A forbidden source is not an empty source. Ask an organization administrator to
grant the needed permission; subscribe to the product to enable its data.

## Readiness, history and incomplete results

- `index_ready: false` means the first entity index has not completed. Wait for
  collection and indexing before interpreting results.
- `card: null` with `index_ready: true` and no `redirect_to` means the entity ID
  is unknown in this organization.
- Entities can merge when new evidence shows two entities are the same. Reading
  a merged ID returns the **surviving** entity's card, with `redirect_to` set to
  the survivor's ID. Use `redirect_to` as the ID from then on. If the survivor has
  itself been retired, `card` is `null` and `redirect_to` names that retired
  entity: the ID was known and merged, but no current entity is left to show.
  A retired entity that was never merged is indistinguishable from an unknown ID.
- Source freshness includes `source`, optional `last_success` in Unix seconds,
  `stale` and optional `detail`. Missing successful collection time is unknown.
- Sightings are **best effort**, retained for up to 365 days. They cover events
  already collected from sensors; they are not a complete login audit. Interval
  endpoints are approximate, with refresh intervals of up to two hours for IPs
  and hostnames, and six hours for account observations. They do not prove
  continuous activity or absence outside the interval.
- A card's recent activity is a summary, not the complete history. The entity's
  `attrs.recent_activity_incomplete` and `attrs.possible_matches_incomplete`
  markers disclose incomplete summaries or candidates. Use paged sightings for
  history and resolve for identifier candidates. `attrs.projection_catching_up`
  means some projected information may be out of date.
- Search and sightings can return `next_cursor`. Pass it back unchanged with
  the same selectors until no cursor remains. One page is not the full set.
- Activity is a bounded preview: each requested source reports `status`, `items`,
  `truncated` and a full-view `link`. An unavailable or timed-out source may still
  return partial items. Keep those items and the status together.

| Activity status | Meaning |
|---|---|
| `ok` | The source answered; inspect `truncated` before treating the preview as complete. |
| `forbidden` | The caller lacks the source's permission. |
| `not_subscribed` | The required product subscription is absent. |
| `unavailable` | The source could not provide a complete answer. |
| `timeout` | The source did not complete within its deadline. |

## API routes

Routes below are relative to `https://api.limacharlie.io/v1`.
`{oid}` is your organization ID and `{entity_id}` is the opaque ID returned by
resolution or search. Treat entity IDs as opaque strings.

| Method and route | Inputs and response |
|---|---|
| `POST /cloudsec/{oid}/entities/resolve` | JSON body: `identifiers` (1–100 objects with `value`, optional `type`), optional `at` in Unix seconds. Each value is at most 1024 bytes. Returns per-input `detected_types`, confirmed `matches`, unconfirmed `possible` and `ambiguous`, plus readiness and source freshness. Omit `type` to detect plausible identifier types. |
| `GET /cloudsec/{oid}/entities/search` | Required `q` prefix; optional `kind` (`user` or `host`), `limit` (1–100), `cursor`. Returns `entities` with the matched identifier and optional `next_cursor`. |
| `GET /cloudsec/{oid}/entities/{entity_id}` | Optional `sightings_days` (1–365, default 30). Returns `card`, `index_ready` and optional `redirect_to` or `sightings` restriction. |
| `GET /cloudsec/{oid}/entities/{entity_id}/sightings` | Optional `kind` (`user`, `logon`, `int_ip`, `ext_ip`, `hostname`), `since`, `until`, `limit` (1–500), `cursor`. Returns `sightings`, optional `next_cursor`, and `best_effort: true`. `since` is inclusive; `until` is exclusive. |
| `GET /cloudsec/{oid}/entities/{entity_id}/activity` | Optional `since`, `until`, `sources` (comma-separated `email,detections,sensor,cloud`; default all). Default window is the last 30 days; maximum window is 30 days. Returns per-source status, bounded items, truncation and full-view links. |

All timestamps are Unix **seconds**. For `ip` resolution without `at`, results
include current holders and, with event permission, sighting holders from the
last 30 days. With `at`, resolution uses sighting intervals at that time and
marks approximate matches. Without event permission, only current holders are
available; historical sighting matches are omitted.

`ambiguous: true` means multiple **confirmed** entities matched. Possible-only
results, or one confirmed entity plus possible candidates, can have
`ambiguous: false`; that does not confirm the possible candidates. Resolution
returns a client limitation error if the candidate set exceeds its bound, rather
than silently dropping candidates.

See the [API reference](api-reference.md) for authentication and the wider Cloud
Security API.

## Response reference

All timestamps are Unix seconds. Fields described as optional are omitted when
they have no value. Ignore unknown fields: responses can gain fields over time.

### Resolve

The response has `results` (one object per input, in input order), `index_ready`
and `sources` (freshness, see [Cards](#cards)). `sightings: "forbidden"` appears
when the caller lacks `insight.evt.get`; see [Permissions](#permissions).

| Result field | Meaning |
|---|---|
| `input` | The `value` and optional `type` you submitted. |
| `detected_types` | The identifier types tried. With an explicit `type` it contains only that type; otherwise the types the value's shape could be. |
| `matches` | Confirmed candidates, with confidence `authoritative` or `corroborated`. |
| `possible` | Unconfirmed candidates. Never select one automatically. |
| `ambiguous` | `true` when `matches` holds more than one entity. See [API routes](#api-routes). |

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
`redirect_to` and optional `sightings`. The card has:

| Card field | Meaning |
|---|---|
| `entity` | `id`, `kind`, `display_name` and `attrs` (see below). |
| `identifiers` | Every identifier of the entity: `type`, `value`, `display`, `confidence`, the `sources` that assert it, and `first_seen` and `last_seen`. A `0` timestamp means unknown. |
| `relationships` | Links to other entities: `rel` (such as `owns`), `direction`, the related `entity` (`id`, `kind`, `display_name`), `confidence` and the `source` that reported it. `direction` is `out` when this entity is the subject (a User that `owns` a Host) and `in` when the other entity is. |
| `recent_activity` | Optional, omitted without `insight.evt.get`. Account observations on sensors within the `sightings_days` window: `rel` (`active_on` or `logged_on`), `sid`, the account label in `value`, `first_ts`, `last_ts`, `confidence` and `approximate`. `entity` names the other entity when exactly one confirmed match exists; otherwise it is absent and the candidates appear in `possible_matches`. |
| `possible_matches` | Unconfirmed candidates, shaped like a [match](#resolve). |
| `telemetry_sources` | Optional attached adapter sensors; see [Adapter identities](#adapter-identities-and-external-actors). |
| `cloud` | Cloud or identity records linked to the entity: `urn` and `type` (the resource type from the URN). `name`, `exposed` and `open_findings` are optional and omitted when unknown; read open findings with the `cloud` [activity source](#readiness-history-and-incomplete-results). |
| `pivots` | Links, not data: `product`, `label`, `route`, `params` and the `permission` needed. A sensor identifier yields a sensor-timeline pivot (`product: "edr"`, permission `sensor.get`). |
| `sources` | Freshness of each source behind the card: `source`, optional `last_success`, `stale` and optional `detail`. |

`entity.attrs` is a small summary object. Keys that can appear:

| `attrs` key | Meaning |
|---|---|
| `external` | `true` for a User with no internal directory record: known only through an adapter, or flagged by its provider as outside the organization. Removed when a directory record joins the entity. See [Adapter identities](#adapter-identities-and-external-actors). |
| `human` | On a User from a directory or identity provider: `true` for a person, `false` for a known non-human principal such as a service account. Absent when the source does not say. |
| `platform` | On a Host: the platform reported by its sensor, such as `windows`. |
| `os` | On a Host built from a managed-device or third-party asset record: the operating system the source reported. |
| `posture` | On such a Host, device-posture facts the source reported (for example `encryption`, `screen_lock`, `managed_state`, `ownership`, `os_version`, `model`, `manufacturer`). Only reported facts appear. |
| `last_alive_day` | On a Host with a sensor: the latest known UTC day (`YYYY-MM-DD`) the sensor manager saw it alive. With several sensors, the latest day. Absent when unknown. |
| `sources` | The sorted, de-duplicated list of sources that contributed to the entity. |
| `joins_stale` | `true` when the sensor-to-cloud link data was unavailable at the last refresh and the entity kept its earlier cloud links. Treat the card's source freshness as stale. |
| `split_from` | List of earlier entity IDs: this entity was created when the identifiers of an earlier entity no longer formed one group. The earlier ID stays with the group that kept most of its identifiers. |
| `recent_activity_incomplete`, `possible_matches_incomplete`, `projection_catching_up` | Incompleteness markers; see [Readiness](#readiness-history-and-incomplete-results). |

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
identifier `type` and `value` that matched the prefix).

### Activity

`GET .../activity` returns `entity_id`, `index_ready`, `since`, `until`,
`sources` (one object per requested source) and optional `redirect_to` and
`sightings`. Each source object has `source`, `status`, `items`, `truncated` and
`link`, where `link` is the route of the full view. Items are the records the
underlying product returns: messages for `email`, detections for `detections`,
`sid` with live state for `sensor`, and open findings for `cloud`. When the index
is not ready or the entity has no card, the route returns the card response shape
(`card: null`) instead.

## MCP and CLI

These MCP tools are read-only. All six are in the `cloud_security`,
`cloud_security_readonly`, `historical_data`, `historical_data_readonly`,
`email_security` and `email_security_readonly` profiles, so an email or
historical-data investigation can pivot without switching profile.

| Tool | Arguments | Purpose |
|---|---|---|
| `cloudsec_entity_pivot` | `identifier` (required), optional `type`, `at` | The default for "what is this identifier?". Resolves one identifier, then returns the cards of its confirmed, unambiguous matches (at most 10) in `cards`. The resolve results stay in `candidates`; possible and ambiguous candidates are never followed automatically. Also returns `index_ready`, `sources`, any other top-level resolve fields, `truncated` and, for a card that failed to load, `card_errors`. |
| `cloudsec_entity_resolve` | `identifiers` (required, 1–100 objects with `value` and optional `type`), optional `at` | Batch resolution only: candidates for every input, no cards. The [resolve response](#resolve) unchanged. |
| `cloudsec_entity_get` | `entity_id` (required), optional `sightings_days` (1–365) | One entity card with `index_ready`, `redirect_to` and `sightings`, unchanged. |
| `cloudsec_entity_search` | `q` (required), optional `kind`, `limit` (1–100), `cursor` | One page of identifier-prefix search with readiness and the next cursor. |
| `cloudsec_entity_sightings` | `entity_id` (required), optional `kind`, `since`, `until`, `limit` (1–500), `cursor` | One page of best-effort sightings. Needs `insight.evt.get`. |
| `cloudsec_entity_activity` | `entity_id` (required), optional `since`, `until`, `sources` | Activity preview, preserving per-source status and truncation. |

Arguments follow the [API routes](#api-routes). `type` takes one of the
[identifier types](#identifiers-and-confidence).

The CLI command group is `limacharlie cloudsec entity`. Each subcommand answers
`--ai-help` with guidance on its purpose and response fields.

| Subcommand | Main selectors |
|---|---|
| `pivot` | `--identifier` (one value), optional `--type`, `--at`. Resolves the identifier and fetches cards the same way as `cloudsec_entity_pivot`. |
| `resolve` | Repeatable `--identifier`, optional `--type`, `--at`. |
| `get` | `--entity-id`, optional `--sightings-days`. |
| `search` | `--q`, optional `--kind`, `--limit`, `--cursor`. |
| `sightings` | `--entity-id`, optional `--kind`, `--since`, `--until`, `--limit`, `--cursor`. |
| `activity` | `--entity-id`, optional `--since`, `--until`, repeatable `--source`. |

`pivot` ships in the next CLI release. Use `resolve` followed by `get` with
python-limacharlie 5.7.0 and later. Run `limacharlie cloudsec entity --help` to
see what your installed release provides.

Use the organization and output options described in [CLI](cli.md). Preserve
ambiguity, forbidden statuses, redirects and continuation cursors when scripting;
an empty preview is not evidence that nothing happened. See [MCP](mcp.md) for
profile setup.

## Worked investigation

A message from a suspicious sender reached `alice@example.com`. Which machine does
she own, what did it do, and is there cloud exposure? The values below are
synthetic.

1. **Resolve the mailbox to a User.** Pass the address with no `type`. One
   confirmed, unambiguous match gives a User ID such as `eu_k5xw4zdpnvsxe3tl`. If
   `ambiguous` is `true`, or the only candidates are in `possible`, stop and pick
   with evidence instead of taking the first.
2. **Read the User card.** `relationships` with `rel: "owns"` and
   `direction: "out"` list the Hosts she owns, for example `eh_nfzxiyltmrzgs43t`.
   Check `redirect_to` and use it as the ID if present.
3. **Ask for activity.** For the User, `email` shows her messages; `detections` and
   `sensor` include her owned Hosts. Then ask for the Host's `detections`,
   `sensor` and `cloud` sources. Read each `status` and `truncated` before
   concluding anything.

=== "CLI"

    ```bash
    # Next CLI release: resolve and fetch the card in one step.
    limacharlie cloudsec entity pivot --identifier alice@example.com --oid $OID

    # python-limacharlie 5.7.0 and later:
    limacharlie cloudsec entity resolve --identifier alice@example.com --oid $OID
    limacharlie cloudsec entity get --entity-id eu_k5xw4zdpnvsxe3tl --oid $OID
    limacharlie cloudsec entity activity --entity-id eu_k5xw4zdpnvsxe3tl \
      --source email --source detections --oid $OID
    limacharlie cloudsec entity activity --entity-id eh_nfzxiyltmrzgs43t \
      --source detections --source sensor --source cloud --oid $OID
    ```

=== "MCP"

    ```text
    cloudsec_entity_pivot    {"identifier": "alice@example.com"}
    cloudsec_entity_activity {"entity_id": "eu_k5xw4zdpnvsxe3tl",
                              "sources": ["email", "detections"]}
    cloudsec_entity_activity {"entity_id": "eh_nfzxiyltmrzgs43t",
                              "sources": ["detections", "sensor", "cloud"]}
    ```

=== "API"

    ```bash
    BASE="https://api.limacharlie.io/v1/cloudsec/$OID/entities"

    curl -s -X POST "$BASE/resolve" \
      -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" \
      -d '{"identifiers": [{"value": "alice@example.com"}]}'

    curl -s -H "Authorization: Bearer $JWT" \
      "$BASE/eu_k5xw4zdpnvsxe3tl?sightings_days=30"

    curl -s -H "Authorization: Bearer $JWT" \
      "$BASE/eu_k5xw4zdpnvsxe3tl/activity?sources=email,detections"

    curl -s -H "Authorization: Bearer $JWT" \
      "$BASE/eh_nfzxiyltmrzgs43t/activity?sources=detections,sensor,cloud"
    ```

The same walk works from any starting identifier: a hostname, an IP address
(add `at` for a past time), a sensor ID or a GitHub login. Each step needs the
permissions in the [table above](#permissions).

## Add Intune device evidence

The optional Entra application grant
`DeviceManagementManagedDevices.Read.All` enables managed-device inventory,
reported device posture and ownership associations. See
[Entra setup](provider-setup/entra.md#intune-managed-device-inventory-optional).
Without it, directory identities and the rest of the provider continue working;
Intune device evidence is unavailable rather than evidence of no devices.
