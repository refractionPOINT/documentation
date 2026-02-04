# Documentation Regeneration Recipe for LimaCharlie Go SDK

## Purpose
This recipe provides step-by-step instructions for an AI assistant (Claude Code or similar LLM) to regenerate the LimaCharlie Go SDK documentation when the SDK code changes.

## Prerequisites
- Access to the LimaCharlie Go SDK repository: https://github.com/refractionPOINT/go-limacharlie/
- Access to the LimaCharlie API OpenAPI specification: https://api.limacharlie.io/openapi
- Access to existing LimaCharlie documentation (if available) in `limacharlie-docs-markdown` directory

## Regeneration Steps

### Step 1: Analyze Current SDK Structure
```yaml
Task: Fetch and analyze the Go SDK repository at https://github.com/refractionPOINT/go-limacharlie/

Extract:
- Repository structure and organization
- Main modules (limacharlie, firehose)
- Package dependencies
- Build and test configuration
- README content for context
```

### Step 2: Deep Dive into SDK Code
```
Task: Analyze the main SDK code in the limacharlie directory

Focus on:
1. Client struct and initialization methods
   - Look for: NewClient*, ClientOptions, configuration loading
   
2. Authentication mechanisms
   - API key, JWT, UID support
   - Configuration file formats (YAML)
   - Environment variable usage
   
3. Core functionality modules:
   - Sensor management (sensor.go or similar)
   - Detection rules (rules.go, dr_rules.go)
   - Artifacts (artifacts.go)
   - Organization management (org.go)
   - Event streaming (webhook.go, events.go)
   
4. Data structures and types
   - All exported structs
   - Enums and constants
   - Error types
   
5. Helper utilities
   - HTTP client wrappers
   - Retry logic
   - Validation functions
```

### Step 3: Analyze API Integration
```python
Task: Fetch the OpenAPI spec from https://api.limacharlie.io/openapi

Map SDK methods to API endpoints:
- Which endpoints does each SDK method call?
- What are the request/response formats?
- Authentication headers required
- Rate limiting information
```

### Step 4: Identify Code Patterns
```
Task: Analyze the SDK for patterns and conventions

Look for:
- Error handling patterns
- Logging approach (zerolog usage)
- Concurrency patterns
- Testing patterns
- Configuration management
- Resource cleanup patterns
```

### Step 5: Generate Documentation Structure

Create a comprehensive README.md with the following sections:

```markdown
# LimaCharlie Go SDK Documentation

## Overview
[Brief description of the SDK and its purpose]

## Table of Contents
- Installation
- Authentication
- Client Initialization
- Core Components
  - Sensor Management
  - Detection Rules
  - Artifacts
  - Events and Data Streaming
  - Organization Management
- Data Structures
- Error Handling
- Advanced Features
- Examples
- Best Practices
- Troubleshooting
- API Endpoints Reference
- SDK Versioning
- Additional Resources

## Installation
[Current installation commands from go.mod]

## Authentication
[All authentication methods with code examples]
- API Key Authentication
- JWT Authentication
- Configuration File
- Environment Variables

## Client Initialization
[How to create and configure clients]

## Core Components

### Sensor Management
[Complete coverage of sensor operations]
- List, Get, Delete sensors
- Isolation/Network control
- Tagging
- Tasking with examples

### Detection Rules
[Rule structure and management]
- Rule format (YAML/JSON)
- CRUD operations
- Namespaces
- TTL support

### Artifacts
[File and data artifact handling]
- Upload methods
- Export methods
- GCS integration
- Size limitations

### Events and Data Streaming
[Real-time and historical data]
- Webhook configuration
- Event types
- Firehose module usage

### Organization Management
[Administrative operations]
- Organization info
- Quota management
- User management
- API key management

## Data Structures
[All exported types with field descriptions]

## Error Handling
[Common errors and handling patterns]

## Advanced Features
[Special capabilities like investigation context, concurrent operations]

## Examples
[Complete, runnable code examples for common use cases]
- Basic sensor monitoring
- Detection rule creation
- Artifact collection
- Batch operations
- Error handling examples

## Best Practices
[Security, performance, and maintainability guidelines]

## Troubleshooting
[Common issues and solutions]

## API Endpoints Reference
[Table of endpoints used by SDK]

## SDK Versioning
[How to check and update versions]

## Additional Resources
[Links to repo, docs, support]
```

### Step 6: Code Examples Requirements

For EACH major function/method in the SDK, provide:

1. **Basic Usage Example**
   ```go
   // Clear, simple example showing the most common use case
   ```

2. **Complete Example with Error Handling**
   ```go
   // Production-ready example with proper error handling
   ```

3. **Advanced Usage** (if applicable)
   ```go
   // Examples showing optional parameters, configuration options
   ```

### Step 7: LLM-Optimized Documentation

Ensure the documentation is optimized for LLM consumption:

1. **Precise Type Information**
   - Include all struct fields with their types
   - Show JSON tags for API serialization
   - Document optional vs required fields

2. **Method Signatures**
   - Full function signatures with parameter and return types
   - Document all parameters including optional ones
   - Explain return values and possible errors

3. **Import Statements**
   - Always show complete import statements in examples
   - Include version specifications where relevant

4. **Context and Dependencies**
   - Explain when to use each method
   - Note any prerequisites or dependencies
   - Clarify relationships between different components

5. **Common Patterns**
   - Show idiomatic Go patterns used in the SDK
   - Include error checking patterns
   - Demonstrate proper resource cleanup

### Step 8: Validation Checklist

Before finalizing, ensure:

- [ ] All exported functions are documented
- [ ] All data structures have field descriptions
- [ ] Authentication methods are clearly explained
- [ ] Error types and handling are covered
- [ ] Examples compile and are realistic
- [ ] Configuration options are enumerated
- [ ] API endpoint mappings are accurate
- [ ] Versioning information is current
- [ ] Security best practices are included
- [ ] Performance considerations are noted

### Step 9: Special Considerations

1. **Breaking Changes**
   - Note any breaking changes from previous versions
   - Provide migration guides if applicable

2. **Platform-Specific Features**
   - Document any OS-specific functionality
   - Note platform limitations

3. **Dependencies**
   - List all external dependencies
   - Note minimum Go version required

4. **Testing**
   - Document how to run tests
   - Include test environment setup

### Step 10: Output Format

Generate the documentation as:
- **Primary file**: `README.md` in the `go-sdk` directory
- **Format**: Markdown with Go syntax highlighting
- **Style**: Concise, technical, example-heavy
- **Target audience**: Developers and AI assistants generating code

## Execution Instructions for AI Assistant

When asked to regenerate this documentation:

1. Start by creating a task list using TodoWrite tool
2. Fetch the latest SDK code from GitHub
3. Analyze all `.go` files in the repository
4. Fetch the current OpenAPI specification
5. Follow steps 1-10 above systematically
6. Generate comprehensive documentation
7. Save to `go-sdk/README.md`

## Example Prompt to Trigger Regeneration

"Please regenerate the LimaCharlie Go SDK documentation following the recipe in go-sdk/REGENERATION_RECIPE.md. The SDK repository is at https://github.com/refractionPOINT/go-limacharlie/"

## Important Notes

- Focus on precision and completeness over brevity
- Include ALL public methods and types
- Provide working code examples for every major feature
- Ensure examples are self-contained and runnable
- Document both common and edge cases
- Keep security considerations prominent
- Make the documentation LLM-friendly with clear patterns and complete information