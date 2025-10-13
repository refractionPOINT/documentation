# Quick Start Guide - Documentation Pipeline Improvements

## Current Status (October 12, 2025)

✅ **Working**: Basic pipeline generates 265 clean markdown pages
❌ **Broken**: Semantic batching and enhancement features
📋 **Next**: Debug Claude CLI integration and implement improvements

## For the Next Developer

### What Was Done

1. **Generated documentation** - 265 markdown files committed
2. **Verified quality** - Assessment complete (see verification report)
3. **Created improvement plan** - Detailed roadmap in `IMPROVEMENT_PLAN.md`
4. **Built debug tools** - Script ready to investigate issues

### Quick Test

Run the debug script to check Claude CLI integration:

```bash
cd doc-pipeline
python3 debug_claude_cli.py
```

This will:
- Test basic JSON responses from Claude
- Test small batch prompts (5 pages)
- Test with real pipeline data (10 pages)
- Identify specific failure points

### Start Here: Phase 1 - Debug & Fix

**Goal**: Get semantic batching working

**Steps**:

1. **Run debug script** (5 min)
   ```bash
   python3 doc-pipeline/debug_claude_cli.py
   ```

2. **Review findings** (10 min)
   - Check console output
   - Review `.doc-pipeline-state/debug_response.txt` if generated
   - Identify if issue is:
     - Response formatting (Claude wrapping JSON in markdown)
     - Prompt size (290 pages too large)
     - Timeout (needs >5 minutes)

3. **Implement fix** (2-4 hours)

   **If response formatting issue:**
   - Update `doc-pipeline/lib/claude_client.py`
   - Add `clean_response()` method (code in debug script)
   - Strip markdown code blocks before JSON parsing

   **If prompt too large:**
   - Implement category-level batching
   - See `IMPROVEMENT_PLAN.md` Priority 2
   - Process 12 categories separately instead of all 290 pages

   **If timeout issue:**
   - Increase `batch_timeout` in config
   - Add progress logging
   - Consider async processing

4. **Test with small dataset** (1 hour)
   ```bash
   # Create test with 10 pages
   python3 -m doc-pipeline --dry-run  # Verify discovery works
   # TODO: Add --max-pages flag for testing
   ```

5. **Verify full pipeline** (30 min)
   ```bash
   # Run on full dataset
   python3 -m doc-pipeline --no-commit

   # Check outputs
   ls -la limacharlie-docs-markdown/API_INDEX.md
   ls -la limacharlie-docs-markdown/COMBINED.md
   ```

### File Organization

```
documentation/
├── IMPROVEMENT_PLAN.md          # Detailed improvement roadmap
├── QUICK_START.md               # This file - start here
├── PIPELINE_USAGE.md            # User guide for running pipeline
├── LIMACHARLIE_DOCS_RECIPE.md   # Original conversion recipe
│
├── doc-pipeline/
│   ├── README.md                # Pipeline overview
│   ├── ARCHITECTURE.md          # Design and phases
│   ├── cli.py                   # Command-line interface
│   ├── pipeline.py              # Main orchestrator
│   ├── config.py                # Configuration
│   ├── models.py                # Data structures
│   ├── debug_claude_cli.py      # Debug script (start here!)
│   │
│   ├── lib/
│   │   ├── fetch.py             # ✅ Working
│   │   ├── convert.py           # ✅ Working
│   │   ├── analyze.py           # ✅ Working
│   │   ├── batch.py             # ❌ Needs fix
│   │   ├── understand.py        # ❌ Blocked by batch.py
│   │   ├── synthesize.py        # ❌ Blocked by understand.py
│   │   ├── claude_client.py     # ⚠️  Needs improvement
│   │   └── verify.py            # ✅ Working
│   │
│   └── tests/
│       ├── test_fetch.py
│       ├── test_convert.py
│       ├── test_analyze.py
│       ├── test_batch.py        # ❌ Currently failing
│       └── test_integration.py
│
├── limacharlie-docs-markdown/   # Generated output (265 pages)
└── .doc-pipeline-state/         # Pipeline state and reports
    ├── 01-fetch.json
    ├── 02-convert.json
    ├── 03-analyze.json
    └── verification_report.json
```

### Key Decisions to Make

Before diving into implementation, consider:

1. **Semantic enhancements vs. quality fixes**
   - Current output is usable without batching/API index
   - Fixing code block loss might be higher priority
   - What's the actual use case? LLM consumption or human docs?

2. **Batching approach**
   - Category-level (12 batches) - simpler, less optimal
   - Semantic sub-batching - better quality, more complex
   - Manual batching config - most control, needs maintenance

3. **Claude CLI vs. API**
   - CLI: Simpler, uses local config
   - API: More control, need credentials management
   - Current code uses CLI - changing would be significant

### Testing Your Changes

```bash
# Run unit tests
cd doc-pipeline
python3 -m pytest tests/ -v

# Run specific test
python3 -m pytest tests/test_batch.py -v

# Run with debugging
python3 -m pytest tests/test_batch.py -v -s

# Test full pipeline (dry run)
python3 -m doc-pipeline --dry-run

# Test full pipeline (real run, no commit)
python3 -m doc-pipeline --no-commit

# Check quality
python3 -c "
import json
with open('.doc-pipeline-state/verification_report.json') as f:
    report = json.load(f)
    print(f'Critical issues: {report[\"critical\"]}')
    print(f'Pages passed: {report[\"passed\"]}/{report[\"total_pages\"]}')
"
```

### Success Criteria (Phase 1)

You're done with Phase 1 when:

- [ ] Debug script shows all tests passing
- [ ] Pipeline runs without errors
- [ ] `API_INDEX.md` generated
- [ ] `COMBINED.md` generated
- [ ] Verification report shows improvement
- [ ] Tests passing

### Getting Help

**Understanding the architecture:**
- Read `doc-pipeline/ARCHITECTURE.md`
- Check `doc-pipeline/README.md`

**Understanding the issue:**
- Run `debug_claude_cli.py`
- Check `.doc-pipeline-state/debug_response.txt`
- Review commit `5e1b6d1` for what was generated

**Understanding the plan:**
- Read `IMPROVEMENT_PLAN.md`
- Focus on Priority 1 first

### Estimated Time

- **Phase 1 (Debug & Fix)**: 12-16 hours
- **Phase 2 (Quality)**: 12-16 hours
- **Phase 3 (Features)**: 8-10 hours
- **Phase 4 (Testing)**: 14-16 hours

**Total**: 46-58 hours (~1.5-2 weeks)

### Questions?

1. Check `IMPROVEMENT_PLAN.md` Open Questions section
2. Review existing code comments
3. Run debug script for diagnostics
4. Check verification report for quality metrics

## Alternative: Skip Semantic Features

If semantic batching proves too complex, consider:

**Option A: Basic pipeline only**
- Keep current working pipeline
- Focus on fixing code block loss
- Manual API index creation
- Estimated time: 1 week instead of 2

**Option B: Different approach**
- Use Claude API directly instead of CLI
- Simpler prompting strategy
- Less ambitious semantic features
- Estimated time: 1-1.5 weeks

**Option C: Hybrid approach**
- Keep working pipeline for basic conversion
- Add post-processing scripts for enhancements
- Separate concerns: conversion vs. enrichment
- Estimated time: 1.5 weeks

Discuss with team before committing to full semantic enhancement implementation.

## Next Commit Should Include

When you're ready to commit your fixes:

```bash
# Add your changes
git add doc-pipeline/

# Commit with clear message
git commit -m "fix: debug and resolve Claude CLI batching issue

- Add response cleaning to handle markdown wrappers
- Implement category-level batching for reliability
- Update tests with smaller fixtures
- Add comprehensive debugging output

Resolves batching failures and enables semantic processing.
"
```

Good luck! 🚀
