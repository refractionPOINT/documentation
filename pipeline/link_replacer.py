#!/usr/bin/env python3
"""
Link Replacer Utility

Replaces Document360 URL references with relative local markdown file paths.
This makes the documentation self-contained and suitable for AI consumption.
"""

import re
from pathlib import Path
from typing import Dict, Optional, Tuple
import urllib.parse

import config
from utils import log, log_error, log_warning, load_json


class LinkReplacer:
    """Handles replacement of Document360 links with local file references."""

    def __init__(self):
        """Initialize the link replacer with URL mappings."""
        self.url_to_file = {}  # Maps URL patterns to local file paths
        self.slug_to_file = {}  # Maps slugs to local file paths
        self.replacements_made = 0
        self.links_not_found = set()

        self._build_mappings()

    def _build_mappings(self):
        """Build comprehensive URL → file path mappings."""
        log("Building URL to file path mappings...")

        # Load discovered pages (URL → slug mapping)
        try:
            discovered_pages = load_json(config.DISCOVERED_PAGES_FILE)
            log(f"Loaded {len(discovered_pages)} discovered pages")
        except Exception as e:
            log_error(f"Failed to load discovered pages: {e}")
            discovered_pages = {}

        # Load topic map (topic_id → file path mapping)
        try:
            topic_map_file = config.METADATA_DIR / "topic_map.json"
            topic_map = load_json(topic_map_file)
            log(f"Loaded {len(topic_map)} topics")
        except Exception as e:
            log_error(f"Failed to load topic map: {e}")
            topic_map = {}

        # Build slug → file path mapping from topic map
        for topic_id, topic_info in topic_map.items():
            file_path = topic_info.get("file_path", "")
            if file_path:
                # Extract slug from topic_id (e.g., "tasks/adapter-deployment" → "adapter-deployment")
                slug = topic_id.split('/')[-1]
                self.slug_to_file[slug] = file_path

                # Also store the full topic_id
                self.slug_to_file[topic_id] = file_path

        log(f"Built mapping for {len(self.slug_to_file)} slugs/topics")

        # Build URL → file path mapping from discovered pages
        for url, page_info in discovered_pages.items():
            slug = page_info.get("slug", "")

            # Try to find the file for this slug
            file_path = self._find_file_for_slug(slug, topic_map)

            if file_path:
                # Store mappings for various URL formats
                self.url_to_file[url] = file_path

                # Also store just the path portion for relative URLs
                if "/docs/" in url:
                    path_part = "/" + url.split("/docs/", 1)[1]
                    self.url_to_file[path_part] = file_path

                    # Handle /v2/docs/ format
                    if "/v2/" not in path_part:
                        self.url_to_file["/v2/docs/" + url.split("/docs/", 1)[1]] = file_path

        log(f"Built URL mappings for {len(self.url_to_file)} URLs")

    def _find_file_for_slug(self, slug: str, topic_map: Dict) -> Optional[str]:
        """Find the local file path for a given slug."""
        # Try direct slug lookup
        if slug in self.slug_to_file:
            return self.slug_to_file[slug]

        # Try finding in topic map by searching for slug in topic_id
        for topic_id, topic_info in topic_map.items():
            if slug in topic_id or topic_id.endswith(slug):
                return topic_info.get("file_path", "")

        # Try normalized slug (replace - with _ and vice versa)
        normalized_slug = slug.replace("-", "_")
        if normalized_slug in self.slug_to_file:
            return self.slug_to_file[normalized_slug]

        normalized_slug = slug.replace("_", "-")
        if normalized_slug in self.slug_to_file:
            return self.slug_to_file[normalized_slug]

        # Try partial matches (handle truncated slugs in topic IDs)
        # For example "tutorial-creating-a-webhook-adapter" should match "tutorial-creating"
        for topic_slug, file_path in self.slug_to_file.items():
            # Check if the topic_slug is a prefix of the search slug
            if slug.startswith(topic_slug) or topic_slug in slug:
                return file_path

        return None

    def _extract_slug_from_url(self, url: str) -> str:
        """Extract the slug portion from a URL."""
        # Remove query parameters and fragments
        url = url.split('?')[0].split('#')[0]

        # Extract the part after /docs/
        if "/docs/" in url:
            slug = url.split("/docs/", 1)[1]
            # Remove trailing slash
            slug = slug.rstrip('/')
            return slug

        return url

    def _is_doc360_link(self, url: str) -> bool:
        """Check if a URL is a Document360 documentation link."""
        doc360_patterns = [
            "docs.limacharlie.io/docs/",
            "docs.limacharlie.io/v2/docs/",
            "/v2/docs/",
            "/docs/",
        ]

        # Don't replace API docs or external resources
        exclude_patterns = [
            "docs.limacharlie.io/apidocs/",
            "/apidocs/",
            "cdn.document360.io",
            "http://",  # Only if not limacharlie
            "https://",  # Only if not limacharlie
        ]

        # Check if it's a doc360 link
        is_doc360 = any(pattern in url for pattern in doc360_patterns)

        if not is_doc360:
            return False

        # Check exclusions
        if "apidocs" in url or "cdn.document360.io" in url:
            return False

        # If it's an external URL (http/https), only process if it's limacharlie
        if url.startswith("http://") or url.startswith("https://"):
            return "limacharlie.io" in url

        return True

    def _calculate_relative_path(self, from_file: Path, to_file: Path) -> str:
        """Calculate relative path from one file to another."""
        import os

        try:
            # Convert to absolute paths
            from_abs = Path(config.BASE_DIR) / from_file
            to_abs = Path(config.BASE_DIR) / to_file

            # Get the directory containing the source file
            from_dir = from_abs.parent

            # Calculate relative path using os.path.relpath
            rel_path = os.path.relpath(to_abs, from_dir)

            return rel_path
        except Exception as e:
            log_warning(f"Failed to calculate relative path from {from_file} to {to_file}: {e}")
            # Fallback: return absolute path from output directory
            return str(to_file)

    def replace_links_in_content(self, content: str, current_file_path: str) -> Tuple[str, int]:
        """
        Replace Document360 links in markdown content with local file references.

        Args:
            content: The markdown content
            current_file_path: Path to the current file (for calculating relative paths)

        Returns:
            Tuple of (updated content, number of replacements made)
        """
        replacements = 0

        # Pattern to match markdown links: [text](url)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

        def replace_link(match):
            nonlocal replacements

            link_text = match.group(1)
            link_url = match.group(2)

            # Skip if not a Document360 link
            if not self._is_doc360_link(link_url):
                return match.group(0)  # Return unchanged

            # Try to find local file for this URL
            local_file = None

            # Try direct URL lookup
            if link_url in self.url_to_file:
                local_file = self.url_to_file[link_url]
            else:
                # Try extracting slug and looking it up
                slug = self._extract_slug_from_url(link_url)
                local_file = self._find_file_for_slug(slug, {})

            if local_file:
                # Calculate relative path from current file to target file
                rel_path = self._calculate_relative_path(
                    Path(current_file_path),
                    Path(local_file)
                )

                replacements += 1
                return f"[{link_text}]({rel_path})"
            else:
                # Log links that couldn't be resolved
                self.links_not_found.add(link_url)
                return match.group(0)  # Return unchanged

        # Replace all links
        updated_content = link_pattern.sub(replace_link, content)

        return updated_content, replacements

    def process_file(self, file_path: Path) -> int:
        """
        Process a single markdown file and replace links.

        Args:
            file_path: Path to the markdown file

        Returns:
            Number of replacements made
        """
        try:
            # Read the file
            content = file_path.read_text(encoding='utf-8')

            # Get relative path for this file
            rel_path = str(file_path.relative_to(config.BASE_DIR))

            # Replace links
            updated_content, replacements = self.replace_links_in_content(content, rel_path)

            # Write back only if changes were made
            if replacements > 0:
                file_path.write_text(updated_content, encoding='utf-8')
                log(f"Updated {file_path.name}: {replacements} links replaced")

            self.replacements_made += replacements
            return replacements

        except Exception as e:
            log_error(f"Failed to process {file_path}: {e}")
            return 0

    def get_stats(self) -> Dict:
        """Get statistics about link replacements."""
        return {
            "total_replacements": self.replacements_made,
            "unresolved_links": list(self.links_not_found),
            "unresolved_count": len(self.links_not_found),
            "url_mappings": len(self.url_to_file),
            "slug_mappings": len(self.slug_to_file),
        }
