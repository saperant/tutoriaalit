package main

import "fmt"

type Asetukset struct{ Portti int }

// lataa palauttaa nil-osoittimen, kun asetuksia ei ole. Kutsuja unohtaa
// tarkistaa sen.
func lataa(nimi string) *Asetukset {
	if nimi == "tuotanto" {
		return &Asetukset{Portti: 443}
	}
	return nil
}

func main() {
	a := lataa("testi")
	fmt.Println("portti:", a.Portti)
}
