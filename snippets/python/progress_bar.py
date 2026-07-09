"""Compute a Query Console-style progress bar from Search API responses.

The Search API reports progress with batch counters. Before a search runs, the
validate response carries the whole-query denominator as ``stats.batchesInScope``.
Once the search is running, every page carries both the denominator and the
numerator under ``stats.cumulativeStats`` (``batchesInScope`` and
``batchesCompleted``). The progress bar is ``batchesCompleted / batchesInScope``,
clamped to 0-100% - the same formula the Query Console uses.
"""

from typing import Optional


def progress_percent(batches_completed: int, batches_in_scope: int) -> float:
    """Return query completion as a percentage in the range [0, 100].

    ``batches_in_scope`` is the whole-query denominator and ``batches_completed``
    is the numerator carried on each page. A zero (or missing) denominator means
    the scope is not known yet, so progress is reported as 0. The result is
    clamped to 100 because the numerator can briefly exceed the denominator when
    a batch is re-opened across page boundaries.
    """
    if batches_in_scope <= 0:
        return 0.0
    return max(0.0, min(100.0, 100.0 * batches_completed / batches_in_scope))


def _cumulative_stats(page: dict) -> Optional[dict]:
    """Return the ``cumulativeStats`` block from a Search API page, or ``None``."""
    for result in page.get("results", []):
        cumulative = (result.get("stats") or {}).get("cumulativeStats")
        if cumulative:
            return cumulative
    return None


def page_progress_percent(page: dict) -> float:
    """Compute progress from one Search API page (a parsed ``SearchResponse``).

    Returns 100.0 once the search reports completion (the completion flag is the
    authoritative "done" signal), and 0.0 until the scope is known (no
    ``cumulativeStats`` yet).
    """
    if page.get("completed"):
        return 100.0
    cumulative = _cumulative_stats(page)
    if not cumulative:
        return 0.0
    return progress_percent(
        cumulative.get("batchesCompleted", 0),
        cumulative.get("batchesInScope", 0),
    )


if __name__ == "__main__":
    # A page reporting 50 of 200 batches completed -> 25%.
    example_page = {
        "completed": False,
        "results": [
            {"stats": {"cumulativeStats": {"batchesInScope": 200, "batchesCompleted": 50}}}
        ],
    }
    print(f"{page_progress_percent(example_page):.0f}% complete")
