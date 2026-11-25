# Testaus, sopimukset ja virheet

Puhdas funktio on helpoin mahdollinen testattava: sama syöte antaa aina
saman tuloksen, eikä testi tarvitse alustusta, valekomponentteja tai
siivousta. Tässä luvussa käydään läpi Racketin testikehys rackunit,
moduulien **sopimukset** (*contracts*) ja virheiden käsittely.

## Moduulit ja testialimoduuli

Jokainen `#lang racket` -tiedosto on moduuli. `provide` kertoo, mitä
moduuli vie ulos, ja `require` tuo toisen moduulin nimet. Kaikki
viemätön on yksityistä.

Esimerkkinä on muuttumaton FIFO-jono, joka on toteutettu kahdella
listalla. Lisäys tehdään käännetyn loppuosan etuun ja poisto alkuosan
etusta. Kun alkuosa tyhjenee, loppuosa käännetään. Jokainen alkio
käännetään vain kerran, joten operaatiot ovat **tasoitetusti** O(1).

```{.scheme tiedosto="esimerkit/06-jono/jono.rkt" osa="toteutus"}
```

Testit kirjoitetaan samaan tiedostoon `module+ test` -alimoduuliin. Se
ei kuulu moduulin ajonaikaiseen sisältöön, vaan `raco test` ajaa sen
erikseen. Testi näkee moduulin yksityisetkin nimet.

```{.scheme tiedosto="esimerkit/06-jono/jono.rkt" osa="testit"}
```

| rackunit | Tarkistaa |
|----------|-----------|
| `check-equal?` | `equal?`-vertailu, virheilmoitus näyttää molemmat arvot |
| `check-true`, `check-false` | totuusarvon |
| `check-=` | liukuluvut toleranssilla |
| `check-exn` | että lauseke heittää annetun poikkeuksen |
| `test-case` | nimeää testiryhmän |

Onnistuneet testit eivät tulosta mitään, ja epäonnistunut testi
tulostaa virheilmoituksen. `raco test .` ajaa hakemiston kaikkien
tiedostojen testit. Tämän tutoriaalin testaaja ajaa jokaisen
esimerkin pääohjelman, joten esimerkin pääohjelma tuo
testialimoduulin itse:

```{.scheme tiedosto="esimerkit/06-jono/main.rkt" osa="simulaatio"}
```

```{.tuloste tiedosto="esimerkit/06-jono.odotettu"}
```

## Sopimukset

Dynaamisesti tyypitetyssä kielessä virheellinen arvo voi kulkea pitkään
ennen kuin se aiheuttaa virheen, ja silloin syyllistä on vaikea
löytää. Racketin ratkaisu on **sopimus moduulin rajalla**:
`contract-out` liittää vietyyn nimeen ehdon, joka tarkistetaan
jokaisessa kutsussa moduulin ulkopuolelta.

```{.scheme tiedosto="esimerkit/06-jono/jono.rkt" osa="rajapinta"}
```

`(-> jono? any/c jono?)` on funktiosopimus: kaksi argumenttia ja
paluuarvo. `jonon-eka` vaatii, että jono ei ole tyhjä. Ehto kuuluu
rajapinnan kuvaukseen eikä jää toteutuksen sisälle.

Sopimusrikkomus kertoo **syyllisen** (*blame*). Jos kutsuja antaa
väärän argumentin, syyllinen on kutsuja. Jos funktio palauttaa väärän
arvon, syyllinen on funktion moduuli.

```{.scheme tiedosto="esimerkit/06-sopimus.kaatuu.rkt" osa="sopimus"}
```

```{.tuloste tiedosto="esimerkit/06-sopimus.virhe"}
```

Sisäiset kutsut moduulin sisällä eivät tarkista sopimusta, joten
toteutuksen tiukat silmukat eivät hidastu. `define/contract`
tarkistaa sopimuksen myös yksittäiselle määrittelylle. Sitä käytetään
harvemmin, koska jokainen kutsu maksaa tarkistuksen.

## Virheet arvoina ja poikkeuksina

Racketissa on kaksi tapaa ilmaista epäonnistuminen:

- **Arvo**: odotettu epäonnistuminen, kuten jäsentäminen tai haku,
  palauttaa `#f`:n tai erillisen tulosarvon. Kutsuja käsittelee sen
  heti.
- **Poikkeus**: ohjelmointivirhe tai tilanne, jota kutsuja ei voi
  järkevästi käsitellä paikan päällä. `raise` heittää, ja
  `with-handlers` ottaa kiinni predikaatin perusteella.

```{.scheme tiedosto="esimerkit/06-virheet.rkt" osa="arvona"}
```

Kun epäonnistuvia vaiheita on monta peräkkäin, jokaisen tuloksen
tarkistaminen erikseen tuottaa sisäkkäisiä ehtoja. `and` ketjuttaa
vaiheet: se palauttaa ensimmäisen `#f`:n tai viimeisen arvon, joten
ensimmäinen epäonnistuminen ohittaa loput.

```{.scheme tiedosto="esimerkit/06-virheet.rkt" osa="ketju"}
```

Sama ajatus on monen kielen syntaksissa: Rustin `?`-operaattori,
Kotlinin ja JavaScriptin `?.` sekä Javan `Optional.map` ja `flatMap`
jatkavat ketjua vain, jos edellinen vaihe onnistui. Yleinen nimi
rakenteelle "arvo tai epäonnistuminen, ja tapa ketjuttaa niitä" on
*monadi*; nimeä tärkeämpää on tunnistaa malli.

Oma poikkeustyyppi periytetään `exn:fail`-tyypistä. Se voi kantaa
lisätietoa, kuten rivinumeron:

```{.scheme tiedosto="esimerkit/06-virheet.rkt" osa="oma"}
```

```{.scheme tiedosto="esimerkit/06-virheet.rkt" osa="kasittely"}
```

```{.tuloste tiedosto="esimerkit/06-virheet.odotettu"}
```

Tulosteen toinen rivi on ketjun tulos neljälle avaimelle: vain
ensimmäinen läpäisee kaikki vaiheet. `with-handlers` ottaa kiinni vain
predikaatin hyväksymät poikkeukset.
`exn:fail?` sieppaa kaikki tavalliset virheet mutta ei käyttäjän
keskeytystä (`exn:break`), ja niin pitääkin olla.

## Käytännössä

- **Testit samassa tiedostossa** ovat Racketin, Rustin
  (`#[cfg(test)] mod tests`) ja D:n tapa. Testi pysyy koodin vieressä
  ja näkee yksityiset osat. Pythonissa ja Javassa testit ovat erillisissä
  tiedostoissa, ja yksityisen osan testaaminen on merkki siitä, että
  sen pitäisi olla oma moduulinsa.
- **Puhtaan ytimen testit ovat nopeita ja vakaita.** Mitä enemmän
  logiikasta on puhtaissa funktioissa, sitä vähemmän tarvitaan
  valekomponentteja (*mock*). Luku 9 jatkaa tätä ajatusta.
- **Sopimukset ovat Design by Contract -ajattelua.** Eiffel toi
  esi- ja jälkiehdot oliokieliin. Valtavirrassa niitä vastaavat
  tyyppivihjeet ja ajonaikaiset tarkistimet (Pythonin pydantic,
  TypeScriptin zod), Javan Bean Validation ja C++26:n sopimukset.
  Racketin tärkeä lisä on syyllisen nimeäminen rajapinnan yli.
- **Tarkista rajalla, luota sisällä.** Syöte validoidaan, kun se tulee
  järjestelmään (rajapinta, tiedosto, verkko). Sisäiset funktiot
  saavat luottaa tyyppeihinsä. Jos jokainen funktio tarkistaa kaiken,
  koodi hidastuu ja ehdot alkavat ristiriidella.
- **Poikkeuksen hinta riippuu kielestä.** Racketin poikkeus on
  kevyt, mutta odotettu epäonnistuminen ilmaistaan silti arvona, jotta
  se näkyy kutsujalle. Rust (`Result`), Go (virhearvo) ja funktionaaliset
  kielet (`Either`, `Option`) tekevät virheestä osan tyyppiä. Javassa ja
  C++:ssa poikkeus on kallis ja varattu poikkeuksellisille tilanteille.

## Itsearviointi

- Osaat kirjoittaa rackunit-testit `module+ test` -alimoduuliin ja ajaa
  ne `raco test` -komennolla.
- Osaat kirjoittaa moduulin rajapinnalle sopimukset ja tulkita
  sopimusrikkomuksen syyllisen.
- Osaat päättää, ilmaistaanko epäonnistuminen paluuarvona vai
  poikkeuksena, ja määritellä oman poikkeustyypin.
- Osaat ketjuttaa peräkkäiset epäonnistuvat vaiheet ilman sisäkkäisiä
  ehtoja ja tunnistat saman mallin muiden kielten syntaksista.
- Osaat selittää, miksi kahden listan jono on tasoitetusti O(1) ja miksi
  sen vanhat versiot pysyvät käyttökelpoisina.
