# LimaCharlie SDK & CLI

## Go

The Go library is a simple abstraction to the [LimaCharlie.io REST API](https://api.limacharlie.io/). The REST API currently supports many more functions. If it's missing a function available in the REST API that you would like to use, let us know at support@limacharlie.io.

  * Repo - <https://github.com/refractionPOINT/go-limacharlie>




### Getting Started

#### Authentication

You can use Client Options to declare your client/org, or you can use environment variables.

**Using Environment Variables:**

  * `LC_OID`: Organization ID

  * `LC_API_KEY`: your LC API KEY

  * `LC_UID`: optional, your user ID




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


**Using Client Options:**


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


### SDK

#### Examples


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


## Python

The Python library is a simple abstraction to the [LimaCharlie.io REST API](https://api.limacharlie.io/). The REST API currently supports many more functions. If it's missing a function available in the REST API that you would like to use, let us know at support@limacharlie.io.

  * Repo - <https://github.com/refractionpoint/python-limacharlie>




### Getting Started

#### Installing

##### PyPi (pip)

The library and the CLI is available as a Python package on PyPi (<https://pypi.org/project/limacharlie/>). It can be installed using pip as shown below.


    pip install limacharlie

##### Docker Image

In addition to the PyPi distribution we also offer a pre-built Docker image on DockerHub (<https://hub.docker.com/r/refractionpoint/limacharlie>).


    docker run refractionpoint/limacharlie:latest whoami

    # Using a specific version (Docker image tag matches the library version)
    docker run refractionpoint/limacharlie:4.9.13 whoami

    # If you already have a credential file locally, you can mount it inside the Docker container
    docker run -v ${HOME}/.limacharlie:/root/.limacharlie:ro refractionpoint/limacharlie:latest whoami

#### Credentials

Authenticating to use the SDK / CLI can be done in a few ways.

**Option 1 - Logging In**
The simplest is to login to an Organization using an [API key](../Platform%20Management/Access%20and%20Permissions/api-keys.md).

Use `limacharlie login` to store credentials locally. You will need an `OID` (Organization ID) and an API key, and (optionally) a `UID` (User ID), all of which you can get from the Access Management --> REST API section of the web interface.

The login interface supports named environments, or a default one used when no environment is selected.

To list available environments:


    limacharlie use

Setting a given environment in the current shell session can be done like this:


    limacharlie use my-dev-org

You can also specify a `UID` (User ID) during login to use a _user_ API key representing
the total set of permissions that user has (see User Profile in the web interface).

**Option 2 - Environment Variables**
You can use the `LC_OID` and `LC_API_KEY` and `LC_UID` environment variables to replace the values used logging in. The environment variables will be used if no other credentials are specified.

### SDK

The root of the functionality in the SDK is from the `Manager` object. It holds the credentials and is tied to a specific LimaCharlie Organization.

You can authenticate the `Manager` using an `oid` (and optionally a `uid`), along with either a `secret_api_key` or `jwt` directly. Alternatively you can just use an environment name (as specified in `limacharlie login`). If no creds are provided, the `Manager` will try to use the default environment and credentials.

#### Importing


    import limacharlie

    YARA_SIG = 'https://raw.githubusercontent.com/Yara-Rules/rules/master/Malicious_Documents/Maldoc_PDF.yar'

    # Create an instance of the SDK.
    mgr = limacharlie.Manager()

    # Get a list of all the sensors in the current Organization.
    all_sensors = mgr.sensors()

    # Select the first sensor in the list.
    sensor = all_sensors[0]

    # Tag this sensor with a tag for 10 minutes.
    sensor.tag( 'suspicious', ttl = 60 * 10 )

    # Send a task to the sensor (unidirectionally, not expecting a response).
    sensor.task( 'os_processes' )

    # Send a yara scan to that sensor for processes "evil.exe".
    sensor.task( 'yara_scan -e *evil.exe ' + YARA_SIG )


#### Use of gevent

Note that the SDK uses the `gevent` package which sometimes has issues with other
packages that operate at a low level in python. For example, Jupyter notebooks
may see freezing on importing `limacharlie` and require a tweak to load:


    {
     "display_name": "IPython 2 w/gevent",
     "language": "python",
     "argv": [
      "python",
      "-c", "from gevent.monkey import patch_all; patch_all(thread=False); from ipykernel.kernelapp import main; main()",
      "-f",
      "{connection_file}"
     ]
    }


### Components

#### Manager

This is a the general component that provides access to the managing functions of the API like querying sensors online, creating and removing Outputs etc.

#### Firehose

The `Firehose` is a simple object that listens on a port for LimaCharlie.io data. Under the hood it creates a Syslog Output on limacharlie.io pointing to itself and removes it on shutdown. Data from limacharlie.io is added to `firehose.queue` (a `gevent Queue`) as it is received.

It is a basic building block of automation for limacharlie.io.

#### Spout

Much like the `Firehose`, the Spout receives data from LimaCharlie.io, the difference
is that the `Spout` does not require opening a local port to listen actively on. Instead
it leverages `stream.limacharlie.io` to receive the data stream over HTTPS.

A `Spout` is automatically created when you instantiate a `Manager` with the
`is_interactive = True` and `inv_id = XXXX` arguments in order to provide real-time
feedback from tasking sensors.

#### Sensor

This is the object returned by `manager.sensor( sensor_id )`.

It supports a `task`, `hostname`, `tag`, `untag`, `getTags` and more functions. This
is the main way to interact with a specific sensor.

The `task` function sends a task to the sensor unidirectionally, meaning it does not
receive the response from the sensor (if any). If you want to interact with a sensor
in real-time, use the interactive mode (as mentioned in the `Spout`) and use either
the `request` function to receive replies through a `FutureResults` object or the
`simpleRequest` to wait for the response and receive it as a return value.

#### Artifacts

The `Artifacts` is a helpful class to upload [artifacts](../Add-Ons/Services/addons-services-dumper.md) to LimaCharlie without going through a sensor.

#### Extensions

The `Extensions` can be used to subscribe to and manage extensions within your org.


    import limacharlie
    from limacharlie import Extension

    mgr = limacharlie.Manager()
    ext = Extension(mgr)
    ext.subscribe('binlib')


#### Payloads

The `Payloads` can be used to manage various executable [payloads](../Sensors/Endpoint%20Agent/payloads.md) accessible to sensors.

#### Replay

The `Replay` object allows you to interact with [Replay](../Add-Ons/Services/replay.md) jobs managed by LimaCharlie. These allow you to re-run [D&R Rules](../Detection%20and%20Response/writing-and-testing-rules.md) on historical data.

Sample command line to query one sensor:


    limacharlie-replay --sid 9cbed57a-6d6a-4af0-b881-803a99b177d9 --start 1556568500 --end 1556568600 --rule-content ./test_rule.txt


Sample command line to query an entire organization:


    limacharlie-replay --entire-org --start 1555359000 --end 1556568600 --rule-name my-rule-name


#### Search

The `Search` object allows you to perform an IOC search across multiple organizations.

#### SpotCheck

The `SpotCheck` object (sometimes called Fleet Check) allows you to manage an active (query sensors directly as opposed to searching on indexed historical data) search for various IOCs on an organization's sensors.

#### Configs

The `Configs` is used to retrieve an organization's configuration as a config file, or apply
an existing config file to an organization. This is the concept of Infrastructure as Code.

#### Webhook

The `Webhook` object demonstrates handling [webhooks emitted by the LimaCharlie cloud](../Sensors/Adapters/Adapter%20Tutorials/tutorial-creating-a-webhook-adapter.md), including verifying the shared-secret signing of the webhooks.

### Examples:

  * [Basic Manager Operations](https://github.com/refractionPOINT/python-limacharlie/blob/master/samples/demo_manager.py)

  * [Basic Firehose Operations](https://github.com/refractionPOINT/python-limacharlie/blob/master/samples/demo_firehose.py)

  * [Basic Spout Operations](https://github.com/refractionPOINT/python-limacharlie/blob/master/samples/demo_spout.py)

  * [Basic Integrated Operations](https://github.com/refractionPOINT/python-limacharlie/blob/master/samples/demo_interactive_sensor.py)

  * [Sample Configs](https://github.com/refractionPOINT/python-limacharlie/tree/master/limacharlie/sample_configs)




### Command Line Interface

Many of the objects available as part of the LimaCharlie Python SDK also support various command line interfaces.

#### Query

[LimaCharlie Query Language (LCQL)](../Detection%20and%20Response/LimaCharlie%20Query%20Language/lcql-examples.md) provides a flexible, intuitive and interactive way to explore your data in LimaCharlie.


    limacharlie query --help

#### ARLs

[Authenticated Resource Locators (ARLs)](../Add-Ons/Reference/reference-authentication-resource-locator.md) describe a way to specify access to a remote resource, supporting many methods, including authentication data, and all that within a single string.

ARLs can be used in the [YARA manager](../Add-Ons/Extensions/LimaCharlie%20Extensions/ext-yara-manager.md) to import rules from GitHub repositories and other locations.

Testing an ARL before applying it somewhere can be helpful to shake out access or authentication errors beforehand. You can test an ARL and see what files are fetched, and their contents, by running the following command:


    limacharlie get-arl -a [github,Yara-Rules/rules/email]

#### Firehose

Listens on interface `1.2.3.4`, port `9424` for incoming connections from LimaCharlie.io.
Receives only events from hosts tagged with `fh_test`.


    python -m limacharlie.Firehose 1.2.3.4:9424 event -n firehose_test -t fh_test --oid c82e5c17-d519-4ef5-a4ac-caa4a95d31ca

#### Spout

Behaves similarly to the Firehose, but instead of listening from an internet accessible port, it connects to the `stream.limacharlie.io` service to stream the output over HTTPS. This means the Spout allows you to get ad-hoc output like the Firehose, but it also works through NATs and proxies.

It is MUCH more convenient for short term ad-hoc outputs, but it is less reliable than a Firehose for very large amounts of data.


    python -m limacharlie.Spout event --oid c82e5c17-d519-4ef5-a4ac-caa4a95d31ca

#### Configs

The `fetch` command will get a list of the Detection & Response rules in your
organization and will write them to the config file specified or the default
config file `lc_conf.yaml` in YAML format.


    limacharlie configs fetch --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca`

Then `push` can upload the rules specified in the config file (or the default one)
to your organization. The optional `--force` argument will remove active rules not
found in the config file. The `--dry-run` simulates the sync and displays the changes
that would occur.

The `--config` allows you to specify an alternate config file and the `--api-key` allows
you to specify a file on disk where the API should be read from (otherwise, of if `-` is
specified as a file, the API Key is read from STDIN).


    limacharlie configs push --dry-run --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca --config /path/to/template.yaml --all --ignore-inaccessible

All these capabilities are also supported directly by the `limacharlie.Configs` object.

The Sync functionality currently supports all common useful configurations. The `--no-rules` and `--no-outputs` flags can be used to ignore one or the other in config files and sync. Additional flags are also supported, see `limacharlie configs --help`.

To understand better the config format, do a `fetch` from your organization. Notice the use of the `include`
statement. Using this statement you can combine multiple config files together, making
it ideal for the management of complex rule sets and their versioning.

#### Spot Checks

Used to perform Organization-wide checks for specific indicators of compromise. Available as a custom API `SpotCheck` object or as a module from the command line. Supports many types of IoCs like file names, directories, registry keys, file hashes and YARA signatures.


    python -m limacharlie.SpotCheck --no-macos --no-linux --tags vip --file c:\\evil.exe`

For detailed usage:


    python -m limacharlie.SpotCheck --help

#### Search

Shortcut utility to perform IOC searches across all locally configured organizations.


    limacharlie search --help

#### Extensions

Shortcut utility to manage extensions.


    limacharlie extension --help

#### Artifact Upload

Shortcut utility to upload and retrieve [Artifacts](../Add-Ons/Services/addons-services-dumper.md) within LimaCharlie with just the CLI (no agent).


    limacharlie artifacts --help

#### Artifact Download

Shortcut utility to download [Artifact Collection](../Add-Ons/Services/addons-services-dumper.md) in LimaCharlie locally.


    limacharlie artifacts get_original --help

#### Replay

Shortcut utility to perform [Replay](../Add-Ons/Services/replay.md) jobs from the CLI.


    limacharlie replay --help

#### Detection & Response

Shortcut utility to manage Detection and Response rules over the CLI.


    limacharlie dr --help

#### Events & Detections

Print out to STDOUT events or detections matching the parameter.


    limacharlie events --help
    limacharlie detections --help

#### List Sensors

Print out all basic sensor information for all sensors matching the [selector](../Sensors/Reference/reference-sensor-selector-expressions.md).


    limacharlie sensors --selector 'plat == windows'

#### Invite Users

Invite single or multiple users to LimaCharlie. Invited users will be sent an email to confirm their address, enable the account and create a new password.

Keep in mind that this actions operates in the user context which means you need to use user scoped API key. For more information on how to obtain one, see <https://docs.limacharlie.io/apidocs/introduction#getting-a-jwt>

Invite a single user:


    limacharlie users invite --email=user1@example.com

Invite multiple users:


    limacharlie users invite --email=user1@example.com,user2@example.com,user3@example.com

Invite multiple users from new line delimited entries in a text file:


    cat users_to_invite.txt
    user1@example.com
    user2@example.com
    user3@example.com


    limacharlie users invite --file=users_to_invite.txt

In LimaCharlie, an Organization ID is a unique identifier assigned to each tenant or customer account. It distinguishes different organizations within the platform, enabling LimaCharlie to manage resources, permissions, and data segregation securely. The Organization ID ensures that all telemetry, configurations, and operations are kept isolated and specific to each organization, allowing for multi-tenant support and clear separation between different customer environments.




Command-line Interface

In LimaCharlie, an Organization represents a tenant within the SecOps Cloud Platform, providing a self-contained environment to manage security data, configurations, and assets independently. Each Organization has its own sensors, detection rules, data sources, and outputs, offering complete control over security operations. This structure enables flexible, multi-tenant setups, ideal for managed security providers or enterprises managing multiple departments or clients.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

LimaCharlie Extensions allow users to expand and customize their security environments by integrating third-party tools, automating workflows, and adding new capabilities. Organizations subscribe to Extensions, which are granted specific permissions to interact with their infrastructure. Extensions can be private or public, enabling tailored use or broader community sharing. This framework supports scalability, flexibility, and secure, repeatable deployments.

Infrastructure as Code (IaC) automates the management and provisioning of IT infrastructure using code, making it easier to scale, maintain, and deploy resources consistently. In LimaCharlie, IaC allows security teams to deploy and manage sensors, rules, and other security infrastructure programmatically, ensuring streamlined, repeatable configurations and faster response times, while maintaining infrastructure-as-code best practices in cybersecurity operations.
