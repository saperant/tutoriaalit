# Iteraattorit ja generaattorit {.runko-kokoelmat}

Iterointi on Pythonin keskeinen abstraktio. `for`-silmukka,
koostelausekkeet, `sum`, `sorted`, `zip`, purku `a, b = pari` ja
`in`-operaattori toimivat kaikille olioille, jotka toteuttavat
iteraattoriprotokollan. Generaattorit tekevät iteraattorien
kirjoittamisesta helppoa, ja niillä rakennetaan laiskoja putkia, jotka
käsittelevät mielivaltaisen suuren datan vakiomuistissa.

## Iteraattoriprotokolla

Protokollassa on kaksi roolia:

- *Iteroitava* (*iterable*) on olio, jonka `__iter__`-metodi palauttaa
  uuden iteraattorin. Lista, merkkijono, sanakirja ja tiedosto ovat
  iteroitavia.
- *Iteraattori* on olio, jonka `__next__` palauttaa seuraavan alkion
  tai nostaa `StopIteration`-poikkeuksen. Iteraattorin `__iter__`
  palauttaa iteraattorin itsensä.

`for x in olio` tekee saman kuin `it = iter(olio)` ja toistuvat
`next(it)`-kutsut, kunnes `StopIteration` lopettaa silmukan. Oma
iteroitava luokka tarvitsee vain `__iter__`-metodin:

```{.python tiedosto="esimerkit/06-protokolla.py" osa="luokka"}
```

Ero iteroitavan ja iteraattorin välillä on käytännössä tärkeä:

```{.python tiedosto="esimerkit/06-protokolla.py" osa="kertakaytto"}
```

```{.tuloste tiedosto="esimerkit/06-protokolla.odotettu"}
```

`Sivutus`-olion voi käydä läpi monta kertaa, koska jokainen
`__iter__`-kutsu luo uuden iteraattorin. Iteraattori sen sijaan kuluu:
toinen `list(iteraattori)` palauttaa tyhjän listan eikä nosta virhettä.
Sama koskee generaattoreita, `map`- ja `filter`-olioita, `zip`-olioita
ja avattua tiedostoa. Jos funktio käy syötteensä läpi kahdesti, sen on
otettava `Sequence` tai muutettava syöte listaksi, ei `Iterable`.

## Generaattorit

Funktio, jossa on `yield`, on *generaattorifunktio*. Kutsu ei suorita
koodia vaan palauttaa generaattorin. Jokainen `next` suorittaa
funktiota seuraavaan `yield`-lauseeseen asti ja jäädyttää sen tilan
paikallisine muuttujineen. Kun funktio palaa, generaattori nostaa
`StopIteration`-poikkeuksen.

*Generaattorilauseke* `(p for p in pyynnot if p.tila >= 500)` on
koostelausekkeen laiska versio: se tuottaa alkion kerrallaan eikä
rakenna listaa. `yield from` delegoi toiselle iteroitavalle.

Generaattoreista rakennetaan *putki*, jossa jokainen vaihe on oma
funktionsa. Esimerkki suodattaa palvelimen lokista hitaat
virhepyynnöt:

```{.python tiedosto="esimerkit/06-loki.py" osa="putki"}
```

```{.python tiedosto="esimerkit/06-loki.py" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-loki.syote"}
```

```{.tuloste tiedosto="esimerkit/06-loki.odotettu"}
```

```{.dot otsikko="Laiska putki: pyynnöt (`next()`) kulkevat kuluttajalta lähteelle ja alkiot yksi kerrallaan takaisin."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.3;
  syote [label="sys.stdin", shape=plain, style=""];
  j [label="jasenna"]; v [label="virheelliset"]; h [label="hitaat"];
  f [label="for", shape=plain, style=""];
  syote -> j [label="rivi"];
  j -> v [label="Pyynto"];
  v -> h [label="Pyynto"];
  h -> f [label="Pyynto"];
  f -> h [label="next()", style=dashed, constraint=false];
  h -> v [label="next()", style=dashed, constraint=false];
  v -> j [label="next()", style=dashed, constraint=false];
  j -> syote [label="next()", style=dashed, constraint=false];
}
```

Putki on laiska: `jasenna` lukee seuraavan rivin vasta, kun `virheelliset`
pyytää seuraavaa pyyntöä, ja niin edelleen. Muistissa on kerrallaan vain
yksi rivi, joten sama koodi käsittelee kilotavun ja sata gigatavua.
Vaiheet ovat erikseen testattavia, ja niitä voi yhdistellä eri
järjestyksissä. Parametrien tyyppi `Iterable` ja paluutyyppi
`Iterator` dokumentoivat sopimuksen: vaihe ottaa minkä tahansa
iteroitavan ja käy sen läpi kerran.

Rikkinäinen rivi ohitetaan tässä hiljaa. Tuotantokoodissa ohitetut
rivit laskettaisiin tai lokitettaisiin (luku 13), ja virheellinen
luku nostaisi `ValueError`-poikkeuksen rivinumeron kanssa.

## itertools

`itertools` sisältää valmiita, C:llä toteutettuja iteraattorirakenteita.
Ne ovat nopeita ja laiskoja:

```{.python tiedosto="esimerkit/06-itertools.py" osa="itertools"}
```

| Funktio | Tehtävä |
|---------|---------|
| `batched(it, n)` | erät, esim. tietokantaan kirjoitus 1000 rivin erissä (3.12) |
| `pairwise(it)` | peräkkäiset parit: muutokset, välit |
| `accumulate(it)` | juokseva summa tai muu kertymä |
| `groupby(it, key)` | *peräkkäiset* samanavaimiset alkiot ryhmiksi |
| `chain.from_iterable(its)` | sarjojen ketjutus |
| `islice(it, n)` | n ensimmäistä alkiota mistä tahansa iteraattorista |
| `count`, `cycle`, `repeat` | äärettömät sarjat |
| `product`, `permutations`, `combinations` | kombinatoriikka |
| `tee(it, n)` | yhden iteraattorin haarautus (puskuroi) |

`groupby` yhdistää vain peräkkäiset alkiot, joten syöte lajitellaan
ensin samalla avaimella, jos ryhmien halutaan olevan täydellisiä.
Kaikkien ryhmien kerääminen on yleensä selkeämpää `defaultdict`-tyypillä
(luku 5).

Generaattori voi olla ääretön, koska arvot lasketaan vasta
pyydettäessä. Kuluttaja päättää, montako se ottaa:

```{.python tiedosto="esimerkit/06-itertools.py" osa="aareton"}
```

```{.tuloste tiedosto="esimerkit/06-itertools.odotettu"}
```

## Generaattorin elinkaari

Generaattori pitää kehyksensä elossa, kunnes se on käyty loppuun tai
roskienkeruu poistaa sen. Kesken jäänyt generaattori suljetaan
`close()`-kutsulla, joka nostaa sen sisällä `GeneratorExit`-poikkeuksen,
jolloin `finally`-lohkot ajetaan. Generaattoria, joka pitää resurssia
(avattua tiedostoa), ei pidä jättää roikkumaan; resurssi avataan
kutsujan `with`-lohkossa ja generaattori saa vain iteroitavan.

Generaattorilla on myös `send`- ja `throw`-metodit, joilla sille voi
lähettää arvoja. Ne olivat ennen `async`/`await`-syntaksia korutiinien
toteutustapa. Uudessa koodissa niitä tarvitaan harvoin; poikkeus on
`contextlib.contextmanager` (luku 7), joka rakentuu niiden päälle.

## Käytännössä

- **Generaattoriputki** (*pipeline*) virtaavalle datalle: jokainen
  vaihe on pieni funktio `Iterable` sisään, `Iterator` ulos. Malli
  vastaa Unixin putkia ja C++:n rangeja. Muisti pysyy vakiona.
- **Laiska oletuksena, lista kun tarvitaan.** Generaattori, kun dataa
  käydään läpi kerran; lista, kun tarvitaan pituus, indeksointi tai
  monta läpikäyntiä. Koostelauseke listan rakentamiseen,
  generaattorilauseke funktion argumenttina: `sum(x.summa for x in rivit)`.
- **Käytä `itertools`-moduulia ennen omaa silmukkaa.** Valmis funktio
  on testattu, nopea ja kertoo nimellään, mitä tehdään.
- **Iteroitava rajapinnassa.** Funktio, joka ottaa `Iterable`-tyypin,
  kelpuuttaa listan, generaattorin, tiedoston ja tietokantakursorin.
  Sopimus on, että sitä käydään läpi kerran.
- **Hinta:** generaattorin jokainen alkio maksaa kehyksen
  jatkamisen, mikä on hieman kalliimpaa kuin listan läpikäynti. Hyöty on
  muistissa ja siinä, että käsittely alkaa ennen kuin kaikki data on
  luettu. Pieniä kokoelmia käsiteltäessä ero on merkityksetön.
- **Sudenkuopat:** iteraattorin kuluminen (toinen läpikäynti on hiljaa
  tyhjä), `groupby` lajittelemattomalle syötteelle ja laiskuuden
  viivästämät poikkeukset: virhe nousee vasta, kun putkea kulutetaan,
  ei kun se rakennetaan.

## Itsearviointi

- Osaat selittää iteroitavan ja iteraattorin eron ja kertoa, miksi
  generaattorin toinen läpikäynti on tyhjä.
- Osaat toteuttaa oman iteroitavan luokan `__iter__`-metodilla.
- Osaat rakentaa laiskan generaattoriputken ja tyypittää sen vaiheet
  `Iterable`- ja `Iterator`-tyypeillä.
- Osaat käyttää `itertools`-funktioita `batched`, `pairwise`,
  `accumulate`, `groupby` ja `islice` ja tiedät `groupby`-ansan.
- Osaat valita generaattorin ja listan välillä muistin ja
  läpikäyntikertojen perusteella.
