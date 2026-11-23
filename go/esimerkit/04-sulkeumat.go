// Funktiot arvoina ja sulkeumat: strategia, generaattori ja välikerros.
package main

import (
	"fmt"
	"strings"
)

// @alku tyyppi
// Muunnos on funktiotyyppi. Pienen strategian ilmaisemiseen ei tarvita
// rajapintaa eikä luokkaa.
type Muunnos func(string) string

func ketjuta(muunnokset ...Muunnos) Muunnos {
	return func(s string) string {
		for _, m := range muunnokset {
			s = m(s)
		}
		return s
	}
}

// @loppu tyyppi

// @alku laskuri
// uusiTunnus palauttaa sulkeuman, joka muistaa tilansa.
func uusiTunnus(etuliite string) func() string {
	n := 0
	return func() string {
		n++
		return fmt.Sprintf("%s-%03d", etuliite, n)
	}
}

// @loppu laskuri

func main() {
	siisti := ketjuta(strings.TrimSpace, strings.ToLower,
		func(s string) string { return strings.ReplaceAll(s, " ", "-") })
	fmt.Println(siisti("  Uusi Tilaus Saapui "))

	tilaus := uusiTunnus("T")
	lasku := uusiTunnus("L")
	fmt.Println(tilaus(), tilaus(), lasku(), tilaus())

	// @alku silmukka
	var tehtavat []func()
	for _, nimi := range []string{"a", "b", "c"} {
		// Go 1.22:sta alkaen jokaisella kierroksella on oma muuttuja.
		tehtavat = append(tehtavat, func() { fmt.Print(nimi) })
	}
	for _, t := range tehtavat {
		t()
	}
	fmt.Println()
	// @loppu silmukka
}
