# Command Line Interface

The [Python SDK](sdks/python-sdk.md) package installs the LimaCharlie CLI.

```bash
pip install limacharlie
```

The CLI uses a `limacharlie <noun> <verb>` command pattern. Every command supports `--help` for detailed usage and `--ai-help` for AI-optimized explanations. Run `limacharlie --help` to see all available commands.

## Authentication

You can authenticate the CLI in different ways.

### Option 1 - Logging In

The most simple method is to log in to an Organization with an [API key](../7-administration/access/api-keys.md).

Use `limacharlie auth login` to store the credentials on your computer. You need an `OID` (Organization ID) and an API key. A `UID` (User ID) is optional. Get these values from the Access Management --> REST API section of the web interface.

The login interface supports named environments. It uses a default environment when you select no environment.

To list the available organizations:

```bash
limacharlie auth list-orgs
```

To set an organization for the current shell session, use this command:

```bash
limacharlie auth use-org my-dev-org
```

You can also give a `UID` (User ID) at login. The CLI then uses a *user* API key that has the full set of permissions of that user. See User Profile in the web interface.

### Option 2 - Environment Variables

Use the `LC_OID`, `LC_API_KEY`, and `LC_UID` environment variables in place of the values from the login. The CLI uses these environment variables if you specify no other credentials.

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

[LimaCharlie Query Language (LCQL)](../4-data-queries/lcql-examples.md) gives you a flexible and interactive way to explore your data in LimaCharlie.

```bash
limacharlie search --help
```

### ARLs

[Authenticated Resource Locators (ARLs)](../8-reference/authentication-resource-locator.md) specify access to a remote resource in one string. They support many access methods and can include authentication data.

You can use ARLs in the [YARA manager](../5-integrations/extensions/limacharlie/yara-manager.md) to import rules from GitHub repositories and other locations.

Test an ARL before you use it somewhere. A test finds access errors and authentication errors early. This command tests an ARL and shows which files it gets, and their contents:

```bash
limacharlie arl get -a [github,Yara-Rules/rules/email]
```

### Streaming

Stream events, detections, or audit logs in real time. The command uses pull-mode spouts (HTTPS) or push-mode firehose listeners (TLS).

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

The `pull` command gets the organization configuration and writes it to a local YAML file.

```bash
limacharlie sync pull --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca
```

The `push` command then uploads the configuration in the YAML file to your organization. The `--dry-run` flag simulates the sync and shows the changes that it would make.

```bash
limacharlie sync push --dry-run --oid c82e5c17-d519-4ef5-a4ac-c454a95d31ca --config /path/to/template.yaml
```

The `Configs` SDK class (`limacharlie.sdk.configs`) also supports all these capabilities.

The Sync function supports all common useful configurations. Use the hive flags (`--hive-dr-general`, `--hive-fp`, `--outputs`, etc.) to control which resource types the CLI syncs. See `limacharlie sync --help` for all options.

To learn the config format, do a `pull` from your organization. Look at the `include` statement. This statement combines more than one config file into one configuration. Use it to manage complex rule sets and their versions.

### Spot Checks

Do checks for specific indicators of compromise across the Organization. Spot checks support many types of IoC, such as file names, directories, registry keys, file hashes, and YARA signatures.

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

Run [Replay](../5-integrations/services/replay.md) jobs from the CLI.

```bash
limacharlie replay --help
```

### Detection & Response

Manage Detection and Response rules over the CLI.

```bash
limacharlie dr --help
```

### Events & Detections

Print the events or the detections that match the parameter to STDOUT.

```bash
limacharlie event --help
limacharlie detection --help
```

### List Sensors

Print the basic sensor information for all sensors that match the [selector](../8-reference/sensor-selector-expressions.md).

```bash
limacharlie sensor list --selector 'plat == windows'
```

### Add Users

Add one user or more users to a LimaCharlie organization. Each new user gets an email. The email asks the user to confirm the address, enable the account, and create a new password.

This action operates in the user context, so you must use a user scoped API key. To get one, see <https://api.limacharlie.io/static/swagger/#getting-a-jwt>

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

Create, inspect, and attach to [AI Sessions](../9-ai-sessions/index.md) from the terminal. The CLI exposes both ownership models that the cloud supports: **org-owned** sessions and **user-owned** sessions. An org-owned session starts from an `ai_agent` Hive template, and the cloud bills it against the org's stored Anthropic key. A user-owned session starts fresh, and the cloud bills it against your personal Claude credential.

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

The `ai session attach --interactive` command works with both kinds of session. It sends prompts when you own the session (user-owned). When the session is org-owned, it shows a notice and becomes read-only, because the cloud exposes only a read-only WebSocket for those sessions by design.

See [AI Sessions — Command Line Interface](../9-ai-sessions/cli.md) for the full command reference, override semantics, the org-vs-user split, and stream output formatting.
