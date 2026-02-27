#### Authentication

You can use Client Options to declare your client/org, or you can use environment variables.

**Using Environment Variables:**

* `LC_OID`: Organization ID
* `LC_API_KEY`: your LC API KEY
* `LC_UID`: optional, your user ID

```python
package main

import (
	"fmt"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    client, err := limacharlie.NewClientFromLoader(limacharlie.ClientOptions{}, nil, &limacharlie.EnvironmentClientOptionLoader{})
    if err != nil {
        fmt.Println(err)
    }

    org, _ := limacharlie.NewOrganization(client)
    fmt.Printf("Hello, this is %s", org.GetOID())
}
```

**Using Client Options:**

```python
package main

import (
	"fmt"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    clientOptions = limacharlie.ClientOptions{
        OID: "MY_OID",
        APIKey: "MY_API_KEY",
        UID: "MY_UID",
    }
    org, _ := limacharlie.NewOrganizationFromClientOptions(clientOptions, nil)
    fmt.Printf("Hello, this is %s", org.GetOID())
}
```

### SDK

#### Examples

```python
package main

import (
	"fmt"

	"github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
    client, err := limacharlie.NewClientFromLoader(limacharlie.ClientOptions{}, nil, &limacharlie.EnvironmentClientOptionLoader{})
    if err != nil {
        fmt.Println(err)
    }

    org, _ := limacharlie.NewOrganization(client)

    // List all sensors
    sensors, err := org.ListSensors()
    if err != nil {
        fmt.Println(err)
    }
    for sid, sensor := range sensors {
        fmt.Printf("%s - %s", sid, sensor.Hostname)
    }

    // List D&R rules from Hive
    hiveClient := limacharlie.NewHiveClient(org)
    rules, _ := hiveClient.List(limacharlie.HiveArgs{
        HiveName:     "dr-general",
        PartitionKey:  org.GetOID(),
    })
    for rule_name, _ := range rules {
        fmt.Println(rule_name)
    }

    // Add D&R rule to Hive
    enabled := true
    case_sensitive := false
    if _, err := hiveClient.Add(limacharlie.HiveArgs{
        HiveName:     "dr-general",
        PartitionKey: org.GetOID(),
        Key:          "test_rule_name",
        Enabled:      &enabled,
        Data: limacharlie.Dict{
            "detect": limacharlie.Dict{
                "event":            "NEW_PROCESS",
                "op":               "is",
                "path":             "event/COMMAND_LINE",
                "value":            "whoami",
                "case sensitive":   &case_sensitive,
            },
            "respond": []limacharlie.Dict{{
                "action": "report",
                "name":   "whoami detection",
            }},
        },
    }); err != nil {
        fmt.Println(err)
    }

    // List extensions
    extensions, _ := org.Extensions()
    for _, extension_name := range extensions {
        fmt.Println(extension_name)
    }

    // Subscribe to extension
    subscription_request := org.SubscribeToExtension("binlib")
    if subscription_request != nil {
        fmt.Println(subscription_request)
    }

    // List payloads
    payloads, _ := org.Payloads()
    for payload, _ := range payloads {
        fmt.Println(payload)
    }

    // List installation keys
    installation_keys, _ := org.InstallationKeys()
    for _, key := range installation_keys {
        fmt.Println(key.Description)
    }

    // Create installation key
    key_request, _ := org.AddInstallationKey(InstallationKey{
		Description: "my-test-key",
		Tags:        []string{"tag", "another-tag"},
	})

}
```

## Python

The Python library is a simple abstraction to the [LimaCharlie.io REST API](https://api.limacharlie.io/static/swagger/). The REST API currently supports many more functions. If it's missing a function available in the REST API that you would like to use, let us know at support@limacharlie.io.

* Repo - <https://github.com/refractionpoint/python-limacharlie>

### Getting Started

#### Installing

##### PyPi (pip)

The library and the CLI is available as a Python package on PyPi (<https://pypi.org/project/limacharlie/>). It can be installed using pip as shown below.

```bash
pip install limacharlie
```

##### Docker Image

In addition to the PyPi distribution we also offer a pre-built Docker image on DockerHub (<https://hub.docker.com/r/refractionpoint/limacharlie>).

```bash
docker run refractionpoint/limacharlie:latest whoami

# Using a specific version (Docker image tag matches the library version)
docker run refractionpoint/limacharlie:5.0.0 whoami

# If you already have a credential file locally, you can mount it inside the Docker container
docker run -v ${HOME}/.limacharlie:/root/.limacharlie:ro refractionpoint/limacharlie:latest whoami
```

#### Credentials

Authenticating to use the SDK / CLI can be done in a few ways.

**Option 1 - Logging In**
 The simplest is to login to an Organization using an [API key](../7-administration/access/api-keys.md).

Use `limacharlie auth login` to store credentials locally. You will need an `OID` (Organization ID) and an API key, and (optionally) a `UID` (User ID), all of which you can get from the Access Management --> REST API section of the web interface.

The login interface supports named environments, or a default one used when no environment is selected.

To list available organizations:

```bash
limacharlie auth list-orgs
```

Setting a given organization in the current shell session can be done like this:

```bash
limacharlie auth use-org my-dev-org
```

You can also specify a `UID` (User ID) during login to use a *user* API key representing
 the total set of permissions that user has (see User Profile in the web interface).

**Option 2 - Environment Variables**
 You can use the `LC_OID` and `LC_API_KEY` and `LC_UID` environment variables to replace the values used logging in. The environment variables will be used if no other credentials are specified.

### SDK

The SDK is organized around two main objects: `Client` (handles authentication and HTTP) and `Organization` (provides access to all org-scoped operations).

You can authenticate the `Client` using an `oid` and `api_key` directly, or use environment variables and config file credentials. If no credentials are provided, the `Client` resolves them from the environment (as configured via `limacharlie auth login`).

#### Importing

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.sensor import Sensor

YARA_SIG = 'https://raw.githubusercontent.com/Yara-Rules/rules/master/Malicious_Documents/Maldoc_PDF.yar'

# Create an instance of the SDK.
client = Client()
org = Organization(client)

# Get a list of all the sensors in the current Organization.
all_sensors = list(org.list_sensors())

# Select the first sensor.
sensor = Sensor(org, all_sensors[0]["sid"])

# Tag this sensor with a tag for 10 minutes.
sensor.add_tag('suspicious', ttl=60 * 10)

# Send a task to the sensor (unidirectionally, not expecting a response).
sensor.task('os_processes')

# Send a yara scan to that sensor for processes "evil.exe".
sensor.task('yara_scan -e *evil.exe ' + YARA_SIG)
```

### Components

#### Client

The `Client` handles HTTP communication with the LimaCharlie API, including JWT generation/refresh, retry with exponential backoff, and rate limit awareness. Import from `limacharlie.client`.

#### Organization

The `Organization` is the main entry point for all org-scoped operations: listing sensors, managing rules, accessing hives, outputs, users, extensions, and more. Import from `limacharlie.sdk.organization`.

#### Sensor

A `Sensor` is created with `Sensor(org, sid)`.

It supports `task`, `hostname`, `add_tag`, `remove_tag`, `get_tags`, `isolate`, `rejoin`, and more. This is the main way to interact with a specific sensor. Import from `limacharlie.sdk.sensor`.

The `task` function sends a task to the sensor unidirectionally, meaning it does not
 receive the response from the sensor (if any).

#### Firehose

The `Firehose` is a TLS push-mode streaming listener. Under the hood it creates an Output on limacharlie.io pointing to itself and removes it on shutdown. Import from `limacharlie.sdk.firehose`.

#### Spout

Much like the `Firehose`, the `Spout` receives data from LimaCharlie.io, the difference
 is that the `Spout` does not require opening a local port to listen actively on. Instead
 it leverages `stream.limacharlie.io` to receive the data stream over HTTPS. Import from `limacharlie.sdk.spout`.

#### Hive

The `Hive` provides access to LimaCharlie's key-value configuration store. Used for D&R rules, secrets, playbooks, and more. Import from `limacharlie.sdk.hive`.

#### Extensions

The `Extensions` class manages extension subscriptions and requests.

```python
from limacharlie.client import Client
from limacharlie.sdk.organization import Organization
from limacharlie.sdk.extensions import Extensions

client = Client()
org = Organization(client)
ext = Extensions(org)
ext.subscribe('binlib')
```

#### Search

The `Search` object allows you to execute LCQL queries, validate queries, estimate costs, and manage saved queries. Import from `limacharlie.sdk.search`.

#### Replay

The `Replay` object allows you to interact with [Replay](../5-integrations/services/replay.md) jobs managed by LimaCharlie. These allow you to re-run D&R Rules on historical data. Import from `limacharlie.sdk.replay`.

#### Artifacts

The `Artifacts` class is used to upload, list, and download artifacts. Import from `limacharlie.sdk.artifacts`.

#### Payloads

The `Payloads` can be used to manage various executable [payloads](../2-sensors-deployment/endpoint-agent/payloads.md) accessible to sensors.

#### Configs

The `Configs` is used to retrieve an organization's configuration as a config file, or apply
 an existing config file to an organization. This is the concept of Infrastructure as Code. Import from `limacharlie.sdk.configs`.

### Examples:

* [Sample Configs](https://github.com/refractionPOINT/python-limacharlie/tree/master/limacharlie/sample_configs)

### Command Line Interface

The CLI uses a `limacharlie <noun> <verb>` command pattern. Every command supports `--help` for detailed usage and `--ai-help` for AI-optimized explanations.

#### Search / Query

[LimaCharlie Query Language (LCQL)](../4-data-queries/lcql-examples.md) provides a flexible, intuitive and interactive way to explore your data in LimaCharlie.

```bash
limacharlie search --help
```

#### ARLs

[Authenticated Resource Locators (ARLs)](../8-reference/authentication-resource-locator.md) describe a way to specify access to a remote resource, supporting many methods, including authentication data, and all that within a single string.

ARLs can be used in the [YARA manager](../5-integrations/extensions/limacharlie/yara-manager.md) to import rules from GitHub repositories and other locations.

Testing an ARL before applying it somewhere can be helpful to shake out access or authentication errors beforehand. You can test an ARL and see what files are fetched, and their contents, by running the following command:

```bash
limacharlie arl get -a [github,Yara-Rules/rules/email]
```

#### Streaming

Stream events, detections, or audit logs in real-time. Uses pull-mode spouts (HTTPS) or push-mode firehose listeners (TLS).

```bash
# Stream events (pull-mode via stream.limacharlie.io, works through NATs and proxies)
limacharlie stream events
limacharlie stream events --tag server

# Stream detections
limacharlie stream detections

# Stream audit logs
limacharlie stream audit
```

#### Sync (Infrastructure as Code)

The `pull` command will fetch the organization configuration and write it to a local YAML file.

```bash
limacharlie sync pull --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca
```

Then `push` can upload the configuration specified in the YAML file to your organization. The `--dry-run` simulates the sync and displays the changes that would occur.

```bash
limacharlie sync push --dry-run --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca --config /path/to/template.yaml
```

All these capabilities are also supported directly by the `Configs` SDK class (`limacharlie.sdk.configs`).

The Sync functionality supports all common useful configurations. Use the hive flags (`--hive-dr-general`, `--hive-fp`, `--outputs`, etc.) to control which resource types are synced. See `limacharlie sync --help` for all options.

To understand better the config format, do a `pull` from your organization. Notice the use of the `include`
 statement. Using this statement you can combine multiple config files together, making
 it ideal for the management of complex rule sets and their versioning.

#### Spot Checks

Used to perform Organization-wide checks for specific indicators of compromise. Supports many types of IoCs like file names, directories, registry keys, file hashes and YARA signatures.

```bash
limacharlie spotcheck --help
```

#### Search

Shortcut utility to perform IOC searches across all locally configured organizations.

```bash
limacharlie search --help
```

#### Extensions

Shortcut utility to manage extensions.

```bash
limacharlie extension --help
```

#### Artifacts

Shortcut utility to upload, list, and download Artifacts within LimaCharlie.

```bash
limacharlie artifact --help
```

#### Replay

Shortcut utility to perform [Replay](../5-integrations/services/replay.md) jobs from the CLI.

```bash
limacharlie replay --help
```

#### Detection & Response

Shortcut utility to manage Detection and Response rules over the CLI.

```bash
limacharlie dr --help
```

#### Events & Detections

Print out to STDOUT events or detections matching the parameter.

```bash
limacharlie event --help
limacharlie detection --help
```

#### List Sensors

Print out all basic sensor information for all sensors matching the [selector](../8-reference/sensor-selector-expressions.md).

```bash
limacharlie sensor list --selector 'plat == windows'
```

#### Add Users

Add single or multiple users to a LimaCharlie organization. Added users will be sent an email to confirm their address, enable the account and create a new password.

Keep in mind that this action operates in the user context which means you need to use a user scoped API key. For more information on how to obtain one, see <https://api.limacharlie.io/static/swagger/#getting-a-jwt>

Add a single user:

```bash
limacharlie user add --email user1@example.com
```

Add multiple users:

```bash
limacharlie user add --email user1@example.com,user2@example.com,user3@example.com
```

Add multiple users from new line delimited entries in a text file:

```bash
cat users_to_add.txt
user1@example.com
user2@example.com
user3@example.com
```

```bash
limacharlie user add --file users_to_add.txt
```
