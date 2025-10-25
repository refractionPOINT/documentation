"""
Essential utility functions for the LimaCharlie reporting skill.
"""

import os
import socket


def find_available_port(start: int = 8080, end: int = 8090) -> int:
    """
    Find an available port in the given range.

    Args:
        start: Starting port number (default: 8080)
        end: Ending port number (default: 8090)

    Returns:
        Available port number

    Raises:
        RuntimeError: If no available port found in range
    """
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('localhost', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available port found in range {start}-{end}")


def process_exists(pid: int) -> bool:
    """
    Check if a process with the given PID exists.

    Args:
        pid: Process ID to check

    Returns:
        True if process exists, False otherwise
    """
    try:
        # Send signal 0 to check if process exists (doesn't actually send a signal)
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False
