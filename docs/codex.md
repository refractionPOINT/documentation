---
description: Set up LimaCharlie with OpenAI Codex. Paste one line into Codex (CLI, app or IDE extension) and Codex creates your free account, connects your computers, cloud, identity and email, and checks that it works.
---

# LimaCharlie with Codex

OpenAI Codex can set LimaCharlie up for you from the Codex CLI, the Codex app or the IDE extension. You do not need security experience. Codex asks what you run, proposes a plan, does the technical work and tells you when it needs you.

Paste this into Codex:

```text
Set me up with LimaCharlie by following https://docs.limacharlie.io/ai-setup/
```

That page is the playbook Codex follows. The rest of this page covers the access Codex needs.

## Give Codex a terminal that can reach the internet

Codex runs commands in a sandbox. OpenAI's documentation says the agent runs with network access turned off by default, and the workspace sandbox writes only to your working folder and temporary folders. LimaCharlie setup needs more than that. It installs the `limacharlie` command-line tool into `~/.local`, saves your sign-in under `~/.limacharlie.d`, and talks to the internet. You have two choices:

- Let Codex ask you for approval, and approve the commands you recognize to run outside the sandbox. This is the safer choice.
- Widen the sandbox for this setup in `~/.codex/config.toml`, then narrow it again afterward:

    ```toml
    [sandbox_workspace_write]
    network_access = true
    ```

    To let it write `~/.local` and `~/.limacharlie.d`, add `writable_roots` to the same table with full paths. Replace `YOU` with your user name, and do not rely on `~` being expanded:

    ```toml
    [sandbox_workspace_write]
    network_access = true
    writable_roots = ["/home/YOU/.local", "/home/YOU/.limacharlie.d"]
    ```

    On macOS the home folder is `/Users/YOU`. Codex keeps the installation key in a `.limacharlie-setup` folder inside your working folder, so that folder needs no extra setting.

Check OpenAI's [approvals and security page](https://learn.chatgpt.com/docs/agent-approvals-security) and the rest of the [Codex documentation](https://learn.chatgpt.com/docs) for the current setting names. Do not use a mode that disables the sandbox and approvals for this setup.

The sign-in opens your browser and waits for it to return to a `localhost` address on the same computer. Run Codex on your own computer, not on a remote machine, or the sign-in cannot finish.

Start Codex in an empty folder you do not mind it writing to, for example `~/limacharlie-setup`.

## Codex CLI, app or IDE extension

All three can run the setup, because each can run commands. Pick the one you already use.

- **Codex CLI.** Install it from OpenAI's CLI page, run `codex` in your folder, and paste the prompt.
- **Codex app.** Open a project in your folder and paste the prompt in a new thread.
- **IDE extension.** Open the Codex panel in your editor and paste the prompt.

The first time you use Codex, it asks you to sign in with ChatGPT or another available method.

Claude Code, Gemini CLI and other assistants can follow the same playbook. See [Using the CLI with other Frontier Models](6-developer-guide/frontier-models.md).

## Optional: the LimaCharlie MCP server

Codex does not need it. The command-line tool covers everything. If you want LimaCharlie tools available directly, add the hosted MCP server and sign in:

```bash
codex mcp add limacharlie --url https://mcp.limacharlie.io/mcp
codex mcp login limacharlie
```

In the Codex app or IDE extension, choose **Authenticate** in the server list instead. If sign-in fails because Codex cannot register with the server, skip this step and use the command-line tool. To use an API key instead of the browser sign-in, see the [Codex section](6-developer-guide/frontier-models.md#openai-codex) of the frontier models guide.

## Give Codex standing instructions

If you plan to keep using Codex with LimaCharlie after setup, save the [agent context file](6-developer-guide/frontier-models.md#teach-the-model-the-platform) as `AGENTS.md` in your folder. Codex loads it automatically.

## What Codex will ask of you

- Sign in with Google or Microsoft in your browser.
- A few plain questions about what you use: sign-in service, cloud, computers, email.
- A yes before each change, and before it installs anything.
- Steps only an administrator of your own Google, Microsoft or cloud account can do, such as granting access.

Codex does not need your passwords or keys in the chat. If it asks for one, ask why, and say no if you are not comfortable.

## Related

- [Set up LimaCharlie with an AI assistant](ai-setup.md), the full playbook
- [LimaCharlie with Claude](claude.md)
- [Using the CLI with other Frontier Models](6-developer-guide/frontier-models.md)
