# Synthesize Documentation Topics

You are a technical documentation architect. Your task is to analyze cleaned documentation pages and reorganize them into self-contained, LLM-optimized topics.

## CRITICAL VALIDATION RULE

**BEFORE merging documents, you MUST verify they are about the SAME specific topic.**

- ✅ MERGE: Documents about "Config Hive API", "Config Hive CLI", "Config Hive Examples" → All about Config Hive
- ❌ DO NOT MERGE: "BinLib", "Enterprise SOC", "LCQL" → Different topics entirely
- ❌ DO NOT MERGE: "Windows Agent", "Linux Agent", "macOS Agent" → Different platforms (keep separate for clarity)

**If documents are about DIFFERENT topics, OUTPUT THEM SEPARATELY. DO NOT MERGE.**

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

1. **VALIDATE RELATEDNESS FIRST**: Before merging, confirm documents are about the SAME specific topic
2. **Merge Related Content ONLY**: Only combine pages about the identical topic
3. **Keep Unrelated Content Separate**: If documents cover different topics, output them separately
4. **Preserve Technical Depth**: Keep ALL technical details - commands, configs, code examples, parameters
5. **Make Self-Contained**: Each topic should be complete - no "see page X for details"
6. **No Summarization**: Include FULL content, not summaries
7. **Optimize Structure**: Use clear headings, bullet points, code blocks
8. **Add Keywords**: Think about how LLMs might search for this content

## Quality Standards

- **COMPLETE**: Each topic is fully self-contained with ALL technical details
- **FOCUSED**: Each topic covers exactly ONE specific concept/task/reference
- **COHERENT**: All content in a topic must be directly related
- **DETAILED**: Technical, specific, and comprehensive (not vague)
- **STRUCTURED**: Clear hierarchy and formatting
- **SEARCHABLE**: Includes multiple phrasings and keywords
- **ACCURATE**: Preserves all technical accuracy exactly

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
