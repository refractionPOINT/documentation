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

	result, err := org.ValidateLCQLQuery("-1h | * | * | event/FILE_PATH ends with '.exe'")
	if err != nil {
		panic(err)
	}
	if result.Error != "" {
		fmt.Printf("invalid query: %s\n", result.Error)
	}
}
