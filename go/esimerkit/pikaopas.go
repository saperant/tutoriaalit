// Pikaoppaan koodi: Go:n syntaksi tiiviisti.
package main

import (
	"context"
	"errors"
	"fmt"
	"maps"
	"slices"
	"strings"
	"sync"
	"time"
)

// @alku tyypit
type Tila int

const (
	Auki Tila = iota // 0
	Kiinni
)

type Piste struct{ X, Y int } // vientinimi: iso alkukirjain

func (p Piste) Pituus2() int   { return p.X*p.X + p.Y*p.Y } // arvo
func (p *Piste) Siirra(dx int) { p.X += dx }                // osoitin

type Muoto interface{ Ala() float64 } // implisiittinen toteutus

func Kartoita[T, U any](s []T, f func(T) U) []U {
	tulos := make([]U, 0, len(s))
	for _, x := range s {
		tulos = append(tulos, f(x))
	}
	return tulos
}

// @loppu tyypit

// @alku virheet
var ErrEiLoydy = errors.New("ei löydy")

func hae(m map[string]int, k string) (int, error) {
	v, ok := m[k]
	if !ok {
		return 0, fmt.Errorf("hae %q: %w", k, ErrEiLoydy)
	}
	return v, nil
}

// @loppu virheet

func main() {
	// @alku perus
	x := 3              // lyhyt esittely, tyyppi päätellään
	var y float64 = 1.5 // eksplisiittinen tyyppi
	s := []int{3, 1, 2} // viipale
	m := map[string]int{"a": 1}
	s = append(s, 4)
	slices.Sort(s)
	if v, ok := m["a"]; ok && x > 2 {
		fmt.Println(v, y, s, len(s), cap(s) >= len(s))
	}
	for i, r := range "hä" { // indeksi tavuina, r on rune
		fmt.Print(i, string(r), " ")
	}
	fmt.Println(slices.Sorted(maps.Keys(m)))
	// @loppu perus

	// @alku kaytto
	p := Piste{3, 4}
	p.Siirra(1)
	fmt.Println(p, p.Pituus2(), Kartoita(s, func(n int) string {
		return strings.Repeat("*", n)
	}))
	if _, err := hae(m, "b"); errors.Is(err, ErrEiLoydy) {
		fmt.Println(err)
	}
	// @loppu kaytto

	// @alku rinnakkaisuus
	ctx, peru := context.WithTimeout(context.Background(), time.Second)
	defer peru()
	tulokset := make(chan int, len(s))
	var wg sync.WaitGroup
	for _, n := range s {
		wg.Add(1)
		go func() {
			defer wg.Done()
			select {
			case tulokset <- n * n:
			case <-ctx.Done():
			}
		}()
	}
	wg.Wait()
	close(tulokset)
	summa := 0
	for t := range tulokset {
		summa += t
	}
	fmt.Println(summa)
	// @loppu rinnakkaisuus
}
