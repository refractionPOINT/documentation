"""Synthesis of processed documentation into coherent knowledge base."""
import json
from typing import List, Dict, Any
from collections import defaultdict
import tempfile
from pathlib import Path
from .understand import ProcessedPage
from .claude_client import ClaudeClient


def build_api_index(
    pages: List[ProcessedPage],
    claude_client: ClaudeClient
) -> str:
    """
    Build comprehensive API index from all extracted APIs.

    Args:
        pages: All processed pages
        claude_client: Claude client for synthesis

    Returns:
        Markdown API index
    """
    # Collect all APIs
    all_apis = []
    api_to_pages = defaultdict(list)

    for page in pages:
        for api in page.extracted_apis:
            api_name = api['name']
            api_to_pages[api_name].append(page.slug)
            all_apis.append({
                'name': api_name,
                'signature': api['signature'],
                'description': api['description'],
                'pages': api_to_pages[api_name]
            })

    # Deduplicate by name
    unique_apis = {}
    for api in all_apis:
        name = api['name']
        if name not in unique_apis:
            unique_apis[name] = api
        else:
            # Merge page references
            unique_apis[name]['pages'] = list(set(
                unique_apis[name]['pages'] + api['pages']
            ))

    # Ask Claude to organize and enrich
    apis_json = json.dumps(list(unique_apis.values()), indent=2)

    prompt = f"""Create a comprehensive API index from these extracted APIs.

APIs:
{apis_json}

Organize by:
1. Category (Sensor APIs, Detection APIs, Platform APIs, etc.)
2. Alphabetically within category
3. Include signature and description
4. List all pages where each API appears

Output markdown with this structure:

# API Index

## Category Name

- `api_name(signature)`: Description
  - Pages: page1, page2

Output only the markdown, no code blocks."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        return claude_client.run_subagent_prompt(prompt_file)
    finally:
        Path(prompt_file).unlink()


def resolve_cross_references(pages: List[ProcessedPage]) -> List[ProcessedPage]:
    """
    Resolve cross-references and add bidirectional links.

    Args:
        pages: Processed pages with cross-references

    Returns:
        Pages with resolved cross-reference links in markdown
    """
    # Build slug to page mapping
    page_map = {p.slug: p for p in pages}

    # Track reverse references
    reverse_refs = defaultdict(list)

    for page in pages:
        for ref in page.cross_refs:
            target_slug = ref['page']
            relationship = ref['relationship']
            reverse_refs[target_slug].append({
                'page': page.slug,
                'relationship': relationship
            })

    # Add cross-reference sections to markdown
    enhanced_pages = []

    for page in pages:
        markdown = page.enhanced_markdown

        # Add forward references
        if page.cross_refs:
            markdown += "\n\n## Related Documentation\n\n"
            for ref in page.cross_refs:
                rel_type = ref['relationship'].replace('_', ' ').title()
                target_page = page_map.get(ref['page'])
                if target_page:
                    markdown += f"- **{rel_type}**: [{target_page.slug}]({target_page.slug}.md)\n"

        # Add reverse references
        if page.slug in reverse_refs:
            if not page.cross_refs:
                markdown += "\n\n## Related Documentation\n\n"
            for ref in reverse_refs[page.slug]:
                rel_type = ref['relationship'].replace('_', ' ').title()
                source_page = page_map.get(ref['page'])
                if source_page:
                    markdown += f"- **Referenced by** ({rel_type}): [{source_page.slug}]({source_page.slug}.md)\n"

        enhanced_pages.append(ProcessedPage(
            slug=page.slug,
            enhanced_markdown=markdown,
            extracted_apis=page.extracted_apis,
            cross_refs=page.cross_refs,
            metadata=page.metadata
        ))

    return enhanced_pages
