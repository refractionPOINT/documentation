# Asset Tag Namespace (`lc:asset:*`)

`lc:asset:*` is a reserved sensor-tag namespace for marking endpoints with structured asset metadata — criticality, network exposure, environment, owner, compliance regimes, and OS. It is a convention layered on top of [Sensor Tags](sensor-tags.md): there is no separate field on the sensor model, no migration to run, and no per-surface schema to extend. Any LimaCharlie surface that needs asset context (Vulnerabilities, D&R, Cases, Search, Query Console, Outputs, etc.) reads the same tags and gets a consistent view.

The first consumer of the namespace is the [Vulnerability Reporting extension](../5-integrations/extensions/limacharlie/vulnerability-reporting.md), which uses `lc:asset:criticality:*` to drive risk scoring and SLA windows. Other surfaces will adopt the same parser as they need asset context.

## Why tags

LimaCharlie tags are already the cross-cutting metadata mechanism for sensors:

- They are visible on every event under `routing.tags`.
- They are queryable in D&R rules, sensor selectors, LCQL, and the API.
- They can be applied at enrollment time, by mass-tagging selectors, by D&R response actions, or manually through the web app and CLI.

Adding a new sensor-model field for asset metadata would require schema changes, per-surface adoption, and a separate write path. A tag convention sidesteps all of that: every surface that already understands tags inherits the new metadata for free.

## Schema

The namespace defines six tag prefixes. The value follows the prefix as a third colon-separated segment.

| Tag | Values | Cardinality | Purpose |
|---|---|---|---|
| `lc:asset:criticality:<v>` | `critical`, `high`, `medium`, `low` | Singleton | Asset importance. Used as a risk-score multiplier and to drive priority sort and SLA windows. |
| `lc:asset:exposure:<v>` | `internet-facing`, `dmz`, `internal` | Singleton | Network reachability. Feeds risk scoring and filter chips. |
| `lc:asset:env:<v>` | `prod`, `staging`, `dev`, `test` | Singleton | Environment for filtering and suppression scoping. |
| `lc:asset:owner:<v>` | Free text | Singleton | Routing target for assignment / paging (e.g. a team name, an email, a Slack handle). |
| `lc:asset:compliance:<v>` | Free text (e.g. `pci`, `hipaa`, `sox`, `gdpr`) | Multi-value | Compliance regimes the asset is subject to. A sensor can carry several at once. |
| `lc:asset:os:<distro>-<release>` | Free text (e.g. `debian-11`, `redhat-enterprise-9`) | Singleton | Linux distribution and release. Lets the [Vulnerability Reporting extension](../5-integrations/extensions/limacharlie/vulnerability-reporting.md#linux-distro-aware-matching) apply distro backport data so backported security fixes aren't flagged as vulnerable. Split on the **last** `-`. |

### Validation rules

The closed-set fields (`criticality`, `exposure`, `env`) only accept the values listed above. Tags with malformed or unknown values for those fields are dropped by the parser — this prevents typos like `lc:asset:criticality:hi` from creating a phantom bucket in dashboards or SLAs.

`owner` and `compliance` accept any non-empty value after the prefix.

If a sensor carries multiple tags for the same singleton field (for example, both `lc:asset:env:prod` and `lc:asset:env:staging`), the parser picks the first match in lexical order. This is deterministic but should be avoided — fix the tags rather than rely on the resolution order.

`compliance` values are deduplicated and sorted alphabetically when emitted as JSON, so `lc:asset:compliance:pci` plus `lc:asset:compliance:hipaa` always renders as `["hipaa","pci"]` regardless of tag order.

## Applying tags

Use the [`limacharlie` CLI](../6-developer-guide/cli.md) (or the API equivalents documented in [Sensor Tags](sensor-tags.md)).

### Tag a single sensor

```bash
limacharlie tag add --sid SENSOR_ID --tag lc:asset:criticality:critical
limacharlie tag add --sid SENSOR_ID --tag lc:asset:exposure:internet-facing
limacharlie tag add --sid SENSOR_ID --tag lc:asset:env:prod
limacharlie tag add --sid SENSOR_ID --tag lc:asset:owner:platform-team
limacharlie tag add --sid SENSOR_ID --tag lc:asset:compliance:pci
limacharlie tag add --sid SENSOR_ID --tag lc:asset:os:debian-11
```

### Tag a fleet by selector

Mass-tagging is the practical path for any non-trivial environment. The selector uses [sensor selector expressions](../8-reference/sensor-selector-expressions.md).

```bash
# All Linux production hosts: env=prod
limacharlie tag mass-add \
    --selector 'plat == "linux" and "prod" in tags' \
    --tag lc:asset:env:prod

# Engineering bench (already tagged 'bender') becomes dev
limacharlie tag mass-add \
    --selector '"bender" in tags' \
    --tag lc:asset:env:dev

# Internet-facing tier picked up via existing 'edge' tag
limacharlie tag mass-add \
    --selector '"edge" in tags' \
    --tag lc:asset:exposure:internet-facing

# All assets in the cardholder-data scope
limacharlie tag mass-add \
    --selector '"cde" in tags' \
    --tag lc:asset:compliance:pci
```

Tags applied via mass-add are persistent (no TTL) unless `--ttl` is passed. Re-running mass-add is idempotent.

### Apply at enrollment time

Installation keys can carry a fixed list of tags applied to every sensor that enrols against them. Bake the asset metadata into separate keys per asset class — for example, one key per environment + criticality combination — so the metadata lands the moment the sensor connects.

### Apply via D&R rules

D&R rules can add or remove tags as a response action. This is useful when asset state can be inferred from telemetry — for example, tagging a host as `lc:asset:exposure:internet-facing` when it starts answering on a public IP, or as `lc:asset:env:prod` based on a hostname pattern.

```yaml
respond:
  - action: add tag
    tag: lc:asset:env:prod
```

## How surfaces consume the tags

Each consumer surface uses a canonical parser that turns a sensor's tag set into a structured `AssetMetadata` object:

- **Go:** `ParseAssetMetadata(tags)` returns an `AssetMetadata` struct with `Criticality`, `Exposure`, `Env`, `Owner`, and `Compliance` fields. Used by extensions and backend services.
- **TypeScript:** `parseAssetMetadataFromTags(tags)` mirrors the Go shape for use in the LimaCharlie web app and any TypeScript SDK consumer.

Both implementations share the same prefix list, the same closed-set validation, and the same tie-breaking rules so a tag set is interpreted identically across the platform.

The Vulnerability Reporting extension exposes the parsed metadata under an `asset_metadata` field on every endpoint and finding when `include_tags=true` is requested. See the [extension page](../5-integrations/extensions/limacharlie/vulnerability-reporting.md) for the response shape.

## Override hatches

Organizations that already run an asset taxonomy (for example, a long-standing `crown-jewel` / `tier-1` / `tier-3` scheme) can map their existing tags into the canonical buckets without re-tagging the fleet.

Today the override is exposed by the Vulnerability Reporting extension as a `criticality_tag_overrides` configuration field:

```json
{
  "criticality_tag_overrides": {
    "crown-jewel": "critical",
    "tier-1": "high",
    "tier-3": "low"
  }
}
```

The mapping is consulted only when no canonical `lc:asset:criticality:*` tag is present on the sensor. Explicit canonical tags always win, so an org can migrate gradually: leave the override map in place, start applying canonical tags to the most important assets, and remove the override entries as coverage grows.

Override values must be one of the four canonical buckets; any other value is silently ignored at read time and rejected when the configuration is written.

Other surfaces will adopt the same override pattern (or its equivalent) as they consume the namespace.

## Sample real-world tagging

A hypothetical SaaS company runs four classes of assets. The tag plan:

| Asset class | Tags |
|---|---|
| Production app servers (public-facing, in PCI scope) | `lc:asset:criticality:critical`, `lc:asset:exposure:internet-facing`, `lc:asset:env:prod`, `lc:asset:compliance:pci`, `lc:asset:owner:platform-team` |
| Production database tier (internal, in PCI scope) | `lc:asset:criticality:critical`, `lc:asset:exposure:internal`, `lc:asset:env:prod`, `lc:asset:compliance:pci`, `lc:asset:owner:platform-team` |
| Staging cluster (DMZ, no compliance scope) | `lc:asset:criticality:medium`, `lc:asset:exposure:dmz`, `lc:asset:env:staging`, `lc:asset:owner:platform-team` |
| Engineering laptops (internal, dev work) | `lc:asset:criticality:low`, `lc:asset:exposure:internal`, `lc:asset:env:dev`, `lc:asset:owner:it-help` |
| HR file share (internal, in HIPAA + SOX scope) | `lc:asset:criticality:high`, `lc:asset:exposure:internal`, `lc:asset:env:prod`, `lc:asset:compliance:hipaa`, `lc:asset:compliance:sox`, `lc:asset:owner:hr-ops` |

Driven by `limacharlie tag mass-add` calls keyed off existing infrastructure tags (e.g. an installation key per asset class, a hostname prefix, a cloud-provider label propagated via the cloud adapters), the entire fleet can be classified in a single pass and kept current as new sensors enrol.

## See Also

- [Sensor Tags](sensor-tags.md) — General tagging mechanism and API surface
- [Sensor Selector Expressions](../8-reference/sensor-selector-expressions.md) — Selector syntax used by mass-add
- [Vulnerability Reporting Extension](../5-integrations/extensions/limacharlie/vulnerability-reporting.md) — First consumer of the namespace
- [`limacharlie` CLI](../6-developer-guide/cli.md) — `tag add` / `tag mass-add` reference
