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

	hive := limacharlie.NewHiveClient(org)
	saved, err := hive.Get(limacharlie.HiveArgs{
		HiveName:     "query",
		PartitionKey: "YOUR_OID",
		Key:          "my-saved-query",
	})
	if err != nil {
		panic(err)
	}

	resp, err := org.Query(limacharlie.QueryRequest{
		Query:  saved.Data["query"].(string),
		Stream: "event",
	})
	if err != nil {
		panic(err)
	}
	for _, r := range resp.Results {
		fmt.Println(r)
	}
}
