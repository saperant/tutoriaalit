# Johdanto {.runko-johdanto}

Tämä tutoriaali opettaa funktionaalisen ohjelmoinnin ajattelutapoja
Lispin perinteestä. Kielenä on Racket, mutta tavoite ei ole Racketin
hallinta työkielenä. Opeteltavat mallit esiintyvät nykyään lähes kaikissa
valtavirran kielissä: lambdat ja sulkeumat, `map`, `filter` ja `reduce`,
muuttumaton data, hahmontunnistus, laiskat iteraattorit, makrot ja
tulkit. Ne on helpointa oppia kielessä, jossa ne ovat perusasioita eivätkä
myöhemmin lisättyjä ominaisuuksia.

Tutoriaali olettaa taidon *Ohjelmoinnin perusteet*: lukija osaa
muuttujat, ehdot, silmukat, funktiot ja tavalliset tietorakenteet
jossakin kielessä. Racketia ei tarvitse osata entuudestaan.

## Miksi Lisp ja miksi Racket

John McCarthy kehitti Lispin vuonna 1958 tekoälytutkimuksen kieleksi.
Lisp toi ohjelmointiin monta asiaa, jotka ovat nykyään itsestäänselviä:

| Lispin keksintö | Missä nykyään |
|-----------------|---------------|
| roskienkeruu | Java, C#, Python, JavaScript, Go |
| funktiot arvoina, lambdat | lähes kaikki kielet, C++11, Java 8 |
| ehtolauseke, joka palauttaa arvon | `?:`, Rustin `if`, Kotlinin `when` |
| REPL eli vuorovaikutteinen kehote | Python, Node.js, Jupyter |
| koodi datana, makrot | Rustin `macro_rules!`, Julia, Elixir |
| dynaaminen tyypitys | Python, JavaScript, Ruby |

Scheme (Sussman ja Steele, 1975) karsi Lispistä ytimen: leksikaalinen
näkyvyys, sulkeumat ja taatut häntäkutsut. Scheme oli pitkään MIT:n
ohjelmoinnin peruskurssin kieli ja kirjan *Structure and Interpretation
of Computer Programs* (SICP) perusta. Racket syntyi 1990-luvulla PLT
Schemenä opetuskäyttöön, ja vuonna 2010 se nimettiin uudelleen, koska
kieli oli kasvanut Schemeä laajemmaksi.

Racketin valintaan on kolme syytä:

- Racket on **ohjelmointikielten tekemiseen** suunniteltu kieli. Sen
  makrojärjestelmä on Lisp-perheen kehittynein, ja jokainen tiedosto
  alkaa rivillä `#lang`, joka valitsee kielen.
- Kieli on **käytännöllinen**: moduulit, sopimukset (contracts),
  tietueet, hahmontunnistus, laaja standardikirjasto ja hyvä
  dokumentaatio.
- Opetusmateriaali on **erinomaista**. *How to Design Programs* ja
  SICP:n Racket-versiot käyttävät sitä.

Racket ei ole yleinen tuotantokieli. Lisp-perheen tuotantokieliä ovat
Clojure (JVM), Common Lisp ja Emacs Lisp. Funktionaalisia tuotantokieliä
ovat myös Haskell, OCaml, F#, Elixir ja Scala. Tässä tutoriaalissa
opittu siirtyy niihin suoraan.

## Mitä tutoriaali ei ole

Tutoriaali ei ole kattava Racket-opas eikä tyyppiteorian johdanto.
Staattisesti tyypitettyä funktionaalista ohjelmointia (Haskell, OCaml,
Typed Racket) käsitellään vain viittauksina. Jokaisen luvun
*Käytännössä*-osio kertoo, missä sama malli näkyy Pythonissa,
JavaScriptissä, Javassa, C++:ssa tai Rustissa, sillä niissä lukija mallia
todennäköisimmin käyttää.

## Työkalut

Racketin asennus sisältää seuraavat ohjelmat:

| Ohjelma | Käyttö |
|---------|--------|
| `racket tiedosto.rkt` | ajaa moduulin ja sen `main`-alimoduulin |
| `racket` | REPL: lausekkeiden kokeilu |
| `raco test tiedosto.rkt` | ajaa `test`-alimoduulin testit |
| `raco make tiedosto.rkt` | kääntää tavukoodiksi hakemistoon `compiled/` |
| `raco expand tiedosto.rkt` | näyttää makrojen laajennuksen |
| `raco pkg install nimi` | asentaa paketin |
| `raco docs aihe` | avaa dokumentaation selaimeen |
| `drracket` | Racketin oma kehitysympäristö |

DrRacket on aloittelijalle helpoin ympäristö: se näyttää virheen kohdan
ja tarjoaa askeltavan suorittajan sekä makrojen tarkastelijan. VS
Codessa on Magic Racket -laajennus. Emacsissa vastaava on racket-mode.
Tämän tutoriaalin esimerkit on testattu Racketin versiolla 8.10.
Kehityskontti sisältää saman version (ks. `README.md`).

## Ensimmäinen ohjelma

Ensimmäinen ohjelma laskee syötteen yleisimmät sanat. Se näyttää
funktionaalisen ohjelman tyypillisen muodon: data kulkee funktiosta
toiseen, eikä yhtään muuttujaa päivitetä.

```{.scheme tiedosto="esimerkit/01-sanat.rkt" osa="sanat"}
```

```{.scheme tiedosto="esimerkit/01-sanat.rkt" osa="paa"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/01-sanat.syote"}
```

```{.tuloste tiedosto="esimerkit/01-sanat.odotettu"}
```

Lyhyt lukuohje syntaksiin:

- Kaikki on **etuliitemuotoista**: `(f a b)` kutsuu funktiota `f`
  argumenteilla `a` ja `b`. Myös operaattorit ovat funktioita: `(+ 1 2)`.
- Sulut eivät ole koristetta. `(f)` kutsuu funktiota, `f` on funktio
  itse.
- Hakasulkeet `[...]` ovat samoja kuin kaarisulkeet. Niitä käytetään
  tavan vuoksi sidontojen ja haarojen ympärillä.
- Nimet saavat sisältää merkkejä `-`, `?`, `!`, `>` ja `/`.
  Käytäntönä predikaatin nimi päättyy `?`-merkkiin (`empty?`),
  tilaa muuttavan funktion nimi `!`-merkkiin (`set!`) ja muunnoksen
  nimessä on `->` (`hash->list`).
- `;` aloittaa kommentin. `#lang racket` valitsee tiedoston kielen.

Funktio `for/fold` kokoaa tuloksen silmukassa ilman sijoitusta. Funktio
`hash-update` palauttaa *uuden* taulun eikä muuta vanhaa. Luku 4
käsittelee molemmat.

## Tutoriaalin rakenne

| Luku | Aihe | Ajattelutapa |
|------|------|--------------|
| 2 | Lausekkeet ja listat | kaikki on lauseke, lista rekursiivisena datana |
| 3 | Rekursio | rakenteellinen rekursio ja häntäkutsut |
| 4 | Korkeamman asteen funktiot | funktiot arvoina, sulkeumat |
| 5 | Muuttumaton data | tietueet, hahmontunnistus, pysyvät rakenteet |
| 6 | Testaus, sopimukset ja virheet | rackunit, sopimukset ja syyllinen |
| 7 | Koodi datana ja makrot | kielen laajentaminen |
| 8 | Laiska laskenta | virrat, lupaukset ja generaattorit |
| 9 | Tila ja ohjelman rakenne | funktionaalinen ydin, imperatiivinen kuori |
| 10 | Oma tulkki | `eval` ja `apply`, ympäristöt |
| 11 | Lopuksi | nyrkkisäännöt ja lähteet |

Luku 10 valmistaa taitoon *Kääntäjätekniikka*. Luvut 4, 5 ja 8 ovat
eniten käytössä valtavirran kielissä.
