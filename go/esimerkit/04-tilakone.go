// Jakaa CSV-rivin kenttiin tilakoneella. Lainausmerkeissä oleva kenttä
// saa sisältää pilkkuja, ja "" tarkoittaa lainausmerkkiä.
package main

import (
	"errors"
	"fmt"
	"strings"
)

type tila int

const (
	kentanAlku tila = iota
	tavallinen
	lainattu
	lainausLoppui
)

var errLainaus = errors.New("päättymätön lainaus")

func jaaKentat(rivi string) ([]string, error) {
	var kentat []string
	var nyk strings.Builder
	t := kentanAlku
	for _, r := range rivi {
		switch t {
		case kentanAlku, tavallinen:
			switch {
			case r == ',':
				kentat = append(kentat, nyk.String())
				nyk.Reset()
				t = kentanAlku
			case r == '"' && t == kentanAlku:
				t = lainattu
			default:
				nyk.WriteRune(r)
				t = tavallinen
			}
		case lainattu:
			if r == '"' {
				t = lainausLoppui
			} else {
				nyk.WriteRune(r)
			}
		case lainausLoppui:
			switch r {
			case '"': // "" lainauksen sisällä
				nyk.WriteRune('"')
				t = lainattu
			case ',':
				kentat = append(kentat, nyk.String())
				nyk.Reset()
				t = kentanAlku
			default:
				return nil, fmt.Errorf("merkki %q lainauksen jälkeen",
					r)
			}
		}
	}
	if t == lainattu {
		return nil, errLainaus
	}
	return append(kentat, nyk.String()), nil
}

func main() {
	for _, rivi := range []string{
		`Oulu,"Hallituskatu 7, B",90100`,
		`"Sanoi ""moi""",,loppu`,
		`"kesken,1`,
		`"a"b,2`,
	} {
		kentat, err := jaaKentat(rivi)
		if err != nil {
			fmt.Println("virhe:", err)
			continue
		}
		fmt.Printf("%d %q\n", len(kentat), kentat)
	}
}
