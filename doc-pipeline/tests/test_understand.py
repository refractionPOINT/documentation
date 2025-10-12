import sys
from pathlib import Path
import pytest
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.understand import generate_batch_prompt, ProcessedPage
from models import Page


def test_generate_batch_prompt_includes_all_pages():
    """Test that batch prompt includes all pages in the batch."""
    batch = {
        'id': 'batch_01_sensors',
        'theme': 'Sensor installation',
        'pages': [
            Page(slug="sensor-windows", title="Windows Sensors",
                 url="https://docs.limacharlie.io/docs/sensor-windows",
                 category="sensors",
                 raw_html="<h1>Windows Sensors</h1><p>Install on Windows...</p>"),
            Page(slug="sensor-linux", title="Linux Sensors",
                 url="https://docs.limacharlie.io/docs/sensor-linux",
                 category="sensors",
                 raw_html="<h1>Linux Sensors</h1><p>Install on Linux...</p>"),
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
    from lib.understand import parse_batch_output

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


@pytest.mark.anyio
async def test_process_batches_parallel(mocker):
    """Test that batches are processed in parallel."""
    batches = [
        {'id': f'batch_{i}', 'theme': f'Theme {i}',
         'pages': [Page(slug=f"page-{i}", title=f"Page {i}", url="...", category="test", raw_html="<p>test</p>")]}
        for i in range(5)
    ]

    mock_client = mocker.Mock()

    # Track call order to verify parallelism
    call_times = []
    import time

    def mock_run(*args, **kwargs):
        # Synchronous function that simulates processing time
        call_times.append(time.time())
        time.sleep(0.1)  # Simulate processing
        return '{"pages": [{"slug": "test", "enhanced_markdown": "# Test", "extracted_apis": [], "cross_refs": [], "metadata": {}}]}'

    mock_client.run_subagent_prompt = mock_run

    from lib.understand import process_batches_parallel

    start = time.time()
    results = await process_batches_parallel(batches, mock_client)
    duration = time.time() - start

    # If parallel, should take ~0.1s. If sequential, would take ~0.5s
    assert duration < 0.3
    assert len(results) == 5
