# Runner Environment

Every AI Session runs inside a managed container image, the **session runner**. LimaCharlie pre-builds this image with a fixed set of CLI tools, language runtimes, and reference data. This page lists what is on `PATH`, so you can decide which tools to give to an agent in `allowed_tools` (or to block in `denied_tools`) without a read of the Dockerfile.

The runner is a Debian Bookworm slim image. The agent process runs as the non-root `claude` user from the `/workspace` directory. Each tool below is available as a normal shell command in `Bash` tool calls. The [tool permissions](tool-permissions.md) of the session control access to them.

!!! note
    This list is the contract of the runner image, but tool **availability** is not tool **authorization**. A CLI can be pre-installed, and the agent still needs an `allowed_tools` entry such as `Bash(gcloud:*)` (or a bare `Bash`) before it can call the CLI. You must also supply the needed credentials in the session `env`, or the agent must fetch them from a Hive secret at runtime.

## Cloud provider CLIs

| Command | Tool | Notes |
|---|---|---|
| `gcloud` | Google Cloud CLI | Includes `gsutil`, `bq`, and the standard component set. |
| `aws` | AWS CLI v2 | Installed under `/usr/local/aws-cli`. |
| `az` | Azure CLI | Installed under `/opt/az`. |
| `doctl` | DigitalOcean CLI | |
| `vultr-cli` | Vultr CLI | |

## Source control & developer tooling

| Command | Tool | Notes |
|---|---|---|
| `git` | Git | |
| `gh` | GitHub CLI | Authenticate with a token in the session `env` (e.g. `GH_TOKEN`). |
| `node`, `npm` | Node.js 20.x | Used by `claude` and `m365`. |
| `python3`, `pip`, `pipx` | Python 3 + pipx | The activated venv is at `/opt/venv` (see [Python environment](#python-environment)). |
| `jq` | JSON processor | |
| `tree`, `less`, `groff`, `unzip`, `tar`, `wget`, `curl` | Standard Unix utilities | |

## Identity, secrets & remote access

| Command | Tool | Notes |
|---|---|---|
| `op` | 1Password CLI | |
| `sdm` | StrongDM CLI | |
| `tailscale` | Tailscale | |
| `m365` | Microsoft 365 CLI | Installed globally with `npm`. |

## Security tooling

| Command | Tool | Notes |
|---|---|---|
| `sublime` | [Sublime Security CLI](https://docs.sublime.security/docs/sublime-cli) | Email security analysis. |
| `chkp_harmony_endpoint_management_cli` | [Check Point Harmony Endpoint Management CLI](https://github.com/CheckPointSW/harmony-endpoint-management-cli) | Pass credentials with `CP_CI_CLIENT_ID`, `CP_CI_ACCESS_KEY`, `CP_CI_GATEWAY`. |
| `mmdblookup` | MaxMind DB lookup (`mmdb-bin`) | GeoLite2 City + ASN databases are mounted at `/usr/share/GeoIP/`. They can be absent in local-built images. The SDK bridge advertises GeoIP capabilities only when the databases exist. |

## Binary analysis

| Command / Path | Tool | Notes |
|---|---|---|
| `lcre` | [LCRE](https://github.com/refractionPOINT/lcre) | LimaCharlie Reverse Engineering helper binary. Ghidra scripts are at `/opt/lcre/scripts/ghidra` (also exposed as `LCRE_SCRIPTS_PATH`). |
| `analyzeHeadless` | Ghidra 11.0.3 | Installed at `/opt/ghidra` (also `GHIDRA_HOME`). `support/` is on `PATH`, so headless calls work directly. It uses the OpenJDK 17 JRE (`JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64`). |

## LimaCharlie & Claude CLIs

| Command | Tool | Notes |
|---|---|---|
| `limacharlie` | LimaCharlie CLI v2 (Python) | Installed in the `/opt/venv` Python environment from the [`cli-v2` branch](https://github.com/refractionPOINT/python-limacharlie/tree/cli-v2). For D&R-driven sessions, agent-scoped credentials are pre-injected — see [D&R-Driven Sessions](dr-sessions.md). |
| `claude` | [Claude Code CLI](https://docs.claude.com/en/docs/claude-code) | The same upstream CLI that the runner orchestrates internally. An agent can call it for sub-invocations. |

## Python environment

The container has an activated Python virtual environment at `/opt/venv`. This environment is first on `PATH` for the `claude` user. It pre-installs:

- `claude-agent-sdk` — the SDK that the runner orchestrator drives.
- `limacharlie` — the LimaCharlie Python SDK and `limacharlie` command, from the `cli-v2` branch.
- `chkp-harmony-endpoint-management-cli` and `sublime-cli` — installed in dedicated pipx-managed venvs and exposed with `/usr/local/bin/` symlinks (see the security tooling table above).

A plain `pip install <pkg>` in an agent session installs into `/opt/venv`. The package is then importable.

## Reference data on disk

| Path | Contents |
|---|---|
| `/workspace/documentation/` | Full clone of [refractionPOINT/documentation](https://github.com/refractionPOINT/documentation) (this site's source). Use it for lookups with `Read` or `Grep` and no `WebFetch` round-trip. |
| `/workspace/lc-ai/ai-agents/`, `/workspace/lc-ai/ai-teams/` | Reference catalogue of existing AI agent and team definitions from the [lc-ai](https://github.com/refractionPOINT/lc-ai) repository. Use it when an agent must design or change another agent. |
| `/opt/lc-essentials/`, `/opt/lc-advanced-skills/`, `/opt/lc-fundamentals/` | The three first-party Claude Code plugins from `lc-ai/marketplace/plugins/`. Their skills are loaded automatically when the matching plugin is enabled for the session. |

## Stability of this list

The runner image is rebuilt and re-tagged on every release of `ai-sessions`. The Dockerfile pins each CLI tool to a version, and a tool changes only when that pin changes. Tools do not disappear or move to an older version between sessions on the same image tag. To add a new CLI to the runner, change the code in [`docker/Dockerfile.session-runner`](https://github.com/refractionPOINT/ai-sessions/blob/master/docker/Dockerfile.session-runner). The new CLI ships in the next image build.

## See also

- [Tool Permissions & Profiles](tool-permissions.md) — how to authorize the agent to call these tools with `Bash(<prefix>:*)`.
- [D&R-Driven Sessions](dr-sessions.md) and [User Sessions](user-sessions.md) — how to start sessions and how `env` values and Hive secrets reach the runner.
- [Alternative Providers](alternative-providers.md) — Bedrock and Vertex configuration. It uses the `aws` and `gcloud` credentials in the same runner.
