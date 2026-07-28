# File

## Overview

This Adapter ingests logs from a file. It can do one pass over the file, or it can read new content as the file grows (like `tail -f`). For more detail about file collection, see the [Log Collection Guide](../../log-collection-guide.md).

### Configuration

All adapters support the same `client_options`. Always specify them when you use the binary adapter or create a webhook adapter. If you use an Adapter helper in the web app, you do not need to specify these values.

- `client_options.identity.oid`: the LimaCharlie Organization ID (OID) that this adapter is used with.
- `client_options.identity.installation_key`: the LimaCharlie Installation Key that this adapter uses to identify itself to LimaCharlie.
- `client_options.platform`: the type of data that this adapter ingests, for example `text`, `json`, `gcp`, or `carbon_black`.
- `client_options.sensor_seed_key`: a name that you choose for this adapter. LimaCharlie generates the Sensor IDs (SID) from this name. See below.

Adapter type `file`:

- `file_path`: a file pattern, for example `./files_*.txt`
- `no_follow`: if `true`, the adapter sends the file content but does not report additions to the file
- `inactivity_threshold`: the number of seconds without a change after which the adapter ignores a file (default: 86400, that is 24 hours)
- `reactivation_threshold`: the number of seconds in which an inactive file must change for the adapter to tail it again (default: 60)
- `backfill`: if `true`, the adapter makes one pass over all the matching files and ingests them. Use this option for historical ingestion
- `serialize_files`: if `true`, the adapter ingests the files one at a time. Use this option for a very large number of files that can exhaust memory
- `poll`: if `true`, use polling instead of filesystem event notifications to detect file changes. See [Polling Mode](#polling-mode) below
- `multi_line_json`: if `true`, the adapter buffers lines and assembles complete JSON objects that span multiple lines before it sends them
- `write_timeout_sec`: the number of seconds before a write to LimaCharlie times out (default: 600)

### Polling Mode

By default, the file adapter uses filesystem notifications from the operating system (such as `inotify` on Linux or `kqueue` on BSD/macOS) to detect new data in a file. This mechanism is efficient, but it can fail to detect changes in these situations:

- **Log rotation**: When a log management tool (for example `newsyslog` or `logrotate`) rotates a file, the original file descriptor can become stale. The notification watcher can stay attached to the old file, which is now renamed or deleted, and miss the writes to the new file at the same path.
- **Network and virtual filesystems**: NFS, CIFS/SMB, and some filesystems that use FUSE do not always deliver filesystem notifications.
- **Platform-specific quirks**: Some operating systems or filesystem drivers have incomplete or inconsistent support for notifications.

Set `poll: true` to switch the adapter to polling. The adapter then checks the file for new content at regular intervals. Polling is a little less efficient than event notifications, but it is more reliable on different platforms and with log rotation.

The adapter also detects rotation with the inode of the file. If the inode of a file changes between poll cycles, the adapter closes the old file handle and opens the new file. This detection works with polling mode to give reliable collection across rotations.

**When to use `poll: true`:**

- You use FreeBSD, OpenBSD, NetBSD, or Solaris
- Tools such as `newsyslog` or `logrotate` rotate your log files
- The adapter stops collection after a log rotation event
- Your files are on a network filesystem or a virtual filesystem

**Example:**

```yaml
file:
  client_options:
    identity:
      oid: "your-organization-id"
      installation_key: "your-installation-key"
    platform: "text"
    sensor_seed_key: "freebsd-syslogs"
  file_path: "/var/log/messages"
  poll: true
```

### CLI Deployment

Get the [Adapter downloads](../deployment.md) from the deployment page.

```bash
chmod +x /path/to/lc_adapter

/path/to/lc_adapter file client_options.identity.installation_key=$INSTALLATION_KEY \
client_options.identity.oid=$OID \
client_options.platform=text \
client_options.sensor_seed_key=$SENSOR_NAME \
client_options.hostname=$SENSOR_NAME \
file_path=/path/to/file
```
