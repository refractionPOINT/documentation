import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.batch import create_semantic_batches
from models import Page


def test_create_semantic_batches_groups_related_pages(mocker):
    """Test that pages are grouped semantically by Claude."""
    pages = [
        Page(slug="sensor-windows", title="Windows Sensors", url="...", category="sensors", raw_html=""),
        Page(slug="sensor-linux", title="Linux Sensors", url="...", category="sensors", raw_html=""),
        Page(slug="detection-rules", title="D&R Rules", url="...", category="detection", raw_html=""),
        Page(slug="yara-rules", title="YARA Scanning", url="...", category="detection", raw_html=""),
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
    pages = [Page(slug=f"page-{i}", title=f"Page {i}", url="...", category="test", raw_html="")
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


def test_create_semantic_batches_handles_invalid_json(mocker):
    """Test that invalid JSON from Claude is handled gracefully."""
    pages = [Page(slug="test", title="Test", url="...", category="test", raw_html="")]

    mock_client = mocker.Mock()
    mock_client.run_subagent_prompt.return_value = "This is not JSON"

    with pytest.raises(ValueError, match="Claude returned invalid JSON"):
        create_semantic_batches(pages, mock_client)


def test_create_semantic_batches_handles_missing_batches_key(mocker):
    """Test that missing 'batches' key is handled."""
    pages = [Page(slug="test", title="Test", url="...", category="test", raw_html="")]

    mock_client = mocker.Mock()
    mock_client.run_subagent_prompt.return_value = '{"wrong_key": []}'

    with pytest.raises(ValueError, match="missing 'batches' key"):
        create_semantic_batches(pages, mock_client)


def test_create_semantic_batches_handles_empty_batches(mocker):
    """Test that empty batch list returns empty result."""
    pages = [Page(slug="test", title="Test", url="...", category="test", raw_html="")]

    mock_client = mocker.Mock()
    mock_client.run_subagent_prompt.return_value = '{"batches": []}'

    result = create_semantic_batches(pages, mock_client)
    assert result == []


def test_create_semantic_batches_validates_batch_structure(mocker):
    """Test that batches missing required keys are rejected."""
    pages = [Page(slug="test", title="Test", url="...", category="test", raw_html="")]

    mock_client = mocker.Mock()
    # Missing 'theme' key in batch
    mock_client.run_subagent_prompt.return_value = '''
{
  "batches": [
    {
      "id": "batch_01",
      "page_slugs": ["test"]
    }
  ]
}
'''

    with pytest.raises(ValueError, match="Batch 0 missing required key: theme"):
        create_semantic_batches(pages, mock_client)
