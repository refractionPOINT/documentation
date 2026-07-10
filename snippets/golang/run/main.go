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

	// The Go SDK's Query takes the full LCQL string (time range included).
	resp, err := org.Query(limacharlie.QueryRequest{
		Query:      "-1h | * | * | event/FILE_PATH ends with '.exe'",
		Stream:     "event",
		LimitEvent: 1000,
	})
	if err != nil {
		panic(err)
	}
	for _, r := range resp.Results {
		fmt.Println(r)
	}
}
