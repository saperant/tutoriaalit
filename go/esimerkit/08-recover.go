// Paniikki rajalla: yksittäisen tehtävän ohjelmointivirhe muutetaan
// virheeksi, eikä koko palvelu kaadu. net/http tekee saman
// käsittelijöille.
package main

import (
	"fmt"
)

// @alku turvallinen
func turvallisesti(nimi string, tehtava func()) (err error) {
	defer func() {
		if p := recover(); p != nil {
			err = fmt.Errorf("tehtävä %s: paniikki: %v", nimi, p)
		}
	}()
	tehtava()
	return nil
}

// @loppu turvallinen

func main() {
	tehtavat := map[string]func(){
		"a-ok":      func() {},
		"b-indeksi": func() { _ = []int{1, 2}[len("abc")] },
		"c-nil": func() {
			var m map[string]int
			m["x"] = 1
		},
	}
	for _, nimi := range []string{"a-ok", "b-indeksi", "c-nil"} {
		fmt.Println(turvallisesti(nimi, tehtavat[nimi]))
	}
}
