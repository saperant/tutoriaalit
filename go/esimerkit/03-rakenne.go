// Rakenteen ja metodin määrittely lyhyesti.
package main

import "fmt"

// @alku rakenne
// Mittaus kokoaa yhteen kuuluvat kentät yhdeksi tyypiksi.
type Mittaus struct {
	Anturi string
	Arvo   float64
}

// String on metodi: funktio, jolla on vastaanottaja (m Mittaus).
func (m Mittaus) String() string {
	return fmt.Sprintf("%s=%.1f", m.Anturi, m.Arvo)
}

// @loppu rakenne

func main() {
	// @alku kaytto
	m := Mittaus{Anturi: "ulko", Arvo: -3.5} // koosteliteraali
	var tyhja Mittaus                        // kentillä nolla-arvot
	m.Arvo += 1.5
	fmt.Println(m.String(), m.Anturi, tyhja.Arvo)
	fmt.Println(m) // fmt kutsuu String-metodia itse
	// @loppu kaytto
}
