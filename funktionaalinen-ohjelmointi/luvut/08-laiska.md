# Laiska laskenta, virrat ja generaattorit

Racket arvioi argumentit ennen kutsua (*ahne* eli *strict* arviointi),
kuten useimmat kielet. **Laiska** arviointi lykkää laskentaa, kunnes
arvoa tarvitaan. Näin voidaan käsitellä äärettömiä sekvenssejä, välttää
tarpeeton työ ja käsitellä suuria syötteitä vakiomuistissa. Haskell on
oletuksena laiska. Muissa kielissä laiskuus on erillinen väline:
iteraattori, generaattori tai virta.

## Lupaukset

`delay` luo **lupauksen** (*promise*): se tallentaa lausekkeen
arvioimatta sitä. `force` arvioi lausekkeen ensimmäisellä kerralla ja
palauttaa sen jälkeen muistetun arvon.

```{.scheme tiedosto="esimerkit/08-lupaus.rkt" osa="lupaus"}
```

Lupaus toimii myös laiskana argumenttina. Funktio päättää itse, tarvitaanko
arvoa. Tällä tavalla toteutetaan lyhytpiirtoinen `or` tai lokitus,
jonka viesti muodostetaan vain, jos taso on päällä.

```{.scheme tiedosto="esimerkit/08-lupaus.rkt" osa="ehto"}
```

```{.tuloste tiedosto="esimerkit/08-lupaus.odotettu"}
```

## Virrat

**Virta** (*stream*) on lista, jonka loppuosa on lupaus. `stream-cons`
laskee ensimmäisen alkion, mutta loppu lasketaan vasta tarvittaessa.
Virta voi siksi olla ääretön:

```{.scheme tiedosto="esimerkit/08-virrat.rkt" osa="luvut"}
```

Virroille on samat työkalut kuin listoille (`stream-map`,
`stream-filter`, `stream-ref`). Eratostheneen seula on virtana
kirjaimellisesti määritelmänsä: alkuluvut ovat ensimmäinen luku ja
seulottu loppuosa, josta sen monikerrat on poistettu.

```{.scheme tiedosto="esimerkit/08-virrat.rkt" osa="seula"}
```

Virtaketju ei rakenna välilistoja. Jokainen alkio kulkee ketjun läpi
yksi kerrallaan, ja kuluttaja päättää, milloin lopetetaan:

```{.scheme tiedosto="esimerkit/08-virrat.rkt" osa="putki"}
```

```{.tuloste tiedosto="esimerkit/08-virrat.odotettu"}
```

Virtaseula on kaunis mutta ei tehokas. Jokainen alkuluku lisää ketjuun
suodattimen, joten n:nnen alkuluvun laskeminen tekee neliöllisesti
työtä. Taulukkoon perustuva seula on oikea työkalu, kun yläraja tiedetään.

## Generaattorit ja jatkeet

Generaattori kirjoitetaan kuin tavallinen funktio, mutta `yield`
palauttaa arvon ja **keskeyttää** suorituksen. Seuraava kutsu jatkaa
siitä, mihin jäätiin. Puun läpikäynti säilyttää luonnollisen
rekursiivisen muotonsa, ja kutsuja saa arvot yksi kerrallaan:

```{.scheme tiedosto="esimerkit/08-generaattori.rkt" osa="puu"}
```

```{.scheme tiedosto="esimerkit/08-generaattori.rkt" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-generaattori.odotettu"}
```

Racketin generaattorit on toteutettu **jatkeilla** (*continuations*).
Jatke on "loppuosa laskennasta" arvona: `call/cc` antaa sen ohjelmalle,
ja sen kutsuminen palaa laskennan siihen kohtaan. Schemen jatkeista on
johdettu monta valtavirran ohjausrakennetta: generaattorit,
`async`/`await`, korutiinit, poikkeukset ja peruuttava haku (*backtracking*).
Racketissa niitä harvoin käytetään suoraan. Ne ovat välineitä, joilla
kirjastot rakentavat korkeamman tason ohjausrakenteita.

## Laiska syötteen käsittely

Laiskuuden käytännöllisin hyöty on suurten syötteiden käsittely.
`in-lines` lukee rivin kerrallaan. `#:final` lopettaa silmukan
ensimmäisen virheen jälkeen, joten loppua syötettä ei lueta lainkaan.

```{.scheme tiedosto="esimerkit/08-loki.rkt" osa="loki"}
```

```{.tuloste tiedosto="esimerkit/08-loki.syote"}
```

```{.tuloste tiedosto="esimerkit/08-loki.odotettu"}
```

## Käytännössä

- **Iteraattorit ovat valtavirran virtoja.** Pythonin generaattorit ja
  `itertools`, Javan `Stream` (laiska, kunnes kutsutaan
  päätösoperaatiota), C#:n `IEnumerable` ja `yield return`, Rustin
  iteraattorit ja C++20:n `std::views` ovat laiskoja ketjuja.
  Välilistoja ei synny, ja ketju pysähtyy, kun kuluttaja lopettaa.
- **Laiskuus ja sivuvaikutukset eivät sovi yhteen.** Jos laiska
  lauseke lukee tiedostoa tai tulostaa, vaikutuksen ajankohta riippuu
  siitä, milloin ja kuinka monta kertaa arvoa pyydetään. Javan
  Streamin tai Pythonin generaattorin voi käydä läpi vain kerran.
  Toinen läpikäynti palauttaa hiljaa tyhjän tuloksen.
- **Laiskuus voi pitää muistia varattuna.** Virta, jonka alkuun
  viitataan, säilyttää kaikki jo lasketut alkiot. Haskellissa
  odottavien laskujen (*thunk*) kertyminen on tunnettu muistivuodon
  lähde. Pidä viittaus vain siihen kohtaan, jota tarvitset.
- **`async`/`await` on keskeytettävä funktio.** Kun tiedät, että
  generaattori jäädyttää suorituksen kohtaan `yield` ja jatkaa siitä,
  ymmärrät myös, miten `await` toimii JavaScriptissä, Pythonissa, C#:ssa
  ja Rustissa. Kääntäjä muuttaa funktion tilakoneeksi, ja tila säilyy
  keskeytyksen yli.
- **Laiska alustus on yleinen malli.** Javan `Supplier`, Kotlinin
  `by lazy`, Rustin `OnceLock` ja C#:n `Lazy<T>` ovat lupauksia.
  Monisäikeisessä ohjelmassa alustuksen täytyy olla synkronoitu, ja
  kirjastototeutukset hoitavat sen.

## Itsearviointi

- Osaat käyttää lupauksia (`delay`, `force`) ja selittää, miksi
  lupauksen lauseke arvioidaan korkeintaan kerran.
- Osaat määritellä äärettömän virran ja käsitellä siitä äärellisen osan.
- Osaat kirjoittaa generaattorin, joka käy rekursiivisen rakenteen läpi,
  ja selittää yhteyden jatkeisiin ja `async`/`await`-rakenteeseen.
- Osaat käsitellä suuren syötteen laiskasti niin, että muistinkäyttö
  ei riipu syötteen koosta.
- Osaat tunnistaa laiskuuden sudenkuopat: sivuvaikutusten ajoituksen,
  kertakäyttöiset iteraattorit ja muistin, joka jää varatuksi.
