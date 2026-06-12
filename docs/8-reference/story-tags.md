# Story Tag Namespace (`lc:story:*`)

`lc:story:*` is a reserved tag namespace for declaring **emergent graphs** of LimaCharlie components. A *story* is the union of components (Hive records) carrying `lc:story:STORY_NAME[:...]` tags within an org, plus the directed edges between them. There is no separate story record anywhere — membership IS the tags. Edges come from two places: most are **derived** by the assembler from the member records' own configuration, and the rest are **declared** with `links:` tags (see [Edge ontology](#edge-ontology)).

The first consumer of the namespace is the LimaCharlie web app and the AI Sessions terminal, both of which render a story as a node-link diagram via the same shared `<StoryGraph>` component. The web app fetches the assembled story through a single API endpoint (`GET /v1/orgs/{oid}/stories/{name}`); the AI emits the matching card via `lc-card story`.

## Why tags

LimaCharlie tags are the cross-cutting metadata mechanism for every Hive record (D&R rules, playbooks, adapters, cloud sensors, lookups, etc.):

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
| `LABEL_SLUG`  | `^(?:[a-z0-9]\|[a-z0-9][a-z0-9_-]{0,62}[a-z0-9])$` | Like `STORY_NAME`, but no trailing `-`/`_` (a trailing separator would humanize to a trailing space). Rendered with `-` and `_` turned into spaces — see [Label humanization](#label-humanization). |

Tags that violate any gate are **silently dropped** by the assembler — they never produce phantom nodes or edges. This matches the [`lc:asset:*`](../2-sensors-deployment/asset-tags.md) convention: malformed metadata must never show up in a dashboard.

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
| Config      | `extension`       | Installed extension subscription (reserved — see [Reservation](#reservation)) |
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
3. **`links:`/`edge-label:` pair not in the allowed-pair matrix** → drop the tag (see [Declared edges](#declared-edges-and-the-allowed-pair-matrix)).
4. **Component with an unknown root type** (not in the slug table) → drop the entire component.
5. **`edge-label:` without a matching `links:`** → drop (no phantom edges).
6. **Edge whose target isn't a member of the story** → drop the edge silently (applies to derived edges too).
7. **Multiple `label:` tags on the same node** → lexically-first slug wins (mirrors the `lc:asset:*` tie-break).

Membership nuance: rules 1–2 reject the tag at parse time, so a rejected tag confers nothing — not even membership. Rule 3 voids only the edge semantics: the tag parsed successfully, so the bearer remains a member of the story.

### Label humanization

`LABEL_SLUG` values render with `-` and `_` replaced by spaces (`web-server-fleet` → "web server fleet"), but the two label kinds are humanized at different layers:

- **Node labels** are humanized by the assembler: the API payload carries `"label": "web server fleet"` for a `label:web-server-fleet` tag.
- **Edge labels** stay in slug form in the API payload (`"label": "writes-to"`) so they double as stable identifiers; the rendering surface humanizes them (`StoryGraph` renders "writes to").

This keeps the slug safe to use inside a tag (which has restricted charset) while still producing readable labels in the rendered graph.

## Edge ontology

Edges are facts about how components connect; membership is curation of what belongs in the picture. The assembler keeps those responsibilities separate:

- **Derived edges** are computed by the assembler from the member records' own configuration — ARLs, extension requests, and name references that are already written down in the resource definitions. They require no tags, and they can never go stale: edit a rule to call a different playbook and the story updates on the next fetch.
- **Declared edges** come from `links:` tags and cover relationships that exist operationally but are not expressed in any configuration (telemetry feeding a detection, an agent writing to its memory).

Every edge in the assembled story carries an `origin` field: `"derived"` or `"declared"`.

### Derived edges

For each member, the assembler inspects the record content and emits an edge when it finds one of the reference patterns below **and the target is also a member of the story**. A reference to a non-member never pulls the target into the story — membership stays curated.

| Source | Target | Label | Derived from |
|---|---|---|---|
| `dr-rule` | `lookup` | `consults` | `op: lookup` with `hive://lookup/NAME` or `lcr://lookup/NAME` in the detect logic |
| `dr-rule` | `yara-rule` | `scans-with` | `hive://yara/NAME` in a respond task (e.g. `yara_scan`) |
| `dr-rule` | `ai-agent` | `starts` | `action: start ai agent` with `definition: hive://ai_agent/NAME`, or `extension request` to `ext-feedback` with `feedback_destination: ai_agent` carrying an `ai_agent_name:` |
| `dr-rule` | `playbook` | `runs` | `extension request` to `ext-playbook` (`name:` in the request) or `ext-feedback` (`playbook_name:`), or any `hive://playbook/NAME` reference |
| `dr-rule` | `extension` | `invokes` | `action: extension request` with `extension name: NAME` (reserved — `extension` nodes don't surface, see [Reservation](#reservation)) |
| `dr-rule` | `secret` | `authenticates-with` | `hive://secret/NAME` (e.g. inline `start ai agent` credentials) |
| `dr-rule` | `output` | `forwards-to` | `action: output` with `name: NAME` (lands once `output` nodes surface) |
| `fp-rule` | `dr-rule` | `suppresses` | fp logic (which sits at the record root) comparing `path: cat` with `op: is` — exact matches only — against a name the rule `report`s |
| `cloud-sensor` | `secret` | `authenticates-with` | `hive://secret/NAME` in the sensor configuration |
| `adapter` | `secret` | `authenticates-with` | `hive://secret/NAME` in the adapter configuration |
| `ai-agent` | `secret` | `authenticates-with` | `anthropic_secret`, `lc_api_key_secret`, etc. |
| `playbook` | `lookup` / `yara-rule` | `uses` | `hive://...` ARLs found in the playbook code (best-effort) |
| `playbook` | `secret` | `authenticates-with` | `hive://secret/NAME` in the playbook code (best-effort) |
| `playbook` | `playbook` | `runs` | `hive://playbook/NAME` in the playbook code (best-effort) |
| `playbook` | `ai-agent` | `starts` | `hive://ai_agent/NAME` in the playbook code (best-effort) |

The mechanism is uniform: any `hive://HIVE/NAME` (or `lcr://lookup/NAME`) string in a member's record content, where `HIVE` maps to a canonical type slug, produces a candidate edge — plus three structural extractors that don't use ARLs and apply to `dr-rule` members (extension requests by name, `action: output` by name, fp `cat` matching).

**Do not declare `links:` tags for these relationships.** The platform draws them for you; a declared duplicate changes nothing except flipping the edge's `origin` to `"declared"` (see [Precedence](#precedence-and-de-duplication)).

### Declared edges and the allowed-pair matrix

`links:` tags are reserved for relationships no configuration expresses. Each `(bearer type → TARGET_TYPE)` pair must appear in the matrix below; a `links:` or `edge-label:` tag with a pair outside the matrix is silently dropped (drop rule 3). The matrix is a superset of the derived pairs — manually declaring a derivable edge stays valid (useful when the config reference doesn't exist yet).

| Source | Allowed targets (default edge label) |
|---|---|
| `sensor`, `cloud-sensor`, `adapter` | `dr-rule`, `fp-rule`, `yara-rule` (`telemetry`); `ai-agent` (`triggers`); `output` (`forwards-to`); `secret` (`authenticates-with`); `installation-key` (`enrolls-with`) |
| `dr-rule` | `lookup` (`consults`); `yara-rule` (`scans-with`); `ai-agent` (`starts`); `playbook` (`runs`); `extension` (`invokes`); `secret` (`authenticates-with`); `output` (`forwards-to`); `payload` (`deploys`); `sop` (`documented-by`); `case` (`files`); `detection` (`reports`) |
| `fp-rule` | `dr-rule` (`suppresses`) |
| `yara-rule` | `dr-rule` (`triggers`) |
| `playbook` | `output` (`writes-to`); `lookup` (`uses`); `yara-rule` (`uses`); `secret` (`authenticates-with`); `payload` (`deploys`); `ai-agent` (`starts`); `playbook` (`runs`); `extension` (`invokes`); `sop` (`follows`); `case` (`files`); `artifact` (`files`); `detection` (`reports`) |
| `ai-agent` | `ai-memory` (`remembers`); `ai-skill` (`uses`); `sop` (`follows`); `output` (`writes-to`); `playbook` (`runs`); `ai-agent` (`starts`); `extension` (`invokes`); `secret` (`authenticates-with`); `case` (`files`); `artifact` (`files`); `detection` (`reports`) |
| `extension` | `dr-rule`, `fp-rule`, `yara-rule`, `lookup`, `output`, `playbook` (`manages`) |
| `user` | `role` (`member-of`); `api-key` (`owns`) |
| `detection`, `vulnerability`, `artifact` | `case` (`escalates-to`) |

Direction convention: data-flow edges point the way data moves (telemetry → detection → response → sink); dependency edges point from the consumer to the dependency (`dr-rule → lookup`, `adapter → secret`).

**Migration note:** before the matrix, any pair of known slugs was a valid `links:` target. Existing tags whose pair falls outside the matrix keep conferring membership, but their edges no longer render. Re-point or remove them — and if a legitimate pair is missing from the matrix, it can be added (the matrix can grow; pairs are never removed).

### Canonical edge labels

Derived edges always carry the canonical label for their pair. Declared edges without an `edge-label:` tag get the pair's default label filled in by the assembler — so an unlabeled `links:` tag still renders consistently. An explicit `edge-label:` overrides the default; any charset-valid slug is accepted, but stick to the vocabulary unless you have a strong reason:

`telemetry`, `triggers`, `starts`, `runs`, `invokes`, `consults`, `scans-with`, `suppresses`, `forwards-to`, `writes-to`, `reports`, `authenticates-with`, `enrolls-with`, `manages`, `uses`, `remembers`, `follows`, `deploys`, `documented-by`, `files`, `escalates-to`, `member-of`, `owns`

### Precedence and de-duplication

If the same `(from, to)` edge is both derived and declared, the assembler emits a single edge: `origin` is `"declared"`, and the label is the declared `edge-label:` if present, otherwise the canonical default for the pair.

## Where stories surface

- **AI Sessions terminal** — the AI emits the StoryCard via `lc-card story --oid OID --name STORY_NAME` when the user asks to see a named story. The card fetches the assembled story from the API and renders the graph inline.
- **LimaCharlie web app** — any page that wants to render a story uses the same shared `StoryGraph` component. Future surfaces (an org-level "Story Library", per-extension landing pages) will plug into the same shape.
- **API** — `GET /v1/orgs/{oid}/stories` returns the catalog (story names found in the org). `GET /v1/orgs/{oid}/stories/{name}` returns the assembled `{ name, nodes, edges }` graph; each edge carries an `origin` field (`"derived"` or `"declared"`). Per-Hive read permissions are enforced server-side; the response is scoped to what the caller can read.

## Worked example

Three Hive records carry tags. Together they form the `prod-pipeline` story:

```text
# On D&R rule "exfil-detect" (Hive: dr-general):
lc:story:prod-pipeline
lc:story:prod-pipeline:label:exfiltration-detector
lc:story:prod-pipeline:links:playbook:respond

# On Playbook "respond" (Hive: playbook):
lc:story:prod-pipeline:links:ai-agent:triage

# On AI agent "triage" (Hive: ai_agent):
lc:story:prod-pipeline
```

Assembles to:

```json
{
  "name": "prod-pipeline",
  "nodes": [
    { "id": "ai-agent/triage",      "type": "ai-agent", "name": "triage"  },
    { "id": "dr-rule/exfil-detect", "type": "dr-rule",
      "name": "exfil-detect", "label": "exfiltration detector" },
    { "id": "playbook/respond",     "type": "playbook", "name": "respond" }
  ],
  "edges": [
    { "from": "dr-rule/exfil-detect", "to": "playbook/respond",
      "label": "runs", "origin": "declared" },
    { "from": "playbook/respond", "to": "ai-agent/triage",
      "label": "starts", "origin": "declared" }
  ]
}
```

Neither `links:` tag carries an `edge-label:`, so the assembler fills in the canonical default for each pair (`dr-rule → playbook` is `runs`, `playbook → ai-agent` is `starts`). And if `exfil-detect`'s respond block actually invoked the playbook via `ext-playbook`, the first `links:` tag would be unnecessary — the edge would appear automatically with `"origin": "derived"`.

## Applying tags

Use the [`limacharlie` CLI](../6-developer-guide/cli.md) or the API equivalents documented in [Sensor Tags](../2-sensors-deployment/sensor-tags.md). Tags can be added at the Hive record level via the standard tag editor in the web app, via the CLI, or via D&R rule responses.

The workflow is: **tag membership on everything, declare only the edges no config expresses.** If a member's configuration already references another member (a rule's `hive://lookup/...`, an adapter's `hive://secret/...`, an `extension request`), the edge is derived automatically — adding a `links:` tag for it is redundant.

### Tag a single Hive record

```bash
# Mark a D&R rule as part of the "prod-pipeline" story:
limacharlie hive set --hive-name dr-general \
    --key exfil-detect \
    --tag-add lc:story:prod-pipeline \
    --tag-add lc:story:prod-pipeline:label:exfiltration-detector
```

### Compose a multi-component story

A typical story spans several components. Membership tags go on everything; the only `links:` tag needed here is the telemetry edge, because "this sensor's data feeds this rule" is not written in any config:

```bash
# Cloud sensor: member + declared telemetry edge to the rule
limacharlie hive set --hive-name cloud_sensor --key web-fleet \
    --tag-add lc:story:detection-pipeline \
    --tag-add lc:story:detection-pipeline:links:dr-rule:exfiltration

# D&R rule: member only — its detect consults hive://lookup/threat-domains
# and its respond invokes the playbook via ext-playbook, so those edges
# are derived.
limacharlie hive set --hive-name dr-general --key exfiltration \
    --tag-add lc:story:detection-pipeline

# Playbook: member only
limacharlie hive set --hive-name playbook --key quarantine \
    --tag-add lc:story:detection-pipeline

# Lookup: member only
limacharlie hive set --hive-name lookup --key threat-domains \
    --tag-add lc:story:detection-pipeline
```

The assembled graph: `web-fleet —telemetry→ exfiltration` (declared), `exfiltration —runs→ quarantine` (derived), `exfiltration —consults→ threat-domains` (derived).

### Remove a component from a story

Untag the component. The next request for the story sees one fewer node and any edges pointing at it disappear (the assembler drops dangling edges).

## Reservation

The `sensor` type slug is reserved for endpoint sensors but not yet surfaced by the v1 assembler — endpoint sensor selectors only support exact tag matching, which would miss link-only sensors and break the implicit-membership rule. `links:sensor:SID` tags will parse, but no allowed-pair matrix row currently *targets* `sensor`, so the tag is dropped at the matrix gate (drop rule 3); a matrix row will be added when the sensor side is wired up. Use `cloud-sensor` (which IS surfaced) for sensor-shaped components today.

Data-flow singletons (`output`, `payload`), Records (`case`, `artifact`, `detection`, `vulnerability`), IAM (`user`, `role`), and config singletons (`installation-key`, `api-key`) are similarly reserved — they are not Hive-backed today, so they cannot carry tags or appear as nodes, and edges pointing at them are dropped at the dangling-edge step. They will surface as they're added to the assembler.

`extension` is also reserved, for a different reason: its backing hive (`extension_subscription`) is internal — **never tag extension subscription records**. Extension nodes don't surface, and edges targeting `extension` drop at the dangling-edge step. Model an extension-mediated flow through its visible components instead — e.g. ext-feedback's webhook cloud sensor declaring `links:ai-agent:...` (`triggers`), while the rule→agent leg derives from the `ai_agent_name` in the extension request.

## See also

- [Asset Tags (`lc:asset:*`)](../2-sensors-deployment/asset-tags.md) — sister tag namespace for asset metadata; same drop-rule philosophy.
- [Sensor Tags](../2-sensors-deployment/sensor-tags.md) — the underlying tagging mechanism and API surface.
- [`limacharlie` CLI](../6-developer-guide/cli.md) — `hive set` (`--tag-add`/`--tag-rm`) reference.
