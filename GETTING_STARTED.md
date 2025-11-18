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

## Step 4: Install the lc_essentials Plugin

```
/plugin install lc-essentials@limacharlie-marketplace
```

## Next Steps

The plugin provides 121 skills for LimaCharlie operations including:
- Sensor management and live investigation
- Detection & Response rule creation
- LCQL queries and historical data analysis
- AI-powered query and rule generation

See `marketplace/plugins/lc_essentials/README.md` for full documentation.
