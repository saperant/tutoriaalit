// Sanalaskuri lukee tekstiä syötteestä ja tulostaa yleisimmät sanat.
package main

import (
	"bufio"
	"cmp"
	"fmt"
	"os"
	"slices"
	"strings"
	"unicode"
)

type sanaMaara struct {
	sana  string
	maara int
}

func main() {
	maarat := make(map[string]int)
	lukija := bufio.NewScanner(os.Stdin)
	lukija.Split(bufio.ScanWords)
	for lukija.Scan() {
		sana := strings.ToLower(strings.TrimFunc(lukija.Text(),
			func(r rune) bool { return !unicode.IsLetter(r) }))
		if sana != "" {
			maarat[sana]++
		}
	}
	if err := lukija.Err(); err != nil {
		fmt.Fprintln(os.Stderr, "lukuvirhe:", err)
		os.Exit(1)
	}

	lista := make([]sanaMaara, 0, len(maarat))
	for s, m := range maarat {
		lista = append(lista, sanaMaara{s, m})
	}
	slices.SortFunc(lista, func(a, b sanaMaara) int {
		return cmp.Or(cmp.Compare(b.maara, a.maara),
			strings.Compare(a.sana, b.sana))
	})
	for _, sm := range lista[:min(5, len(lista))] {
		fmt.Printf("%-15s %d\n", sm.sana, sm.maara)
	}
}
