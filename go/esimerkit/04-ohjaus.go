// Ohjausrakenteet: if alustuksella, switch, for-muodot ja funktiot.
package main

import (
	"fmt"
	"os"
)

// @alku funktiot
// jaa palauttaa osamäärän ja jakojäännöksen. Nimetyt paluuarvot
// dokumentoivat merkityksen.
func jaa(jaettava, jakaja int) (osamaara, jaannos int) {
	return jaettava / jakaja, jaettava % jakaja
}

// summa on variadinen: kutsu summa(1, 2) tai summa(lista...).
func summa(luvut ...int) int {
	s := 0
	for _, n := range luvut {
		s += n
	}
	return s
}

// @loppu funktiot

// @alku switch
func luokittele(koodi int) string {
	switch {
	case koodi >= 500:
		return "palvelinvirhe"
	case koodi >= 400:
		return "asiakasvirhe"
	case koodi == 304, koodi == 204:
		return "ei sisältöä"
	default:
		return "ok"
	}
}

// @loppu switch

func main() {
	// @alku if
	if arvo, ok := os.LookupEnv("TUTORIAALI_TASO"); ok {
		fmt.Println("taso:", arvo)
	} else {
		fmt.Println("taso: oletus")
	}
	// @loppu if

	// @alku for
	for i := range 3 { // Go 1.22: kokonaisluvun yli
		fmt.Print(i, " ")
	}
	n := 27
	for n != 1 { // while-silmukka
		if n%2 == 0 {
			n /= 2
		} else {
			n = 3*n + 1
		}
	}
	fmt.Println(n)

	ruudukko := [][]string{{".", "."}, {".", "#"}, {"#", "."}}
haku:
	for y, rivi := range ruudukko {
		for x, solu := range rivi {
			if solu == "#" {
				fmt.Println("este kohdassa", x, y)
				break haku // nimetty break poistuu molemmista
			}
		}
	}
	// @loppu for

	q, r := jaa(17, 5)
	luvut := []int{4, 5, 6}
	fmt.Println(q, r, summa(1, 2), summa(luvut...))
	for _, k := range []int{200, 204, 404, 503} {
		fmt.Print(luokittele(k), "; ")
	}
	fmt.Println()
}
