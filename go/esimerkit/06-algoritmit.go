// Standardikirjaston algoritmit: lajittelu, haku ja prioriteettijono.
package main

import (
	"cmp"
	"container/heap"
	"fmt"
	"slices"
	"strings"
)

type Tapahtuma struct {
	Aika         int
	Kuvaus       string
	Prioriteetti int
}

// @alku keko
// tapahtumaJono toteuttaa heap.Interface-rajapinnan. Pienin aika
// ensin.
type tapahtumaJono []Tapahtuma

func (j tapahtumaJono) Len() int           { return len(j) }
func (j tapahtumaJono) Less(a, b int) bool { return j[a].Aika < j[b].Aika }
func (j tapahtumaJono) Swap(a, b int)      { j[a], j[b] = j[b], j[a] }
func (j *tapahtumaJono) Push(x any)        { *j = append(*j, x.(Tapahtuma)) }
func (j *tapahtumaJono) Pop() any {
	vanha := *j
	t := vanha[len(vanha)-1]
	*j = vanha[:len(vanha)-1]
	return t
}

// @loppu keko

func main() {
	tapahtumat := []Tapahtuma{
		{30, "varmuuskopio", 2}, {10, "käynnistys", 1},
		{20, "raportti", 2}, {10, "tarkistus", 3},
	}

	// @alku lajittelu
	// Ensisijaisesti prioriteetin, toissijaisesti ajan mukaan.
	jarjestetty := slices.Clone(tapahtumat)
	slices.SortFunc(jarjestetty, func(a, b Tapahtuma) int {
		return cmp.Or(cmp.Compare(a.Prioriteetti, b.Prioriteetti),
			cmp.Compare(a.Aika, b.Aika))
	})
	for _, t := range jarjestetty {
		fmt.Print(t.Kuvaus, " ")
	}
	fmt.Println()

	// Vakaa lajittelu säilyttää yhtä suurten alkuperäisen järjestyksen.
	slices.SortStableFunc(jarjestetty, func(a, b Tapahtuma) int {
		return cmp.Compare(a.Aika, b.Aika)
	})
	fmt.Println(jarjestetty[0].Kuvaus, jarjestetty[1].Kuvaus)
	// @loppu lajittelu

	// @alku haku
	ajat := []int{5, 10, 20, 40, 80}
	i, loytyi := slices.BinarySearch(ajat, 25)
	fmt.Println(i, loytyi, slices.Index(ajat, 40),
		slices.Contains(ajat, 7), slices.Max(ajat), min(3, 1, 2))
	j := slices.IndexFunc(tapahtumat, func(t Tapahtuma) bool {
		return strings.HasPrefix(t.Kuvaus, "rap")
	})
	fmt.Println(j)
	// @loppu haku

	// @alku kaytto
	jono := &tapahtumaJono{}
	for _, t := range tapahtumat {
		heap.Push(jono, t)
	}
	heap.Push(jono, Tapahtuma{15, "hälytys", 0})
	for jono.Len() > 0 {
		t := heap.Pop(jono).(Tapahtuma)
		fmt.Printf("%d %s; ", t.Aika, t.Kuvaus)
	}
	fmt.Println()
	// @loppu kaytto
}
