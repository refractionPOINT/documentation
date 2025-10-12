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


def test_run_subagent_prompt_success(mocker, tmp_path):
    """Test successful subagent execution with prompt file."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value.returncode = 0
    mock_run.return_value.stdout = '{"result": "success"}'

    client = ClaudeClient()
    # Pre-set availability to avoid the version check call
    client._available = True

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
    import subprocess

    mock_run = mocker.patch('subprocess.run')
    mock_run.side_effect = subprocess.TimeoutExpired(cmd=['claude'], timeout=300)

    client = ClaudeClient()
    # Pre-set availability to avoid the version check call
    client._available = True

    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Test prompt")

    with pytest.raises(subprocess.TimeoutExpired):
        client.run_subagent_prompt(str(prompt_file), timeout=300)


def test_run_subagent_prompt_failure(mocker, tmp_path):
    """Test error handling for failed subagent execution."""
    mock_run = mocker.patch('subprocess.run')
    mock_run.return_value.returncode = 1
    mock_run.return_value.stderr = 'Error: invalid prompt format'

    client = ClaudeClient()
    client._available = True

    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Test prompt")

    with pytest.raises(RuntimeError, match="Claude subagent failed"):
        client.run_subagent_prompt(str(prompt_file))
