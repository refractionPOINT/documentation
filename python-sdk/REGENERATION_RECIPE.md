# Documentation Regeneration Recipe for LimaCharlie Python SDK

## Purpose
This recipe enables future Claude Code instances to regenerate comprehensive documentation for the LimaCharlie Python SDK when the SDK code changes.

## Prerequisites
- Access to the LimaCharlie Python SDK repository: https://github.com/refractionPOINT/python-limacharlie/
- Access to LimaCharlie documentation (if available in markdown format)
- Access to the LimaCharlie OpenAPI spec: https://api.limacharlie.io/openapi

## Step-by-Step Instructions

### 1. Repository Analysis
```bash
# Clone the latest SDK
git clone https://github.com/refractionPOINT/python-limacharlie.git /tmp/python-limacharlie
```

Then analyze these key files in order:
- `/limacharlie/__init__.py` - Version, imports, and global configuration
- `/limacharlie/Manager.py` - Main entry point class (read first 500+ lines)
- `/limacharlie/Sensor.py` - Individual sensor management
- `/limacharlie/Firehose.py` - Push-based streaming
- `/limacharlie/Spout.py` - Pull-based streaming
- `/limacharlie/DRCli.py` - Detection & Response CLI interface
- `/limacharlie/Sync.py` - Configuration synchronization
- `/limacharlie/Payloads.py` - Artifact management
- `/limacharlie/Hive.py` - Key-value storage
- `/limacharlie/Query.py` - Query builder
- `/limacharlie/Replay.py` - Event replay
- `/limacharlie/Jobs.py` - Background jobs
- `/limacharlie/Extensions.py` - Add-on management
- `/limacharlie/Billing.py` - Billing operations
- `/limacharlie/User.py` and `/limacharlie/UserPreferences.py` - User management
- `/limacharlie/Webhook.py` and `/limacharlie/WebhookSender.py` - Webhook operations
- `/limacharlie/utils.py` - Utility functions and exceptions
- `/limacharlie/constants.py` - Constants and configuration paths

### 2. Examine Sample Code
Review the `/samples/` directory for real-world usage patterns:
- `demo_manager.py` - Basic manager operations
- `demo_firehose.py` - Streaming implementation
- `demo_interactive_sensor.py` - Interactive sensor control
- `demo_spout.py` - Spout usage
- `demo_delete_duplicate_sensors.py` - Practical automation

### 3. API Documentation Analysis
Fetch and analyze the OpenAPI spec:
```
URL: https://api.limacharlie.io/openapi
```
Extract:
- Available endpoints and their purposes
- Required parameters for each endpoint
- Authentication methods
- Response formats
- Error codes

### 4. Documentation Structure

Create a comprehensive README.md with these sections:

#### Required Sections (in order):
1. **Overview** 
   - Brief platform description
   - Key features list
   - Current SDK version (from `__version__`)

2. **Installation**
   - pip install command
   - Requirements from `requirements.txt`
   - Python version compatibility
   - Dependencies

3. **Authentication**
   - API Key authentication (most common)
   - OAuth authentication (from oauth_*.py files)
   - JWT token usage
   - Environment-based auth (LC_OID, LC_API_KEY)
   - Configuration file format (~/.limacharlie)
   - Multiple environment support

4. **Core Classes**
   - Class hierarchy diagram
   - Brief description of each class's purpose

5. **Manager Class** (Most important - be thorough!)
   - Initialization parameters (ALL of them with descriptions)
   - Organization management methods
   - Sensor listing and search
   - Installation key management
   - Detection & Response rule management
   - Output management
   - Artifact operations
   - Service management
   - Include return types for each method

6. **Sensor Management**
   - Creating sensor objects
   - Getting sensor information
   - Sending tasks (single and multiple)
   - Interactive task execution with futures
   - Sensor isolation/rejoin
   - Tag management
   - Common sensor tasks list (os_info, file_get, etc.)

7. **Detection and Response Rules**
   - D&RL structure explanation
   - Detection operators (is, contains, matches, and, or, etc.)
   - Response actions (report, task, isolate, add_tag)
   - Complete rule examples
   - FalsePositive rules

8. **Real-time Data Streaming**
   - Firehose (push) - full initialization parameters
   - Spout (pull) - full initialization parameters
   - Event filtering options
   - Processing patterns

9. **Artifacts and Payloads**
   - Artifact listing and retrieval
   - Payload creation and management
   - Using payloads in tasks

10. **Event Ingestion**
    - Custom event ingestion
    - Third-party log integration examples

11. **Advanced Features**
    - Hive operations (key-value storage)
    - LCQL query language
    - Replay functionality
    - Jobs management
    - Extensions
    - Sync operations

12. **Error Handling**
    - LcApiException usage
    - Retry logic
    - Quota error handling
    - Common error scenarios

13. **Complete Examples** (3 comprehensive examples)
    - Automated Threat Hunting
    - Incident Response Automation
    - Compliance and Audit Automation

14. **Best Practices**
    - Performance optimization
    - Security practices
    - Error handling patterns

15. **Troubleshooting**
    - Common issues and solutions

### 5. Code Analysis Guidelines

When analyzing code:

#### Method Documentation Pattern:
```python
# For each public method, document:
method_name(param1, param2, ...)
  Parameters:
    - param1 (type): description
    - param2 (type): description
  Returns:
    type: description
  Example:
    code example
```

#### Focus Areas:
1. **Manager class methods** - Document ALL public methods
2. **Required vs optional parameters** - Be explicit
3. **Return value structures** - Show example responses
4. **Error conditions** - What exceptions are raised
5. **Deprecation notices** - Flag any deprecated methods

### 6. Example Generation Rules

For each major feature, create:
1. **Basic usage example** - Minimal working code
2. **Advanced usage example** - With error handling and options
3. **Real-world scenario** - Practical implementation

Include these patterns:
- Authentication setup
- Error handling with try/except
- Resource cleanup (shutdown() calls)
- Timeout specifications
- Batch operations vs individual calls

### 7. Special Attention Areas

Pay extra attention to:
1. **Authentication methods** - Multiple ways to authenticate
2. **Streaming differences** - Firehose vs Spout use cases
3. **Task command syntax** - Exact format for sensor tasks
4. **Detection rule syntax** - D&RL operators and structure
5. **Investigation IDs** - How they propagate through operations
6. **Platform-specific features** - Windows vs Linux vs macOS

### 8. Documentation Style

- **Purpose**: Optimize for LLM consumption
- **Code blocks**: Use ```python for all code
- **Comments**: Explain complex operations inline
- **Return values**: Always show example returns
- **Parameters**: Include type hints and whether optional
- **Links**: Reference classes with proper paths (e.g., `/limacharlie/Manager.py:line_number`)

### 9. Validation Checklist

Before finalizing, ensure:
- [ ] All public methods are documented
- [ ] Authentication section covers all methods
- [ ] At least 3 complete, runnable examples
- [ ] Error handling is demonstrated
- [ ] Common sensor tasks are listed
- [ ] D&R rule structure is explained with examples
- [ ] Streaming (Firehose/Spout) differences are clear
- [ ] Best practices section includes security guidance
- [ ] Troubleshooting covers common issues

### 10. Output Format

Generate a single comprehensive README.md file that:
- Uses clear markdown formatting
- Has a detailed table of contents
- Includes extensive code examples
- Shows both correct and incorrect usage (Good/Bad patterns)
- Provides complete, copy-paste ready examples

## Execution Command

To regenerate the documentation, provide this instruction to Claude Code:

```
Please regenerate the LimaCharlie Python SDK documentation following the recipe in REGENERATION_RECIPE.md. 
1. Clone the latest SDK from https://github.com/refractionPOINT/python-limacharlie/
2. Analyze all core classes and methods
3. Fetch the OpenAPI spec from https://api.limacharlie.io/openapi
4. Generate comprehensive documentation optimized for LLM consumption
5. Include at least 3 complete real-world examples
6. Save as README.md in the python-sdk directory
```

## Notes for Future Claude

- The SDK uses both Python 2 and 3 compatibility code, but focus on Python 3 patterns
- The Manager class is the most important - be extremely thorough with it
- Real-time streaming has two modes (push/pull) - explain when to use each
- Authentication can be complex - cover all methods clearly
- Include practical examples that combine multiple features
- Error handling is critical for production use - emphasize it
- The documentation should enable an LLM to write functional code without accessing the source

## Version Tracking

When regenerating, note:
- Current SDK version from `__version__` in `__init__.py`
- Date of regeneration
- Any major API changes discovered
- New features or deprecated methods

This recipe should enable consistent, high-quality documentation generation across SDK updates.