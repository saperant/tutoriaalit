package main

import (
	"bytes"
	"flag"
	"os"
	"path/filepath"
	"testing"
)

// @alku kulta
// Kultainen tiedosto (golden file): odotettu tuloste on tiedostossa.
// Kun tuloste muuttuu tarkoituksella: go test ./cmd/kauppa -paivita
var paivita = flag.Bool("paivita", false, "päivitä kultaiset tiedostot")

func TestAja(t *testing.T) {
	syote, err := os.Open(filepath.Join("..", "..", "testdata",
		"komennot.txt"))
	if err != nil {
		t.Fatal(err)
	}
	defer syote.Close()
	var tuloste bytes.Buffer
	if err := aja(syote, &tuloste); err != nil {
		t.Fatal(err)
	}
	kulta := filepath.Join("..", "..", "testdata", "odotettu.txt")
	if *paivita {
		if err := os.WriteFile(kulta, tuloste.Bytes(), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	odotettu, err := os.ReadFile(kulta)
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(tuloste.Bytes(), odotettu) {
		t.Errorf("tuloste poikkeaa:\n%s\nodotettiin:\n%s", &tuloste,
			odotettu)
	}
}

// @loppu kulta
