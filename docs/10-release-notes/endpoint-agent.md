# Endpoint Agent Release Notes

Release notes for the EDR sensor installed on Windows, macOS, Linux and Chrome endpoints. For the latest releases of every component, see the [release notes overview](index.md).

!!! tip "Subscribe"
    Get each release as it ships with the [Endpoint Agent RSS feed](https://docs.limacharlie.io/10-release-notes/endpoint-agent.xml).

## 2026-10-29

### Endpoint Agent 5.4.2

#### New Features

- New `cert_store_list` command lists the certificates in the host's trust stores (Windows machine stores, Linux CA bundles and Java keystores, macOS keychains) with fingerprints and self-signed flags.
- New Windows `crash_dump_info` command lists the kernel crash dumps on the host and analyzes them: stop code, crash time, loaded drivers, the crashing stack and the most likely culprit drivers with their signers.

#### Bug Fixes

- `file_get` now retrieves files that report a size of zero, such as those under `/proc` and `/sys` on Linux, instead of returning them empty.
- File hashing and content searches over `/proc` no longer consume kernel log or trace streams.
- Windows: after an upgrade, the sensor service binary was readable only by SYSTEM and Administrators, so it appeared unsigned to standard users; it now keeps its normal permissions, and already-affected hosts are repaired on their next upgrade.
- Windows: fixed a crash loop at startup on hosts low on memory, caused by an oversized kernel acquisition buffer for registry events.
- Fixed a crash on hosts low on memory when an internal list could not grow.
- Fixed a crash in YARA file scanning when memory runs low; the scan is now reported as an error and skipped.

#### Improvements

- More reliable crash reporting, including crashes in older sensor services running a newer Host Based Sensor.

---

## 2026-10-22

### Endpoint Agent 5.4.1

#### New Features

- Linux module loads are now captured from kernel mapping events instead of a once-a-second `/proc` sweep, catching short-lived processes at lower I/O cost (requires root and kernel 3.12 or later).
- Windows software inventory now includes each package's publisher, install location and uninstall command when the installer provides them.

#### Bug Fixes

- The sensor now sends the server name (SNI) on every cloud connection, so new installs enroll behind firewalls and proxies that route TLS traffic by server name.
- Application control now recognises Windows binaries signed under Microsoft's new "Windows Production PCA 2026" authority, so an enforcing allowlist that trusts the OS vendor no longer blocks them.
- Linux module load events were never reported on hosts with kernel acquisition running; they now are.
- Linux: memory regions on NVMe-backed files are no longer dropped from process memory maps, so memory scans and YARA scans now cover them.
- Linux: module paths containing spaces or belonging to deleted libraries are now reported correctly.
- Fixed a buffer overflow in process memory collection that could corrupt the sensor's memory when reading a region whose size is not a page multiple.
- macOS: process memory collection no longer unmaps memory in the target process.
- 32-bit Linux: reading process memory above 2 GB no longer fails or returns empty data.
- macOS: hardened DNS parsing in the network extension against malformed packets that could crash it or report incorrect data.
- Fixed a memory read overrun when the sensor stores the cloud's public key.
- Linux/macOS install script: now stops cleanly on an unsupported OS or architecture instead of attempting a bad download.
- Windows install script: `.\install.ps1 -Install` with a key file now works, and running with no arguments shows help.
- Windows install script: now installs the 64-bit sensor when launched from a 32-bit PowerShell, as RMM tools often do.
- Windows install script: no longer clears a `$License` or `$Version` variable already set in the calling PowerShell session.

#### Improvements

- Updated the sensor's embedded TLS, certificate-validation and archive libraries to pick up upstream security fixes, including a TLS downgrade issue, distrusted certificate authorities and unsafe archive extraction.
- The system tray's installation state is now reported in `get_debug_data` and in the sensor's regular status sync.

### Endpoint Agent 5.3.13

#### Bug Fixes

- The sensor now sends the server name (SNI) on every cloud connection, so new installs enroll behind firewalls and proxies that route TLS traffic by server name.

#### Improvements

- Updated the sensor's embedded TLS, certificate-validation and archive libraries to pick up upstream security fixes, including a TLS downgrade issue, distrusted certificate authorities and unsafe archive extraction.

---

## 2026-10-13

### Endpoint Agent 5.4.0

#### New Features

- Application allowlisting: the sensor can now enforce an application control policy on Windows and macOS, blocking executions the policy does not allow, with a permissive mode that reports would-be blocks without enforcing.
- Application control reports each blocked or would-be-blocked execution as an event carrying what is needed to approve it: file hash, signer details, matched rule, parent process, user and application metadata.
- Application control: repeated blocks of the same execution within 5 minutes are folded into a single summary event with a count and first/last timestamps.
- Application control: trusted installers — naming an updater in the policy lets the software it installs run, so self-updating applications keep working under an allowlist.
- Application control: when a policy is first applied, already-running processes it would deny are reported, or terminated if the policy asks for it while enforcing.
- Application control: users are now notified with a desktop toast when one of their executions is blocked, with an optional system tray icon that keeps a history of blocks.
- New `force_sync` command sends the sensor's sync immediately, so configuration changes reach a host right away instead of at the next interval (up to five minutes later).

#### Bug Fixes

- Fixed a Windows sensor crash loop at startup on hosts low on memory, caused by an oversized allocation when processing kernel process snapshots.
- The sensor now honours backoff requests from the cloud; previously they could be silently ignored.
- Windows autoruns entries now report their strings with the correct encoding, so they are properly identified and displayed.
- macOS launchd services now report their correct process ID instead of 0.
- Fixed lost block reports on macOS when many blocks occurred in quick succession.

---

## 2026-10-06

### Endpoint Agent: Changes from 4.33.25 to 5.3.12

A roll-up of everything that changed in the Endpoint Agent between 4.33.25 and 5.3.12, for fleets upgrading from the 4.33 line in one step. Each release in between has its own entry further down this page.

#### New Features

- New [response commands](../8-reference/endpoint-commands.md): `reg_get`, `usb_list_devices`, `dir_find`, `file_grep`, `container_list`, `repo_list`, `restart_core` and `repair_core_config`.
- `reg_list` can recurse into sub-keys; `os_drivers` now works on Linux; artifact retrieval can collect several files in one task.
- Installed-package listing now covers Linux and macOS packages and Windows hotfixes; autoruns now expand wildcard paths.
- The sensor service can be upgraded or uninstalled through cloud tasking, and upgrades can be pinned to a version.
- Shell commands can run as a specific user.
- TLS 1.3 for the cloud connection, with automatic fallback to TLS 1.2.
- USB Data Loss Prevention, managed from the cloud.
- YARA scanning built in, with match addresses for memory detections and the `macho` module.
- Windows script visibility through the Antimalware Scan Interface (AMSI), reported already deobfuscated.
- Linux process events identify their container and Kubernetes pod.
- Cloud VMs on AWS, Azure and Google Cloud report their native instance identity; GKE nodes report their cluster.
- Linux detection of setuid privilege changes and of AF_ALG, RxRPC and NETLINK socket creation.
- Linux DNS events report the process that sent the query or received the response (kernel 5.15+).
- Local applications can send events to the sensor through a Unix socket API.
- macOS installation is now one guided window instead of seven separate prompts.
- RPM packages for Linux.
- The Windows service now installs under `C:\Program Files\limacharlie\`; existing installs are migrated on upgrade.
- Full crash reports (stack trace, modules, fault detail) on Windows, macOS and Linux.

#### Bug Fixes

- Fixed a large set of sensor crashes, including the sensor terminating itself on transient OS resource failures, crashes at shutdown on CentOS/RHEL 7, and a race in the random number generator.
- Linux and macOS now shut down cleanly when stopped, so service stops, restarts and reboots no longer show up as crashes.
- Cloud-driven upgrades and uninstalls now complete reliably on Linux and macOS.
- Linux kernel acquisition now loads on kernel 5.4, on RHEL/Oracle Linux 9, and on hosts without cgroup2, and recovers after the service is force-killed.
- Fixed process events being linked to the wrong parent on hosts that reuse process IDs quickly.
- Windows: fixed multi-second delays opening files on network shares.
- Windows kernel acquisition: fixed network events being lost in bursts and events arriving out of order.
- Fixed connections staying on a dead link for hours after a network disruption, and hangs behind unresponsive proxies.
- Payload downloads and artifact uploads now work through enterprise TLS inspection, filtering proxies and redirects, and large uploads resume after interruptions.
- Fixed macOS file-creation events reporting the parent directory instead of the file.
- The sensor's log file is no longer world-readable or world-writable.
- Events dropped by a full outbound queue are now counted and reported instead of being discarded silently.
- Hardened DNS collection against malformed packets.

#### Improvements

- Windows: significantly lower CPU and memory usage, from caching file hashes and code-signature checks and reusing buffers on busy code paths.
- Smaller downloads: the Linux and macOS binaries are 30–45% smaller, and cloud-delivered modules are cached on disk across restarts.
- The Linux sensor now requires glibc 2.12 instead of 2.17.
- Transfer and command failures now report readable error descriptions instead of bare codes.
- Sensor diagnostics now report kernel telemetry health, event loss and service version.
- Windows Event Log collection resumes where it left off after a restart.
- Updated embedded libraries, including TLS (mbedtls 4.1.1).

---

## 2026-09-30

### Endpoint Agent 5.3.12

#### New Features

- Cloud virtual machines on AWS, Azure and Google Cloud now report their native cloud instance identity when the sensor connects, so a host can be matched to its cloud inventory.
- Sensors on Google Kubernetes Engine nodes now also report the cluster they run in, so a sensor can be tied to its Kubernetes node.
- Sensors running inside a Kubernetes pod can report the pod and container they belong to.

#### Bug Fixes

- Fixed a Windows sensor crash when a cloud message arrived while the Host Based Sensor was still starting, most often seen during an organization-wide version upgrade.
- Linux kernel acquisition: hosts where it cannot load no longer reload the component every 20 minutes, which after several days crashed the sensor on older distributions such as CentOS 7.
- Fixed a sensor crash when caching a document larger than the cache's size limit.
- Fixed a crash when logging some event field types on Linux and macOS.
- Network requests (uploads, downloads, cloud lookups) now honor their timeout even when the remote end sends data very slowly, so they can no longer hang indefinitely.
- macOS: kernel acquisition now starts on a fresh install even when nobody is logged in, instead of staying off until a user logs in.
- macOS: if Full Disk Access is still needed after an install at the login window, the prompt now appears once a user logs in.
- macOS: the system extension no longer grows its memory use with every network flow seen.
- macOS: fixed a resource leak each time the sensor read another process's memory.
- macOS: fixed a reference-counting bug when matching disks to USB devices.
- Fixed gradual memory growth in file type tracking on long-running macOS and Linux hosts.

---

## 2026-09-21

### Endpoint Agent 5.3.11

#### Bug Fixes

- On Red Hat Enterprise Linux 9 and Oracle Linux 9 hosts running the stock Red Hat kernel, fixed kernel acquisition failing to start at all, leaving the host with no process, file, socket, network or DNS telemetry from the kernel.
- Fixed the sensor diagnostic report returning an empty agent log section on healthy hosts, because it looked for the log in the location used before the sensor moved to its data directory. The report now also lists every location it searched when no log is found.

#### Improvements

- Linux kernel acquisition no longer floods the sensor log. Its DNS attribution status line was written on nearly every poll and accounted for the large majority of everything the sensor logged on a busy host; it is now reported when the status actually changes, and at most every five minutes otherwise.
- When the sensor cannot keep up with kernel events and discards some, it now reports how many were lost in a single periodic summary instead of one log line per discarded record — more information, at a fraction of the log volume, and quietest exactly when the host is under load.

---

## 2026-09-16

### Endpoint Agent 5.3.10

#### New Features

- New `restart_core` command restarts the sensor on demand on Linux and macOS. The sensor shuts down exactly as it would for an administrative stop and its service manager starts it again; the command is refused on hosts where nothing would bring the sensor back.
- New `repair_core_config` command checks an installed sensor's service configuration against what the installer should have written and repairs any drift, with a dry-run mode that reports without changing anything. It currently covers the Windows service recovery setting that lets the service manager restart a sensor that failed to start.

#### Bug Fixes

- Fixed the sensor deliberately terminating itself when the operating system refused a thread or another resource, rather than reporting the failure and carrying on. This accounted for a significant share of sensor crashes in the field.
- On Windows, fixed the sensor terminating itself while reading the environment of a process whose environment block had grown large.
- On Windows, fixed a crash when a USB key listing was requested on a host with removable USB storage attached.
- On Linux, fixed the sensor permanently losing kernel acquisition after the service was force-killed. A process the sensor had started could keep the acquisition listener's address held across every later restart, leaving the sensor connected and reporting healthy while collecting no kernel telemetry.
- The CPU usage the sensor reports now reflects its load across the reporting interval. A momentary burst was previously reported as sustained load, and a reading the sensor could not measure was reported as 255%.
- On Windows, fixed event log collection writing its bookmarks into the sensor's upgrade log instead of its own file. Bookmarks are re-established once on upgrade to this release.
- On Linux, kernel acquisition load failures now report why the load actually failed instead of an unrelated error code.

#### Improvements

- Cloud-delivered modules are now kept on disk and reused across restarts, so the sensor no longer re-downloads several megabytes every time a host boots. The cloud still decides what the sensor loads, and every module is verified before it runs exactly as it was when delivered over the network.
- The macOS sensor download is substantially smaller — roughly 38% for the service binary and 35% for the Host Based Sensor module — and the Linux kernel acquisition module is smaller again on top of the previous release's reduction.
- Linux `.deb` and `.rpm` packages now register the service through the sensor itself, so an upgrade restores the service definition when it has gone missing. Previously only Debian-family systemd hosts recovered from that, and RPM hosts never did.

---

## 2026-09-08

### Endpoint Agent 5.3.9

#### New Features

- New `dir_find` command walks a directory tree and reports file metadata and hashes, with include and exclude patterns, size and age filters, and caps on how many files and bytes a single run may touch.
- New `file_grep` command searches file contents for literal patterns, with optional case-insensitivity, a per-file match limit, surrounding context bytes, and an option to include binary files.
- New `container_list` command inventories containers and images on a Linux host — runtime, image reference and digest, creation time, state and main process id — covering Docker and Podman, with containers under containerd and CRI-O identified from their process cgroups.
- Artifact retrieval can now collect several files in one task: files are selected by pattern under a root directory, each paired with a caller-supplied payload id, and bounded by limits on file count and total bytes.
- New `repo_list` command reports the git checkouts on a host along with their identity — worktree path, remotes and their URLs, the current branch and the commit it resolves to, whether HEAD is detached, the last fetch time, and optionally the declared submodules — so a repository can be tied to the hosts that have it cloned without a follow-up file read per candidate.

#### Bug Fixes

- On Linux, fixed an upgrade leaving the sensor stopped. Stopping the service also terminated the upgrade process running inside it, so the new binary was installed but never started, and no restart policy brought it back.
- On Linux, fixed a cloud-driven uninstall being terminated by the service stop it had just issued, which left the service definition, the sensor's data directory and the staged uninstaller behind.
- On Linux and macOS, the sensor now shuts down cleanly when stopped. Termination signals were not handled, so every service stop, restart, reboot and upgrade was reported to the cloud as a crash — nearly the entire crash volume from those platforms. A stop now waits for the sensor's own teardown (measured at about 4 seconds with all modules loaded) rather than being immediate.
- On Windows, fixed the sensor terminating itself when Windows briefly refused to return a process listing, which happens transiently while the process list is changing under it.
- On CentOS and RHEL 7 (and other hosts with glibc 2.17), fixed a crash during a clean shutdown.
- Fixed crash reports being lost on hosts that could not reach the cloud on their first connection attempt, real crashes then being reported as clean exits, and the sensor occasionally reporting a crash context it had manufactured itself.
- The sensor's log file is now created readable only by its owner. It was world-readable, and it can contain DNS queries, file paths and command lines. A host that has already been logging keeps its existing file's permissions until that file is removed.
- Hardened DNS collection against two out-of-bounds reads reachable from a crafted DNS packet the host merely observes: a datagram too short to hold a DNS header, and a compression pointer in the final byte of a packet.

#### Improvements

- macOS and Linux crashes now produce a full crash report — stack trace, loaded modules and fault detail — where previously they left only a marker saying the last run had not exited cleanly. Debug information is published per release, so a report from either platform can be resolved to source without a follow-up on the affected host.
- 32-bit Windows crash reports now carry a complete stack trace instead of the two or three frames the optimized build allowed.
- The Linux sensor download is substantially smaller — roughly 45% for the service binary and 30% for the Host Based Sensor module — because debug information is now published separately instead of being shipped to endpoints. Every upgrade transfers less.
- The sample macOS MDM profile now marks the sensor's background service and system extension as managed, so they can no longer be switched off or removed by a user from System Settings.
- Releases now include the Varist file scanning engine, so it can be turned on by configuration instead of requiring a custom build.

---

## 2026-08-31

### Endpoint Agent 5.3.8

#### New Features

- New `usb_list_devices` command lists every USB device on the host — device class, manufacturer, product and serial number, and the interfaces each device exposes — so a composite device such as a flash drive that also presents a keyboard is reported as both.

#### Bug Fixes

- On Windows, fixed a severe delay opening files on network shares. The sensor asked Windows for a fully resolved path on every file open, which a network redirector can only answer with one round trip per path component — measured at 6.4 seconds to open a single document over SMB. Network volumes now use the path the application opened with; local volumes are unchanged.
- On Windows, fixed a possible system crash when non-cached asynchronous file I/O reached the file filter.
- Fixed process events being attributed to the wrong parent on hosts that create processes rapidly. A process ID reused within roughly 70 seconds of its previous owner's exit could be linked to that dead process, which also prevented the real parent from ever being found.
- On Windows kernel acquisition, fixed process and registry events being returned out of chronological order once their internal buffer filled.
- On Windows kernel acquisition, fixed network connection and termination events being discarded a whole buffer at a time — nearly every event in a burst — instead of only the oldest, and with no record of the loss.
- On Windows, the crash minidump is no longer written into `C:\Windows\System32`, where it accumulated and was never removed; it now goes to the sensor's data directory and is removed on uninstall.
- Module images staged by a run that ended uncleanly are now cleaned up at startup instead of accumulating in the sensor's data directory.
- Hardened process enumeration and termination tracking against memory-allocation failure and a malformed process list, either of which could leak memory or crash the sensor.
- On Windows, fixed payload downloads and artifact uploads failing on hosts whose certificate store does not hold the server's root certificate; the sensor's embedded certificate chain was only consulted when Windows reported a partially trusted chain, not an untrusted root.
- On Windows 7, fixed a crash while validating a server certificate for payload downloads and artifact uploads.

#### Improvements

- Windows crash reports now carry the full fault detail — exception code, faulting address, the memory address accessed and whether it was read or written, registers, and a stack trace resolvable per module — instead of only an approximate location, so a crash can be diagnosed without a follow-up on the affected host.
- Sensor modules delivered to a host now appear under a name that identifies the module rather than a generic temporary file name.
- Updated embedded third-party libraries for HTTP, TLS certificate verification and archive handling.

---

## 2026-08-24

### Endpoint Agent 5.3.7

#### New Features

- On Linux, DNS events now report the process that sent the query or received the response, where the kernel supports it (verified on 5.15 and newer); older kernels keep delivering DNS events without a process ID. DNS events on Windows and macOS are unchanged.
- On Linux, kernel telemetry — file, process, socket, network and DNS — now loads on kernel 5.4, where it previously failed to load entirely. Network isolation still requires a newer kernel.

#### Bug Fixes

- On Linux, fixed all network connection telemetry being lost on kernels that cannot support network isolation; connection tracking now loads independently of isolation.
- On Linux, fixed the DNS tracker staying on packet capture for the life of the sensor when it started before kernel acquisition was ready, leaving DNS events without a process ID on hosts where the kernel could provide one.
- On Linux, fixed the process tracker staying on its netlink fallback under the same conditions, which could leave short-lived processes without a path or command line.
- On Linux, hardened kernel DNS collection against packets whose declared payload length exceeds what they carry; such packets could corrupt the sensor's buffer and caused the DNS events behind them to be discarded.
- On Linux, fixed sensor diagnostics reporting every kernel telemetry subprogram as inactive when the reporting component had simply not yet queried the kernel; the status is now omitted until it is known.
- Fixed a possible deadlock when the sensor is stopped by a signal on Linux and macOS.

#### Improvements

- On Linux, sensor diagnostics now report whether DNS events are being attributed to a process.

---

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

---

## 2025-10-24

### Endpoint Agent

#### Stable: 4.33.10.5

- Fix an issue with the `epp_list_exclusions` command not showing all exclusions

#### Latest: 4.33.19

- Fix an issue with the `epp_list_exclusions` command not showing all exclusions
- Change the compression algorithm for Debian installer packages from xz to gzip for better compatibility with older distributions

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

---

## 2025-09-12

### Endpoint Agent v4.33.15

- macOS system extension: fixes for potential install and upgrade issues, improved logging for troubleshooting
- Fixes a macOS install issue when using the package installer (.pkg)

---

## 2025-08-28

### Endpoint Agent 4.33.14

- Reduce CPU usage of the OS tracker. The component is used for: new system service notifications, new driver notifications, and new autoruns/bootstrap notifications.

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

---

## 2025-06-27

### Endpoint Agent 4.33.9

Important fixes for Windows 7 and Windows 8 support.

---

## 2025-05-30

### Endpoint Agent 4.33.8

- Fix a potential deadlock on upgrade in the HBS component
- Fix a reverse logic issue processing the `LC_DISABLE_REVERSE_DNS_HOSTNAME` environment variable. Accepted values: `1`, `true`, `0`, `false` (case insensitive)

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

---

## 2025-04-18

### Endpoint Agent 4.33.6

- Allow the sensor to drop the VDI file (delayed start) during the installation procedure via `-t`
- Added a sensor troubleshooting utility: a standalone command and a command line option for the sensor (`-H`) to help diagnose common misconfigurations and connectivity problems

---

## 2025-04-11

### Endpoint Agent 4.33.5

- Performance improvements for macOS
- Infrastructure work to support Endpoint Protection Platforms (EPP), and added support for Microsoft Windows Defender

!!! note "Note of Change"
    LC Detection Events are now immutable. One can no longer remove past events or modify them in any way, as detection events are a factual historic record and it's prudent to keep them as such.

---

## 2025-03-28

### Endpoint Agent v4.33.4

- Fix missing pipe event for Windows
- Fix the kernel acquisition module for Linux ARM64 builds

---

## 2025-03-06

### EDR Agent v4.33.2

Fixed a path expansion issue that would cause the cleanup command on Windows to leave configuration files after the uninstallation procedure.

---

## 2025-02-21

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

## 2024-10-19

### EDR Sensor v4.31.1

Network connection stability enhancements on all platforms.

The enhancements are in both the cloud-triggered upgrade version of the sensor AND in the on-disk installation, but there is no requirement to deploy both simultaneously.
