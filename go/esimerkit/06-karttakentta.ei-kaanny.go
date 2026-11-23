package main

import "fmt"

type Tuote struct{ Saldo int }

func main() {
	varasto := map[string]Tuote{"x1": {10}}
	varasto["x1"].Saldo -= 3 // @virhe: kartan arvo ei ole osoitettavissa
	fmt.Println(varasto)
}
