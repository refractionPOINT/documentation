import sys
from pathlib import Path
import pytest
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.understand import process_batch_with_retry


@pytest.mark.anyio
async def test_process_batch_with_retry_succeeds_on_second_attempt(mocker):
    """Test that failed batches are retried."""
    batch = {
        'id': 'batch_01',
        'theme': 'Test',
        'pages': [mocker.Mock(slug="test", title="Test", url="...", raw_html="<p>test</p>")]
    }

    mock_client = mocker.Mock()

    # First call fails, second succeeds
    call_count = 0
    def mock_run(*args):
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


@pytest.mark.anyio
async def test_process_batch_with_retry_fails_after_max_retries(mocker):
    """Test that batches fail after max retries exceeded."""
    batch = {
        'id': 'batch_01',
        'theme': 'Test',
        'pages': [mocker.Mock(slug="test", title="Test", url="...", raw_html="<p>test</p>")]
    }

    mock_client = mocker.Mock()

    def mock_run(*args):
        raise RuntimeError("Claude failed")

    mock_client.run_subagent_prompt = mock_run

    with pytest.raises(RuntimeError):
        await process_batch_with_retry(batch, mock_client, max_retries=3)
