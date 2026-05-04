# LimaCharlie Python SDK v4

!!! warning "Deprecated"
    Version 4 of the LimaCharlie Python SDK is deprecated and will be removed
    in a future release. New code should use the
    [Python SDK](python-sdk.md) (v5). This page is kept for users
    maintaining existing v4 integrations. Both v4 and v5 target the same
    LimaCharlie REST API, so the underlying capabilities available to your
    code are unchanged.

## Overview

The v4 Python SDK is a thin abstraction over the LimaCharlie REST API,
centered on the `Manager` object. The REST API supports more functionality
than the SDK; if a REST endpoint you need is not exposed in v4, prefer
migrating to v5 rather than extending v4.

- Source (v4 branch): <https://github.com/refractionPOINT/python-limacharlie/tree/v4>
- REST API: <https://api.limacharlie.io>

## Installation

!!! warning "v4 is deprecated"
    `pip install limacharlie` now installs **v5**. To stay on v4 (not
    recommended), pin to the v4 release line:

    ```bash
    pip install "limacharlie<5"
    ```

### Requirements

- Python 3.x
- pip

### Dependencies

Core dependencies (installed automatically):

- `requests`
- `passlib`
- `pyyaml`
- `tabulate`
- `termcolor`
- `pygments`
- `rich`
- `cryptography>=44.0.1`

## Authentication

The SDK and CLI support several ways of providing credentials.

### Logging In

The simplest path is to log in with an
[API key](../../7-administration/access/api-keys.md):

```bash
limacharlie login
```

You will be prompted for an `OID` (Organization ID, in UUID format) and an
API key, both available from the **REST API** section of the web interface.

The login flow supports named environments — credentials are stored under a
chosen name, with one set used as the default when no environment is
selected.

To list available environments:

```bash
limacharlie use
```

To activate a named environment in the current shell session:

```bash
. <(limacharlie use dev-org)
```

You can also provide a `UID` (User ID) at login to use a *user-scoped* API
key, which carries the full set of permissions assigned to that user (see
**User Profile** in the web interface).

### Environment Variables

`LC_OID`, `LC_API_KEY`, and `LC_UID` can replace the values stored at login.
Environment variables are used when no other credentials are explicitly
provided.

### Credentials File

When using `limacharlie login`, credentials are stored in plain text at
`~/.limacharlie`:

```yaml
# Top-level / default credentials
api_key: xxx
oid: xxx
# Optional, only required for user-scoped API keys
uid: xxx

# Named environments, selected via "limacharlie use <environment>"
env:
  org-1:
    api_key: xxx
    oid: xxx
    # uid: xxx
  org-2:
    api_key: xxx
    oid: xxx
    # uid: xxx
```

If you edit this file by hand, preserve the original ownership and `0600`
permissions so that other users cannot read it. If storing plain-text
credentials on disk is unacceptable for your environment, use environment
variables instead.

## Docker

A Docker image with the latest tool is published at
<https://hub.docker.com/r/refractionpoint/limacharlie>:

```bash
docker run refractionpoint/limacharlie:latest whoami

# Or mount an existing local credentials file into the container
docker run -v "${HOME}/.limacharlie:/root/.limacharlie:ro" \
  refractionpoint/limacharlie:latest whoami
```

## SDK

The entry point for the SDK is the `Manager` object. It holds credentials
and is bound to a specific Organization.

You can authenticate `Manager` by passing an `oid` (and optionally a `uid`)
together with either a `secret_api_key` or a `jwt`. Alternatively, pass a
named `environment` from `limacharlie login`. If no credentials are
provided, `Manager` falls back to the default environment.

### Importing

```python
import limacharlie

YARA_SIG = 'https://raw.githubusercontent.com/Yara-Rules/rules/master/Malicious_Documents/Maldoc_PDF.yar'

# Create an instance of the SDK.
man = limacharlie.Manager()

# Manager.sensors() is a generator that paginates internally.
all_sensors = list(man.sensors())

# Select the first sensor.
sensor = all_sensors[0]

# Tag this sensor for 10 minutes.
sensor.tag('suspicious', ttl=60 * 10)

# Send a task to the sensor (unidirectional, no response collected).
sensor.task('os_processes')

# Send a YARA scan to the sensor for processes named "evil.exe".
sensor.task('yara_scan -e *evil.exe ' + YARA_SIG)
```

### Components

#### Manager

The general-purpose component for organization-level operations: querying
sensors, creating and removing Outputs, and so on.

#### Firehose

`Firehose` listens on a local port for LimaCharlie data. Internally it
creates a Syslog Output on LimaCharlie pointing at itself, and removes that
Output on shutdown. Incoming data is added to `firehose.queue` (a standard
`queue.Queue`) as it arrives.

It is a basic building block for automation against LimaCharlie.

#### Spout

`Spout` plays a similar role to `Firehose`, but does not require an open
listening port. Instead it streams data over HTTPS from
`stream.limacharlie.io`, which makes it work behind NATs and proxies.

A `Spout` is created automatically when `Manager` is instantiated with
`is_interactive=True` and an `inv_id`, in order to provide real-time
feedback from sensor tasking.

#### Sensor

The object returned by `manager.sensor(sensor_id)`.

It exposes `task`, `hostname`, `tag`, `untag`, `getTags`, and related
functions, and is the main way to interact with a specific sensor.

`task` sends a one-way task to a sensor; the response (if any) is not
collected. To interact with a sensor in real time, instantiate `Manager`
with `is_interactive=True` and use either `request` (returns a
`FutureResults` object) or `simpleRequest` (blocks until the response is
available).

#### Artifacts

`Artifacts` uploads
[Artifact Collection](../../5-integrations/extensions/limacharlie/artifact.md)
items to LimaCharlie without going through a sensor.

#### Payloads

`Payloads` manages the executable
[payloads](../../2-sensors-deployment/endpoint-agent/payloads.md) made
available to sensors.

#### Replay

`Replay` runs [Replay](../../5-integrations/services/replay.md) jobs to
re-evaluate
[D&R rules](../../3-detection-response/index.md) over historical data.

#### Search

`Search` performs an IOC search across multiple organizations.

#### SpotCheck

`SpotCheck` (also called Fleet Check) performs an active search — querying
sensors directly rather than indexed history — for various IOCs across an
organization's sensors.

#### Configs

`Configs` retrieves an organization's configuration as a config file, or
applies a config file to an organization. This is the foundation of the
Infrastructure-as-Code workflow in v4.

#### Webhook

`Webhook` is a reference implementation for handling webhooks emitted by
LimaCharlie, including verification of the shared-secret signature.

### Examples

#### Basic Manager Operations

Adapted from
[`samples/demo_manager.py`](https://github.com/refractionPOINT/python-limacharlie/blob/v4/samples/demo_manager.py).

```python
import limacharlie
import getpass
import json

if __name__ == "__main__":
    def debugPrint(msg):
        print(msg)

    man = limacharlie.Manager(
        oid=input('Enter OID: '),
        secret_api_key=getpass.getpass(prompt='Enter secret API key: '),
        print_debug_fn=debugPrint,
    )

    # Manager.sensors() is a generator that paginates internally.
    all_sensors = list(man.sensors())

    print("Got %d sensors." % len(all_sensors))

    print("First sensor %s has tags: %s" % (
        all_sensors[0].sid,
        all_sensors[0].getTags(),
    ))

    for sensor in all_sensors:
        if not sensor.isOnline():
            print("Sensor %s is offline, next..." % sensor.sid)
            continue
        print("Sensor info: %s" % json.dumps(sensor.getInfo(), indent=2))
        sensor.task('dir_list . *')
        break
```

#### Basic Firehose Operations

Adapted from
[`samples/demo_firehose.py`](https://github.com/refractionPOINT/python-limacharlie/blob/v4/samples/demo_firehose.py).

```python
import limacharlie
import getpass
import json
import signal
import sys

if __name__ == "__main__":
    def signal_handler(sig, frame):
        global fh
        print('You pressed Ctrl+C!')
        fh.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    def debugPrint(msg):
        print(msg)

    man = limacharlie.Manager(
        oid=input('Enter OID: '),
        secret_api_key=getpass.getpass(prompt='Enter secret API key: '),
        print_debug_fn=debugPrint,
    )

    fh = limacharlie.Firehose(
        man,
        input('Local Interface (e.g. 1.2.3.4:9424): '),
        'event',
        public_dest=input('Public Interface (or leave empty): ') or None,
        name='firehose_test',
    )

    while True:
        data = fh.queue.get()
        print(json.dumps(data, indent=2) + "\n\n")
```

#### Basic Spout Operations

Adapted from
[`samples/demo_spout.py`](https://github.com/refractionPOINT/python-limacharlie/blob/v4/samples/demo_spout.py).

```python
import limacharlie
import getpass
import json
import signal
import sys

if __name__ == "__main__":
    def signal_handler(sig, frame):
        global sp
        print('You pressed Ctrl+C!')
        sp.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    def debugPrint(msg):
        print(msg)

    man = limacharlie.Manager(
        oid=input('Enter OID: '),
        secret_api_key=getpass.getpass(prompt='Enter secret API key: '),
        print_debug_fn=debugPrint,
    )

    sp = limacharlie.Spout(man, 'event')

    while True:
        data = sp.queue.get()
        print(json.dumps(data, indent=2) + "\n\n")
```

#### Basic Interactive Sensor Operations

Adapted from
[`samples/demo_interactive_sensor.py`](https://github.com/refractionPOINT/python-limacharlie/blob/v4/samples/demo_interactive_sensor.py).

```python
import limacharlie
import getpass
import json
import uuid

if __name__ == "__main__":
    def debugPrint(msg):
        print(msg)

    print("Starting in interactive mode.")
    man = limacharlie.Manager(
        oid=input('Enter OID: '),
        secret_api_key=getpass.getpass(prompt='Enter secret API key: '),
        print_debug_fn=None,
        inv_id=str(uuid.uuid4()),
        is_interactive=True,
    )

    # is_interactive=True enables Sensor.request(), which returns a
    # FutureResults object you can poll for the sensor's response.

    sensors = list(man.sensors())
    print("Got %d sensors." % len(sensors))

    for sensor in sensors:
        print("Sensor info: %s" % sensor.getInfo())
        print("Asking for autoruns...")
        try:
            future = sensor.request('os_autoruns')
        except limacharlie.utils.LcApiException as e:
            if 'host not connected' in str(e):
                print("Offline, moving on...")
                continue
            raise

        responses = future.getNewResponses(timeout=10)
        if not responses:
            print("Never got a response.")
        else:
            print("Received: %s" % json.dumps(responses, indent=2))

    print("All done.")
```

#### Rules Config Syncing

Sample config files are available in the v4 branch at
[`limacharlie/sample_configs/`](https://github.com/refractionPOINT/python-limacharlie/tree/v4/limacharlie/sample_configs).

## Command Line Interface

Many of the SDK objects also expose command-line interfaces.

### Firehose

```bash
python -m limacharlie.Firehose 1.2.3.4:9424 event \
  -n firehose_test -t fh_test \
  --oid c82e5c17-d519-4ef5-a4ac-caa4a95d31ca
```

Listens on `1.2.3.4:9424` for incoming connections from LimaCharlie.
Receives only events from hosts tagged `fh_test`.

### Spout

```bash
python -m limacharlie.Spout event \
  --oid c82e5c17-d519-4ef5-a4ac-caa4a95d31ca
```

Behaves like Firehose, but instead of accepting an incoming connection it
streams data from `stream.limacharlie.io` over HTTPS. This means Spout
works through NATs and proxies and is more convenient for short-lived
ad-hoc output, though less reliable than a Firehose for very large volumes.

### Configs

```bash
limacharlie configs fetch --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca

limacharlie configs push --dry-run --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca
```

`fetch` writes the organization's configuration to a config file (default
`lc_conf.yaml`) in YAML format.

`push` uploads the rules in the config file to the organization. The
`--force` flag also removes active rules that are not present in the config
file. `--dry-run` simulates the sync and prints the changes that would be
made.

`--config` selects an alternate config file. `--api-key` reads the API key
from a file on disk (or from STDIN if `-` is given).

These capabilities are also available directly through the
`limacharlie.Configs` object.

The sync covers the common configurable surfaces. Flags such as
`--no-rules` and `--no-outputs` exclude individual sections; see
`limacharlie configs --help` for the full list. The `include` directive
lets you compose multiple config files together, which is convenient for
managing large rule sets.

### Spot Checks

```bash
python -m limacharlie.SpotCheck \
  --no-macos --no-linux --tags vip --file 'c:\\evil.exe'
```

Performs an organization-wide check for specific indicators of compromise.
Available as the `SpotCheck` object or as a CLI module. Supports many IOC
types including file names, directories, registry keys, file hashes, and
YARA signatures.

For full usage:

```bash
python -m limacharlie.SpotCheck --help
```

### Search

```bash
limacharlie search --help
```

Performs IOC searches across all locally configured organizations.

### Artifact Upload

```bash
limacharlie artifacts upload --help
```

Uploads
[Artifact Collection](../../5-integrations/extensions/limacharlie/artifact.md)
items directly to LimaCharlie from the CLI (no agent required).

### Artifact Download

```bash
limacharlie artifacts get_original --help
```

Downloads
[Artifact Collection](../../5-integrations/extensions/limacharlie/artifact.md)
items from LimaCharlie to the local filesystem.

### Replay

```bash
limacharlie replay --help
```

Runs [Replay](../../5-integrations/services/replay.md) jobs from the CLI.

### Detection & Response

```bash
limacharlie dr --help
```

Manages D&R rules from the CLI.

### Events & Detections

```bash
limacharlie events --help
limacharlie detections --help
```

Prints events or detections matching the given parameters to STDOUT.

### List Sensors

```bash
limacharlie sensors --selector '*'
```

Prints basic sensor information for all sensors matching the selector.

### Extension

```bash
limacharlie extension --help
```

Performs actions against
[Extensions](../../5-integrations/extensions/index.md) from the CLI.

### ARLs

```bash
limacharlie get-arl --help
```

Prints the data returned from the given
[ARL](../../8-reference/authentication-resource-locator.md). Example:

```bash
limacharlie get-arl -a [github,Yara-Rules/rules/email]
```
