package main

import "fmt"

type Laskuri struct {
	maarat map[string]int // nolla-arvo on nil-kartta
}

func (l *Laskuri) Lisaa(avain string) { l.maarat[avain]++ }

func main() {
	var l Laskuri
	fmt.Println(l.maarat["a"]) // nil-kartasta lukeminen on sallittua
	l.Lisaa("a")               // kirjoittaminen kaatuu
}
