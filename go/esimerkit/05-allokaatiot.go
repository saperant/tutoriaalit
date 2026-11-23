// Allokaatioiden mittaaminen testing.AllocsPerRun-funktiolla.
// Sama mittari näkyy testeissä: go test -bench . -benchmem.
package main

import (
	"fmt"
	"strconv"
	"strings"
	"testing"
)

type Piste struct{ X, Y float64 }

// @alku pako
//
//go:noinline
func uusiArvo(x, y float64) Piste { return Piste{x, y} }

//go:noinline
func uusiOsoitin(x, y float64) *Piste { return &Piste{x, y} } // pakenee

// @loppu pako

// @alku kokoelmat
func kasvattaen(n int) []int {
	var s []int
	for i := range n {
		s = append(s, i)
	}
	return s
}

func varaten(n int) []int {
	s := make([]int, 0, n) // kapasiteetti tiedetään etukäteen
	for i := range n {
		s = append(s, i)
	}
	return s
}

func yhdistaPlus(osat []string) string {
	s := ""
	for _, o := range osat {
		s += o // jokainen += luo uuden merkkijonon
	}
	return s
}

func yhdistaBuilder(osat []string) string {
	var b strings.Builder
	n := 0
	for _, o := range osat {
		n += len(o)
	}
	b.Grow(n)
	for _, o := range osat {
		b.WriteString(o)
	}
	return b.String()
}

// @loppu kokoelmat

// Tulokset sijoitetaan pakettitason muuttujiin, jotta kääntäjä ei
// poista laskentaa.
var (
	nieluF float64
	nieluN int
)

func main() {
	osat := make([]string, 100)
	for i := range osat {
		osat[i] = strconv.Itoa(i)
	}
	mittaa := func(nimi string, f func()) {
		fmt.Printf("%-16s %5.0f allokaatiota\n", nimi,
			testing.AllocsPerRun(100, f))
	}
	mittaa("arvo", func() { p := uusiArvo(1, 2); nieluF = p.X })
	mittaa("osoitin", func() { nieluF = uusiOsoitin(1, 2).X })
	mittaa("append kasvaen", func() { nieluN = len(kasvattaen(1000)) })
	mittaa("append varaten", func() { nieluN = len(varaten(1000)) })
	mittaa("merkkijono +=", func() { nieluN = len(yhdistaPlus(osat)) })
	mittaa("strings.Builder", func() {
		nieluN = len(yhdistaBuilder(osat))
	})
}
