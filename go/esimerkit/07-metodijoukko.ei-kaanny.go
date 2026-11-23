package main

import "fmt"

type Kirjaaja interface{ Kirjaa(string) }

type Muistiloki struct{ rivit []string }

// Osoitinvastaanottaja: vain *Muistiloki toteuttaa Kirjaajan.
func (m *Muistiloki) Kirjaa(s string) { m.rivit = append(m.rivit, s) }

// Käännösaikainen tarkistus siitä, että tyyppi toteuttaa rajapinnan.
var _ Kirjaaja = (*Muistiloki)(nil)

func main() {
	var loki Muistiloki
	var k Kirjaaja = &loki
	k = loki // @virhe: Kirjaa-metodilla on osoitinvastaanottaja
	k.Kirjaa("käynnistyi")
	fmt.Println(loki.rivit)
}
