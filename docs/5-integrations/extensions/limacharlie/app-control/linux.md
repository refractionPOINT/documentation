# Application Control on Linux

## Overview

On Linux, [Application Control](../app-control.md) uses the same policies, rules, modes and events as on Windows and macOS, managed from the same console pages and the same two Config Hive types. This page covers what is different on Linux: how the sensor enforces, what a host needs, what stands in for code signatures, the limits, and how to check a host before you roll out.

- The sensor is the enforcement point. It asks the kernel to be consulted before a program file is opened for execution and answers allow or deny. There is no kernel module and no driver.
- Linux programs carry no code signature. OS vendor trust comes from the package manager instead: a file counts as the vendor's own when a package signed by the distribution owns it and its content still matches what the package installed.
- The policy applies to program files: executables, the dynamic loader, and script files started through `#!`.

## Requirements

- Endpoint agent **5.4.4** or later, installed as the service, so that it runs as root. See [Linux installation](../../../../2-sensors-deployment/endpoint-agent/linux/installation.md).
- Kernel **5.0** or later, built with `CONFIG_FANOTIFY_ACCESS_PERMISSIONS`. Every mainstream distribution kernel released since 2019 has it. A host on an older kernel, such as the 3.10 kernel of RHEL and CentOS 7, reports why it cannot enforce and applies no policy.
- `CAP_SYS_ADMIN` in the initial user namespace. The service install has it. A sensor running in a container, or under a service unit that drops capabilities, cannot take exec permission events.
- `dpkg` (Debian, Ubuntu) or `rpm` (Red Hat Enterprise Linux, Fedora, CentOS, Rocky Linux, AlmaLinux, Amazon Linux, Oracle Linux, SUSE, openSUSE) for OS vendor trust. On a host with neither, nothing is vendor trusted and an allowlist has to name everything that may run.
- The extension, the permissions and the sensor version requirements of the [main page](../app-control.md#requirements), and a policy whose `platforms` names `linux`. An empty `platforms` list reaches Windows and macOS only, so a Linux host is never matched by a policy that does not name it. The console's `install-mode` and `lockdown` policies have no platform list, so [install mode](../app-control.md#install-mode) and [lockdown](../app-control.md#lockdown) do not reach Linux hosts; a policy that names `linux` and matches the same tag does.

Linux Application Control has been exercised on Ubuntu 20.04, 24.04 and 26.04, Oracle Linux 9 and Fedora 45. On CentOS 7 the sensor reports but cannot enforce.

## How it works on Linux

The sensor places a fanotify exec-permission mark on every mounted filesystem it can see. From then on the kernel pauses each `execve` until the sensor has answered for the file being opened. The sensor judges the file through the policy's [evaluation order](../app-control.md#how-it-works), with package provenance in the place of OS vendor trust, and answers. A denied execution fails with `Operation not permitted` before any of its code runs. An allowed one proceeds; the round trip is well under a millisecond for a path or vendor decision.

Points worth knowing:

- **Every mount the sensor can see is covered, as it appears.** The sensor re-reads the mount table when it changes, so a filesystem mounted after the sensor started is marked within a few seconds. Pseudo filesystems (`proc`, `sysfs`, `cgroup`, `devpts` and the like) and every FUSE filesystem are left unmarked on purpose.
- **A decision has a budget.** If the sensor cannot answer within 1.5 seconds, for example because a very large file is being hashed from a slow disk, it allows the execution and reports it as `APP_CONTROL_UNRESOLVED`.
- **Interpreters and scripts.** The dynamic loader (`ld-linux-x86-64.so.2`) is opened for execution by the kernel for every dynamically linked program, so it is judged like any program and must be allowed. A script started directly, through its `#!` line, is judged as a file. A script read by an interpreter from standard input or passed with `-c` is not, because no file is opened for execution.
- **Lineage.** Trusted installers work as on the other platforms. On Linux the sensor also looks through subshells and pipelines, which fork without executing a file, so a command started from `$( )` inside a package maintainer script still inherits the installer's trust.
- **The sensor's own commands are not judged.** Programs the sensor starts itself, such as a `run` task sent from the cloud, run without a verdict.

!!! warning "Fail-open"
    The sensor is the only enforcement point. When the sensor is not running, the kernel releases every pending execution and the host runs without Application Control. A sensor restart, and the sensor's own module upgrades, pause enforcement for about two seconds each. Nothing on the host can block while the sensor is down.

## Rules on Linux

| Kind | On Linux |
| --- | --- |
| `path` | Matches. A value ending in `/` matches every file under that directory. Matching is case-insensitive for ASCII characters, as on the other platforms. |
| `sha256` | Matches. |
| `signer`, `signing_id`, `signer_root` | Never match. A Linux file carries no signature, so a rule of one of these kinds is simply never satisfied on a Linux host. |
| `installer` | Works, named by `path`. |

Two things about paths:

- **The file that was opened is what is judged.** A program started through a symbolic link is judged under the link's target. Name real files in rules. On Fedora, `dnf` is a link to `/usr/bin/dnf5`; on RHEL 9 and its derivatives, `dnf` and `yum` are links to `/usr/bin/dnf-3`.
- **A path rule that allows a directory allows whatever can be written into it.** Keep path allows to directories only root can change, such as `/usr/local/bin/` or `/opt/<vendor>/`, never to `/tmp/`, `/home/` or `/var/tmp/`.

### Package managers as trusted installers

Under an `allowlist`, package installation and upgrades need the package manager named as a trusted installer, because the maintainer scripts a package runs are written to temporary locations at install time and belong to no package: `dpkg` runs them from `/var/lib/dpkg/tmp.ci/`, `rpm` writes each scriptlet to `/var/tmp/` and runs it with the shell. Without an installer rule, an `allowlist` refuses the first maintainer script and the install fails half way.

Add one [installer rule](../../../../7-administration/config-hive/app-control-rule.md#installer-rules) per package manager binary on the host:

| Distribution family | Installer rules |
| --- | --- |
| Debian, Ubuntu | `/usr/bin/apt`, `/usr/bin/apt-get`, `/usr/bin/dpkg` |
| RHEL 8 and 9 and derivatives, Oracle Linux, Amazon Linux 2023 | `/usr/bin/rpm`, `/usr/bin/dnf-3`, `/usr/bin/microdnf` when present |
| Fedora 41 and later | `/usr/bin/rpm`, `/usr/bin/dnf5`, `/usr/bin/dnf-3` when present |

For example, saved as `installer-dpkg.json`:

```json
{
    "action": "installer",
    "kind": "path",
    "value": "/usr/bin/dpkg"
}
```

```bash
limacharlie hive set \
  --hive-name app_control_rule \
  --key installer-dpkg \
  --input-file installer-dpkg.json \
  --enabled
```

`apt` and `apt-get` are owned by the distribution, so vendor trust already allows them to run; they are named as installers because they run the packages' configuration scripts, through `dpkg-preconfigure` and debconf, before `dpkg` is involved. The three rules together are the set the Debian and Ubuntu upgrades were verified with. The same mechanism serves any other installer you rely on, such as a configuration-management agent or `pip`, with the same breadth of trust the [main page](../app-control.md#self-updating-software-and-trusted-installers) describes.

## OS vendor trust: package provenance

With `trust_os_vendor: true`, the sensor builds an index of every file the host's packages installed, with the digest each package recorded, and treats a file as the vendor's own when all of the following hold:

1. A package owns the file's path.
2. The package is a **platform** package.
3. The file's content still matches the digest the package recorded for it.

What makes a package a platform package:

- **rpm.** The package header is signed by a key whose owner address belongs to the distribution: `redhat.com`, `fedoraproject.org`, `centos.org`, `rockylinux.org`, `almalinux.org`, `amazon.com`, `oracle.com`, `suse.com`, `suse.de` or `opensuse.org`. The sensor reads the keys from `/etc/pki/rpm-gpg`, from `/usr/share/distribution-gpg-keys` and from the `gpg-pubkey` packages the host has imported.
- **dpkg.** No signature survives installation, so the archive's own claim stands in. A package counts when its maintainer address is at `ubuntu.com`, `canonical.com` or `debian.org`, or when the installed version is listed in an apt index whose release file names the distribution as its origin. The second test goes stale on a host that has not run `apt update` in a long time.

Vendor trust therefore does not cover:

- **Third-party packages**, even when they came from a signed repository: Docker, Google Chrome, Microsoft, HashiCorp and other vendor repositories, EPEL, and anything built locally. Allow them by `path` or `sha256`.
- **Snaps, Flatpaks and AppImages.** Their programs are not part of a package the distribution signed. A snap or Flatpak needs a path allow for its store (`/snap/`, `/var/lib/flatpak/`). An AppImage mounts itself through FUSE, so its inner programs are never judged at all; only the AppImage file itself is.
- **Configuration files that are executable**, such as the scripts in `/etc/update-motd.d/` or `/etc/cron.daily/` shipped by Debian and Ubuntu packages as `conffiles`. They carry no digest in the package, so vendor trust cannot vouch for them. Add a path allow for the directory, or move to a `blocklist` stance for such hosts.

### Package upgrades

The index is rebuilt within about two seconds of a change to the package database, and the sensor knows when a transaction is in progress. During that window, a file a platform package owns, whose content no longer matches the index, is **allowed** rather than refused, and reported as `APP_CONTROL_UNRESOLVED` with reason `52`. That is what lets `glibc`, `systemd` and `coreutils` be replaced under an `enforcing` allowlist without refusing the system's own loader. Process 1 is never denied on any policy, and is reported with reason `53` when it would have been.

## Programs that are already running

[`on_enable`](../app-control.md#programs-that-are-already-running) works as described on the main page. On Linux, `terminate` never stops process 1 or 2, a kernel thread, or the sensor itself. A program refused only because no rule matched it, when the policy names installers, is reported and left running, as on the other platforms.

## Limitations

- **Program files only.** Shared libraries, `LD_PRELOAD`, `dlopen`, scripts fed to an interpreter from standard input or `-c`, and programs executed from memory (`memfd_create`) are not controlled.
- **No signatures.** `signer`, `signing_id` and `signer_root` rules never match. Third-party software has no durable identity on Linux, so it is allowed by path, with the exposure a path rule carries, or by hash, with the maintenance a hash rule carries.
- **FUSE filesystems are not covered.** Programs under `sshfs`, `gvfs`, AppImage mounts and other FUSE filesystems run unjudged and unreported.
- **Network filesystems are judged but never cached.** A program on NFS, CIFS or 9p is hashed on every execution when the policy needs its digest.
- **No user notification.** The policy's user notification and tray icon settings have no effect on Linux.
- **Fail-open while the sensor is down**, as described above.

## Events on Linux

The events are the ones described in [Reading would-be blocks](../app-control.md#reading-would-be-blocks) and in the [EDR events reference](../../../../8-reference/edr-events.md#app_control_denied), with these differences:

- `APP_CONTROL_SIGNER`, `APP_CONTROL_SIGNING_ID`, `APP_CONTROL_SIGNATURE_STATUS`, the thumbprints and the application identity fields are absent.
- `APP_CONTROL_VENDOR_TRUSTED` is `1` when package provenance vouched for the file.
- `HASH` is the file's SHA-256.
- `FILE_PATH` is the path of the file that was opened, after symbolic links.

Every Linux sensor also reports what its host can do, with or without a policy, in the `APP_CONTROL_HOST` sequence of `APP_CONTROL_STATUS`. It is sent in each `SYNC` and in the reply to the [`app_control_policy`](../../../../8-reference/endpoint-commands.md#app_control_policy) command:

| Field | Meaning |
| --- | --- |
| `APP_CONTROL_HOST_EXEC_HOOK` | `1` when the kernel delivers exec permission events and the sensor may take them. A host that reports `0` cannot enforce. |
| `APP_CONTROL_HOST_PRIVILEGED` | `1` when the sensor holds `CAP_SYS_ADMIN`. |
| `APP_CONTROL_HOST_BPF_LSM` | `1` when `bpf` is in the kernel's active LSM list. Informational. |
| `APP_CONTROL_HOST_MOUNTS_MARKED` | Mounts covered on the last pass over the mount table. |
| `APP_CONTROL_HOST_MOUNTS_SKIPPED` | Mounts left uncovered on purpose: pseudo and FUSE filesystems. |
| `APP_CONTROL_HOST_MOUNTS_FAILED` | Mounts the sensor tried to cover and could not. |
| `APP_CONTROL_HOST_ERROR` | The operating system's error text when the hook is unavailable. |
| `APP_CONTROL_HOST_KERNEL` | The kernel release, as `uname -r` reports it. |

## Checking a host before you roll out

Run these on the host, as root, before enrolling it or before adding it to an enforcing policy. Each one changes nothing.

### 1. Kernel version and configuration

```bash
uname -r
grep -E 'CONFIG_FANOTIFY(_ACCESS_PERMISSIONS)?=' "/boot/config-$(uname -r)"
```

Expect a kernel at 5.0 or later and both lines set:

```text
CONFIG_FANOTIFY=y
CONFIG_FANOTIFY_ACCESS_PERMISSIONS=y
```

On a distribution that does not ship `/boot/config-*`, read `zcat /proc/config.gz` instead.

### 2. Exec permission events

The sensor's own test, as a script: it opens a fanotify group, asks for an exec-permission mark on `/`, and closes the group again. Nothing is blocked, nothing is logged.

```bash
sudo python3 - <<'EOF'
import ctypes, os, sys
libc = ctypes.CDLL(None, use_errno=True)
libc.fanotify_init.argtypes = [ctypes.c_uint, ctypes.c_uint]
libc.fanotify_mark.argtypes = [ctypes.c_int, ctypes.c_uint, ctypes.c_uint64, ctypes.c_int, ctypes.c_char_p]
fd = libc.fanotify_init(0x4 | 0x1 | 0x2, os.O_RDONLY | os.O_CLOEXEC)  # FAN_CLASS_CONTENT | FAN_CLOEXEC | FAN_NONBLOCK
if fd < 0:
    print("exec permission events: unavailable (fanotify_init: %s)" % os.strerror(ctypes.get_errno()))
    sys.exit(1)
rc = libc.fanotify_mark(fd, 0x1, 0x40000, -100, b"/")  # FAN_MARK_ADD, FAN_OPEN_EXEC_PERM, AT_FDCWD
err = ctypes.get_errno()
os.close(fd)
if rc == 0:
    print("exec permission events: available")
else:
    print("exec permission events: unavailable (fanotify_mark: %s)" % os.strerror(err))
    sys.exit(1)
EOF
```

| Output | Meaning |
| --- | --- |
| `exec permission events: available` | The host can enforce. |
| `unavailable (fanotify_mark: Invalid argument)` | The kernel predates exec permission events (kernel 3.10 and 4.x). The host can only report. |
| `unavailable (fanotify_init: Operation not permitted)` | Not run as root, or `CAP_SYS_ADMIN` is missing. Run it with `sudo`; inside a container, the sensor will fail the same way. |

### 3. Privilege of the sensor service

```bash
sudo capsh --print | grep -o cap_sys_admin
```

Expect `cap_sys_admin`. If the sensor runs under a unit with a `CapabilityBoundingSet` of its own, check that set instead. `capsh` comes with the `libcap` tools (`libcap2-bin` on Debian and Ubuntu, `libcap` on the rpm distributions).

### 4. Package provenance

On an rpm host, list the signing keys the host knows and count the installed packages by the key that signed them:

```bash
rpm -q gpg-pubkey --qf '%{VERSION} %{PACKAGER}\n'
rpm -qa --qf '%{RSAHEADER:pgpsig}\n' | awk '{print $NF}' | sort | uniq -c | sort -rn
```

The first command names each imported key with its owner; one whose owner address is at the distribution is a platform key. The second counts packages per signing key id, which matches the last 8 or 16 characters of a key's id. For example, on Oracle Linux 9:

```text
8d8b756f Oracle Linux (release key 1) <secalert_us@oracle.com>
   1066 bc4d06a08d8b756f
      2 (none)
```

Every package counted under a platform key is vendor trusted. Packages under another key, or `(none)`, need rules of their own (the two unsigned ones here are the `gpg-pubkey` records themselves, which own no file).

On a dpkg host, count the packages whose maintainer is the distribution against the total, and list the rest:

```bash
dpkg-query -W -f='${Maintainer}\n' | wc -l
dpkg-query -W -f='${Maintainer}\n' | grep -cE '@([a-z0-9.-]+\.)?(ubuntu\.com|canonical\.com|debian\.org)>'
dpkg-query -W -f='${Package} ${Maintainer}\n' | grep -vE '@([a-z0-9.-]+\.)?(ubuntu\.com|canonical\.com|debian\.org)>'
```

The last command prints the packages that vendor trust will not cover, such as a vendor's own `.deb` for a browser or a container runtime. Those are the programs to allow by path before enforcing.

### 5. Filesystems the hook does not cover

```bash
findmnt -rno TARGET,FSTYPE | awk '$2 ~ /^fuse/'
```

Every line is a FUSE filesystem whose programs run unjudged. A desktop host lists `gvfs` and the portal mount of the logged-in user; a server normally lists nothing.

### 6. After the sensor is installed

Once the sensor is enrolled, read the host's own report:

```bash
limacharlie task request --sid <SID> --command app_control_policy
```

Look at `APP_CONTROL_STATUS` → `APP_CONTROL_HOST`. A host that can enforce reports `APP_CONTROL_HOST_EXEC_HOOK: 1` and `APP_CONTROL_HOST_PRIVILEGED: 1`; otherwise `APP_CONTROL_HOST_ERROR` says why.

To find every Linux host that cannot enforce without asking each one, a D&R rule on the `SYNC` event does it fleet-wide. Each matching host produces a detection:

```yaml
detect:
  event: SYNC
  op: is
  path: event/APP_CONTROL_STATUS/APP_CONTROL_HOST/APP_CONTROL_HOST_EXEC_HOOK
  value: 0
respond:
  - action: report
    name: app-control-linux-no-exec-hook
```

Then follow the [rollout](../app-control.md#rolling-out) on the main page: Audit first, read the `APP_CONTROL_DENIED` events, add the installer rules and the path rules the reports call for, and only then move the host to Rehearsal and Enforcing.

!!! warning "Enroll new hosts into Audit, not Enforcing"
    A host that joins an `enforcing` allowlist at enrollment is judged from the moment the policy arrives. If its package database is not one the sensor recognizes, nothing is vendor trusted, and the policy refuses the host's own daemons, `sshd` included. Target enforcing policies by tag and add the tag only after the host's first Audit reports show the system's own programs as vendor trusted.

## See Also

- [Application Control](../app-control.md)
- [Application Control policies](../../../../7-administration/config-hive/app-control-policy.md)
- [Application Control rules](../../../../7-administration/config-hive/app-control-rule.md)
- [Linux installation](../../../../2-sensors-deployment/endpoint-agent/linux/installation.md)
- [EDR events reference](../../../../8-reference/edr-events.md#app_control_denied)
