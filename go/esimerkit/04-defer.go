// defer: siivous, suoritusjärjestys ja Close-virheen talteenotto.
package main

import (
	"errors"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
)

// @alku tallenna
// tallenna kirjoittaa tiedoston. Close voi epäonnistua kirjoituksen
// jälkeen (esim. täysi levy), joten sen virhe kerätään nimettyyn
// paluuarvoon.
func tallenna(polku string, data []byte) (err error) {
	f, err := os.Create(polku)
	if err != nil {
		return err
	}
	defer func() {
		err = errors.Join(err, f.Close())
	}()
	_, err = f.Write(data)
	return err
}

// @loppu tallenna

// @alku jarjestys
func jarjestys() {
	for i := range 3 {
		defer fmt.Println("defer", i) // argumentit lasketaan heti
	}
	fmt.Println("funktion runko")
}

// @loppu jarjestys

func main() {
	jarjestys()
	polku := filepath.Join(os.TempDir(), "go-tutoriaali-defer.txt")
	defer os.Remove(polku)
	if err := tallenna(polku, []byte("data\n")); err != nil {
		fmt.Println("virhe:", err)
		return
	}
	sisalto, err := os.ReadFile(polku)
	fmt.Printf("%q %v\n", sisalto, err)
	err = tallenna(filepath.Join(os.TempDir(), "ei-hakemistoa", "x"), nil)
	fmt.Println("puuttuva hakemisto:", errors.Is(err, fs.ErrNotExist))
}
