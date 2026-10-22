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

	// Names and metadata only: the record data is never loaded.
	records, err := hive.ListMtd(limacharlie.HiveArgs{
		HiveName:     "lookup",
		PartitionKey: "YOUR_OID",
	})
	if err != nil {
		panic(err)
	}
	for name, record := range records {
		fmt.Println(name, record.UsrMtd.Tags)
	}
}
