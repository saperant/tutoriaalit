// Package tunnus validoi tuotetunnukset. Paketti on internal-hakemiston
// alla, joten vain tämän moduulin paketit voivat tuoda sen.
package tunnus

import (
	"errors"
	"fmt"
	"strings"
)

// ErrMuoto palautetaan, kun tunnus ei ole muotoa AA-1234.
var ErrMuoto = errors.New("tunnuksen muoto on AA-1234")

// Normalisoi poistaa ympäröivät välilyönnit, muuttaa kirjaimet
// isoiksi ja tarkistaa muodon: kaksi kirjainta, viiva ja 1-6 numeroa.
func Normalisoi(s string) (string, error) {
	t := strings.ToUpper(strings.TrimSpace(s))
	etu, numerot, ok := strings.Cut(t, "-")
	if !ok || len(etu) != 2 || len(numerot) < 1 || len(numerot) > 6 {
		return "", fmt.Errorf("%q: %w", s, ErrMuoto)
	}
	for _, r := range etu {
		if r < 'A' || r > 'Z' {
			return "", fmt.Errorf("%q: %w", s, ErrMuoto)
		}
	}
	for _, r := range numerot {
		if r < '0' || r > '9' {
			return "", fmt.Errorf("%q: %w", s, ErrMuoto)
		}
	}
	return t, nil
}
