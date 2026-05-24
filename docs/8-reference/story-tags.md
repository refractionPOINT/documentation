# Story Tag Namespace (`lc:story:*`)

`lc:story:*` is a reserved tag namespace for declaring **emergent graphs** of LimaCharlie components. A *story* is the union of components (Hive records) carrying `lc:story:STORY_NAME[:...]` tags within an org, plus the directed links those tags declare between them. There is no separate story record anywhere — the graph IS the tags.

The first consumer of the namespace is the LimaCharlie web app and the AI Sessions terminal, both of which render a story as a node-link diagram via the same shared `<StoryGraph>` component. The web app fetches the assembled story through a single API endpoint (`GET /v1/orgs/{oid}/stories/{name}`); the AI emits the matching card via `lc-card story`.

## Why tags

LimaCharlie tags are the cross-cutting metadata mechanism for every Hive record (D&R rules, playbooks, outputs, adapters, cloud sensors, lookups, etc.):

- They are visible on every record via the API and the web app.
- They can be added or removed by API, by CLI, by D&R rule responses, or by hand in the web app.
- Every surface that already understands tags inherits the new metadata for free.

Adding a story concept as a new top-level resource would require a schema, a write path, and per-surface adoption. A tag convention sidesteps all of that: any component that carries a tag is in the story. Remove the tag and the component leaves the story. The narrative is fully distributed and authored in place.

## Schema

The namespace defines four tag shapes. Each begins with `lc:story:` followed by the story name and zero or more colon-separated suffix segments.

| Tag                                                              | Meaning                                                                         | Where it lives                  |
|------------------------------------------------------------------|---------------------------------------------------------------------------------|---------------------------------|
| `lc:story:NAME`                                                  | The bearer is a member node of story `NAME`.                                    | On any tag-capable component.   |
| `lc:story:NAME:label:LABEL_SLUG`                                 | Override the display label of the bearer's node in story `NAME`.                | On the source (bearer) node.    |
| `lc:story:NAME:links:TARGET_TYPE:TARGET_NAME`                    | Declare a directed edge from the bearer to the `(TARGET_TYPE, TARGET_NAME)` target in story `NAME`. | On the source (bearer) node. |
| `lc:story:NAME:edge-label:TARGET_TYPE:TARGET_NAME:LABEL_SLUG`    | Label the edge above. Optional; paired with a matching `links:` tag.            | On the source (bearer) node.    |

### Implicit membership

**Any** tag matching `lc:story:NAME` or `lc:story:NAME:*` makes the bearer a member of story `NAME`. The bare `lc:story:NAME` tag adds no extra information beyond membership; it's still useful as a way to express *"this thing matters in the story even though it doesn't connect to anything"* (an isolated node).

### Charset rules

Every segment that isn't a fixed keyword has a strict regex:

| Segment       | Regex                              | Notes                                                              |
|---------------|------------------------------------|--------------------------------------------------------------------|
| `STORY_NAME`  | `^[a-z0-9][a-z0-9_-]{0,63}$`       | Lowercase, digits, underscore, hyphen. Starts alnum. Up to 64 chars. |
| `TARGET_TYPE` | one of the canonical type slugs    | See table below.                                                   |
| `TARGET_NAME` | `^[a-z0-9][a-z0-9_.-]{0,127}$`     | Same as `STORY_NAME` plus `.` (covers Hive record keys with dots).   |
| `LABEL_SLUG`  | `^[a-z0-9][a-z0-9_-]{0,63}$`       | Same as `STORY_NAME`. Rendered with `-` and `_` turned into spaces. |

Tags that violate any gate are **silently dropped** by the assembler — they never produce phantom nodes or edges. This matches the [`lc:asset:*`](asset-tags.md) convention: malformed metadata must never show up in a dashboard.

### Canonical type slugs

Used in `TARGET_TYPE` for `links:` and `edge-label:` tags, and as the `type` field of each rendered node. Stable identifiers — new slugs can be added but existing slugs must not be renamed.

| Category    | Slug              | Backing system              |
|-------------|-------------------|-----------------------------|
| Runtime     | `cloud-sensor`    | Hive `cloud_sensor`         |
| Runtime     | `adapter`         | Hive `external_adapter`     |
| Runtime     | `sensor`          | Endpoint sensor (reserved — see "Reservation" below) |
| Detection   | `dr-rule`         | Hive `dr-general` / `dr-managed` / `dr-service` |
| Detection   | `fp-rule`         | Hive `fp`                   |
| Detection   | `yara-rule`       | Hive `yara`                 |
| Response    | `playbook`        | Hive `playbook`             |
| Response    | `sop`             | Hive `sop`                  |
| Data flow   | `output`          | Output configuration        |
| Data flow   | `lookup`          | Hive `lookup`               |
| Data flow   | `payload`         | Payload configuration       |
| Config      | `extension`       | Installed extension subscription |
| Config      | `installation-key`| Installation key            |
| Config      | `secret`          | Hive `secret`               |
| Config      | `api-key`         | API key                     |
| IAM         | `user`            | User                        |
| IAM         | `role`            | Group / role                |
| Records     | `case`            | Case                        |
| Records     | `artifact`        | Artifact                    |
| Records     | `detection`       | Detection atom              |
| Records     | `vulnerability`   | Vulnerability finding       |
| AI          | `ai-agent`        | Hive `ai_agent`             |
| AI          | `ai-skill`        | Hive `ai_skill`             |
| AI          | `ai-memory`       | Hive `ai_memory`            |

### Drop rules (assembler)

Applied deterministically by the assembler when it walks the tag set:

1. **Charset gate failure** → drop the tag.
2. **Unknown `TARGET_TYPE`** → drop the tag (forward-compat: the table can grow without invalidating older clients).
3. **Component with an unknown root type** (not in the slug table) → drop the entire component.
4. **`edge-label:` without a matching `links:`** → drop (no phantom edges).
5. **Edge whose target isn't a member of the story** → drop the edge silently.
6. **Multiple `label:` tags on the same node** → lexically-first slug wins (mirrors the `lc:asset:*` tie-break).

### Label humanization

`LABEL_SLUG` values are rendered with `-` and `_` replaced by spaces. `web-server-fleet` becomes "web server fleet"; `triggers-alert` becomes "triggers alert". This keeps the slug safe to use inside a tag (which has restricted charset) while still producing readable labels in the rendered graph.

## Where stories surface

- **AI Sessions terminal** — the AI emits the StoryCard via `lc-card story --oid OID --name STORY_NAME` when the user asks to see a named story. The card fetches the assembled story from the API and renders the graph inline.
- **LimaCharlie web app** — any page that wants to render a story uses the same shared `StoryGraph` component. Future surfaces (an org-level "Story Library", per-extension landing pages) will plug into the same shape.
- **API** — `GET /v1/orgs/{oid}/stories` returns the catalog (story names found in the org). `GET /v1/orgs/{oid}/stories/{name}` returns the assembled `{ name, nodes, edges }` graph. Per-Hive read permissions are enforced server-side; the response is scoped to what the caller can read.

## Worked example

Three Hive records carry tags. Together they form the `prod-pipeline` story:

```text
# On D&R rule "exfil-detect" (Hive: dr-general):
lc:story:prod-pipeline
lc:story:prod-pipeline:label:exfiltration-detector
lc:story:prod-pipeline:links:playbook:respond
lc:story:prod-pipeline:edge-label:playbook:respond:triggers

# On Playbook "respond" (Hive: playbook):
lc:story:prod-pipeline:links:output:siem

# On Output "siem":
lc:story:prod-pipeline
```

Assembles to:

```json
{
  "name": "prod-pipeline",
  "nodes": [
    { "id": "dr-rule/exfil-detect", "type": "dr-rule",
      "name": "exfil-detect", "label": "exfiltration detector" },
    { "id": "output/siem",          "type": "output",   "name": "siem"    },
    { "id": "playbook/respond",     "type": "playbook", "name": "respond" }
  ],
  "edges": [
    { "from": "dr-rule/exfil-detect", "to": "playbook/respond", "label": "triggers" },
    { "from": "playbook/respond",     "to": "output/siem" }
  ]
}
```

## Applying tags

Use the [`limacharlie` CLI](../6-developer-guide/cli.md) or the API equivalents documented in [Sensor Tags](../2-sensors-deployment/sensor-tags.md). Tags can be added at the Hive record level via the standard tag editor in the web app, via the CLI, or via D&R rule responses.

### Tag a single Hive record

```bash
# Mark a D&R rule as part of the "prod-pipeline" story:
limacharlie hive set-tags --hive dr-general \
    --name exfil-detect \
    --tag lc:story:prod-pipeline \
    --tag lc:story:prod-pipeline:label:exfiltration-detector \
    --tag lc:story:prod-pipeline:links:playbook:respond
```

### Compose a multi-component story

A typical story spans several components. The pattern is the same regardless of component type:

```bash
# Source: cloud sensor → links → D&R rule
limacharlie hive set-tags --hive cloud_sensor --name web-fleet \
    --tag lc:story:detection-pipeline \
    --tag lc:story:detection-pipeline:links:dr-rule:exfiltration

# Source: D&R rule → links → playbook + output
limacharlie hive set-tags --hive dr-general --name exfiltration \
    --tag lc:story:detection-pipeline \
    --tag lc:story:detection-pipeline:links:playbook:quarantine \
    --tag lc:story:detection-pipeline:links:output:siem \
    --tag lc:story:detection-pipeline:edge-label:playbook:quarantine:triggers

# Sink: playbook (no outgoing links, still a member):
limacharlie hive set-tags --hive playbook --name quarantine \
    --tag lc:story:detection-pipeline

# Sink: output:
limacharlie hive set-tags --hive output --name siem \
    --tag lc:story:detection-pipeline
```

### Remove a component from a story

Untag the component. The next request for the story sees one fewer node and any edges pointing at it disappear (the assembler drops dangling edges).

## Reservation

The `sensor` type slug is reserved for endpoint sensors but not yet surfaced by the v1 assembler — endpoint sensor selectors only support exact tag matching, which would miss link-only sensors and break the implicit-membership rule. `links:sensor:SID` tags will parse successfully but the edge will be dropped at the dangling-edge step until the sensor side is wired up. Use `cloud-sensor` (which IS surfaced) for sensor-shaped components today.

Records (`case`, `artifact`, `detection`, `vulnerability`), IAM (`user`, `role`), and config singletons (`installation-key`, `api-key`) are similarly reserved and will surface as they're added to the assembler.

## See also

- [Asset Tags (`lc:asset:*`)](../2-sensors-deployment/asset-tags.md) — sister tag namespace for asset metadata; same drop-rule philosophy.
- [Sensor Tags](../2-sensors-deployment/sensor-tags.md) — the underlying tagging mechanism and API surface.
- [`limacharlie` CLI](../6-developer-guide/cli.md) — `hive set-tags` reference.
