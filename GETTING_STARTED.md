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

## Step 2: Clone This Repository

```bash
git clone https://github.com/refractionPOINT/documentation.git
cd documentation
```

## Step 3: Install the Marketplace

From within Claude Code, run:
```
/plugin marketplace add ./marketplace
```

## Step 4: Install the lc-essentials Plugin

```
/plugin install lc-essentials@limacharlie-marketplace
```

## Step 5: Authenticate with LimaCharlie

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

See `marketplace/plugins/lc-essentials/README.md` for full documentation.
