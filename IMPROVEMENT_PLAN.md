# Documentation Pipeline Improvement Plan

## Executive Summary

The pipeline successfully generates 265 clean markdown pages but the semantic enhancement features (batching, API indexing, cross-references) are not working. This plan addresses the issues and improves overall quality.

## Current State

**Working:**
- ✅ FETCH: 290 pages discovered via Algolia
- ✅ CONVERT: HTML → Markdown via markitdown
- ✅ ANALYZE: Metadata extraction (keywords, complexity, related pages)
- ✅ VERIFY: Quality validation and reporting

**Broken:**
- ❌ BATCH_GROUP: Claude CLI integration fails with empty JSON response
- ❌ UNDERSTAND: Semantic processing not running
- ❌ SYNTHESIZE: API index and cross-references not generated

**Quality Issues:**
- 387 critical issues (missing code blocks, content loss)
- 957 warnings (missing links, heading mismatches)
- Only 12/290 pages passed without issues

## Priority 1: Debug Claude CLI Integration

### Issue
The semantic batching phase fails when calling Claude CLI:
```
ValueError: Claude returned invalid JSON: Expecting value: line 1 column 1 (char 0)
```

### Root Cause Analysis Needed

**Hypothesis 1: Prompt too large**
- Batching all 290 pages at once may exceed context limits
- Prompt includes all page titles and slugs

**Hypothesis 2: Claude CLI configuration**
- `claude --print` may not be outputting properly
- Stdin/stdout handling issue

**Hypothesis 3: Response format**
- Claude may be outputting markdown wrapper around JSON
- Need to strip formatting before parsing

### Investigation Tasks

1. **Test Claude CLI directly**
   ```bash
   echo "Return JSON: {\"test\": \"value\"}" | claude --print
   ```
   - Verify basic JSON responses work
   - Check for markdown code blocks in output

2. **Create minimal reproduction**
   - Test with 5 pages instead of 290
   - Verify prompt structure
   - Capture raw output before JSON parsing

3. **Add debugging to batch.py**
   - Log raw response before JSON parsing
   - Save failed responses to temp files
   - Add retry with exponential backoff

4. **Review claude_client.py**
   - Consider using `claude --output-format json` if available
   - Add response cleaning (strip markdown, etc.)
   - Validate response before returning

### Implementation Steps

**Step 1: Add response cleaning** (2 hours)
```python
# In claude_client.py
def clean_response(self, raw_output: str) -> str:
    """Remove markdown code blocks and extra formatting."""
    # Strip ```json and ``` wrappers
    if raw_output.strip().startswith('```'):
        lines = raw_output.strip().split('\n')
        # Remove first and last lines if they're code fences
        if lines[0].startswith('```'):
            lines = lines[1:]
        if lines[-1].startswith('```'):
            lines = lines[:-1]
        raw_output = '\n'.join(lines)
    return raw_output.strip()
```

**Step 2: Create test with small dataset** (1 hour)
```bash
# Create test script: doc-pipeline/tests/test_batch_small.py
python3 -m pytest doc-pipeline/tests/test_batch_small.py -v
```

**Step 3: Add better error handling** (1 hour)
- Log raw responses
- Save to `.doc-pipeline-state/failed_responses/`
- Add retry logic with backoff

**Estimated time: 4 hours**

## Priority 2: Incremental Batching Approach

### Problem
Processing 290 pages in one batch is too large for reliable Claude API calls.

### Solution: Multi-stage Batching

**Stage 1: Category-level batching**
- Batch pages by existing category (12 categories)
- Each category processed independently
- Parallelize category processing

**Stage 2: Size-based splitting**
- If category > 30 pages, split into sub-batches
- 5-10 pages per sub-batch
- Maintain semantic coherence

### Implementation

**Update batch.py to support category batching:**

```python
def create_semantic_batches_by_category(
    pages: List[Page],
    claude_client: ClaudeClient,
    category_structure: Dict[str, List[Page]]
) -> List[Dict[str, Any]]:
    """
    Create batches grouped by category first, then semantically within category.

    This reduces prompt size and improves coherence.
    """
    all_batches = []

    for category, category_pages in category_structure.items():
        print(f"Batching category: {category} ({len(category_pages)} pages)")

        if len(category_pages) <= 10:
            # Small category - process as single batch
            batches = [create_single_batch(category, category_pages)]
        else:
            # Large category - use Claude to sub-batch
            batches = create_semantic_batches(category_pages, claude_client)

        all_batches.extend(batches)

    return all_batches
```

**Estimated time: 6 hours**

## Priority 3: Fix Critical Conversion Issues

### Analysis of Critical Issues

From verification report:
- **Missing code blocks**: 387 instances
  - Most common in SDK/API documentation
  - HTML tables with code may not convert properly

- **Content loss**: Pages with <50% word retention
  - Complex layouts confuse markitdown
  - Nested structures get truncated

### Solutions

**Solution 1: Enhanced conversion for code-heavy pages** (4 hours)

Detect pages with many code blocks and use specialized conversion:

```python
def enhanced_convert(html_content: str, page_slug: str) -> str:
    """
    Enhanced conversion for code-heavy pages.
    """
    # Detect if page is code-heavy
    code_block_count = html_content.count('<pre>') + html_content.count('<code')

    if code_block_count > 5:
        # Use BeautifulSoup to extract code blocks first
        preserved_code = extract_code_blocks(html_content)

        # Convert main content
        markdown = markitdown.convert(html_content)

        # Verify code blocks preserved
        if count_code_blocks(markdown) < len(preserved_code):
            # Re-insert missing code blocks
            markdown = reinsert_code_blocks(markdown, preserved_code)

    return markdown
```

**Solution 2: Manual override list** (2 hours)

Maintain list of problematic pages that need special handling:

```python
# doc-pipeline/config.py
MANUAL_CONVERSION_OVERRIDES = {
    'limacharlie-sdk': 'custom_sdk_converter',
    'adapter-types-evtx': 'custom_xml_converter',
}
```

**Solution 3: Verification-driven fixes** (ongoing)

Use verification report to prioritize:
1. Fix top 20 critical pages first
2. Test conversion improvements
3. Re-run verification
4. Iterate

**Estimated time: 6 hours initial, ongoing improvements**

## Priority 4: Generate Missing Artifacts

Once batching works, generate the high-value artifacts:

### API_INDEX.md (2 hours)

Comprehensive API reference:
```markdown
# LimaCharlie API Index

## Organization Management
- `Organization.create(name, template)` - Create new organization
  - **Location**: [Platform Management](/docs/platform-management)
  - **Parameters**: name (str), template (str, optional)
  - **Returns**: Organization object

## Sensor Operations
- `Sensor.task(command, args)` - Execute command on sensor
  - **Location**: [Endpoint Agent Commands](/docs/endpoint-agent-commands)
  ...
```

### COMBINED.md (1 hour)

Single-file documentation:
- Organized by learning path
- Table of contents with anchor links
- Perfect for LLM context loading

### METADATA_INDEX.json (1 hour)

Searchable metadata:
```json
{
  "pages": [
    {
      "slug": "detection-and-response",
      "title": "Detection and Response",
      "complexity": "intermediate",
      "keywords": ["D&R", "rules", "YARA"],
      "prerequisites": ["events", "sensors"],
      "related": [...]
    }
  ],
  "api_index": {...},
  "learning_paths": [...]
}
```

**Estimated time: 4 hours**

## Priority 5: Improve Test Coverage

### Current State
- Unit tests for individual phases
- No integration test that runs full pipeline
- No fixture data for testing

### Improvements

**1. Create test fixture data** (3 hours)
```
doc-pipeline/tests/fixtures/
  ├── sample_pages/
  │   ├── simple.html
  │   ├── code_heavy.html
  │   ├── complex_layout.html
  │   └── expected_output/
  │       ├── simple.md
  │       ├── code_heavy.md
  │       └── complex_layout.md
  └── mock_responses/
      ├── claude_batch_response.json
      └── claude_synthesis_response.json
```

**2. Add integration test** (4 hours)
```python
def test_full_pipeline_with_sample_data():
    """
    Test complete pipeline with 10 sample pages.
    """
    config = Config(
        output_dir=tmp_path / "output",
        state_dir=tmp_path / "state",
    )

    # Use mocked Claude responses
    with patch('doc_pipeline.lib.claude_client.ClaudeClient'):
        success = run_pipeline(config)
        assert success

        # Verify outputs
        assert (tmp_path / "output" / "API_INDEX.md").exists()
        assert (tmp_path / "output" / "COMBINED.md").exists()
```

**3. Add performance benchmarks** (2 hours)
- Track pipeline execution time
- Monitor API call count
- Measure output quality metrics

**Estimated time: 9 hours**

## Implementation Timeline

### Phase 1: Debug & Fix (Week 1)
**Focus**: Get semantic batching working
- [ ] Debug Claude CLI integration (4 hours)
- [ ] Implement incremental batching (6 hours)
- [ ] Test with small dataset (2 hours)
- [ ] Verify full pipeline works end-to-end (2 hours)

**Deliverable**: Pipeline runs successfully with semantic enhancements

### Phase 2: Quality Improvements (Week 2)
**Focus**: Fix conversion issues
- [ ] Enhanced conversion for code-heavy pages (4 hours)
- [ ] Manual override system (2 hours)
- [ ] Fix top 20 critical pages (6 hours)
- [ ] Re-run verification (1 hour)

**Deliverable**: <100 critical issues, >50% pages passing validation

### Phase 3: Complete Features (Week 3)
**Focus**: Generate missing artifacts
- [ ] API_INDEX.md generation (2 hours)
- [ ] COMBINED.md generation (1 hour)
- [ ] METADATA_INDEX.json (1 hour)
- [ ] Cross-reference resolution (2 hours)
- [ ] Documentation and examples (2 hours)

**Deliverable**: Full feature set working

### Phase 4: Testing & Hardening (Week 4)
**Focus**: Reliability and maintainability
- [ ] Create fixture data (3 hours)
- [ ] Integration tests (4 hours)
- [ ] Performance benchmarks (2 hours)
- [ ] Error recovery improvements (3 hours)
- [ ] Documentation updates (2 hours)

**Deliverable**: Production-ready pipeline

## Success Criteria

### Functional Requirements
- ✅ Pipeline runs without errors on full dataset
- ✅ All phases complete successfully
- ✅ API_INDEX.md generated with 100+ APIs
- ✅ COMBINED.md includes all pages
- ✅ Cross-references working between pages

### Quality Metrics
- ✅ <50 critical issues in verification report
- ✅ >80% pages pass basic validation
- ✅ No code block loss in SDK documentation
- ✅ <10% content loss across all pages

### Performance Targets
- ✅ Full pipeline completes in <20 minutes
- ✅ <100 Claude API calls for 290 pages
- ✅ Parallel processing of categories

### Maintainability
- ✅ >80% test coverage
- ✅ Integration test covering full pipeline
- ✅ Clear error messages and logging
- ✅ Documentation for troubleshooting

## Next Steps

1. **Immediate**: Start Phase 1 - Debug Claude CLI integration
2. **This week**: Complete incremental batching implementation
3. **Next week**: Begin quality improvements
4. **Review point**: After Phase 2, assess if semantic enhancements provide enough value

## Open Questions

1. **Should we pursue semantic enhancements or focus on quality?**
   - Current output is usable without semantic features
   - Fixing conversion issues may provide more value
   - Consider ROI of each improvement

2. **What's the target audience?**
   - LLM consumption: Need COMBINED.md and API_INDEX
   - Human readers: Need individual clean pages
   - Both: Need quality first, enhancements second

3. **How often will pipeline run?**
   - Daily: Incremental updates needed
   - Weekly: Full rebuild acceptable
   - On-demand: Current approach works

4. **Integration with existing docs workflow?**
   - Does this replace manual docs?
   - How do we handle manual edits?
   - Version control strategy?
