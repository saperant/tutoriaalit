// Perustyypit, nolla-arvot, muunnokset ja vakiot.
package main

import (
	"fmt"
	"math"
)

// @alku vakiot
type Taso int

// iota numeroi vakiot. Tyypitetty vakio estää sekoittamasta tasoa
// tavalliseen kokonaislukuun vahingossa.
const (
	Virhe Taso = iota
	Varoitus
	Info
	Debug
)

const kilotavu = 1 << 10 // tyypitön vakio: tarkkuus säilyy

// @loppu vakiot

func main() {
	// @alku nolla
	var (
		lkm    int
		nimi   string
		valmis bool
		suhde  float64
		osoite *int
	)
	fmt.Printf("%d %q %t %g %v\n", lkm, nimi, valmis, suhde, osoite)
	// @loppu nolla

	// @alku muunnokset
	var tavut int64 = 3 * kilotavu
	var lohkot int32 = 512
	// tavut / lohkot ei käänny: tyypit on muunnettava itse.
	fmt.Println(tavut / int64(lohkot))
	x := 2.99
	fmt.Println(int(x), int(-x), math.Round(x)) // katkaisu kohti nollaa
	var pieni uint8 = 250
	pieni += 10 // kiertää ilman varoitusta
	fmt.Println(pieni, math.MaxInt64)
	// @loppu muunnokset

	// @alku taso
	taso := Info
	fmt.Println(taso, taso > Varoitus, Debug-Virhe)
	// @loppu taso
}
