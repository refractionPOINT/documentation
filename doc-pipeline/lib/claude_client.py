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
