// Geneeriset funktiot ja tyypit: rajoitteet ja ~-tyyppijoukot.
package main

import (
	"cmp"
	"errors"
	"fmt"
	"slices"
)

// @alku funktiot
// Suodata ja Muunna toimivat minkä tahansa alkiotyypin kanssa.
func Suodata[T any](s []T, ehto func(T) bool) []T {
	var tulos []T
	for _, x := range s {
		if ehto(x) {
			tulos = append(tulos, x)
		}
	}
	return tulos
}

func Muunna[T, U any](s []T, f func(T) U) []U {
	tulos := make([]U, len(s))
	for i, x := range s {
		tulos[i] = f(x)
	}
	return tulos
}

// Luku-rajoite: ~ hyväksyy myös tyypit, joiden pohjatyyppi on int tai
// float64, kuten Sentit alla.
type Luku interface {
	~int | ~int64 | ~float64
}

func Summa[T Luku](s []T) T {
	var tulos T
	for _, x := range s {
		tulos += x
	}
	return tulos
}

type Sentit int64

// @loppu funktiot

// @alku tyyppi
// Pino on geneerinen tyyppi. Nolla-arvo on tyhjä, käyttövalmis pino.
type Pino[T any] struct{ alkiot []T }

var ErrTyhja = errors.New("pino on tyhjä")

func (p *Pino[T]) Lisaa(x T) { p.alkiot = append(p.alkiot, x) }

func (p *Pino[T]) Ota() (T, error) {
	var nolla T
	if len(p.alkiot) == 0 {
		return nolla, ErrTyhja
	}
	x := p.alkiot[len(p.alkiot)-1]
	p.alkiot = p.alkiot[:len(p.alkiot)-1]
	return x, nil
}

// SuurinAvain vaatii järjestettävän avaimen: cmp.Ordered.
func SuurinAvain[K cmp.Ordered, V any](m map[K]V) (K, bool) {
	var suurin K
	loytyi := false
	for k := range m {
		if !loytyi || k > suurin {
			suurin, loytyi = k, true
		}
	}
	return suurin, loytyi
}

// @loppu tyyppi

func main() {
	luvut := []int{3, 8, 1, 9, 4}
	parilliset := Suodata(luvut, func(n int) bool { return n%2 == 0 })
	tekstit := Muunna(luvut, func(n int) string {
		return fmt.Sprint(n * n)
	})
	fmt.Println(parilliset, tekstit, Summa(luvut))
	fmt.Println(Summa([]Sentit{150, 275}), Summa([]float64{0.5, 0.25}))

	var p Pino[string]
	p.Lisaa("a")
	p.Lisaa("b")
	x, _ := p.Ota()
	_, _ = p.Ota()
	_, err := p.Ota()
	fmt.Println(x, err)

	k, ok := SuurinAvain(map[string]int{"b": 1, "c": 2, "a": 3})
	fmt.Println(k, ok, slices.Max(luvut))
}
