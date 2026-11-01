---
description: Set up LimaCharlie with Claude. Paste one line into Claude Code, Claude Desktop or claude.ai and Claude creates your free account, connects your computers, cloud, identity and email, and checks that it works.
---

# LimaCharlie with Claude

Claude can set LimaCharlie up for you, whether you use Claude Code in a terminal, Claude Desktop, or claude.ai in a browser. You do not need security experience. Claude asks what you run, proposes a plan, does the technical work and tells you when it needs you.

Paste this into Claude:

```text
Set me up with LimaCharlie by following https://docs.limacharlie.io/ai-setup/
```

That page is the playbook Claude follows. The rest of this page covers how to give Claude the access it needs. Do this first if you can, because it lets Claude do more on its own.

## Which Claude do you use?

| You use | What Claude can do | What to set up |
| --- | --- | --- |
| Claude Code | Install and run the `limacharlie` command-line tool on your computer. This is the smoothest path. | Nothing before you start. Claude installs the tool itself. Adding the connector is optional. |
| Claude Desktop or claude.ai | Use LimaCharlie through a connector, and walk you through the web app for the rest. It cannot run commands. | Add the LimaCharlie connector (below). |

## Claude Code

1. Install and sign in to Claude Code. Anthropic's [setup guide](https://code.claude.com/docs/en/setup) has the current steps and the plans that include it.
2. Run `claude` in a terminal and paste the prompt above.
3. Claude asks before it installs the LimaCharlie CLI (it needs Python 3.10 or newer) and before it signs you in. Sign-in opens your browser. Choose your Google or Microsoft account.

Approve commands one by one while you set up. Do not turn on an auto-approve mode for a session that has LimaCharlie write access.

Two optional extras:

- **Connector.** Gives Claude LimaCharlie tools without the terminal. Run this, then type `/mcp` inside Claude Code and follow the browser sign-in:

    ```bash
    claude mcp add --transport http limacharlie https://mcp.limacharlie.io/mcp
    ```

- **Plugin.** Adds ready-made skills for day-to-day work after setup. See [Connecting AI Assistants](../6-developer-guide/mcp-server.md#option-1-claude-code-plugin-recommended).

## Claude Desktop and claude.ai

1. In Claude, open **Customize**, then **Connectors**.
2. Choose **Add**, then **Add custom connector**.
3. Name it `LimaCharlie` and enter this address:

    ```text
    https://mcp.limacharlie.io/mcp
    ```

4. Choose **Continue**, then sign in to LimaCharlie when asked.
5. In a new chat, turn the connector on with the **+** button, then **Connectors**. Paste the prompt above.

Menu names change. Anthropic's article on [custom connectors](https://support.claude.com/en/articles/11175166-getting-started-with-custom-connectors-using-remote-mcp) has the current ones. On Team and Enterprise plans an owner has to add the connector first. A free Claude plan allows one custom connector.

Because Claude cannot run commands in this setup, expect it to ask you to click through some screens in the [LimaCharlie web app](https://app.limacharlie.io). It tells you exactly where.

## What Claude will ask of you

- Sign in with Google or Microsoft.
- A few plain questions about what you use: sign-in service, cloud, computers, email.
- A yes before each change, and before it installs anything.
- Steps only an administrator of your own Google, Microsoft or cloud account can do, such as granting access.

Claude does not need your passwords or keys in the chat. If it asks for one, ask why, and say no if you are not comfortable.

## Related

- [Set up LimaCharlie with an AI assistant](ai-assistant-setup.md), the full playbook
- [LimaCharlie with Codex](limacharlie-with-codex.md)
- [Connecting AI Assistants](../6-developer-guide/mcp-server.md), the reference for every connection option
