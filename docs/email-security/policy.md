# Policy Reference

--8<-- "includes/email-security-beta.md"

Email Security is configured through Hive records. Anything the console can
configure, `limacharlie hive set` can configure — so tenant onboarding and
fleet-wide policy are a script, not a UI workflow.

| Hive | Records | Purpose |
|---|---|---|
| `mailsec_provider` | one per mail connection | which tenant to protect, with which credential — see [Connecting Providers](providers.md) |
| `mailsec_policy` | many, discriminated by `policy_type` | automations, exclusions, VIPs, thresholds, banners, retention, reporter replies, hunt defaults, clustering |
| `dr-mail` | one per custom rule | your own mail detection rules — see [Custom Rules](custom-rules.md) |

## How `mailsec_policy` records work

Every record carries a `policy_type` discriminator. There may be **many records
of each type**, and they compose into one resolved policy.

### Composition is by record name

Records compose in **record-name order**. The name is not decoration: it is the
only thing that makes composition deterministic when two records set the same
field. An organization that needs a specific precedence names its records
accordingly — `00-baseline`, `50-team-x`, `99-override` — the same convention as
every other ordered configuration surface.

How each type composes:

| Type | Composition |
|---|---|
| `automations` | Concatenated in name order; evaluated as an ordered list |
| `exclusions` | Concatenated — a set of independent suppressions |
| `vips` | Union, deduplicated and sorted |
| `thresholds` | Last writer wins per field, with the ordering invariant re-checked afterwards |
| `banners`, `reporter_reply`, `hunt_defaults`, `clustering` | Last writer wins per field |
| `retention` | **Maximum** wins — see [Retention](#retention) |

### Unknown fields are refused

Every record body is decoded strictly. A key the contract does not define is a
**rejected record**, not an ignored field. A policy is a security control, and a
typo'd key that silently does nothing is the worst available failure mode: the
operator believes mail is being quarantined and it is not. A rejected record is
visible; an ignored field is not.

The validator's own wording is what you get back — in the CLI, in the API, and
verbatim in the console's Policy page.

### Editing preserves what you did not touch

The console's **Policy** page edits every record type, and saves are
**patch-preserving**: fields the form does not manage are written back exactly as
they were. Editing a policy record in the UI never silently drops a field you set
through the API or through git-sync.

### Defaults

An organization that has written no policy still has one. Every type below states
its default, and the defaults are deliberately inert: nothing moves mail, nothing
modifies mail, and nothing sends mail until you say so.

---

## `automations`

The ordered list of `{match → actions}` rules that decide what happens to a
message automatically.

```yaml
policy_type: automations
automations:
  - name: malicious-quarantine
    match:
      verdicts: [malicious]
    actions: [quarantine_message]
    mode: alert_only
  - name: reported-mail-quarantine
    match:
      user_reported: true
      min_score: 45
    actions: [quarantine_message]
    mode: alert_only
```

### `match`

| Field | Meaning |
|---|---|
| `verdicts` | Any of `malicious`, `suspicious`, `graymail`, `benign`, `unknown`, `error`. An unrecognized verdict is refused rather than silently never matching |
| `tags` | Verdict tags contributed by the rules that fired |
| `directions` | `inbound`, `outbound`, `internal` |
| `min_score` | 0–100 |
| `user_reported` | Tri-state: omit to ignore, `true` for mail a human flagged, `false` for mail nobody reported |

An **empty match matches everything**. An enforcing rule with an empty match is
refused at save — "quarantine all mail" is never what someone meant to write.

### `actions`

| Action | |
|---|---|
| `quarantine_message` | Out of the inbox, restorable |
| `trash_message` | To recoverable trash |
| `move_to_spam` | To the junk/spam location |
| `banner_message` | Prepend the warning banner |

Deliberately **not** automatable: the campaign-wide sweeps (an automation acting
on one message must not fan out to hundreds without a human — that is an explicit
action), `restore_message` (undoing is a human decision), and the disposition
labels (labels are evidence, and a machine writing them would poison the data set
that measures the machine).

!!! warning "Two further action names validate but do not execute"
    Policy validation accepts `submit_to_triage` and `crawl_link` as automatable,
    but the remediation executor implements neither, so an automation that
    dispatches one records a failed action rather than doing anything. Use only
    the four actions in the table above.

### `mode`

| Mode | |
|---|---|
| `alert_only` | **The default.** The rule is evaluated and its intent recorded; the mailbox is not touched. Actions report `alert_only` as their result |
| `enforce` | The action is performed at the provider |

The default is load-bearing. A rule whose mode is missing, misspelled, or written
by an older tool falls back to the harmless behaviour — falling back to `enforce`
would mean a typo silently deletes mail. An unrecognized mode is refused at
save, and anything that ever slipped past decoding still behaves as
`alert_only`.

!!! danger "Enforcement is currently organization-wide at the executor"
    The remediation executor authorizes *automated* action when **any** resolved
    automation rule is in `enforce` mode. Which rule dispatches which action is
    still decided per rule, but the executor's consent check is not per rule — so
    putting one rule into `enforce` enables the organization's automated paths
    generally. Treat the first `enforce` as the decision that this organization
    now moves mail automatically.

    Analyst-initiated actions are unaffected: a human clicking quarantine always
    executes.

**Default:** subscribing seeds a recommended preset entirely in `alert_only` —
malicious → quarantine and graymail → move to spam among them. Nobody is
surprise-quarantined on day one. Review the seeded records before switching any
of them to `enforce`.

---

## `exclusions`

Suppress signals **before** scoring, so an excluded rule contributes nothing to
the score and never appears in the verdict's reasons. It still appears in
`matched_signals`, so a suppression is auditable rather than invisible.

```yaml
policy_type: exclusions
exclusions:
  - rule_id: ms-sender-first-contact
    sender_domain: newsletters.partner.example
    reason: "Marketing partner onboarded 2026-08; every send is a first contact"
    expires_at: "2026-12-31T00:00:00Z"
```

| Field | |
|---|---|
| `rule_id`, `sender_email`, `sender_domain`, `mailbox` | The scope. **At least one is required** |
| `reason` | **Required.** An exclusion is a permanent hole in detection, and one whose rationale nobody recorded is one nobody can ever safely remove |
| `created_by` | Optional attribution |
| `expires_at` | Optional. After it, the exclusion is inert without anyone deleting it — which is what makes a time-boxed exclusion safe to grant |

Addresses and domains are lowercased on save.

**Default:** none.

---

## `vips`

The protected identities that impersonation detection compares against — the
display names and addresses a `Finance` request is most damaging in the name of.

```yaml
policy_type: vips
vips:
  - name: Ada Lovelace
    email: ada@corp.example
    title: CFO
list_refs:
  - hive://lookup/execs
```

| Field | |
|---|---|
| `vips[]` | Inline entries. Each needs a `name` **or** an `email`; `title` is context for an analyst, not a matching key |
| `list_refs[]` | References to `lookup` Hive records, so the executive list lives in one place — the same lookup your D&R rules and your HR export already feed — instead of being copied into policy where it drifts |

A `list_ref` must be of the form `hive://lookup/<name>`.

### The two accepted lookup shapes

A LimaCharlie lookup record is a map of key → metadata. Both forms are read, and
both are normalized into the same VIP:

```yaml
# (a) the key is the email address, metadata is optional context
"ada@corp.example":
  name: Ada Lovelace
  title: CFO
```

```yaml
# (b) the key is the display name, the address (if known) is in the metadata
"Ada Lovelace":
  email: ada@corp.example
  title: CFO
```

In shape (a) the **key wins** over any `email` in the metadata: in a lookup the
key is the indicator, and that is what every other consumer of the record matches
on. A disagreeing metadata field must not make mail security protect a different
address than the rules do.

An entry with neither a plausible email key nor an email in its metadata — the
bare `"Ada Lovelace": {}` a newline upload produces — becomes a **name-only VIP**.
That is legal and useful: display-name impersonation is the high-yield shape and
needs no address to be detected.

Metadata keys are matched case-insensitively; `name` (alias `display_name`),
`email` and `title` are read and everything else is ignored, so a list maintained
for another purpose can be pointed at without being reshaped.

Both the plain and the pre-indexed (optimized) storage forms of a lookup record
are read, because which one the Hive holds depends only on how the record was
uploaded.

### What is surfaced

- A reference whose record is **absent, disabled, not shaped like a lookup, or
  empty of usable entries** resolves to zero entries and is **reported to the
  organization** — a configured VIP list that contributes nobody is a coverage
  lie, and it is reported repeatedly until fixed rather than once per process.
- A reference that could not be **read** keeps serving its last good entries and
  is reported as stale rather than lost, so one datastore blip does not disarm
  your VIP list.
- Malformed entries and truncation are counted and reported **as counts, never
  with the entry's contents** — a VIP list is a list of named people, and a
  malformed row is exactly as personal as a well-formed one.
- One reference contributes at most **1,000 entries**. The VIP list is scanned
  once per message, so pointing this at a large threat feed would put a huge scan
  in the ingest path of every message. Truncation is surfaced, never silent.

Resolution never fails the policy: inline entries and every other reference stay
in force.

**Default:** none.

---

## `thresholds`

The verdict cutoffs and per-rule overrides.

```yaml
policy_type: thresholds
malicious_min: 80
suspicious_min: 40
rule_overrides:
  ms-link-unranked-domain:
    weight: 15
  ms-graymail-precedence-bulk:
    disabled: true
```

| Field | Default | |
|---|---|---|
| `malicious_min` | 85 | 1–100 |
| `suspicious_min` | 45 | 1–100 |
| `rule_overrides` | — | Keyed by rule id: `disabled` to switch a packaged rule off for your organization, `weight` (0–100) to replace its packaged weight |

`malicious_min` must remain **above** `suspicious_min`. Two records that are each
individually sane can compose into an inversion — one lowers malicious, another
raises suspicious — so the invariant is enforced after composition, not only per
record. An inverted pair would make every suspicious message malicious.

Rule ids are stable and are never renamed, which is the only reason an override
can be persisted at all.

---

## `banners`

The warning banner's text and switch.

```yaml
policy_type: banners
enabled: true
text: "External sender. Verify before clicking links or opening attachments."
```

| Field | Default | |
|---|---|---|
| `enabled` | `false` | Bannering rewrites the customer's mail, and nothing in this product modifies mail by default |
| `text` | A packaged warning | **Plain text only** — no `<` or `>` — and capped at 512 characters |

The HTML template is fixed and sanitized in code; policy contributes only the
text. Accepting markup here would turn a configuration field into stored HTML
injection against your own users.

Bannering also needs the provider capability: `Mail.ReadWrite` is enough on
Microsoft 365 (edited in place), while Google Workspace additionally needs the
optional `https://mail.google.com/` scope and **replaces** the message.

---

## `retention`

How long flagged evidence is kept.

```yaml
policy_type: retention
flagged_days: 180
```

| Field | Default | Range |
|---|---|---|
| `flagged_days` | 400 | 30–400 |

400 is the schema's hard ceiling: policy can only choose *within* what the store
keeps, because a policy asking for longer would be a promise the database
silently breaks.

Composition takes the **maximum** rather than the last writer. Two records
disagreeing about retention is a disagreement about how much evidence to destroy,
and the safe resolution is always "keep it longer" — a shorter setting is
recoverable by editing policy, deleted rows are not.

The 35-day searchable message index and the raw-message window are separate and
are not configured here.

---

## `reporter_reply`

The templated acknowledgement sent to someone who reported a message. See
[User Reports](user-reports.md#reporter-replies).

```yaml
policy_type: reporter_reply
enabled: true
templates:
  malicious: "Thanks — you were right. We removed that message from every mailbox it reached."
  benign: "Thanks for checking. That message is legitimate; no action was needed."
```

| Field | Default | |
|---|---|---|
| `enabled` | `false` | It sends mail on your behalf to your own staff; opt-in |
| `templates` | — | Keyed by verdict. A verdict with no template falls back to a generic acknowledgement, so enabling replies can never leave a reporter with silence |

Template keys must be verdicts. Values are plain text (no `<` or `>`), capped at
4096 characters.

---

## `hunt_defaults`

Starting values for retro-hunt requests.

```yaml
policy_type: hunt_defaults
window_days: 7
max_results: 1000
dry_run: true
```

| Field | Default | Range |
|---|---|---|
| `window_days` | 7 | 1–365 |
| `max_results` | 1000 | 1–100000 |
| `dry_run` | `true` | An operation that can bulk-remediate defaults to "show me what this would match" |

---

## `clustering`

How aggressively messages are grouped into a campaign — which is what sets the
blast radius of a campaign-wide action. It is a separate record from
`thresholds` on purpose: `thresholds` is how harshly mail is *judged*, and
folding the reach of a bulk quarantine into a record named for scoring would hide
it.

```yaml
policy_type: clustering
body_similarity: true
body_similarity_distance: 30
```

| Field | Default | Range |
|---|---|---|
| `body_similarity` | `true` | Whether the body fuzzy hash may count as an agreeing cluster key |
| `body_similarity_distance` | 30 | 0–35. Lower is stricter; 0 means byte-identical normalized bodies only |

The default is **on**, because the organization that most needs body similarity —
one being hit by a kit that randomizes subjects and links — is the one least
likely to go looking for a switch to turn on.

The distance default is measured, not chosen: across a 404-message corpus of
ordinary business mail the closest pair of *unrelated* messages is 39 apart,
while two copies of one message differing only in the recipient's name and the
link's tracking parameters are 0 apart. The ceiling of 35 sits below that closest
pair deliberately — a setting above it is one you cannot have measured.

See [Body similarity](campaigns.md#body-similarity) for what the key is and how a
body is normalized before it is hashed.

!!! note "Turning it off does not stop the digest being computed"
    `body_similarity: false` stops the digest counting as *agreement*. It is
    still computed, still stored, still returned on the message and still
    searchable. So turning the switch back on gives you working clustering
    immediately, rather than only for mail that arrives afterwards — and the
    digest an analyst is looking at is never a value the product quietly stopped
    maintaining.

---

## Reading the resolved policy

The resolved automation mode — the effective safety banner — is reported by
coverage, and the console shows it on both **Overview** and **Settings**:

```bash
limacharlie mailsec coverage --oid $OID --output yaml --filter 'overview'
```

It reads `enforce` when any resolved rule can act, and fails closed to
`alert_only` when the policy is absent, unreadable, or carries a mode this build
does not recognize.
