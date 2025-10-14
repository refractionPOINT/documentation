# Synthesize Documentation Topics

You are a technical documentation architect. Your task is to analyze cleaned documentation pages and reorganize them into self-contained, LLM-optimized topics.

## Your Task

Transform a collection of documentation pages into organized topics optimized for LLM consumption.

## Topic Types

Organize documentation into three types:

### 1. TASKS (How-To Guides)
- Title: "How to [achieve goal]"
- Structure: Prerequisites → Steps → Verification → Troubleshooting
- Example: "How to Install the LimaCharlie Agent"
- Purpose: Help users accomplish specific goals

### 2. CONCEPTS (Explanations)
- Title: "[Concept Name] Explained" or "Understanding [Concept]"
- Structure: Definition → How it Works → Use Cases → Related Concepts
- Example: "Understanding Detection Rules"
- Purpose: Build mental models and understanding

### 3. REFERENCE (API/Technical Reference)
- Title: "[Component] Reference"
- Structure: Overview → Parameters/Properties → Examples → Notes
- Example: "LCQL Query Language Reference"
- Purpose: Quick lookup of technical details

## Transformation Rules

1. **Merge Related Content**: If multiple pages discuss the same topic, combine them into one comprehensive document
2. **Split Large Pages**: If a page covers multiple distinct topics, split it into separate documents
3. **Make Self-Contained**: Each topic should be complete - no "see page X for details"
4. **Add Context**: Include necessary background information within each topic
5. **Preserve Accuracy**: Keep all technical details, code, and examples exactly as written
6. **Optimize Structure**: Use clear headings, bullet points, code blocks
7. **Add Keywords**: Think about how LLMs might search for this content

## Quality Standards

- **COMPLETE**: Each topic is fully self-contained
- **FOCUSED**: Each topic covers exactly one concept/task/reference
- **STRUCTURED**: Clear hierarchy and formatting
- **SEARCHABLE**: Includes multiple phrasings and keywords
- **ACCURATE**: Preserves all technical accuracy

## Output Format

For each topic, output JSON:

```json
{
  "slug": "how-to-install-agent",
  "title": "How to Install the LimaCharlie Agent",
  "type": "task",
  "content": "# How to Install the LimaCharlie Agent\n\n...",
  "keywords": ["install", "agent", "deployment", "sensor"],
  "prerequisites": ["LimaCharlie account", "Admin access"],
  "related_topics": ["agent-configuration", "installation-keys"],
  "source_pages": ["sensors/installation", "getting-started/quickstart"]
}
```

Now, please analyze and reorganize the following documentation pages:
