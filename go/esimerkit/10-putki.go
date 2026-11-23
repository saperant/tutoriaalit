// Putki (pipeline) ja ryhmän peruutus: ensimmäinen virhe peruu muut
// vaiheet contextin kautta, eikä yksikään goroutine jää roikkumaan.
package main

import (
	"context"
	"errors"
	"fmt"
	"strconv"
	"sync"
)

// @alku vaiheet
// tuota lähettää rivit kanavaan, kunnes ne loppuvat tai ctx perutaan.
func tuota(ctx context.Context, rivit []string) <-chan string {
	ulos := make(chan string)
	go func() {
		defer close(ulos)
		for _, r := range rivit {
			select {
			case ulos <- r:
			case <-ctx.Done():
				return
			}
		}
	}()
	return ulos
}

// jasenna muuntaa rivit luvuiksi. Virhe ilmoitetaan funktiolla
// epaonnistui, joka peruu koko putken.
func jasenna(ctx context.Context, sisaan <-chan string,
	epaonnistui func(error)) <-chan int {
	ulos := make(chan int)
	go func() {
		defer close(ulos)
		for r := range sisaan {
			n, err := strconv.Atoi(r)
			if err != nil {
				epaonnistui(fmt.Errorf("jäsennys: %w", err))
				return
			}
			select {
			case ulos <- n:
			case <-ctx.Done():
				return
			}
		}
	}()
	return ulos
}

// @loppu vaiheet

// @alku ryhma
func summaa(rivit []string) (int, error) {
	ctx, peru := context.WithCancelCause(context.Background())
	defer peru(nil)
	var kerran sync.Once
	epaonnistui := func(err error) {
		kerran.Do(func() { peru(err) }) // vain ensimmäinen virhe
	}

	summa := 0
	for n := range jasenna(ctx, tuota(ctx, rivit), epaonnistui) {
		summa += n
	}
	if err := context.Cause(ctx); err != nil {
		return 0, err
	}
	return summa, nil
}

// @loppu ryhma

func main() {
	fmt.Println(summaa([]string{"1", "2", "3", "4"}))
	_, err := summaa([]string{"1", "kaksi", "3"})
	var nv *strconv.NumError
	fmt.Println(err, errors.As(err, &nv))
}
