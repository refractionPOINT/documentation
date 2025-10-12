"""Claude-powered understanding and enhancement of documentation pages."""
import json
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ProcessedPage:
    """Result of processing a page through Claude."""
    slug: str
    enhanced_markdown: str
    extracted_apis: List[Dict[str, str]]
    cross_refs: List[Dict[str, str]]
    metadata: Dict[str, Any]


def generate_batch_prompt(batch: Dict[str, Any]) -> str:
    """
    Generate prompt for processing a batch of pages.

    Args:
        batch: Batch dictionary with id, theme, and pages

    Returns:
        Prompt string for Claude
    """
    # Load template
    template_path = Path(__file__).parent.parent / 'prompts' / 'batch_processing.md'
    template = template_path.read_text()

    # Format pages content
    pages_content = []
    for i, page in enumerate(batch['pages'], 1):
        pages_content.append(f"""
### Page {i}: {page.title}

**Slug:** {page.slug}
**URL:** {page.url}

**HTML Content:**
```html
{page.raw_html}
```
""")

    # Fill template
    prompt = template.format(
        batch_id=batch['id'],
        theme=batch['theme'],
        page_count=len(batch['pages']),
        pages_content='\n'.join(pages_content)
    )

    return prompt


def parse_batch_output(output: str) -> List[ProcessedPage]:
    """
    Parse Claude's batch processing output.

    Args:
        output: JSON output from Claude

    Returns:
        List of ProcessedPage objects
    """
    data = json.loads(output)

    pages = []
    for page_data in data['pages']:
        pages.append(ProcessedPage(
            slug=page_data['slug'],
            enhanced_markdown=page_data['enhanced_markdown'],
            extracted_apis=page_data['extracted_apis'],
            cross_refs=page_data['cross_refs'],
            metadata=page_data['metadata']
        ))

    return pages
