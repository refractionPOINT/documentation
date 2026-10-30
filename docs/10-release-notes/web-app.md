# Web App Release Notes

Release notes for the LimaCharlie web application. For the latest releases of every component, see the [release notes overview](index.md).

!!! tip "Subscribe"
    Get each release as it ships with the [Web App RSS feed](https://docs.limacharlie.io/10-release-notes/web-app.xml).

## 2026-10-13

### Web App 6.6.2

A redesigned Email Security overview, case assignment without user management rights, and a new permission for listing org users.

#### New Features

- **Email Security overview redesign**: the overview now opens with four summary cards, recent threat groups, and a full breakdown of message verdicts. Each verdict shows its count and percentage and links to the matching messages. Detailed collection health moves into one Pipeline health section, and the status summary links straight to each issue. Each card is labelled "Current status" or "Selected period", so it is clear what the number measures.
- **Email Security period selector**: the overview uses the same Time Period selector as the Dashboard, with Past Day, Past Week, and Past Month. It now opens on Past Month. The selected period and the spam-folder filter carry through to threat groups and to message and group drilldowns.
- **`user.list` permission**: a new read-only permission that lets a user list the email addresses of an org's users. It is included in the Owner, Administrator, and Operator roles.
- **Case assignment without `user.ctrl`**: users who can edit cases (`investigation.set`) can now assign them without `user.ctrl`. Both assignee pickers list existing case assignees and yourself, and accept a typed email address. With `user.list` or `user.ctrl`, the pickers also list the org's users.

#### Bug Fixes

- Email Security dialogs opened from the Message, Campaign, or Group drawer, such as Quarantine or "Override this verdict", now show above the drawer instead of behind it.
- Email Security action timelines, verdict history, report "resolved by", and submissions now show the person's email instead of a user ID. Showing other users' emails requires `user.ctrl`.
- "Recent suspicious and malicious mail" on the Email Security overview shows the real subject line instead of a lower-cased, masked version.
- Changing the Email Security overview period no longer opens drilldowns with the previous date range while new data loads.

---

## 2026-10-11

### Web App 6.6.1

Product-aware onboarding, more accurate Cloud Security sensor coverage, and mail in the provider's spam folder in Email Security.

#### New Features

- **Product-aware onboarding**: when you create an organization, you now pick what to protect: Endpoint, Cloud Security, Email Security, or Code Security. "Just exploring" creates a demo org. Each product has its own setup screen, turns on the extensions it needs, and opens that product's setup when the org is ready. A new org without sensors that uses only Cloud Security or only Email Security now opens on that product.
- **Email Security spam folder**: Messages and Groups now hide mail that the provider already filed in its spam folder. A notice next to the result count says so and has a Show action. You can also use the "Include mail in the spam folder" checkbox in the filter bar. A group is hidden only when every copy is in the spam folder. By default, the Overview verdict numbers also leave out spam-folder mail, with the same checkbox to include it.
- **Cloud Security sensor coverage**: coverage now counts only running machines that can run a sensor. Serverless and managed workloads, stopped machines, and Kubernetes clusters whose nodes are already listed are no longer counted as gaps. The stats row shows how many assets were set aside and how many were matched to a sensor by hostname only. The Unmonitored compute list adds a Type column, a Next step column (install keys, instance group template, or the Kubernetes deployment guide), and a CSV export.
- **Cloud inventory age**: the Sensor coverage page shows when the cloud inventory was last collected, and adds a "Re-scan now" button. If nothing in the cloud can run a sensor, the Cloud compute lane now says "Not applicable" instead of "Unknown".

#### Bug Fixes

- On Sensor coverage, "Work compute gaps" now scrolls to the list of unmonitored compute instead of doing nothing.

---

## 2026-10-09

### Web App 6.6.0

A major expansion of Application Control, a triage-first Email Security console, richer Entity pages, Linux vulnerability verification coverage, and a clearer Cloud and Code Security experience.

#### New Features

- **Email Security overview**: the overview now leads with the work that needs an analyst: mail still in inboxes, open user reports, flagged campaigns, protection mode, and recent suspicious or malicious messages. A compact coverage strip, clearer health summaries, actionable plan warnings, flatter navigation, and a compact status table for bulk group actions round it out.
- **Email Security verdicts**: decisions made through an API key now show as "API key", and the mail provider's own spam placement (Google or Microsoft junk folder) is shown and usable in the console. Triage queues, verdict evidence, and action consent are clearer.
- **Entities**: the Recent activity table shows when, where, who, and how an activity was observed, and why a row is unconfirmed. Entity graphs draw attached sensors, possible activity, and cloud sign-ins, and show filter chips only for kinds that are present. The Email activity table lists only flagged mail, with verdict, disposition, and a link to the message. The breadcrumb returns you to the search, view, and page you came from.
- **Entities availability**: subscribed Cloud Security orgs now see Entities before connecting a cloud provider, as long as sensors and adapters can supply entities.
- **Vulnerability verification**: Linux vulnerability views show distro-verification badges, a separate unverified count, status filters, and per-host coverage. Grouped kernel findings list the contributing packages, and older installed kernel builds are labelled "installed, likely not running" with a host toggle to include them.
- **Sensor Kind**: the Sensors list adds a Kind column and filter: Endpoint agents, Browsers, Third-party EDR devices, Identity / email sources, and Cloud / log feeds.
- **Cloud Security**: Risks gets a collapsible filter rail with counts, full finding titles, and clearer finding explanations. Finding counts show the age of their source, failed reads recover and partial dashboards still render, and unknown data-store providers are explained.
- **Hive editor Markdown view**: SOPs, Org Notes, AI skills, and agent prompts can be viewed as rendered Markdown.
- **Cases**: the case detail page stays usable for cases with a very large number of detections, and auto-grouping now defaults to on in the settings form.

#### Bug Fixes

- The case queue SLA column now uses the org's configured SLA targets instead of the built-in defaults.
- Mark False Positive no longer opens the testing workspace over the generated rule.
- Query Console warns about an unknown source instead of crashing.
- The floating assistant no longer covers drawers, pagination, or bulk-action bars.
- After a deploy, an open tab recovers from stale page chunks with a single reload.
- Compliance stays usable when some reads fail, and stops retrying failed scroll loads.
- Email Security sparse searches stay complete, and status badges in queue cells are spaced and stacked correctly.
- Bulk action bars stay on one line, with responsive overflow.

---

## 2026-10-05

### Web App 6.5.0

Email Security is now generally available. This release also adds a new Application Control page, clearer compliance reports, Cloud Security setup and page improvements, a System theme option, and faster loading.

#### New Features

- (Email Security) **Email Security is generally available**: protect Microsoft 365 and Google Workspace mailboxes through the provider API, with no MX or mail routing change. Every message gets an explainable verdict, and you can search, investigate, and remediate it from the console. A guided setup takes you from connecting a provider to your first results. Messages, recipient groups, campaigns, and user reports each have their own triage view, with bulk remediation and Hunt for searching past mail. Detection rules, policies, and warning banners are managed in Settings. Subscribe to the Email Security extension to enable it. See [Email Security](../email-security/index.md).
- (Cloud Security) **Clearer pages and setup**: Identity Risks rows link to Identity 360 and to that identity's findings, and Access loads much faster. The Policies page states the real collection schedule. GCP setup lists the optional roles for CIS GCP v5.0 and the APIs to enable. The Google Workspace permissions list shows every scope. Microsoft 365 onboarding can generate a certificate for full coverage.
- (Compliance) **Why a control is incomplete**: reports keep all four result statuses, and Manual is used only for organizational attestations. Controls explain why they are incomplete, such as collection still running, stale data, or missing inventory. You can filter by reason, and the export includes the same explanations.
- (Application Control) **Application Control page**: manage policies and rules in one place. Create, edit, duplicate, enable, disable, and delete policies, and search and filter rules. Policies are listed in the order a sensor applies them, and a policy fully covered by an earlier one is marked Unreachable. New `app_control.get` and `app_control.set` permissions, and Git Sync support for Application Control. Requires the Application Control extension.
- (Platform) **System theme**: the appearance setting now offers Light, Dark, or System, which follows your operating system.
- (Platform) **Faster loading**: the console starts faster, organizations load sooner, and the Sensors list loads faster for large fleets. Sensor filters show a loading indicator while a query runs.
- (Platform) **Navigation**: Give Feedback is in the Cloud Security sidebar. Users & Roles, REST API, and Access Control Lists are now tabs under one Access Management link. Extension pages share one layout and filter bar.
- (Playbooks) **Python SDK version**: choose the Python SDK version (v4 or v5) for a playbook.

#### Bug Fixes

- (Platform) The API key permission picker now offers all assignable permissions.
- (Detection) Importing a community rule keeps the rule name and enables Create.
- (Billing) CSV exports write negative amounts as numbers, and unit prices no longer show as $0.

---

## 2026-09-16

### Web App 6.4.0

A personal LimaCharlie Bots workspace, a Code Security overview backed by real scan coverage, and GitLab and Bitbucket source-control connections.

#### New Features

- (Bots) **LimaCharlie Bots workspace**: a personal workspace at `/sessions/workspace` where you switch between named bots, build groups, and watch them hand work to one another. It carries a persistent roster, direct and group conversations, `@mentions`, saved drafts and read state, published files, questions and approvals, pause and stop, and explicit review and continuation. Each bot shows live progress: elapsed time, the tool it is running, what it is waiting on, and what is queued behind it. Handoffs between bots play as a compact bubble row above the composer, so an exchange is readable rather than gone before you see it. For users in the rollout, the AI Terminal button opens the workspace; the legacy terminal is one click away.
- (Bots) **Start a fresh chat and browse history**: a New chat action gives a bot a clean runtime while keeping its configuration, saved memory, routines, and readable history. Past chats open read-only, with artifact downloads still available. Drafts and scroll positions stay separate per chat. Group conversations get the same New chat button, history picker, and read-only history view.
- (Bots) **Bot memories**: a Memories browser in conversation details lists a bot's saved notes with names and timestamps. You can read, edit, and delete them. In a group you pick whose bank to open. Changes apply to new sessions and never touch chat history.
- (Bots) **Routines**: scheduled routines move out of conversation details into their own destination at `/sessions/workspace/routines`, linked from the roster, the conversation header, and the quick switcher. Search every routine, filter by upcoming, paused, or needs attention, manage schedules, and inspect run history. A "Make this recurring" action on a bot's result builds the routine from the original request instead of asking you to retype it.
- (Bots) **Bot avatars**: the free-text avatar field becomes a searchable gallery of 24 illustrations with live preview and a deterministic default. Existing initials, emoji, and icon names still render.
- (Bots) **Auto-approve is on by default**: every eligible bot in a chat starts with auto-approve on. Per-bot opt-outs are kept, persist across a reload, and survive a change of group membership.
- (Bots) **A starter team that knows the platform**: the generic Lead, Hunter, Response, and Reviewer roster is replaced by six LimaCharlie specialists — Sensor Fleet Operator, D&R Rulesmith, LCQL Hunter, CloudSec Cartographer, MailSec Investigator, and Automation Fabric Engineer. Each has focused operating instructions that route through the LimaCharlie AI skills.
- (Cloud Security) **Code Security overview**: Code Security opened on a repository table, which hid most of what it does. A new default Overview tab leads with a prioritized fix queue — one dependency upgrade, and how many findings and repositories it clears — plus scanner coverage across active repositories, the capabilities your connected GitHub Apps actually hold, and a code to image to running-workload evidence strip. Repository, image, and registry inventories keep their tabs.
- (Cloud Security) **Code Security's controls follow detected App permissions**: the UI used to infer what it could do from connection settings, and told orgs whose App already held the permission to go install a second one. It now reads the App's real capabilities. Available shows no notice, unavailable names the missing permissions and links to the install page, and unknown says the check could not be made and will be retried. Where an org has several connections, the ones that cannot publish are named. Capabilities are asked per repository, so a repository outside an App's selection is no longer told a check is available. Every answer states how fresh it is.
- (Cloud Security) **GitLab and Bitbucket Cloud connections**: both can now be added and edited from the Cloud Security provider wizard like every other provider, with inline validation that matches the backend, the exact token scopes named on the permissions step, repository badges, and "Open on provider" links.
- (Cloud Security) **Pull-request checks from the Code page**: Code Security can scan what a pull request introduces and publish the result as a check run a team can make required, but nothing reacted to a `pull_request` delivery, so that check never fired. Three webhook rules now cover it — rescan a repository after a push, check a pull request, and re-check one whose base branch moved. That last case GitHub reports without any push, so the check kept the conclusion it had and left a green gate on a diff nobody scanned. The Code page installs and removes the rules, with a badge per rule; previously they had to be written by hand with `limacharlie hive set`.
- (Sensors) **Event Collection reads its event types from the extension**: the Event Types picker was built from a bundled list that had fallen behind and was missing 40 real events, so a recently added event could not be selected at all. It now reads the list from the Exfil extension, so new events appear as the platform adds them. A rule naming an event the extension no longer reports keeps that value instead of being written back truncated.
- (Platform Logs) **Audit log detail panel**: selecting a log used to squeeze the table into a narrow split. The detail now opens as a drawer over the table, with the event type and time in its header, the payload below, and Escape to dismiss.
- (Extensions) **Varist scan paths**: an "Online only" checkbox on the sensor picker. An offline sensor is dropped rather than queued, so listing every sensor in the org was inviting a scan that would never run.
- (Outputs) **Elastic output**: the `is_compress_request` parameter is described, so the gzip toggle renders as an optional checkbox.
- (Platform) **Startup animation**: app startup shows one of three security animations — radar, shield, or secure stream — in place of a generic spinner. It follows the theme and respects reduced motion.

#### Bug Fixes

- (Cloud Security) Static analysis runs unless you turn it off, but the policy form only ever wrote engines that were on, so unticking it produced a record identical to one that never mentioned it and the engine kept running. The denial is now written, and the policy form, the Code setup checklist, and the repository drawer stop reporting the engine off on every record written before it was named.
- (Cloud Security) A failed connection preflight blocks the save instead of decorating it. A required check that a source-control token is missing a scope is where an unusable connection is turned away, and "saved anyway" meant the refusal surfaced hours later in a scan status. Sync now in the edit flow is blocked on the same condition. An optional failure still saves, and a provider type with no tester is never blocked.
- (Cloud Security) The push-rescan recipe keyed on routing and hostname alone, which any adapter in the org could reuse. It now requires a signature-verified webhook delivery.
- (Cloud Security) Code Security's SBOM download accepts only https URLs, so a backend-supplied link can no longer carry another scheme into an anchor.
- (Cloud Security) Scan Diagnostics showed the last pass's targets, which drop to zero whenever no repository is due. An org with hundreds of scanned repositories read as empty. It now shows standing tracked-repository coverage, with last-pass activity as its own labelled section.
- (Cloud Security) The Code Actions setup step linked a file in a private repository. It now links the public setup guide.
- (Bots) Routines render and edit correctly when the API omits zero clock fields, and a timezone alias such as the default `Etc/UTC` validates.
- (Bots) A failed turn can start a new chat. New chat was disabled on a failed conversation with a tooltip asking you to finish work that had already released its runtime, and a provider-level failure such as a usage limit reproduced on every retry, so the conversation could never leave that state. A refused new chat now says why instead of showing the word "conflict".
- (Bots) Avatars are visually distinct and color selection is its own control, a stale prompt closes when its task stops, the message composer grows to fit a multiline draft, chat follows new messages while you are at the bottom, and duplicate approvals, answers, and sends are prevented.
- (Platform) The app no longer stays on an older deployment. "Update now" requested service-worker activation and reloaded immediately, which could interrupt the handoff and serve the old cache. The reload now waits for the new worker to take control, and unversioned files and SPA routes revalidate instead of sitting in the browser cache.
- (Add-ons) Logged-out visitors opening an Add-ons marketplace page saw a blank screen. The public route now renders inside a layout, so the page has height and the marketplace sidebar appears.
- (Extensions) Varist scan results showed a blank Status badge, and picking any Risk Level emptied the list, because the scan result often omits the rating flag. The flag is derived from the numeric rating when it is absent, and the Status column sorts on that value.
- (Platform) Light-mode warning colors are darkened for readable contrast, including investigation lane indicators and event markers.
- (Organizations) The Organizations list no longer shows a second spinner from the New Organization dialog while it loads plans and templates.

---

## 2026-09-08

### Web App 6.3.0

A full testing workspace for D&R and False Positive rules, endpoint agents as a vulnerability source in Cloud Security, and a Query Console that holds far less memory.

#### New Features

- **Rule testing workspace for D&R rules**: the rule page's stored tests and its replay panel are now one surface. A fullscreen workspace replays every stored case against the rule as currently edited and reports pass or fail per case, with a summary in the section header. A replayed event can be saved onto the matching test side in one click, so an ad-hoc probe becomes a stored case. A second workspace runs the rule over stored telemetry as a historical scan and renders each hit as a row, with a "Keep as non-match test" button that stores the hit's matched payload on the suite. Each suite row also gets a play button beside Run all, so one case can be re-run without disturbing the other verdicts.
- **Rule logic tree**: the detect block renders as its boolean tree with the replay evaluation drawn on it. Green nodes evaluated true, red nodes false, and dashed nodes were short-circuited. Clicking an operation shows what it read, what it expected, and what it saw in the event. Multi-event runs get a per-event switcher, a failed run pre-selects the operation that killed the match, and stateful rules render their `with child` and `with descendant` subtrees. Anything the view cannot reconstruct from the trace falls back to the raw lines rather than guessing.
- **Test coverage on the rules list**: a sortable Tests column shows each rule's case count, and a coverage readout beside the filter controls reports over the rows on screen. Narrowing to Custom rules answers how much of what your own team wrote is tested, instead of being dragged down by managed and service rules.
- **A rule now tells you how much it matches**: saving an enabled rule replays the last hour of stored telemetry in the background and reports how often the rule matched. A count at flood level (100 an hour or more) comes back as a warning. A rule that is too broad announces itself seconds after the save instead of hours later in Detections. False Positive rules report suppressions and never warn, because a busy suppressor is a working one. Metadata-only saves skip the check, and a failed check stays silent rather than blocking the save.
- **The save gate matches the server**: saving a rule with failing tests always failed at the API, but the dialog offered "Save anyway". It now blocks the save and routes into the rule testing workspace. A `report`, `add var` or `del var` action with no `name` is also caught inline in the editor rather than as an opaque API error.
- **Edit rules in YAML or JSON, with import and export**: the D&R editor gains a YAML/JSON toggle over the detect and respond editors, file export of the stored shape (detect, respond, tests) as `.yaml` or `.json`, drag-and-drop import validated before it reaches the editors, and smart paste on the detect editor. The editor sniffs each rule's format on open and warns before a conversion would drop YAML comments. False Positive rules get the same toolbar.
- **False Positive rules get the full testing experience**: the testing workspace and the rule logic tree are now on the False Positive rule page as well.
- **Promote a Query Console query to a D&R rule**: an LCQL query converts to a detect block with no AI involved. Sensor selectors, event types and the filter expression tree all map across. Time ranges and projections are dropped with an explicit note. Anything that would make the rule broader than the query, such as an unsupported operator or an incomplete query, stops the conversion instead.
- **Test a detection against its rule**: a new action in the detection viewer opens the originating D&R rule's testing workspace with the triggering event preloaded. It appears when the detection carries a real sensor event and the viewer holds the replay permission.
- **Endpoint agents are a vulnerability source in Cloud Security**: a new Policies tab turns the endpoint-agent vulnerability lane on, so CVEs a LimaCharlie agent reports become Cloud Security findings. The Coverage tab reports the lane beside cloud compute coverage, a host with no cloud provider behind it renders as a first-class resource with its own findings and pivots, and a finding's kill chain badges the hops a LimaCharlie agent covers.
- **More to go on when triaging a vulnerability**: findings now carry the exploit band (KEV overdue, KEV due, exploit likely, exploit probable, elevated, baseline), whether a fix is available, which lane observed it (cloud, agent, or both), and CISA's KEV due date. Each of these is absent when the platform did not report it, and an absence is shown as unknown rather than as a negative answer.
- **VEX and SLA policy editors**: two `cloudsec_policy` types had no authoring surface, and both sit behind a headline feature. Policies gains a VEX tab for the OpenVEX documents that move a finding to "not affected" with author provenance, including a client-side parse preview, and an SLA tab for the clock behind every finding's due date. A finding can now be marked not affected from the finding itself.
- **Coverage page**: the Inventory tab's sensor coverage becomes a Coverage page that reports each lane separately, so a workload with an agent but no vulnerability source no longer reads as fully covered. The org-level pending count for endpoint-agent inventory is reported instead of being dropped.
- **Shared fixes**: when one remediation resolves several findings, the finding shows the other findings it covers and drills through to the exact cause.
- **Integrations panel**: Cloud Security accepts SARIF, CycloneDX, LimaCharlie scanner reports and third-party asset batches, and every one of those doors was API-only and named nowhere in the app. Settings gains an Integrations tab that documents them in-product, deep-linkable at `?tab=integrations`.
- **Identity and asset filters**: the Access and Assets screens gain server-side selectors, and sensitivity counts survive a cross-filter instead of resetting.
- **Compliance reason codes**: a control that was not assessed now says why, rather than sitting blank. Azure authorization evidence has its own view, and a finding whose authorization coverage has a gap is classed as such.
- **Managed Kubernetes clusters are typed**: the platform is retyping managed clusters from `ComputeInstance` to `KubeCluster`, with namespaces, workloads, services and roles alongside. Every Cloud Security list and map keyed on resource type now understands them, so a cluster keeps its place in the compute population and is classified the same way on every path that reaches it.
- **The Providers list names the provider**: the source badge and the record name become one identity column with the brand glyph, the record name, and the provider's full name spelled out under it. A provider type this build has never seen degrades to a neutral badge carrying the raw token instead of rendering blank.
- **Elastic output**: the `is_create_action` parameter is described, so the output editor renders it as an optional checkbox instead of an unlabelled required field.

#### Bug Fixes

- The event tree could crash the app. An atom cycle in `routing/parent` and `routing/this` recursed until the stack blew and tripped the global error boundary. The tree and the ancestor walk now track the atoms they have visited, read a self-reference as "no parent", and truncate instead of spinning.
- Atoms and sensor ids interpolated into Insight URLs are now escaped. Event data decides what an atom contains, and one carrying a `/` rerouted the request to a different endpoint that answers with a success and no event, so the ancestor chain silently truncated with no error. Detection ids are escaped on both the read and the delete.
- The extension definition editor showed every permission unchecked no matter what the extension held, and saving from that state dropped every permission the user did not happen to re-tick.
- Selecting a rule from halfway down the D&R sidebar jumped the list back to the top. The sidebar now keeps its scroll position while the editor still resets.
- Pasting a second rule while a smart-paste suggestion was still showing kept the stale card and never offered the new suggestion's action.
- The inline "mark as crown jewel" prefill seeded the resource family instead of the resource kind, which the platform rejected for data stores and identities and mis-seeded for compute.
- Renaming an AI Session with a name over 200 characters failed with a raw API error. The input now shows an inline error and the mutation never fires. Length is counted in code points, so an emoji-heavy name the API accepts is not rejected.
- A tooltip on truncated text now re-measures when its container resizes, so it appears and disappears as the column changes width instead of going stale.

#### Improvements

- **The Query Console holds far less memory.** A loaded search now releases the rows on pages far from the viewport and fetches them again from the continuation token when you scroll back. What a search retains no longer grows with every row it has ever loaded, so a very large result set stays usable.
- **The Detections live feed holds up under a flood.** Every incoming batch used to re-sort the whole accumulated list. Batches now merge into the already sorted rows.
- Section collapsers can be dragged with touch as well as a mouse, and stop dragging cleanly when the tab is hidden or focus is lost.

---

## 2026-08-20

### Web App 6.2.0

Resizable columns on every table, more of LimaCharlie extensions moving onto first-class pages, multi-provider credentials for AI Sessions, better reporting when a search leaves events out, and keyboard navigation in the org pickers.

#### New Features

- **Resizable columns on every table**: column resizing is now on by default for every table in the app, not just Search results.
- **The Query Console tells you when a search left events out**: a search that sheds events used to report "Complete!" regardless, and a query whose only match was skipped rendered as "no results". A warning badge in the status row now carries the headline count ("16 events skipped"), and a notice card above the results — closed by default — carries the per-reason breakdown, an explanation of why the search moved past those events rather than stalling, and a sampled list of them.
- **Dedicated YARA Scanners page**: `ext-yara` replaces the generic schema-driven renderer with a first-class page at `/orgs/:oid/yara-scanners`.
- **Dedicated File & Registry Integrity page**: `ext-integrity` replaces the generic schema-driven renderer with a first-class page at `/orgs/:oid/integrity`.
- **Dedicated Sensor Cull page**: `ext-sensor-cull` replaces the generic schema-driven renderer with a first-class page at `/orgs/:oid/sensor-cull`.
- **AI Sessions: multi-provider credentials**: alongside Anthropic, you can now connect OpenAI, Google Gemini and OpenRouter, each with its own auth methods (API key, Azure OpenAI, Vertex for Gemini, Bedrock/Vertex for Anthropic). Session profiles gain a Provider select, session details show which provider a session ran on. See User Settings → AI Terminal.
- **Keyboard navigation in the org pickers**: both the full-screen `/orgs` list and the bottom-left org switcher autofocus their search field, let Tab move into the results, arrow keys move the highlight and Enter selects. A single filtered match is preselected, so typing enough to narrow to one org and pressing Enter enters it.
- **Export affected hosts from Vulnerability Reporting**: an Export hosts control (CSV or Excel) on the CVE detail page, the CVE drawer's Impacted Assets tab, and the package drawer's Affected hosts section. The export drains the entire listing rather than the pages the table happened to load, de-duplicates by sensor, and reports truncation instead of passing a partial file off as complete.
- **LOLRMM community rules render properly**: LOLRMM rules are plain Sigma YAML and now open in the Sigma detail view instead of falling through to the "Unable to parse rule content" raw fallback.
- **Entra ID adapter on Microsoft national clouds**: the Entra ID setup and edit forms gain the endpoint picker already offered by the Defender adapter, so a US Government tenant (GCC High, DoD) can be configured. The field is optional and omitted when unset, so existing commercial adapters are untouched.

#### Bug Fixes

- Values loaded into a creatable multi-select rendered as empty — every existing pattern on an Artifact Collection or File & Registry Integrity rule was invisible in the edit modal. Adding one pattern to a field that looked empty silently replaced all the pre-existing ones on save.
- AI Terminal state no longer bleeds between sessions: file upload and download cards stayed pinned to the session they happened in rather than appearing in every conversation, and switching sessions no longer carries over the composer draft, the retry prompt, the download bar or a stale "queued behind a blocked turn" notice. A freshly started session also no longer sits idle because an earlier session in the same tab already consumed an initial prompt.
- The permissions table no longer overflows the addon and extension editors' modals, where the Write column sat off-screen until the user scrolled sideways.
- Opening an app that has been deleted from a stale link now shows a "not found" zero state with a route back to the launcher instead of a load failure, and a malformed link no longer crashes the render.
- Artifact Collection with no configuration saved yet reads as "no rules yet" instead of reporting an error.

---

## 2026-08-13

### Web App 6.1.0

Several UX improvements, new remediation signal (SLA due dates, root-cause roll-ups, coverage honesty), updated UX for some extensions, and performance improvements for Query Console.

#### New Features

- **Cloud Security speaks one language**: every remaining screen — Inventory (Resources and Third-party assets), Attack Surface, Access, the Query Console, Compliance, Policies, Settings and the MSSP fleet board — now opens on the shared tinted filter bar.
- **Compliance report layout**: the Compliance screen becomes a charts-and-rail report — a compliance-score donut and a failures-by-severity bar chart side by side, the controls table beneath them, and the assignment cards as a rail running down beside all three.
- **Cloud Security fleet board modernized**: `/cloud-security` adopts the UI language, adds two fleet rollup donuts, makes every column header a sort control, and splits freshness into sortable Last scan and Providers columns so a failing provider count is its own column rather than a badge in someone else's cell.
- **SLA due dates on the findings worklist**: findings gain a Due column showing relative age ("in 6d", "12d ago", "today"), with a tooltip carrying the exact deadline, the SLA state, and the policy clause that set it.
- **Root-cause roll-ups on findings**: when one finding's remediation already implies another, the child shows a "root cause" chip that links straight to its parent and the parent shows how many findings it implies.
- **Compliance score honesty**: a framework that grades only a fraction of its controls no longer shows a bare green score. The score loses its good-result tint and states how much was actually assessed.
- **Vulnerability-source coverage**: the Coverage tab adds a second dimension beside sensor coverage — whether anything is actually reporting CVEs on a workload — computed per scanner scope, so a workload with a sensor but no vulnerability source no longer reads as fully covered.
- **Real internet entry points in the kill chain**: the first hop now renders the actual front door — App Service, Cloud Run URL, Kubernetes API server, function URL, load balancer, CDN, AI inference endpoint — labelled with its hostname, instead of a generic globe that said nothing about how an attacker got in.
- **Privilege escalation and cloud hierarchy in Topology**: scope-escalation hops render as their own edge category with a distinct signature and priority on a crowded canvas, and cloud-hierarchy containers (organization, folder, project, account) draw as containers rather than workloads.
- **AWS boundary and trust evidence**: permission boundaries, boundary-capped grants and trust-policy conditions on can-assume edges now have a screen, and a finding's cloud is read from the finding itself so vulnerability-coverage aggregates keep their cloud badge and readable resource name.
- **Dedicated Event Collection page**: `ext-exfil` replaces the generic schema-driven form with a first-class page.
- **Dedicated Artifact Collection page**: `ext-artifact` gains a custom made UI page with Collection Rules and PCAP Capture Rules tabs.
- **Dedicated Reliable Tasking page**: `ext-reliable-tasking` moves off the generic schema renderer onto a custom page.
- **The shared filter bar reaches the rest of the app**: the Platform Logs audit tab, False Positive Rules, and the sensor Vulnerabilities tab all move onto the same panel. The sensor Vulnerabilities tab's four bordered summary tiles become stats on the bar, and the Payloads list moves onto the standard table so dates and sizes stop wrapping.
- **New Org and Recent Org lists for everyone**: the redesigned organization and recent-organization lists are now the default for all users.
- **Query Console performance**: a search over a large result set now completes much faster, holds less memory and spends less time in garbage collection. Scrolling with a row selected is more performant, and result sets that previously exhausted the browser's heap now load.
- **Connect wizard permissions**: the provider setup flow's "Permissions required" list now includes the AWS Organizations policy reads and the GCP Cloud Run / Cloud Functions viewer roles, so a customer following the least-privilege list verbatim gets the public-invoker exposure verdicts rather than silently missing them.

#### Bug Fixes

- A single transient failure while polling for search results — a 502, a dropped connection, a laptop changing networks — permanently ended the search with no explanation; polling now survives it and picks the query back up.
- Returning to the Query Console tab after a network reconnect silently re-ran a finished search as a brand new server-side scan, replacing the results on screen and billing the org a second time.
- A crash affecting dropdown menus ("Maximum update depth exceeded") caused by an upstream `react-select` bug is fixed.
- The Cloud Security "Failed" sync badge showed the collector error only as hover text that could not be selected or copied; the tooltip now stays open and the badge copies the raw error to the clipboard.
- The Vulnerabilities tab and section no longer appear on a sensor's detail view for organizations not subscribed to vulnerability reporting, where they showed a misleading empty "0 findings" report.
- The CAASM coverage-policy editor offered a capability no source could satisfy, which produced a permanent coverage gap on every device; it is removed from the picker, and policies that already contain it render as unsupported instead of blank.
- SOPs and Organization Notes had no working "View Docs" link, and their editors called records "Sop" and "Org_notes"; both now link to the published documentation and use proper record type names.
- The Inventory resource count rendered unformatted (`373109 assets`) while every other count on the screen used thousands separators, and a shared accessibility defect meant several dropdowns' labels were not associated with their control.
- The "EDR everywhere" policy template button appeared to do nothing due to a read-after-write bug, and a full-screen empty state could swallow clicks on neighbouring controls.

---

## 2026-07-29

### Web App 6.0.2

A rebuilt Cloud Security Risks triage table, finding ownership as a filter and column, a self-serve Cloud Security upgrade flow, and a reorganized sidebar.

#### New Features

- **Cloud Security Risks — dense triage worklist**: the card-per-finding list is now a ruled, sortable table at roughly twice the row density, a sticky header, server-side sorting on Risk and Severity, and select-all in the header checkbox so the bulk triage bar only appears once you pick rows. Multiple UX improvements related to this change.
- **Owner facet and column on Risks**: findings can now be filtered and scanned by who owns them. An Owner group in the facet rail lists Unassigned first, then your own account marked "(you)", then everyone else by count.
- **Data Security matches the Risks layout**: the Data Security screen adopts the same tinted filter bar, flat facet rail and badge styling as the Risks worklist.
- **Self-serve Cloud Security upgrade**: free-tier orgs can now upgrade without leaving the page. The trial band's CTA on the Cloud Security Overview opens an in-context upgrade modal that explains what upgrading changes, quotes the real monthly price for your org, collects payment details only if there's no card on file, and confirms on completion.
- **SOPs and Organization Notes move to Organization Settings**: both sidebar entries move out of Automation — where they sat next to D&R rules, playbooks and lookups — into the Organization Settings group after Integrations, with matching breadcrumbs. Existing links and bookmarks to /sops and /org-notes still work.
- **Apps entry always visible in the sidebar**: the Apps navigation item no longer disappears for users lacking the app.get permission; it renders for everyone and the page itself explains the missing permission when opened.

#### Bug Fixes

- The "Cloud Security isn't enabled" screen sent its main button to the extension's configuration page, which has no way to subscribe and often showed a permission wall; it now goes to the marketplace entry where the extension can actually be subscribed, and the button reads "View extension".
- Cloud Security still described itself as pre-GA and not publicly subscribable in the not-enabled gate and the feedback modal, even though it is generally available and self-serve.
- The Risks lens picker showed an empty "Select..." whenever the active class filters didn't match a preset lens, making it look like no lens was applied while a filter was in fact active; it now reads "Custom".
- Cloud resources were classified by their name, so a load balancer called "public-lb" was drawn as the internet node and a VM called "db-1" was drawn as a data store; classification now uses the resource's actual type. Similarly, an IAM principal named something like "public-reports@..." was labelled "Public - anyone on the internet".
- The fleet board's top attack path card navigated to a retired URL and silently bounced users to the org Overview; it now opens the Attack Surface workspace, and old bookmarked path links redirect there too.
- Third-party assets and reconciled inventory assets both displayed as "Third-party asset" in the graph type filter and node labels; inventory assets now read "Inventory asset".
- The shared-fix strip and the "resolves N findings" count only considered one kind of root cause, so privilege-escalation causes never appeared and mixed causes were counted twice — the strip and the finding detail card could disagree on the same fix. The shared-fix card also described every cause as a firewall rule, even when the fix was an IAM role binding.
- Sortable Risk and Severity column headers rendered a truncated "..." because the label plus the sort icon didn't fit their track.
- In dark mode, Risks table rows swallowed their own dividers and the header band.

---

## 2026-07-28

### Web App 6.0.1

A small fix to the Cloud Security onboarding sign-up flow.

#### Bug Fixes

- Signing up from a Cloud Security onboarding link still asked which product you wanted before creating an account, even though the link had already committed you to one.

---

## 2026-07-27

### Web App 6.0.0

Cloud Security goes generally available, a one-link self-serve onboarding flow, and a rebuilt Cloud Security Overview dashboard.

#### New Features

- **Cloud Security is generally available**: the product is no longer gated behind an early-access flag, so every organization with the Cloud Security extension sees it in the sidebar.
- **Self-serve onboarding link**: a single shareable URL - `/onboard?purpose=cloud-security` - now takes someone from no account to a working organization.
- **Cloud Security Overview rebuilt**: the Overview now uses the same flat dashboard language as the Case Management dashboard.
- **Full-screen kill-chain view**: the most-critical-path tile gains a "View full screen" action.
- **Trial status on the Overview**: organizations on the Cloud Security trial now see a banner at the top of the Overview stating the provider-connection cap and how many are used, the trial length, and a "See plans" link — instead of only finding out when they hit the limit.
- **Provider-aware connect wizard diagram**: the diagram in the provider setup wizard now draws what the provider you selected actually contributes — compute, network, data, identity, AI and vulnerability coverage for a cloud, or identities, apps and devices for a directory — and labels the credential path with how that provider authenticates (IAM roles, AssumeRole, GitHub App, and so on). The edge into your workspace now states the sync cadence you just chose on that step.

#### Bug Fixes

- The Overview coverage bar read 100% in nearly every state, because it counted only sources that had already completed one sweep rather than the estate itself; it now reports accounts collecting, shows a real shortfall while a connected source has delivered nothing, and stays empty rather than showing 0/0 before the first scan lands.
- Privilege-escalation findings were drawn with an invented "Internet -> public exposure" entry hop and a rationale claiming an open attack path, even for identity-only findings that are not internet-reachable; the exposure claim is now only made when the backend asserts it, and entitlement hops are labelled "can assume" instead of "reaches".
- The generic rationale on some findings printed a bare category name such as "High ciem."; the three entitlement categories now spell out what they mean.
- Verifying your email during sign-up sent you to the organization list and lost the onboarding flow you started; the verification link now returns you exactly where you left off, and the original tab no longer sits on a stale "verify your email" card after verification completes.
- The choke-point sentence naming your crown-jewel resources appeared in English in every language; it is now translated across all locales.
- Creating a secret inline in the provider wizard labelled the name field "New secret (required)", which read as if it were the credential itself; it now says "New secret name". Providers that take a raw key (LimaCharlie, OpenAI, Anthropic) also show a bare-key placeholder instead of suggesting a JSON wrapper.
- The provider wizard and first-run artwork drew logos for internal resources on a provider LimaCharlie does not support; the illustrations no longer use them.

---

## 2026-07-26

### Web App 5.14.0

A redesigned permissions editor, modernized Outputs and Artifacts experiences, and an "Overview" org diagram.

#### New Features

- **Permissions — grouped, read/write-aware editor**: the flat ~120-row permission lists become collapsible resource groups (collapsed by default, search auto-expands matches) with separate Read and Write bulk toggles per group.
- **Outputs — modernized list and dry-run testers**: the Outputs list moves to the modern sortable table. New "Test Transform" / "Test Template" modals dry-run expressions server-side against an editable sample event before saving, and a WebSocket output destination is now creatable from the UI.
- **Artifacts — modernized list and full-screen viewer**: the Artifacts list becomes a Detections-style table with a new full-screen record viewer.
- **Org Overview diagram**: new "Overview" page with high level diagram.
- **Search — full-data exports**: the query console download menu splits into "Visible columns" (CSV/Excel/HTML/PDF, mirroring the table) and "All fields" (NDJSON plus new CSV/Excel that export every flattened field of every event), so nested event details are no longer dropped from spreadsheet exports.
- **Sign-up — Grid escape hatch**: the sign-up flow asks whether users want the full LimaCharlie platform or the AI-assisted Grid before choosing an auth method.
- **Entra ID adapter**: an optional `streams` parameter (risk detections / sign-ins / audit logs) is exposed in the cloud adapter form and CLI template, and USP sensor tiles gain per-type documentation links (starting with Entra ID / Azure AD / Office 365).
- **Extended localization**: extension pages for 10+ more extensions are now fully localized across all nine languages.

#### Bug Fixes

- Permission checkboxes in the API-key, add-on, and extension editors updated the form value but never visually toggled after the grouped-editor rewrite; they now toggle correctly.
- Privileged permissions (`apikey.ctrl`, `user.ctrl`, `billing.ctrl`) could be bulk-granted in one click via select-all in the API-key/extension/add-on editors; they must now be granted individually.
- A hidden HoverCard added a second window scrollbar on every page that used one, sliding the app under the sidebar when scrolled.
- The modal close button floated over scrolled content in tall modals (e.g. the Data Classification rule editor); it now pins to the content and scrolls with the header.
- The sidebar collapse caret was hidden and unclickable on tablet-width viewports because the fixed top navbar overran the sidebar rail.
- Sortable table column headers wrapped their sort icon onto a second line in narrow columns (e.g. the Sensors "Type" column).
- Long unbroken tokens (resource ids, base64 keys) overflowed the CAASM "What Changed" column.
- Opening a Data Classification rule authored via IaC could crash the item detail when a hand-authored rule carried non-string values; such values are now coerced safely.
- The Artifacts list sent Insight timestamps in milliseconds instead of seconds, breaking the feature once the API began rejecting out-of-range values.

---

## 2026-07-15

### Web App 5.13.0

Expanded Vulnerability Reporting, a revamped audit log, a redesigned REST API section, and continued localization across the extension catalog.

#### New Features

- **Vulnerability Reporting**: a new Vulnerable Packages tab (with a package drawer listing live affected hosts) and a "Group by application" toggle on per-host tables that collapses per-CVE rows to one line per application. Exports are stamped with org name and OID, gain a server-generated remediation-plan CSV and a vulnerable-packages CSV.
- **Vulnerabilities dashboard polish**: the Packages table collapses like the other tabs, posture stats match the detail-panel strip, and the CVE and package detail sidebars cross-link to each other. The CISA KEV catalog now opens with the full filter parameters applied.
- **Audit log revamp**: the Platform Logs audit tab adds sensor, date-range, and event-type filters plus client-side origin/identity search, bidirectional infinite scroll ("Load newer events"), and a row detail panel with a scrollable JSON viewer of the raw record.
- **REST API section redesign**: API Details becomes a compact definition card with hover-to-copy on API Root, OID, and Org JWT and a Swagger reference link. The User-Generated, Service-Managed, and Ingestion key tables move behind a segmented pill switcher showing one table at a time, with a contextual Create button and one-line dates.
- **EPP status dashboard**: the per-sensor EPP status page is redesigned as a status dashboard, with the metric tiles filled out and macOS status, product name, and not-subscribed states corrected on the Sensor Overview EPP card.
- **AI provider onboarding**: a CLI escape hatch lets you configure AI providers not yet supported in the guided onboarding flow.
- **Internationalization**: continued localization of the extension catalog - Artifact, binlib, reliable-tasking, EPP, dumper, integrity, feedback, exfil, atomic-red-team, govee, hayabusa, infrastructure, lookup-manager, and ~30 more extension pages are now translated across all nine locales.

#### Bug Fixes

- Tooltips now render above modals instead of behind them.
- Cloud adapter forms now enforce required secret and number fields before submit.
- Sensor Overview hides cards and chips that don't apply to adapters and USP sensors, long tags no longer blow out the Overview grid, and EPP status resolves instead of stalling on "Waiting for sync".
- A newly created hive record shows its GUID immediately, and User ID click-to-copy is restored on the account settings page.
- Workload Scanning last-scan stats are corrected (wire tolerance) with a richer Last Scan detail, and the "Findings closed" column in Top remediations is fixed. The CVE sidebar count stat is labelled "Findings" rather than "Impacted hosts".

---

## 2026-07-09

### Web App 5.12.0

The console and Grid app are now fully localized in English, Español, 日本語, Français, Deutsch, Português, 한국어, Italiano, and Nederlands alongside redesigned sensor pages and per-sensor vulnerability report exports.

#### New Features

- **Internationalization**: the console and Grid app are fully localized in English, Spanish (Español), Japanese (日本語), French (Français), German (Deutsch), Portuguese (Português), Korean (한국어), Italian (Italiano), and Dutch (Nederlands). A Language Switcher in User Settings sets the preferred language per device.
- **Sensor Analytics dashboard**: the per-sensor Analytics page is rebuilt as a responsive card-grid dashboard with a single shared time-range selector, replacing the stack of full-width charts.
- **Sensor Overview redesign**: identity, network, and system details are organized into grouped cards with inline status chips for connection, seal, network, and platform state. Seal and Isolate controls move into the page header, with the full pending/cancel state machine preserved.
- **Search progress indicator**: the query console status line shows a live percent-scanned figure while a paginated query runs, with a hover tooltip listing batch, event, and data counts for the in-scope scan. Cancelled searches are now labelled "Cancelled" instead of "Complete!".
- **Per-sensor Vulnerability Report export**: the Sensor Vulnerabilities tab adds an Export report menu with PDF, HTML, Markdown, CSV, and Excel formats. Reports include a KPI summary strip, top remediation recommendations aggregated by package and fix version, and the full findings table (CVE, application, version, severity, score, LC Risk, EPSS %, KEV, fix version, first detected date).
- **Builder Program promo**: free-tier users periodically see a Builder Program offer (first 3 months free) in the console. The promo is limited to first-party LimaCharlie branding, shown at most once every 7 days, and suppressed permanently once a user expresses interest.
- **Vulnerability tables: First Detected and Version columns**: both the sensor-level and org-level vulnerability tables add a sortable First Detected column (the date a vulnerability was first observed on the host, marking the start of the remediation clock) and a Version column showing the installed version of each vulnerable package. The version value also feeds the compliance CSV export, replacing a previously hardcoded blank.
- **Vulnerabilities dashboard and CVE detail redesign**: the org Vulnerabilities page replaces the 2×4 KPI card grid with a compact posture strip, brings charts forward, and narrows the CVE list/detail gracefully on smaller viewports. The CVE detail gains a cleaner CVSS metric card and a full-width EPSS percentile meter with banded severity coloring.
- **Microsoft Defender adapter**: an optional Endpoint field targets Enterprise (Commercial), GCC, GCC High (L4), or DoD (L5) Microsoft cloud environments. Existing adapters continue to use the enterprise endpoint by default.
- **SentinelOne adapter**: optional `site_ids` and `account_ids` fields scope ingestion to a single tenant of an MSP/partner console, and a `collect_agents` toggle pulls all in-scope endpoints as individual sensors immediately rather than waiting for telemetry.
- **Sensor sub-page tables**: Autoruns, Drivers, Event Collection, Packages, Users, Services, Integrity, and Processes migrate to the updated table component, gaining sortable column headers, truncation tooltips, and consistent viewport-fill height. Event Collection and Integrity rule chips move into per-row kebab menus, and several empty-state typos are fixed.
- **Analytics charts**: all analytics charts across D&R rules, False-Positive rules, Outputs, Adapter Analytics, VibeRails, Billing quota, and the Grid app are updated. Outputs and Adapter Analytics charts now display side by side with a single shared time-range selector.

#### Bug Fixes

- The "Create new App" button now works for orgs with zero apps; a transparent overlay was intercepting pointer events over the page header.
- Opening the AI Terminal no longer crashes the app with "Maximum update depth exceeded".
- Seal and isolate pending transition states now display correctly, so "Pending rejoin" and "Pending unseal" surface during the backend transition window instead of holding on "Isolated" or "Sealed".

---

## 2026-06-29

### Web App 5.11.0

Expanded AI cost tracking adds spend breakdowns, MSSP chargeback, and a savings trend to the AI Usage page, now available in the main web app alongside deeper Vulnerabilities filtering and functional app egress.

#### New Features

- **AI cost tracking**: the AI Usage page now offers 7/30/90-day ranges, a KPI strip (spend, investigations, cost per investigation, tokens), spend breakdowns by model and detection rule with per-investigation unit cost, per-tenant re-bill markup for MSSP chargeback in the CSV export, anomaly and trend indicators, and a savings trend chart. Sub-cent costs display adaptive precision instead of rounding to $0.00.
- **AI Usage in the main web app**: the AI Usage view, previously Grid-only, is now reachable from the main web app sidebar under the AI group, gated by the `ai_agent.get` permission.
- **Vulnerabilities subscription gating**: orgs without the Vulnerability Reporting extension now see a subscribe call-to-action (for `billing.ctrl` users) or an admin-contact prompt, replacing the misleading empty state.
- **Vulnerabilities platform filtering**: the Platform facet now scopes the CVEs tab, and dashboard charts and KPI tiles update to reflect active Severity and Platform filters, with a caveat label when other filters can't be represented in the rollup.
- **Vulnerabilities application grouping**: the host vuln table splits the combined column into sortable Application and CVE columns, grouping all CVEs for a package together; the org drawer defaults to application sort and the sensor tab keeps score sort.
- **Vulnerabilities false-positive feedback**: a per-finding "Report incorrect detection" action collects a structured reason and relays it to the product team, separate from the local mark-false-positive triage action.
- **Gmail adapter**: setup and edit forms for single-mailbox OAuth and Workspace service-account flows, with per-feed capability toggles, subject scoping, and masked managed-secret storage for service-account credentials.
- **ThreatLocker adapter**: Include Child Organizations scoping for parent API tokens and individual toggles for the Approval Requests, Unified Audit, and System Audit feeds.
- **Brand feature flags**: branded deployments can disable fleet billing, case management, automation SOPs, mini apps, and the AI terminal per deployment.
- **Windows PowerShell installer**: the Windows install wizard leads with a copy-paste PowerShell one-liner using LimaCharlie's hosted install.ps1, mirroring the Linux curl installer, with the manual EXE/MSI tab still available.
- **Search timing breakdown**: the per-stage timing breakdown is now on by default for all users.
- **Sensor Connectivity**: the Add Sensor panel now lists the org's webhook endpoint alongside the existing addresses, making firewall setup for cloud sensors and webhook adapters easier.
- **Apps launcher icons**: apps now derive distinct icons from author emoji, required-permission prefixes, and other signals before falling back to the generic diamond.
- **Per-theme logos**: runtime configs support a dedicated dark-theme logo alongside the standard logo.

#### Bug Fixes

- Apps declaring allowed_origins can now make third-party fetch() calls; apps load from a real HTTP origin with their own permissive floor CSP instead of inheriting the console's strict policy. The brokered lc.api path and app isolation are unchanged.
- Apps now open correctly on Grid, which previously failed with a sandbox handshake timeout.
- Creating a false-positive rule from a detection now names the draft from the detection (category and detect ID) instead of "Untitled-1".
- Deleting a REST API key now requires confirmation through a danger dialog, preventing accidental deletion that would break integrations.
- Replaying a D&R rule with target: detection now runs against the detection stream instead of the event stream, which had matched nothing.
- Projection queries that select `ts` without an alias now show the column, formatted as YYYY-MM-DD HH:mm:ss in the table and exports.
- Saved query text can now be edited in the Edit Query modal, not just renamed.
- The saved-query size limit now matches the backend's 1024-byte ceiling, raised from a stricter 512-byte client cap.
- CVE descriptions from the NVD feed now render as sanitized HTML instead of literal tag text on the CVE detail page and sidebar drawer.
- The CVE detail page layout is now stable, with stacked tables sized to their actual row count instead of growing unboundedly or leaving large empty gaps.
- The KEV and Total vulnerability tiles now use server-computed host-wide counts instead of page-limited values, fixing incorrect counts for sensors with many findings.
- The create-case org picker now shows all cases-enabled orgs for accounts spanning more than 200 orgs, resolving names for up to 10,000 orgs.
- Social share previews are fixed for Grid and the main web app, with OG and Twitter tags added and robots.txt updated to allow social crawlers while keeping the console out of search indexes.

---

## 2026-06-18

### Web App 5.10.0

Fleet Billing arrives for MSSPs, alongside AI Terminal refinements and clearer session-state reporting.

#### New Features

- **Fleet Billing**: a cross-tenant billing console for MSSPs.
- **AI Terminal**: visual improvements and refined landing actions.
- **AI session statuses**: Running, Waiting, and Ended states, with an indicator when a session is awaiting user input.
- **Access Management**: added a Role column to the user table.
- **Case console**: added a selectable page size.

#### Bug Fixes

- Query console download now matches the visible table.
- Added a Minimize button to the AI Session chat floating button.
- Added the AI Session chat button to the sessions page.
- Restored the "Download file from session" action in the chat menu.
- Restored the app version and release notes in the profile menu, and fixed the Dark Mode font.
- Adjusted the light-mode AI Terminal card fill color for better contrast.

---

## 2026-06-11

### Web App 5.9.0

Notable improvements and fixes:

#### New Features

- **AI Terminal ShareCard** — share sessions socially and invite users to tenants.
- **Docked corner chat** — persistent AI chat launcher with pop-out, draft-new-session, minimize/maximize, and a live-session selector.
- **Session fork** — fork an AI session with full lineage tracking.
- **Card-list session browser** inside the chat layout with a unified action dropdown.
- **Onboarding demand-signal cards** for unsupported AI providers.
- **Feedback rich card** plus unsupported-request guidance for the AI FDE.
- **ThreatLocker** platform and adapter support.
- **AI Workbench** — agent usage moved into a dedicated Usage tab.
- **Search** — scroll-to-top/bottom buttons, perceived + server timing on the status line, and query ID in the timing breakdown tooltip.
- **AI Sessions** — rationalized session user state (Active + needs-attention), and `lc-compliance` as a selectable plugin.
- **Git Sync** — added missing config hives to the UI.

#### Bug Fixes

- Fixed dark-mode LimaCharlie logo visibility.
- Included `ai_agent.operate` in FDE and worker-key permission lists.
- Cases — batched bulk assign / tags / close-note to avoid rate-limit failures.
- Restored the agent list table in the AI Agents tabs.
- CVE detail now opens from the sensor vulnerability list.
- Timestamp column hidden for aggregation search results.

---

## 2026-02-08

### Web App 5.5.5

Enhancements to the AI Sessions experience with granular permission controls and improved session management, adds Windows ARM64 sensor support for customers on newer Windows hardware, introduces search customization features including drag-and-drop column reordering and improved time range displays, and streamlines the sensor installation workflow with better Docker instructions and installation key visibility. The release also includes important security improvements for OAuth authentication and API key isolation between environments.

- **AI Sessions**: Granular permissions, pagination, SOPs enabled
- **Windows ARM64**: New sensor support for ARM-based Windows devices
- **Search**: Drag-and-drop columns, column popover, improved time display
- **Investigation Viewer**: Major overhaul with new sidebar and unified data handling
- **Sensor Installation**: Better Docker instructions, fixed modal behavior
- **Security**: Environment-specific API keys, GitHub OAuth trust, CSP fixes

---

## 2025-10-24

### Web App 5.2.1

A good batch of bug fixes.

---

## 2025-10-17

### Web App 5.2.0

**Features:**

- Show errors "in place" for Outputs, Detections, and Extensions to accelerate troubleshooting
- Support text data types in extensions (e.g. for large inputs, per community request)

**Bug fixes:** Query console, D&R rule creation flow, Console, File system.

---

## 2025-10-13

### Web App 5.1.0

Substantial update of Access Management for clarity and convenience of user management. Continued refinement of the UX for user and group management.

**Bug fixes:** Artifact list, file system, and more.

---

## 2025-09-30

### Web App 5.0.0

The Query Console is now in the new UI theme. Feature-rich search and analytic capabilities integrated with the rest of the LimaCharlie platform marks a major revision.

!!! note
    The Query Console remains in beta while we continue to improve performance and refine usability.

---

## 2025-09-12

### Web App v4.5.0

Many bug fixes and some ongoing UX improvements.

---

## 2025-08-28

### Web App 4.4.9

- Improved UX for Access Management and Adapters pages
- Add Wiz cloud sensor adapter integration
- Many fixes and smaller improvements

---

## 2025-07-18

### Web App 4.4.4

A patch release with minor bug fixes.

---

## 2025-07-10

### Web App 4.4.3

Fixed regression with sensor timeline view.

---

## 2025-06-27

### Web App 4.1.2

Bug fixes for customers and community.

---

## 2025-06-17

### Web App 4.4.0

- **AI-powered community rules (Beta)**: Easy way to turn thousands of community rules into LimaCharlie detection & response rules.
- New and improved Extensions page
- Bug fixes, including a few around auto-generated Extensions UI for extension builders

---

## 2025-05-30

### Web App 4.3.3

AI-assisted detection read-out, navigation improvements, showing org selector consistently, and a number of bug fixes.

---

## 2025-05-22

### Web App 4.3.2

Fixes for a few edge-case crashes and recently reported bugs.

---

## 2025-05-20

### Web App 4.3.1

UI support for Endpoint Protection solution, bug fixes.

---

## 2025-05-08

### Web App 4.2.8

A number of UI bug fixes.

---

## 2025-04-18

### Web App 4.2.3

Fixing the artifact download broken in some cases, and other small bug fixes.

---

## 2025-04-11

### Web App 4.2.1

- **AI co-writer for D&R**: Use "ask AI" when creating a rule and it helps you write a detection and response based on your prompt. Currently uses Google's Gemini 2 Flash model tuned for LimaCharlie D&R rules. Standard AI disclaimer applies: "trust but verify."
- **Event Tree**: Updated for usability and performance on giant trees. Enjoy collapsing and expanding groups of events, and traverse the tree with no strain on your browser.
- Other performance optimizations and bug fixes

---

## 2025-03-28

### Web App 4.1.4

UI betterment: quick filters for common platforms on the Sensor list, reliable navigation from/to Detections, other small improvements and bug fixes.

### Web App 4.1.1

Usability improvements on Detection page, ability to re-run command in sensor console, fix "copy array index," and numerous bug fixes.

---

## 2025-03-14

### Web App v4.0.2

- A long-awaited modernized UI is available (in preview). More work is on the way to further improve user experience.
- In-product dashboards available (in preview): a bird's eye view on key detections and the flow of data.

This is not just a paint job: we made substantial internal changes and will continue to improve quality.

!!! note
    On large orgs, the dashboards can take up to 15 seconds to load the very first time, and normalize after the first load. Optimizations are on the way.

    The Query Console is not available in the Modern UI yet. We will bring it there in a much better shape. In the meantime, switch back to the Old Theme to access it.

---

## 2025-02-28

### Web App v3.10.1

- Introduce Event Latency (`routing/latency`), and add latency metrics to Sensor Analytics, to help identify and troubleshoot event latency issues
- Add "Search by Description" to the org list
- Bug fixes
- **Report a Bug**: Integrated tool to report bugs easily

---

## 2025-02-21

### Web App v3.9.3

Bug fixes: handling edge-cases of org creation and adding users flows, fixing MS 365 sensor false status in certain rare conditions, other small fixes and internal instrumentation improvements.

---

## 2025-01-24

### Web App v3.8.12

**New Features:**

- **New Australia Datacenter**: Added a new datacenter in Australia to enhance performance and availability for users in the region.
- **Secrets Manager Integration**: The SMTP password field now allows integration with the secrets manager, providing a more secure way to handle authentication credentials.
- **New Extension**: ext-nims allows you to send detections from LimaCharlie to NIMS via the Notion API.

**Bug Fixes and Enhancements:**

- **Autofill OTP**: The one-time password (OTP) field now properly auto-fills from password managers.
- **User Permissions Warning**: A warning message has been implemented to notify users when revoking permissions for a user.

---

## 2025-01-09

### Web App v3.8.10

**Bug Fixes and Improvements:**

- Fixed a bug where creating a new secret in a secret manager and changing cloud adapter configuration at the same time would not update the cloud configuration with the new secret.

---

## 2024-12-12

### Web App v3.8.8

**New Features:**

- Introduced user-level saved queries for improved data management.

**Bug Fixes and Improvements:**

- Fixed the alignment of the "skip for now" text on the initial sensor onboarding screen during organization creation.
- Resolved an error related to empty extension configurations.
- Fixed a minor horizontal scroll issue on the sensors page.
- Fixed an issue where the organization creation waiting room would display "missing permission errors" when opening the app.
- Minor enhancement on the input field for adding a user to your organization, where it will now show an error if the "add user" button is clicked without an email filled in.
- Updated various mentions of "Yara" to be all caps to reflect it being an acronym.
