# Release Notes

Release notes for LimaCharlie platform components, organized by date.

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

- Fix some Linux GLIBC compatibility issues. The minimum GLIBC supported version is now 2.16 (released 2012) for all 3 supported architectures (x86, x86_64, and ARM64)
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
