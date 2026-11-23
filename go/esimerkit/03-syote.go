// Lukee mittausrivejä "anturi arvo" ja tulostaa anturikohtaiset
// keskiarvot. Virheelliset rivit raportoidaan rivinumeron kanssa.
package main

import (
	"bufio"
	"fmt"
	"os"
	"slices"
	"strconv"
	"strings"
)

type tilasto struct {
	summa float64
	maara int
}

func main() {
	tilastot := map[string]*tilasto{}
	lukija := bufio.NewScanner(os.Stdin)
	rivinro := 0
	for lukija.Scan() {
		rivinro++
		rivi := strings.TrimSpace(lukija.Text())
		if rivi == "" || strings.HasPrefix(rivi, "#") {
			continue
		}
		kentat := strings.Fields(rivi)
		if len(kentat) != 2 {
			fmt.Fprintf(os.Stderr, "rivi %d: odotettiin 2 kenttää\n",
				rivinro)
			continue
		}
		arvo, err := strconv.ParseFloat(kentat[1], 64)
		if err != nil {
			fmt.Fprintf(os.Stderr, "rivi %d: %v\n", rivinro, err)
			continue
		}
		t := tilastot[kentat[0]]
		if t == nil {
			t = &tilasto{}
			tilastot[kentat[0]] = t
		}
		t.summa += arvo
		t.maara++
	}
	if err := lukija.Err(); err != nil {
		fmt.Fprintln(os.Stderr, "lukuvirhe:", err)
		os.Exit(1)
	}
	nimet := make([]string, 0, len(tilastot))
	for nimi := range tilastot {
		nimet = append(nimet, nimi)
	}
	slices.Sort(nimet)
	for _, nimi := range nimet {
		t := tilastot[nimi]
		fmt.Printf("%-8s %6.2f (%d)\n", nimi, t.summa/float64(t.maara),
			t.maara)
	}
}
