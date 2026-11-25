// Aikaraja ja jaksollinen työ: time.Timer ja time.Ticker.
package main

import (
	"errors"
	"fmt"
	"time"
)

var errAikaraja = errors.New("aikaraja ylittyi")

// @alku aikaraja
// odota palauttaa kanavan arvon tai virheen, jos arvoa ei tule ajoissa.
func odota(tulokset <-chan string, raja time.Duration) (string, error) {
	ajastin := time.NewTimer(raja)
	defer ajastin.Stop()
	select {
	case tulos := <-tulokset:
		return tulos, nil
	case <-ajastin.C:
		return "", errAikaraja
	}
}

// @loppu aikaraja

// @alku jakso
// kysele kutsuu funktiota valmis jakson välein, kunnes se palauttaa
// true tai yrityksiä on tehty enimmäismäärä.
func kysele(valmis func() bool, jakso time.Duration, enintaan int) int {
	tikitin := time.NewTicker(jakso)
	defer tikitin.Stop() // muuten tikitin jää käyntiin
	for yritys := 1; yritys <= enintaan; yritys++ {
		<-tikitin.C
		if valmis() {
			return yritys
		}
	}
	return -1
}

// @loppu jakso

func main() {
	// @alku kaytto
	nopea := make(chan string, 1)
	nopea <- "tulos"
	tulos, err := odota(nopea, time.Second)
	fmt.Printf("%q %v\n", tulos, err)

	hidas := make(chan string) // kukaan ei lähetä
	tulos, err = odota(hidas, 20*time.Millisecond)
	fmt.Printf("%q %v\n", tulos, err)

	kyselyja := 0
	valmis := func() bool { kyselyja++; return kyselyja == 3 }
	fmt.Println("valmis yrityksellä", kysele(valmis, 5*time.Millisecond, 10))
	// @loppu kaytto
}
