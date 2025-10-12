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
    claude_client: ClaudeClient
) -> List[Dict[str, Any]]:
    """
    Group pages into semantic batches using Claude.

    Args:
        pages: List of pages to batch
        claude_client: Claude client for making requests

    Returns:
        List of batch dictionaries with structure:
        {
            'id': 'batch_01_name',
            'theme': 'Description of batch theme',
            'pages': [Page, Page, ...],
            'page_slugs': ['slug1', 'slug2', ...]
        }
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
