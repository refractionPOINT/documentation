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
