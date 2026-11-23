package main

import (
	"fmt"
	"os" // @virhe: käyttämätön tuonti on käännösvirhe
)

func main() {
	tulos, err := fmt.Println("tallennetaan")
	virheita := 0 // @virhe: käyttämätön muuttuja on käännösvirhe
	if err != nil {
		return
	}
	fmt.Println("kirjoitettiin", tulos, "tavua")
}
