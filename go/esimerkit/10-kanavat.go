// Kanavien perusteet: synkronointi, puskuri, sulkeminen ja select.
package main

import (
	"fmt"
	"time"
)

func main() {
	// @alku perus
	valmis := make(chan struct{}) // puskuroimaton: odottaa vastaanottajaa
	tulokset := make(chan int, 3) // puskuri: lähetys odottaa vain täynnä
	go func() {
		defer close(tulokset) // lähettäjä sulkee, ei vastaanottaja
		for i := 1; i <= 5; i++ {
			tulokset <- i * i
		}
	}()
	go func() {
		for t := range tulokset { // päättyy, kun kanava suljetaan
			fmt.Print(t, " ")
		}
		fmt.Println()
		close(valmis)
	}()
	<-valmis
	_, auki := <-tulokset // suljetusta kanavasta saa nolla-arvon heti
	fmt.Println("auki:", auki)
	// @loppu perus

	// @alku select
	hidas := make(chan string)
	go func() {
		time.Sleep(200 * time.Millisecond)
		hidas <- "vastaus"
	}()
	select {
	case v := <-hidas:
		fmt.Println(v)
	case <-time.After(20 * time.Millisecond):
		fmt.Println("aikakatkaisu")
	}

	tapahtumat := make(chan string, 1)
	select {
	case tapahtumat <- "tallennus": // ei tukkeudu, jos tilaa on
		fmt.Println("jonossa")
	default:
		fmt.Println("jono täynnä, pudotetaan")
	}
	// @loppu select
	// Huom: hidas-goroutine jää odottamaan ikuisesti. Ks. 10-vuoto.go.
}
