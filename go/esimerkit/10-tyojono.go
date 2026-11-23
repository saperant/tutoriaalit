// Työntekijäallas (worker pool): kiinteä määrä goroutineja käsittelee
// jonon tehtäviä. Rinnakkaisuus on rajattu, ja tulokset kootaan.
package main

import (
	"fmt"
	"hash/crc32"
	"slices"
	"strings"
	"sync"
)

type tehtava struct {
	id   int
	data string
}

type tulos struct {
	id       int
	tarkiste uint32
}

// @alku allas
func kasittele(tehtavat []tehtava, tyontekijoita int) []tulos {
	jono := make(chan tehtava)
	tulokset := make(chan tulos)

	var wg sync.WaitGroup
	for range tyontekijoita {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for t := range jono {
				summa := crc32.ChecksumIEEE([]byte(t.data))
				tulokset <- tulos{t.id, summa}
			}
		}()
	}
	// Syöttäjä ja sulkija omissa goroutineissaan, jotta pääfunktio
	// voi kerätä tuloksia samaan aikaan.
	go func() {
		for _, t := range tehtavat {
			jono <- t
		}
		close(jono)
	}()
	go func() {
		wg.Wait()
		close(tulokset)
	}()

	var kaikki []tulos
	for t := range tulokset {
		kaikki = append(kaikki, t)
	}
	// Valmistumisjärjestys vaihtelee; järjestetään tunnisteen mukaan.
	slices.SortFunc(kaikki, func(a, b tulos) int { return a.id - b.id })
	return kaikki
}

// @loppu allas

func main() {
	var tehtavat []tehtava
	for i := range 6 {
		tehtavat = append(tehtavat,
			tehtava{i, strings.Repeat(fmt.Sprint(i), 1000)})
	}
	for _, t := range kasittele(tehtavat, 3) {
		fmt.Printf("%d %08x\n", t.id, t.tarkiste)
	}
}
