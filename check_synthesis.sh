#!/bin/bash
# Quick status check for synthesis pipeline

echo "=== Synthesis Pipeline Status ==="
echo

# Check if process is running
if pgrep -f "run_pipeline.py" > /dev/null; then
    echo "✓ Pipeline is RUNNING"
    echo

    # Show recent progress
    echo "=== Recent Progress (last 20 lines) ==="
    tail -20 /tmp/synthesis-fixed.log
    echo

    # Show stats
    echo "=== Current Stats ==="
    echo "Topics created: $(find output/topics -name "*.md" 2>/dev/null | wc -l)"
    echo "  - Tasks: $(find output/topics/tasks -name "*.md" 2>/dev/null | wc -l)"
    echo "  - Concepts: $(find output/topics/concepts -name "*.md" 2>/dev/null | wc -l)"
    echo "  - Reference: $(find output/topics/reference -name "*.md" 2>/dev/null | wc -l)"
    echo
else
    echo "✗ Pipeline is NOT running"
    echo

    # Check if it completed
    if grep -q "PIPELINE COMPLETE" /tmp/synthesis-fixed.log 2>/dev/null; then
        echo "✓ Pipeline COMPLETED successfully!"
        echo
        tail -30 /tmp/synthesis-fixed.log
    elif grep -q "failed" /tmp/synthesis-fixed.log 2>/dev/null; then
        echo "✗ Pipeline FAILED"
        echo
        tail -30 /tmp/synthesis-fixed.log
    else
        echo "? Pipeline status unknown"
    fi
fi

echo
echo "=== Full log: /tmp/synthesis-fixed.log ==="
echo "=== Monitor: watch -n 10 bash check_synthesis.sh ==="
