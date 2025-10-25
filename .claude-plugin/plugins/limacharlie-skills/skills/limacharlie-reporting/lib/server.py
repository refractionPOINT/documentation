"""
Ultra-simple HTTP server for serving HTML reports on localhost.

This module provides a minimal HTTP server that:
- Starts automatically when needed using Python's built-in http.server
- Serves HTML reports from /tmp directory
- Runs as a background subprocess that persists
"""

import os
import subprocess
import tempfile
import time
import uuid
from typing import Optional

from .utils import find_available_port


class ReportServer:
    """
    Simple HTTP server for serving HTML reports using Python's http.server module.

    The server runs as a subprocess in the background and serves files from /tmp.

    Usage:
        server = ReportServer()
        url = server.serve_html(html_content, title="My Report")
        print(f"Report available at: {url}")
    """

    def __init__(self):
        """Initialize the server (doesn't start it yet)."""
        self.port: Optional[int] = None
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.serve_dir = tempfile.gettempdir()  # Use /tmp directory

    def _ensure_started(self) -> None:
        """Start the server if it's not already running."""
        if self.running:
            return

        # Find available port
        self.port = find_available_port()

        # Start Python's http.server as a subprocess
        try:
            self.process = subprocess.Popen(
                ['python3', '-m', 'http.server', str(self.port)],
                cwd=self.serve_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Give the server a moment to start up
            time.sleep(0.5)

            self.running = True
            print(f"Report server started at http://localhost:{self.port}")
        except Exception as e:
            print(f"Failed to start server: {e}")
            raise

    def serve_html(self, html: str, filename: Optional[str] = None) -> str:
        """
        Serve an HTML report and return its URL.

        Args:
            html: Complete HTML document to serve
            filename: Optional custom filename (will add .html if missing)

        Returns:
            URL where the report can be accessed
        """
        self._ensure_started()

        # Generate filename if not provided
        if filename is None:
            filename = f"report-{uuid.uuid4().hex[:8]}.html"
        elif not filename.endswith('.html'):
            filename = f"{filename}.html"

        # Sanitize filename (remove unsafe characters)
        filename = "".join(c for c in filename if c.isalnum() or c in ('-', '_', '.'))

        # Write HTML to file in /tmp
        filepath = os.path.join(self.serve_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)

        return f"http://localhost:{self.port}/{filename}"

    def shutdown(self) -> None:
        """Shutdown the server."""
        if not self.running:
            return

        self.running = False

        # Terminate the subprocess
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2.0)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass

        print("Report server shutdown")


# Global server instance
_server: Optional[ReportServer] = None


def get_server() -> ReportServer:
    """
    Get or create the global report server instance.

    Returns:
        ReportServer instance
    """
    global _server
    if _server is None:
        _server = ReportServer()
    return _server
