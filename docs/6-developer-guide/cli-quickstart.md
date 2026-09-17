# CLI Quick Start

The LimaCharlie command-line interface (CLI) lets you work with your
LimaCharlie organizations from a terminal. This guide takes you from a new
computer to listing your organizations and sensors.

## Before you begin

You need:

- A LimaCharlie account. [Create one for free](https://app.limacharlie.io/signup)
  if you do not already have one.
- Python 3.10 or newer. Check with `python3 --version` on macOS or Linux, or
  `py --version` on Windows.
- Access to a terminal (Terminal on macOS or Linux, or PowerShell on Windows).

## 1. Install the CLI

We recommend [pipx](https://pipx.pypa.io/stable/installation/) because it keeps
the CLI isolated from other Python packages while making the `limacharlie`
command available everywhere.

=== "pipx (recommended)"

    ```bash
    pipx install limacharlie
    ```

=== "uv"

    ```bash
    uv tool install limacharlie
    ```

=== "pip"

    ```bash title="macOS or Linux"
    python3 -m pip install --user limacharlie
    ```

    ```powershell title="Windows PowerShell"
    py -m pip install --user limacharlie
    ```

Confirm that the command is available:

```bash
limacharlie --version
```

If your shell reports that `limacharlie` is not found, follow the installer
message about adding its binary directory to your `PATH`. For pipx, run
`pipx ensurepath`, restart your terminal, and try again.

## 2. Sign in

Browser-based sign-in is the easiest option for a person using the CLI:

```bash
limacharlie auth login --oauth
```

Your browser opens so you can sign in with Google. To use a Microsoft account,
run:

```bash
limacharlie auth login --oauth --provider microsoft
```

On a remote computer without a browser, add `--no-browser`. Open the printed
URL on a computer with a browser and complete the sign-in there.

### Sign in with an API key

API keys are useful for automation or terminals where browser sign-in is not
practical. In the LimaCharlie web app, open your organization and go to
**Access Management > REST API** to find its Organization ID (OID) and create
an API key. Treat the key like a password.

```bash
limacharlie auth login --oid YOUR_ORG_ID --api-key YOUR_API_KEY
```

The login command stores credentials locally for later commands. Do not put a
real API key in documentation, source control, screenshots, or shell scripts.
For temporary automation, credentials can instead be supplied as environment
variables:

=== "macOS or Linux"

    ```bash
    export LC_OID="YOUR_ORG_ID"
    export LC_API_KEY="YOUR_API_KEY"
    ```

=== "Windows PowerShell"

    ```powershell
    $Env:LC_OID = "YOUR_ORG_ID"
    $Env:LC_API_KEY = "YOUR_API_KEY"
    ```

## 3. Verify your login

Check the identity and organization available to the CLI:

```bash
limacharlie auth whoami
```

If you can access more than one organization, list them and select the one you
want to use. An OID is a UUID, not the organization's display name.

```bash
limacharlie org list
limacharlie auth use-org YOUR_ORG_ID
```

You can also target one command without changing your default organization:

```bash
limacharlie org info --oid YOUR_ORG_ID
```

## 4. Try some read-only commands

Display information about the selected organization:

```bash
limacharlie org info
```

List its sensors:

```bash
limacharlie sensor list
```

Narrow the results with common filters:

```bash
limacharlie sensor list --online
limacharlie sensor list --hostname web
limacharlie sensor list --selector 'plat == windows'
limacharlie sensor list --limit 10
```

The default output is a table in a terminal. Choose a machine-readable format
when using the CLI in a script or sending its output to another tool:

```bash
limacharlie sensor list --output json
limacharlie sensor list --output yaml
limacharlie sensor list --output csv
```

## 5. Find your next command

The CLI has help at every level:

```bash
limacharlie --help
limacharlie sensor --help
limacharlie sensor list --help
limacharlie sensor list --ai-help
```

Explore commands grouped by common use case:

```bash
limacharlie help discover
```

Most commands follow the pattern `limacharlie <noun> <verb>`, such as
`limacharlie sensor list` or `limacharlie detection list`. Before running a
command that creates, changes, or deletes data, read its `--help` output and
confirm that you selected the intended organization.

## Troubleshooting

### Authentication fails

Run `limacharlie auth login --oauth` again, or confirm that the OID and API key
belong to the same organization. Use `limacharlie auth whoami` after signing in
to test the credentials.

### The wrong organization is selected

Run `limacharlie org list`, then `limacharlie auth use-org YOUR_ORG_ID`. You can
always add `--oid YOUR_ORG_ID` to target a specific organization for one
command.

### A command is denied

Your account or API key may not have the required permission in that
organization. Run `limacharlie auth whoami --show-perms` to inspect your current
permissions, then ask an organization administrator for the required access.

### See where credentials are stored

```bash
limacharlie config show-paths
```

For more commands and examples, continue to the [CLI reference](sdk-overview.md).
