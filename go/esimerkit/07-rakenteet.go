// Rakenteet, konstruktorifunktio, upotus ja tyyppivalinta.
package main

import (
	"fmt"
	"sync"
	"time"
)

// @alku konstruktori
// Tilillä on invariantti (tunnus ei ole tyhjä), joten nolla-arvo ei
// kelpaa, ja tili luodaan konstruktorifunktiolla UusiTili.
type Tili struct {
	tunnus string
	saldo  int64 // senteissä
	mu     sync.Mutex
}

func UusiTili(tunnus string) (*Tili, error) {
	if tunnus == "" {
		return nil, fmt.Errorf("tyhjä tilitunnus")
	}
	return &Tili{tunnus: tunnus}, nil
}

func (t *Tili) Talleta(sentit int64) {
	t.mu.Lock()
	defer t.mu.Unlock()
	t.saldo += sentit
}

// @loppu konstruktori

// @alku upotus
type Aikaleima struct{ Luotu, Muutettu time.Time }

func (a *Aikaleima) Kosketa(t time.Time) { a.Muutettu = t }

// Asiakirja upottaa Aikaleiman: sen kentät ja metodit näkyvät
// Asiakirjan omina. Tämä on koostamista, ei periytymistä.
type Asiakirja struct {
	Aikaleima
	Otsikko string
}

// @loppu upotus

// @alku tyyppivalinta
func kuvaa(arvo any) string {
	switch v := arvo.(type) {
	case nil:
		return "nil"
	case int, int64:
		return fmt.Sprintf("kokonaisluku %v", v)
	case string:
		return fmt.Sprintf("merkkijono, %d tavua", len(v))
	case fmt.Stringer:
		return "Stringer: " + v.String()
	case error:
		return "virhe: " + v.Error()
	default:
		return fmt.Sprintf("tuntematon %T", v)
	}
}

// @loppu tyyppivalinta

func main() {
	t, err := UusiTili("FI-1")
	if err != nil {
		fmt.Println(err)
		return
	}
	t.Talleta(1250)
	fmt.Println(t.tunnus, t.saldo)

	hetki := time.Date(2026, 11, 1, 12, 0, 0, 0, time.UTC)
	d := Asiakirja{Otsikko: "Sopimus"}
	d.Luotu = hetki
	d.Kosketa(hetki.Add(time.Hour)) // ylennetty metodi
	fmt.Println(d.Otsikko, d.Muutettu.Sub(d.Luotu))

	for _, a := range []any{42, "hei", time.Second, fmt.Errorf("x"),
		nil, 1.5} {
		fmt.Println(kuvaa(a))
	}
}
