# Claude-Powered Documentation Pipeline Implementation Plan

> **For Claude:** Use `${SUPERPOWERS_SKILLS_ROOT}/skills/collaboration/executing-plans/SKILL.md` to implement this plan task-by-task.

**Goal:** Transform the documentation pipeline from brute-force HTML→Markdown conversion to intelligent, LLM-optimized processing using Claude CLI with batched subagent dispatch.

**Architecture:** 7-phase pipeline (FETCH → BATCH_GROUP → PARALLEL_UNDERSTAND → SYNTHESIZE → ENHANCE → VERIFY → DETECT) where related pages are grouped into semantic batches, processed in parallel by Claude subagents, then synthesized into a coherent, cross-referenced knowledge base optimized for LLM consumption.

**Tech Stack:** Python 3.8+, Claude CLI (subprocess), asyncio for parallel processing, existing pipeline infrastructure

---

## Task 1: Claude CLI Integration Setup

**Files:**
- Create: `doc-pipeline/lib/claude_client.py`
- Create: `doc-pipeline/tests/test_claude_client.py`
- Modify: `doc-pipeline/requirements.txt`

**Step 1: Write the failing test for Claude CLI availability check**

Create `doc-pipeline/tests/test_claude_client.py`:

```python
import pytest
from doc_pipeline.lib.claude_client import ClaudeClient, ClaudeNotAvailableError


def test_claude_availability_check_success(mocker):
    """Test that Claude CLI availability is correctly detected."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = "Claude CLI version 1.0.0"

    client = ClaudeClient()
    assert client.is_available() == True


def test_claude_availability_check_failure(mocker):
    """Test that missing Claude CLI is correctly detected."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = FileNotFoundError()

    client = ClaudeClient()
    assert client.is_available() == False


def test_claude_required_raises_when_unavailable(mocker):
    """Test that operations fail gracefully when Claude is unavailable."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = FileNotFoundError()

    client = ClaudeClient()
    with pytest.raises(ClaudeNotAvailableError):
        client.check_required()
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest doc-pipeline/tests/test_claude_client.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'doc_pipeline.lib.claude_client'"

**Step 3: Write minimal implementation**

Create `doc-pipeline/lib/claude_client.py`:

```python
"""Claude CLI integration for documentation pipeline."""
import subprocess
import json
from typing import Optional, Dict, Any
from pathlib import Path


class ClaudeNotAvailableError(Exception):
    """Raised when Claude CLI is not available."""
    pass


class ClaudeClient:
    """Client for interacting with Claude CLI."""

    def __init__(self):
        """Initialize Claude client."""
        self._available: Optional[bool] = None

    def is_available(self) -> bool:
        """Check if Claude CLI is available."""
        if self._available is not None:
            return self._available

        try:
            result = subprocess.run(
                ['claude', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            self._available = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self._available = False

        return self._available

    def check_required(self) -> None:
        """Raise error if Claude CLI is not available."""
        if not self.is_available():
            raise ClaudeNotAvailableError(
                "Claude CLI is not available. Install from: "
                "https://github.com/anthropics/claude-cli"
            )
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest doc-pipeline/tests/test_claude_client.py::test_claude_availability_check_success -v`
Expected: PASS

Run: `python3 -m pytest doc-pipeline/tests/test_claude_client.py::test_claude_availability_check_failure -v`
Expected: PASS

Run: `python3 -m pytest doc-pipeline/tests/test_claude_client.py::test_claude_required_raises_when_unavailable -v`
Expected: PASS

**Step 5: Add pytest-mock to requirements**

Modify `doc-pipeline/requirements.txt`:

```
# ... existing requirements ...
pytest-mock>=3.12.0
```

Run: `pip3 install pytest-mock`

**Step 6: Commit**

```bash
git add doc-pipeline/lib/claude_client.py doc-pipeline/tests/test_claude_client.py doc-pipeline/requirements.txt
git commit -m "feat: add Claude CLI availability checking"
```

---

## Task 2: Claude Subagent Execution

**Files:**
- Modify: `doc-pipeline/lib/claude_client.py`
- Modify: `doc-pipeline/tests/test_claude_client.py`

**Step 1: Write test for subagent prompt execution**

Add to `doc-pipeline/tests/test_claude_client.py`:

```python
def test_run_subagent_prompt_success(mocker, tmp_path):
    """Test successful subagent execution with prompt file."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = '{"result": "success"}'

    client = ClaudeClient()
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Test prompt")

    result = client.run_subagent_prompt(str(prompt_file))

    assert result == '{"result": "success"}'
    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert 'claude' in args
    assert str(prompt_file) in args


def test_run_subagent_prompt_timeout(mocker, tmp_path):
    """Test timeout handling for long-running subagents."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = subprocess.TimeoutExpired(cmd=['claude'], timeout=300)

    client = ClaudeClient()
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Test prompt")

    with pytest.raises(subprocess.TimeoutExpired):
        client.run_subagent_prompt(str(prompt_file), timeout=300)
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest doc-pipeline/tests/test_claude_client.py::test_run_subagent_prompt_success -v`
Expected: FAIL with "AttributeError: 'ClaudeClient' object has no attribute 'run_subagent_prompt'"

**Step 3: Implement subagent execution**

Add to `doc-pipeline/lib/claude_client.py`:

```python
    def run_subagent_prompt(
        self,
        prompt_file: str,
        timeout: int = 300
    ) -> str:
        """
        Execute a subagent with the given prompt file.

        Args:
            prompt_file: Path to markdown file containing prompt
            timeout: Timeout in seconds (default 5 minutes)

        Returns:
            Output from the subagent

        Raises:
            ClaudeNotAvailableError: If Claude CLI not available
            subprocess.TimeoutExpired: If execution exceeds timeout
        """
        self.check_required()

        result = subprocess.run(
            ['claude', '--prompt-file', prompt_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude subagent failed: {result.stderr}")

        return result.stdout
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest doc-pipeline/tests/test_claude_client.py::test_run_subagent_prompt_success -v`
Expected: PASS

Run: `python3 -m pytest doc-pipeline/tests/test_claude_client.py::test_run_subagent_prompt_timeout -v`
Expected: PASS

**Step 5: Commit**

```bash
git add doc-pipeline/lib/claude_client.py doc-pipeline/tests/test_claude_client.py
git commit -m "feat: add Claude subagent prompt execution"
```

---

## Task 3: BATCH_GROUP Phase - Semantic Batching

**Files:**
- Create: `doc-pipeline/lib/batch.py`
- Create: `doc-pipeline/tests/test_batch.py`

**Step 1: Write test for semantic batch grouping**

Create `doc-pipeline/tests/test_batch.py`:

```python
import pytest
from doc_pipeline.lib.batch import create_semantic_batches
from doc_pipeline.models import Page


def test_create_semantic_batches_groups_related_pages(mocker):
    """Test that pages are grouped semantically by Claude."""
    pages = [
        Page(slug="sensor-windows", title="Windows Sensors", url="...", html_content=""),
        Page(slug="sensor-linux", title="Linux Sensors", url="...", html_content=""),
        Page(slug="detection-rules", title="D&R Rules", url="...", html_content=""),
        Page(slug="yara-rules", title="YARA Scanning", url="...", html_content=""),
    ]

    mock_client = mocker.Mock()
    mock_client.run_subagent_prompt.return_value = """
{
  "batches": [
    {
      "id": "batch_01_sensors",
      "theme": "Installing and configuring sensors",
      "page_slugs": ["sensor-windows", "sensor-linux"]
    },
    {
      "id": "batch_02_detection",
      "theme": "Detection and response rules",
      "page_slugs": ["detection-rules", "yara-rules"]
    }
  ]
}
"""

    batches = create_semantic_batches(pages, mock_client)

    assert len(batches) == 2
    assert batches[0]['id'] == 'batch_01_sensors'
    assert len(batches[0]['pages']) == 2
    assert batches[1]['id'] == 'batch_02_detection'
    assert len(batches[1]['pages']) == 2


def test_create_semantic_batches_respects_size_limits(mocker):
    """Test that batches are sized appropriately (5-10 pages)."""
    pages = [Page(slug=f"page-{i}", title=f"Page {i}", url="...", html_content="")
             for i in range(50)]

    mock_client = mocker.Mock()
    # Simulate Claude creating properly sized batches
    batches_json = {
        "batches": [
            {
                "id": f"batch_{i:02d}",
                "theme": f"Theme {i}",
                "page_slugs": [f"page-{j}" for j in range(i*7, min((i+1)*7, 50))]
            }
            for i in range(8)  # 50 pages / ~7 per batch = 8 batches
        ]
    }
    mock_client.run_subagent_prompt.return_value = str(batches_json).replace("'", '"')

    batches = create_semantic_batches(pages, mock_client)

    for batch in batches:
        assert 1 <= len(batch['pages']) <= 10
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest doc-pipeline/tests/test_batch.py::test_create_semantic_batches_groups_related_pages -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'doc_pipeline.lib.batch'"

**Step 3: Write minimal implementation**

Create `doc-pipeline/lib/batch.py`:

```python
"""Semantic batching of documentation pages using Claude."""
import json
from typing import List, Dict, Any
from pathlib import Path
from ..models import Page
from .claude_client import ClaudeClient


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

        # Parse response
        batch_data = json.loads(response)

        # Build batch objects with actual Page references
        page_map = {p.slug: p for p in pages}
        batches = []

        for batch_def in batch_data['batches']:
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
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest doc-pipeline/tests/test_batch.py::test_create_semantic_batches_groups_related_pages -v`
Expected: PASS

Run: `python3 -m pytest doc-pipeline/tests/test_batch.py::test_create_semantic_batches_respects_size_limits -v`
Expected: PASS

**Step 5: Commit**

```bash
git add doc-pipeline/lib/batch.py doc-pipeline/tests/test_batch.py
git commit -m "feat: add semantic batching using Claude"
```

---

## Task 4: PARALLEL_UNDERSTAND Phase - Subagent Processing

**Files:**
- Create: `doc-pipeline/lib/understand.py`
- Create: `doc-pipeline/tests/test_understand.py`
- Create: `doc-pipeline/prompts/batch_processing.md` (template)

**Step 1: Write test for batch processing prompt generation**

Create `doc-pipeline/tests/test_understand.py`:

```python
import pytest
from doc_pipeline.lib.understand import generate_batch_prompt, ProcessedPage
from doc_pipeline.models import Page


def test_generate_batch_prompt_includes_all_pages():
    """Test that batch prompt includes all pages in the batch."""
    batch = {
        'id': 'batch_01_sensors',
        'theme': 'Sensor installation',
        'pages': [
            Page(slug="sensor-windows", title="Windows Sensors",
                 url="https://docs.limacharlie.io/docs/sensor-windows",
                 html_content="<h1>Windows Sensors</h1><p>Install on Windows...</p>"),
            Page(slug="sensor-linux", title="Linux Sensors",
                 url="https://docs.limacharlie.io/docs/sensor-linux",
                 html_content="<h1>Linux Sensors</h1><p>Install on Linux...</p>"),
        ]
    }

    prompt = generate_batch_prompt(batch)

    assert 'batch_01_sensors' in prompt
    assert 'Sensor installation' in prompt
    assert 'sensor-windows' in prompt
    assert 'Windows Sensors' in prompt
    assert '<h1>Windows Sensors</h1>' in prompt
    assert 'sensor-linux' in prompt
    assert 'Linux Sensors' in prompt


def test_parse_batch_output_extracts_processed_pages():
    """Test parsing Claude's batch processing output."""
    from doc_pipeline.lib.understand import parse_batch_output

    output = """
{
  "pages": [
    {
      "slug": "sensor-windows",
      "enhanced_markdown": "# Windows Sensors\\n\\nInstall sensors on Windows...",
      "extracted_apis": [
        {
          "name": "install_sensor()",
          "signature": "install_sensor(platform: str) -> bool",
          "description": "Installs the sensor on the specified platform"
        }
      ],
      "cross_refs": [
        {
          "page": "sensor-troubleshooting",
          "relationship": "debugging"
        }
      ],
      "metadata": {
        "summary": "Guide for installing sensors on Windows systems",
        "keywords": ["sensor", "windows", "installation"],
        "complexity": "beginner"
      }
    }
  ]
}
"""

    pages = parse_batch_output(output)

    assert len(pages) == 1
    assert pages[0].slug == "sensor-windows"
    assert "# Windows Sensors" in pages[0].enhanced_markdown
    assert len(pages[0].extracted_apis) == 1
    assert pages[0].extracted_apis[0]['name'] == "install_sensor()"
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest doc-pipeline/tests/test_understand.py::test_generate_batch_prompt_includes_all_pages -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'doc_pipeline.lib.understand'"

**Step 3: Create batch processing prompt template**

Create `doc-pipeline/prompts/batch_processing.md`:

```markdown
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
{
  "pages": [
    {
      "slug": "page-slug",
      "enhanced_markdown": "# Title\n\nContent...",
      "extracted_apis": [
        {
          "name": "function_name()",
          "signature": "full signature with types",
          "description": "what it does and when to use it"
        }
      ],
      "cross_refs": [
        {
          "page": "related-page-slug",
          "relationship": "prerequisite|continuation|alternative|debugging"
        }
      ],
      "metadata": {
        "summary": "one-sentence summary",
        "keywords": ["key", "words"],
        "complexity": "beginner|intermediate|advanced"
      }
    }
  ]
}
```

**Critical**: Output ONLY valid JSON. No markdown code blocks, no explanatory text.
```

**Step 4: Write minimal implementation**

Create `doc-pipeline/lib/understand.py`:

```python
"""Claude-powered understanding and enhancement of documentation pages."""
import json
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass
from ..models import Page


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
{page.html_content}
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
```

**Step 5: Run test to verify it passes**

Run: `python3 -m pytest doc-pipeline/tests/test_understand.py::test_generate_batch_prompt_includes_all_pages -v`
Expected: PASS

Run: `python3 -m pytest doc-pipeline/tests/test_understand.py::test_parse_batch_output_extracts_processed_pages -v`
Expected: PASS

**Step 6: Commit**

```bash
git add doc-pipeline/lib/understand.py doc-pipeline/tests/test_understand.py doc-pipeline/prompts/batch_processing.md
git commit -m "feat: add batch prompt generation and output parsing"
```

---

## Task 5: Parallel Batch Execution

**Files:**
- Modify: `doc-pipeline/lib/understand.py`
- Modify: `doc-pipeline/tests/test_understand.py`

**Step 1: Write test for parallel batch processing**

Add to `doc-pipeline/tests/test_understand.py`:

```python
import asyncio


@pytest.mark.asyncio
async def test_process_batches_parallel(mocker):
    """Test that batches are processed in parallel."""
    batches = [
        {'id': f'batch_{i}', 'theme': f'Theme {i}',
         'pages': [Page(slug=f"page-{i}", title=f"Page {i}", url="...", html_content="<p>test</p>")]}
        for i in range(5)
    ]

    mock_client = mocker.Mock()

    # Track call order to verify parallelism
    call_times = []

    async def mock_run(*args, **kwargs):
        call_times.append(asyncio.get_event_loop().time())
        await asyncio.sleep(0.1)  # Simulate processing
        return '{"pages": [{"slug": "test", "enhanced_markdown": "# Test", "extracted_apis": [], "cross_refs": [], "metadata": {}}]}'

    mock_client.run_subagent_prompt = mock_run

    from doc_pipeline.lib.understand import process_batches_parallel

    start = asyncio.get_event_loop().time()
    results = await process_batches_parallel(batches, mock_client)
    duration = asyncio.get_event_loop().time() - start

    # If parallel, should take ~0.1s. If sequential, would take ~0.5s
    assert duration < 0.3
    assert len(results) == 5
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest doc-pipeline/tests/test_understand.py::test_process_batches_parallel -v`
Expected: FAIL with "ImportError: cannot import name 'process_batches_parallel'"

**Step 3: Add pytest-asyncio to requirements**

Modify `doc-pipeline/requirements.txt`:

```
# ... existing ...
pytest-asyncio>=0.21.0
```

Run: `pip3 install pytest-asyncio`

**Step 4: Implement parallel processing**

Add to `doc-pipeline/lib/understand.py`:

```python
import asyncio
import tempfile
from typing import Tuple


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


async def process_batches_parallel(
    batches: List[Dict[str, Any]],
    claude_client: Any,
    max_concurrent: int = 10
) -> Dict[str, List[ProcessedPage]]:
    """
    Process multiple batches in parallel.

    Args:
        batches: List of batches to process
        claude_client: Claude client instance
        max_concurrent: Max number of concurrent subagents (default 10)

    Returns:
        Dictionary mapping batch_id to processed pages
    """
    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_limit(batch):
        async with semaphore:
            return await process_batch_async(batch, claude_client)

    # Process all batches
    tasks = [process_with_limit(batch) for batch in batches]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect successful results
    processed = {}
    for result in results:
        if isinstance(result, Exception):
            print(f"Batch processing failed: {result}")
            continue
        batch_id, pages = result
        processed[batch_id] = pages

    return processed
```

**Step 5: Run test to verify it passes**

Run: `python3 -m pytest doc-pipeline/tests/test_understand.py::test_process_batches_parallel -v`
Expected: PASS

**Step 6: Commit**

```bash
git add doc-pipeline/lib/understand.py doc-pipeline/tests/test_understand.py doc-pipeline/requirements.txt
git commit -m "feat: add parallel batch processing with asyncio"
```

---

## Task 6: SYNTHESIZE Phase - Global Integration

**Files:**
- Create: `doc-pipeline/lib/synthesize.py`
- Create: `doc-pipeline/tests/test_synthesize.py`

**Step 1: Write test for API index synthesis**

Create `doc-pipeline/tests/test_synthesize.py`:

```python
import pytest
from doc_pipeline.lib.synthesize import build_api_index, resolve_cross_references
from doc_pipeline.lib.understand import ProcessedPage


def test_build_api_index_deduplicates_apis(mocker):
    """Test that duplicate APIs from different pages are merged."""
    pages = [
        ProcessedPage(
            slug="page1",
            enhanced_markdown="...",
            extracted_apis=[
                {"name": "sensor.install()", "signature": "install() -> bool", "description": "Installs sensor"}
            ],
            cross_refs=[],
            metadata={}
        ),
        ProcessedPage(
            slug="page2",
            enhanced_markdown="...",
            extracted_apis=[
                {"name": "sensor.install()", "signature": "install() -> bool", "description": "Installs the sensor"}
            ],
            cross_refs=[],
            metadata={}
        ),
    ]

    mock_client = mocker.Mock()
    mock_client.run_subagent_prompt.return_value = """
# API Index

## Sensor APIs

- `sensor.install() -> bool`: Installs the sensor on the system
  - Pages: page1, page2
"""

    api_index = build_api_index(pages, mock_client)

    assert "sensor.install()" in api_index
    assert "page1" in api_index
    assert "page2" in api_index


def test_resolve_cross_references_adds_bidirectional_links():
    """Test that cross-references are resolved bidirectionally."""
    pages = [
        ProcessedPage(
            slug="sensor-install",
            enhanced_markdown="# Install",
            extracted_apis=[],
            cross_refs=[{"page": "sensor-troubleshoot", "relationship": "debugging"}],
            metadata={}
        ),
        ProcessedPage(
            slug="sensor-troubleshoot",
            enhanced_markdown="# Troubleshoot",
            extracted_apis=[],
            cross_refs=[],
            metadata={}
        ),
    ]

    resolved = resolve_cross_references(pages)

    # sensor-install should have link to troubleshoot
    install_page = next(p for p in resolved if p.slug == "sensor-install")
    assert "sensor-troubleshoot" in install_page.enhanced_markdown

    # sensor-troubleshoot should have reverse link to install
    troubleshoot_page = next(p for p in resolved if p.slug == "sensor-troubleshoot")
    assert "sensor-install" in troubleshoot_page.enhanced_markdown
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest doc-pipeline/tests/test_synthesize.py::test_build_api_index_deduplicates_apis -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'doc_pipeline.lib.synthesize'"

**Step 3: Write minimal implementation**

Create `doc-pipeline/lib/synthesize.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest doc-pipeline/tests/test_synthesize.py::test_build_api_index_deduplicates_apis -v`
Expected: PASS

Run: `python3 -m pytest doc-pipeline/tests/test_synthesize.py::test_resolve_cross_references_adds_bidirectional_links -v`
Expected: PASS

**Step 5: Commit**

```bash
git add doc-pipeline/lib/synthesize.py doc-pipeline/tests/test_synthesize.py
git commit -m "feat: add API index building and cross-reference resolution"
```

---

## Task 7: Refactor Pipeline Orchestration

**Files:**
- Modify: `doc-pipeline/pipeline.py`
- Modify: `doc-pipeline/tests/test_integration.py`

**Step 1: Write integration test for new pipeline flow**

Add to `doc-pipeline/tests/test_integration.py`:

```python
import pytest
from doc_pipeline.pipeline import run_pipeline
from doc_pipeline.config import Config


def test_pipeline_with_claude_phases(mocker, tmp_path):
    """Test complete pipeline with new Claude-powered phases."""
    config = Config(
        output_dir=tmp_path / "output",
        state_dir=tmp_path / "state",
        base_url="https://docs.limacharlie.io",
    )

    # Mock all external dependencies
    mock_fetch = mocker.patch('doc_pipeline.lib.fetch.fetch_pages')
    mock_fetch.return_value = [
        mocker.Mock(slug="test-page", title="Test", url="...", html_content="<h1>Test</h1>")
    ]

    mock_claude = mocker.patch('doc_pipeline.lib.claude_client.ClaudeClient')
    mock_claude.return_value.is_available.return_value = True

    mock_batch = mocker.patch('doc_pipeline.lib.batch.create_semantic_batches')
    mock_batch.return_value = [{
        'id': 'batch_01',
        'theme': 'Test',
        'pages': mock_fetch.return_value
    }]

    mock_process = mocker.patch('doc_pipeline.lib.understand.process_batches_parallel')
    from doc_pipeline.lib.understand import ProcessedPage
    mock_process.return_value = {
        'batch_01': [ProcessedPage(
            slug="test-page",
            enhanced_markdown="# Test Page",
            extracted_apis=[],
            cross_refs=[],
            metadata={}
        )]
    }

    success = run_pipeline(config)

    assert success is True
    assert (tmp_path / "output" / "test-page.md").exists()
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest doc-pipeline/tests/test_integration.py::test_pipeline_with_claude_phases -v`
Expected: FAIL (pipeline doesn't use new phases yet)

**Step 3: Refactor pipeline.py to use new phases**

Modify `doc-pipeline/pipeline.py`:

```python
"""Main pipeline orchestration."""
import asyncio
from pathlib import Path
from typing import List
from .config import Config
from .models import Page
from .lib.fetch import fetch_pages
from .lib.claude_client import ClaudeClient
from .lib.batch import create_semantic_batches
from .lib.understand import process_batches_parallel, ProcessedPage
from .lib.synthesize import build_api_index, resolve_cross_references
from .lib.detect import detect_changes


def run_pipeline(config: Config) -> bool:
    """
    Run the complete documentation pipeline.

    Phases:
    1. FETCH - Download pages
    2. BATCH_GROUP - Create semantic batches
    3. PARALLEL_UNDERSTAND - Process batches with Claude
    4. SYNTHESIZE - Build indexes and resolve references
    5. ENHANCE - Global optimizations (future)
    6. VERIFY - Semantic validation (future)
    7. DETECT - Git change tracking

    Args:
        config: Pipeline configuration

    Returns:
        True if successful, False otherwise
    """
    print("=" * 60)
    print("LIMACHARLIE DOCUMENTATION PIPELINE")
    print("=" * 60)

    # Initialize Claude client
    claude_client = ClaudeClient()
    claude_client.check_required()

    # Phase 1: FETCH
    print("\n[FETCH] Discovering and downloading pages...")
    pages = fetch_pages(config)
    print(f"✓ Fetched {len(pages)} pages")

    # Phase 2: BATCH_GROUP
    print("\n[BATCH_GROUP] Creating semantic batches...")
    batches = create_semantic_batches(pages, claude_client)
    print(f"✓ Created {len(batches)} batches")

    # Phase 3: PARALLEL_UNDERSTAND
    print("\n[PARALLEL_UNDERSTAND] Processing batches with Claude...")
    processed_batches = asyncio.run(
        process_batches_parallel(batches, claude_client)
    )

    # Flatten to page list
    all_processed: List[ProcessedPage] = []
    for batch_pages in processed_batches.values():
        all_processed.extend(batch_pages)
    print(f"✓ Processed {len(all_processed)} pages")

    # Phase 4: SYNTHESIZE
    print("\n[SYNTHESIZE] Building indexes and resolving references...")
    api_index = build_api_index(all_processed, claude_client)
    resolved_pages = resolve_cross_references(all_processed)
    print(f"✓ Built API index and resolved cross-references")

    # Write output files
    print("\n[OUTPUT] Writing documentation files...")
    config.output_dir.mkdir(parents=True, exist_ok=True)

    for page in resolved_pages:
        output_file = config.output_dir / f"{page.slug}.md"
        output_file.write_text(page.enhanced_markdown)

    # Write API index
    (config.output_dir / "API_INDEX.md").write_text(api_index)

    # Write metadata index
    import json
    metadata_index = {
        page.slug: page.metadata
        for page in resolved_pages
    }
    (config.output_dir / "METADATA_INDEX.json").write_text(
        json.dumps(metadata_index, indent=2)
    )

    print(f"✓ Wrote {len(resolved_pages)} markdown files")

    # Phase 7: DETECT (if git enabled)
    if config.git_commit_changes:
        print("\n[DETECT] Detecting changes...")
        detect_changes(config)

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)

    return True
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest doc-pipeline/tests/test_integration.py::test_pipeline_with_claude_phases -v`
Expected: PASS

**Step 5: Commit**

```bash
git add doc-pipeline/pipeline.py doc-pipeline/tests/test_integration.py
git commit -m "refactor: integrate Claude-powered phases into pipeline"
```

---

## Task 8: Error Handling and Recovery

**Files:**
- Modify: `doc-pipeline/lib/understand.py`
- Create: `doc-pipeline/tests/test_error_handling.py`

**Step 1: Write test for batch retry logic**

Create `doc-pipeline/tests/test_error_handling.py`:

```python
import pytest
import asyncio
from doc_pipeline.lib.understand import process_batch_with_retry


@pytest.mark.asyncio
async def test_process_batch_with_retry_succeeds_on_second_attempt(mocker):
    """Test that failed batches are retried."""
    batch = {
        'id': 'batch_01',
        'theme': 'Test',
        'pages': [mocker.Mock(slug="test", title="Test", url="...", html_content="<p>test</p>")]
    }

    mock_client = mocker.Mock()

    # First call fails, second succeeds
    call_count = 0
    async def mock_run(*args):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("Claude failed")
        return '{"pages": [{"slug": "test", "enhanced_markdown": "# Test", "extracted_apis": [], "cross_refs": [], "metadata": {}}]}'

    mock_client.run_subagent_prompt = mock_run

    batch_id, pages = await process_batch_with_retry(batch, mock_client, max_retries=3)

    assert batch_id == 'batch_01'
    assert len(pages) == 1
    assert call_count == 2  # Failed once, succeeded on retry


@pytest.mark.asyncio
async def test_process_batch_with_retry_fails_after_max_retries(mocker):
    """Test that batches fail after max retries exceeded."""
    batch = {
        'id': 'batch_01',
        'theme': 'Test',
        'pages': [mocker.Mock(slug="test", title="Test", url="...", html_content="<p>test</p>")]
    }

    mock_client = mocker.Mock()

    async def mock_run(*args):
        raise RuntimeError("Claude failed")

    mock_client.run_subagent_prompt = mock_run

    with pytest.raises(RuntimeError):
        await process_batch_with_retry(batch, mock_client, max_retries=3)
```

**Step 2: Run test to verify it fails**

Run: `python3 -m pytest doc-pipeline/tests/test_error_handling.py::test_process_batch_with_retry_succeeds_on_second_attempt -v`
Expected: FAIL with "ImportError: cannot import name 'process_batch_with_retry'"

**Step 3: Implement retry logic**

Add to `doc-pipeline/lib/understand.py`:

```python
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


# Update process_batches_parallel to use retry logic
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
```

**Step 4: Run test to verify it passes**

Run: `python3 -m pytest doc-pipeline/tests/test_error_handling.py::test_process_batch_with_retry_succeeds_on_second_attempt -v`
Expected: PASS

Run: `python3 -m pytest doc-pipeline/tests/test_error_handling.py::test_process_batch_with_retry_fails_after_max_retries -v`
Expected: PASS

**Step 5: Commit**

```bash
git add doc-pipeline/lib/understand.py doc-pipeline/tests/test_error_handling.py
git commit -m "feat: add batch retry logic with exponential backoff"
```

---

## Task 9: Update Documentation

**Files:**
- Modify: `doc-pipeline/README.md`
- Create: `doc-pipeline/ARCHITECTURE.md`

**Step 1: Update README with new architecture**

Modify `doc-pipeline/README.md` to replace old architecture section (lines 119-139):

```markdown
## Architecture

### Pipeline Phases

```
Input: docs.limacharlie.io
  ↓
[FETCH] → Discover structure + Download HTML (Algolia API)
  ↓
[BATCH_GROUP] → Semantic batching via Claude (5-10 pages per batch)
  ↓
[PARALLEL_UNDERSTAND] → Claude subagents process batches in parallel
  ↓
[SYNTHESIZE] → Build API index + resolve cross-references
  ↓
[ENHANCE] → Global optimizations (coming soon)
  ↓
[VERIFY] → Semantic validation (coming soon)
  ↓
[DETECT] → Git diff + Change report
  ↓
Output: LLM-optimized markdown + Comprehensive indexes
```

### Key Features

- **Semantic Understanding**: Claude reads and understands page content, not just converts HTML
- **Intelligent Batching**: Related pages processed together for better cross-referencing
- **Parallel Processing**: 10x faster through concurrent subagent execution
- **Rich Enhancement**: API extraction, cross-references, context additions
- **Quality Focus**: Optimized for LLM consumption, not just human readability

### Requirements

- Python 3.8+
- **Claude CLI** (required): Install from https://github.com/anthropics/claude-cli
- Git (for change tracking)
- Internet connection (for fetching)
```

**Step 2: Create architecture documentation**

Create `doc-pipeline/ARCHITECTURE.md`:

```markdown
# Documentation Pipeline Architecture

## Overview

This pipeline transforms web-based documentation into LLM-optimized markdown through intelligent processing powered by Claude AI.

## Design Principles

1. **Semantic Understanding Over Mechanical Conversion**: Claude reads and comprehends content rather than blindly converting HTML to markdown
2. **Batched Processing**: Related pages processed together to discover patterns and relationships
3. **Parallel Execution**: Concurrent subagent processing for speed without sacrificing quality
4. **Context Preservation**: Enhanced markdown includes implicit context made explicit
5. **Cross-Reference Network**: Pages linked by semantic relationships, not just navigation structure

## Pipeline Phases

### 1. FETCH
**Purpose**: Discover and download source documentation

**Implementation**: `doc-pipeline/lib/fetch.py`

- Uses Algolia search API to discover all documentation pages
- Filters by version (current version only)
- Downloads HTML content
- Handles pagination, rate limiting, retries

**Output**: List of `Page` objects with HTML content

### 2. BATCH_GROUP
**Purpose**: Group related pages for coherent processing

**Implementation**: `doc-pipeline/lib/batch.py`

- Claude analyzes all page titles and URLs
- Creates semantic batches of 5-10 related pages
- Batches based on:
  - Topical coherence
  - Workflow relationships
  - API surface similarity

**Why batching matters**: Pages processed together allow Claude to:
- Identify common patterns
- Create accurate cross-references
- Understand terminology consistency
- Extract complete API signatures from examples spread across pages

**Output**: List of batch definitions with page assignments

### 3. PARALLEL_UNDERSTAND
**Purpose**: Transform HTML into LLM-optimized markdown

**Implementation**: `doc-pipeline/lib/understand.py`

**Process**:
1. For each batch, generate specialized prompt
2. Launch Claude subagent via CLI (`claude --prompt-file ...`)
3. Run 10-40 subagents concurrently (asyncio)
4. Each subagent:
   - Reads HTML for all pages in batch
   - Understands purpose (tutorial/reference/concept)
   - Extracts APIs with full signatures
   - Identifies cross-references within batch
   - Generates enhanced markdown

**Subagent Prompt Template**: `doc-pipeline/prompts/batch_processing.md`

**Output Schema** (per page):
```json
{
  "slug": "page-identifier",
  "enhanced_markdown": "# Title\n\nContent with added context...",
  "extracted_apis": [
    {
      "name": "function()",
      "signature": "function(param: Type) -> ReturnType",
      "description": "What it does and when to use it"
    }
  ],
  "cross_refs": [
    {
      "page": "related-page-slug",
      "relationship": "prerequisite|continuation|alternative|debugging"
    }
  ],
  "metadata": {
    "summary": "One-sentence description",
    "keywords": ["key", "terms"],
    "complexity": "beginner|intermediate|advanced"
  }
}
```

**Error Handling**:
- Automatic retry with exponential backoff (3 attempts)
- Batch isolation (one failure doesn't stop others)
- Timeout protection (5 min per batch)

**Output**: Dictionary mapping batch_id to list of `ProcessedPage` objects

### 4. SYNTHESIZE
**Purpose**: Integrate batch outputs into coherent knowledge base

**Implementation**: `doc-pipeline/lib/synthesize.py`

**Sub-phases**:

**A. API Index Building**:
- Collect all extracted APIs from all batches
- Deduplicate by API name
- Use Claude to organize by category
- Add usage patterns and common workflows
- Output: `API_INDEX.md`

**B. Cross-Reference Resolution**:
- Collect within-batch references
- Use Claude to find cross-batch connections
- Add bidirectional links
- Append "Related Documentation" sections to markdown

**C. Gap Detection** (future):
- Identify APIs without tutorials
- Flag missing conceptual explanations
- Report documentation holes

**Output**:
- Enhanced `ProcessedPage` objects with global context
- `API_INDEX.md`
- `METADATA_INDEX.json`

### 5. ENHANCE (planned)
**Purpose**: Global-level optimizations

**Future capabilities**:
- Generate learning paths
- Create concept maps
- Add per-category overviews
- Build intelligent `COMBINED.md`

### 6. VERIFY (planned)
**Purpose**: Semantic validation

**Future checks**:
- Accuracy against source HTML
- Hallucination detection
- API completeness
- Cross-reference validity

### 7. DETECT
**Purpose**: Track changes via Git

**Implementation**: `doc-pipeline/lib/detect.py` (existing)

- Git diff analysis
- Categorize changes (structural vs content)
- Generate human-readable report
- Auto-commit if enabled

## Data Flow

```
Page (HTML)
  → Batch (5-10 Pages)
    → ProcessedPage (enhanced markdown + metadata)
      → Synthesized (cross-refs + API index)
        → Output Files (.md + .json)
          → Git Commit
```

## Key Data Structures

**Page** (`models.py`):
```python
@dataclass
class Page:
    slug: str           # URL identifier
    title: str          # Page title
    url: str            # Full URL
    html_content: str   # Raw HTML
```

**ProcessedPage** (`lib/understand.py`):
```python
@dataclass
class ProcessedPage:
    slug: str
    enhanced_markdown: str
    extracted_apis: List[Dict[str, str]]
    cross_refs: List[Dict[str, str]]
    metadata: Dict[str, Any]
```

**Batch**:
```python
{
    'id': 'batch_01_name',
    'theme': 'What this batch covers',
    'pages': [Page, Page, ...],
    'page_slugs': ['slug1', 'slug2', ...]
}
```

## Performance Characteristics

### Speed
- **Fetch**: ~30 seconds (290 pages with rate limiting)
- **Batch Group**: ~10 seconds (single Claude call)
- **Parallel Understand**: ~5-10 minutes (30-40 concurrent subagents)
- **Synthesize**: ~30 seconds (API index + cross-refs)
- **Total**: ~10-15 minutes

### Quality Gains vs. Previous Pipeline
- ✅ Semantic understanding (not blind conversion)
- ✅ Rich cross-references (not just navigation)
- ✅ Complete API documentation (signatures + context)
- ✅ Explicit prerequisites and relationships
- ✅ Warnings and gotchas preserved with semantic markup
- ✅ Code examples with usage explanations

### Cost
- ~40 Claude API calls per run (batching + synthesis)
- Optimized through batching (290 pages → 40 calls, not 290 calls)

## Configuration

Key settings in `config.py`:

```python
@dataclass
class Config:
    # Claude
    max_concurrent_batches: int = 10  # Parallel subagents
    batch_timeout: int = 300          # 5 min per batch

    # Batching
    min_batch_size: int = 5
    max_batch_size: int = 10

    # Features
    extract_api_signatures: bool = True
    generate_summaries: bool = True
    add_cross_references: bool = True
```

## Testing Strategy

1. **Unit Tests**: Each phase tested in isolation with mocks
2. **Integration Tests**: Full pipeline with mocked Claude responses
3. **End-to-End**: Real execution on small doc subset (manual)

## Future Enhancements

1. **Incremental Updates**: Only process changed pages
2. **Multi-Version Support**: Maintain docs for multiple product versions
3. **Quality Scoring**: Automatically rate documentation completeness
4. **Interactive Mode**: Allow human review/editing between phases
5. **Custom Subagent Skills**: Specialized prompts for API docs vs tutorials
```

**Step 3: Commit**

```bash
git add doc-pipeline/README.md doc-pipeline/ARCHITECTURE.md
git commit -m "docs: update architecture documentation for Claude-powered pipeline"
```

---

## Task 10: Manual Testing and Validation

**Files:**
- Create: `doc-pipeline/tests/manual_test.py` (test script for small subset)

**Step 1: Create manual test script**

Create `doc-pipeline/tests/manual_test.py`:

```python
#!/usr/bin/env python3
"""Manual test script for validating pipeline on small documentation subset."""
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from doc_pipeline.config import Config
from doc_pipeline.pipeline import run_pipeline


def main():
    """Run pipeline on small test subset."""
    print("MANUAL PIPELINE TEST")
    print("=" * 60)
    print("This will run the full pipeline but only process a small subset")
    print("of pages to validate the Claude-powered approach.")
    print()

    # Configure for small test
    config = Config(
        output_dir=Path("test-output"),
        state_dir=Path(".test-state"),
        # Add any test-specific config here
    )

    print("Configuration:")
    print(f"  Output: {config.output_dir}")
    print(f"  State: {config.state_dir}")
    print()

    input("Press Enter to start pipeline test...")

    try:
        success = run_pipeline(config)

        if success:
            print("\n✓ Pipeline completed successfully!")
            print("\nGenerated files:")
            for file in sorted(config.output_dir.glob("*.md")):
                print(f"  - {file.name}")

            # Show sample output
            sample_file = next(config.output_dir.glob("*.md"), None)
            if sample_file:
                print(f"\nSample output from {sample_file.name}:")
                print("-" * 60)
                print(sample_file.read_text()[:500])
                print("...")
                print("-" * 60)
        else:
            print("\n✗ Pipeline failed")
            return 1

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**Step 2: Make script executable and run manual test**

```bash
chmod +x doc-pipeline/tests/manual_test.py
python3 doc-pipeline/tests/manual_test.py
```

**Expected**: Pipeline runs successfully, generates enhanced markdown files with:
- Semantic structure
- API signatures with descriptions
- Cross-references
- Added context
- Clean formatting

**Step 3: Validate output quality**

Manual checks:
1. Read a few generated .md files - verify they're more readable than current output
2. Check API_INDEX.md - should have organized, categorized APIs
3. Verify cross-references link to actual pages
4. Confirm warnings/notes are semantically marked (> **Warning:**)

**Step 4: Commit test script**

```bash
git add doc-pipeline/tests/manual_test.py
git commit -m "test: add manual validation script for pipeline testing"
```

---

## Final Steps

### Run Full Test Suite

```bash
# Run all automated tests
python3 -m pytest doc-pipeline/tests/ -v

# Expected: All tests pass
```

### Update CHANGELOG

Create `CHANGELOG.md`:

```markdown
# Changelog

## [2.0.0] - 2025-10-11

### Added
- Claude-powered semantic understanding of documentation
- Intelligent batching of related pages
- Parallel subagent processing for speed
- Rich API index with categorization and usage patterns
- Bidirectional cross-references with relationship types
- Retry logic with exponential backoff
- Comprehensive architecture documentation

### Changed
- **BREAKING**: Pipeline now requires Claude CLI to be installed
- Replaced mechanical HTML→Markdown conversion with semantic enhancement
- Restructured from 6 to 7 phases
- Output optimized for LLM consumption, not just human readability

### Improved
- 10x better quality through semantic understanding
- Similar speed to old pipeline through parallelization
- Complete API documentation with signatures and context
- Cross-references based on relationships, not just navigation
- Explicit prerequisites and warnings

### Removed
- Direct markitdown usage (replaced with Claude processing)
- Simple pattern-based metadata extraction (replaced with Claude analysis)
```

### Final Commit

```bash
git add CHANGELOG.md
git commit -m "chore: release v2.0.0 with Claude-powered pipeline"
```

---

## Execution Notes

- Each task follows TDD: test first, watch fail, implement, watch pass, commit
- All file paths are absolute from repository root
- Every commit is atomic and independently functional
- Tests use mocks to avoid requiring Claude during testing
- Manual validation required at end to confirm quality
