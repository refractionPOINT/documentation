[![LimaCharlie](https://cdn.document360.io/logo/84ec2311-0e05-4c58-90b9-baa9c041d22b/a8f5c28d58ea4df0b59badd4cebcc541-Logo_Blue.png)](/)

* [LimaCharlie Log In](https://app.limacharlie.io)

* v2

  + [v1 Deprecated](/v1/docs "v1")
  + [v2](/docs "v2")

Contents x

* [Getting Started](what-is-limacharlie)
* [Sensors](installation-keys)
* [Events](event-schemas)
* [Query Console](query-console-ui)
* [Detection and Response](replay)
* [Platform Management](limacharlie-sdk)
* [Outputs](output-allowlisting)
* [Add-Ons](developer-grant-program)
* [Tutorials](reporting)
* [FAQ](faq-general)
* Release Notes
* [Connecting](mcp-server)

[Powered by![Document360](https://cdn.document360.io/static/images/document360-logo.svg)](https://document360.com/powered-by-document360/?utm_source=docs&utm_medium=footer&utm_campaign=poweredbylogo)

---

Endpoint Agent Commands

* 18 Apr 2025
* 3 Minutes to read

Share this

* Print
* Share
* Dark

  Light

Contents

# Endpoint Agent Commands

* Updated on 18 Apr 2025
* 3 Minutes to read

* Print
* Share
* Dark

  Light

---

Article summary

Did you find this summary helpful?

Thank you for your feedback!

Endpoint Agent commands offer a safe way to interact with a Sensor's host either for investigation, management, or threat mitigation purposes.

## Sending Commands

Commands can be sent to Sensors via:

* Manually using the Console of a sensor in the [web application](https://app.limacharlie.io).
* Manually using the [CLI](https://github.com/refractionPOINT/python-limacharlie)
* Programmatically in the response action of a [Detection & Response](/v2/docs/detection-and-response) rule, via the `task` action.
* Programmatically using the [REST API](https://doc.limacharlie.io/docs/api/b3A6MTk2NDI0OQ-task-sensor)

Sensor REPort/REPly Events

Regardless of which you choose, sent commands will be acknowledged immediately with an empty response, followed by a `CLOUD_NOTIFICATION` event being sent by the sensor. The content of command outputs are delivered as sensor [events](/v2/docs/endpoint-agent-events-overview) suffixed with `_REP`, depending on the command.

**Please ensure that you have enabled the appropriate response event(s) in** [**Event Collection**](/v2/docs/ext-exfil) **to ensure that you will receive the Sensor response.**

This non-blocking approach makes responses accessible via the [event streams](/v2/docs/sensors) passing through Detection & Response rules and Outputs.

## Structure

Commands follow typical CLI conventions using a mix of positional arguments and named optional arguments.

Here's `dir_list` as an example:

```
dir_list [-h] [-d DEPTH] rootDir fileExp

positional arguments:
    rootDir     the root directory where to begin the listing from
    fileExp     a file name expression supporting basic wildcards like * and ?

optional arguments:
    -h, --help      show this help message and exit
    -d DEPTH, --depth DEPTH     optional maximum depth of the listing, defaults to a single level
```

The Console in the web application will provide autocompletion hints of possible commands for a sensor and their parameters. For API users, commands and their usage details may be retrieved via the `/tasks` and `/task` REST API endpoints.

## Investigation IDs

To assist in finding the responses more easily, you may specify an arbitrary `investigation_id` string with a command. The response will then include that value under `routing/investigation_id`. Under the hood, this is exactly how the Console view in the web application works.

If an `investigation_id` is prefixed with `__` (double underscore) it will omit the resulting events from being forwarded to Outputs. This is primarily to allow Services to interact with sensors without spamming.

## Command Line Format

When issuing commands to sensors as a command line (versus a list of tokens), the quoting and escaping of arguments can be confusing. This is a short explanation:

The command line tasks are parsed as if they were issued to a shell like `sh` or `cmd.exe` with a few tweaks to make it easier and more intuitive to use.

Arguments are parsed as separated by spaces, like: `dir_list /home/user *` is equal to 2 arguments: `/home/user` and `*`.

If an argument contains spaces, for example a single directory like `/file/my files`, you must use either single (`'`) or double (`"`) quotes around the argument, like: `dir_list "/files/my files"`.

A backslash (`\`), like in Windows file paths does not need to be escaped. It is only interpreted as an escape character when it is followed by a single or double quote.

The difference between single quotes and double quotes is that double quotes support escaping characters within using `\`, while single quotes never interpret `\` as an escape character. For example:

* `log_get --file "c:\\temp\\my dir\\" --type json` becomes `log_get`, `--file`, `c:\temp\my dir\`, `--type`, `json`
* `log_get --file 'c:\\temp\\my dir\\' --type json` becomes `log_get`, `--file`, `c:\\temp\\my dir\\`, `--type`, `json`
* `log_get --file 'c:\temp\my dir\' --type json` becomes `log_get`, `--file`, `c:\temp\my dir\`, `--type`, `json`
* `log_get --file "c:\temp\my dir\\" --type json` becomes `log_get`, `--file`, `c:\temp\my dir\`, `--type`, `json`

This means that as a general statement, unless you want to embed quoted strings within specific arguments, it is easier to use single quotes around arguments and not worry about escaping `\`.

Endpoint Agents are lightweight software agents deployed directly on endpoints like workstations and servers. These sensors collect real-time data related to system activity, network traffic, file changes, process behavior, and much more.

Similar to agents, Sensors send telemetry to the LimaCharlie platform in the form of EDR telemetry or forwarded logs. Sensors are offered as a scalable, serverless solution for securely connecting endpoints of an organization to the cloud.

Command-line Interface

---

Was this article helpful?

Yes    No

Thank you for your feedback! Our team will get back to you

How can we improve this article?

Your feedback

[ ]  Need more information

[ ]  Difficult to understand

[ ]  Inaccurate or irrelevant content

[ ]  Missing/broken link

[ ]  Others

Comment

Comment (Optional)

Character limit : 500

Please enter your comment

Email (Optional)

Email

[ ]   Notify me about change

Please enter a valid email

Cancel

---

###### Related articles

* [Reference: EDR Events](/docs/reference-edr-events)
* [Endpoint Agent Events Overview](/docs/endpoint-agent-events-overview)
* [Detection and Response](/docs/detection-and-response)
* [Response Actions](/docs/response-actions)
* [Payloads](/docs/payloads)
* [Installation Keys](/docs/installation-keys)
* [Reference: Error Codes](/docs/reference-error-codes)
* [Exfil (Event Collection)](/docs/ext-exfil)

---

###### What's Next

* [Reference: Endpoint Agent Commands](/docs/reference-endpoint-agent-commands)

Table of contents

+ [Sending Commands](#sending-commands)
+ [Structure](#structure)
+ [Investigation IDs](#investigation-ids)
+ [Command Line Format](#command-line-format)

Tags

* [browser agent](/docs/en/tags/browser%20agent)
* [endpoint agent](/docs/en/tags/endpoint%20agent)
* [linux](/docs/en/tags/linux)
* [macos](/docs/en/tags/macos)
* [sensors](/docs/en/tags/sensors)
* [windows](/docs/en/tags/windows)
