// Pieni HTTP-palvelu, joka käännetään staattiseksi binääriksi ja
// ajetaan distroless-kuvassa ilman kuorta ja paketinhallintaa.
package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"
)

func main() {
	// Distroless-kuvassa ei ole curlia: binääri tarkistaa itse
	// oman terveytensä, kun se käynnistetään valitsimella -terveys.
	terveys := flag.Bool("terveys", false, "tarkista palvelun terveys")
	flag.Parse()
	if *terveys {
		asiakas := http.Client{Timeout: 2 * time.Second}
		v, err := asiakas.Get("http://127.0.0.1:8080/terveys")
		if err != nil || v.StatusCode != http.StatusOK {
			os.Exit(1)
		}
		return
	}
	versio := os.Getenv("VERSIO")
	http.HandleFunc("/terveys", func(w http.ResponseWriter, _ *http.Request) {
		fmt.Fprintln(w, "ok")
	})
	http.HandleFunc("/", func(w http.ResponseWriter, _ *http.Request) {
		fmt.Fprintf(w, "staattinen palvelu %s\n", versio)
	})
	log.Fatal(http.ListenAndServe(":8080", nil))
}
