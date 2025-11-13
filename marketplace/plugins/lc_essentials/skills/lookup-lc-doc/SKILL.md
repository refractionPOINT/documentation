---
name: lookup-lc-doc
description: Search and retrieve LimaCharlie documentation from the local docs/ folder. Use when users ask about LimaCharlie platform features, SDKs, APIs, D&R rules, LCQL, sensors, outputs, extensions, integrations, or any LimaCharlie-related topics. Covers platform documentation, Python SDK, and Go SDK.
---

# Looking Up LimaCharlie Documentation

Use this skill proactively whenever a user asks about LimaCharlie features, configuration, or implementation.

## When to Use

Invoke this skill when users ask about:

- **Platform features**: D&R rules, LCQL queries, sensors, events, outputs, extensions
- **APIs**: REST API usage, authentication, endpoints
- **SDKs**: Python SDK or Go SDK usage, examples, methods
- **Configuration**: Setting up integrations, adapters, outputs
- **Getting started**: Tutorials, quick start guides, installation
- **Any LimaCharlie topic**: General questions about capabilities or how to use features

## What This Skill Does

This is a simple documentation lookup tool that:

1. Uses Grep to search for relevant keywords in the `docs/` folder
2. Identifies the most relevant documentation files
3. Reads and returns the content to help answer the user's question

## How to Use

When a user asks about LimaCharlie:

1. **Search**: Use Grep to search the `docs/` folder for relevant keywords from the user's question
   - Search in `docs/limacharlie/` for platform documentation
   - Search in `docs/python-sdk/` for Python SDK docs
   - Search in `docs/go-sdk/` for Go SDK docs

2. **Read**: Use Read tool to retrieve the most relevant files found

3. **Respond**: Provide the user with the relevant documentation content to answer their question

## Search Tips

- Use multiple keywords from the user's query for better results
- Try variations (e.g., "D&R", "detection", "response")
- Check multiple documentation folders if needed
- Read the most promising files based on filenames and paths

## Example Workflow

```
User: "How do I write LCQL queries?"

1. Grep for "LCQL" in docs/limacharlie/
2. Read relevant files found (e.g., docs on LCQL syntax, examples)
3. Share the documentation content with the user
```

Keep it simple - just search, read, and share the relevant docs.
