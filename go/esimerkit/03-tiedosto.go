// Komentoriviliput ja tiedostot: flag, os ja bufio.
package main

import (
	"bufio"
	"errors"
	"flag"
	"fmt"
	"io/fs"
	"os"
	"strconv"
	"strings"
)

// @alku kirjoita
func kirjoita(polku string, arvot []float64) (err error) {
	f, err := os.Create(polku)
	if err != nil {
		return err
	}
	// Kirjoitetun tiedoston sulkeminen voi epäonnistua (levy täynnä),
	// joten sen virhe liitetään paluuarvoon.
	defer func() { err = errors.Join(err, f.Close()) }()

	w := bufio.NewWriter(f)
	for i, arvo := range arvot {
		fmt.Fprintf(w, "anturi%d %.1f\n", i+1, arvo)
	}
	return w.Flush() // palauttaa myös aiempien kirjoitusten virheen
}

// @loppu kirjoita

// @alku lue
// ylittavat palauttaa anturit, joiden lukema on vähintään raja.
func ylittavat(polku string, raja float64) ([]string, error) {
	f, err := os.Open(polku)
	if err != nil {
		return nil, err
	}
	defer f.Close()

	var osumat []string
	rivit := bufio.NewScanner(f)
	for rivit.Scan() {
		nimi, luku, _ := strings.Cut(rivit.Text(), " ")
		arvo, err := strconv.ParseFloat(luku, 64)
		if err == nil && arvo >= raja {
			osumat = append(osumat, nimi)
		}
	}
	return osumat, rivit.Err()
}

// @loppu lue

// @alku aja
func aja(polku string, raja float64) error {
	if err := kirjoita(polku, []float64{21.5, 23, 19.25}); err != nil {
		return err
	}
	sisalto, err := os.ReadFile(polku) // pieni tiedosto kerralla
	if err != nil {
		return err
	}
	fmt.Printf("%d tavua\n", len(sisalto))

	osumat, err := ylittavat(polku, raja)
	if err != nil {
		return err
	}
	fmt.Printf("vähintään %.1f: %v\n", raja, osumat)

	if err := os.Remove(polku); err != nil {
		return err
	}
	_, err = ylittavat(polku, raja) // tiedostoa ei enää ole
	fmt.Println(err)
	fmt.Println(errors.Is(err, fs.ErrNotExist))
	return nil
}

// @loppu aja

// @alku main
func main() {
	raja := flag.Float64("raja", 20, "pienin raportoitava lukema")
	flag.Parse()
	if flag.NArg() != 1 {
		fmt.Fprintln(os.Stderr, "käyttö: tiedosto [-raja N] TIEDOSTO")
		os.Exit(2)
	}
	if err := aja(flag.Arg(0), *raja); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

// @loppu main
