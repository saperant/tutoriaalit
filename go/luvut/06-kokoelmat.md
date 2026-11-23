# Viipaleet, kartat ja merkkijonot {.runko-kokoelmat}

Go:n sisäänrakennetut kokoelmat ovat taulukko, viipale ja kartta.
Standardikirjaston `slices`- ja `maps`-paketit (Go 1.21) tarjoavat
niille geneeriset algoritmit, ja `container`-paketissa ovat keko,
lista ja rengas. Muut tietorakenteet kirjoitetaan itse tai haetaan
kirjastosta; niiden teoria on taidossa *Tietorakenteet*.

## Viipaleet

Taulukko `[N]T` on kiinteän kokoinen arvo, ja sitä käytetään harvoin
suoraan. *Viipale* `[]T` on kolmen sanan otsake: osoitin taustataulukkoon,
pituus ja kapasiteetti. Viipaleen viipalointi ei kopioi dataa:

```{.go tiedosto="esimerkit/06-viipaleet.go" osa="otsake"}
```

`append` lisää alkion. Jos kapasiteettia on jäljellä, alkio kirjoitetaan
samaan taustataulukkoon; muuten varataan uusi, suurempi taulukko ja data
kopioidaan. Tästä seuraa Go:n tunnetuin viipalesudenkuoppa: `append`
lyhyempään viipaleeseen voi kirjoittaa toisen viipaleen alkion päälle.

```{.go tiedosto="esimerkit/06-viipaleet.go" osa="sudenkuoppa"}
```

Täysi viipalelauseke `s[alku:loppu:max]` rajaa kapasiteetin, jolloin
seuraava `append` varaa aina uuden taulukon. Funktio, joka palauttaa
viipaleen sisäisestä taulukostaan, palauttaa yleensä kopion.

Kapasiteetti kasvaa pienillä viipaleilla kaksinkertaiseksi ja suurilla
noin 1,25-kertaiseksi. Siksi `s = append(s, x)` on keskimäärin vakioaikainen,
mutta tulos on aina sijoitettava takaisin:

```{.go tiedosto="esimerkit/06-viipaleet.go" osa="kasvu"}
```

`slices`-paketti kattaa tavalliset toimenpiteet:

```{.go tiedosto="esimerkit/06-viipaleet.go" osa="kopio"}
```

```{.tuloste tiedosto="esimerkit/06-viipaleet.odotettu"}
```

Nil-viipale (`var s []int`) ja tyhjä viipale (`[]int{}`) toimivat
samoin: pituus on nolla, ja niihin voi lisätä. Ero näkyy vain
vertailussa `s == nil` ja JSON-koodauksessa (`null` vai `[]`).

## Kartat

`map[K]V` on hajautustaulu. Avaimen tyypin on oltava vertailtava
(luvut, merkkijonot, osoittimet, rakenteet ja taulukot, joiden kentät
ovat vertailtavia), joten viipale ei kelpaa avaimeksi.

```{.go tiedosto="esimerkit/06-kartat.go" osa="perus"}
```

- Haku palauttaa puuttuvalle avaimelle nolla-arvon. Muoto `v, ok :=
  m[k]` erottaa puuttuvan avaimen nolla-arvosta.
- Läpikäyntijärjestys on tarkoituksella satunnainen. Järjestetty
  läpikäynti tehdään lajittelemalla avaimet:
  `slices.Sorted(maps.Keys(m))`.
- Kartta ei ole säieturvallinen. Samanaikainen kirjoitus ja luku
  kaataa ohjelman (`concurrent map writes`).

Joukko on kartta, jonka arvotyyppi on tyhjä rakenne:

```{.go tiedosto="esimerkit/06-kartat.go" osa="joukko"}
```

Kartan arvo on kopio, joten rakenne-arvon kenttää ei voi muuttaa
paikallaan. Arvo luetaan, muutetaan ja kirjoitetaan takaisin, tai
kartassa säilytetään osoittimia:

```{.go tiedosto="esimerkit/06-kartat.go" osa="arvot"}
```

```{.go tiedosto="esimerkit/06-karttakentta.ei-kaanny.go"}
```

```
cannot assign to struct field varasto["x1"].Saldo in map
```

Ryhmittely hyödyntää sitä, että nil-viipaleeseen voi lisätä:

```{.go tiedosto="esimerkit/06-kartat.go" osa="ryhmittely"}
```

```{.tuloste tiedosto="esimerkit/06-kartat.odotettu"}
```

Nil-kartasta voi lukea, mutta siihen kirjoittaminen kaatuu. Tyypillinen
virhe on rakenne, jonka karttakenttää ei ole alustettu:

```{.go tiedosto="esimerkit/06-nilkartta.kaatuu.go"}
```

```{.tuloste tiedosto="esimerkit/06-nilkartta.virhe"}
```

## Merkkijonot

Merkkijono on muuttumaton tavujono. `len` palauttaa tavujen määrän,
ja indeksointi palauttaa tavun. Lähdekoodi on UTF-8:aa, joten
merkkijonoliteraalit ovat UTF-8:aa, mutta merkkijono voi sisältää
mielivaltaisia tavuja. `range` purkaa UTF-8:n ja antaa jokaisen merkin
(`rune`) alkukohdan tavuina:

```{.go tiedosto="esimerkit/06-merkkijonot.go" osa="tavut"}
```

`strings`-paketti sisältää tavalliset toimenpiteet. `strings.Cut`
(Go 1.18) korvaa monta `Index`- ja viipalointikutsua:

```{.go tiedosto="esimerkit/06-merkkijonot.go" osa="paketti"}
```

Merkkijono kootaan `strings.Builder`-tyypillä, joka toteuttaa
`io.Writer`-rajapinnan:

```{.go tiedosto="esimerkit/06-merkkijonot.go" osa="builder"}
```

Virheellinen UTF-8 ei kaada mitään, vaan `range` ja `[]rune` antavat
korvausmerkin U+FFFD:

```{.go tiedosto="esimerkit/06-merkkijonot.go" osa="virheellinen"}
```

```{.tuloste tiedosto="esimerkit/06-merkkijonot.odotettu"}
```

Muunnokset `[]byte(s)` ja `string(b)` kopioivat datan, koska merkkijono
on muuttumaton. `bytes`-paketissa on samat funktiot tavuviipaleille,
joten I/O-koodi voi pysyä tavuissa ilman muunnoksia.

## Iteraattorit

Go 1.23 toi omat iteraattorit: funktio, jonka tyyppi on
`func(yield func(T) bool)` (`iter.Seq[T]`), kelpaa `range`-lauseeseen.
Silmukan runko on `yield`-funktio, ja `break` näkyy iteraattorille
`yield`-kutsun palauttamana `false`-arvona:

```{.go tiedosto="esimerkit/06-iteraattorit.go" osa="puu"}
```

```{.go tiedosto="esimerkit/06-iteraattorit.go" osa="rivit"}
```

```{.go tiedosto="esimerkit/06-iteraattorit.go" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-iteraattorit.odotettu"}
```

Iteraattori kätkee tietorakenteen sisäisen muodon ja laskee alkiot
vasta tarvittaessa. `slices.Collect`, `slices.Sorted`, `maps.Keys` ja
`maps.Values` muuntavat iteraattoreita ja kokoelmia toisikseen.

## Algoritmit

Lajittelu tehdään `slices.Sort`- tai `slices.SortFunc`-funktiolla.
Vertailufunktio palauttaa negatiivisen, nollan tai positiivisen luvun,
ja `cmp.Or` ketjuttaa avaimet. `SortFunc` ei ole vakaa;
`SortStableFunc` säilyttää yhtä suurten alkioiden järjestyksen.

```{.go tiedosto="esimerkit/06-algoritmit.go" osa="lajittelu"}
```

```{.go tiedosto="esimerkit/06-algoritmit.go" osa="haku"}
```

Prioriteettijono tehdään `container/heap`-paketilla. Tyyppi toteuttaa
viisi metodia, ja paketti ylläpitää kekoehtoa:

```{.go tiedosto="esimerkit/06-algoritmit.go" osa="keko"}
```

```{.go tiedosto="esimerkit/06-algoritmit.go" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-algoritmit.odotettu"}
```

| Toiminto | Funktio | Aikavaativuus |
|----------|---------|---------------|
| Lajittelu | `slices.Sort`, `SortFunc` (pdqsort) | $O(n \log n)$ |
| Vakaa lajittelu | `slices.SortStableFunc` | $O(n \log n)$ |
| Binäärihaku | `slices.BinarySearch` | $O(\log n)$ |
| Lineaarinen haku | `slices.Index`, `Contains`, `IndexFunc` | $O(n)$ |
| Kopio, vertailu | `slices.Clone`, `Equal` | $O(n)$ |
| Peräkkäiset kaksoiskappaleet pois | `slices.Compact` | $O(n)$ |
| Ääriarvot | `min`, `max` (1.21), `slices.Max` | $O(n)$ |
| Prioriteettijono | `container/heap` | $O(\log n)$ |

## Käytännössä

- **Esivaraa kapasiteetti**, kun alkioiden määrä tiedetään:
  `make([]T, 0, n)`. Älä käytä `make([]T, n)` ja `append`-kutsua
  yhdessä, sillä tulos alkaa `n` nolla-arvolla.
- **Palauta kopio sisäisestä viipaleesta**, jos kutsuja ei saa muuttaa
  olion tilaa. Ota vastaan viipale ja tallenna se vain, jos dokumentoit
  omistuksen siirtyvän.
- **Kartan läpikäynnin järjestykseen ei saa luottaa.** Järjestä avaimet
  tulostusta, testejä ja toistettavia tiedostoja varten.
- **`map[K]struct{}` joukoksi**, `map[K]bool` vain, jos arvon `false`
  merkitys on tarpeen.
- **Säieturvallisuus:** suojaa jaettu kartta lukolla. `sync.Map` sopii
  vain erityistapauksiin (avaimet kirjoitetaan kerran ja luetaan
  paljon).
- **Merkkijonojen kokoaminen** `strings.Builder`-tyypillä tai
  `strings.Join`-funktiolla, ei `+=`-operaattorilla silmukassa.
- **Unicode:** pituus merkkeinä on `utf8.RuneCountInString`, ei `len`.
  Kirjainkoosta riippumaton vertailu on `strings.EqualFold`.
- **Hinta.** Kartan haku on hajautuksen ja vertailun hinta, noin
  kymmeniä nanosekunteja; pieni viipale ja lineaarinen haku voi olla
  nopeampi alle muutaman kymmenen alkion joukolle. Rajapintatyypin
  (`any`) alkiot maksavat allokaation ja epäsuoruuden, joten geneerinen
  `[]T` on parempi kuin `[]any`.

## Itsearviointi

- Osaat selittää viipaleen otsakkeen, pituuden ja kapasiteetin ja
  välttää `append`-sudenkuopan täydellä viipalelausekkeella tai kopiolla.
- Osaat käyttää karttoja, erottaa puuttuvan avaimen nolla-arvosta ja
  käydä kartan läpi järjestyksessä.
- Osaat käsitellä merkkijonoja tavuina ja Unicode-merkkeinä ja koota
  niitä tehokkaasti.
- Osaat kirjoittaa oman iteraattorin `iter.Seq`-tyypillä.
- Osaat lajitella monella avaimella `slices.SortFunc`- ja
  `cmp.Or`-funktioilla ja käyttää `container/heap`-pakettia.
