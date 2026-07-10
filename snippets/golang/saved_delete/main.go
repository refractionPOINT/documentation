package main

import (
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
	if _, err := hive.Remove(limacharlie.HiveArgs{
		HiveName:     "query",
		PartitionKey: "YOUR_OID",
		Key:          "my-saved-query",
	}); err != nil {
		panic(err)
	}
}
