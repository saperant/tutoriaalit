// Arvo- ja viitesemantiikka: mikä kopioituu sijoituksessa ja kutsussa.
package main

import "fmt"

type Piste struct{ X, Y int }

// @alku vastaanottajat
// Siirra ottaa arvon: muutos kohdistuu kopioon.
func (p Piste) Siirra(dx int) Piste {
	p.X += dx
	return p
}

// SiirraPaikallaan ottaa osoittimen: muutos näkyy kutsujalle.
func (p *Piste) SiirraPaikallaan(dx int) { p.X += dx }

// @loppu vastaanottajat

func nollaa(taulukko [3]int, viipale []int, kartta map[string]int) {
	taulukko[0] = 0
	viipale[0] = 0
	kartta["a"] = 0
}

func main() {
	// @alku kopiot
	a := Piste{1, 2}
	b := a // rakenne kopioituu kokonaan
	b.X = 99
	fmt.Println(a, b)

	c := a.Siirra(10)
	a.SiirraPaikallaan(5) // Go ottaa osoitteen automaattisesti: (&a)
	fmt.Println(a, c)

	t := [3]int{1, 2, 3}        // taulukko on arvo
	v := []int{1, 2, 3}         // viipale on otsake, joka viittaa dataan
	k := map[string]int{"a": 1} // kartta on viite
	nollaa(t, v, k)
	fmt.Println(t, v, k)
	// @loppu kopiot

	// @alku osoitin
	p := &Piste{3, 4} // osoite paikalliseen on turvallinen Go:ssa
	q := p
	q.Y = 0 // sama kuin (*q).Y = 0
	fmt.Println(*p, p == q)
	// @loppu osoitin

	// @alku new
	laskuri := new(int) // *int, joka osoittaa nolla-arvoon
	*laskuri += 2
	jono := make([]int, 2, 8)      // viipale: pituus 2, kapasiteetti 8
	hinnat := make(map[string]int) // tyhjä kartta, johon voi kirjoittaa
	hinnat["kahvi"] = 350
	fmt.Println(*laskuri, len(jono), cap(jono), hinnat)
	// @loppu new
}
