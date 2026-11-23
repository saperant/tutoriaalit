// fmt-paketin muotoilukoodit ja Stringer-rajapinta.
package main

import (
	"fmt"
	"os"
	"strconv"
)

type Lampotila float64

// String tekee tyypistä fmt.Stringer-rajapinnan toteuttajan.
func (l Lampotila) String() string {
	return fmt.Sprintf("%.1f °C", float64(l))
}

type Mittaus struct {
	Anturi string
	Arvo   Lampotila
	Paikka []string
}

func main() {
	// @alku verbit
	m := Mittaus{"ulko-1", 21.37, []string{"piha", "pohjoinen"}}
	fmt.Printf("%v\n%+v\n", m, m)
	fmt.Printf("%#v\n", m.Paikka)
	fmt.Printf("%T | %q | %x | %08.3f | %6d|%-6d|\n",
		m.Arvo, m.Anturi, 255, 3.14159, 42, 42)
	// @loppu verbit

	// @alku strconv
	s := strconv.Itoa(1234) + strconv.FormatFloat(0.5, 'f', 2, 64)
	n, err := strconv.ParseInt("ff", 16, 64)
	fmt.Println(s, n, err)
	_, err = strconv.Atoi("12a")
	fmt.Println(err)
	// @loppu strconv

	// @alku stderr
	fmt.Fprintf(os.Stdout, "%s: %v\n", "valmis", true)
	// @loppu stderr
}
