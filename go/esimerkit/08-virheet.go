// Virheet arvoina: vartijavirheet, käärintä %w:llä, oma virhetyyppi,
// errors.Is ja errors.As sekä errors.Join.
package main

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
)

// @alku tyypit
// ErrEiLoydy on vartijavirhe (sentinel): kutsuja vertaa siihen
// errors.Is-funktiolla.
var ErrEiLoydy = errors.New("ei löydy")

// RiviVirhe kertoo, missä jäsennys epäonnistui. Kutsuja saa tiedot
// errors.As-funktiolla.
type RiviVirhe struct {
	Rivi int
	Syy  error
}

func (e *RiviVirhe) Error() string {
	return fmt.Sprintf("rivi %d: %v", e.Rivi, e.Syy)
}

// Unwrap paljastaa syyn, jotta errors.Is ja errors.As näkevät sen.
func (e *RiviVirhe) Unwrap() error { return e.Syy }

// @loppu tyypit

// @alku kerrokset
var tiedostot = map[string]string{
	"palvelu.conf": "portti=8080\nyhteydet=x10\n",
}

func lueTiedosto(nimi string) (string, error) {
	sisalto, ok := tiedostot[nimi]
	if !ok {
		return "", fmt.Errorf("tiedosto %s: %w", nimi, ErrEiLoydy)
	}
	return sisalto, nil
}

func jasenna(sisalto string) (map[string]int, error) {
	tulos := map[string]int{}
	for i, rivi := range strings.Split(strings.TrimSpace(sisalto), "\n") {
		avain, arvo, _ := strings.Cut(rivi, "=")
		n, err := strconv.Atoi(arvo)
		if err != nil {
			return nil, &RiviVirhe{Rivi: i + 1, Syy: err}
		}
		tulos[avain] = n
	}
	return tulos, nil
}

func lataaAsetukset(nimi string) (map[string]int, error) {
	sisalto, err := lueTiedosto(nimi)
	if err != nil {
		return nil, fmt.Errorf("asetusten lataus: %w", err)
	}
	asetukset, err := jasenna(sisalto)
	if err != nil {
		return nil, fmt.Errorf("asetusten lataus: %s: %w", nimi, err)
	}
	return asetukset, nil
}

// @loppu kerrokset

// @alku validointi
func validoi(portti int, nimi string) error {
	var virheet []error
	if portti < 1 || portti > 65535 {
		virheet = append(virheet, fmt.Errorf("portti %d ei kelpaa", portti))
	}
	if nimi == "" {
		virheet = append(virheet, errors.New("nimi puuttuu"))
	}
	return errors.Join(virheet...) // nil, jos lista on tyhjä
}

// @loppu validointi

func main() {
	// @alku kaytto
	for _, nimi := range []string{"puuttuu.conf", "palvelu.conf"} {
		_, err := lataaAsetukset(nimi)
		fmt.Println(err)

		var rv *RiviVirhe
		var nv *strconv.NumError
		switch {
		case errors.Is(err, ErrEiLoydy):
			fmt.Println("  -> käytetään oletuksia")
		case errors.As(err, &rv) && errors.As(err, &nv):
			fmt.Printf("  -> korjaa rivi %d, arvo %q\n", rv.Rivi,
				nv.Num)
		}
	}
	fmt.Println(validoi(70000, ""))
	fmt.Println(validoi(80, "api") == nil)
	// @loppu kaytto
}
