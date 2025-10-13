import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.synthesize import build_api_index, resolve_cross_references
from lib.understand import ProcessedPage


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
