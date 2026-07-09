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
	enabled := true
	if _, err := hive.Add(limacharlie.HiveArgs{
		HiveName:     "query",
		PartitionKey: "YOUR_OID",
		Key:          "my-saved-query",
		Data: limacharlie.Dict{
			"query":  "event/FILE_PATH ends with .exe",
			"stream": "event",
		},
		Enabled: &enabled,
	}); err != nil {
		panic(err)
	}
}
