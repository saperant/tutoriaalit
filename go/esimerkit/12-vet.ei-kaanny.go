package main

import "fmt"

func main() {
	nimi, maara := "kahvi", 3
	fmt.Printf("%d kpl tuotetta %d\n", maara, nimi) // @virhe: go vet
	fmt.Printf("%d kpl tuotetta %s\n", maara, nimi)
}
