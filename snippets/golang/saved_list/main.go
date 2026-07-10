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
	queries, err := hive.List(limacharlie.HiveArgs{
		HiveName:     "query",
		PartitionKey: "YOUR_OID",
	})
	if err != nil {
		panic(err)
	}
	fmt.Println(queries)
}
