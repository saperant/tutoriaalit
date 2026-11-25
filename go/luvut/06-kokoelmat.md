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

```{.tuloste tiedosto="esimerkit/06-viipaleet.odotettu" rivit="1-2"}
```

```{.dot otsikko="Viipale on otsake, joka osoittaa taustataulukkoon. `data` ja `osa` jakavat saman taulukon: `osa` alkaa indeksistä 1, joten sen kapasiteetti on neljä. Sijoitus `osa[0] = 7` näkyy siksi myös `data`-viipaleessa. Harmaat alkiot ovat kapasiteettia pituuden takana."}
digraph {
  rankdir=TB; nodesep=0.7; ranksep=0.6;
  node [shape=plain, style=""];
  d [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>data</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus 3</td><td port="c" bgcolor="#EEF1F6">kapasiteetti 5</td></tr></table>>];
  o [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>osa = data[1:3]</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus 2</td><td port="c" bgcolor="#EEF1F6">kapasiteetti 4</td></tr></table>>];
  t [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td port="c0" bgcolor="#FFFFFF" width="34">0</td><td port="c1" bgcolor="#FFFFFF" width="34">7</td><td port="c2" bgcolor="#FFFFFF" width="34">0</td><td port="c3" bgcolor="#E5E7EB" width="34">0</td><td port="c4" bgcolor="#E5E7EB" width="34">0</td></tr>
    <tr><td border="0"><font point-size="8">0</font></td><td border="0"><font point-size="8">1</font></td><td border="0"><font point-size="8">2</font></td><td border="0"><font point-size="8">3</font></td><td border="0"><font point-size="8">4</font></td></tr>
    <tr><td border="0" align="left" colspan="5"><i>taustataulukko [5]int</i></td></tr></table>>];
  d:p:s -> t:c0:n;
  o:p:s -> t:c1:n;
}
```

`append` lisää alkion. Jos kapasiteettia on jäljellä, alkio kirjoitetaan
samaan taustataulukkoon; muuten varataan uusi, suurempi taulukko ja data
kopioidaan. Tästä seuraa Go:n tunnetuin viipalesudenkuoppa: `append`
lyhyempään viipaleeseen voi kirjoittaa toisen viipaleen alkion päälle.

```{.go tiedosto="esimerkit/06-viipaleet.go" osa="sudenkuoppa"}
```

```{.tuloste tiedosto="esimerkit/06-viipaleet.odotettu" rivit="3-4"}
```

```{.dot otsikko="`append`-sudenkuoppa: `alku := pohja[:2]` on pituudeltaan kaksi, mutta sen kapasiteetti ulottuu taulukon loppuun. `append(alku, \"UUSI\")` mahtuu, joten se kirjoittaa samaan taulukkoon alkion `c` päälle, ja muutos näkyy `pohja`-viipaleessa."}
digraph {
  rankdir=TB; nodesep=0.7; ranksep=0.6;
  node [shape=plain, style=""];
  p [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>pohja</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus 4</td><td port="c" bgcolor="#EEF1F6">kapasiteetti 4</td></tr></table>>];
  a [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>alku (append-kutsun jälkeen)</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus 3</td><td port="c" bgcolor="#EEF1F6">kapasiteetti 4</td></tr></table>>];
  ta [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td port="c0" bgcolor="#FFFFFF" width="40">a</td><td port="c1" bgcolor="#FFFFFF" width="40">b</td><td port="c2" bgcolor="#F8D7DA" width="40">UUSI</td><td port="c3" bgcolor="#FFFFFF" width="40">d</td></tr>
    <tr><td border="0"><font point-size="8">0</font></td><td border="0"><font point-size="8">1</font></td><td border="0"><font point-size="8">2</font></td><td border="0"><font point-size="8">3</font></td></tr>
    <tr><td border="0" align="left" colspan="4"><i>yhteinen taustataulukko</i></td></tr></table>>];
  p:p:s -> ta:c0:n;
  a:p:s -> ta:c0:n;
}
```

```{.dot otsikko="Täysi viipalelauseke `pohja[:2:2]` rajaa kapasiteetin kahteen. `append(rajattu, \"erillinen\")` ei mahdu, joten se varaa uuden taulukon ja kopioi alkiot sinne. `pohja` ja sen taulukko eivät muutu."}
digraph {
  rankdir=TB; nodesep=0.7; ranksep=0.6;
  node [shape=plain, style=""];
  p [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>pohja</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus 4</td><td port="c" bgcolor="#EEF1F6">kapasiteetti 4</td></tr></table>>];
  r [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td border="0" align="left" colspan="3"><i>rajattu (append-kutsun jälkeen)</i></td></tr>
    <tr><td port="p" bgcolor="#EEF1F6">osoitin</td><td port="l" bgcolor="#EEF1F6">pituus 3</td><td port="c" bgcolor="#EEF1F6">kapasiteetti 4</td></tr></table>>];
  tc [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td port="c0" bgcolor="#FFFFFF" width="40">a</td><td port="c1" bgcolor="#FFFFFF" width="40">b</td><td port="c2" bgcolor="#FFFFFF" width="40">UUSI</td><td port="c3" bgcolor="#FFFFFF" width="40">d</td></tr>
    <tr><td border="0"><font point-size="8">0</font></td><td border="0"><font point-size="8">1</font></td><td border="0"><font point-size="8">2</font></td><td border="0"><font point-size="8">3</font></td></tr>
    <tr><td border="0" align="left" colspan="4"><i>pohjan taustataulukko</i></td></tr></table>>];
  tb [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="5">
    <tr><td port="c0" bgcolor="#FFFFFF" width="48">a</td><td port="c1" bgcolor="#FFFFFF" width="48">b</td><td port="c2" bgcolor="#FFFFFF" width="48">erillinen</td><td port="c3" bgcolor="#E5E7EB" width="48"> </td></tr>
    <tr><td border="0"><font point-size="8">0</font></td><td border="0"><font point-size="8">1</font></td><td border="0"><font point-size="8">2</font></td><td border="0"><font point-size="8">3</font></td></tr>
    <tr><td border="0" align="left" colspan="4"><i>uusi taulukko</i></td></tr></table>>];
  p:p:s -> tc:c0:n;
  r:p:s -> tb:c0:n;
}
```

Täysi viipalelauseke `s[alku:loppu:max]` rajaa kapasiteetin, jolloin
seuraava `append` varaa aina uuden taulukon. Funktio, joka palauttaa
viipaleen sisäisestä taulukostaan, palauttaa yleensä kopion.

Kapasiteetti kasvaa pienillä viipaleilla kaksinkertaiseksi ja suurilla
noin 1,25-kertaiseksi. Siksi `s = append(s, x)` on keskimäärin vakioaikainen,
mutta tulos on aina sijoitettava takaisin:

```{.go tiedosto="esimerkit/06-viipaleet.go" osa="kasvu"}
```

```{.tuloste tiedosto="esimerkit/06-viipaleet.odotettu" rivit="5-5"}
```

`slices`-paketti kattaa tavalliset toimenpiteet:

```{.go tiedosto="esimerkit/06-viipaleet.go" osa="kopio"}
```

```{.tuloste tiedosto="esimerkit/06-viipaleet.odotettu" rivit="6-7"}
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
Hakasulkeissa oleva `T` on tyyppiparametri: sama määrittely toimii
mille tahansa alkiotyypille (luku 7).
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

- **`make([]T, n)` ja `append` eivät kuulu yhteen.** Esivaraus
  (luku 5) kirjoitetaan `make([]T, 0, n)`. `make([]T, n)` luo `n`
  nolla-arvoa, ja `append` lisää uudet alkiot niiden perään.
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
