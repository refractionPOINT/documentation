# Varist Hybrid Analyzer

The Varist extension (`ext-varist`) turns on the [Varist](https://www.varist.com/) Hybrid Analyzer that ships inside the LimaCharlie endpoint agent, keeps it turned on across sensor restarts, and surfaces its results across the fleet: a filterable list of scans, a per-scan analysis report, and an action that scans a path on many sensors at once.

The Hybrid Analyzer is a malware and behavioural analysis engine. On an endpoint where it is enabled, the agent scans the image of every process that starts and reports anything that rates as a threat, and it answers on-demand scans of any file or directory. Results arrive as ordinary LimaCharlie events, so they can be queried, routed to an [Output](../../outputs/index.md), and matched by [D&R rules](../../../3-detection-response/index.md) like any other telemetry.

!!! info "Third-party scanning engine"
    The Hybrid Analyzer is a third-party product built by [Varist](https://www.varist.com/), not by LimaCharlie. LimaCharlie embeds the engine in the endpoint agent, runs it, and integrates its output into the platform — but the analysis itself, the malware definitions, the ratings and the detection names all come from Varist, and its use is governed by the Varist license. Definition files are fetched by the endpoint directly from Varist's infrastructure. Questions about a specific verdict, a detection name, or engine coverage belong with Varist; questions about enabling it, tasking it, or the events it produces belong with LimaCharlie.

## What it does

1. **Enables the engine across the fleet.** A license key in the extension configuration is pushed to every sensor as collector configuration and re-applied automatically whenever a sensor reconnects, so Varist stays on through restarts and upgrades without per-sensor tasking.
2. **Scans on process launch.** While the engine is running, the agent scans the image of each process as it starts and emits an event for anything rating 90 or above.
3. **Scans on demand.** The `varist_scan` sensor command scans a file or a directory tree. The extension's **Scan paths** action sends the same scan to as many as 500 sensors in one call.
4. **Reports as events.** Every reported file produces a `VARIST_SCAN_FILE_REP` event carrying the file name, its SHA-256, the rating, and the full analysis report.
5. **Surfaces the results.** The extension adds a **Varist Scans** page to the web app with a fleet-wide list and a per-scan **Analysis Report** view.

## Requirements

- **Endpoint Agent 5.3.9 or later.** The Varist engine is embedded in the agent from that release; earlier agents have no engine to enable. See [Versioning & Upgrades](../../../2-sensors-deployment/endpoint-agent/versioning-upgrades.md).
- **Windows or Linux on x86-64.** Every other platform and architecture — macOS, ARM, Chrome — answers `ERROR_NOT_SUPPORTED` (50) to every Varist command.
- **Outbound HTTPS from the endpoint to `beacon.varist.ai`**, Varist's own definition-file service, where the scanner fetches and updates its definitions. Without them the engine cannot initialize and scans fail.
- A Varist license key, set in the extension configuration (see [Setup](#setup)). The license is what authorizes both the engine and its definition updates.

Scanning is CPU-bound. The scanner sizes its worker pool to the host's logical CPU count, and the agent caps its own dispatch pool at half that, so a scan of a large directory tree will use a meaningful share of the machine while it runs.

## Setup

Navigate to the [Varist extension page](https://app.limacharlie.io/add-ons/extension-detail/ext-varist) in the marketplace, select the organization, and click **Subscribe**. Pricing for the add-on is shown on that page.

Then open the extension's configuration and set:

| Field | Type | Description |
|-------|------|-------------|
| `license` (**Varist License Key**) | string | The license the sensors use to run the Varist engine. Setting it enables Varist on every sensor in the organization and keeps it enabled across restarts. Leaving it empty disables Varist and stops the engine on any sensor that was running it. |

Subscribing installs one managed D&R rule, `ext-varist-sync`, in the `dr-managed` hive. It fires an internal action on every sensor `SYNC` and is what drives the reconciliation described in [How enablement reaches the endpoint](#how-enablement-reaches-the-endpoint). The install is idempotent — it is re-applied whenever the extension's configuration changes, so a rule that was deleted or edited heals itself. Unsubscribing removes it.

The extension requests the permissions it needs at subscribe time, including `sensor.task` (to dispatch scans), the Insight read permissions (to list and fetch scan events), and the managed-rule permissions (to own its sync rule).

!!! note "Event collection"
    The five `VARIST_*` events are part of the default event-collection set for Windows and Linux sensors, so no change is needed in a default organization. If your organization has a hand-edited **Sensors → Event Collection** configuration, add `VARIST_SCAN_FILE_REP`, `VARIST_SCAN_REP`, `VARIST_START_REP`, `VARIST_STOP_REP` and `VARIST_STATUS_REP` to it, or scan verdicts will never leave the host and the scan list will stay empty.

## How enablement reaches the endpoint

The agent does not persist any Varist state: the engine is started in memory and is gone after a restart. Rather than re-tasking each sensor, the extension keeps the license in the sensor's collector configuration and lets the normal configuration channel re-apply it:

1. On every sensor `SYNC`, the `ext-varist-sync` rule reports the sensor's per-collector configuration generations to the extension.
2. The extension compares the generation of the Varist collector against the one implied by the configured license. An empty license maps to generation `0`, which is also the generation of a sensor that was never configured — so a sensor in an organization with no license is never touched.
3. When they differ, the extension returns a sensor configuration update carrying the license, and the platform delivers it to the sensor and records the new generation.
4. The agent reads the license from that configuration and starts the engine — or stops it, when the license is empty. A sensor that restarts reports generation `0` again on its next `SYNC`, and the cloud re-applies without anyone doing anything.

Changing the license in the configuration changes the generation, so the fleet converges on the new one; the engine is restarted only on the sensors whose license actually changed.

On the endpoint, starting the engine means the agent extracts the scanner from its own binary — there is no separate download or installer — and runs it as a child process listening on loopback only (`127.0.0.1:4660`, or the next free port above it if that one is taken). The license is handed to the scanner over that loopback connection rather than through its environment or command line. The scanner then fetches its definition files from `beacon.varist.ai` and builds its scan pool; until it is ready it answers "not ready" rather than scanning.

A watchdog inside the agent checks the scanner every 15 seconds and restarts it if the process is gone or has stopped answering on its port. Repeated restarts that never hold are given up on after five attempts, so a scanner that cannot run at all — a bad license, for instance — does not respawn forever; a scanner that stays healthy for a minute clears the count, and pushing the license again resets it.

## Scanning

### On process launch

While the engine is running, the agent scans the image of every process that starts, and reports the result when the rating is **90 or above**. This is what makes Varist an on-access control rather than only an on-demand one, and the rating floor is what keeps the volume down: 90 and above is the malicious band, not the merely unusual one.

### On demand

A scan targets a path. When the path is a file, that file is scanned; when it is a directory, the tree beneath it is walked and every file scanned, in parallel, up to the requested depth.

A scan produces **one `VARIST_SCAN_FILE_REP` event per file that meets the rating threshold** plus **one `VARIST_SCAN_REP`** when the whole scan finishes, carrying how many files were scanned and how many were reported. Files below the threshold are scanned but not reported.

From a sensor console, or the CLI:

```bash
limacharlie task send --sid <SID> --task 'varist_scan "/home/user/Downloads" -r 80 -d 20'
```

From the extension — including from the web app's **Scan paths** button — the same scan can be sent to many sensors at once:

```bash
limacharlie extension request --name ext-varist --action run_varist_scan \
  --data '{"sensor_ids":["<SID1>","<SID2>"],"path":"/home/user/Downloads","min_rating":80}'
```

The extension fans out to at most 500 sensors per call, ten at a time, and returns the number of sensors that accepted the task along with the ids of those that did not (an offline sensor is a failure here, not a queued task — for that, see [Reliable Tasking](reliable-tasking.md)).

## Ratings

Varist rates each analyzed object from `0` to `100`. The web app buckets that number into the same risk flags Varist uses:

| Flag | Rating | `VARIST_RATING` in events |
|------|--------|---------------------------|
| MALICIOUS | 90 and above | 9000 and above |
| HIGH RISK | 60 – 89 | 6000 – 8999 |
| MEDIUM RISK | 40 – 59 | 4000 – 5999 |
| LOW RISK | 20 – 39 | 2000 – 3999 |
| NO RISK | below 20 | below 2000 |

`VARIST_RATING` in the event is the rating multiplied by 100, so it carries two decimal places as an integer. The `Rating` field inside the analysis report is the unscaled `0`–`100` value. Rating thresholds passed to a scan (`-r`, `min_rating`) are on the unscaled `0`–`100` scale.

## Events

| Event | When it fires |
|-------|---------------|
| `VARIST_SCAN_FILE_REP` | One per file whose rating meets the scan's threshold — from an on-demand scan or from a process launch. |
| `VARIST_SCAN_REP` | Once per on-demand scan, when it completes. |
| `VARIST_START_REP` | Reply to a `varist_start` command. |
| `VARIST_STOP_REP` | Reply to a `varist_stop` command. |
| `VARIST_STATUS_REP` | Reply to a `varist_status` command. |

### VARIST_SCAN_FILE_REP

| Field | Type | Description |
|-------|------|-------------|
| `FILE_NAME` | string | Full path of the file that was scanned. |
| `HASH` | string | SHA-256 of the file, lowercase hex. |
| `VARIST_SCAN_RESULT` | string | Scan status: `OK` when the engine completed the analysis, `ERROR` when it failed. This is a status, not a verdict — a detection still scans successfully. |
| `VARIST_SCAN_TIME` | integer | Analysis duration in milliseconds. |
| `VARIST_RATING` | integer | Rating × 100 (see [Ratings](#ratings)). |
| `VARIST_RESPONSE` | object | The full analysis report. |

### The analysis report

`VARIST_RESPONSE` is the analyzer's own report, parsed into an object by the platform:

```json
{
  "FileName": "/home/user/Downloads/sample.bin",
  "Sha256": "70d49113c7a5d47ee251a2e8680ee5d82a1b54de446e55fc7ba6ed5ca00db329",
  "ScanResult": "OK",
  "ScanTime": 1759,
  "TimeStamp": "2026-04-20T21:48:16Z",
  "Rating": 96.5,
  "Versions": {
    "ServiceVersion": "2.4.1",
    "SdkVersion": "2.4.1|5.8.2",
    "AntivirVersion": "202605211521",
    "AivseconVersion": "202605211521"
  },
  "RootObject": {
    "Id": 0,
    "ParentId": 0,
    "Name": "/home/user/Downloads/sample.bin",
    "Sha256": "70d49113c7a5d47ee251a2e8680ee5d82a1b54de446e55fc7ba6ed5ca00db329",
    "ObjectType": "File",
    "ObjectSize": 274432,
    "Rating": 96.5,
    "MetaData": {},
    "IndicatorCategories": [
      {
        "Category": "Detected",
        "Indicators": [
          {
            "Item": "Detection",
            "Info": "EICAR-Test-File",
            "Description": "Detected as EICAR-Test-File",
            "Rating": 0
          }
        ]
      }
    ]
  }
}
```

| Field | Description |
|-------|-------------|
| `FileName`, `Sha256` | The scanned file and its hash. |
| `ScanResult` | `OK` or `ERROR`, as in the event. |
| `ScanTime` | Analysis duration in milliseconds. |
| `TimeStamp` | When the analysis completed, RFC 3339. |
| `Rating` | Final rating of the root object, `0`–`100`. |
| `Versions` | Engine, SDK and definition-file versions used for this scan. |
| `RootObject` | The analyzed object tree. |

Each object in the tree carries `Name`, `Id`, `ParentId`, `ObjectType`, `ObjectSize`, its own `Rating`, its `IndicatorCategories`, and any nested `Objects` — an archive, an installer or a document with an embedded payload reports each contained object separately, with the parent's rating reflecting the analysis of the whole. Indicators are grouped by category (`Detected`, `Execute`, `Evasion`, `Network`, `Crypto`, `Registry`, `Inject`, `Autoex` and others), and each indicator has an `Item`, free-form `Info`, a `Description`, and its own `Rating`. A named malware detection appears as an `Item` of `Detection` under the `Detected` category, with the detection name in `Info`. URL indicators add a `Components` object breaking the URL into its parts.

Fields other analyzer builds emit, such as `SummaryDescription`, may be absent. The web app falls back to bucketing the numeric `Rating` when no flag is supplied.

### VARIST_SCAN_REP

Echoes the request (`FILE_PATH`, `VARIST_MIN_RATING`, `VARIST_MAX_DEPTH`, `VARIST_LONG_FORM`) and adds:

| Field | Type | Description |
|-------|------|-------------|
| `ERROR` | integer | `0` on success. See [Error Codes](../../../8-reference/error-codes.md); `50` (`NOT_SUPPORTED`) on an unsupported platform, and `9` (`NOT_INITIALIZED`) when the engine is not running on the sensor. |
| `VARIST_FILE_SCANNED_COUNT` | integer | Files scanned. |
| `VARIST_FILE_REPORTED_COUNT` | integer | Files that met the rating threshold and produced an event. |

### VARIST_STATUS_REP

| Field | Type | Description |
|-------|------|-------------|
| `ERROR` | integer | `0` when the engine is running. |
| `VARIST_PORT` | integer | Loopback port the scanner is bound to. |
| `VARIST_STATUS_PID` | integer | Process id of the scanner. |
| `VARIST_STATUS_UPTIME` | integer | Seconds since the scanner started. |
| `VARIST_STATUS_START_TIME` | integer | Scanner start time, Unix seconds. |
| `VARIST_STATUS_SCAN_COUNT` | integer | Scans performed since start. |
| `VARIST_STATUS_SCAN_SUCCESS_COUNT` | integer | Of those, successful. |
| `VARIST_STATUS_SCAN_FAILURE_COUNT` | integer | Of those, failed. |
| `VARIST_STATUS_SCAN_TIME_AVG` | integer | Average scan time in milliseconds. |

## Querying and detecting

Varist events are ordinary telemetry. To list what the fleet reported in the last day above a HIGH RISK rating:

```text
-24h | * | VARIST_SCAN_FILE_REP | event/VARIST_RATING is greater than 7999 | routing/hostname as hostname event/FILE_NAME as FILE_NAME event/HASH as HASH event/VARIST_RATING as VARIST_RATING
```

To raise a detection whenever a file rates as malicious:

```yaml
# Detect
event: VARIST_SCAN_FILE_REP
op: and
rules:
  - op: exists
    path: event/VARIST_RATING
  - op: is greater than
    path: event/VARIST_RATING
    value: 8999
```

```yaml
# Respond
- action: report
  name: Varist - malicious file detected
```

Because the rating floor for process-launch scans is already 90, a rule with no rating test at all is a reasonable starting point for organizations that only want to know when Varist reported anything.

## Web app

Once subscribed, the organization gets a **Varist Scans** page:

- **Scan list** — every reported scan across the fleet, newest first, with the file name, its risk badge and rating, scan duration, timestamp, file size and the sensor that reported it. A risk-level filter narrows the list to one band.
- **Analysis Report** — clicking a row opens the detail view: the rating and its flag, file information, and three tabs — **Indicators Overview** (findings grouped by category), **Root object** (the analyzed object tree, with each contained object's own type, size and rating) and **JSON output** (the raw report).
- **Scan paths** — a dialog that takes a path, optional long-form and advanced options (minimum rating, maximum depth), and a sensor picker with hostname and online-only filters. Results land in the list within about half a minute.

## Extension API

All three actions are available over the REST API and the CLI.

| Action | Description |
|--------|-------------|
| `list_scans` | A page of normalized scan rows across the fleet. |
| `get_scan` | One scan: the normalized row plus the raw analysis report. |
| `run_varist_scan` | Send a `varist_scan` to a list of sensors. |

### list_scans

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `start` | integer | now − 10 days | Start of the window, Unix seconds. |
| `end` | integer | now | End of the window, Unix seconds. |
| `limit` | integer | 50 | Rows per page; maximum 500. |
| `cursor` | string | | Continuation cursor from a previous page. |
| `rating_min` | integer | | Only rows rating at least this, `0`–`100`. |
| `flag` | enum | | One of `MALICIOUS`, `HIGH RISK`, `MEDIUM RISK`, `LOW RISK`, `NO RISK`. |
| `sensor_id` | string | | Restrict to one sensor. |

Returns `items` — rows of `analysis_id`, `sensor_id`, `hostname`, `platform`, `file_name`, `sha256`, `object_type`, `size`, `rating`, `rating_flag`, `scan_duration_ms`, `ts_ms` and `event_atom` — plus a `cursor` when more results are available.

```bash
curl --location 'https://api.limacharlie.io/v1/extension/request/ext-varist' \
--header 'Authorization: Bearer $JWT' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data 'oid=$YOUR_OID&action=list_scans&data={"limit":50,"rating_min":80}'
```

### get_scan

| Parameter | Type | Description |
|-----------|------|-------------|
| `sensor_id` | string | **Required.** Sensor that produced the event. |
| `event_atom` | string | **Required.** Event atom, as returned by `list_scans` in `event_atom`. |

Returns `summary` (the same row shape as `list_scans`) and `report` (the raw analysis report).

### run_varist_scan

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sensor_ids` | list of strings | | **Required.** Up to 500 sensors. |
| `path` | string | | **Required.** File or directory to scan on each sensor. Paths containing shell metacharacters are rejected. |
| `long_form` | boolean | `false` | Run the engine's full analysis instead of the lower-overhead simple scan. |
| `min_rating` | integer | 80 | Report threshold, `0`–`100`. |
| `max_depth` | integer | 20 | Directory recursion depth. |

Returns `dispatched` (how many sensors accepted the task), `failed` (the sensor ids that did not) and `task_string` (the exact command that was sent).

## Sensor commands

| Command | Description |
|---------|-------------|
| `varist_scan` | Scan a file or directory. |
| `varist_start` | Start the engine with a license, for this run of the sensor only. |
| `varist_stop` | Stop the engine. |
| `varist_status` | Report the scanner's port, pid, uptime and scan counters. |

`varist_start` and `varist_stop` act on the running sensor only — they change nothing in the cloud, and the next configuration reconciliation puts the sensor back in the state the extension's license implies. Use the extension configuration to turn Varist on or off for real; use these for troubleshooting.

### varist_scan

Scan files or directories with the Varist engine.

**Platforms:** Windows | Linux

**Parameters:**

- `path` (required): file or directory path to scan, positional
- `-r`, `--rating-min` (optional): minimum rating to report, `0`–`100`; default `80`
- `-d`, `--max-depth` (optional): directory recursion depth; default `20`
- `-l`, `--long-form` (optional): run the full analysis rather than the simple scan; default off

**Response Events:** `VARIST_SCAN_FILE_REP` (one per reported file), `VARIST_SCAN_REP` (on completion)

**Usage Example:**

```bash
limacharlie task send --sid <SID> --task 'varist_scan "C:\\Users\\Public\\Downloads" -r 90 -d 5 -l'
```

### varist_start

Start the Varist engine on the sensor with the given license. Not persisted: the engine is lost on the next sensor restart.

**Platforms:** Windows | Linux

**Parameters:**

- `-k`, `--license-key` (required): the Varist license key

**Response Event:** `VARIST_START_REP`

```bash
limacharlie task send --sid <SID> --task 'varist_start -k <LICENSE_KEY>'
```

### varist_stop

Stop the Varist engine on the sensor.

**Platforms:** Windows | Linux

**Response Event:** `VARIST_STOP_REP`

### varist_status

Report whether the engine is running, and its counters.

**Platforms:** Windows | Linux

**Response Event:** `VARIST_STATUS_REP`

```bash
limacharlie task send --sid <SID> --task 'varist_status'
```

## Troubleshooting

| Symptom | What to check |
|---------|---------------|
| The scan list is empty | Is a license set in the extension configuration? Has at least one sensor connected since it was set — the license is applied on the sensor's next `SYNC`. Are the `VARIST_*` events in the organization's event-collection configuration? |
| A command returns `ERROR_NOT_SUPPORTED` (50) | The sensor is not Windows or Linux on x86-64, or its agent predates 5.3.9. |
| A scan returns `NOT_INITIALIZED` (9) | The engine is not running on that sensor. Run `varist_status`; if it reports no scanner, confirm the license is set and that the host can reach `beacon.varist.ai` for definition files. |
| `varist_status` reports a scanner, but scans time out | Check host CPU: a directory scan uses a worker per core. Scanning a smaller subtree, or a lower `--max-depth`, bounds the work. |
| A scan found files but reported none | `VARIST_SCAN_REP` carries `VARIST_FILE_SCANNED_COUNT` and `VARIST_FILE_REPORTED_COUNT`. A reported count of zero means nothing met the rating threshold — lower `-r` to see more. |
| Scans stop after a while on one host | The watchdog gives up after five restarts that do not hold. Re-apply the license (change it and change it back, or use `varist_start`) to reset it, and check the sensor's log for why the scanner exited. |

## See Also

- [Endpoint Agent Commands](../../../8-reference/endpoint-commands.md)
- [Error Codes](../../../8-reference/error-codes.md)
- [Detection & Response](../../../3-detection-response/index.md)
- [Using Extensions](../using-extensions.md)
- [Varist](https://www.varist.com/) — the vendor of the Hybrid Analyzer engine
