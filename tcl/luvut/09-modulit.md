# Nimiavaruudet, paketit ja tiedostot {.runko-modulit}

Pieni skripti mahtuu yhteen tiedostoon, mutta EDA-projektin skriptit
kasvavat nopeasti kirjastoiksi: yhteiset rajoitteet, raporttien
jäsentimet ja kulun vaiheet. Tämä luku näyttää, miten koodi jaetaan
nimiavaruuksiin ja paketteihin ja miten tiedostoja ja ulkoisia
ohjelmia käsitellään turvallisesti.

## Nimiavaruudet

`namespace eval ::nimi {…}` luo nimiavaruuden. Sen proseduurit ja
muuttujat ovat muotoa `::nimi::jasen`, eivätkä ne törmää muiden
skriptien eikä työkalun omiin komentoihin. Tämä on tärkeää EDA-
työkaluissa, joiden globaalissa nimiavaruudessa on tuhansia komentoja.

- `variable nimi ?arvo?` määrittelee nimiavaruuden muuttujan, ja
  proseduurin sisällä sama komento ottaa sen käyttöön.
- `namespace export` luettelee julkiset komennot.
- `namespace ensemble create` tekee nimiavaruudesta alikomentoja
  ottavan komennon, kuten Tcl:n oma `string` tai `dict`.

## Paketit

`package provide nimi versio` ilmoittaa paketin ja `package require
nimi ?versio?` lataa sen. Tulkki etsii paketteja `auto_path`-listan
hakemistoista tiedostoista `pkgIndex.tcl`, jotka kertovat, miten paketti
ladataan. Paketti ladataan vasta, kun sitä pyydetään.

```{.tcl tiedosto="esimerkit/09-paketti/pkgIndex.tcl"}
```

```{.tcl tiedosto="esimerkit/09-paketti/ajoitus.tcl"}
```

Pääohjelma lisää oman hakemistonsa hakupolkuun. `info script` kertoo
skriptin polun, joten ohjelma löytää kirjastonsa riippumatta siitä,
mistä hakemistosta se käynnistetään:

```{.tcl tiedosto="esimerkit/09-paketti/main.tcl"}
```

```{.tuloste tiedosto="esimerkit/09-paketti.odotettu"}
```

Vaihtoehto `pkgIndex.tcl`-tiedostolle on *Tcl-moduli*: tiedosto
`nimi-1.0.tm` hakemistossa, joka on lisätty komennolla
`::tcl::tm::path add`. Yksinkertaisimmillaan kirjasto ladataan
`source`-komennolla, kuten luvun 11 esimerkissä.

## Tiedostot

`open polku tila` avaa kanavan (`r`, `w`, `a`), `gets` ja `read` lukevat,
`puts` kirjoittaa ja `close` sulkee. `fconfigure` asettaa merkistön
(`-encoding utf-8`) ja rivinvaihdot (`-translation lf`). Oletusmerkistö
riippuu järjestelmän lokaalista, joten se asetetaan aina, kun
tiedostossa voi olla muita kuin ASCII-merkkejä.

```{.tcl tiedosto="esimerkit/09-tiedostot.tcl" osa="kirjoitus"}
```

`file` käsittelee polkuja ja hakemistoja siirrettävästi: `file join`,
`file dirname`, `file tail`, `file extension`, `file mkdir`, `file
rename`, `file delete` ja `file exists`. `glob` hakee tiedostoja
kuviolla ja palauttaa listan.

```{.tcl tiedosto="esimerkit/09-tiedostot.tcl" osa="hakemistot"}
```

## Ulkoiset ohjelmat

`exec` ajaa ohjelman suoraan ilman komentotulkkia. Argumentit ovat
Tcl:n sanoja, joten tiedostonimen välilyönnit eivät riko komentoa
eikä komentotulkki-injektiota synny. `exec` palauttaa tulosteen ja
heittää virheen, jos

- ohjelman paluuarvo ei ole nolla (`-errorcode CHILDSTATUS pid koodi`),
- tai ohjelma kirjoittaa virhevirtaan. Tämän estää ohjaus `2>@1`
  (virhevirta tulosteeseen) tai `2>@stderr`.

```{.tcl tiedosto="esimerkit/09-tiedostot.tcl" osa="exec"}
```

```{.tuloste tiedosto="esimerkit/09-tiedostot.odotettu"}
```

Komentotulkin piirteitä (putket, ohjaukset) tarvitaan harvoin, sillä
`exec` ymmärtää itse `|`, `<`, `>` ja `<<`. Jos komentotulkkia on pakko
käyttää, sille annetaan kiinteä skripti ja muuttuvat arvot
argumentteina: `exec sh -c {…"$1"…} sh $arvo`.

## Käytännössä

- **Kaikki koodi nimiavaruuteen.** Projektin etuliite (`::projekti::`)
  estää törmäykset työkalun ja muiden skriptien kanssa.
- **Paketti ja versio, kun koodia jaetaan.** `package require` versioineen
  tekee riippuvuudet näkyviksi ja epäonnistuu selvästi.
- **Polut `info script`-komennon suhteen.** Älä oleta nykyistä
  hakemistoa; EDA-työkalut vaihtavat sitä.
- **Atominen kirjoitus** väliaikaistiedoston ja `file rename`-komennon
  avulla, kun muut prosessit lukevat tiedostoa.
- **Merkistö aina asetettuna.** `fconfigure $f -encoding utf-8`.
- **`exec` listana, ei komentotulkin kautta.** Käsittele
  `CHILDSTATUS`-virhe ja ohjaa virhevirta tarkoituksella.

## Itsearviointi

- Osaat jakaa koodin nimiavaruuteen ja tehdä siitä komentokokoelman
  (`namespace ensemble`).
- Osaat tehdä paketin ja ladata sen `package require`-komennolla
  skriptin omasta hakemistosta.
- Osaat lukea ja kirjoittaa tiedostoja merkistö huomioiden ja kirjoittaa
  tiedoston atomisesti.
- Osaat ajaa ulkoisen ohjelman `exec`-komennolla ja käsitellä sen
  paluuarvon ja virhetulosteen.
