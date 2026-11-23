// Tuotantokelpoinen http.Server: aikakatkaisut ja hallittu sammutus,
// joka antaa käynnissä olevien pyyntöjen valmistua.
package main

import (
	"context"
	"errors"
	"fmt"
	"io"
	"net"
	"net/http"
	"time"
)

func main() {
	// @alku palvelin
	aloitettu := make(chan struct{}, 1)
	kasittelija := http.HandlerFunc(func(w http.ResponseWriter,
		r *http.Request) {
		aloitettu <- struct{}{}
		time.Sleep(100 * time.Millisecond) // hidas pyyntö
		fmt.Fprintln(w, "valmis")
	})
	srv := &http.Server{
		Handler:           kasittelija,
		ReadHeaderTimeout: 5 * time.Second, // suojaa hitailta asiakkailta
		ReadTimeout:       10 * time.Second,
		WriteTimeout:      10 * time.Second,
		IdleTimeout:       60 * time.Second,
	}
	kuuntelija, err := net.Listen("tcp", "127.0.0.1:0") // vapaa portti
	if err != nil {
		fmt.Println(err)
		return
	}
	palveluLoppui := make(chan error, 1)
	go func() { palveluLoppui <- srv.Serve(kuuntelija) }()
	// @loppu palvelin

	vastaus := make(chan string, 1)
	go func() {
		asiakas := &http.Client{Timeout: 5 * time.Second}
		r, err := asiakas.Get("http://" + kuuntelija.Addr().String())
		if err != nil {
			vastaus <- err.Error()
			return
		}
		defer r.Body.Close()
		data, _ := io.ReadAll(r.Body)
		vastaus <- fmt.Sprintf("%d %s", r.StatusCode, data)
	}()
	<-aloitettu // pyyntö on nyt käsittelyssä

	// @alku sammutus
	// Oikeassa palvelussa sammutus alkaa signaalista:
	//   ctx, stop := signal.NotifyContext(ctx, os.Interrupt,
	//       syscall.SIGTERM)
	ctx, peru := context.WithTimeout(context.Background(), 5*time.Second)
	defer peru()
	if err := srv.Shutdown(ctx); err != nil { // odottaa pyyntöjä
		fmt.Println("sammutus:", err)
	}
	err = <-palveluLoppui
	fmt.Println("Serve palautti:", errors.Is(err, http.ErrServerClosed))
	fmt.Print("asiakas sai: ", <-vastaus)
	// @loppu sammutus
}
