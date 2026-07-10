// Command progress_bar shows how to compute a Query Console-style progress bar
// from LimaCharlie Search API responses.
//
// The Search API reports progress with batch counters. Before a search runs the
// validate response carries the whole-query denominator as stats.batchesInScope;
// once it is running every page carries both the denominator and the numerator
// under stats.cumulativeStats (batchesInScope and batchesCompleted). The bar is
// batchesCompleted / batchesInScope, clamped to 0-100% - the same formula the
// Query Console uses.
package main

import (
	"encoding/json"
	"fmt"
)

// searchPage is a minimal view of a Search API page response (SearchResponse).
// Only the fields needed to compute progress are modeled.
type searchPage struct {
	Completed bool `json:"completed"`
	Results   []struct {
		Stats struct {
			CumulativeStats *struct {
				BatchesInScope   uint64 `json:"batchesInScope"`
				BatchesCompleted uint64 `json:"batchesCompleted"`
			} `json:"cumulativeStats"`
		} `json:"stats"`
	} `json:"results"`
}

// progressPercent returns query completion as a percentage in [0, 100].
//
// batchesInScope is the whole-query denominator and batchesCompleted is the
// numerator carried on each page. A zero denominator means the scope is not
// known yet, so progress is 0. The result is clamped to 100 because the
// numerator can briefly exceed the denominator when a batch is re-opened across
// page boundaries.
func progressPercent(batchesCompleted, batchesInScope uint64) float64 {
	if batchesInScope == 0 {
		return 0
	}
	pct := 100 * float64(batchesCompleted) / float64(batchesInScope)
	if pct > 100 {
		return 100
	}
	return pct
}

// pageProgressPercent computes progress from one Search API page response body.
// It returns 100 once the search reports completion, and 0 until the scope is
// known (no cumulativeStats yet).
func pageProgressPercent(body []byte) (float64, error) {
	var page searchPage
	if err := json.Unmarshal(body, &page); err != nil {
		return 0, err
	}
	if page.Completed {
		return 100, nil
	}
	for _, r := range page.Results {
		if c := r.Stats.CumulativeStats; c != nil {
			return progressPercent(c.BatchesCompleted, c.BatchesInScope), nil
		}
	}
	return 0, nil
}

func main() {
	// A page reporting 50 of 200 batches completed -> 25%.
	body := []byte(`{"completed":false,"results":[{"stats":{"cumulativeStats":{"batchesInScope":200,"batchesCompleted":50}}}]}`)
	pct, err := pageProgressPercent(body)
	if err != nil {
		panic(err)
	}
	fmt.Printf("%.0f%% complete\n", pct)
}
