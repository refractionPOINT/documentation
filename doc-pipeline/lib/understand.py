"""Claude-powered understanding and enhancement of documentation pages."""
import json
import asyncio
import tempfile
from typing import List, Dict, Any, Tuple
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


async def process_batch_async(
    batch: Dict[str, Any],
    claude_client: Any
) -> Tuple[str, List[ProcessedPage]]:
    """
    Process a single batch asynchronously.

    Args:
        batch: Batch to process
        claude_client: Claude client instance

    Returns:
        Tuple of (batch_id, list of processed pages)
    """
    # Generate prompt
    prompt = generate_batch_prompt(batch)

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(
            None,
            claude_client.run_subagent_prompt,
            prompt_file
        )

        # Parse output
        pages = parse_batch_output(output)

        return batch['id'], pages

    finally:
        Path(prompt_file).unlink()


async def process_batch_with_retry(
    batch: Dict[str, Any],
    claude_client: Any,
    max_retries: int = 3
) -> Tuple[str, List[ProcessedPage]]:
    """
    Process batch with retry logic.

    Args:
        batch: Batch to process
        claude_client: Claude client
        max_retries: Maximum retry attempts

    Returns:
        Tuple of (batch_id, processed pages)

    Raises:
        RuntimeError: If all retries exhausted
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            return await process_batch_async(batch, claude_client)
        except Exception as e:
            last_error = e
            print(f"Batch {batch['id']} failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    raise RuntimeError(f"Batch {batch['id']} failed after {max_retries} attempts: {last_error}")


async def process_batches_parallel(
    batches: List[Dict[str, Any]],
    claude_client: Any,
    max_concurrent: int = 10
) -> Dict[str, List[ProcessedPage]]:
    """
    Process multiple batches in parallel with retry logic.

    Args:
        batches: List of batches to process
        claude_client: Claude client instance
        max_concurrent: Max number of concurrent subagents (default 10)

    Returns:
        Dictionary mapping batch_id to processed pages
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_limit(batch):
        async with semaphore:
            return await process_batch_with_retry(batch, claude_client)  # Use retry version

    tasks = [process_with_limit(batch) for batch in batches]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    processed = {}
    failed = []

    for result in results:
        if isinstance(result, Exception):
            failed.append(str(result))
            continue
        batch_id, pages = result
        processed[batch_id] = pages

    if failed:
        print(f"WARNING: {len(failed)} batches failed:")
        for error in failed:
            print(f"  - {error}")

    return processed
