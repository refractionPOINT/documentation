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

	est, err := org.EstimateLCQLQueryBilling("-1h | * | * | event/FILE_PATH ends with '.exe'")
	if err != nil {
		panic(err)
	}
	fmt.Printf("billed events: %d, estimated price: %.2f %s\n",
		est.BilledEvents, est.EstimatedPrice.Price, est.EstimatedPrice.Currency)
}
