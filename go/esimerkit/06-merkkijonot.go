// Merkkijonot ovat muuttumattomia tavujonoja, yleensä UTF-8:aa.
package main

import (
	"fmt"
	"strings"
	"unicode/utf8"
)

func main() {
	// @alku tavut
	s := "Äänekoski"
	fmt.Println(len(s), utf8.RuneCountInString(s)) // tavut ja merkit
	fmt.Printf("%x %q\n", s[0], s[:2])             // tavu ja 2 tavua
	for i, r := range s[:5] {                      // range purkaa UTF-8:n
		fmt.Printf("%d:%c ", i, r)
	}
	fmt.Println()
	merkit := []rune(s)
	fmt.Println(string(merkit[:3]), strings.ToUpper(s[2:]))
	// @loppu tavut

	// @alku paketti
	rivi := "  GET /api/tilaukset?raja=10 HTTP/1.1 "
	metodi, loput, _ := strings.Cut(strings.TrimSpace(rivi), " ")
	polku, _, _ := strings.Cut(loput, " ")
	polku, kysely, _ := strings.Cut(polku, "?")
	fmt.Println(metodi, polku, kysely,
		strings.HasPrefix(polku, "/api/"),
		strings.Split(strings.Trim(polku, "/"), "/"))
	fmt.Println(strings.EqualFold("Go", "GO"),
		strings.Join([]string{"a", "b"}, ", "),
		strings.Count("banaani", "a"),
		strings.LastIndex("a.b.c", "."))
	// @loppu paketti

	// @alku builder
	var b strings.Builder
	for i := range 3 {
		fmt.Fprintf(&b, "rivi %d;", i) // Builder on io.Writer
	}
	fmt.Println(b.String(), b.Len())
	// @loppu builder

	// @alku virheellinen
	rikki := string([]byte{0x66, 0xff, 0x6f})
	fmt.Println(utf8.ValidString(rikki), []rune(rikki),
		strings.ToValidUTF8(rikki, "?"))
	// @loppu virheellinen
}
