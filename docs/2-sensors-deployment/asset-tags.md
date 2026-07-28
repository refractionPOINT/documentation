# Asset Tag Namespace (`lc:asset:*`)

`lc:asset:*` is a reserved namespace for sensor tags. It marks endpoints with structured asset metadata: criticality, network exposure, environment, owner, compliance regimes, and OS. The namespace is a convention on top of [Sensor Tags](sensor-tags.md). There is no separate field on the sensor model, no migration to run, and no schema to extend for each surface. Any LimaCharlie surface that needs asset context (Vulnerabilities, D&R, Cases, Search, Query Console, Outputs, etc.) reads the same tags and gets a consistent view.

The first consumer of the namespace is the [Vulnerability Reporting extension](../5-integrations/extensions/limacharlie/vulnerability-reporting.md). It uses `lc:asset:criticality:*` for risk scores and SLA windows. Other surfaces will adopt the same parser when they need asset context.

## Why tags

LimaCharlie tags are already the metadata mechanism that all sensors share:

- They are visible on every event under `routing.tags`.
- They are queryable in D&R rules, sensor selectors, LCQL, and the API.
- You can apply them at enrollment time, with mass-tagging selectors, with D&R response actions, or manually in the web app and the CLI.

A new field on the sensor model for asset metadata would need schema changes, adoption in each surface, and a separate write path. A tag convention avoids all of that. Every surface that already understands tags gets the new metadata with no more work.

## Schema

The namespace defines six tag prefixes. The value comes after the prefix, as a third colon-separated segment.

| Tag | Values | Cardinality | Purpose |
|---|---|---|---|
| `lc:asset:criticality:<v>` | `critical`, `high`, `medium`, `low` | Singleton | Asset importance. Used as a multiplier for the risk score, and for the priority sort and the SLA windows. |
| `lc:asset:exposure:<v>` | `internet-facing`, `dmz`, `internal` | Singleton | Network reachability. Used for the risk score and the filter chips. |
| `lc:asset:env:<v>` | `prod`, `staging`, `dev`, `test` | Singleton | Environment. Used for filters and for the scope of suppression. |
| `lc:asset:owner:<v>` | Free text | Singleton | The routing target for assignment and paging (for example, a team name, an email, or a Slack handle). |
| `lc:asset:compliance:<v>` | Free text (for example, `pci`, `hipaa`, `sox`, `gdpr`) | Multi-value | The compliance regimes that apply to the asset. A sensor can have more than one. |
| `lc:asset:os:<distro>-<release>` | Free text (for example, `debian-11`, `redhat-enterprise-9`) | Singleton | Linux distribution and release. This lets the [Vulnerability Reporting extension](../5-integrations/extensions/limacharlie/vulnerability-reporting.md#linux-distro-aware-matching) apply distro backport data, so it does not flag backported security fixes as vulnerable. Split on the **last** `-`. |

### Validation rules

The closed-set fields (`criticality`, `exposure`, `env`) accept only the values in the table above. The parser drops tags with malformed or unknown values for those fields. This stops a typo such as `lc:asset:criticality:hi` from creating a phantom bucket in dashboards or SLAs.

`owner` and `compliance` accept any non-empty value after the prefix.

If a sensor has more than one tag for the same singleton field, the parser picks the first match in lexical order. For example, a sensor can have both `lc:asset:env:prod` and `lc:asset:env:staging`. The result is deterministic, but do not depend on it. Correct the tags instead.

In JSON output, `compliance` values are deduplicated and sorted alphabetically. `lc:asset:compliance:pci` and `lc:asset:compliance:hipaa` therefore always give `["hipaa","pci"]` in any tag order.

## Applying tags

Use the [`limacharlie` CLI](../6-developer-guide/cli.md), or the equivalent API calls in [Sensor Tags](sensor-tags.md).

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

Mass-tagging is the practical method for any environment that is not small. The selector uses [sensor selector expressions](../8-reference/sensor-selector-expressions.md).

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

Tags that you apply with mass-add are persistent (no TTL), unless you give `--ttl`. The mass-add command is idempotent, so you can run it again.

### Apply at enrollment time

An installation key can carry a fixed list of tags. These tags are applied to every sensor that enrolls with that key. Put the asset metadata in a separate key for each asset class, for example one key for each combination of environment and criticality. The sensor then gets the metadata when it connects.

### Apply via D&R rules

A D&R rule can add or remove tags as a response action. Use this when the telemetry shows the state of the asset. For example, tag a host as `lc:asset:exposure:internet-facing` when it starts to answer on a public IP, or as `lc:asset:env:prod` from a hostname pattern.

```yaml
respond:
  - action: add tag
    tag: lc:asset:env:prod
```

## How surfaces consume the tags

Each consumer surface uses a canonical parser. The parser converts the tag set of a sensor into a structured `AssetMetadata` object:

- **Go:** `ParseAssetMetadata(tags)` returns an `AssetMetadata` struct with `Criticality`, `Exposure`, `Env`, `Owner`, and `Compliance` fields. Extensions and backend services use this function.
- **TypeScript:** `parseAssetMetadataFromTags(tags)` has the same shape as the Go function. The LimaCharlie web app and any TypeScript SDK consumer use it.

The two implementations share the same prefix list, the same closed-set validation, and the same tie-breaking rules. A tag set therefore has the same interpretation across the platform.

If you request `include_tags=true`, the Vulnerability Reporting extension gives the parsed metadata in an `asset_metadata` field on every endpoint and finding. For the response shape, see the [Vulnerability Reporting extension page](../5-integrations/extensions/limacharlie/vulnerability-reporting.md).

## Override hatches

An organization that already has an asset taxonomy can map its tags into the canonical buckets. It does not have to tag the fleet again. One example is a long-standing `crown-jewel` / `tier-1` / `tier-3` scheme.

Today, the Vulnerability Reporting extension gives this override in a `criticality_tag_overrides` configuration field:

```json
{
  "criticality_tag_overrides": {
    "crown-jewel": "critical",
    "tier-1": "high",
    "tier-3": "low"
  }
}
```

The mapping is used only when the sensor has no canonical `lc:asset:criticality:*` tag. An explicit canonical tag always has priority, so an organization can migrate one step at a time. Keep the override map, apply canonical tags to the most important assets first, and remove the override entries when coverage grows.

An override value must be one of the four canonical buckets. Any other value is ignored at read time and rejected when the configuration is written.

Other surfaces will adopt the same override pattern, or an equivalent, when they consume the namespace.

## Sample real-world tagging

A hypothetical SaaS company runs four classes of assets. The tag plan:

| Asset class | Tags |
|---|---|
| Production app servers (public-facing, in PCI scope) | `lc:asset:criticality:critical`, `lc:asset:exposure:internet-facing`, `lc:asset:env:prod`, `lc:asset:compliance:pci`, `lc:asset:owner:platform-team` |
| Production database tier (internal, in PCI scope) | `lc:asset:criticality:critical`, `lc:asset:exposure:internal`, `lc:asset:env:prod`, `lc:asset:compliance:pci`, `lc:asset:owner:platform-team` |
| Staging cluster (DMZ, no compliance scope) | `lc:asset:criticality:medium`, `lc:asset:exposure:dmz`, `lc:asset:env:staging`, `lc:asset:owner:platform-team` |
| Engineering laptops (internal, dev work) | `lc:asset:criticality:low`, `lc:asset:exposure:internal`, `lc:asset:env:dev`, `lc:asset:owner:it-help` |
| HR file share (internal, in HIPAA + SOX scope) | `lc:asset:criticality:high`, `lc:asset:exposure:internal`, `lc:asset:env:prod`, `lc:asset:compliance:hipaa`, `lc:asset:compliance:sox`, `lc:asset:owner:hr-ops` |

Use `limacharlie tag mass-add` calls that key off existing infrastructure tags. Such tags include an installation key for each asset class, a hostname prefix, or a cloud-provider label that the cloud adapters propagate. You can classify the full fleet in one pass and keep it current as new sensors enroll.

## See Also

- [Sensor Tags](sensor-tags.md) — General tagging mechanism and API surface
- [Sensor Selector Expressions](../8-reference/sensor-selector-expressions.md) — Selector syntax used by mass-add
- [Vulnerability Reporting Extension](../5-integrations/extensions/limacharlie/vulnerability-reporting.md) — First consumer of the namespace
- [`limacharlie` CLI](../6-developer-guide/cli.md) — `tag add` / `tag mass-add` reference
