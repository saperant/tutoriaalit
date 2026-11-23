// Package varasto pitää kirjaa tuotteiden saldoista. Varasto on
// turvallinen käyttää useasta goroutinesta.
package varasto

// @alku tuonnit
import (
	"cmp"
	"errors"
	"fmt"
	"slices"
	"sync"

	"example.com/kauppa/internal/tunnus"
)

// @loppu tuonnit

// @alku tyyppi
// Virheet, joihin kutsuja voi verrata errors.Is-funktiolla.
var (
	ErrTuntematon   = errors.New("tuntematon tuote")
	ErrSaldoEiRiita = errors.New("saldo ei riitä")
	ErrMaara        = errors.New("määrän on oltava positiivinen")
)

// Varasto on käyttövalmis nolla-arvona.
type Varasto struct {
	mu     sync.Mutex
	saldot map[string]int
}

// @loppu tyyppi

// Rivi on yhden tuotteen saldo.
type Rivi struct {
	Tunnus string
	Saldo  int
}

// Lisaa kasvattaa tuotteen saldoa ja luo tuotteen tarvittaessa.
func (v *Varasto) Lisaa(t string, maara int) error {
	t, err := tarkista(t, maara)
	if err != nil {
		return err
	}
	v.mu.Lock()
	defer v.mu.Unlock()
	if v.saldot == nil {
		v.saldot = make(map[string]int)
	}
	v.saldot[t] += maara
	return nil
}

// @alku ota
// Ota vähentää saldoa. Saldo ei voi mennä negatiiviseksi.
func (v *Varasto) Ota(t string, maara int) error {
	t, err := tarkista(t, maara)
	if err != nil {
		return err
	}
	v.mu.Lock()
	defer v.mu.Unlock()
	saldo, ok := v.saldot[t]
	switch {
	case !ok:
		return fmt.Errorf("%s: %w", t, ErrTuntematon)
	case saldo < maara:
		return fmt.Errorf("%s: saldo %d, pyydetty %d: %w", t, saldo,
			maara, ErrSaldoEiRiita)
	}
	v.saldot[t] = saldo - maara
	return nil
}

// @loppu ota

// Saldo palauttaa tuotteen saldon.
func (v *Varasto) Saldo(t string) (int, error) {
	t, err := tunnus.Normalisoi(t)
	if err != nil {
		return 0, err
	}
	v.mu.Lock()
	defer v.mu.Unlock()
	saldo, ok := v.saldot[t]
	if !ok {
		return 0, fmt.Errorf("%s: %w", t, ErrTuntematon)
	}
	return saldo, nil
}

// Rivit palauttaa saldot tunnuksen mukaan järjestettyinä. Paluuarvo on
// kopio, joten kutsuja ei pääse käsiksi varaston sisäiseen tilaan.
func (v *Varasto) Rivit() []Rivi {
	v.mu.Lock()
	rivit := make([]Rivi, 0, len(v.saldot))
	for t, s := range v.saldot {
		rivit = append(rivit, Rivi{t, s})
	}
	v.mu.Unlock()
	slices.SortFunc(rivit, func(a, b Rivi) int {
		return cmp.Compare(a.Tunnus, b.Tunnus)
	})
	return rivit
}

func tarkista(t string, maara int) (string, error) {
	if maara <= 0 {
		return "", fmt.Errorf("%d: %w", maara, ErrMaara)
	}
	return tunnus.Normalisoi(t)
}
