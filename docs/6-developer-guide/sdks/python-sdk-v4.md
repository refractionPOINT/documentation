# LimaCharlie Python SDK v4

!!! warning "Deprecated"
    Version 4 of the LimaCharlie Python SDK is deprecated and will be removed
    in a future release. Use the [Python SDK](python-sdk.md) (v5) for new
    code. This page stays available for users that maintain existing v4
    integrations. v4 and v5 use the same LimaCharlie REST API, so your code
    has the same capabilities with each version.

## Overview

The v4 Python SDK is a thin abstraction of the LimaCharlie REST API. The
`Manager` object is at its center. The REST API supports more functions
than the SDK. If v4 does not expose a REST endpoint that you need, migrate
to v5 instead of an extension to v4.

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

The SDK and the CLI support several ways to give credentials.

### Logging In

The most direct method is to log in with an
[API key](../../7-administration/access/api-keys.md):

```bash
limacharlie login
```

The CLI prompts you for an `OID` (Organization ID, in UUID format) and an
API key. You get both from the **REST API** section of the web interface.

The login flow supports named environments. The CLI stores credentials
under a name that you choose. It uses one set as the default when you
select no environment.

To list available environments:

```bash
limacharlie use
```

To activate a named environment in the current shell session:

```bash
. <(limacharlie use dev-org)
```

You can also give a `UID` (User ID) at login to use a *user-scoped* API
key. This key has all the permissions of that user. See **User Profile** in
the web interface.

### Environment Variables

`LC_OID`, `LC_API_KEY`, and `LC_UID` can replace the values that you store
at login. The SDK uses the environment variables when you give no other
credentials.

### Credentials File

When you use `limacharlie login`, the CLI stores credentials in plain text
at `~/.limacharlie`:

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

If you edit this file by hand, keep the original ownership and the `0600`
permissions. Other users then cannot read the file. If your environment
does not allow plain-text credentials on disk, use environment variables
instead.

## Docker

The latest tool is available as a Docker image at
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

To authenticate `Manager`, give an `oid` (and optionally a `uid`) with
either a `secret_api_key` or a `jwt`. As an alternative, give a named
`environment` from `limacharlie login`. If you give no credentials,
`Manager` uses the default environment.

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

The general-purpose component for operations at the organization level:
queries of sensors, creation and removal of Outputs, and more.

#### Firehose

`Firehose` listens on a local port for LimaCharlie data. It creates a
Syslog Output on LimaCharlie that points at itself, and it removes that
Output at shutdown. It adds incoming data to `firehose.queue` (a standard
`queue.Queue`) as the data arrives.

It is a basic component for automation with LimaCharlie.

#### Spout

`Spout` has a similar function to `Firehose`, but it does not need an open
listening port. It streams data over HTTPS from `stream.limacharlie.io`.
Thus it works behind NATs and proxies.

When you create a `Manager` with `is_interactive=True` and an `inv_id`, the
SDK creates a `Spout` automatically. The `Spout` gives real-time feedback
from sensor tasking.

#### Sensor

The object returned by `manager.sensor(sensor_id)`.

It exposes `task`, `hostname`, `tag`, `untag`, `getTags`, and related
functions. It is the primary interface to a specific sensor.

`task` sends a one-way task to a sensor. It does not collect the response.
To interact with a sensor in real time, create a `Manager` with
`is_interactive=True`. Then use `request` (it returns a `FutureResults`
object) or `simpleRequest` (it blocks until the response is available).

#### Artifacts

`Artifacts` uploads
[Artifact Collection](../../5-integrations/extensions/limacharlie/artifact.md)
items to LimaCharlie without a sensor.

#### Payloads

`Payloads` manages the executable
[payloads](../../2-sensors-deployment/endpoint-agent/payloads.md) that are
available to sensors.

#### Replay

`Replay` runs [Replay](../../5-integrations/services/replay.md) jobs to
re-evaluate
[D&R rules](../../3-detection-response/index.md) over historical data.

#### Search

`Search` does an IOC search across more than one organization.

#### SpotCheck

`SpotCheck` (also called Fleet Check) does an active search for IOCs across
the sensors of an organization. It queries the sensors directly and not the
indexed history.

#### Configs

`Configs` gets the configuration of an organization as a config file. It
can also apply a config file to an organization. It is the base of the
Infrastructure-as-Code workflow in v4.

#### Webhook

`Webhook` is a reference implementation that handles the webhooks that
LimaCharlie sends. It also checks the shared-secret signature.

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

This command listens on `1.2.3.4:9424` for incoming connections from
LimaCharlie. It receives only events from hosts with the `fh_test` tag.

### Spout

```bash
python -m limacharlie.Spout event \
  --oid c82e5c17-d519-4ef5-a4ac-caa4a95d31ca
```

Spout operates like Firehose, but it does not accept an incoming
connection. It streams data from `stream.limacharlie.io` over HTTPS. Thus
Spout works through NATs and proxies, and it is more convenient for
short-lived ad-hoc output. But it is less reliable than a Firehose for very
large volumes.

### Configs

```bash
limacharlie configs fetch --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca

limacharlie configs push --dry-run --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca
```

`fetch` writes the configuration of the organization to a config file in
YAML format. The default file is `lc_conf.yaml`.

`push` uploads the rules in the config file to the organization. The
`--force` flag also removes active rules that are not present in the config
file. `--dry-run` simulates the sync and prints the changes that the sync
will make.

`--config` selects an alternate config file. `--api-key` reads the API key
from a file on disk (or from STDIN if `-` is given).

These capabilities are also available directly through the
`limacharlie.Configs` object.

The sync covers the common configurable surfaces. Flags such as
`--no-rules` and `--no-outputs` exclude single sections. For the full list,
see `limacharlie configs --help`. The `include` directive combines more
than one config file. This is convenient for large rule sets.

### Spot Checks

```bash
python -m limacharlie.SpotCheck \
  --no-macos --no-linux --tags vip --file 'c:\\evil.exe'
```

This command checks all of an organization for specific indicators of
compromise. It is available as the `SpotCheck` object or as a CLI module.
It supports many IOC types: file names, directories, registry keys, file
hashes, and YARA signatures.

For full usage:

```bash
python -m limacharlie.SpotCheck --help
```

### Search

```bash
limacharlie search --help
```

Does IOC searches across all organizations that you configured locally.

### Artifact Upload

```bash
limacharlie artifacts upload --help
```

Uploads
[Artifact Collection](../../5-integrations/extensions/limacharlie/artifact.md)
items directly to LimaCharlie from the CLI. No sensor is necessary.

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

Prints the events or detections that match the given parameters to STDOUT.

### List Sensors

```bash
limacharlie sensors --selector '*'
```

Prints basic sensor information for each sensor that matches the selector.

### Extension

```bash
limacharlie extension --help
```

Does actions on
[Extensions](../../5-integrations/extensions/index.md) from the CLI.

### ARLs

```bash
limacharlie get-arl --help
```

Prints the data that the given
[ARL](../../8-reference/authentication-resource-locator.md) returns. Example:

```bash
limacharlie get-arl -a [github,Yara-Rules/rules/email]
```
