You are processing a batch of related LimaCharlie documentation pages to create LLM-optimized markdown.

## Batch Information

**Batch ID:** {batch_id}
**Theme:** {theme}
**Pages in this batch:** {page_count}

## Pages to Process

{pages_content}

## Your Task

For each page, generate LLM-optimized documentation by:

1. **Understanding the PURPOSE**: Is this a tutorial, reference, concept explanation, or troubleshooting guide?

2. **Extracting semantic meaning**: Go beyond text to understand concepts, relationships, prerequisites

3. **Identifying key elements**:
   - API methods/functions with complete signatures and descriptions
   - Code examples with explanations of when/why to use them
   - Prerequisites and related concepts
   - Warnings, gotchas, common pitfalls
   - Cross-references to other pages IN THIS BATCH

4. **Generating enhanced markdown** that:
   - Preserves 100% technical accuracy from source HTML
   - Adds context where implicit (e.g., "This requires you to first...")
   - Uses semantic markup (> **Warning:**, > **Note:**, etc.)
   - Links to related pages with relationship type
   - Optimizes heading hierarchy for scanning

## Output Format

Return JSON with this exact structure:

```json
{{
  "pages": [
    {{
      "slug": "page-slug",
      "enhanced_markdown": "# Title\n\nContent...",
      "extracted_apis": [
        {{
          "name": "function_name()",
          "signature": "full signature with types",
          "description": "what it does and when to use it"
        }}
      ],
      "cross_refs": [
        {{
          "page": "related-page-slug",
          "relationship": "prerequisite|continuation|alternative|debugging"
        }}
      ],
      "metadata": {{
        "summary": "one-sentence summary",
        "keywords": ["key", "words"],
        "complexity": "beginner|intermediate|advanced"
      }}
    }}
  ]
}}
```

**Critical**: Output ONLY valid JSON. No markdown code blocks, no explanatory text.
