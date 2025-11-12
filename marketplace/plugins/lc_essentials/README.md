# LimaCharlie Essentials Plugin

Essential utilities for working with LimaCharlie in Claude Code. This plugin provides intelligent agents to help you access LimaCharlie documentation and resources efficiently.

## Overview

The LimaCharlie Essentials plugin provides core utilities that make working with LimaCharlie easier. It currently includes the `lc-doc` agent for intelligent documentation search and retrieval.

## Features

- **Smart Documentation Retrieval**: Automatically searches local or remote LimaCharlie documentation
- **Dual-Mode Operation**: Uses local docs when available, falls back to GitHub when needed
- **Comprehensive Results**: Returns original documentation content with minimal synthesis
- **Fast Performance**: Powered by Claude 3.5 Haiku for quick responses
- **Source Attribution**: Always includes references to source files or URLs

## Agents

### lc-doc Agent

The `lc-doc` agent is a specialized documentation retrieval assistant that helps you find and access LimaCharlie documentation on any topic.

**Key capabilities:**
- Searches through LimaCharlie documentation intelligently
- Understands natural language queries about LimaCharlie topics
- Returns comprehensive, original documentation content
- Automatically detects whether to use local or remote documentation
- Provides source references for all content

**Supported topics:**
- LCQL (LimaCharlie Query Language)
- Sensors and agent deployment
- Detection & Response (D&R) rules
- Event types and schemas
- API and SDK usage
- Extensions and integrations
- Getting started guides
- Outputs and data export
- Cloud sensors and adapters

## Installation

### Via Marketplace

If the LimaCharlie marketplace is configured:

```bash
/plugin marketplace add https://raw.githubusercontent.com/refractionPOINT/documentation/master/marketplace/.claude-plugin/marketplace.json
/plugin install lc-essentials
```

### Manual Installation

1. Clone or download the LimaCharlie documentation repository
2. Copy the `lc_essentials` directory to your Claude Code plugins folder
3. Restart Claude Code or reload plugins

## Usage

### Finding Documentation

Simply invoke the agent with your documentation request:

```
Use the lc-doc agent to show me documentation on LCQL syntax
```

```
I need docs on installing sensors
```

```
Show me how D&R rules work
```

The agent will automatically:
1. Detect whether local documentation is available
2. Search for relevant documentation files
3. Read and compile the content
4. Present it with proper source references

### Example Queries

**LCQL and Querying:**
```
Show me LCQL query examples
Explain LCQL syntax
How do I write LCQL queries for threat hunting?
```

**Sensors:**
```
How do I install sensors on Windows?
Show me sensor deployment options
What platforms does LimaCharlie support?
```

**Detection & Response:**
```
How do I write D&R rules?
Show me D&R rule examples
What are managed rulesets?
```

**Events:**
```
What event types are available?
Show me the schema for NEW_PROCESS events
What events does LimaCharlie collect?
```

**API/SDK:**
```
How do I authenticate with the API?
Show me Python SDK examples
How do I use the REST API?
```

**Extensions:**
```
What extensions are available?
How do I configure a Syslog output?
Show me how to set up cloud sensors
```

## How It Works

### Local Mode (Preferred)

When running from within the LimaCharlie documentation repository:

1. Agent checks if `docs/limacharlie/` directory exists
2. Uses `Glob` to find relevant documentation files
3. Uses `Grep` to search for keywords in the docs
4. Uses `Read` to retrieve full file contents
5. Presents original documentation with local file path references

**Advantages:**
- Fast access to documentation
- No network requests needed
- Can search across all files efficiently
- Full text search capabilities

### Remote Mode (Fallback)

When local documentation is not available:

1. Agent detects absence of local docs
2. Uses `WebFetch` to retrieve documentation from GitHub
3. Fetches from: `https://raw.githubusercontent.com/refractionPOINT/documentation/master/docs/limacharlie/doc/`
4. Presents documentation with GitHub URL references

**Advantages:**
- Works from anywhere
- Always accesses latest documentation
- No local setup required

## Output Format

The agent provides well-structured documentation responses:

```markdown
# [Topic Title]

[Original documentation content, preserving structure and formatting]

## Examples
[Code examples and samples as written in docs]

## Sources
- docs/limacharlie/doc/path/to/file.md (local mode)
- https://github.com/.../file.md (remote mode)

## Related Topics
- [Related topic 1]
- [Related topic 2]
```

## Use Cases

### Learning LimaCharlie

Quickly access documentation while learning:
```
Show me getting started documentation
What is LCQL?
How do sensors work?
```

### Writing D&R Rules

Get rule syntax and examples:
```
Show me D&R rule syntax
Give me examples of detection rules
How do I write response actions?
```

### Integration Development

Access API and SDK documentation:
```
Show me API authentication docs
How do I use the Python SDK?
What REST endpoints are available?
```

### Troubleshooting

Find relevant documentation for issues:
```
Why aren't my sensors reporting?
How do I debug D&R rules?
What does event type X contain?
```

### Quick Reference

Get quick answers without leaving your workflow:
```
What are the LCQL operators?
Show me sensor platform IDs
What outputs can I configure?
```

## Performance

- **Model**: Claude 3.5 Haiku (optimized for speed and cost)
- **Response Time**:
  - Local mode: 2-5 seconds (depending on search complexity)
  - Remote mode: 5-10 seconds (includes network fetch time)
- **Search Efficiency**: Optimized glob and grep patterns for fast file discovery

## Best Practices

### Writing Effective Queries

**Good queries:**
- "Show me LCQL syntax documentation"
- "How do I install sensors on Windows?"
- "Give me examples of D&R rules for PowerShell"

**Less effective:**
- "Tell me about LimaCharlie" (too broad)
- "docs" (no specific topic)

### Getting Comprehensive Results

Ask for specific topics:
```
Show me comprehensive documentation on LCQL including syntax and examples
```

### Finding Related Information

The agent will often suggest related topics:
```
I found documentation on X. Related topics include Y and Z. Would you like to see those too?
```

## Troubleshooting

### No Documentation Found

**Issue**: Agent reports it can't find documentation on a topic

**Solutions:**
- Try rephrasing with different keywords (e.g., "query language" instead of "LCQL")
- Ask for related topics to understand what's available
- Use broader search terms first, then narrow down

### Slow Response Time

**Issue**: Documentation retrieval takes longer than expected

**Solutions:**
- If using remote mode, check network connectivity
- Try more specific queries to reduce search space
- Break complex queries into smaller, focused requests

### Partial Results

**Issue**: Agent returns incomplete documentation

**Solutions:**
- Ask for "comprehensive" or "complete" documentation
- Request specific sections or aspects
- Ask follow-up questions for additional details

## Requirements

- Claude Code with plugin support
- For local mode: Running from within the LimaCharlie documentation repository
- For remote mode: Internet connectivity to access GitHub

## Configuration

No special configuration required. The plugin works out of the box once installed.

The agent automatically determines which mode to use based on the environment.

## Examples

### Example 1: Learning LCQL

**Request**: "Show me documentation on LCQL syntax"

**Response**: Comprehensive LCQL syntax documentation including:
- Query structure (timeframe, selector, event type, filter, projection)
- Operators and functions
- Examples of common queries
- Source references

### Example 2: Sensor Installation

**Request**: "How do I install sensors on Linux?"

**Response**: Complete Linux sensor installation guide including:
- Installation methods (package manager, script, manual)
- Installation keys and configuration
- Platform-specific considerations
- Verification steps
- Source documentation link

### Example 3: D&R Rule Writing

**Request**: "Give me examples of D&R rules"

**Response**: Multiple D&R rule examples including:
- Detection rule syntax
- Response action examples
- Common use cases (process detection, network monitoring, etc.)
- Best practices
- Source references

## Future Enhancements

Planned additions to the `lc_essentials` plugin:

- Additional agents for common LimaCharlie workflows
- Integration with other LimaCharlie plugins
- Cached documentation for offline access
- Interactive documentation exploration

## Contributing

To improve this plugin:

1. Fork the [documentation repository](https://github.com/refractionPOINT/documentation)
2. Make your changes to the plugin files
3. Test thoroughly in both local and remote modes
4. Submit a pull request with clear description of improvements

## Support

For issues, questions, or feature requests:

- **GitHub Issues**: [refractionPOINT/documentation](https://github.com/refractionPOINT/documentation/issues)
- **LimaCharlie Support**: support@limacharlie.io
- **Community**: [LimaCharlie Community](https://limacharlie.io/community)

## License

This plugin is part of the LimaCharlie documentation repository and follows the same license terms.

## Version History

### 1.0.0 (Initial Release)
- `lc-doc` agent for documentation search and retrieval
- Dual-mode operation (local and remote)
- Support for all major LimaCharlie documentation topics
- Optimized with Claude 3.5 Haiku model
- Comprehensive error handling and fallback mechanisms
