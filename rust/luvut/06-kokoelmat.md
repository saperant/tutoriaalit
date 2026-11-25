# Kokoelmat, merkkijonot ja iteraattorit {.runko-kokoelmat}

Standardikirjaston kokoelmat ovat `std::collections`-modulissa, ja ne
kaikki toimivat iteraattoreiden kanssa. Iteraattorit ovat Rustin
tärkein abstraktio datan käsittelyyn: ne korvaavat indeksisilmukat ja
kääntyvät yhtä tehokkaaksi koodiksi. Luku esittelee ensin kokoelmat ja
sulkeumat, joita iteraattorien metodit käyttävät, ja sitten
iteraattorit, hajautustaulun ja merkkijonot.

## Kokoelmat

| Kokoelma | Käyttö | Vastine C++:ssa |
|---------------------|---------------------------|----------------------|
| `Vec<T>` | oletuskokoelma: kasvava taulukko | `std::vector` |
| `VecDeque<T>` | jono, lisäys ja poisto molemmista päistä | `std::deque` |
| `HashMap<K, V>`, `HashSet<T>` | hajautustaulu, järjestys satunnainen | `unordered_map`, `unordered_set` |
| `BTreeMap<K, V>`, `BTreeSet<T>` | järjestetty, välihaut | `std::map`, `std::set` |
| `BinaryHeap<T>` | prioriteettijono (suurin ensin) | `priority_queue` |
| `LinkedList<T>` | harvoin tarpeen | `std::list` |

`Vec` on oikea valinta lähes aina. Muihin siirrytään, kun tarvitaan
haku avaimella, järjestys tai jonon molemmat päät. Kokoelmien yleiset
ominaisuudet käsitellään taitopuun taidoissa *Tietorakenteet* ja
*Algoritmit*; tässä luvussa keskitytään Rustin rajapintoihin.

## Sulkeumat

Kokoelmien ja iteraattorien metodit ottavat parametrikseen *sulkeumia*.
Sulkeuma (*closure*) `|x| lauseke` on nimetön funktio, joka voi siepata
ympäristönsä muuttujia. Kääntäjä valitsee sieppaustavan sen mukaan,
mitä sulkeuma muuttujalla tekee, ja sieppaus noudattaa luvun 5
lainaussääntöjä. Sulkeuman tyyppi toteuttaa yhden tai useamman
kolmesta piirteestä:

| Piirre | Sulkeuma | Sieppaus | Kutsut |
|--------|----------|----------|--------|
| `Fn` | vain lukee | jaettu lainaus | monta, myös rinnakkain |
| `FnMut` | muuttaa siepattua arvoa | muokkaava lainaus | monta, yksi kerrallaan |
| `FnOnce` | luovuttaa siepatun arvon | siirto | yksi |

Funktio, joka ottaa sulkeuman parametrina, valitsee piirteistä
väljimmän, joka sille riittää. `move`-sana siirtää siepatut arvot
sulkeuman omistukseen. Sitä tarvitaan, kun sulkeuma elää luontipaikkaansa
pidempään: paluuarvona tai toisessa säikeessä (luku 11).

```{.rust tiedosto="esimerkit/06-sulkeumat.rs" osa="parametri"}
```

```{.rust tiedosto="esimerkit/06-sulkeumat.rs" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/06-sulkeumat.odotettu"}
```

Jokaisella sulkeumalla on oma nimetön tyyppinsä, joten kaksi samalta
näyttävää sulkeumaa ovat eri tyyppiä. Sulkeuma, joka ei sieppaa mitään,
kelpaa myös funktio-osoittimeksi (luku 4).

## Iteraattorit

Iteraattori on mikä tahansa tyyppi, joka toteuttaa piirteen `Iterator`
ja sen metodin `next(&mut self) -> Option<Self::Item>`. Kokoelmasta saa
kolme iteraattoria:

| Kutsu | Alkion tyyppi | Kokoelma |
|---------------------------------|--------------|----------------------|
| `v.iter()` tai `for x in &v` | `&T` | lainataan |
| `v.iter_mut()` tai `for x in &mut v` | `&mut T` | lainataan muokattavaksi |
| `v.into_iter()` tai `for x in v` | `T` | kulutetaan |

*Sovittimet* (*adapters*), kuten `map`, `filter`, `enumerate`, `zip`,
`take` ja `skip`, tuottavat uuden iteraattorin. *Kuluttajat*, kuten
`collect`, `sum`, `count`, `fold`, `find`, `any` ja `max_by_key`,
käyvät iteraattorin läpi:

```{.rust tiedosto="esimerkit/06-iteraattorit.rs" osa="ketju"}
```

```{.rust tiedosto="esimerkit/06-iteraattorit.rs" osa="koosteet"}
```

```{.tuloste tiedosto="esimerkit/06-iteraattorit.odotettu" rivit="1-2"}
```

`collect` rakentaa minkä tahansa kokoelman, joka toteuttaa
`FromIterator`-piirteen. Kohdetyyppi annetaan muuttujan tyyppinä tai
*turbokalamuodossa* `collect::<Vec<_>>()`.

Viipaleilla on lisäksi ikkunoita ja paloja käsittelevät iteraattorit:

```{.rust tiedosto="esimerkit/06-iteraattorit.rs" osa="ikkunat"}
```

```{.tuloste tiedosto="esimerkit/06-iteraattorit.odotettu" rivit="3-4"}
```

Iteraattorit ovat *laiskoja*: sovittimet eivät tee mitään ennen kuin
kuluttaja pyytää alkioita. Siksi päättymätön lukuväli `1..` on
käyttökelpoinen, kun `find` lopettaa ensimmäiseen osumaan:

```{.rust tiedosto="esimerkit/06-iteraattorit.rs" osa="laiska"}
```

```{.tuloste tiedosto="esimerkit/06-iteraattorit.odotettu" rivit="5-5"}
```

## Hajautustaulu ja entry-rajapinta

`HashMap` ja `BTreeMap` tarjoavat `entry`-rajapinnan, jolla haku ja
lisäys tehdään yhdellä haulla. C++:n `operator[]`, joka lisää
oletusarvon huomaamatta, puuttuu tarkoituksella:

```{.rust tiedosto="esimerkit/06-sanakirjat.rs" osa="entry"}
```

`BTreeMap` pitää avaimet järjestyksessä ja tukee välihakuja:

```{.rust tiedosto="esimerkit/06-sanakirjat.rs" osa="btree"}
```

```{.rust tiedosto="esimerkit/06-sanakirjat.rs" osa="joukko"}
```

```{.tuloste tiedosto="esimerkit/06-sanakirjat.odotettu"}
```

`HashMap` käyttää oletuksena SipHash-tiivistettä, joka kestää
palvelunestohyökkäykset, joissa hyökkääjä tuottaa törmääviä avaimia.
Se on hitaampi kuin C++-toteutusten tiivisteet. Sisäisellä datalla
tiivisteen voi vaihtaa nopeampaan (esim. `rustc-hash`- tai
`ahash`-kirjasto).

## Merkkijonot

Rustissa on kaksi merkkijonotyyppiä: omistava, kasvava `String` ja
lainattu viipale `&str`. Molemmat ovat aina kelvollista UTF-8:aa, ja
pituus on tavuina. Merkkijonoa ei voi indeksoida, koska tavuindeksi voi
osua merkin keskelle ja merkki-indeksi olisi lineaarinen operaatio:

```{.rust tiedosto="esimerkit/06-indeksi.ei-kaanny.rs"}
```

```
error[E0277]: the type `str` cannot be indexed by `{integer}`
```

Merkkeihin päästään iteraattoreilla `chars()` ja `bytes()`. Viipale
tavuvälistä (`&s[a..b]`) aiheuttaa paniikin, jos raja ei osu merkin
rajalle; `get(a..b)` palauttaa silloin `None`:

```{.rust tiedosto="esimerkit/06-merkkijonot.rs" osa="utf8"}
```

```{.rust tiedosto="esimerkit/06-merkkijonot.rs" osa="muokkaus"}
```

Jäsennyksessä käytetään viipaleita palauttavia metodeja `split`,
`split_once`, `trim` ja `lines`, jotka eivät kopioi dataa, sekä
`parse`-metodia. Kun `Result`-arvoja tuottava iteraattori kerätään
tyyppiin `Result<Vec<T>, E>`, tulos on ensimmäinen virhe tai kaikki
arvot:

```{.rust tiedosto="esimerkit/06-merkkijonot.rs" osa="jasennys"}
```

```{.tuloste tiedosto="esimerkit/06-merkkijonot.odotettu"}
```

Muut merkkijonotyypit liittyvät rajapintoihin: `OsString` ja `Path`
käyttöjärjestelmän nimille, jotka eivät välttämättä ole UTF-8:aa, sekä
`CString` ja `CStr` C-rajapinnoille (luku 12).

## Käytännössä

- **Iteraattori ennen indeksisilmukkaa.** `for x in &v` ja
  iteraattoriketjut eivät tarvitse rajatarkistuksia, ilmaisevat
  aikomuksen ja toimivat kaikille kokoelmille. Indeksi on oikea
  valinta, kun algoritmi todella käsittelee indeksejä (esim. kahden
  osoittimen menetelmä).
- **Iteraattorit ovat nollakustanteisia.** `filter().map().sum()`
  kääntyy yhdeksi silmukaksi ilman välitaulukoita. `collect()`
  välivaiheena sen sijaan varaa muistia: kerää vasta lopuksi.
- **Varaa kapasiteetti.** Kun koko tiedetään, `Vec::with_capacity(n)`
  ja `String::with_capacity(n)` välttävät uudelleenvaraukset. `collect`
  tekee tämän itse, kun iteraattori tietää kokonsa.
- **`&str` parametrina, `String` kenttänä.** Älä tee merkkijonoja
  `to_string()`-kutsuilla vain välittääksesi niitä. `format!` varaa
  aina; kirjoita usean osan tulosteet suoraan `write!`-makrolla.
- **`HashMap`-järjestys on satunnainen.** Tulosteet ja testit, joiden on
  oltava toistettavia, lajittelevat tai käyttävät `BTreeMap`-tyyppiä.
- **`sort_unstable` ellei vakautta tarvita.** Se ei varaa muistia ja on
  nopeampi. `sort_by_key` laskee avaimen jokaisessa vertailussa; kallis
  avain lasketaan kerran `sort_by_cached_key`-metodilla.
- **Merkkijonon indeksi on tavuindeksi.** `find` palauttaa tavuindeksin,
  joka kelpaa viipalointiin. Käyttäjälle näkyvien merkkien laskemiseen
  `chars().count()` ei riitä kaikille kielille (yhdistelmämerkit);
  siihen tarvitaan grafeemirajat (`unicode-segmentation`-kirjasto).

## Itsearviointi

- Osaat valita kokoelman käyttötarpeen mukaan ja perustella, miksi
  `Vec` on oletus.
- Osaat kirjoittaa iteraattoriketjun, jossa on sovittimia ja
  kuluttaja, ja kertoa, milloin muistia varataan.
- Osaat erottaa `iter`-, `iter_mut`- ja `into_iter`-metodit ja niiden
  alkioiden tyypit.
- Osaat kirjoittaa funktion, joka ottaa tai palauttaa sulkeuman, ja
  valita rajaksi `Fn`-, `FnMut`- tai `FnOnce`-piirteen.
- Osaat käyttää `entry`-rajapintaa laskentaan ja ryhmittelyyn.
- Osaat käsitellä UTF-8-merkkijonoja ilman indeksointia ja selittää
  `String`- ja `&str`-tyyppien eron.
