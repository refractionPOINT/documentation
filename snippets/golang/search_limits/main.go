// Read an organization's resolved search limits.
//
// The execution limits are pointers because a limit that is not enforced is
// nil, never 0: in a set of limits a zero would read as "nothing allowed".
package main

import (
	"fmt"

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

	limits, err := org.GetSearchLimits()
	if err != nil {
		panic(err)
	}

	fmt.Printf("concurrent queries: %d\n", limits.Concurrency.MaxConcurrentQueries)
	fmt.Printf("results per page:   %d\n", limits.Pagination.ResultsPerPage)
	fmt.Printf("max page duration:  %ds\n", limits.Pagination.MaxPageDurationSeconds)
	fmt.Printf("max cursor bytes:   %d\n", limits.Pagination.MaxCursorBytes)
	fmt.Printf("resumable for:      %ds\n", limits.Retention.ResumableForSeconds)
	fmt.Printf("page results kept:  %ds\n", limits.Retention.PageResultsForSeconds)
	fmt.Printf("max request body:   %d bytes\n", limits.Request.MaxRequestBodyBytes)
	fmt.Printf("open-query listing: %t\n", limits.Capabilities.OpenQueryListing)

	// Nil is "no limit applies". Dereferencing without the check panics, and
	// reading a zero value as the limit gets the contract exactly backwards.
	if d := limits.Execution.MaxQueryDurationSeconds; d != nil {
		fmt.Printf("query duration:     cut off after %ds\n", *d)
	} else {
		fmt.Println("query duration:     not enforced")
	}
	if n := limits.Execution.MaxResponseBytes; n != nil {
		fmt.Printf("max response:       %d bytes\n", *n)
	} else {
		fmt.Println("max response:       not enforced")
	}
}
