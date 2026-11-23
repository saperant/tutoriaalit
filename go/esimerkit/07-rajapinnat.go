// Pienet rajapinnat ja io.Reader/io.Writer-koostaminen.
package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"strings"
)

// @alku laskuri
// laskevaKirjoittaja kääri minkä tahansa io.Writerin ja laskee
// kirjoitetut tavut. Se on itsekin io.Writer.
type laskevaKirjoittaja struct {
	w io.Writer
	n int64
}

func (l *laskevaKirjoittaja) Write(p []byte) (int, error) {
	n, err := l.w.Write(p)
	l.n += int64(n)
	return n, err
}

// @loppu laskuri

// @alku kuluttaja
// rivimaara tarvitsee vain lukemisen, joten se pyytää io.Readerin:
// kelpaa tiedosto, verkkoyhteys, merkkijono tai pakattu virta.
func rivimaara(r io.Reader) (int, error) {
	s := bufio.NewScanner(r)
	n := 0
	for s.Scan() {
		n++
	}
	return n, s.Err()
}

// @loppu kuluttaja

func main() {
	// @alku kaytto
	n, err := rivimaara(strings.NewReader("a\nb\nc\n"))
	fmt.Println(n, err)

	lk := &laskevaKirjoittaja{w: os.Stdout}
	fmt.Fprintf(lk, "otsikko\n")
	r := io.LimitReader(strings.NewReader("abcdefgh\n"), 4)
	if _, err := io.Copy(lk, r); err != nil {
		fmt.Println("kopiointi:", err)
	}
	fmt.Println()
	fmt.Println("tavuja:", lk.n)

	var w io.Writer = lk
	if _, ok := w.(io.StringWriter); !ok { // tyyppivarmistus
		fmt.Println("ei WriteString-metodia")
	}
	// @loppu kaytto
}
