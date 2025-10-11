"""Configuration for documentation pipeline."""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """Pipeline configuration."""
    # Source
    base_url: str = "https://docs.limacharlie.io"
    docs_path: str = "/docs"

    # Output paths
    output_dir: Path = Path("limacharlie-docs-markdown")
    state_dir: Path = Path(".doc-pipeline-state")
    raw_html_dir: Path = Path("limacharlie-docs")

    # Behavior
    rate_limit_delay: float = 0.5  # seconds between requests
    request_timeout: int = 30
    retry_attempts: int = 3

    # Enhancement options
    extract_api_signatures: bool = True
    generate_summaries: bool = True
    add_cross_references: bool = True
    optimize_headings: bool = True

    # Verification options
    verify_content: bool = True
    verify_apis: bool = True
    verify_metadata: bool = True
    fail_on_critical: bool = False

    # Change detection
    git_commit_changes: bool = True
    git_commit_message: str = "Update LimaCharlie documentation"

    def __post_init__(self):
        """Ensure paths are Path objects."""
        if not isinstance(self.output_dir, Path):
            self.output_dir = Path(self.output_dir)
        if not isinstance(self.state_dir, Path):
            self.state_dir = Path(self.state_dir)
        if not isinstance(self.raw_html_dir, Path):
            self.raw_html_dir = Path(self.raw_html_dir)
