# Release Notes

## 2025-10-13

Web App 5.1.0

* Substantial update of Access Management for clarity and convenience of user management. We continue refine the UX of user and group management.
* Bug fixes: artifact list, file system, and more.

## 2025-09-30

Web App 5.0.0

* The Query Console is now in in the New UI Theme. Feature reach search and analytic capabilities integrated with the rest of LimaCharlie platform marks a major revision. See the [updated docs](https://docs.limacharlie.io/docs/query-console-ui) for details.

> Note: the Query console remains in beta while we continue to improve performance and refine usability.

## 2025-09-12

Endpoint Agent v4.33.15

* macOS system extension - fixes for potential install and upgrade issues, improved logging for troubleshooting
* Fixes a macOS install issue when using the package installer (`.pkg`)

Web App v 4.5.0

* Many bug fixes and some ongoing UX improvements.

## 2025-08-28

Endpoint Agent 4.33.14:

* includes "reduce CPU usage of the OS tracker". The component is used for: new system service notifications, new driver notification & new autoruns / bootstrap notifications.

Web App 4.4.9:

* Improved UX for Access Management and Adapters pages
* Add Wiz cloud sensor adapter integration
* Many fixes and smaller improvements

Other notable updates:

* Re-introduction of org templates during the org creation. We currently offer EDR Quick Start and Basic Browser Monitoring to get the new org configured on creation. You can always add configurations as code using our [IaC Generator](https://iac.limacharlie.io/).
* Parsing unstructured logs on ingestion made easier. With `parsing_grok` one can use OpenSearch Grok processor syntax, and tap to powerful ready-to-use [Grok patterns](https://github.com/opensearch-project/OpenSearch/blob/main/libs/grok/src/main/resources/patterns/grok-patterns) and vast knowledge of grokking the data with Elastic. [Docs updated](https://docs.limacharlie.io/docs/logcollectionguide?highlight=parsing_grok) with examples.

## 2025-08-08

Endpoint Agent 4.33.13 and 4.33.10.3

* Fix a Windows 2016 compatibility issue in the kernel driver for both `lc:stable` (4.33.10.3) and `lc:latest` (4.33.13) versions.

## 2025-07-18

Endpoint Agent 4.33.11

* Bug Fixes
  + Resolved event loss on high-traffic Windows systems
  + Fixed kernel upgrade failures that could occur during system updates
  + Addressed code signing compatibility issues on macOS
* Breaking Changes
  + Console logging is now opt-in via `-v` or `--verbose` flags **Note:** The previous `-v` flag for displaying installer version has been changed to `-V`. This improves default output cleanliness while maintaining debugging capabilities
* New `stable` version is now `4.33.10`

Web App 4.4.4

* A patch release with minor bug fixes

## 2025-07-10

Web App 4.4.3: fixed regression with sensor timeline view.

lc adapters v1.30.11: integration with Cylance, Proofpoint Tap, and Wiz. Big and special thanks for the community contributors <https://github.com/shortstack> and [RagingRedRiot](https://github.com/RagingRedRiot).

* *Note: these adapters are supported in the downloadable Adapter, but not yet rolled out to the webapp as "cloud adapter"*

## 2025-06-27

Endpoint Agent 4.33.9 - important fixes for Windows 7 and Windows 8 support

Web App 4.1.2 - bug fixes for customers and community

Also, last week we introduced two new rule sets from our community partners to LimaCharlie Add Ons collection:

* [SoteriaSec](https://soteriasec.io/) Commercial Ruleset: Google Workspace Rules
* [BLOKWORX](https://blokworx.com/) Detection & Response rules set covering detection of a collection of remote access services usage

## 2025-06-17

Web App 4.4.0

* AI powered community rules in "Beta". Easy way to turn thousands of community rules to LimaCharlie detection & response. [See the docs](https://docs.limacharlie.io/docs/community-rules)
* New and improve Extensions page
* Bug fixes, including a few around auto-generated Extensions UI for extension builders

## 2025-05-30

Endpoint Agent 4.33.8 (now `latest`)

* Fix a potential deadlock on upgrade in the HBS component
* Fix a reverse logic issue processing the `LC_DISABLE_REVERSE_DNS_HOSTNAME` environment variables - the possible / accepted values are `1`, `true`, `0`, `false` (case insensitive)

Web App 4.3.3

* AI assisted detection read-out; navigation improvements, showing org selector consistently, and a number of bug fixes.

## 2025-05-22

Endpoint Agent 4.33.7 (now `latest`)

* Linux
  + Fix some Linux GLIBC compatibility issues. The minimum GLIBC supported version is now 2.16 (released 2012) for all 3 supported architectures (x86, x86_64 and arm64)
  + Fix the Linux alpine / musl libc binaries
* macOS:
  + standalone installer is now a universal binary (FAT) to prevent users from installing on the wrong architecture
  + Fix an issue where the host isolation command wouldn't terminate existing connections
* Windows:
  + Added an environment variable (`LC_LOCAL_CACHE_ONLY_REVOCATION_CHECK`) to prevent the Windows' WinTrust code signing library from it's revocation cache from the internet. The default and *recommended* setting is to let WinTrust update its cache but the sensor may connect to content delivery networks (CDNs) on port 80 to do so
* General
  + The sensor troubleshooting tool (`rphcp -H`) was missing in the .deb, .msi or .pkg installers

Web App 4.3.2

* Fixes few edge-case crashes and recently reported bugs

## 2025-05-20

Releasing LimaCharlie Endpoint Protection integrates with third-party EDR solutions to provide a better view of security operations and extend agent's capabilities. This functionality comprises the EPP Extension, Web App, and a previously released Endpoint Agent v4.33.6. For detailed documentation, see [Endpoint Protection](/v2/docs/ext-epp)

**Web App 4.3.1:** UI support for Endpont Protection solution, bug fixes

**Extensions:** `Endpoint Protection` extension, a component of the EPP solution that codifies key configurations for Microsoft Defender.

## 2025-05-08

LC adapter v1.30.1

* Adding Sublime adapter - Audit logs from Sublime can be ingested cloud-to-cloud via the API, see [Docs](https://docs.limacharlie.io/docs/adapter-types-sublime-security) for details.

Web App 4.2.8

* A number of UI bug fixes.

## 2025-04-18

Endpoint agent 4.33.6

* Allow the sensor to drop the VDI file (delayed start) during the installation procedure via `-t`
* Added a sensor troubleshooting utility - a standalone command and a command line option for the sensor (`-H`) to help diagnose common misconfigurations and connectivity problems.

WebApp 4.2.3

* Fixing the artifact download broken in some cases, and other small bug fixes.

## 2025-04-11

Web App 4.2.1

* AI co-writer for D&R: use "ask AI" when creating the rule and it helps you write a detection and response based on your prompt.
  + We currently use Google's `gemini-2-flash` [model](https://deepmind.google/technologies/gemini/flash/) that we tuned to do a good job building Detections and Responses in LimaCharlie, while the standard AI disclaimer applies: "trust but verify".
* Event Tree updated for usability and performance on giant trees: enjoy collapsing and expanding groups of events, and traverse the tree with no strain on your browser.
* Other performance optimizations and bug fixes

Endpoint Agent 4.33.5

* Performance improvements for macOS
* Infrastructure work to support Endpoint Protection Platforms (EPP), and added support for Microsoft Windows Defender

> Note of change
>
> LC Detection Events are now immutable. One can no longer remove the past events, or modify them in any way, as the detection events are factual historic record, and it's prudent to keep them as such.

## 2025-03-28

* Web app 4.1.4
  + UI betterment: quick filters for common platforms on Sensor list, reliable navigation from/to Detections, other small improvements and bug fixes.
* [Adapter for SentinelOne](https://docs.limacharlie.io/docs/sentinelone): connects to SentinelOne MGMT API and send to LC alerts, threats, and other events of interest.

## 2025-03-28

* Endpoint agent v4.33.4
  + Fix missing pipe event for Windows
  + Fix the kernel acquisition module for Linux arm64 builds
* Extensions and adapters:
  + Git-Sync - take the best from LimaCharlie Infra as Code by connecting with Git and syncing the desired sections of your configurations in easy to use UI. [Documentation](https://refractionpoint.slack.com/archives/C058QHECQC8/p1743177137477489)
  + ext-renigma v1.0.0 - initial release of integration with [REnigma](https://dtrsec.com/) - an advanced malware analysis platform leveraging its unique Record and Replay technology - read more in the [Docs](https://docs.limacharlie.io/docs/ext-renigma).
  + MIMECAST adapter - connect to the Mimecast API to stream audit events as they happen Read more in the [Docs](https://docs.limacharlie.io/docs/adapter-types-mimecast).
* Web app 4.1.1
  + Usability improvements on Detection page, ability to re-run command in sensor/console, fix "copy array index", and numerous bug fixes.

## 2025-03-14

Web App `v4.0.2`

* A long-awaited modernized UI is available (in preview). More work in on the way to further improve user experience.
* In-product dashboards available (in preview) - a bird's eye view on key detections and the flow of data.

This is not just a paint job: we made substantial internal changes and will continue to improve quality. Learn more on what has changed in our blog: [**Announcing Our UI Update and In-product Dashboards**](https://limacharlie.io/blog/announcing-improved-ui-experience-and-in-product-dashboard)**.**

> Notes
>
> * On large orgs, the dashboards can take up to 15 sec to load the very first time, and normalize after the first load. Optimizations on the way.
> * The Query Console is not available in the Modern UI yet. We will bring it there, in a much better shape. Meantime you'll have to switch back to the Old Theme to access to it.

Add-Ons & Adapters:

* New: [PandaDoc adapter](/v2/docs/adapter-types-pandadoc) to connect and fetch PandaDoc API logs
* New: [CrowdStrike Falcon Cloud adapter](/v2/docs/adapter-types-crowdstrike-falcon-cloud) - allows you to connect to CrowdStrike Falcon Cloud to stream events as they happen in the CrowdStrike Falcon Console.
* Update: Cloud-CLI v1.4.8 Extension - We have improved observability in the CLI extensions such as `ext-cloud-cli` which allows us to support users better. Additionally, we have improved error handling and reporting around long running CLI commands which may have got stuck or timed out.

## 2025-03-06

EDR Agent: `v4.33.2`

* Fixed a path expansion issues that would cause the cleanup command on Windows to leave configuration files after the uninstallation procedure.

Adapter: `v1.27.2`

* Added support for ZenDesk, read more in our docs: <https://docs.limacharlie.io/docs/adapter-types-zendesk>

## 2025-02-28

Introducing LimaCharlie Labs, where we share with you brave experiments and early prototypes of features and extensions that may or may not become production, based on your input and feedback. Check the `LABS` badge on the Web App.

* Playbook Extension is now available in the Labs - see [documentation here](/v2/docs/playbook)

Web App `v3.10.1`

* Introduce Event Latency (`routing/latency`), and add latency metrics to the Sensor Analytics, to help identify and troubleshoot any event latency issues.
* Add "Search by Description" to the org list.
* Bug fixes.
* "Report a Bug": integrated tool to report bugs easily so that we do more bug fixes for y'all.

## 2025-02-21

Web App `v3.9.3`

* Bug fixes: handling edge-cases of org creation and adding users flows, fixing MS 365 sensor false status in certain rare conditions, other small fixes and internal instrumentation improvements.

CLI `4.9.12`

* Add users, simplified. Wrapping the [new API](https://api.limacharlie.io/static/swagger/#/Users/addOrgUser), a new command `limacharlie users invite` makes it easy to add a user, or a batch of users, to the org - without requesting them to create LimaCharlie account. See [Invite users section in LimaCharlie SDK](/v2/docs/limacharlie-sdk#invite-users) for usage.

EDR Endpoint Agent `v4.33.1`

* Fix various directory and file permissions on macOS
* Added a status file to help troubleshooting
  + The status file contains the sensor id, organization id, version and the agent's service uptime
  + File locations are platform specific:
    - Linux: `/opt/limacharlie/hcp_hbs_status.json`
    - macOS: `/Library/Application Support/limacharlie/hcp_hbs_status.json`
    - Windows: `c:\\programdata\\limacharlie\\hcp_hbs_status.json`
* Fix a missing package name for `Microsoft Edge Update` on Windows
* Fix a pattern matching issues that what affecting file integrity notifications
* Added the `LC_DISABLE_REVERSE_DNS_HOSTNAME` environment variable support for customers wanting to use the local hostname instead of resolving it

## 2025-01-24

Web App `v3.8.12`

* New Features:
  + New Australia Datacenter: We have added a new datacenter in Australia to enhance the performance and availability of our services for users in the region.
  + Secrets Manager Integration: The SMTP password field now allows for integration with our secrets manager, providing a more secure way to handle authentication credentials.
  + New Extension: `ext-nims` allows you to send detections from LimaCharlie to NIMS via the Notion API. Read more [here](https://docs.limacharlie.io/docs/ext-nims).
* Bug Fixes & Enhancements:
  + Autofill OTP: The one-time password (OTP) field now properly auto-fills from password managers.
  + User Permissions Warning: A warning message has been implemented to notify users when revoking permissions to a user.

## 2025-01-09

Web App `v3.8.10`

* Bug Fixes and Improvements
  + Fixed a bug where creating a new secret in a secret manager and changing cloud adapter configuration at the same time would not update the cloud configuration with the new secret. This fix prevents the bug by stopping a certain event from being propagated.

ext-usage-alerts `v1.0.0`

* Newly released extension which allows you to create, maintain, & automatically refresh usage alert conditions for an Organization. Read more [here](https://docs.limacharlie.io/docs/ext-usage-alerts).

## 2024-12-12

Web App `v3.8.8`

* New features
  + Introduced user-level saved queries for improved data management.
* Bug Fixes and Improvements
  + Fixed the alignment of the 'skip for now' text on the initial sensor onboarding screen during organization creation.
  + Resolved an error related to empty extension configurations, enhancing user experience.
  + Fixed a minor scroll issue on the sensors page where there was a slight horizontal scroll possible on the page.
  + Implemented a fix for an issue where the organization creation waiting room would display "missing permission errors" when opening the app.
  + Minor enhancement on the input field for adding a user to your organization, where it will now show an error if the 'add user' button is clicked without a user's email filled in.
  + Updating various mentions of "Yara" to be all caps to reflect it being an acronym

## 2024-10-28

New MITRE Report API In this release, we've added a new REST API and CLI for producing a MITRE report for a given Organization based on the D&R rules in place (using their tags like `attack..t1000.xxx`).

* API: <https://api.limacharlie.io/static/swagger/#/Rules/getOrgMITREReport>
* CLI: `limacharlie mitre-report`

The resulting JSON report can be used with the attack-navigator: <https://mitre-attack.github.io/attack-navigator/>. This capability makes it easier to track security coverage against MITRE ATT&CK framework.

## 2024-10-19

EDR Sensor `v4.31.1`

* Network connection stability enhancements on all platforms.
* The enhancements are both in the cloud-triggered upgrade version of the sensor AND in the on-disk installation, but there is no requirement to deploy both simultaneously.

## 2024-10-17

New sort and bulk actions functionality for tables

In this release, we are adding the ability to sort columns in the LimaCharlie web app. In addition, tables now support bulk actions (Enable/Disable and Delete). This applies to the following sections of the web app: Adapters, Yara Rules, Secrets, Lookups, False Positive Rules and Detection and Response Rules.

## Prior Release Notes

All prior date release notes are located here: <https://limacharlie.io/release-notes>