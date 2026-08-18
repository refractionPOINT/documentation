# Release Notes

Release notes for LimaCharlie platform components, organized by date.

!!! tip "Subscribe to these release notes"
    Every entry below is also published as a feed, so a new release can reach you instead of you checking this page. Entries that change an event schema or break an existing integration are additionally published on their own feed.

    - **Everything**: [RSS](https://docs.limacharlie.io/10-release-notes/feed.xml) or [JSON Feed](https://docs.limacharlie.io/10-release-notes/feed.json)
    - **Endpoint Agent only**: [RSS](https://docs.limacharlie.io/10-release-notes/endpoint-agent.xml)
    - **Web App only**: [RSS](https://docs.limacharlie.io/10-release-notes/web-app.xml)
    - **Adapters only**: [RSS](https://docs.limacharlie.io/10-release-notes/adapters.xml)
    - **Extensions only**: [RSS](https://docs.limacharlie.io/10-release-notes/extensions.xml)
    - **CLI only**: [RSS](https://docs.limacharlie.io/10-release-notes/cli.xml)
    - **Platform announcements only**: [RSS](https://docs.limacharlie.io/10-release-notes/platform.xml)
    - **Breaking and schema changes only**: [RSS](https://docs.limacharlie.io/10-release-notes/breaking-changes.xml)

    To route a feed into Slack, run `/feed subscribe https://docs.limacharlie.io/10-release-notes/endpoint-agent.xml` in the channel that should receive it.

    For discussion and email notification of the same releases, set the [Platform Updates category](https://community.limacharlie.com/c/platform-updates/5) in the community forum to Watching. For service availability rather than releases, subscribe on the [status page](https://status.limacharlie.io/).

## 2026-08-14

### Endpoint Agent 5.3.6

#### New Features

- Linux hosts that cannot provide a cgroup2 mount — unprivileged containers, read-only root filesystems, kernels built without cgroup BPF support — now keep kernel-level file, process, socket and network telemetry instead of losing all of it.

#### Bug Fixes

- Fixed the sensor silently discarding queued events when its outbound queue filled up; discarded events are now counted and reported.
- The outbound event queue is now bounded by memory size as well as by event count, so a few very large events can no longer displace thousands of small ones.
- Fixed every kernel-sourced DNS event on Linux reporting process ID 0 and being held for 10 seconds before delivery.
- Fixed Linux network isolation being reported as available on hosts where the sensor could not exempt its own connection, where isolating the host would have cut off the connection needed to un-isolate it.
- Fixed the sensor aborting under Wine while collecting Windows Event Log events; an incomplete Event Log bookmark implementation is now detected at the point of use and log resumption is disabled cleanly.
- macOS file-access monitoring now matches file extensions case-insensitively, so a rule for `.docx` also matches `Report.DOCX`. Linux continues to match exactly.
- Removing an adhoc exfil rule now returns a receipt reporting whether the rule was found and removed, matching the behavior of adding one.

#### Improvements

- Sensor diagnostics now report how many events the outbound queue has discarded, their estimated size, and the current queue depth against its limits.
- Sensor diagnostics now report which Linux kernel telemetry subprograms are active, so a partial kernel acquisition is visible rather than appearing healthy.
- On Linux hosts without kernel DNS support, DNS collection now falls back to packet capture, and packet captures are opened only when that fallback is actually in use instead of on every Linux sensor.
- The sensor now warns when file-access monitoring is enabled with no file patterns configured, instead of appearing healthy while unable to report anything.

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

## 2026-08-11

### Endpoint Agent 5.3.5

#### New Features

- Linux process events now identify the container a process belongs to, including its Kubernetes pod; the fields are absent for ordinary host processes.
- New Windows script visibility through the Antimalware Scan Interface: scripts and .NET assemblies are reported as the host application submits them for scanning, already deobfuscated. Enabled from the cloud.
- YARA memory detections now report the address of the match, so a detection points at the exact location in the target process.
- YARA rules can now use the `macho` module to inspect Mach-O images.

#### Bug Fixes

- Fixed cloud-driven sensor upgrades never taking effect on macOS. The new binary is now put in place atomically before the service is stopped, on both macOS and Linux.
- Fixed the sensor sitting connected but idle for up to 10 minutes after its cloud connection was replaced, delaying collectors and telemetry; it now re-syncs immediately.
- Fixed the sensor hanging indefinitely when a configured proxy accepts the connection but never answers the CONNECT request; the attempt is now bounded and retried.
- Proxy replies split across packets, sent with LF-only headers, or answering with a 2xx status other than 200 are now handled correctly.
- Fixed the sensor's log file being created world-writable on installed Linux sensors.
- Uninstalling on Linux now removes the kernel acquisition mount point it used to leave behind, and macOS uninstall now deregisters its installer receipt.
- Fixed the arm64 Debian package being refused by dpkg; it is now published as `limacharlie_<version>_arm64.deb`.
- Payload downloads and artifact uploads are now strictly compliant HTTP, so filtering proxies and SSL inspection agents no longer drop them as malformed.
- Fixed artifact uploads reporting success while delivering no data when a network device answered with a redirect.
- Fixed certificate verification failures for payload downloads, artifact uploads and sensor upgrades on hosts with enterprise TLS inspection roots; verification now uses the operating system trust store alongside the built-in certificates.
- Fixed the sensor deadlocking while listing process handles when Windows stopped answering a handle name query.
- Fixed process hollowing detection rescanning every module in full instead of skipping the parts already matched on disk.
- Fixed stateful detection tracking comparing only part of its key, which could route events to the wrong tracking group.
- Fixed the sensor aborting under Wine when probing the Windows Event Log bookmark API.
- Fixed a potential out-of-bounds read when matching short YARA rule namespaces.
- Corrected swapped country and organization labels in the sensor's certificate issuer output.

#### Improvements

- Payload download and artifact upload failures now report a readable description in the command receipt and in the local log, instead of a bare numeric code.
- Transfer failures that previously all reported error 0 now report distinct codes: a sensor that has not yet received its artifact configuration, and a connection closed without a response.
- Payload downloads and artifact uploads now use a full HTTP client, adding chunked response support, correct response framing and enforced timeouts.
- The Linux x86_64 and i386 sensor now requires glibc 2.12 instead of 2.17, so it installs on older distributions; the optional eBPF module still requires 2.14.
- A configuration update is no longer held up by an in-progress payload download.
- The payload download size limit now applies to the whole transfer rather than to each resumed request.

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

### Endpoint Agent 5.3.4

#### New Features

- The registry listing command can now recursively list sub-keys down to an optional maximum depth, reporting fully-qualified key paths; oversized results are returned as partial replies flagged for follow-up.

#### Bug Fixes

- Fixed corrupted process events from macOS kernel acquisition: invalid timestamps, missing file paths and command lines, and spurious phantom process records.
- Fixed file transfers and the sensor's cloud connection aborting when a TLS 1.3 server sends a post-handshake session ticket, common behind SSL-inspection proxies.
- Fixed repeated payload put commands failing on Windows: moving a file into place now overwrites an existing destination, matching other platforms.
- Fixed payload downloads and log/artifact uploads failing when certificate verification is explicitly disabled.
- Uninstalling the Windows MSI now fully removes the sensor's identity and data, so a later reinstall enrolls as a fresh sensor.
- Fixed a rare crash caused by concurrent use of the sensor's random number generator, seen most often on macOS under heavy file activity.
- Fixed a crash on sensor shutdown after a partially failed startup.
- Fixed a potential crash when reading executable paths from the Windows registry under low-memory conditions.
- Fixed assorted small latent bugs across the sensor uncovered by expanded static analysis.

#### Improvements

- Windows Event Log collection now resumes from where it left off after a sensor restart, recovering events logged while the sensor was not running.
- Sensor upgrade and uninstall operations now write warnings and errors to a dedicated log file in the sensor data directory.
- Listing endpoint protection exclusions now reports an error code on failure, distinguishing a failed query from a host with no exclusions.
- Windows WMI query failures now report a dedicated WMI error code instead of a generic failure, for example when Defender is disabled by policy.

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

## 2026-07-14

### Endpoint Agent 5.3.3

#### New Features

- The sensor service can now be upgraded or uninstalled through cloud tasking.
- Upgrade and uninstall commands reply with their result, including the OS error code on failure.
- Sensor upgrades can be pinned to a specific version.
- Sensor connections now report a unique per-boot identifier to the cloud.
- Sensor connections now report the main network interface's MAC address.
- Windows endpoint protection status now falls back to Security Center antivirus data when the Defender query fails.

#### Bug Fixes

- Sensors that connect but receive no data from the cloud now retry with a fresh TLS handshake after 30 seconds.
- Fixed connection failures under pinned-certificate trust: TLS hostname verification now applies only to public CA trust.
- Fixed a TLS 1.2 handshake failure with servers using certain RSA-PSS signature schemes.
- Fixed macOS notarization of the sensor binary.
- Fixed a thread-synchronization race on Linux and macOS that could destabilize the sensor.
- Fixed a small memory leak when kernel acquisition shuts down on macOS.
- Fixed incorrect formatting in several sensor debug log messages.
- Fixed assorted small bugs across the sensor on Linux and Windows.

#### Improvements

- Updated the embedded TLS library (mbedtls) to 4.1.1.

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

## 2026-07-06

### Endpoint Agent 5.3.2

#### Bug Fixes

- Fixed connection failures under pinned-certificate trust: TLS hostname verification now applies only to public CA trust.
- Fixed a TLS 1.2 handshake failure with servers using certain RSA-PSS signature schemes.

---

## 2026-07-02

### Endpoint Agent 5.3.1

#### New Features

- TLS 1.3 is now supported for the sensor's connection to the LimaCharlie cloud, with automatic fallback to TLS 1.2.
- Shell commands can now be run as a specific user instead of always running with the sensor's own privileges.
- USB Data Loss Prevention is now configuration-driven, so the enforcement mode and allowed-device list persist across restarts and can be managed centrally from the cloud.

#### Bug Fixes

- Improved the reliability of running shell commands: fixed lost error output, incorrect exit codes, and commands being cut short on hosts whose clock jumps.
- Endpoint protection status now reports specific errors when a query fails, instead of a single generic failure.
- Fixed several memory-safety issues and memory leaks across the sensor, including at shutdown and on Windows.

#### Improvements

- Linux kernel component failures are now easier to diagnose, with more detail reported in its status.

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

## 2026-06-05

### Endpoint Agent 5.3.0

#### New Features

- New `reg_get` command fetches a single named Windows registry value by key and value name, for values too large or keys too crowded to retrieve with `reg_list`.
- macOS installation is now a single guided window with a three-step checklist — system extension, network content filter, Full Disk Access — replacing the previous sequence of seven separate prompts.

#### Bug Fixes

- Fixed macOS file-creation events reporting the parent directory instead of the new file's path, which stopped exfil watch rules from matching specific files.
- Fixed a leak of registry key handles when listing Windows registry keys.

#### Improvements

- File hashing is faster and allocates far less memory, lowering sensor overhead on hosts with heavy file activity.

---

## 2026-05-30

### Endpoint Agent 5.2.6

#### Bug Fixes

- Fixed very large artifact uploads never completing: each part is now retried up to ten times with backoff, so a brief network interruption no longer restarts the transfer from the beginning.
- Fixed uploads of locked files larger than 4 GB on Windows looping indefinitely over the first 4 GB.
- The sensor now shuts down promptly while an upload is retrying, instead of waiting out its backoff.

---

## 2026-05-09

### Vulnerability Management Uplift

Major uplift to the Vulnerability Reporting extension and its surfaces.

- **Canonical asset-tag namespace**: introduces the `lc:asset:*` tag convention (criticality, exposure, environment, owner, compliance) for cross-cutting asset metadata. The Vulnerability Reporting extension is the first consumer; the namespace is intended to be reused across LimaCharlie surfaces. See [Asset Tag Namespace](../2-sensors-deployment/asset-tags.md).
- **Vulnerability Reporting extension**: new public-facing documentation covering setup, scan modes (`scheduled` / `manual` / `all`), criticality-tag overrides, KEV + EPSS enrichment, LC Risk scoring, and the full action surface. See [Vulnerability Reporting](../5-integrations/extensions/limacharlie/vulnerability-reporting.md).
- **Finding resolutions**: documented the resolution model — every finding is implicitly **open** until an operator records `mitigated`, `accepted`, or `false_positive`. Accepted-exception expiries lapse back into the open count, and `vuln_finding.*` events (`created`, `closed`, `kev_match`, `state_changed`) can be routed via Outputs to Jira, Slack, Cases, etc.

---

## 2026-04-02

### Endpoint Agent 5.1.0

#### New Features

- The `os_drivers` command now works on Linux, listing the host's loaded kernel modules.
- The sensor health check now downloads and verifies the latest health-check binary from the cloud, so diagnostics stay current without upgrading the sensor.

#### Bug Fixes

- Fixed macOS and Windows sensors staying on a dead connection for hours after a network disruption; keepalive behavior is now consistent across all platforms and connections recover promptly.
- Fixed occasional missing line breaks in the sensor's local log file.

#### Improvements

- The sensor health check now reports details of the installed sensor binary on disk.
- Sensor debug data now includes the sensor service version.
- Sensor service details are now reported to the cloud on every sync, instead of only when debug data is requested.
- Linux and macOS sensor binaries are smaller.

---

## 2026-02-08

### Endpoint Agent 4.33.26

- **Feature**: Windows ARM64 support
- Fix cloud initialization issue on start and reboots
- Fix an eBPF umount issue on Linux whenever LVM is used

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

### Endpoint Agent

#### Stable: 4.33.10.5

- Fix an issue with the `epp_list_exclusions` command not showing all exclusions

#### Latest: 4.33.19

- Fix an issue with the `epp_list_exclusions` command not showing all exclusions
- Change the compression algorithm for Debian installer packages from xz to gzip for better compatibility with older distributions

### Web App 5.2.1

A good batch of bug fixes.

---

## 2025-10-17

### Endpoint Agent

**New stable release 4.33.10.4** - fixed memory leak in file type tracker, upgrade recommended.

**New release 4.33.18:**

Number of fixes including:

- A memory leak in the file type tracker
- Potential crashes in cloud task processing and log tracker
- Version reporting fixes on Windows 11, Linux, and macOS
- Certificate updates to avoid solely relying on the platform keychain
- Update the size of the file tracking buffer to avoid missing events on Linux

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

### Endpoint Agent v4.33.15

- macOS system extension: fixes for potential install and upgrade issues, improved logging for troubleshooting
- Fixes a macOS install issue when using the package installer (.pkg)

### Web App v4.5.0

Many bug fixes and some ongoing UX improvements.

---

## 2025-08-28

### Endpoint Agent 4.33.14

- Reduce CPU usage of the OS tracker. The component is used for: new system service notifications, new driver notifications, and new autoruns/bootstrap notifications.

### Web App 4.4.9

- Improved UX for Access Management and Adapters pages
- Add Wiz cloud sensor adapter integration
- Many fixes and smaller improvements

### Other Notable Updates

- **Org Templates**: Re-introduction of org templates during org creation. Currently offering EDR Quick Start and Basic Browser Monitoring to get the new org configured on creation. You can always add configurations as code using the IaC Generator.
- **Parsing Unstructured Logs**: With `parsing_grok` you can use OpenSearch Grok processor syntax, and tap into powerful ready-to-use Grok patterns and the vast knowledge of grokking data with Elastic.

---

## 2025-08-08

### Endpoint Agent 4.33.13 and 4.33.10.3

Fix a Windows 2016 compatibility issue in the kernel driver for both `lc:stable` (4.33.10.3) and `lc:latest` (4.33.13) versions.

---

## 2025-07-18

### Endpoint Agent 4.33.11

**Bug Fixes:**

- Resolved event loss on high-traffic Windows systems
- Fixed kernel upgrade failures that could occur during system updates
- Addressed code signing compatibility issues on macOS

**Breaking Changes:**

- Console logging is now opt-in via `-v` or `--verbose` flags. The previous `-v` flag for displaying installer version has been changed to `-V`. This improves default output cleanliness while maintaining debugging capabilities.

New stable version is now **4.33.10**.

### Web App 4.4.4

A patch release with minor bug fixes.

---

## 2025-07-10

### Web App 4.4.3

Fixed regression with sensor timeline view.

### LC Adapters v1.30.11

Integration with Cylance, Proofpoint Tap, and Wiz. Big and special thanks to community contributors [shortstack](https://github.com/shortstack) and RagingRedRiot.

!!! note
    These adapters are supported in the downloadable Adapter, but not yet rolled out to the web app as "cloud adapter."

---

## 2025-06-27

### Endpoint Agent 4.33.9

Important fixes for Windows 7 and Windows 8 support.

### Web App 4.1.2

Bug fixes for customers and community.

### New Community Rule Sets

Two new rule sets from community partners added to the LimaCharlie Add-Ons collection:

- **SoteriaSec Commercial Ruleset**: Google Workspace Rules
- **BLOKWORX Detection & Response**: Rules covering detection of a collection of remote access services usage

---

## 2025-06-17

### Web App 4.4.0

- **AI-powered community rules (Beta)**: Easy way to turn thousands of community rules into LimaCharlie detection & response rules.
- New and improved Extensions page
- Bug fixes, including a few around auto-generated Extensions UI for extension builders

---

## 2025-05-30

### Endpoint Agent 4.33.8

- Fix a potential deadlock on upgrade in the HBS component
- Fix a reverse logic issue processing the `LC_DISABLE_REVERSE_DNS_HOSTNAME` environment variable. Accepted values: `1`, `true`, `0`, `false` (case insensitive)

### Web App 4.3.3

AI-assisted detection read-out, navigation improvements, showing org selector consistently, and a number of bug fixes.

---

## 2025-05-22

### Endpoint Agent 4.33.7

**Linux:**

- Fix some Linux GLIBC compatibility issues. The minimum GLIBC supported version is now 2.17 (released 2012) for all 3 supported architectures (x86, x86_64, and ARM64)
- Fix the Linux Alpine / musl libc binaries

**macOS:**

- Standalone installer is now a universal binary (FAT) to prevent users from installing on the wrong architecture
- Fix an issue where the host isolation command wouldn't terminate existing connections

**Windows:**

- Added an environment variable (`LC_LOCAL_CACHE_ONLY_REVOCATION_CHECK`) to prevent the Windows WinTrust code signing library from updating its revocation cache from the internet. The default and recommended setting is to let WinTrust update its cache, but the sensor may connect to content delivery networks (CDNs) on port 80 to do so.

**General:**

- The sensor troubleshooting tool (`rphcp -H`) was missing in the .deb, .msi, and .pkg installers

### Web App 4.3.2

Fixes for a few edge-case crashes and recently reported bugs.

---

## 2025-05-20

### LimaCharlie Endpoint Protection

Releasing LimaCharlie Endpoint Protection, which integrates with third-party EDR solutions to provide a better view of security operations and extend agent capabilities. This functionality comprises the EPP Extension, Web App, and a previously released Endpoint Agent v4.33.6.

### Web App 4.3.1

UI support for Endpoint Protection solution, bug fixes.

### Extensions

Endpoint Protection extension: a component of the EPP solution that codifies key configurations for Microsoft Defender.

---

## 2025-05-08

### LC Adapter v1.30.1

Adding Sublime adapter. Audit logs from Sublime can be ingested cloud-to-cloud via the API.

### Web App 4.2.8

A number of UI bug fixes.

---

## 2025-04-18

### Endpoint Agent 4.33.6

- Allow the sensor to drop the VDI file (delayed start) during the installation procedure via `-t`
- Added a sensor troubleshooting utility: a standalone command and a command line option for the sensor (`-H`) to help diagnose common misconfigurations and connectivity problems

### Web App 4.2.3

Fixing the artifact download broken in some cases, and other small bug fixes.

---

## 2025-04-11

### Web App 4.2.1

- **AI co-writer for D&R**: Use "ask AI" when creating a rule and it helps you write a detection and response based on your prompt. Currently uses Google's Gemini 2 Flash model tuned for LimaCharlie D&R rules. Standard AI disclaimer applies: "trust but verify."
- **Event Tree**: Updated for usability and performance on giant trees. Enjoy collapsing and expanding groups of events, and traverse the tree with no strain on your browser.
- Other performance optimizations and bug fixes

### Endpoint Agent 4.33.5

- Performance improvements for macOS
- Infrastructure work to support Endpoint Protection Platforms (EPP), and added support for Microsoft Windows Defender

!!! note "Note of Change"
    LC Detection Events are now immutable. One can no longer remove past events or modify them in any way, as detection events are a factual historic record and it's prudent to keep them as such.

---

## 2025-03-28

### Web App 4.1.4

UI betterment: quick filters for common platforms on the Sensor list, reliable navigation from/to Detections, other small improvements and bug fixes.

### Adapters

SentinelOne adapter: connects to SentinelOne MGMT API and sends alerts, threats, and other events of interest to LimaCharlie.

### Endpoint Agent v4.33.4

- Fix missing pipe event for Windows
- Fix the kernel acquisition module for Linux ARM64 builds

### Extensions and Adapters

- **Git-Sync**: Take the best from LimaCharlie Infrastructure as Code by connecting with Git and syncing the desired sections of your configurations in an easy-to-use UI. See [documentation](../5-integrations/extensions/limacharlie/git-sync.md).
- **ext-renigma v1.0.0**: Initial release of integration with REnigma, an advanced malware analysis platform leveraging its unique Record and Replay technology.
- **Mimecast adapter**: Connect to the Mimecast API to stream audit events as they happen.

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

### Add-Ons and Adapters

- **PandaDoc adapter**: Connect and fetch PandaDoc API logs.
- **CrowdStrike Falcon Cloud adapter**: Connect to CrowdStrike Falcon Cloud to stream events as they happen in the CrowdStrike Falcon Console.
- **Cloud-CLI v1.4.8 Extension**: Improved observability in CLI extensions such as ext-cloud-cli. Additionally, improved error handling and reporting around long-running CLI commands which may have gotten stuck or timed out.

---

## 2025-03-06

### EDR Agent v4.33.2

Fixed a path expansion issue that would cause the cleanup command on Windows to leave configuration files after the uninstallation procedure.

### Adapter v1.27.2

Added support for ZenDesk.

---

## 2025-02-28

### LimaCharlie Labs

Introducing LimaCharlie Labs, where we share brave experiments and early prototypes of features and extensions that may or may not become production, based on your input and feedback. Check the LABS badge on the Web App.

**Playbook Extension** is now available in Labs.

### Web App v3.10.1

- Introduce Event Latency (`routing/latency`), and add latency metrics to Sensor Analytics, to help identify and troubleshoot event latency issues
- Add "Search by Description" to the org list
- Bug fixes
- **Report a Bug**: Integrated tool to report bugs easily

---

## 2025-02-21

### Web App v3.9.3

Bug fixes: handling edge-cases of org creation and adding users flows, fixing MS 365 sensor false status in certain rare conditions, other small fixes and internal instrumentation improvements.

### CLI 4.9.12

Add users, simplified. Wrapping the new API, a new command `limacharlie users invite` makes it easy to add a user, or a batch of users, to the org without requiring them to create a LimaCharlie account.

### EDR Endpoint Agent v4.33.1

- Fix various directory and file permissions on macOS
- Added a status file to help troubleshooting. The status file contains the sensor ID, organization ID, version, and the agent's service uptime.

    **Status file locations:**

    | Platform | Path |
    |----------|------|
    | Linux | `/opt/limacharlie/hcp_hbs_status.json` |
    | macOS | `/Library/Application Support/limacharlie/hcp_hbs_status.json` |
    | Windows | `C:\ProgramData\limacharlie\hcp_hbs_status.json` |

- Fix a missing package name for Microsoft Edge Update on Windows
- Fix a pattern matching issue that was affecting file integrity notifications
- Added the `LC_DISABLE_REVERSE_DNS_HOSTNAME` environment variable for customers wanting to use the local hostname instead of resolving it

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

### ext-usage-alerts v1.0.0

Newly released extension which allows you to create, maintain, and automatically refresh usage alert conditions for an organization.

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

---

## 2024-10-28

### New MITRE Report API

Added a new REST API and CLI for producing a MITRE report for a given organization based on the D&R rules in place (using their tags like `attack..t1000.xxx`).

- **CLI**: `limacharlie mitre-report`

The resulting JSON report can be used with the [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/). This capability makes it easier to track security coverage against the MITRE ATT&CK framework.

---

## 2024-10-19

### EDR Sensor v4.31.1

Network connection stability enhancements on all platforms.

The enhancements are in both the cloud-triggered upgrade version of the sensor AND in the on-disk installation, but there is no requirement to deploy both simultaneously.

---

## 2024-10-17

### New Sort and Bulk Actions for Tables

Added the ability to sort columns in the LimaCharlie web app. In addition, tables now support bulk actions (Enable/Disable and Delete). This applies to the following sections: Adapters, YARA Rules, Secrets, Lookups, False Positive Rules, and Detection and Response Rules.
