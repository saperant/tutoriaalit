// Jaettu laskuri kolmella tavalla. Lipulla -kilpa ajetaan
// synkronoimaton versio, jonka kilpailutilanteen go run -race löytää.
package main

import (
	"flag"
	"fmt"
	"sync"
	"sync/atomic"
)

const goroutineja, kierroksia = 8, 1000

// @alku versiot
type mutexLaskuri struct {
	mu sync.Mutex
	n  map[string]int
}

func (l *mutexLaskuri) lisaa(avain string) {
	l.mu.Lock()
	l.n[avain]++
	l.mu.Unlock()
}

func aja(f func()) {
	var wg sync.WaitGroup
	for range goroutineja {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for range kierroksia {
				f()
			}
		}()
	}
	wg.Wait()
}

// @loppu versiot

func main() {
	kilpa := flag.Bool("kilpa", false, "aja synkronoimaton versio")
	flag.Parse()

	// @alku kaytto
	if *kilpa {
		n := 0
		aja(func() { n++ }) // VÄÄRIN: datakilpailu
		fmt.Println("synkronoimaton:", n)
		return
	}
	var atominen atomic.Int64 // yksi luku: atominen operaatio riittää
	aja(func() { atominen.Add(1) })

	l := mutexLaskuri{n: map[string]int{}} // rakenne: tarvitaan lukko
	aja(func() { l.lisaa("pyynnot") })
	fmt.Println(atominen.Load(), l.n["pyynnot"])
	// @loppu kaytto
}
