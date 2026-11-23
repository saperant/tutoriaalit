// Omat iteraattorit Go 1.23:n range-over-func-rakenteella.
package main

import (
	"bufio"
	"fmt"
	"iter"
	"maps"
	"slices"
	"strings"
)

// @alku puu
type Puu struct {
	vasen, oikea *Puu
	arvo         int
}

func (p *Puu) Lisaa(arvo int) *Puu {
	if p == nil { // metodia voi kutsua nil-osoittimella
		return &Puu{arvo: arvo}
	}
	if arvo < p.arvo {
		p.vasen = p.vasen.Lisaa(arvo)
	} else {
		p.oikea = p.oikea.Lisaa(arvo)
	}
	return p
}

// Kaikki käy puun läpi järjestyksessä. yield palauttaa false, kun
// kutsuja lopettaa silmukan (break), jolloin läpikäynti keskeytetään.
func (p *Puu) Kaikki() iter.Seq[int] {
	return func(yield func(int) bool) {
		p.kay(yield)
	}
}

func (p *Puu) kay(yield func(int) bool) bool {
	if p == nil {
		return true
	}
	return p.vasen.kay(yield) && yield(p.arvo) && p.oikea.kay(yield)
}

// @loppu puu

// @alku rivit
// Rivit palauttaa numeroidut, ei-tyhjät rivit. iter.Seq2 tuottaa
// pareja kuten range kartan yli.
func Rivit(teksti string) iter.Seq2[int, string] {
	return func(yield func(int, string) bool) {
		s := bufio.NewScanner(strings.NewReader(teksti))
		for n := 1; s.Scan(); n++ {
			if s.Text() != "" && !yield(n, s.Text()) {
				return
			}
		}
	}
}

// @loppu rivit

func main() {
	// @alku kaytto
	var juuri *Puu
	for _, n := range []int{50, 30, 70, 20, 40, 60, 80} {
		juuri = juuri.Lisaa(n)
	}
	for arvo := range juuri.Kaikki() {
		if arvo > 50 {
			break
		}
		fmt.Print(arvo, " ")
	}
	fmt.Println(slices.Collect(juuri.Kaikki()))

	for n, rivi := range Rivit("eka\n\nkolmas\nneljäs") {
		fmt.Printf("%d:%s ", n, rivi)
	}
	fmt.Println()

	ika := map[string]int{"Eero": 31, "Aino": 27}
	fmt.Println(slices.Sorted(maps.Keys(ika)))
	// @loppu kaytto
}
