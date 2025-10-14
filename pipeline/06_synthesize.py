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

        # Use Claude to synthesize into coherent topic with strict validation
        synthesis_prompt = f"""You are synthesizing multiple related documentation pages into a single, cohesive, self-contained topic.

Category: {category}

CRITICAL REQUIREMENTS:
1. **VALIDATE FIRST**: Confirm these documents are about the SAME specific topic
2. **IF UNRELATED**: Output them SEPARATELY with clear section breaks, DO NOT MERGE
3. **IF RELATED**: Merge intelligently while preserving ALL technical details
4. **PRESERVE DEPTH**: Keep ALL code examples, commands, configurations, parameters
5. **NO SUMMARIZATION**: Include complete content, not abbreviated versions
6. **SELF-CONTAINED**: No "see page X for details" - include all necessary information
7. **TECHNICAL ACCURACY**: Preserve exact commands, syntax, and technical details

Output ONLY the synthesized markdown content. Do not add commentary or explanations about what you did.

If documents are unrelated, output them as separate sections like:
```
# Topic 1 Title
[Full content of topic 1]

---

# Topic 2 Title
[Full content of topic 2]
```

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

    def strip_language_prefix(self, slug: str) -> str:
        """Strip language prefix from slug (e.g., 'en-config-hive' -> 'config-hive')."""
        # Common language prefixes used in documentation
        language_prefixes = ['en-', 'fr-', 'es-', 'de-', 'ja-', 'zh-']

        for prefix in language_prefixes:
            if slug.startswith(prefix):
                return slug[len(prefix):]

        return slug

    def extract_topic_keywords(self, slug: str, content: str) -> str:
        """Extract key information for grouping decision."""
        # Get title
        lines = content.split('\n')
        title = slug
        for line in lines:
            if line.startswith('#'):
                title = line.lstrip('#').strip()
                break

        # Get first 500 characters of content
        text_content = []
        for line in lines:
            if line.strip() and not line.startswith('#'):
                text_content.append(line.strip())
                if len(' '.join(text_content)) > 500:
                    break

        preview = ' '.join(text_content)[:500]

        return f"**{slug}** | Title: {title} | Content: {preview}..."

    def semantic_group_topics(self, category: str, slugs: List[str], docs: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Intelligently group related documents using semantic analysis.

        Key improvements:
        1. Strip language prefixes before grouping
        2. Use content similarity instead of string matching
        3. Keep groups small (max 5 docs)
        4. Validate that grouped items are actually related
        """
        utils.log(f"Semantically grouping {len(slugs)} documents in {category}...")

        # Step 1: Strip language prefixes and create initial mapping
        normalized_slugs = {}  # normalized_slug -> [original_slugs]
        for slug in slugs:
            normalized = self.strip_language_prefix(slug)
            if normalized not in normalized_slugs:
                normalized_slugs[normalized] = []
            normalized_slugs[normalized].append(slug)

        utils.log(f"After stripping language prefixes: {len(normalized_slugs)} unique topics")

        # Step 2: Create initial groups based on normalized slugs
        # Use smarter prefix matching that considers topic hierarchy
        initial_groups = {}

        for normalized, slug_list in normalized_slugs.items():
            # Split on hyphens and build hierarchy
            parts = normalized.split('-')

            # Strategy: Only group if share a meaningful prefix (at least 2 segments)
            # and total slug length is similar
            if len(parts) >= 3:
                # Multi-part slug: group by first 2-3 segments
                base = '-'.join(parts[:2])
            else:
                # Short slug: use full slug as base (don't merge different topics)
                base = normalized

            if base not in initial_groups:
                initial_groups[base] = []
            initial_groups[base].extend(slug_list)

        # Step 3: Validate groups and split large ones using semantic analysis
        final_groups = {}

        for base, group_slugs in initial_groups.items():
            # If only 1-2 docs, keep as-is
            if len(group_slugs) <= 2:
                final_groups[base] = group_slugs
                continue

            # If 3-5 docs, validate they're related
            if len(group_slugs) <= 5:
                if self.validate_group_relatedness(group_slugs, docs):
                    final_groups[base] = group_slugs
                else:
                    # Split into individual topics
                    for slug in group_slugs:
                        final_groups[slug] = [slug]
                continue

            # If >5 docs, definitely split using semantic analysis
            subgroups = self.split_large_group(base, group_slugs, docs)
            final_groups.update(subgroups)

        utils.log_success(f"Created {len(final_groups)} semantic topic groups from {len(slugs)} documents")

        # Log large groups for inspection
        for topic_name, topic_slugs in final_groups.items():
            if len(topic_slugs) > 3:
                utils.log(f"  Large group '{topic_name}': {len(topic_slugs)} docs - {topic_slugs[:3]}...")

        return final_groups

    def validate_group_relatedness(self, slugs: List[str], docs: Dict[str, str]) -> bool:
        """
        Use Claude to validate that documents in a group are actually related.

        Returns True if documents should be merged, False if they should stay separate.
        """
        if len(slugs) <= 1:
            return True

        # Prepare document summaries
        doc_summaries = []
        for slug in slugs[:5]:  # Limit to first 5 to keep prompt manageable
            if slug in docs:
                summary = self.extract_topic_keywords(slug, docs[slug])
                doc_summaries.append(summary)

        summaries_text = '\n'.join(doc_summaries)

        # Ask Claude if these documents are related
        validation_prompt = f"""Analyze if these documents are about the SAME topic and should be merged:

{summaries_text}

Answer with ONLY one word:
- "MERGE" if they are about the same specific topic (e.g., all about "Config Hive", or all about "Windows Agent Installation")
- "SEPARATE" if they are about different topics (e.g., one about BinLib, another about Enterprise SOC)

Consider them SAME topic only if they would naturally belong in a single cohesive article.

Answer:"""

        try:
            result = subprocess.run(
                [config.CLAUDE_CLI],
                input=validation_prompt,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )

            if result.returncode == 0:
                response = result.stdout.strip().upper()
                # Look for MERGE or SEPARATE in response
                if 'MERGE' in response and 'SEPARATE' not in response:
                    return True
                elif 'SEPARATE' in response:
                    return False
        except Exception as e:
            utils.log_warning(f"Validation failed: {e}, defaulting to separate")

        # Default to keeping separate to avoid bad merges
        return False

    def split_large_group(self, base: str, slugs: List[str], docs: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Split a large group (>5 docs) into semantic subgroups.

        Uses Claude to cluster documents by semantic similarity.
        """
        utils.log(f"Splitting large group '{base}' with {len(slugs)} documents...")

        # For very large groups, use more aggressive splitting
        if len(slugs) > 10:
            # Split into individual topics to avoid creating mega-files
            result = {}
            for slug in slugs:
                result[slug] = [slug]
            utils.log(f"Large group split into {len(result)} individual topics")
            return result

        # For moderate groups (6-10), try to find natural subgroups
        # Prepare summaries
        doc_summaries = []
        for slug in slugs:
            if slug in docs:
                summary = self.extract_topic_keywords(slug, docs[slug])
                doc_summaries.append(summary)

        summaries_text = '\n'.join(doc_summaries)

        # Ask Claude to suggest grouping
        grouping_prompt = f"""Analyze these {len(slugs)} documents and group them into logical subgroups.
Each subgroup should contain documents about the SAME specific topic.

Documents:
{summaries_text}

Output ONLY a JSON object mapping group names to lists of slugs:
{{
  "group-name-1": ["slug1", "slug2"],
  "group-name-2": ["slug3"],
  "group-name-3": ["slug4", "slug5"]
}}

Keep groups small (max 3-4 documents per group). If documents are unrelated, keep them separate.
Use the original slugs exactly as shown above."""

        try:
            result = subprocess.run(
                [config.CLAUDE_CLI],
                input=grouping_prompt,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8'
            )

            if result.returncode == 0:
                response = result.stdout.strip()
                # Extract JSON
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                if start_idx != -1 and end_idx > 0:
                    json_str = response[start_idx:end_idx]
                    groups = json.loads(json_str)

                    # Validate the grouping
                    all_slugs = set(slugs)
                    grouped_slugs = set()
                    for group_slugs in groups.values():
                        grouped_slugs.update(group_slugs)

                    # If grouping is valid, use it
                    if grouped_slugs == all_slugs:
                        utils.log_success(f"Split into {len(groups)} semantic subgroups")
                        return groups
        except Exception as e:
            utils.log_warning(f"Semantic splitting failed: {e}")

        # Fallback: split into individual topics
        result = {}
        for slug in slugs:
            result[slug] = [slug]
        utils.log(f"Fallback: split into {len(result)} individual topics")
        return result

    def group_related_topics(self, category: str, slugs: List[str], docs: Dict[str, str]) -> Dict[str, List[str]]:
        """Group related documents that should be merged into single topics."""
        # Use the new semantic grouping algorithm
        return self.semantic_group_topics(category, slugs, docs)

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
