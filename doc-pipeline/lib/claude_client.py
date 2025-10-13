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
            Cleaned JSON output from the subagent

        Raises:
            ClaudeNotAvailableError: If Claude CLI not available
            subprocess.TimeoutExpired: If execution exceeds timeout
        """
        self.check_required()

        # Read prompt from file
        with open(prompt_file, 'r') as f:
            prompt_content = f.read()

        # Use --print for non-interactive output and pass prompt via stdin
        result = subprocess.run(
            ['claude', '--print'],
            input=prompt_content,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude subagent failed: {result.stderr}")

        # Clean the response to extract JSON
        return self._clean_json_response(result.stdout)

    def _clean_json_response(self, raw_output: str) -> str:
        """
        Extract JSON from Claude's response, handling common patterns.

        Claude may return:
        - Plain JSON
        - JSON wrapped in ```json ... ```
        - Explanatory text followed by JSON
        - Combinations of the above

        Args:
            raw_output: Raw output from Claude CLI

        Returns:
            Cleaned JSON string
        """
        output = raw_output.strip()

        # If output is empty, return it as-is (will fail JSON parsing)
        if not output:
            return output

        # Strategy 1: Look for JSON in code blocks
        # Pattern: ```json\n{...}\n``` or ```\n{...}\n```
        if '```' in output:
            import re
            # Find content between code fences
            code_block_match = re.search(r'```(?:json)?\s*\n(.*?)\n```', output, re.DOTALL)
            if code_block_match:
                return code_block_match.group(1).strip()

        # Strategy 2: Find first { or [ and extract from there
        # This handles cases where Claude adds explanatory text before JSON
        json_start = -1
        for i, char in enumerate(output):
            if char in ('{', '['):
                json_start = i
                break

        if json_start >= 0:
            # Find matching closing brace/bracket
            # Simple approach: take from first { or [ to end
            # (assumes JSON is the last/main content)
            return output[json_start:].strip()

        # Strategy 3: Return as-is and let JSON parser handle it
        return output
