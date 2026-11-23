// Must-funktiot paniikoivat. Niitä käytetään vain alustuksessa
// vakioarvoille, jolloin virhe on ohjelmointivirhe ja näkyy heti.
package main

import (
	"fmt"
	"regexp"
)

var tunniste = regexp.MustCompile(`^[A-Z]{2}-(\d+$`) // sulku puuttuu

func main() {
	fmt.Println(tunniste.MatchString("FI-123"))
}
