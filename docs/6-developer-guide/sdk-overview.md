# Command Line Interface

The LimaCharlie CLI is installed as part of the [Python SDK](sdks/python-sdk.md) package.

```bash
pip install limacharlie
```

The CLI uses a `limacharlie <noun> <verb>` command pattern. Every command supports `--help` for detailed usage and `--ai-help` for AI-optimized explanations. Run `limacharlie --help` to see all available commands.

## Authentication

Authenticating the CLI can be done in a few ways.

### Option 1 - Logging In

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

You can also specify a `UID` (User ID) during login to use a *user* API key representing the total set of permissions that user has (see User Profile in the web interface).

### Option 2 - Environment Variables

You can use the `LC_OID` and `LC_API_KEY` and `LC_UID` environment variables to replace the values used logging in. The environment variables will be used if no other credentials are specified.

## Docker Image

The CLI is also available as a Docker image on DockerHub (<https://hub.docker.com/r/refractionpoint/limacharlie>).

```bash
docker run refractionpoint/limacharlie:latest whoami

# Using a specific version (Docker image tag matches the library version)
docker run refractionpoint/limacharlie:5.0.0 whoami

# If you already have a credential file locally, you can mount it inside the Docker container
docker run -v ${HOME}/.limacharlie:/root/.limacharlie:ro refractionpoint/limacharlie:latest whoami
```

## Commands

### Search / Query

[LimaCharlie Query Language (LCQL)](../4-data-queries/lcql-examples.md) provides a flexible, intuitive and interactive way to explore your data in LimaCharlie.

```bash
limacharlie search --help
```

### ARLs

[Authenticated Resource Locators (ARLs)](../8-reference/authentication-resource-locator.md) describe a way to specify access to a remote resource, supporting many methods, including authentication data, and all that within a single string.

ARLs can be used in the [YARA manager](../5-integrations/extensions/limacharlie/yara-manager.md) to import rules from GitHub repositories and other locations.

Testing an ARL before applying it somewhere can be helpful to shake out access or authentication errors beforehand. You can test an ARL and see what files are fetched, and their contents, by running the following command:

```bash
limacharlie arl get -a [github,Yara-Rules/rules/email]
```

### Streaming

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

### Sync (Infrastructure as Code)

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

To understand better the config format, do a `pull` from your organization. Notice the use of the `include` statement. Using this statement you can combine multiple config files together, making it ideal for the management of complex rule sets and their versioning.

### Spot Checks

Used to perform Organization-wide checks for specific indicators of compromise. Supports many types of IoCs like file names, directories, registry keys, file hashes and YARA signatures.

```bash
limacharlie spotcheck --help
```

### IOC Search

Search for Indicators of Compromise (domains, IPs, file hashes, etc.) across the Insight data lake.

```bash
limacharlie ioc --help
```

### Extensions

Manage extension subscriptions.

```bash
limacharlie extension --help
```

### Artifacts

Upload, list, and download Artifacts within LimaCharlie.

```bash
limacharlie artifact --help
```

### Replay

Perform [Replay](../5-integrations/services/replay.md) jobs from the CLI.

```bash
limacharlie replay --help
```

### Detection & Response

Manage Detection and Response rules over the CLI.

```bash
limacharlie dr --help
```

### Events & Detections

Print out to STDOUT events or detections matching the parameter.

```bash
limacharlie event --help
limacharlie detection --help
```

### List Sensors

Print out all basic sensor information for all sensors matching the [selector](../8-reference/sensor-selector-expressions.md).

```bash
limacharlie sensor list --selector 'plat == windows'
```

### Add Users

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

### AI Sessions

Create, inspect, and attach to [AI Sessions](../9-ai-sessions/index.md) directly from the terminal. The CLI exposes both ownership models the backend supports — **org-owned** sessions (started from an `ai_agent` Hive template, billed against the org's stored Anthropic key) and **user-owned** sessions (started fresh, billed against your personal Claude credential).

```bash
# --- Org-owned: run an ai_agent Hive record as a template, with overrides.
# (--option flags replace template scalars/lists; --env merges.)
limacharlie ai start-session --definition my-agent \
  --model claude-sonnet-4-6 --max-budget-usd 2.50

limacharlie ai session list --status running        # list org sessions
limacharlie ai session attach --id <SESSION_ID>     # tail the live stream
limacharlie ai session terminate --id <SESSION_ID>

# --- User-owned: chat from the terminal under your own Claude credential.
limacharlie ai auth claude login                    # one-time: store credential
limacharlie ai chat "what sensors pinged in the last hour?"

limacharlie ai chats list --status running          # list your chat sessions
limacharlie ai chats terminate --id <SESSION_ID>
```

The `ai session attach --interactive` command works for either kind of session: it sends prompts when you own the session (user-owned), and falls back to read-only with a notice when the session is org-owned (the backend exposes only a read-only WebSocket for those by design).

See [AI Sessions — Command Line Interface](../9-ai-sessions/cli.md) for the full command reference, override semantics, the org-vs-user split, and stream output formatting.
