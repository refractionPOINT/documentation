# Documentation Pipeline Architecture

## Overview

This pipeline transforms web-based documentation into LLM-optimized markdown through intelligent processing powered by Claude AI.

## Design Principles

1. **Transformation Over Conversion**: Claude transforms human-oriented documentation into LLM-optimized topics, not 1:1 HTML→Markdown conversion
2. **Topic-Based Organization**: Documentation reorganized into self-contained topics (task/concept/reference), not page-by-page replication
3. **Batched Processing**: Related pages processed together to extract coherent topics across boundaries
4. **Parallel Execution**: Concurrent subagent processing for speed without sacrificing quality
5. **Self-Contained Content**: Each topic includes all needed information, eliminating navigation dependencies

## Pipeline Phases

### 1. FETCH
**Purpose**: Discover and download source documentation

**Implementation**: `doc-pipeline/lib/fetch.py`

- Uses Algolia search API to discover all documentation pages
- Filters by version (current version only)
- Downloads HTML content
- Handles pagination, rate limiting, retries

**Output**: List of `Page` objects with HTML content

### 2. BATCH_GROUP
**Purpose**: Group related pages for coherent processing

**Implementation**: `doc-pipeline/lib/batch.py`

- Claude analyzes all page titles and URLs
- Creates semantic batches of 5-10 related pages
- Batches based on:
  - Topical coherence
  - Workflow relationships
  - API surface similarity

**Why batching matters**: Pages processed together allow Claude to:
- Identify common patterns
- Create accurate cross-references
- Understand terminology consistency
- Extract complete API signatures from examples spread across pages

**Output**: List of batch definitions with page assignments

### 3. PARALLEL_UNDERSTAND
**Purpose**: Transform HTML into LLM-optimized markdown

**Implementation**: `doc-pipeline/lib/understand.py`

**Process**:
1. For each batch, generate specialized prompt
2. Launch Claude subagent via CLI (`claude --prompt-file ...`)
3. Run 10-40 subagents concurrently (asyncio)
4. Each subagent:
   - Reads HTML for all pages in batch
   - Understands purpose (tutorial/reference/concept)
   - Extracts APIs with full signatures
   - Identifies cross-references within batch
   - Generates enhanced markdown

**Subagent Prompt Template**: `doc-pipeline/prompts/batch_processing.md`

**Output Schema** (per topic):
```json
{
  "topics": [
    {
      "slug": "descriptive-topic-name",
      "title": "Human-Readable Topic Title",
      "type": "task|concept|reference",
      "content": "# Title\n\nComplete, self-contained markdown...",
      "source_pages": ["original-slug-1", "original-slug-2"],
      "extracted_apis": [
        {
          "name": "function()",
          "signature": "function(param: Type) -> ReturnType",
          "description": "What it does and when to use it"
        }
      ],
      "prerequisites": ["other-topic-slug-needed-first"],
      "related_topics": ["similar-topic-slug"],
      "keywords": ["primary", "terms", "alternate", "phrasings"]
    }
  ]
}
```

**Key Differences from Page-Based Model**:
- Multiple pages can be merged into one topic
- One page can be split into multiple topics
- Topics are self-contained with all needed context
- Prerequisites/related_topics replace navigation-based cross-refs

**Error Handling**:
- Automatic retry with exponential backoff (3 attempts)
- Batch isolation (one failure doesn't stop others)
- Timeout protection (5 min per batch)

**Output**: Dictionary mapping batch_id to list of `ProcessedTopic` objects

### 4. SYNTHESIZE
**Purpose**: Integrate batch outputs into coherent knowledge base

**Implementation**: `doc-pipeline/lib/synthesize.py`

**Sub-phases**:

**A. API Index Building**:
- Collect all extracted APIs from all batches
- Deduplicate by API name
- Use Claude to organize by category
- Add usage patterns and common workflows
- Output: `API_INDEX.md`

**B. Cross-Reference Resolution** (deprecated in transformation model):
- Prerequisites and related_topics are now handled during transformation phase
- No post-processing needed for cross-references

**C. Gap Detection** (future):
- Identify APIs without tutorials
- Flag missing conceptual explanations
- Report documentation holes

**Output**:
- `API_INDEX.md`
- `METADATA_INDEX.json`
- Topics organized by type (tasks/, concepts/, reference/)

### 5. ENHANCE (planned)
**Purpose**: Global-level optimizations

**Future capabilities**:
- Generate learning paths
- Create concept maps
- Add per-category overviews
- Build intelligent `COMBINED.md`

### 6. VERIFY (planned)
**Purpose**: Semantic validation

**Future checks**:
- Accuracy against source HTML
- Hallucination detection
- API completeness
- Cross-reference validity

### 7. DETECT
**Purpose**: Track changes via Git

**Implementation**: `doc-pipeline/lib/detect.py` (existing)

- Git diff analysis
- Categorize changes (structural vs content)
- Generate human-readable report
- Auto-commit if enabled

## Data Flow

```
Page (HTML)
  → Batch (5-10 Pages)
    → ProcessedTopic (transformed, self-contained markdown)
      → Synthesized (API index)
        → Output Files by Type (tasks/*.md, concepts/*.md, reference/*.md + .json)
          → Git Commit
```

## Key Data Structures

**Page** (`models.py`):
```python
@dataclass
class Page:
    slug: str           # URL identifier
    title: str          # Page title
    url: str            # Full URL
    html_content: str   # Raw HTML
```

**ProcessedTopic** (`lib/understand.py`):
```python
@dataclass
class ProcessedTopic:
    slug: str                          # Topic identifier
    title: str                         # Human-readable title
    type: str                          # task, concept, or reference
    content: str                       # Complete markdown
    source_pages: List[str]            # Original page slugs
    extracted_apis: List[Dict[str, str]]
    prerequisites: List[str]           # Topic slugs needed first
    related_topics: List[str]          # Related topic slugs
    keywords: List[str]                # Search terms
```

**Batch**:
```python
{
    'id': 'batch_01_name',
    'theme': 'What this batch covers',
    'pages': [Page, Page, ...],
    'page_slugs': ['slug1', 'slug2', ...]
}
```

## Performance Characteristics

### Speed
- **Fetch**: ~30 seconds (290 pages with rate limiting)
- **Batch Group**: ~10 seconds (single Claude call)
- **Parallel Understand**: ~5-10 minutes (30-40 concurrent subagents)
- **Synthesize**: ~30 seconds (API index + cross-refs)
- **Total**: ~10-15 minutes

### Quality Gains vs. Previous Pipeline
- ✅ Semantic understanding (not blind conversion)
- ✅ Rich cross-references (not just navigation)
- ✅ Complete API documentation (signatures + context)
- ✅ Explicit prerequisites and relationships
- ✅ Warnings and gotchas preserved with semantic markup
- ✅ Code examples with usage explanations

### Cost
- ~40 Claude API calls per run (batching + synthesis)
- Optimized through batching (290 pages → 40 calls, not 290 calls)

## Configuration

Key settings in `config.py`:

```python
@dataclass
class Config:
    # Claude
    max_concurrent_batches: int = 10  # Parallel subagents
    batch_timeout: int = 300          # 5 min per batch

    # Batching
    min_batch_size: int = 5
    max_batch_size: int = 10

    # Features
    extract_api_signatures: bool = True
    generate_summaries: bool = True
    add_cross_references: bool = True
```

## Testing Strategy

1. **Unit Tests**: Each phase tested in isolation with mocks
2. **Integration Tests**: Full pipeline with mocked Claude responses
3. **End-to-End**: Real execution on small doc subset (manual)

## Future Enhancements

1. **Incremental Updates**: Only process changed pages
2. **Multi-Version Support**: Maintain docs for multiple product versions
3. **Quality Scoring**: Automatically rate documentation completeness
4. **Interactive Mode**: Allow human review/editing between phases
5. **Custom Subagent Skills**: Specialized prompts for API docs vs tutorials
