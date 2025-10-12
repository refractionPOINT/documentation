import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.synthesize import build_api_index, resolve_cross_references
from lib.understand import ProcessedTopic


def test_build_api_index_deduplicates_apis(mocker):
    """Test that duplicate APIs from different topics are merged."""
    topics = [
        ProcessedTopic(
            slug="installing-sensors",
            title="Installing Sensors",
            type="task",
            content="...",
            source_pages=["page1"],
            extracted_apis=[
                {"name": "sensor.install()", "signature": "install() -> bool", "description": "Installs sensor"}
            ],
            prerequisites=[],
            related_topics=[],
            keywords=[]
        ),
        ProcessedTopic(
            slug="sensor-setup",
            title="Sensor Setup",
            type="task",
            content="...",
            source_pages=["page2"],
            extracted_apis=[
                {"name": "sensor.install()", "signature": "install() -> bool", "description": "Installs the sensor"}
            ],
            prerequisites=[],
            related_topics=[],
            keywords=[]
        ),
    ]

    mock_client = mocker.Mock()
    mock_client.run_subagent_prompt.return_value = """
# API Index

## Sensor APIs

- `sensor.install() -> bool`: Installs the sensor on the system
  - Topics: installing-sensors, sensor-setup
"""

    api_index = build_api_index(topics, mock_client)

    assert "sensor.install()" in api_index
    assert "installing-sensors" in api_index
    assert "sensor-setup" in api_index


def test_resolve_cross_references_is_deprecated():
    """Test that resolve_cross_references is now a no-op (deprecated)."""
    topics = [
        ProcessedTopic(
            slug="sensor-install",
            title="Installing Sensors",
            type="task",
            content="# Install",
            source_pages=["page1"],
            extracted_apis=[],
            prerequisites=[],
            related_topics=["sensor-troubleshoot"],
            keywords=[]
        ),
        ProcessedTopic(
            slug="sensor-troubleshoot",
            title="Troubleshooting Sensors",
            type="task",
            content="# Troubleshoot",
            source_pages=["page2"],
            extracted_apis=[],
            prerequisites=[],
            related_topics=[],
            keywords=[]
        ),
    ]

    # In the new transformation model, resolve_cross_references is a no-op
    # It returns topics unchanged
    resolved = resolve_cross_references(topics)

    assert len(resolved) == 2
    assert resolved == topics  # Should return unchanged
