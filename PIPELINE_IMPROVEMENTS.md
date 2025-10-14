# Documentation Pipeline Improvements

## Problem Summary

The original pipeline was producing vague, incoherent documentation with critical issues:

### Critical Issues Identified:

1. **Broken Grouping Algorithm**
   - Naive string matching: `slug.rsplit('-', 1)[0]` grouped ALL `en-*` files together
   - Result: 317-line `en.md` file combining BinLib, Enterprise SOC, and LCQL (completely unrelated topics)
   - Result: 754-line `en-tags.md` file mixing platform concepts, APIs, alerts, and K8s deployment

2. **Missing Content**
   - Hive documentation existed in `cleaned-markdown/` but never made it to `topics/`
   - Phase 6 (synthesis) was terminated before completion

3. **No Validation**
   - No semantic check that grouped content was related
   - No validation of topic coherence
   - Language prefixes (`en-`, `fr-`) treated as semantic indicators

4. **Vague Output**
   - Mixed topics created confusing context for LLMs
   - Technical depth lost in merge process
   - Self-containment violated

## Solutions Implemented

### 1. Intelligent Semantic Grouping (06_synthesize.py)

**New Features:**
- **Language prefix stripping**: Removes `en-`, `fr-`, etc. before grouping
- **Semantic validation**: Uses Claude to verify documents are actually related before merging
- **Smart size limits**:
  - Groups >10 docs: Split into individual topics (avoid mega-files)
  - Groups 6-10 docs: Use Claude to find semantic subgroups
  - Groups 3-5 docs: Validate relatedness before merging
  - Groups ≤2 docs: Keep as-is

**Key Methods:**
```python
strip_language_prefix()           # Remove en-, fr- prefixes
semantic_group_topics()            # Smart grouping with validation
validate_group_relatedness()      # Claude-based validation
split_large_group()               # Break up large groups intelligently
```

### 2. Enhanced Synthesis Prompt (prompts/synthesize_topics.md)

**Critical Addition:**
```markdown
## CRITICAL VALIDATION RULE

**BEFORE merging documents, you MUST verify they are about the SAME specific topic.**

- ✅ MERGE: "Config Hive API", "Config Hive CLI" → All about Config Hive
- ❌ DO NOT MERGE: "BinLib", "Enterprise SOC", "LCQL" → Different topics
```

**Requirements Added:**
- Validate relatedness FIRST
- Preserve ALL technical details (no summarization)
- Keep unrelated content separate
- If unsure, default to NOT merging

### 3. Quality Validation Phase (07_validate.py)

**New Checks:**
- **Topic Coherence**: Detect files with multiple unrelated h1 headings
- **Mega-file Detection**: Flag files >500 lines
- **Technical Depth**: Verify code examples, commands, parameters present
- **Self-containment**: Check for excessive external references
- **Coverage**: Ensure all cleaned docs are represented

**Outputs:**
- `validation_report.json`: Full quality assessment
- `topic_map.json`: LLM-optimized topic index

### 4. Pipeline Updates (run_pipeline.py)

- Added Phase 7 (Validation)
- Updated help text and argument choices (1-7)
- Better error handling and reporting

## Expected Results

### Before:
```
topics/concepts/en.md (317 lines)
├── BinLib
├── Enterprise SOC
└── LCQL

topics/concepts/en-tags.md (754 lines)
├── Platform concepts
├── API integration
├── Alert rules
├── Kubernetes
└── CI/CD events
```

### After:
```
topics/concepts/binlib.md
topics/concepts/enterprise-soc.md
topics/concepts/lcql.md
topics/concepts/config-hive.md ← Now discoverable!
topics/concepts/platform-and-use-cases.md
topics/concepts/api-integrations.md
... (each focused on ONE topic)
```

## How to Verify Improvements

### 1. Check Topic Quality
```bash
# Count topics
find output/topics -name "*.md" | wc -l

# Check for mega-files (should be none or few)
find output/topics -name "*.md" -exec wc -l {} \; | sort -n | tail -20

# Look for Hive
find output/topics -name "*hive*.md"
grep -r "Config Hive" output/topics/
```

### 2. Test LLM Queries
```bash
# Should now find Hive documentation
grep -i "hive" output/metadata/topic_map.json

# Sample queries that should work:
# - "How do I configure Hive lookups?"
# - "What is BinLib?" (should get focused answer)
# - "How do I use LCQL?" (should get focused answer)
```

### 3. Review Validation Report
```bash
cat output/metadata/validation_report.json

# Check stats:
# - total_issues: Should be 0 or very low
# - total_warnings: Review any warnings
# - topics_by_category: Verify reasonable distribution
```

## Technical Details

### Semantic Grouping Algorithm

1. **Strip language prefixes**
   - `en-config-hive` → `config-hive`
   - `fr-detection-rules` → `detection-rules`

2. **Initial grouping by topic hierarchy**
   - `config-hive-lookups` → group: `config-hive`
   - `config-hive-secrets` → group: `config-hive`
   - But: `adapter-types-s3` ≠ `adapter-examples-stdin` (different contexts)

3. **Validate with Claude**
   - Extract title + first 500 chars from each doc
   - Ask: "Are these about the SAME topic?"
   - Response: MERGE or SEPARATE

4. **Handle large groups**
   - >10 docs: Always split into individual topics
   - 6-10 docs: Ask Claude to suggest semantic subgroups
   - 3-5 docs: Validate, split if unrelated
   - ≤2 docs: Keep together

### Performance Considerations

- Validation adds ~30s per group (Claude API calls)
- Large groups (>10 docs) skip validation for speed
- Fallback: Default to separation (safer than bad merge)
- Parallelization possible for future optimization

## Migration Notes

### Backup
Old topics backed up to: `output/topics-backup-old-TIMESTAMP/`

### Re-running
```bash
# Full re-synthesis from scratch
python3 pipeline/run_pipeline.py --start 6 --end 7

# Just validation on existing topics
python3 pipeline/run_pipeline.py --start 7 --end 7
```

### Troubleshooting

**Issue**: Phase 6 takes too long
- **Cause**: Validating many groups with Claude
- **Solution**: Consider reducing `MAX_PARALLEL_WORKERS` or increasing timeout

**Issue**: Still seeing merged unrelated topics
- **Cause**: Validation threshold too lenient
- **Solution**: Update `validate_group_relatedness()` to be more strict

**Issue**: Too many individual topics (not merging related ones)
- **Cause**: Validation threshold too strict
- **Solution**: Adjust semantic grouping in `semantic_group_topics()`

## Success Metrics

✅ **No files >500 lines** (prevents mega-files)
✅ **Each topic focused on ONE concept** (coherence)
✅ **Hive documentation discoverable** (coverage)
✅ **Technical details preserved** (depth)
✅ **All cleaned docs represented** (completeness)
✅ **LLM can find specific topics** (retrievability)

## Next Steps

1. **Monitor synthesis completion** (check `/tmp/synthesis-fixed.log`)
2. **Review validation report** (`output/metadata/validation_report.json`)
3. **Test LLM retrieval** with sample queries
4. **Iterate on thresholds** if needed
5. **Document edge cases** for future improvements

## Files Modified

- `pipeline/06_synthesize.py` - Complete rewrite of grouping logic
- `pipeline/prompts/synthesize_topics.md` - Added validation requirements
- `pipeline/07_validate.py` - New validation phase (created)
- `pipeline/run_pipeline.py` - Added phase 7 support

## Files Created

- `pipeline/07_validate.py` - Quality validation
- `output/metadata/validation_report.json` - Quality report
- `output/metadata/topic_map.json` - LLM retrieval index
- `PIPELINE_IMPROVEMENTS.md` - This document
