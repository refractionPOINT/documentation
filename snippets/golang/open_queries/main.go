// List the searches an organization currently has open.
//
// SlotsHeld is what the concurrent-query limit applies to. Count is everything
// the organization has open, including paginated searches parked between pages,
// which are resumable but consume no slot.
package main

import (
	"context"
	"fmt"
	"sort"

	limacharlie "github.com/refractionPOINT/go-limacharlie/limacharlie"
)

func main() {
	org, err := limacharlie.NewOrganizationFromClientOptions(limacharlie.ClientOptions{
		OID:    "YOUR_OID",
		APIKey: "YOUR_API_KEY",
	}, nil)
	if err != nil {
		panic(err)
	}

	// State accepts "all" (the default), "executing" and "idle".
	open, err := org.ListOpenQueries(limacharlie.OpenSearchQueriesFilters{State: "executing"})
	if err != nil {
		panic(err)
	}
	fmt.Printf("%d of %d slots in use, %d search(es) open\n",
		open.SlotsHeld, open.Limit, open.Count)

	// Biggest scanner first - usually the one worth cancelling.
	sort.Slice(open.Queries, func(i, j int) bool {
		return open.Queries[i].EventsScanned > open.Queries[j].EventsScanned
	})
	for _, q := range open.Queries {
		fmt.Printf("%s by=%s scanned=%d billed=%d\n",
			q.QueryID, q.SubmittedBy, q.EventsScanned, q.BilledEvents)
	}

	// ListAllOpenQueries walks the whole listing rather than one server page.
	all, err := org.ListAllOpenQueries(context.Background(), "all")
	if err != nil {
		panic(err)
	}
	for _, q := range all {
		// HoldsSlot is nil only when State is "unknown", which means slot
		// tracking is unavailable - not that the search holds no slot.
		slot := "unknown"
		if q.HoldsSlot != nil {
			slot = fmt.Sprintf("%t", *q.HoldsSlot)
		}
		// ProgressPercent is nil when there is no denominator to divide by.
		progress := "unknown"
		if q.ProgressPercent != nil {
			progress = fmt.Sprintf("%.0f%%", *q.ProgressPercent)
		}
		fmt.Printf("%s state=%s holdsSlot=%s pages=%d progress=%s\n",
			q.QueryID, q.State, slot, q.PagesCompleted, progress)
	}
}
