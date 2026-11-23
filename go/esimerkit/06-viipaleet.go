// Viipaleen otsake, jaettu taustataulukko ja append-sudenkuoppa.
package main

import (
	"fmt"
	"slices"
)

func main() {
	// @alku otsake
	data := make([]int, 3, 5) // pituus 3, kapasiteetti 5
	fmt.Println(data, len(data), cap(data))
	osa := data[1:3] // ei kopioi: osoittaa samaan taulukkoon
	osa[0] = 7
	fmt.Println(data, osa, len(osa), cap(osa))
	// @loppu otsake

	// @alku sudenkuoppa
	pohja := []string{"a", "b", "c", "d"}
	alku := pohja[:2]           // kapasiteettia jää 2
	alku = append(alku, "UUSI") // kirjoittaa pohjan alkion päälle!
	fmt.Println(pohja, alku)

	rajattu := pohja[:2:2]                 // täysi viipalelauseke: cap 2
	rajattu = append(rajattu, "erillinen") // pakko varata uusi taulukko
	fmt.Println(pohja, rajattu)
	// @loppu sudenkuoppa

	// @alku kasvu
	var s []int // nil-viipale toimii kuten tyhjä
	edellinen := -1
	for i := range 2000 {
		s = append(s, i)
		if cap(s) != edellinen {
			fmt.Print(cap(s), " ")
			edellinen = cap(s)
		}
	}
	fmt.Println()
	// @loppu kasvu

	// @alku kopio
	alkuperainen := []int{3, 1, 2}
	kopio := slices.Clone(alkuperainen) // tai append([]int(nil), ...)
	slices.Sort(kopio)
	fmt.Println(alkuperainen, kopio, slices.Equal(alkuperainen, kopio))

	jono := []int{1, 2, 3, 4, 5}
	jono = slices.Delete(jono, 1, 3) // poistaa indeksit 1 ja 2
	jono = slices.Insert(jono, 1, 9)
	fmt.Println(jono)
	// @loppu kopio
}
