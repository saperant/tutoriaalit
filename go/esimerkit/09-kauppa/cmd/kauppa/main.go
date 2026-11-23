// Komento kauppa lukee varastotapahtumia syötteestä:
//
//	lisaa TUNNUS MAARA | ota TUNNUS MAARA | saldo TUNNUS | listaa
package main

import (
	"bufio"
	"errors"
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"

	"example.com/kauppa/varasto"
)

// @alku main
func main() {
	if err := aja(os.Stdin, os.Stdout); err != nil {
		fmt.Fprintln(os.Stderr, "kauppa:", err)
		os.Exit(1)
	}
}

// aja on erotettu main-funktiosta, jotta sitä voi testata ilman
// prosessia: syöte ja tuloste ovat rajapintoja.
func aja(r io.Reader, w io.Writer) error {
	var v varasto.Varasto
	s := bufio.NewScanner(r)
	for s.Scan() {
		kentat := strings.Fields(s.Text())
		if len(kentat) == 0 {
			continue
		}
		if err := suorita(&v, kentat, w); err != nil {
			fmt.Fprintf(w, "virhe: %v\n", err)
		}
	}
	return s.Err()
}

// @loppu main

var errKomento = errors.New("tuntematon komento")

func suorita(v *varasto.Varasto, k []string, w io.Writer) error {
	switch {
	case len(k) == 3 && (k[0] == "lisaa" || k[0] == "ota"):
		maara, err := strconv.Atoi(k[2])
		if err != nil {
			return err
		}
		if k[0] == "lisaa" {
			return v.Lisaa(k[1], maara)
		}
		return v.Ota(k[1], maara)
	case len(k) == 2 && k[0] == "saldo":
		saldo, err := v.Saldo(k[1])
		if err != nil {
			return err
		}
		fmt.Fprintln(w, saldo)
	case len(k) == 1 && k[0] == "listaa":
		for _, r := range v.Rivit() {
			fmt.Fprintf(w, "%-8s %5d\n", r.Tunnus, r.Saldo)
		}
	default:
		return fmt.Errorf("%q: %w", strings.Join(k, " "), errKomento)
	}
	return nil
}
