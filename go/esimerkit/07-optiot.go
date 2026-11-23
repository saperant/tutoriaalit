// Funktionaaliset optiot: laajennettava konstruktori ilman
// rakentajaluokkaa ja ilman pitkiä parametrilistoja.
package main

import (
	"fmt"
	"time"
)

// @alku optiot
type Asiakas struct {
	osoite       string
	aikakatkaisu time.Duration
	yritykset    int
}

type Optio func(*Asiakas)

func AikaKatkaisu(d time.Duration) Optio {
	return func(a *Asiakas) { a.aikakatkaisu = d }
}

func Yritykset(n int) Optio {
	return func(a *Asiakas) { a.yritykset = n }
}

// UusiAsiakas asettaa järkevät oletukset, ja optiot muuttavat niitä.
func UusiAsiakas(osoite string, optiot ...Optio) *Asiakas {
	a := &Asiakas{osoite: osoite, aikakatkaisu: 5 * time.Second,
		yritykset: 3}
	for _, o := range optiot {
		o(a)
	}
	return a
}

// @loppu optiot

func main() {
	// @alku kaytto
	oletus := UusiAsiakas("https://api.esimerkki.fi")
	kiireinen := UusiAsiakas("https://api.esimerkki.fi",
		AikaKatkaisu(500*time.Millisecond), Yritykset(1))
	for _, a := range []*Asiakas{oletus, kiireinen} {
		fmt.Println(a.osoite, a.aikakatkaisu, a.yritykset)
	}
	// @loppu kaytto
}
