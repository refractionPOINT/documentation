"""Smart categorization using Claude for semantic understanding."""
import json
import tempfile
from typing import List, Dict, Tuple
from pathlib import Path

try:
    from ..models import Page
    from .claude_client import ClaudeClient
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from models import Page
    from lib.claude_client import ClaudeClient


def get_semantic_categories() -> Dict[str, str]:
    """
    Define semantic categories for LLM-optimized documentation.

    Returns dict mapping category slug to description.
    No numbered prefixes - pure semantic organization.
    """
    return {
        "getting-started": "Introduction, quickstart, and use cases",
        "sensors": "Endpoint agents, installation, configuration",
        "events": "Telemetry, event types, event schemas",
        "query": "LCQL, querying, search capabilities",
        "detection-response": "D&R rules, detection logic, response actions",
        "platform": "Platform management, organizations, API keys, SDK",
        "adapters": "Data ingestion adapters (all sources)",
        "outputs": "Data export destinations (all outputs)",
        "integrations": "Third-party API integrations",
        "add-ons": "Extensions and add-on services",
        "tutorials": "Guides, walkthroughs, examples",
        "reference": "API references, command lists, technical specs",
        "faq": "Frequently asked questions",
        "other": "Uncategorized content"
    }


def categorize_pages_with_claude(
    pages: List[Page],
    claude_client: ClaudeClient
) -> Dict[str, str]:
    """
    Use Claude to semantically categorize pages.

    Args:
        pages: List of pages with slugs and titles
        claude_client: Claude client for API calls

    Returns:
        Dict mapping slug to category
    """
    categories = get_semantic_categories()

    # Build page list for Claude
    page_info = []
    for page in pages:
        page_info.append({
            'slug': page.slug,
            'title': page.title,
        })

    prompt = f"""You are categorizing LimaCharlie documentation pages for an AI/LLM knowledge base.

AVAILABLE CATEGORIES:
{json.dumps(categories, indent=2)}

PAGES TO CATEGORIZE ({len(pages)} total):
{json.dumps(page_info, indent=2)}

CATEGORIZATION RULES:
1. Use slug AND title to understand page purpose
2. Prioritize specific patterns:
   - "adapter-types-*" → "adapters" (data ingestion)
   - "outputs-destinations-*" → "outputs" (data export)
   - "ext-*" → "add-ons"
   - "api-integrations-*" → "integrations"
   - "reference-*" → "reference"
3. Don't let generic keywords override specific patterns
   Example: "outputs-destinations-opensearch" → "outputs" (NOT "query")
4. Group by FUNCTION not just keyword matching
5. Default to "other" if uncertain

Output valid JSON only:
{{
  "categorization": {{
    "slug1": "category",
    "slug2": "category",
    ...
  }}
}}"""

    # Write prompt to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        response = claude_client.run_subagent_prompt(prompt_file)
        data = json.loads(response)
        return data.get('categorization', {})
    except Exception as e:
        print(f"Warning: Claude categorization failed: {e}")
        print("Falling back to rule-based categorization")
        return _fallback_categorization(pages)
    finally:
        Path(prompt_file).unlink()


def _fallback_categorization(pages: List[Page]) -> Dict[str, str]:
    """
    Fallback rule-based categorization if Claude fails.

    Uses priority-based pattern matching.
    """
    categorization = {}

    for page in pages:
        slug = page.slug.lower()

        # Priority 1: Exact prefix patterns (highest priority)
        if slug.startswith('adapter-types-') or slug.startswith('adapter-examples-'):
            category = 'adapters'
        elif slug.startswith('outputs-destinations-') or slug.startswith('output-destinations-'):
            category = 'outputs'
        elif slug.startswith('ext-'):
            category = 'add-ons'
        elif slug.startswith('api-integrations-'):
            category = 'integrations'
        elif slug.startswith('reference-'):
            category = 'reference'

        # Priority 2: Multi-word specific patterns
        elif 'adapter' in slug and ('type' in slug or 'usage' in slug or 'deployment' in slug):
            category = 'adapters'
        elif 'output' in slug and ('destination' in slug or 'export' in slug):
            category = 'outputs'

        # Priority 3: Category-specific keywords
        elif any(kw in slug for kw in ['quickstart', 'what-is', 'use-case', 'introduction']):
            category = 'getting-started'
        elif any(kw in slug for kw in ['sensor', 'installation', 'agent', 'endpoint', 'chrome-agent', 'docker-agent', 'edge-agent']):
            category = 'sensors'
        elif any(kw in slug for kw in ['event-schema', 'edr-event', 'telemetry', 'ingesting']) and 'adapter' not in slug:
            category = 'events'
        elif any(kw in slug for kw in ['lcql', 'query-console', 'query-with']):
            category = 'query'
        elif any(kw in slug for kw in ['detection', 'response', 'replay', 'd-r', 'rule', 'soteria']):
            category = 'detection-response'
        elif any(kw in slug for kw in ['platform', 'organization', 'api-key', 'sdk', 'limacharlie-sdk']):
            category = 'platform'
        elif any(kw in slug for kw in ['tutorial', 'guide', 'walkthrough']):
            category = 'tutorials'
        elif 'faq' in slug:
            category = 'faq'
        elif any(kw in slug for kw in ['release', 'changelog']):
            category = 'other'
        else:
            category = 'other'

        categorization[page.slug] = category

    return categorization


def apply_categorization(
    pages: List[Page],
    categorization: Dict[str, str]
) -> Dict[str, List[Page]]:
    """
    Apply categorization results to pages and group them.

    Args:
        pages: List of pages to categorize
        categorization: Dict mapping slug to category

    Returns:
        Dict mapping category to list of pages
    """
    categories = {}

    for page in pages:
        category = categorization.get(page.slug, 'other')
        page.category = category

        if category not in categories:
            categories[category] = []
        categories[category].append(page)

    return categories


def categorize_pages_batch(
    pages: List[Page],
    claude_client: ClaudeClient,
    batch_size: int = 100
) -> Dict[str, List[Page]]:
    """
    Categorize pages in batches using Claude.

    For large datasets, processes in chunks to avoid overwhelming Claude.

    Args:
        pages: All pages to categorize
        claude_client: Claude client
        batch_size: Max pages per Claude request

    Returns:
        Dict mapping category to list of pages
    """
    all_categorization = {}

    # Process in batches
    for i in range(0, len(pages), batch_size):
        batch = pages[i:i + batch_size]
        print(f"  Categorizing batch {i//batch_size + 1} ({len(batch)} pages)...")

        batch_categorization = categorize_pages_with_claude(batch, claude_client)
        all_categorization.update(batch_categorization)

    # Apply categorization
    return apply_categorization(pages, all_categorization)
