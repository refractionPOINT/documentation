# Entity Pivot

Entity Pivot connects identifiers from Cloud Security, endpoint security and
Email Security to **User** and **Host** entities. Start with an email address,
Windows account, GitHub user ID or login, hostname, IP address or sensor ID to find the known identities,
relationships and activity associated with it.

A User represents a principal, including a person, service account or shared
mailbox owner. A Host represents a machine, including an endpoint or cloud VM.
Ownership relates a User to a Host; they remain separate entities.

!!! note "Availability"
    The Entity Pivot API is available in every region for organizations with
    Cloud Security. The console page, MCP tools and CLI commands become available
    with their next releases. A `feature_disabled: true` response means the
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

Adapter associations have a separate enablement control, initially off. Existing
entity indexing can remain enabled while adapter sensors stay outside the entity
model. Supporting ingestion, schema and indexing versions must be enabled before
these associations appear; absence is not evidence of no adapter activity.

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
- `card: null` with `index_ready: true` means the entity ID is unknown in this
  organization. After a merge, `redirect_to` identifies the surviving entity;
  follow it instead of treating the old ID as missing.
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

## MCP and CLI

Once the supporting client versions are released, both `cloud_security` and
`cloud_security_readonly` MCP profiles provide these read-only tools:

| Tool | Purpose |
|---|---|
| `cloudsec_entity_pivot` | Resolve `identifier` (optional `type`, `at`), return cards for confirmed unambiguous matches and retain candidates. Possible or ambiguous candidates are not followed automatically. |
| `cloudsec_entity_search` | Search the `q` identifier prefix, optional `kind`, `limit` (1–100), `cursor`, returning one page with readiness and the next cursor. |
| `cloudsec_entity_activity` | Activity preview for `entity_id`, optional `since`, `until`, `sources`, preserving per-source status and truncation. |

The CLI command group is `limacharlie cloudsec entity`, with the following
subcommands. Availability depends on your installed release: check
`limacharlie cloudsec --help` first. A release without `entity` cannot run them;
use the API when its readers are available.

| Subcommand | Main selectors |
|---|---|
| `resolve` | Repeatable `--identifier`, optional `--type`, `--at`. |
| `get` | `--entity-id`, optional `--sightings-days`. |
| `search` | `--q`, optional `--kind`, `--limit`, `--cursor`. |
| `sightings` | `--entity-id`, optional `--kind`, `--since`, `--until`, `--limit`, `--cursor`. |
| `activity` | `--entity-id`, optional `--since`, `--until`, repeatable `--source`. |

Use the organization and output options described in [CLI](cli.md). Preserve
ambiguity, forbidden statuses, redirects and continuation cursors when scripting;
an empty preview is not evidence that nothing happened. See [MCP](mcp.md) for
profile setup.

## Add Intune device evidence

The optional Entra application grant
`DeviceManagementManagedDevices.Read.All` enables managed-device inventory,
reported device posture and ownership associations. See
[Entra setup](provider-setup/entra.md#intune-managed-device-inventory-optional).
Without it, directory identities and the rest of the provider continue working;
Intune device evidence is unavailable rather than evidence of no devices.
