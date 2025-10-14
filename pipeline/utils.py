"""
Shared utility functions for the documentation pipeline.
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

def log(message: str, level: str = "INFO") -> None:
    """Log a message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}", file=sys.stderr)

def log_error(message: str) -> None:
    """Log an error message."""
    log(message, "ERROR")

def log_success(message: str) -> None:
    """Log a success message."""
    log(message, "SUCCESS")

def log_warning(message: str) -> None:
    """Log a warning message."""
    log(message, "WARNING")

def save_json(data: Any, filepath: Path) -> None:
    """Save data to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log(f"Saved JSON to {filepath}")

def load_json(filepath: Path) -> Any:
    """Load data from JSON file."""
    if not filepath.exists():
        raise FileNotFoundError(f"JSON file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def ensure_dir(directory: Path) -> None:
    """Ensure directory exists."""
    directory.mkdir(parents=True, exist_ok=True)

def sanitize_filename(name: str) -> str:
    """Sanitize a string to be used as a filename."""
    # Replace problematic characters
    replacements = {
        '/': '-',
        '\\': '-',
        ':': '-',
        '*': '-',
        '?': '-',
        '"': '-',
        '<': '-',
        '>': '-',
        '|': '-',
        ' ': '-',
    }

    result = name
    for old, new in replacements.items():
        result = result.replace(old, new)

    # Remove any duplicate dashes
    while '--' in result:
        result = result.replace('--', '-')

    # Remove leading/trailing dashes
    result = result.strip('-')

    return result

def extract_url_slug(url: str) -> str:
    """Extract the slug from a documentation URL."""
    # Remove base URL and extract the path component
    if '/docs/' in url:
        slug = url.split('/docs/')[-1]
        # Remove trailing slashes and fragments
        slug = slug.rstrip('/').split('#')[0].split('?')[0]
        return slug
    return sanitize_filename(url)

def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def count_files(directory: Path, pattern: str = "*") -> int:
    """Count files in directory matching pattern."""
    return len(list(directory.glob(pattern)))

class ProgressTracker:
    """Simple progress tracker for pipeline operations."""

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()

    def update(self, increment: int = 1) -> None:
        """Update progress."""
        self.current += increment
        percentage = (self.current / self.total * 100) if self.total > 0 else 0
        elapsed = (datetime.now() - self.start_time).total_seconds()
        rate = self.current / elapsed if elapsed > 0 else 0

        log(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%) - {rate:.1f} items/sec")

    def complete(self) -> None:
        """Mark as complete."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        log_success(f"{self.description} complete: {self.current} items in {elapsed:.1f}s")
