# Entities

Entities connects identifiers from Cloud Security, endpoint security and Email
Security to **User** and **Host** entities. Start with an email address, Windows
account, GitHub user ID or login, hostname, IP address or sensor ID to find the
known identities, relationships and activity associated with it. This is also
called Entity Pivot.

A User represents a principal, including a person, service account or shared
mailbox owner. A Host represents a machine, including an endpoint or cloud VM.
Ownership relates a User to a Host; they remain separate entities.

Entities are built for any organization with Cloud Security from its LimaCharlie
sensors alone, so you do not need to connect a cloud or identity provider first.
Providers add directory identities, devices and cloud context to what the sensors
already provide.

Detection & Response rules and outputs can look up entities as events arrive; see
[Pivots in Rules and Outputs](rule-pivots.md).

!!! note "Requirements"
    Entities needs a Cloud Security subscription and the `cloudsec.get` permission.
    Without the subscription, the API answers HTTP 403. Other data on an entity
    needs the permissions in [Permissions](#permissions).

    The CLI group `limacharlie cloudsec entity` needs python-limacharlie 5.8.0 or
    later for every command and option on this page. The hosted MCP server has all
    six entity tools; a self-hosted MCP server needs v2.5.0 or later.

## Investigate an entity

Open **Entities** from the top level of the console sidebar and search with an
identifier prefix. Results are grouped into Users and Hosts. Search covers every
identifier type below, requires at least two characters (not counting leading or
trailing spaces) and accepts up to 512 UTF-8 bytes. You can also start from
Identity 360, a sensor page or an Email Security message's sender or mailbox
address.

The entity page shows:

- **Identifiers**, listed by type with their confidence and sources.
- **Ownership** relationships between Users and Hosts.
- **Recent activity**: accounts observed on hosts, with when, where and how they
  were observed, and why a row is unconfirmed.
- **Possible matches**, displayed separately as **unconfirmed**.
- **Telemetry sources**: adapter and Chrome browser profile sensors attached to
  the entity. See [Adapter identities](#adapter-identities-and-external-actors).
- **Also seen as** and **Cloud sign-ins**: [leads from adapter events](#leads-from-adapter-events).
- Cloud posture, and activity previews from other products: flagged email,
  detections, live sensor state and open cloud findings.

Unknown exposure or finding counts remain unknown. A source marked stale has not
supplied fresh verified evidence; its data may be out of date.

An identifier can belong to more than one entity. For example, several machines
can share a hostname or IP address. Inspect every candidate rather than choosing
the first result.

### Graph view

The search page and the entity page have a **List** / **Graph** switch. The graph
starts from the entities that match your search, or from the entity you are
viewing. Select **Show connections** on a User or Host to draw its neighbours:
owned Hosts, accounts active on or logged on to a Host, possible matches, attached
sensors, cloud resources, and, with `insight.evt.get`, vendor devices (**Also seen
as**) and cloud sign-ins. Unconfirmed links are drawn as possible. Large neighbourhoods fold into a
**+N more** node, and the graph stops growing at 600 nodes; narrow the search or
hide connections to see others.

## Worked investigation

A message from a suspicious sender reached `alice@example.com`. Which machine does
she own, what did it do, and is there cloud exposure? The values below are
synthetic. The fields named in each step are described in the
[Entities API reference](entities-api.md#response-reference).

1. **Resolve the mailbox to a User.** Search for the address in **Entities**, or
   resolve it with no `type`. One confirmed, unambiguous match gives a User ID such
   as `eu_k5xw4zdpnvsxe3tl`. If `ambiguous` is `true`, or the only candidates are
   in `possible`, stop and pick with evidence instead of taking the first.
2. **Read the User.** `relationships` with `rel: "owns"` and `direction: "out"`
   list the Hosts she owns, for example `eh_nfzxiyltmrzgs43t`. Check `redirect_to`
   and use it as the ID if present; it can name a different kind.
3. **Ask for activity.** For the User, `email` shows flagged mail to or from her
   confirmed addresses (judged malicious or suspicious, or dispositioned malicious
   or spam), not every message. `detections` and `sensor` include her owned Hosts.
   Then ask for the Host's `detections`, `sensor` and `cloud` sources. Read each
   `status` and `truncated` before concluding anything.

=== "CLI"

    ```bash
    # Resolve and fetch the card in one step.
    limacharlie cloudsec entity pivot --identifier alice@example.com --oid $OID

    # Or step by step.
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

With `insight.evt.get`, the Host card's `also_seen_as` and the `cloud_sign_ins` of
both cards add leads from adapter events, such as another product's record of the
same hostname and internal IP; see [Leads from adapter events](#leads-from-adapter-events).

The same walk works from any starting identifier: a hostname, an IP address
(add `at` for a past time), a sensor ID or a GitHub login. Each step needs the
permissions in the [table below](#permissions).

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
| `ad_account_short` | Windows account using a short domain label. A match is corroborated only when exactly one entity holds it and the caller has `insight.evt.get`; otherwise, and always for `AzureAD\` names, it is possible. |
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
Built-in system and machine accounts, such as `SYSTEM`, `NT AUTHORITY\...`,
Windows computer accounts ending in `$`, and Unix service accounts such as `root`,
`_spotlight` or `systemd-*`, are not recorded as activity.

## Permissions

Every entity route requires `cloudsec.get` and an enabled Cloud Security
subscription. Product links and previews use the caller's own permissions.

| Data | Additional permission or subscription |
|---|---|
| Endpoint sightings, recent endpoint activity, historical IP resolution | `insight.evt.get`. Without it, cards and resolution report `sightings: "forbidden"` and omit this evidence; the sightings route returns HTTP 403. |
| Email activity | `mailsec.get` and an enabled Email Security subscription. |
| Detections | `insight.det.get`. For a User without `insight.evt.get`, detections include attached adapter sensors and owned hosts, excluding hosts linked solely by endpoint activity. |
| Live sensor state | `sensor.get`. |
| Observed pivots (`also_seen_as`, `cloud_sign_ins`, `observed_matches`) | `insight.evt.get`, the same permission as sightings; no new permission. Without it the response reports `observations.status: "forbidden"` and the API runs no observation query. See [Leads from adapter events](#leads-from-adapter-events). |
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
  the survivor's ID. Use `redirect_to` as the ID from then on. The survivor can be
  a different kind from the ID you saved: the old `eh_` Host ID of a Chrome extension
  sensor redirects to the signed-in person's `eu_` User. Read `card.entity.kind`
  rather than assuming the kind of the ID you asked for. If the survivor has
  itself been retired, `card` is `null` and `redirect_to` names that retired
  entity: the ID was known and merged, but no current entity is left to show.
  A retired entity that was never merged is indistinguishable from an unknown ID.
- Each source behind a card reports its freshness. A missing successful
  collection time is unknown, not "never".
- Sightings are **best effort**, retained for up to 365 days. They cover events
  already collected from sensors; they are not a complete login audit. Interval
  endpoints are approximate, with refresh intervals of up to two hours for IPs
  and hostnames, and six hours for account observations. They do not prove
  continuous activity or absence outside the interval.
- A card's recent activity is a summary, not the complete history. Incompleteness
  markers on the entity disclose incomplete summaries or candidates. Use paged
  sightings for history and resolve for identifier candidates.
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

The [API reference](entities-api.md#readiness-and-freshness-fields) lists the
response fields behind these states.

## Where entity data comes from

LimaCharlie endpoint sensors supply hosts, the accounts observed on them and their
addresses. Connected identity and cloud providers add directory users, devices and
cloud resources. The sections below cover the other sources.

### Adapter identities and external actors

An adapter sensor can represent a user or device rather than an endpoint host.
Supported parsers declare this meaning automatically; a custom mapping can declare
`sensor_identity_type` alongside `sensor_key_path`. See
[Adapter usage](../2-sensors-deployment/adapters/usage.md#sensor-identity-declarations)
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
no adapter activity. Existing events and sensor names are not backfilled.

A User known only through an adapter is shown as an **External actor**
(`attrs.external: true`). This means no directory-backed observation has joined
that entity; it does not determine whether the actor is malicious. Directory-backed
users appear before external actors in search results. When directory evidence
joins the entity, the external designation is removed.

The entity page's **Telemetry sources** section lists attached adapter and Chrome
browser profile sensors, with sensor ID, platform, identity type, hostname and who
declared the identity: a built-in parser, or a customer mapping shown as
**unconfirmed**. Missing or unknown provenance remains unknown rather than trusted.
Sensor timeline links require `sensor.list`, `sensor.get` and either
`insight.evt.get` or `insight.evt.get.simple`, matching the destination timeline
permissions. An empty section means no attached adapter sources were reported,
not that the entity has never generated telemetry.

Detections activity includes the entity's attached adapter sensor IDs. The same
`insight.det.get` permission applies.

### Chrome browser profiles

A LimaCharlie Chrome extension sensor describes a browser profile, not a
machine. Its hostname is the profile's signed-in account followed by `@` and an
installation token (`alice@example.com@<32 hex characters>`).

- **Signed-in profile.** The sensor attaches to that person's **User** as a
  telemetry source (`identity_type: email`, `identity_source: parser`). It
  follows the same rules as a built-in parser `email` declaration and can join a
  matching directory identity. No machine identifier (hardware address, device ID, IP
  address) is asserted on that User, and the sensor does not create or join a Host.
- **Unsigned or invalid profile.** A profile with no account, or a hostname that is not
  recognized as an account plus token, stays a **Host**. The original label is
  still displayed.
- **Unmatched browser Users** are [external actors](#adapter-identities-and-external-actors)
  (`attrs.external: true`): no directory record matched. This is neither a
  maliciousness verdict nor a statement about whether the account belongs to a
  person, and `human` stays unknown.
- **Saved IDs.** An `eh_` Host ID saved before the sensor was attached to a User
  redirects to the User's `eu_` ID, so `redirect_to` can change the entity kind. See
  [Readiness](#readiness-history-and-incomplete-results).

The profile account is the one the browser was signed in to when the extension
started. It is current inventory evidence, not proof of who produced every
historical browser event.

### Leads from adapter events

Events that adapters deliver from **Sophos, CrowdStrike, Office 365, Entra ID,
Okta and Duo** are read for two kinds of record: devices as another product names
them (Sophos, CrowdStrike, Entra ID and Duo), and sign-ins (Office 365, Entra ID,
Okta and Duo). At read time the API joins them to existing Hosts and Users and
returns the result as **leads**. A lead is explained, approximate evidence to
start an investigation from. It never merges entities, assigns an owner or adds an
identifier, and nothing is stored as a relationship.

| Where | What you get |
|---|---|
| Host card, **Also seen as** (`also_seen_as`) | Device records from those products that may be this Host. |
| Host and User card, **Cloud sign-ins** (`cloud_sign_ins`) | Sampled sign-ins: on a Host, those whose source address one of its sensors also reported near the sign-in time; on a User, those by this person. |
| Resolve, `observation_selectors` | Look up a vendor device ID or a hostname another product reports. See [Look up a device with selectors](entities-api.md#look-up-a-device-with-selectors). |

All of this needs `insight.evt.get` (no new permission). Each panel shows at most
20 rows, newest day first, from the last 30 days; selectors look back up to 31 days.

- Only one case is `corroborated`: exactly one Host had a sensor that reported the
  same hostname **and** the same internal IP on the same UTC day. A public address
  never counts.
- Everything else is `possible`, unlinked or unknown: a hostname-only match,
  several qualifying Hosts, conflicting names, or missing evidence. Every
  qualifying Host is listed and none is selected for you.
- A sign-in's Hosts are always `possible`, even when there is only one: shared NAT,
  VPN or proxy egress identifies an office, not an endpoint.

**How to word a lead.** Describe it by its `reason`, for example "same hostname
and internal IP observed that day", and call it a "lead" or "possible". Do not say
"same machine" or "verified". Reused addresses and names, NAT, VPN and cloned
machines can produce a wrong lead even when it is the only one.

`observations.status` tells you whether the lookup completed. `incomplete`,
`unavailable` and `forbidden` never mean "none". The
[API reference](entities-api.md#leads-in-responses) describes every field and
reason.

### Intune device evidence

The optional Entra application grant
`DeviceManagementManagedDevices.Read.All` enables managed-device inventory,
reported device posture and ownership associations. See
[Entra setup](provider-setup/entra.md#intune-managed-device-inventory-optional).
Without it, directory identities and the rest of the provider continue working;
Intune device evidence is unavailable rather than evidence of no devices.

## MCP and CLI

These MCP tools are read-only. All six are in the `cloud_security`,
`cloud_security_readonly`, `historical_data`, `historical_data_readonly`,
`email_security` and `email_security_readonly` profiles, so an email or
historical-data investigation can pivot without switching profile.

| Tool | Arguments | Purpose |
|---|---|---|
| `cloudsec_entity_pivot` | `identifier` (required), optional `type`, `at`, `observation_selectors` | The default for "what is this identifier?". Resolves one identifier, then returns the cards of its confirmed, unambiguous matches (at most 10) in `cards`. The resolve results stay in `candidates`; possible and ambiguous candidates are never followed automatically. Also returns `index_ready`, `sources`, any other top-level resolve fields (such as `observed_matches` and `observations`), `truncated` and, for a card that failed to load, `card_errors`. |
| `cloudsec_entity_resolve` | `identifiers` (required, 1–100 objects with `value` and optional `type`), optional `at`, `observation_selectors` | Batch resolution only: candidates for every input, no cards. The [resolve response](entities-api.md#resolve) unchanged. |
| `cloudsec_entity_get` | `entity_id` (required), optional `sightings_days` (1–365) | One entity card with `index_ready`, `redirect_to`, `sightings` and `observations`, unchanged. |
| `cloudsec_entity_search` | `q` (required), optional `kind`, `limit` (1–100), `cursor` | One page of identifier-prefix search with readiness and the next cursor. |
| `cloudsec_entity_sightings` | `entity_id` (required), optional `kind`, `since`, `until`, `limit` (1–500), `cursor` | One page of best-effort sightings. Needs `insight.evt.get`. |
| `cloudsec_entity_activity` | `entity_id` (required), optional `since`, `until`, `sources` | Activity preview, preserving per-source status and truncation. |

Arguments follow the [API routes](entities-api.md#api-routes). `type` takes one of the
[identifier types](#identifiers-and-confidence). `observation_selectors` is an
array of at most four [selector objects](entities-api.md#look-up-a-device-with-selectors),
passed to the API as given; the API validates platforms and values. The `at`
argument also pins the day those selectors examine.

The CLI command group is `limacharlie cloudsec entity` (python-limacharlie 5.8.0
or later). Each subcommand answers `--ai-help` with guidance on its purpose and
response fields.

| Subcommand | Main selectors |
|---|---|
| `pivot` | `--identifier` (one value), optional `--type`, `--at`, repeatable `--foreign-hostname` and `--observation-selector`. Resolves the identifier and fetches cards the same way as `cloudsec_entity_pivot`. |
| `resolve` | Repeatable `--identifier`, optional `--type`, `--at`, repeatable `--foreign-hostname` and `--observation-selector`. |
| `get` | `--entity-id`, optional `--sightings-days`. |
| `search` | `--q`, optional `--kind`, `--limit`, `--cursor`. |
| `sightings` | `--entity-id`, optional `--kind`, `--since`, `--until`, `--limit`, `--cursor`. |
| `activity` | `--entity-id`, optional `--since`, `--until`, repeatable `--source`. |

`--foreign-hostname NAME` adds a `foreign_hostname` selector. `--observation-selector JSON`
takes one selector as a JSON object, such as
`'{"type":"vendor_device_id","platform":"sophos","value":"<device id>"}'`. Both can
be repeated, up to four selectors in total, and both subcommands still need an
`--identifier`.

Use the organization and output options described in [CLI](cli.md). Preserve
ambiguity, forbidden statuses, redirects and continuation cursors when scripting;
an empty preview is not evidence that nothing happened. See [MCP](mcp.md) for
profile setup.

## API

The REST routes, every request parameter and every response field are in the
[Entities API reference](entities-api.md).
