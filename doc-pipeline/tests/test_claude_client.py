import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.claude_client import ClaudeClient, ClaudeNotAvailableError


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
