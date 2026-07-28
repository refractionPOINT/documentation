# Standard Operating Procedures (SOPs)

A Standard Operating Procedure is a document that you store in your organization. It
tells AI agents how *your* team wants a job done. [AI Skills](skills.md) are
reusable capabilities that an agent invokes, and [AI Memory](memory.md) is what an
agent learned. An SOP is organizational policy: the escalation path for a ransomware
detection, who must approve the isolation of an endpoint, and which hosts must stay
untouched during business hours.

SOPs are plain documents. LimaCharlie does not execute them. People write them,
agents read them, and agents obey them as instructions. An SOP is therefore the main
way to steer agent behaviour without a change to the agent prompts.

SOPs are in the `sop` [Config Hive](../7-administration/config-hive/index.md), and
each SOP is scoped to a single organization.

## Record format

Each SOP is one Hive record. The key is the SOP name, and the payload has two
fields:

| Field | Required | Purpose |
|---|---|---|
| `text` | Yes | The procedure. Free-form text; markdown is the convention. |
| `description` | No | A one-line summary that decides if the SOP applies. |

```yaml
data:
  description: Standard procedure for confirmed ransomware on an endpoint
  text: |
    # Ransomware Response

    ## Containment
    1. Isolate the affected sensor immediately — do not wait for approval.
    2. Tag the sensor `incident` and note the detection ID.

    ## Escalation
    - Page the on-call responder for any host tagged `prod`.
    - Do not power off servers; collect memory first.

    ## Out of scope
    - Never delete artifacts or detections as part of containment.
usr_mtd:
  enabled: true
  tags: [incident-response, tier-1]
```

The only validation is that `text` must not be empty. No other rule applies to the
content. Write for the reader: an LLM that must decide what to do next.

### Writing an effective `description`

The `description` is load-bearing. An agent scans the list of SOPs, matches each
description against its current task, then fetches only the SOPs that match. With a
vague description ("IR stuff"), the agent never opens the SOP. With a specific
description ("Standard procedure for confirmed ransomware on an endpoint"), the agent
opens it.

### Limits

- Maximum record size: 1 MB per SOP.

!!! warning "New SOPs are created disabled"
    Enable each new SOP with `--enabled` or with `usr_mtd.enabled: true`. Like every
    Hive record, an SOP is created **disabled**. Set the value deliberately — an SOP
    has an effect only when the agents that read it treat it as active policy.

## How agents use SOPs

No component injects SOPs into an agent automatically. An agent loads them itself,
in two steps:

1. **List** the SOPs in the organization and read the names and descriptions.
2. **Fetch by key** only the SOPs with a description that matches the current task.
   Then obey the procedure.

Agents from the LimaCharlie agent library announce the match in their
transcript — `Following SOP: <name>` — so you can audit adherence later.

The granularity of your SOPs is therefore important. One large `security-policy`
document forces the agent to load everything for every task. A set of narrow SOPs
(`ransomware-response`, `after-hours-escalation`, `isolation-approval`) lets the
agent load only what applies.

!!! note "Listing returns full records"
    `limacharlie sop list` and `GET /v1/hive/sop/{oid}` return every SOP in full,
    and this includes `text`. Agents are instructed to read only the names and
    descriptions at that step, then to fetch the body again with `sop get`. If you
    keep many large SOPs, plan the context budget for this.

## Permissions

| Operation | Permission |
|---|---|
| List / read SOPs | `sop.get` |
| Create / update an SOP | `sop.set` |
| Delete an SOP | `sop.del` |
| Read metadata | `sop.get.mtd` |
| Update metadata | `sop.set.mtd` |

Give the read-only pair `sop.get` and `sop.get.mtd` to an agent that only obeys
procedures. Grant `sop.set` only to agents that write policy.

## Managing SOPs

### Web interface

Manage SOPs under **Automation → SOPs** in the organization view. There you can
create, edit, tag, enable, and disable them. In an interactive AI session, the
`/sops` [slash command](rich-cards.md) shows the same list in the chat.

### CLI

```bash
# List every SOP in the organization.
limacharlie sop list --oid <oid> --output yaml

# Read one SOP.
limacharlie sop get --key ransomware-response --oid <oid> --output yaml

# Create or update an SOP from a file, enabled in one shot.
limacharlie sop set --key ransomware-response \
    --input-file ransomware-response.yaml --enabled --oid <oid>

# Or pipe the record in.
cat ransomware-response.yaml | limacharlie sop set \
    --key ransomware-response --enabled --oid <oid>

# Toggle without touching the content.
limacharlie sop disable --key ransomware-response --oid <oid>
limacharlie sop enable --key ransomware-response --oid <oid>

# Organize with tags.
limacharlie sop tag add --key ransomware-response -t incident-response --oid <oid>

# Delete.
limacharlie sop delete --key ransomware-response --confirm --oid <oid>
```

The input file has the same shape as the record above: a `data` block with
`text` and `description`, and an optional `usr_mtd` block.

### REST API

SOPs use the standard Hive endpoints with a hive name of `sop` and the organization
ID as the partition key:

```bash
# List all SOPs.
curl -s "https://api.limacharlie.io/v1/hive/sop/$OID" \
  -H "Authorization: Bearer $LC_JWT"

# Read one SOP.
curl -s "https://api.limacharlie.io/v1/hive/sop/$OID/ransomware-response/data" \
  -H "Authorization: Bearer $LC_JWT"

# Create or update.
curl -s -X POST \
  "https://api.limacharlie.io/v1/hive/sop/$OID/ransomware-response/data" \
  -H "Authorization: Bearer $LC_JWT" \
  --data-urlencode 'data={"text":"# Ransomware Response\n1. Isolate the sensor.","description":"Confirmed ransomware on an endpoint"}' \
  --data-urlencode 'usr_mtd={"enabled":true}'
```

### Python SDK

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.hive import Hive, HiveRecord

client = Client(oid="YOUR_OID", api_key="YOUR_API_KEY")
org = Organization(client)
sops = Hive(org, "sop")

# Create or update an SOP.
record = HiveRecord(
    "ransomware-response",
    data={
        "text": "# Ransomware Response\n1. Isolate the sensor.",
        "description": "Confirmed ransomware on an endpoint",
    },
)
record.enabled = True
record.tags = ["incident-response"]
sops.set(record)

# Read one SOP.
sop = sops.get("ransomware-response")
print(sop.data["text"])

# List every SOP.
for name, rec in sops.list().items():
    print(name, rec.data.get("description"))
```

## Related

- [AI Skills](skills.md) — reusable instruction sets that an agent invokes as capabilities.
- [AI Memory](memory.md) — what an agent learned and must recall later.
- [Config Hive](../7-administration/config-hive/index.md) — the store that holds SOPs.
- [Permissions](../8-reference/permissions.md) — the full permission reference.
