# Getting Started

This guide walks you through setting up Claude Code with the LimaCharlie plugin.

## Step 1: Install Claude Code

**macOS/Linux:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

## Step 2: Install the LimaCharlie Marketplace

From within Claude Code, run:
```
/plugin marketplace add https://github.com/refractionPOINT/lc-ai
```

## Step 3: Install the lc-essentials Plugin

```
/plugin install lc-essentials@lc-marketplace
```

## Step 4: Authenticate with LimaCharlie

The plugin uses OAuth for secure authentication. Run the following command in Claude Code:

```
/mcp
```

This will open your browser to authorize Claude Code with your LimaCharlie account. Once approved, your credentials are:
- Stored securely (macOS Keychain or encrypted storage on other platforms)
- Refreshed automatically - no manual token rotation needed

You're now ready to use the LimaCharlie plugin!

## Next Steps

The plugin provides 121 skills for LimaCharlie operations including:
- Sensor management and live investigation
- Detection & Response rule creation
- LCQL queries and historical data analysis
- AI-powered query and rule generation

See the [lc-ai repository](https://github.com/refractionPOINT/lc-ai) for full plugin documentation.
