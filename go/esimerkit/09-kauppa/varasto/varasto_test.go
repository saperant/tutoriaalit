// Ulkoinen testipaketti varasto_test käyttää vain julkista rajapintaa,
// kuten oikea kutsuja.
package varasto_test

import (
	"errors"
	"fmt"
	"sync"
	"testing"

	"example.com/kauppa/varasto"
)

// @alku apu
// uusiVarasto on testiapuri. t.Helper() saa virheilmoituksen
// osoittamaan kutsujan riviä.
func uusiVarasto(t *testing.T, saldot map[string]int) *varasto.Varasto {
	t.Helper()
	v := &varasto.Varasto{}
	for tunnus, maara := range saldot {
		if err := v.Lisaa(tunnus, maara); err != nil {
			t.Fatalf("Lisaa(%q, %d): %v", tunnus, maara, err)
		}
	}
	return v
}

// @loppu apu

// @alku ota
func TestOta(t *testing.T) {
	tapaukset := []struct {
		nimi      string
		tunnus    string
		maara     int
		virhe     error // nil = onnistuu
		uusiSaldo int
	}{
		{"osa saldosta", "FI-1", 3, nil, 7},
		{"koko saldo", "fi-1", 10, nil, 0},
		{"liikaa", "FI-1", 11, varasto.ErrSaldoEiRiita, 10},
		{"tuntematon", "SE-1", 1, varasto.ErrTuntematon, 10},
		{"nolla", "FI-1", 0, varasto.ErrMaara, 10},
	}
	for _, tc := range tapaukset {
		t.Run(tc.nimi, func(t *testing.T) {
			t.Parallel() // jokaisella alitestillä oma varasto
			v := uusiVarasto(t, map[string]int{"FI-1": 10})
			err := v.Ota(tc.tunnus, tc.maara)
			if !errors.Is(err, tc.virhe) {
				t.Fatalf("Ota() virhe = %v, odotettiin %v", err,
					tc.virhe)
			}
			if saldo, _ := v.Saldo("FI-1"); saldo != tc.uusiSaldo {
				t.Errorf("saldo = %d, odotettiin %d", saldo,
					tc.uusiSaldo)
			}
		})
	}
}

// @loppu ota

// @alku rinnakkain
// TestRinnakkain on hyödyllinen vain kilpailutilanteiden tunnistimen
// kanssa: go test -race.
func TestRinnakkain(t *testing.T) {
	v := uusiVarasto(t, map[string]int{"FI-1": 1000})
	var wg sync.WaitGroup
	for range 10 {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for range 50 {
				_ = v.Ota("FI-1", 1)
				_ = v.Lisaa("SE-2", 1)
			}
		}()
	}
	wg.Wait()
	a, _ := v.Saldo("FI-1")
	b, _ := v.Saldo("SE-2")
	if a != 500 || b != 500 {
		t.Errorf("saldot %d ja %d, odotettiin 500 ja 500", a, b)
	}
}

// @loppu rinnakkain

// @alku esimerkki
// Esimerkkifunktio on sekä dokumentaatiota (go doc) että testi:
// go test vertaa tulostetta Output-kommenttiin.
func ExampleVarasto() {
	var v varasto.Varasto
	_ = v.Lisaa("fi-7", 5)
	_ = v.Lisaa("AA-1", 2)
	err := v.Ota("FI-7", 9)
	fmt.Println(err)
	fmt.Println(v.Rivit())
	// Output:
	// FI-7: saldo 5, pyydetty 9: saldo ei riitä
	// [{AA-1 2} {FI-7 5}]
}

// @loppu esimerkki

// @alku vertailu
func BenchmarkLisaa(b *testing.B) {
	var v varasto.Varasto
	b.ReportAllocs()
	for range b.N {
		if err := v.Lisaa("FI-1", 1); err != nil {
			b.Fatal(err)
		}
	}
}

// @loppu vertailu
