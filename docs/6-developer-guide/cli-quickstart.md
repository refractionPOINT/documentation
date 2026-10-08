# CLI Quick Start

The LimaCharlie command-line interface (CLI) lets you work with your
LimaCharlie organizations from a terminal. This guide takes you from a new
computer to listing your organizations and sensors.

## Before you begin

You need:

- A LimaCharlie account. [Create one for free](https://app.limacharlie.io/signup)
  if you do not already have one.
- Permission to install software on your computer.

## 1. Install the CLI

The CLI requires Python 3.10 or newer. The steps below use
[pipx](https://pipx.pypa.io/latest/how-to/install-pipx.html), which keeps the
CLI isolated from other Python packages while making the `limacharlie` command
available everywhere.

=== "macOS"

    1. Open **Terminal**. Find it with Spotlight Search by pressing
        ++command+space++ and typing `Terminal`.

    2. Check whether [Homebrew](https://brew.sh/) is installed:

        ```bash
        brew --version
        ```

        If `brew` is not found, install Homebrew by following the instructions
        on its website, then open a new Terminal window.

    3. Install pipx and add its commands to your shell's search path:

        ```bash
        brew install pipx
        pipx ensurepath
        ```

    4. Close and reopen Terminal, then install the LimaCharlie CLI:

        ```bash
        pipx install limacharlie
        ```

=== "Linux"

    1. Open your terminal. On many Linux desktops, press ++ctrl+alt+t++.

    2. Install pipx using your distribution's package manager.

        On Ubuntu 23.04 or newer and Debian 12 or newer:

        ```bash
        sudo apt update
        sudo apt install pipx
        ```

        On Fedora:

        ```bash
        sudo dnf install pipx
        ```

        For another distribution, follow the
        [pipx Linux instructions](https://pipx.pypa.io/latest/how-to/install-pipx.html#on-linux).

    3. Add pipx commands to your shell's search path:

        ```bash
        pipx ensurepath
        ```

    4. Close and reopen the terminal, then install the LimaCharlie CLI:

        ```bash
        pipx install limacharlie
        ```

=== "Windows"

    1. Install Python 3.10 or newer from
        [python.org](https://www.python.org/downloads/windows/) if it is not
        already installed. During setup, select **Add python.exe to PATH**.

    2. Open **PowerShell** from the Start menu and confirm Python is available:

        ```powershell
        py --version
        ```

        If you installed Python from the Microsoft Store and `py` is not found,
        use `python3` in place of `py` in the next commands.

    3. Install pipx and add its commands to your search path:

        ```powershell
        py -m pip install --user pipx
        py -m pipx ensurepath
        ```

    4. Close and reopen PowerShell, then install the LimaCharlie CLI:

        ```powershell
        pipx install limacharlie
        ```

If you already use [uv](https://docs.astral.sh/uv/), you can use it instead of
pipx:

```bash
uv tool install limacharlie
```

### Confirm the installation

Run:

```bash
limacharlie --version
```

The output should start with `limacharlie, version` followed by the installed
version number.

If your terminal reports that `limacharlie` is not found, make sure you closed
and reopened it after running `pipx ensurepath`. Then try the install command
again.

To upgrade the CLI later, run:

=== "pipx"

    ```bash
    pipx upgrade limacharlie
    ```

=== "uv"

    ```bash
    uv tool upgrade limacharlie
    ```

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

If the CLI cannot open your browser automatically, add `--no-browser`, then
open the printed URL in a browser on the same computer. On a remote or headless
computer, use an API key instead; the OAuth flow waits for a callback on the
computer running the CLI.

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

### Sign out of the CLI

```bash
limacharlie auth logout
```

This removes the locally stored credentials, but it does not revoke an API key.
Revoke a key separately from **Access Management > REST API** if it should no
longer work anywhere.

For more commands and examples, continue to the [CLI reference](sdk-overview.md).
