# Story Tag Namespace (`lc:story:*`)

`lc:story:*` is a reserved tag namespace that declares **emergent graphs** of LimaCharlie components. A *story* is the set of components (Hive records) in an org that carry `lc:story:STORY_NAME[:...]` tags, plus the directed edges between them. No separate story record exists — the tags are the membership. Edges come from two places. The assembler **derives** most edges from the configuration of the member records. You **declare** the rest with `links:` tags (see [Edge ontology](#edge-ontology)).

The first consumers of the namespace are the LimaCharlie web app and the AI Sessions terminal. Both render a story as a node-link diagram with the same shared `<StoryGraph>` component. The web app fetches the assembled story from one API endpoint (`GET /v1/orgs/{oid}/stories/{name}`). The AI emits the matching card with `lc-card story`.

## Why tags

LimaCharlie tags are the common metadata mechanism for every Hive record (D&R rules, playbooks, adapters, cloud sensors, lookups, etc.):

- The API and the web app show them on every record.
- You can add or remove them with the API, with the CLI, with D&R rule responses, or by hand in the web app.
- Every surface that already understands tags gets the new metadata.

A story as a new top-level resource would need a schema, a write path, and adoption by each surface. A tag convention avoids all of that: any component that carries a tag is in the story. Remove the tag, and the component leaves the story. The narrative is distributed, and you author it in place.

## Schema

The namespace defines four tag shapes. Each shape starts with `lc:story:`, then the story name, then zero or more suffix segments that colons separate.

| Tag                                                              | Meaning                                                                         | Where it lives                  |
|------------------------------------------------------------------|---------------------------------------------------------------------------------|---------------------------------|
| `lc:story:NAME`                                                  | The bearer is a member node of story `NAME`.                                    | On any tag-capable component.   |
| `lc:story:NAME:label:LABEL_SLUG`                                 | Override the display label of the bearer's node in story `NAME`.                | On the source (bearer) node.    |
| `lc:story:NAME:links:TARGET_TYPE:TARGET_NAME`                    | Declare a directed edge from the bearer to the `(TARGET_TYPE, TARGET_NAME)` target in story `NAME`. | On the source (bearer) node. |
| `lc:story:NAME:edge-label:TARGET_TYPE:TARGET_NAME:LABEL_SLUG`    | Label the edge above. Optional. Use it with a matching `links:` tag.            | On the source (bearer) node.    |

### Implicit membership

**Any** tag that matches `lc:story:NAME` or `lc:story:NAME:*` makes the bearer a member of story `NAME`. The bare `lc:story:NAME` tag adds no information other than membership. It is still useful to show that *a component matters in the story but connects to nothing* (an isolated node).

### Charset rules

Every segment that is not a fixed keyword has a strict regex:

| Segment       | Regex                              | Notes                                                              |
|---------------|------------------------------------|--------------------------------------------------------------------|
| `STORY_NAME`  | `^[a-z0-9][a-z0-9_-]{0,63}$`       | Lowercase, digits, underscore, hyphen. Starts alnum. Up to 64 chars. |
| `TARGET_TYPE` | one of the canonical type slugs    | See table below.                                                   |
| `TARGET_NAME` | `^[a-z0-9][a-z0-9_.-]{0,127}$`     | Same as `STORY_NAME` plus `.` (covers Hive record keys with dots).   |
| `LABEL_SLUG`  | `^(?:[a-z0-9]\|[a-z0-9][a-z0-9_-]{0,62}[a-z0-9])$` | Like `STORY_NAME`, but no trailing `-`/`_` (a trailing separator humanizes to a trailing space). The `-` and `_` characters become spaces — see [Label humanization](#label-humanization). |

The assembler **silently drops** each tag that fails a gate. Such tags never produce phantom nodes or edges. This matches the [`lc:asset:*`](../2-sensors-deployment/asset-tags.md) convention: malformed metadata must never appear in a dashboard.

### Canonical type slugs

These slugs go in `TARGET_TYPE` for `links:` and `edge-label:` tags, and in the `type` field of each rendered node. The slugs are stable identifiers. New slugs can be added, but existing slugs must not be renamed.

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
| Interface   | `app`             | Hive `app` (sandboxed iframe mini-app / dashboard) |

### Drop rules (assembler)

The assembler applies these rules deterministically when it reads the tag set:

1. **Charset gate failure** → drop the tag.
2. **Unknown `TARGET_TYPE`** → drop the tag (forward-compat: the table can grow without invalidating older clients).
3. **`links:`/`edge-label:` pair not in the allowed-pair matrix** → drop the tag (see [Declared edges](#declared-edges-and-the-allowed-pair-matrix)).
4. **Component with an unknown root type** (not in the slug table) → drop the entire component.
5. **`edge-label:` without a matching `links:`** → drop (no phantom edges).
6. **Edge whose target is not a member of the story** → drop the edge silently (this applies to derived edges also).
7. **Multiple `label:` tags on the same node** → the lexically-first slug wins (this mirrors the `lc:asset:*` tie-break).

Membership nuance: rules 1 and 2 reject the tag when the assembler parses it, so a rejected tag gives nothing — not even membership. Rule 3 removes only the edge semantics. The tag parsed correctly, so the bearer stays a member of the story.

### Label humanization

In `LABEL_SLUG` values, `-` and `_` become spaces (`web-server-fleet` → "web server fleet"). The two kinds of label are humanized at different layers:

- **Node labels** — the assembler humanizes these. For a `label:web-server-fleet` tag, the API payload carries `"label": "web server fleet"`.
- **Edge labels** — these stay in slug form in the API payload (`"label": "writes-to"`), so they are also stable identifiers. The rendering surface humanizes them (`StoryGraph` renders "writes to").

The slug stays safe to use inside a tag, which has a restricted charset, and the rendered graph still shows readable labels.

## Edge ontology

Edges are facts about how components connect. Membership is your choice of what belongs in the picture. The assembler keeps these two responsibilities separate:

- **Derived edges** — the assembler computes these from the configuration of the member records. It uses ARLs, extension requests, and name references that the resource definitions already contain. These edges need no tags and never become stale. Edit a rule to call a different playbook, and the story updates at the next fetch.
- **Declared edges** — these come from `links:` tags. They cover relationships that exist in operation but that no configuration states, such as telemetry that feeds a detection, or an agent that writes to its memory.

Every edge in the assembled story carries an `origin` field: `"derived"` or `"declared"`.

### Derived edges

For each member, the assembler examines the record content. It emits an edge when it finds one of the reference patterns below **and the target is also a member of the story**. A reference to a non-member never adds the target to the story. You keep control of membership.

| Source | Target | Label | Derived from |
|---|---|---|---|
| `dr-rule` | `lookup` | `consults` | `op: lookup` with `hive://lookup/NAME` or `lcr://lookup/NAME` in the detect logic |
| `dr-rule` | `yara-rule` | `scans-with` | `hive://yara/NAME` in a respond task (e.g. `yara_scan`) |
| `dr-rule` | `ai-agent` | `starts` | `action: start ai agent` with `definition: hive://ai_agent/NAME`, or `extension request` to `ext-feedback` with `feedback_destination: ai_agent` carrying an `ai_agent_name:` |
| `dr-rule` | `playbook` | `runs` | `extension request` to `ext-playbook` (`name:` in the request) or `ext-feedback` (`playbook_name:`), or any `hive://playbook/NAME` reference |
| `dr-rule` | `extension` | `invokes` | `action: extension request` with `extension name: NAME` (reserved — `extension` nodes don't surface, see [Reservation](#reservation)) |
| `dr-rule` | `secret` | `authenticates-with` | `hive://secret/NAME` (e.g. inline `start ai agent` credentials) |
| `dr-rule` | `output` | `forwards-to` | `action: output` with `name: NAME` (lands when `output` nodes surface) |
| `fp-rule` | `dr-rule` | `suppresses` | fp logic (at the record root) that compares `path: cat` with `op: is` — exact matches only — against a name that the rule `report`s |
| `cloud-sensor` | `secret` | `authenticates-with` | `hive://secret/NAME` in the sensor configuration |
| `adapter` | `secret` | `authenticates-with` | `hive://secret/NAME` in the adapter configuration |
| `ai-agent` | `secret` | `authenticates-with` | `anthropic_secret`, `lc_api_key_secret`, etc. |
| `playbook` | `lookup` / `yara-rule` | `uses` | `hive://...` ARLs found in the playbook code (best-effort) |
| `playbook` | `secret` | `authenticates-with` | `hive://secret/NAME` in the playbook code (best-effort) |
| `playbook` | `playbook` | `runs` | `hive://playbook/NAME` in the playbook code (best-effort) |
| `playbook` | `ai-agent` | `starts` | `hive://ai_agent/NAME` in the playbook code (best-effort) |

The mechanism is uniform. Any `hive://HIVE/NAME` or `lcr://lookup/NAME` string in the record content of a member produces a candidate edge, if `HIVE` maps to a canonical type slug. Three structural extractors also apply to `dr-rule` members and do not use ARLs: extension requests by name, `action: output` by name, and fp `cat` matching.

**Do not declare `links:` tags for these relationships.** The cloud draws them for you. A declared duplicate changes only the `origin` of the edge to `"declared"` (see [Precedence](#precedence-and-de-duplication)).

### Declared edges and the allowed-pair matrix

`links:` tags are only for relationships that no configuration states. Each `(bearer type → TARGET_TYPE)` pair must appear in the matrix below. The assembler silently drops a `links:` or `edge-label:` tag whose pair is not in the matrix (drop rule 3). The matrix is a superset of the derived pairs, so a manual declaration of a derivable edge stays valid. This is useful when the configuration reference does not exist yet.

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

Direction convention: data-flow edges point in the direction that the data moves (telemetry → detection → response → output). Dependency edges point from the consumer to the dependency (`dr-rule → lookup`, `adapter → secret`).

**Migration note:** before the matrix, any pair of known slugs was a valid `links:` target. Existing tags whose pair is not in the matrix still give membership, but their edges no longer render. Re-point or remove these tags. If a correct pair is missing from the matrix, it can be added. The matrix can grow, and pairs are never removed.

### Canonical edge labels

Derived edges always carry the canonical label for their pair. For a declared edge without an `edge-label:` tag, the assembler adds the default label of the pair, so an unlabeled `links:` tag still renders consistently. An explicit `edge-label:` replaces the default. The assembler accepts any slug that obeys the charset, but use this vocabulary unless you have a strong reason:

`telemetry`, `triggers`, `starts`, `runs`, `invokes`, `consults`, `scans-with`, `suppresses`, `forwards-to`, `writes-to`, `reports`, `authenticates-with`, `enrolls-with`, `manages`, `uses`, `remembers`, `follows`, `deploys`, `documented-by`, `files`, `escalates-to`, `member-of`, `owns`

### Precedence and de-duplication

If the same `(from, to)` edge is both derived and declared, the assembler emits one edge. The `origin` is `"declared"`. The label is the declared `edge-label:`, or the canonical default for the pair if no `edge-label:` exists.

## Where stories surface

- **AI Sessions terminal** — when the user asks to see a named story, the AI emits the StoryCard with `lc-card story --oid OID --name STORY_NAME`. The card fetches the assembled story from the API and renders the graph inline.
- **LimaCharlie web app** — every page that renders a story uses the same shared `StoryGraph` component. Future surfaces, such as an org-level "Story Library" or a landing page for each extension, will use the same shape.
- **API** — `GET /v1/orgs/{oid}/stories` returns the catalog of story names in the org. `GET /v1/orgs/{oid}/stories/{name}` returns the assembled `{ name, nodes, edges }` graph. Each edge carries an `origin` field (`"derived"` or `"declared"`). The server enforces read permissions for each Hive, and the response contains only what the caller can read.

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

Neither `links:` tag carries an `edge-label:`, so the assembler adds the canonical default for each pair (`dr-rule → playbook` is `runs`, `playbook → ai-agent` is `starts`). If the respond block of `exfil-detect` invoked the playbook with `ext-playbook`, the first `links:` tag would be unnecessary. The edge would appear automatically with `"origin": "derived"`.

## Applying tags

Use the [`limacharlie` CLI](../6-developer-guide/cli.md) or the equivalent API calls that [Sensor Tags](../2-sensors-deployment/sensor-tags.md) documents. You can add tags to a Hive record with the tag editor in the web app, with the CLI, or with D&R rule responses.

The workflow is: **tag membership on everything, and declare only the edges that no configuration states.** If the configuration of a member already refers to another member, the assembler derives the edge automatically. Examples are `hive://lookup/...` in a rule, `hive://secret/...` in an adapter, and an `extension request`. A `links:` tag for such an edge is redundant.

### Tag a single Hive record

```bash
# Mark a D&R rule as part of the "prod-pipeline" story:
limacharlie hive set --hive-name dr-general \
    --key exfil-detect \
    --tag-add lc:story:prod-pipeline \
    --tag-add lc:story:prod-pipeline:label:exfiltration-detector
```

### Compose a multi-component story

A story usually spans several components. Membership tags go on every component. Only the telemetry edge needs a `links:` tag here, because no configuration states that the data of this sensor feeds this rule:

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

Remove the tag from the component. The next request for the story returns one node fewer, and each edge that points to the component disappears (the assembler drops dangling edges).

## Reservation

The `sensor` type slug is reserved for endpoint sensors, but the v1 assembler does not surface it. Selectors for endpoint sensors support only exact tag matching, which misses link-only sensors and breaks the implicit-membership rule. `links:sensor:SID` tags parse, but no row of the allowed-pair matrix *targets* `sensor`, so the assembler drops the tag at the matrix gate (drop rule 3). A matrix row will be added when the sensor side is connected. For sensor-shaped components today, use `cloud-sensor`, which the assembler does surface.

Data-flow singletons (`output`, `payload`), Records (`case`, `artifact`, `detection`, `vulnerability`), IAM (`user`, `role`), and config singletons (`installation-key`, `api-key`) are also reserved. A Hive does not back them today, so they cannot carry tags or appear as nodes, and the assembler drops edges that point to them at the dangling-edge step. They surface when they are added to the assembler.

`extension` is also reserved, for a different reason. **Never tag extension subscription records.** Their backing hive (`extension_subscription`) is internal. Extension nodes do not surface, and edges that target `extension` drop at the dangling-edge step. Model a flow through an extension with the visible components of the extension. For example, the webhook cloud sensor of ext-feedback declares `links:ai-agent:...` (`triggers`), and the rule→agent leg derives from the `ai_agent_name` in the extension request.

## See also

- [Asset Tags (`lc:asset:*`)](../2-sensors-deployment/asset-tags.md) — the related tag namespace for asset metadata. It uses the same approach to drop rules.
- [Sensor Tags](../2-sensors-deployment/sensor-tags.md) — the underlying tagging mechanism and API surface.
- [`limacharlie` CLI](../6-developer-guide/cli.md) — `hive set` (`--tag-add`/`--tag-rm`) reference.
