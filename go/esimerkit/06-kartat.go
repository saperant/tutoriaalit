// Kartat: haku "pilkku ok" -muodossa, joukot ja järjestetty läpikäynti.
package main

import (
	"fmt"
	"maps"
	"slices"
	"strings"
)

type Tuote struct {
	Nimi  string
	Saldo int
}

func main() {
	// @alku perus
	hinnat := map[string]int{"kahvi": 450, "tee": 300}
	hinta, ok := hinnat["kaakao"] // puuttuva avain: nolla-arvo ja false
	fmt.Println(hinta, ok, len(hinnat))
	delete(hinnat, "tee")
	hinnat["mehu"] += 250 // += toimii puuttuvallekin avaimelle
	for _, nimi := range slices.Sorted(maps.Keys(hinnat)) {
		fmt.Print(nimi, "=", hinnat[nimi], " ")
	}
	fmt.Println()
	// @loppu perus

	// @alku joukko
	nahdyt := make(map[string]struct{}) // tyhjä rakenne ei vie tilaa
	var kaksoiset []string
	for _, sana := range strings.Fields("a b a c b a") {
		if _, ok := nahdyt[sana]; ok {
			kaksoiset = append(kaksoiset, sana)
			continue
		}
		nahdyt[sana] = struct{}{}
	}
	slices.Sort(kaksoiset)
	fmt.Println(len(nahdyt), slices.Compact(kaksoiset))
	// @loppu joukko

	// @alku arvot
	varasto := map[string]Tuote{"x1": {"Ruuvi", 10}}
	t := varasto["x1"] // kopio: kartan arvoa ei voi muuttaa paikallaan
	t.Saldo -= 3
	varasto["x1"] = t
	osoitteet := map[string]*Tuote{"x2": {"Mutteri", 5}}
	osoitteet["x2"].Saldo-- // osoittimen kautta muutos onnistuu
	fmt.Println(varasto["x1"], *osoitteet["x2"])
	// @loppu arvot

	// @alku ryhmittely
	tilaukset := []struct{ asiakas, tuote string }{
		{"Aino", "kahvi"}, {"Eero", "tee"}, {"Aino", "pulla"},
	}
	asiakkaittain := map[string][]string{}
	for _, t := range tilaukset {
		// nil-viipaleeseen voi lisätä, joten alustusta ei tarvita
		asiakkaittain[t.asiakas] = append(asiakkaittain[t.asiakas],
			t.tuote)
	}
	fmt.Println(asiakkaittain) // fmt tulostaa kartat avainjärjestyksessä
	// @loppu ryhmittely
}
