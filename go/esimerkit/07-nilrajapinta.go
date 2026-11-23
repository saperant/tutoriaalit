// Sudenkuoppa: nil-osoitin rajapinnan sisällä ei ole nil-rajapinta.
package main

import (
	"errors"
	"fmt"
)

type ValidointiVirhe struct{ Kentta string }

func (v *ValidointiVirhe) Error() string { return "virheellinen " + v.Kentta }

// @alku vaarin
func validoiVaarin(nimi string) error {
	var v *ValidointiVirhe // nil-osoitin
	if nimi == "" {
		v = &ValidointiVirhe{"nimi"}
	}
	return v // VÄÄRIN: palauttaa rajapinnan (tyyppi *ValidointiVirhe, nil)
}

// @loppu vaarin

// @alku oikein
func validoi(nimi string) error {
	if nimi == "" {
		return &ValidointiVirhe{"nimi"}
	}
	return nil // oikein: palauta nil suoraan
}

// @loppu oikein

func main() {
	// @alku kaytto
	err := validoiVaarin("Aino")
	fmt.Println(err == nil, fmt.Sprintf("%T", err))
	err = validoi("Aino")
	fmt.Println(err == nil)

	var vv *ValidointiVirhe
	err = validoi("")
	fmt.Println(errors.As(err, &vv), vv.Kentta)
	// @loppu kaytto
}
