# ASD-STE100 Rewrite Guide — LimaCharlie Documentation

You are rewriting existing MkDocs Markdown pages into **Simplified Technical English
(ASD-STE100)**, adapted for software documentation. The meaning must not change. Only the
language changes.

Read this whole file before you edit anything.

---

## 0. Hard constraints — violating any of these is a failure

**NEVER change any of the following. Copy them through byte-for-byte:**

1. **Anything inside a fenced code block** (```` ``` ````, ```` ~~~ ````) — including comments
   inside the code. Commands, YAML, JSON, Python, Go, shell output: untouched.
2. **Inline code spans** (`` `like_this` ``) — field names, event names, flags, paths, API
   endpoints, selectors.
3. **Every heading line** (`#`, `##`, `###`, …). Heading text is frozen. Other pages link to
   the generated anchors and `mkdocs.yml` mirrors these as nav labels. Do not reword, do not
   change capitalization, do not add or remove headings.
4. **Link targets** — the `(...)` part of `[text](target)`, all relative paths, all `#anchors`,
   all image paths. You may rewrite *link text* only if it stays descriptive and unique
   (rule MD059 is enforced: never produce "here", "this", "link", "read more").
5. **Snippet includes** (`--8<-- "snippets/..."`), abbreviation definitions (`*[TERM]: ...`),
   HTML blocks (`<div class="grid cards" markdown>`, `<details>`, `<img>`), MkDocs attribute
   lists (`{ .lg .middle }`), and icon shortcodes (`:material-rocket-launch:`).
6. **Admonition and tab syntax** — the `!!! note "Title"` / `=== "Python"` marker lines and
   their exact indentation. You may rewrite the prose *inside* an admonition body.
7. **Table structure** — keep the same number of columns and rows, keep the delimiter row.
   You may rewrite cell prose.
8. **Technical facts.** Do not add, remove, soften, or invent a fact, a permission, a version,
   a limit, a default, or a platform. If a sentence is wrong, leave it wrong and report it.
   You are a language editor, not a fact checker.

**Also do not:**

- Reorder sections, merge pages, or delete sections.
- Add a "Note:" or admonition that was not there.
- Change the file's trailing structure (`---` + `## See Also` blocks stay).
- Touch files other than the ones assigned to you.

---

## 1. The four STE principles you are applying

1. **One word, one meaning.** Each word is used in a single approved sense.
2. **One concept, one word.** Never vary a term for style. If it is a "sensor", it is always a
   "sensor" — not an "agent", "endpoint", or "client".
3. **Short, simple, active sentences.**
4. **Explicit structure.** Instructions are numbered steps in the imperative.

---

## 2. Word rules

### 2.1 Approved-word substitutions (apply these mechanically)

| Replace | With |
|---|---|
| utilize, leverage, employ (=use) | use |
| in order to, so as to | to |
| prior to, in advance of | before |
| subsequent to, following (=after) | after |
| in the event that, in the case that | if |
| provided that | if |
| due to the fact that, owing to the fact that | because |
| a number of, a variety of, numerous | many, or a count |
| the majority of | most |
| commence, initiate, kick off | start |
| terminate, cease, halt | stop |
| perform, execute (a step), carry out | do |
| provide, furnish | give, supply, or a specific verb |
| ensure, guarantee | make sure |
| require (=need) | need |
| assist, aid | help |
| obtain, acquire | get |
| additional, supplementary | more |
| approximately, roughly | about |
| attempt | try |
| sufficient, adequate | enough |
| facilitate | help, or a specific verb |
| implement (=build/set up) | build, set up, or add |
| modify, alter | change |
| indicate | show |
| determine | find, or decide |
| retain | keep |
| permit (=let) | let, or allow |
| prevent (=stop) | stop |
| verify (=check) | check |
| observe (=see) | see |
| approximately equal | about the same |
| via | with, through, or by |
| per (=for each) | for each |
| regarding, with respect to, in terms of | about, or for |
| in conjunction with | with |
| a wide range of, a rich set of | many |
| seamlessly, effortlessly, easily, simply, just | *delete the word* |
| powerful, robust, comprehensive, cutting-edge | *delete the word* |
| please | *delete the word* |

`comply with`, `conform to` → **obey**. `follow the instructions` → **obey the
instructions** (in STE, *follow* means *come after*).

### 2.2 Delete filler outright

Remove: *note that*, *it is important to note that*, *keep in mind that*, *of course*,
*basically*, *essentially*, *actually*, *simply*, *just*, *very*, *quite*, *really*,
*in general*, *typically* (when it hides no real qualification), *as you can see*,
*don't worry*.

If a sentence exists only to say a thing is easy or good, delete the sentence.

### 2.3 No idioms, slang, or metaphors

Ban: *out of the box*, *under the hood*, *up and running*, *dig in*, *at a glance*,
*on the fly*, *hand in hand*, *first-class*, *battle-tested*, *heavy lifting*,
*a breeze*, *drop-in*, *spin up*, *fire off*, *kick in*, *plug into* (unless physical),
*best-of-breed*, *state of the art*, *for the modern era*.

Replace with the literal fact. *"Spin up a sensor"* → *"Start a sensor"*.

### 2.4 One meaning per word — watch these

- **since** — use only for time. For cause, write *because*.
- **while** — use only for time. For contrast, write *but* or *although*.
- **as** — use only for comparison. For cause, write *because*.
- **once** — use only for "one time". For sequence, write *after* or *when*.
- **should** — use only for a recommendation. For a requirement, write *must*.
- **may** — use only for permission. For possibility, write *can* or *is possible*.
- **that** vs **which** — use *that* for restrictive clauses. Never drop *that*:
  *"the rule you create"* → *"the rule that you create"*.

### 2.5 Noun clusters: three words maximum

Break longer clusters with prepositions.

- *"sensor installation key management page"* → *"the page that manages installation keys
  for sensors"*
- *"detection rule false positive suppression"* → *"suppression of false positives in
  detection rules"*
- *"cloud security posture management report"* → keep if it is a product name; otherwise
  split.

Product names, event names, and UI labels are **technical names** and are exempt.

### 2.6 Articles are mandatory

*"Click Save button"* → *"Click the Save button."*
*"Sensor sends event to cloud"* → *"The sensor sends the event to the cloud."*

---

## 3. Sentence rules

- **Instruction (procedural) sentence: 20 words maximum.**
- **Descriptive sentence: 25 words maximum.**
- **One instruction per sentence.** Split compound commands into separate steps.
- **Use the imperative** for anything the reader does: *"Open the Sensors page."* — not
  *"You should open…"*, *"You can now open…"*, *"The user opens…"*.
- **Active voice.** Name the actor.
  - *"The event is sent to the cloud by the sensor."* → *"The sensor sends the event to the
    cloud."*
  - Passive is allowed **only** when the actor is genuinely unknown or irrelevant, and mostly
    in descriptive text: *"The rule is stored in the `dr-general` hive."* is acceptable.
- **Simple tenses only** — simple present, simple past, simple future. Avoid the perfect and
  the progressive.
  - *"has been deprecated"* → *"is deprecated"*
  - *"will be running"* → *"runs"*
  - *"is going to send"* → *"sends"*
- **No -ing verb forms as verbs.** A gerund subject must become a clause or a noun.
  - *"Running the installer creates a service."* → *"The installer creates a service."*
  - *"When configuring the adapter, set the key."* → *"When you configure the adapter, set
    the key."*
  - Exceptions: established technical names (*logging*, *monitoring*, *tracking*,
    *Sleeper Mode*), and `-ing` words that are nouns in the product (*a listing*).
- **Write positively.** *"Do not use a key that is not scoped"* → *"Use a scoped key."*
- **No rhetorical questions** in body prose. (Headings are frozen, so a heading that is a
  question stays.)
- **Do not address the reader in the first person plural.** *"Our documentation can walk you
  through…"* → *"This documentation explains how to…"*. Avoid *we*, *our*, *let's*.

---

## 4. Procedure rules

- A sequence of actions becomes a **numbered list**, one action per item, each starting with
  an imperative verb. Do this even if the source used prose — but do **not** invent steps that
  the source does not state.
- Put the condition first: *"If the sensor is offline, the command is queued."*
- State the result of a step after the step, in its own sentence.
- **Warnings and cautions start with the command**, then the reason:
  *"Do not delete the installation key. The sensors that use it stop enrolling."*
  Never bury the instruction after the explanation.

---

## 5. Paragraph rules

- **Six sentences maximum** per paragraph. Aim for three.
- **One topic per paragraph.** The first sentence states the topic.
- Prefer a bulleted list over a long sentence with a series of items.
- Keep the existing paragraph and list boundaries where they already work. Do not fuse a
  list into prose.

---

## 6. LimaCharlie terminology — use exactly one term per concept

Match the term already dominant in the file's section, and never vary it inside a page.
Canonical choices when the source is inconsistent:

| Concept | Use | Do not use |
|---|---|---|
| the software on an endpoint | sensor | agent, client, endpoint agent (except where the page's frozen heading says "Endpoint Agent") |
| a tenant | organization | tenant, account, workspace |
| a detection and response rule | D&R rule | rule engine entry, detection |
| a piece of telemetry | event | log line, record, message |
| the LimaCharlie service | the cloud | the backend, the platform, the service |
| a log-collecting sensor | adapter | connector, shipper, collector |
| a destination for telemetry | output | sink, forwarder |
| the web interface | the web app | the UI, the console, the dashboard |
| a query in LCQL | query | search |

Keep the existing capitalization of product nouns as you find it. Do not start capitalizing
or de-capitalizing "Sensor"/"sensor" across a page — that is not an STE issue.

Keep every acronym that the glossary defines (`OID`, `SID`, `LCQL`, `D&R`, `MSSP`, `EDR`,
`IaC`). Expand an acronym on first use in a page only if the source already did so.

---

## 7. Worked examples

**Marketing prose**

> Before: LimaCharlie's Agentic SecOps Workspace provides you with comprehensive enterprise
> protection that brings together critical cybersecurity capabilities and eliminates
> integration challenges and security gaps for more effective protection against today's
> threats.

> After: The Agentic SecOps Workspace combines security capabilities in one platform. The
> single platform removes the work to integrate separate tools. It also removes the gaps in
> coverage between those tools.

**Procedure buried in prose**

> Before: To get started, you'll want to first create an installation key from the web app,
> and then, once you've done that, you can download the installer and run it with the key you
> just created as an argument.

> After:
> 1. In the web app, create an installation key.
> 2. Download the installer.
> 3. Run the installer. Give the installation key as an argument.

**Passive + perfect tense**

> Before: Events that have been collected by the sensor are subsequently forwarded to any
> outputs that have been configured.

> After: The sensor collects events. It then sends the events to each output that you
> configured.

**Gerund subject and long noun cluster**

> Before: Configuring organization level detection rule exclusion lists prevents alert fatigue.

> After: Exclusion lists for detection rules stop unwanted alerts. You configure these lists
> for each organization.

**Warning order**

> Before: Because deleting an organization is irreversible and all telemetry will be lost,
> you should be very careful before you proceed.

> After: Be careful before you delete an organization. You cannot undo the deletion, and all
> telemetry is lost.

---

## 8. Quality bar and judgement

- **Meaning first.** If STE compliance would make a sentence ambiguous or wrong, keep the
  clearer sentence and stay as close to STE as you can.
- **Do not pad.** STE output is usually 10–25% shorter than the source. If your rewrite is
  longer, you added words that were not needed.
- **Do not mangle domain terms** to fit the STE dictionary. Technical names and technical
  verbs from the security and software domain are permitted: *enroll, ingest, parse, deploy,
  authenticate, query, encrypt, subscribe, enable, disable, install, uninstall, isolate,
  tag, filter, hash, sign, throttle, quarantine, telemetry, artifact, payload, webhook,
  schema, namespace, hive, tenant*.
- Pages that are pure reference tables of field names may need almost no change. That is a
  valid outcome. **Do not invent changes to look busy.**
- Some pages are nothing but a title and a list of links. Leave them nearly untouched.

---

## 9. Before you finish each file

Check every item:

- [ ] Every heading is byte-identical to the source.
- [ ] Every fenced code block is byte-identical to the source.
- [ ] Every link target and image path is unchanged.
- [ ] No link text is "here", "this", "link", "click here", or "read more".
- [ ] No sentence is longer than 25 words; no instruction is longer than 20.
- [ ] No paragraph is longer than six sentences.
- [ ] No banned filler word or idiom survives (section 2.2, 2.3).
- [ ] Every list item in a procedure starts with an imperative verb.
- [ ] Tables have the same shape as the source.
- [ ] The file still ends with a single newline.
- [ ] No fact was added or removed.
