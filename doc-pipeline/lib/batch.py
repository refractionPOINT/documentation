"""Semantic batching of documentation pages using Claude."""
import json
from typing import List, Dict, Any
from pathlib import Path

# Import from parent package
try:
    from ..models import Page
    from .claude_client import ClaudeClient
except ImportError:
    # Fallback for direct execution or testing
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models import Page
    from lib.claude_client import ClaudeClient


def create_semantic_batches(
    pages: List[Page],
    claude_client: ClaudeClient,
    max_pages_per_request: int = 30
) -> List[Dict[str, Any]]:
    """
    Group pages into semantic batches using Claude.

    For large page lists, automatically chunks into smaller groups to avoid
    overwhelming Claude with too much context.

    Args:
        pages: List of pages to batch
        claude_client: Claude client for making requests
        max_pages_per_request: Maximum pages to send to Claude at once (default 30)

    Returns:
        List of batch dictionaries with structure:
        {
            'id': 'batch_01_name',
            'theme': 'Description of batch theme',
            'pages': [Page, Page, ...],
            'page_slugs': ['slug1', 'slug2', ...]
        }
    """
    # If page list is small enough, batch directly
    if len(pages) <= max_pages_per_request:
        return _batch_pages_with_claude(pages, claude_client)

    # For large lists, batch by category first
    print(f"  Large dataset ({len(pages)} pages) - batching by category...")

    # Group pages by category
    by_category: Dict[str, List[Page]] = {}
    for page in pages:
        category = page.category or 'uncategorized'
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(page)

    # Batch each category separately
    all_batches = []
    batch_counter = 0

    for category_name, category_pages in sorted(by_category.items()):
        print(f"  Batching category: {category_name} ({len(category_pages)} pages)")

        # Batch this category
        category_batches = _batch_pages_with_claude(category_pages, claude_client)

        # Renumber batch IDs to be globally unique
        for batch in category_batches:
            batch_counter += 1
            old_id = batch['id']
            # Keep descriptive name but ensure unique numbering
            name_part = old_id.split('_', 2)[-1] if '_' in old_id else old_id
            batch['id'] = f"batch_{batch_counter:02d}_{name_part}"

        all_batches.extend(category_batches)

    return all_batches


def _batch_pages_with_claude(
    pages: List[Page],
    claude_client: ClaudeClient
) -> List[Dict[str, Any]]:
    """
    Internal function to batch a list of pages using Claude.

    Assumes page list is reasonably sized (<= 30 pages).
    """
    # Create prompt for Claude
    page_list = "\n".join([
        f"- {p.slug}: {p.title}"
        for p in pages
    ])

    prompt = f"""You are grouping documentation pages into semantic batches for parallel processing.

PAGES ({len(pages)} total):
{page_list}

Create batches with these criteria:
1. Each batch contains 5-10 related pages
2. Pages in a batch share a common theme/topic
3. Users would likely read these pages together
4. Batches represent coherent workflows or concepts

Output JSON format:
{{
  "batches": [
    {{
      "id": "batch_01_descriptive_name",
      "theme": "Brief description of what this batch covers",
      "page_slugs": ["slug1", "slug2", ...]
    }}
  ]
}}

Output only valid JSON, no markdown formatting."""

    # Write prompt to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        # Get batching from Claude
        response = claude_client.run_subagent_prompt(prompt_file)

        # Parse response with error handling
        try:
            batch_data = json.loads(response)
        except json.JSONDecodeError as e:
            raise ValueError(f"Claude returned invalid JSON: {e}") from e

        # Validate response structure
        if 'batches' not in batch_data:
            raise ValueError("Claude response missing 'batches' key")

        if not batch_data['batches']:
            # Empty result - return empty list
            return []

        # Build batch objects with actual Page references
        page_map = {p.slug: p for p in pages}
        batches = []

        for i, batch_def in enumerate(batch_data['batches']):
            # Validate required keys
            for required_key in ['id', 'theme', 'page_slugs']:
                if required_key not in batch_def:
                    raise ValueError(f"Batch {i} missing required key: {required_key}")

            batch = {
                'id': batch_def['id'],
                'theme': batch_def['theme'],
                'page_slugs': batch_def['page_slugs'],
                'pages': [page_map[slug] for slug in batch_def['page_slugs']
                         if slug in page_map]
            }
            batches.append(batch)

        return batches

    finally:
        Path(prompt_file).unlink()
