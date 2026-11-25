# Arvot, tyypit ja syöte {.runko-tyypit}

JavaScriptissa on seitsemän primitiivityyppiä ja olio. Primitiivit
(`number`, `bigint`, `string`, `boolean`, `undefined`, `null`, `symbol`)
ovat muuttumattomia arvoja; kaikki muu, myös taulukot ja funktiot, on
olioita. Operaattori `typeof` kertoo arvon tyypin:

```{.javascript tiedosto="esimerkit/03-arvot.js" osa="typeof"}
```

`typeof null` on `"object"` historiallisen virheen vuoksi. Taulukon
tunnistaa funktiolla `Array.isArray`, ja `null`-arvon vertailulla
`x === null`.

## Muuttujat

`const` sitoo nimen arvoon pysyvästi, `let` sallii uudelleensijoituksen.
Molempien näkyvyysalue on lohko. Vanhaa `var`-määrittelyä ei käytetä:
sen näkyvyysalue on koko funktio, ja se "nostetaan" (hoisting) funktion
alkuun. Oletus on `const`; `let` kertoo lukijalle, että arvo muuttuu.

## Luvut

`number` on 64-bittinen IEEE 754 -liukuluku. Kokonaisluvut ovat tarkkoja
arvoon 2^53^ − 1 (`Number.MAX_SAFE_INTEGER`) asti. Suuremmille luvuille
on `bigint` (`10n`), jota ei voi sekoittaa `number`-arvoihin samassa
lausekkeessa.

```{.javascript tiedosto="esimerkit/03-arvot.js" osa="luvut"}
```

Jakolasku on aina liukulukujakoa; kokonaislukuosa otetaan funktiolla
`Math.trunc`. Jakojäännöksen `%` etumerkki seuraa jaettavaa. Nollalla
jakaminen ei heitä poikkeusta vaan antaa `Infinity` tai `NaN`, joten
laskennan tulos tarkistetaan funktiolla `Number.isFinite`.

## Muunnokset

```{.javascript tiedosto="esimerkit/03-arvot.js" osa="muunnokset"}
```

Koko esimerkin tuloste (ensimmäiset rivit ovat `typeof`-taulukko):

```{.tuloste tiedosto="esimerkit/03-arvot.odotettu"}
```

`Number(teksti)` hylkää koko merkkijonon, jos se ei ole luku, ja antaa
`NaN`. `parseInt` lukee alusta niin pitkälle kuin pystyy, joten se
hyväksyy myös `"42px"`. Syötteen validointiin `Number` on parempi.
Huomaa myös, että tyhjä merkkijono muuttuu nollaksi.

Implisiittiset muunnokset ovat kielen tunnetuin ansa: `+` yhdistää
merkkijonoja, jos toinen operandi on merkkijono, mutta muut
laskuoperaattorit muuntavat lukuiksi. Tyyppitarkistin hylkää tällaiset
lausekkeet, ja esimerkissä ne on kuitattu tarkoituksellisiksi
kommentilla `@ts-expect-error`:

```{.javascript tiedosto="esimerkit/03-aritmetiikka.ei-kaanny.js"}
```

```text
03-aritmetiikka.ei-kaanny.js(10,10): error TS2362: The left-hand side
of an arithmetic operation must be of type 'any', 'number', 'bigint' or
an enum type.
```

## Yhtäsuuruus

`===` vertaa tyyppiä ja arvoa, `==` muuntaa tyyppejä ennen vertailua.
`Object.is` on muuten sama kuin `===`, mutta pitää `NaN`-arvoa itsensä
kanssa samana ja erottaa nollan etumerkin.

```{.javascript tiedosto="esimerkit/03-yhtasuuruus.js" osa="vertailu"}
```

```{.tuloste tiedosto="esimerkit/03-yhtasuuruus.odotettu"}
```

Oliot ovat yhtä suuria vain, jos ne ovat sama olio:

```{.javascript tiedosto="esimerkit/03-yhtasuuruus.js" osa="viitteet"}
```

`includes` käyttää `Object.is`-tyyppistä vertailua ja löytää `NaN`-arvon,
`indexOf` käyttää `===`-vertailua eikä löydä. `Map` ja `Set` vertaavat
avaimia samoin kuin `includes`.

## Puuttuvat arvot

JavaScriptissa on kaksi puuttuvaa arvoa. `undefined` tarkoittaa, että
arvoa ei ole annettu: alustamaton muuttuja, puuttuva kenttä tai
argumentti, funktio ilman `return`-lausetta. `null` on ohjelmoijan
nimenomainen "ei arvoa". Hyvä käytäntö on käyttää omassa koodissa
toista johdonmukaisesti, yleensä `undefined`, ja `null` siellä, missä
rajapinta (JSON, DOM) sitä käyttää.

```{.javascript tiedosto="esimerkit/03-puuttuva.js" osa="kasittely"}
```

```{.javascript tiedosto="esimerkit/03-puuttuva.js" osa="ero"}
```

```{.tuloste tiedosto="esimerkit/03-puuttuva.odotettu"}
```

- `a ?? b` antaa arvon `b` vain, jos `a` on `null` tai `undefined`.
  `a || b` hylkää myös arvot `0`, `""` ja `false`, joten aikaraja `0`
  vaihtuisi oletukseksi.
- `a?.b` palauttaa `undefined`, jos `a` puuttuu, eikä heitä virhettä.
  Sama toimii kutsuissa (`f?.()`) ja indekseissä (`a?.[i]`).
- Kenttä voi olla olemassa arvolla `undefined`. Olemassaolon kertovat
  `in` ja `Object.hasOwn`. `JSON.stringify` jättää tällaiset kentät pois.

JSDoc-tyypissä hakasulkeet `[aikaraja]` merkitsevät valinnaista kenttää,
ja tiukka tila pakottaa käsittelemään `undefined`-tapauksen.

## Tulostus ja muotoilu

Mallimerkkijono (template literal) `` `...${lauseke}...` `` on
JavaScriptin muotoilukeino. `padStart` ja `padEnd` tasaavat sarakkeet.
Luvut, valuutat ja päivämäärät muotoillaan `Intl`-olioilla, jotka
noudattavat kielen ja alueen käytäntöjä:

```{.javascript tiedosto="esimerkit/03-muotoilu.js" osa="muotoilu"}
```

```{.javascript tiedosto="esimerkit/03-muotoilu.js" osa="perus"}
```

```{.tuloste tiedosto="esimerkit/03-muotoilu.odotettu"}
```

`Intl.NumberFormat` käyttää suomalaisia erottimia (sitova välilyönti
tuhaterottimena, pilkku desimaalierottimena). `toFixed` pyöristää
binääriesityksen mukaan, joten `1.005` pyöristyy alaspäin. Siksi
rahasummat lasketaan kokonaislukuina sentteinä ja muunnetaan euroiksi
vasta tulostettaessa.

`console.log` tulostaa useat argumentit välilyönnein erotettuina ja
oliot luettavassa muodossa. `console.error` kirjoittaa virhevirtaan.
Rakenteinen loki tehdään kirjastolla (luku 11).

## Aika ja päivämäärät

`Date` on aikaleima: millisekuntien määrä vuoden 1970 alusta
UTC-aikaa. Olio ei tiedä aikavyöhykettä eikä esitysmuotoa, vaan ne
annetaan vasta muotoiltaessa.

```{.javascript tiedosto="esimerkit/03-aika.js" osa="aikaleima"}
```

```{.tuloste tiedosto="esimerkit/03-aika.odotettu" rivit="1-2"}
```

`Date` on kielen vanhimpia osia, ja sen rajapinnassa on kolme ansaa:
jäsennyksen tulkinta riippuu merkkijonon muodosta, olio on muuttuva, ja
virheellinen syöte tuottaa hiljaa arvon *Invalid Date*.

```{.javascript tiedosto="esimerkit/03-aika.js" osa="ansat"}
```

```{.tuloste tiedosto="esimerkit/03-aika.odotettu" rivit="3-5"}
```

Näyttämistä varten aikaleima muotoillaan `Intl.DateTimeFormat`-oliolla,
jolle annetaan kieli ja aikavyöhyke. Sama hetki näkyy eri vyöhykkeillä
eri kellonaikana:

```{.javascript tiedosto="esimerkit/03-aika.js" osa="muotoilu"}
```

```{.tuloste tiedosto="esimerkit/03-aika.odotettu" rivit="6-8"}
```

Tiedostoihin, tietokantoihin ja rajapintoihin aika kirjoitetaan
ISO 8601 -muodossa UTC:nä (`toISOString`). Kalenterilaskenta, kuten
"kuukauden päästä" tai toistuva kokous kesäajan vaihtuessa, ei onnistu
luotettavasti aikaleimalla. Sitä varten on suunniteltu
`Temporal`-rajapinta, jossa päivämäärä, kellonaika ja vyöhyke ovat omia
muuttumattomia tyyppejään. Uusimmat selaimet toteuttavat sen, mutta
testatuissa Node-versioissa sitä ei ole, joten Nodessa käytetään
toistaiseksi kirjastoa (date-fns, Luxon).

## Syötteen lukeminen

Node lukee syötettä virtana. Rivit luetaan `readline`-modulilla
asynkronisena iteraattorina, jolloin koko syötettä ei tarvitse pitää
muistissa.

Syöte saapuu vähitellen, joten esimerkissä on kaksi asynkronista
rakennetta, jotka luku 10 selittää tarkasti. `await` odottaa tulosta,
joka valmistuu myöhemmin (lupaus), pysäyttämättä muuta ohjelmaa.
`for await` on silmukka, joka odottaa jokaista alkiota samalla tavalla,
tässä seuraavaa riviä. ES-modulissa `await` kelpaa ylimmällä tasolla,
ja funktiossa sitä saa käyttää, kun funktio on merkitty sanalla
`async`. Lukuun 10 asti riittää tietää, että `await`-kohdassa ohjelma
odottaa ja jatkaa sitten seuraavalta riviltä.

```{.javascript tiedosto="esimerkit/03-syote.js"}
```

```{.tuloste tiedosto="esimerkit/03-syote.odotettu"}
```

Rivin osat puretaan suoraan muuttujiin, ja ylimääräiset kentät
kerätään loppuparametriin `...ylimaaraiset`. `Number.isInteger`
hylkää sekä `NaN`-arvon että desimaaliluvut. Komentoriviargumentit
ovat taulukossa `process.argv` (kaksi ensimmäistä ovat Noden ja
skriptin polut), ja Node 18.3:sta alkaen niitä voi jäsentää funktiolla
`util.parseArgs`.

## Käytännössä

- **`const` oletuksena, `let` kun arvo muuttuu, ei koskaan `var`.**
  Tämä tekee muuttuvan tilan näkyväksi.
- **Aina `===`.** Ainoa yleinen poikkeus on `x == null`, joka tarkoittaa
  "`null` tai `undefined`". Selkeämpi on silti `x ?? oletus` tai
  `x === undefined`.
- **Muunna rajapinnassa, tarkista heti.** Syöte (lomake, tiedosto,
  JSON) muunnetaan tyyppeihinsä yhdessä paikassa, ja `NaN` ja tyhjät
  kentät hylätään siellä. Sisemmän koodin ei tarvitse epäillä arvoja.
- **Rahat sentteinä, päivämäärät UTC-aikaleimoina.** Muotoilu tapahtuu
  vasta tulostettaessa `Intl`-olioilla, jotka luodaan kerran ja joita
  käytetään uudelleen (niiden luonti on kallista). Aika tallennetaan
  ja siirretään ISO 8601 -merkkijonona, jossa on `Z` tai siirtymä.
- **`??` ja `?.` valinnaisille arvoille.** Pitkä `?.`-ketju kertoo
  kuitenkin, että tietomalli on liian löyhä: tarkista rakenne kerran
  rajapinnassa.
- **Hinta.** Pienet kokonaisluvut (31-bittiset, *Smi*) ovat V8:ssa
  tehokkaimpia; luku, joka vaihtelee kokonaisluvun ja liukuluvun
  välillä, pakottaa moottorin yleisempään esitykseen. `bigint` on
  huomattavasti hitaampi kuin `number`.

## Itsearviointi

- Osaat luetella primitiivityypit ja kertoa, miksi `typeof null` on
  `"object"`.
- Osaat valita `===`-, `==`- ja `Object.is`-vertailun välillä ja kertoa,
  miten `NaN` ja `-0` käyttäytyvät.
- Osaat käyttää `??`- ja `?.`-operaattoreita ja selittää, miksi `||`
  on väärä oletusarvoille.
- Osaat muuntaa syötteen luvuksi turvallisesti ja tunnistaa
  implisiittiset muunnokset.
- Osaat muotoilla luvut, rahasummat ja päivämäärät `Intl`-olioilla ja
  lukea syötteen riveittäin.
- Osaat luoda aikaleiman yksiselitteisesti, kertoa `Date`-olion kolme
  ansaa ja näyttää saman hetken eri aikavyöhykkeillä.
