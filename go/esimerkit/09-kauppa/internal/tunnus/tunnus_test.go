package tunnus

import (
	"errors"
	"testing"
)

// @alku taulukko
func TestNormalisoi(t *testing.T) {
	tapaukset := []struct {
		nimi, syote, odotettu string
		virhe                 bool
	}{
		{"kelvollinen", "FI-123", "FI-123", false},
		{"pienet kirjaimet", " se-9 ", "SE-9", false},
		{"ei viivaa", "FI123", "", true},
		{"liian pitkä", "FI-1234567", "", true},
		{"kirjain numerossa", "FI-12a", "", true},
		{"ääkkönen", "ÄÖ-1", "", true},
	}
	for _, tc := range tapaukset {
		t.Run(tc.nimi, func(t *testing.T) {
			saatu, err := Normalisoi(tc.syote)
			if tc.virhe {
				if !errors.Is(err, ErrMuoto) {
					t.Fatalf("virhe = %v, odotettiin ErrMuoto",
						err)
				}
				return
			}
			if err != nil || saatu != tc.odotettu {
				t.Errorf("Normalisoi(%q) = %q, %v; odotettiin %q",
					tc.syote, saatu, err, tc.odotettu)
			}
		})
	}
}

// @loppu taulukko

// @alku fuzz
// FuzzNormalisoi tarkistaa ominaisuuden: kelvollinen tulos on jo
// normalisoitu. go test ajaa siemenet; go test -fuzz=. generoi uusia.
func FuzzNormalisoi(f *testing.F) {
	for _, s := range []string{"FI-1", " ab-12 ", "-", "ÄÄ-1"} {
		f.Add(s)
	}
	f.Fuzz(func(t *testing.T, s string) {
		tulos, err := Normalisoi(s)
		if err != nil {
			return
		}
		uudelleen, err := Normalisoi(tulos)
		if err != nil || uudelleen != tulos {
			t.Errorf("Normalisoi(%q) = %q, toisella kerralla %q, %v",
				s, tulos, uudelleen, err)
		}
	})
}

// @loppu fuzz
