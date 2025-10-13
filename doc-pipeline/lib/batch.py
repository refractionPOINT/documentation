"""Semantic batching of documentation pages using Claude."""
import json
import re
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


def _extract_json_from_markdown(text: str) -> str:
    """
    Extract JSON from markdown code fences.

    Claude often wraps JSON responses in markdown code fences like:
    ```json
    {...}
    ```

    This function extracts the JSON content, or returns the original
    text if no fences are found.

    Args:
        text: Text that may contain markdown-wrapped JSON

    Returns:
        Extracted JSON string, or original text if no fences found
    """
    # Pattern matches ```json or ``` followed by content, then closing ```
    pattern = r'```(?:json)?\s*\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        return match.group(1)

    # No fences found, return original
    return text


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

        # Extract JSON from markdown code fences if present
        json_text = _extract_json_from_markdown(response)

        # Parse response with error handling
        try:
            batch_data = json.loads(json_text)
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
