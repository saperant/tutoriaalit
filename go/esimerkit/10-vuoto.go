// Goroutine-vuoto ja sen korjaus: lähettäjä ei saa jäädä odottamaan
// vastaanottajaa, joka on jo luopunut.
package main

import (
	"context"
	"errors"
	"fmt"
	"runtime"
	"time"
)

func hidasHaku() int {
	time.Sleep(30 * time.Millisecond)
	return 42
}

// @alku vuotava
func hae(ctx context.Context) (int, error) {
	tulos := make(chan int) // VÄÄRIN: puskuroimaton
	go func() {
		tulos <- hidasHaku() // jää jumiin, jos kukaan ei vastaanota
	}()
	select {
	case v := <-tulos:
		return v, nil
	case <-ctx.Done():
		return 0, ctx.Err()
	}
}

// @loppu vuotava

// @alku korjattu
func haeKorjattu(ctx context.Context) (int, error) {
	tulos := make(chan int, 1) // lähetys onnistuu aina
	go func() {
		tulos <- hidasHaku()
	}()
	select {
	case v := <-tulos:
		return v, nil
	case <-ctx.Done():
		return 0, ctx.Err()
	}
}

// @loppu korjattu

func kokeile(nimi string, f func(context.Context) (int, error)) {
	alussa := runtime.NumGoroutine()
	for range 5 {
		ctx, peru := context.WithTimeout(context.Background(),
			time.Millisecond)
		_, err := f(ctx)
		peru() // vapauttaa ajastimen; kutsu aina, mieluiten deferillä
		if !errors.Is(err, context.DeadlineExceeded) {
			fmt.Println("odottamaton:", err)
		}
	}
	time.Sleep(300 * time.Millisecond) // hidasHaku-kutsut valmistuvat
	fmt.Printf("%s: goroutineja jäi %d\n", nimi,
		runtime.NumGoroutine()-alussa)
}

func main() {
	kokeile("vuotava", hae)
	kokeile("korjattu", haeKorjattu)
}
