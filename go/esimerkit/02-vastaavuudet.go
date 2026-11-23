// Go:n perusrakenteet rinnakkain: monta paluuarvoa, virhe arvona,
// rakenne metodeineen ja implisiittisesti toteutettu rajapinta.
package main

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
)

// @alku virhe
// jasennaPari jäsentää muodon "avain=luku". Virhe on tavallinen
// paluuarvo, ei poikkeus.
func jasennaPari(s string) (string, int, error) {
	avain, arvo, ok := strings.Cut(s, "=")
	if !ok {
		return "", 0, errors.New("puuttuva '='")
	}
	n, err := strconv.Atoi(arvo)
	if err != nil {
		return "", 0, fmt.Errorf("avain %q: %w", avain, err)
	}
	return avain, n, nil
}

// @loppu virhe

// @alku rajapinta
type Muoto interface {
	Ala() float64
}

type Suorakaide struct{ Leveys, Korkeus float64 }

// Suorakaide toteuttaa Muodon pelkästään määrittelemällä metodin.
func (s Suorakaide) Ala() float64 { return s.Leveys * s.Korkeus }

// @loppu rajapinta

func main() {
	// @alku kaytto
	for _, syote := range []string{"portti=8080", "aikakatkaisu",
		"yrityksia=kolme"} {
		avain, n, err := jasennaPari(syote)
		if err != nil {
			fmt.Println("virhe:", err)
			continue
		}
		fmt.Println(avain, "->", n)
	}

	var m Muoto = Suorakaide{Leveys: 3, Korkeus: 4}
	fmt.Printf("%T %v %.1f\n", m, m, m.Ala())
	// @loppu kaytto
}
