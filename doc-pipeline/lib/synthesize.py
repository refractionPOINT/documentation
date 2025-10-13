"""Synthesis of processed documentation into coherent knowledge base."""
import json
from typing import List, Dict, Any
from collections import defaultdict
import tempfile
from pathlib import Path
from .understand import ProcessedTopic
from .claude_client import ClaudeClient


def build_api_index(
    topics: List[ProcessedTopic],
    claude_client: ClaudeClient
) -> str:
    """
    Build comprehensive API index from all extracted APIs.

    Args:
        topics: All processed topics
        claude_client: Claude client for synthesis

    Returns:
        Markdown API index
    """
    # Collect all APIs
    all_apis = []
    api_to_topics = defaultdict(list)

    for topic in topics:
        for api in topic.extracted_apis:
            api_name = api['name']
            api_to_topics[api_name].append(topic.slug)
            all_apis.append({
                'name': api_name,
                'signature': api['signature'],
                'description': api['description'],
                'topics': api_to_topics[api_name]
            })

    # Deduplicate by name
    unique_apis = {}
    for api in all_apis:
        name = api['name']
        if name not in unique_apis:
            unique_apis[name] = api
        else:
            # Merge topic references
            unique_apis[name]['topics'] = list(set(
                unique_apis[name]['topics'] + api['topics']
            ))

    # Ask Claude to organize and enrich
    apis_json = json.dumps(list(unique_apis.values()), indent=2)

    prompt = f"""Create a comprehensive API index from these extracted APIs.

APIs:
{apis_json}

Organize by:
1. Category (Sensor APIs, Detection APIs, Platform APIs, etc.)
2. Alphabetically within category
3. Include signature and description
4. List all topics where each API appears

Output markdown with this structure:

# API Index

## Category Name

- `api_name(signature)`: Description
  - Topics: topic1, topic2

Output only the markdown, no code blocks."""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(prompt)
        prompt_file = f.name

    try:
        return claude_client.run_subagent_prompt(prompt_file)
    finally:
        Path(prompt_file).unlink()


def resolve_cross_references(topics: List[ProcessedTopic]) -> List[ProcessedTopic]:
    """
    DEPRECATED: This function is not used in the transformation-based pipeline.

    In the new model, prerequisites and related_topics are handled during
    the transformation phase, not as a post-processing step.

    Args:
        topics: Processed topics

    Returns:
        Topics unchanged
    """
    # In the new transformation model, cross-references are handled
    # during the Claude transformation phase via prerequisites and related_topics
    # This function is kept for backwards compatibility but is a no-op
    return topics
