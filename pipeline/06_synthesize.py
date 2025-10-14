#!/usr/bin/env python3
"""
Phase 6: Topic Synthesis

Analyzes all cleaned documentation and reorganizes into self-contained topics:
- tasks/: How-to guides and procedures
- concepts/: Explanations and conceptual content
- reference/: Technical reference, APIs, configurations

Each topic is complete and self-contained (no "see X for details").
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

import config
import utils


class TopicSynthesizer:
    """Synthesizes cleaned documentation into organized topics."""

    def __init__(self):
        self.cleaned_dir = config.CLEANED_MARKDOWN_DIR
        self.topics_dir = config.TOPICS_DIR
        self.metadata_dir = config.METADATA_DIR

        # Check that cleaned directory exists and has content
        if not self.cleaned_dir.exists():
            utils.log_error(f"Cleaned markdown directory not found: {self.cleaned_dir}")
            utils.log_error("Run phases 1-4 first to generate cleaned markdown.")
            sys.exit(1)

        # Load synthesis prompt (optional - we create prompts inline)
        synthesis_prompt_path = config.PIPELINE_DIR / "prompts" / "synthesize_topics.md"
        if synthesis_prompt_path.exists():
            self.synthesis_prompt = synthesis_prompt_path.read_text(encoding='utf-8')
            utils.log(f"Loaded synthesis prompt from {synthesis_prompt_path}")
        else:
            self.synthesis_prompt = ""
            utils.log("Using inline synthesis prompts")

    def load_all_cleaned_docs(self) -> Dict[str, str]:
        """Load all cleaned markdown files into memory."""
        docs = {}
        utils.log(f"Loading cleaned documentation from {self.cleaned_dir}...")

        for file_path in self.cleaned_dir.glob("*.md"):
            try:
                content = file_path.read_text(encoding='utf-8')
                docs[file_path.stem] = content
            except Exception as e:
                utils.log_error(f"Failed to read {file_path}: {e}")

        utils.log_success(f"Loaded {len(docs)} cleaned documents")
        return docs

    def prepare_doc_catalog(self, docs: Dict[str, str]) -> str:
        """Create a catalog of all documents with titles and first paragraphs."""
        catalog_lines = ["# Documentation Catalog\n"]

        for slug, content in sorted(docs.items()):
            # Get title (first line starting with #)
            lines = content.split('\n')
            title = slug
            for line in lines:
                if line.startswith('#'):
                    title = line.lstrip('#').strip()
                    break

            # Get first paragraph
            first_para = ""
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    first_para = line.strip()[:200]
                    break

            catalog_lines.append(f"## {slug}")
            catalog_lines.append(f"**Title**: {title}")
            catalog_lines.append(f"**Preview**: {first_para}...")
            catalog_lines.append("")

        return '\n'.join(catalog_lines)

    def categorize_documents(self, docs: Dict[str, str]) -> Dict[str, List[str]]:
        """Use Claude to categorize documents into tasks, concepts, and reference."""
        utils.log("Categorizing documents into tasks, concepts, and reference...")

        # Prepare catalog for Claude
        catalog = self.prepare_doc_catalog(docs)

        # Create categorization prompt
        categorization_prompt = f"""You are organizing documentation into three categories:

1. **tasks/**: How-to guides, procedures, step-by-step instructions (e.g., "How to configure X", "Setting up Y")
2. **concepts/**: Explanations, conceptual content, understanding (e.g., "What is X", "Understanding Y")
3. **reference/**: Technical reference, API docs, command lists, configuration options (e.g., "API Reference", "Configuration Options")

Below is a catalog of all documentation pages. For each page, determine which category it belongs to.

Output ONLY a JSON object in this exact format:
{{
  "tasks": ["slug1", "slug2", ...],
  "concepts": ["slug3", "slug4", ...],
  "reference": ["slug5", "slug6", ...]
}}

Do not include any other text or explanation. Only output the JSON.

{catalog}
"""

        try:
            # Call Claude to categorize
            result = subprocess.run(
                [config.CLAUDE_CLI],
                input=categorization_prompt,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes
                encoding='utf-8'
            )

            if result.returncode != 0:
                utils.log_error(f"Claude categorization failed: {result.stderr}")
                return self._fallback_categorization(docs)

            # Parse JSON response
            response = result.stdout.strip()
            # Find JSON object in response (might have surrounding text)
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx == -1 or end_idx == 0:
                utils.log_error("No JSON found in Claude response")
                return self._fallback_categorization(docs)

            json_str = response[start_idx:end_idx]
            categories = json.loads(json_str)

            # Validate structure
            if not all(key in categories for key in ['tasks', 'concepts', 'reference']):
                utils.log_error("Invalid category structure from Claude")
                return self._fallback_categorization(docs)

            utils.log_success(f"Categorized: {len(categories['tasks'])} tasks, "
                            f"{len(categories['concepts'])} concepts, "
                            f"{len(categories['reference'])} reference")

            return categories

        except Exception as e:
            utils.log_error(f"Categorization failed: {e}")
            return self._fallback_categorization(docs)

    def _fallback_categorization(self, docs: Dict[str, str]) -> Dict[str, List[str]]:
        """Fallback categorization based on slug patterns."""
        utils.log("Using fallback pattern-based categorization...")

        categories = {
            'tasks': [],
            'concepts': [],
            'reference': []
        }

        for slug in docs.keys():
            slug_lower = slug.lower()

            # Reference patterns
            if any(pattern in slug_lower for pattern in [
                'reference', 'api', 'command', 'event', 'config',
                'endpoint', 'parameter', 'option'
            ]):
                categories['reference'].append(slug)
            # Task patterns
            elif any(pattern in slug_lower for pattern in [
                'how', 'guide', 'setup', 'install', 'configure',
                'deploy', 'create', 'manage', 'quickstart', 'tutorial'
            ]):
                categories['tasks'].append(slug)
            # Everything else is concepts
            else:
                categories['concepts'].append(slug)

        utils.log_success(f"Fallback categorized: {len(categories['tasks'])} tasks, "
                        f"{len(categories['concepts'])} concepts, "
                        f"{len(categories['reference'])} reference")

        return categories

    def synthesize_topic(self, category: str, slugs: List[str], docs: Dict[str, str]) -> str:
        """Synthesize multiple related documents into a single cohesive topic."""
        if not slugs:
            return ""

        # If only one document, return it as-is
        if len(slugs) == 1:
            return docs[slugs[0]]

        # Combine multiple documents
        combined_content = []
        for slug in slugs:
            if slug in docs:
                combined_content.append(f"# From: {slug}\n\n{docs[slug]}")

        combined_text = "\n\n---\n\n".join(combined_content)

        # Use Claude to synthesize into coherent topic
        synthesis_prompt = f"""You are synthesizing multiple related documentation pages into a single, cohesive, self-contained topic.

Category: {category}

Your task:
1. Merge related content intelligently
2. Remove redundancy while preserving all important information
3. Organize with clear sections and hierarchy
4. Ensure the result is self-contained (no "see page X for details")
5. Keep all code examples, commands, and technical details
6. Maintain all links and references

Output ONLY the synthesized markdown content. Do not add commentary or explanations about what you did.

{combined_text}
"""

        try:
            result = subprocess.run(
                [config.CLAUDE_CLI],
                input=synthesis_prompt,
                capture_output=True,
                text=True,
                timeout=180,  # 3 minutes
                encoding='utf-8'
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                utils.log_error(f"Synthesis failed for {category}: {result.stderr}")
                return combined_text  # Return combined but unsynthesized

        except Exception as e:
            utils.log_error(f"Synthesis failed for {category}: {e}")
            return combined_text

    def group_related_topics(self, category: str, slugs: List[str], docs: Dict[str, str]) -> Dict[str, List[str]]:
        """Group related documents that should be merged into single topics."""
        utils.log(f"Grouping {len(slugs)} documents in {category}...")

        # For now, use simple grouping based on slug prefixes
        # A more sophisticated approach would use Claude to analyze content similarity
        groups = {}

        for slug in slugs:
            # Extract base topic from slug (before last hyphen/underscore)
            base = slug.rsplit('-', 1)[0] if '-' in slug else slug
            base = base.rsplit('_', 1)[0] if '_' in base else base

            # Group similar slugs together
            if base not in groups:
                groups[base] = []
            groups[base].append(slug)

        utils.log_success(f"Created {len(groups)} topic groups from {len(slugs)} documents")
        return groups

    def write_topic_file(self, category: str, topic_name: str, content: str):
        """Write a synthesized topic to the appropriate directory."""
        category_dir = self.topics_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        output_path = category_dir / f"{topic_name}.md"
        output_path.write_text(content, encoding='utf-8')

        return output_path

    def synthesize_all(self):
        """Main synthesis workflow."""
        utils.log("="*60)
        utils.log("Phase 6: Topic Synthesis")
        utils.log("="*60)

        # Load all cleaned docs
        docs = self.load_all_cleaned_docs()
        if not docs:
            utils.log_error("No cleaned documents found")
            return

        # Categorize documents
        categories = self.categorize_documents(docs)

        # Process each category
        synthesis_results = {
            'tasks': [],
            'concepts': [],
            'reference': []
        }

        for category in ['tasks', 'concepts', 'reference']:
            utils.log(f"\n{'='*60}")
            utils.log(f"Processing {category.upper()}")
            utils.log(f"{'='*60}")

            slugs = categories[category]
            if not slugs:
                utils.log(f"No documents in {category}, skipping")
                continue

            # Group related topics
            groups = self.group_related_topics(category, slugs, docs)

            # Synthesize each group
            for topic_name, topic_slugs in groups.items():
                utils.log(f"Synthesizing '{topic_name}' from {len(topic_slugs)} document(s)...")

                content = self.synthesize_topic(category, topic_slugs, docs)
                if content:
                    output_path = self.write_topic_file(category, topic_name, content)
                    synthesis_results[category].append({
                        'topic': topic_name,
                        'source_slugs': topic_slugs,
                        'output_path': str(output_path)
                    })
                    utils.log_success(f"Created: {output_path}")

        # Save synthesis metadata
        metadata_path = self.metadata_dir / "synthesis_results.json"
        utils.save_json(synthesis_results, metadata_path)

        # Print summary
        utils.log("\n" + "="*60)
        utils.log("Synthesis Complete")
        utils.log("="*60)

        total_topics = sum(len(results) for results in synthesis_results.values())
        utils.log_success(f"Created {total_topics} synthesized topics:")
        utils.log_success(f"  - Tasks: {len(synthesis_results['tasks'])} topics")
        utils.log_success(f"  - Concepts: {len(synthesis_results['concepts'])} topics")
        utils.log_success(f"  - Reference: {len(synthesis_results['reference'])} topics")

        utils.log(f"\nTopics directory: {self.topics_dir}")
        utils.log(f"Metadata saved to: {metadata_path}")


def main():
    """Run topic synthesis."""
    synthesizer = TopicSynthesizer()
    synthesizer.synthesize_all()


if __name__ == "__main__":
    main()
