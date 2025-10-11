"""Data models for documentation pipeline."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class Page:
    """Represents a single documentation page."""
    url: str
    slug: str
    title: str
    category: str
    raw_html: str = ""
    markdown: str = ""
    metadata: Dict = field(default_factory=dict)
    api_elements: List[Dict] = field(default_factory=list)
    content_hash: str = ""

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'url': self.url,
            'slug': self.slug,
            'title': self.title,
            'category': self.category,
            'raw_html': self.raw_html,
            'markdown': self.markdown,
            'metadata': self.metadata,
            'api_elements': self.api_elements,
            'content_hash': self.content_hash,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Page':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class DocumentStructure:
    """Represents the entire documentation structure."""
    categories: Dict[str, List[Page]] = field(default_factory=dict)
    navigation: Dict = field(default_factory=dict)
    api_index: Dict = field(default_factory=dict)
    discovered_at: Optional[datetime] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'categories': {
                cat: [page.to_dict() for page in pages]
                for cat, pages in self.categories.items()
            },
            'navigation': self.navigation,
            'api_index': self.api_index,
            'discovered_at': self.discovered_at.isoformat() if self.discovered_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'DocumentStructure':
        """Create from dictionary."""
        categories = {
            cat: [Page.from_dict(page) for page in pages]
            for cat, pages in data.get('categories', {}).items()
        }
        discovered_at = None
        if data.get('discovered_at'):
            discovered_at = datetime.fromisoformat(data['discovered_at'])

        return cls(
            categories=categories,
            navigation=data.get('navigation', {}),
            api_index=data.get('api_index', {}),
            discovered_at=discovered_at,
        )


@dataclass
class VerificationIssue:
    """Represents a verification problem found."""
    severity: str  # "critical", "warning", "info"
    page_slug: str
    issue_type: str
    message: str
    details: Optional[Dict] = None


@dataclass
class VerificationReport:
    """Report of verification results."""
    total_pages: int = 0
    passed: int = 0
    warnings: int = 0
    critical: int = 0
    issues: List[VerificationIssue] = field(default_factory=list)

    def add_issue(self, issue: VerificationIssue):
        """Add an issue and update counters."""
        self.issues.append(issue)
        if issue.severity == "critical":
            self.critical += 1
        elif issue.severity == "warning":
            self.warnings += 1
