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
	args := limacharlie.HiveArgs{
		HiveName:     "lookup",
		PartitionKey: "YOUR_OID",
	}

	// Walk the hive one page at a time, so only one page is in memory.
	err = hive.ListPages(args, limacharlie.ListPageOptions{Limit: 100}, func(page limacharlie.HiveConfigData) error {
		for name, record := range page {
			fmt.Println(name, record.UsrMtd.Enabled)
		}
		return nil
	})
	if err != nil {
		panic(err)
	}
}
