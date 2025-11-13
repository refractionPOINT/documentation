# LimaCharlie Essentials Plugin

A simple Claude Code plugin that helps you quickly find and access LimaCharlie documentation from the local `docs/` folder.

## What It Does

This plugin provides a single skill that searches the LimaCharlie documentation and retrieves relevant content to help answer your questions about:

- LimaCharlie platform features (D&R rules, LCQL, sensors, events, outputs, extensions)
- Python SDK and Go SDK
- API usage and configuration
- Getting started guides and tutorials

## Usage

Just ask questions about LimaCharlie - the skill will automatically activate and search the docs:

- "How do I write D&R rules?"
- "Show me LCQL query examples"
- "How do I configure the Office 365 adapter?"
- "What is the Python SDK syntax for getting sensor info?"

## How It Works

The `lookup-lc-doc` skill:

1. Searches the `docs/` folder using keywords from your question
2. Finds relevant documentation files
3. Returns the content to help answer your question

## Documentation Coverage

- **Platform**: `docs/limacharlie/` - Complete LimaCharlie platform documentation
- **Python SDK**: `docs/python-sdk/` - Python SDK reference and examples
- **Go SDK**: `docs/go-sdk/` - Go SDK reference and examples

Simple, straightforward documentation lookup.
