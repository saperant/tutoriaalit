# Oliot, luokat ja tyypit {.runko-omat-tyypit}

JavaScriptissa on kaksi tapaa kuvata omia tyyppejä. Ajonaikana on
olioita ja niiden prototyyppiketjuja; `class` on niiden päälle rakennettu
syntaksi. Tyyppitarkistimelle kuvataan rakenteita JSDocin
`@typedef`-määrittelyillä, jotka ovat rakenteellisia: olio kelpaa, jos
sillä on oikeat kentät, riippumatta siitä, miten se on luotu.

## Oliot ja purkaminen

Tavallinen olio on JavaScriptin yleisin tietorakenne: tietue, jonka
kentät kirjoitetaan literaaliin. Aiemmissa luvuissa olioita on jo luotu
ja purettu; tässä säännöt ovat koottuina.

```{.javascript tiedosto="esimerkit/07-oliot.js" osa="literaali"}
```

```{.tuloste tiedosto="esimerkit/07-oliot.odotettu" rivit="1-1"}
```

Kenttään viitataan pisteellä (`tuote.hinta`) tai hakasulkeilla, kun
nimi on muuttujassa tai ei kelpaa tunnisteeksi (`tuote["hinta"]`).
Purkaminen (*destructuring*) on sijoitus, jonka vasen puoli on olion
tai taulukon muotoinen:

```{.javascript tiedosto="esimerkit/07-oliot.js" osa="purkaminen"}
```

```{.tuloste tiedosto="esimerkit/07-oliot.odotettu" rivit="2-4"}
```

Sama syntaksi toimii funktion parametreissa (luvun 4 optio-olio) ja
`for...of`-silmukan muuttujassa. Levitys (*spread*) on purkamisen
vastapari: se kopioi olion kentät tai taulukon alkiot uuteen
literaaliin.

```{.javascript tiedosto="esimerkit/07-oliot.js" osa="levitys"}
```

```{.tuloste tiedosto="esimerkit/07-oliot.odotettu" rivit="5-5"}
```

Olion kentät käydään läpi funktioilla `Object.keys`, `Object.values`
ja `Object.entries`, ja `Object.fromEntries` kokoaa pareista olion:

```{.javascript tiedosto="esimerkit/07-oliot.js" osa="lapikaynti"}
```

```{.tuloste tiedosto="esimerkit/07-oliot.odotettu" rivit="6-9"}
```

Kentät luetellaan lisäysjärjestyksessä, paitsi kokonaislukua
muistuttavat avaimet, jotka tulevat ensin numerojärjestyksessä. Kun
avaimet tulevat datasta, oikea rakenne on `Map` (luku 6).

## Luokat

Luokkaa tarvitaan, kun datalla on sääntö, jonka on pädettävä aina
(invariantti), ja metodit valvovat sitä:

```{.javascript tiedosto="esimerkit/07-luokat.js"}
```

```{.tuloste tiedosto="esimerkit/07-luokat.odotettu"}
```

- **Yksityiset jäsenet** (`#saldo`, `#tarkista`) ovat kielen tasolla
  yksityisiä: niitä ei näe luokan ulkopuolelta edes `Object.keys`-
  funktiolla tai debuggerin ulkopuolisella koodilla. Vanha alaviivakäytäntö
  (`_saldo`) on vain sopimus.
- **Staattiset jäsenet** kuuluvat luokalle. Staattinen tehdasmetodi
  (`Tili.avaa`) antaa nimen luontitavalle ja voi palauttaa valmiiksi
  alustetun olion.
- **Getter** (`get saldo()`) näyttää kentältä, mutta on vain luku -
  ominaisuus, joten saldoa ei voi asettaa ohi invariantin.
- **Invariantti tarkistetaan jokaisessa muuttavassa metodissa**, jolloin
  olio ei voi koskaan olla virheellisessä tilassa.
- `toString` määrää, miten olio muuttuu merkkijonoksi.

Yksityiseen kenttään viittaaminen luokan ulkopuolella on jo
jäsennysvirhe:

```{.javascript tiedosto="esimerkit/07-yksityinen.ei-kaanny.js"}
```

```text
SyntaxError: Private field '#arvo' must be declared in an enclosing
class
```

## Prototyypit

Jokaisella oliolla on prototyyppi, josta se perii ominaisuudet. Haku
etenee ketjua pitkin, kunnes ominaisuus löytyy tai ketju päättyy
(`null`). `class` ja `extends` rakentavat saman ketjun:

```{.javascript tiedosto="esimerkit/07-prototyypit.js" osa="ketju"}
```

```{.javascript tiedosto="esimerkit/07-prototyypit.js" osa="luokka"}
```

```{.tuloste tiedosto="esimerkit/07-prototyypit.odotettu"}
```

```{.dot otsikko="Esimerkin prototyyppiketju. Kentät ovat oliossa itsessään, metodit haetaan ketjua pitkin."}
digraph {
  rankdir=TB; ranksep=0.25; node [shape=box];
  y [label="y: nimi, r"];
  yp [label="Ympyra.prototype: pinta()"];
  mp [label="Muoto.prototype: pinta(), kuvaus()"];
  op [label="Object.prototype: toString(), …"];
  n [label="null", shape=plaintext];
  y -> yp -> mp -> op -> n;
}
```

Kutsu `y.kuvaus()` ei löydä metodia oliosta eikä prototyypistä
`Ympyra.prototype`, vaan vasta seuraavasta lenkistä. Metodin sisällä
`this.pinta()` aloittaa haun taas oliosta `y`, joten kutsutuksi tulee
ympyrän oma `pinta`. Metodit ovat prototyypissä ja jaettuja, kentät jokaisessa oliossa.
`super(...)` on kutsuttava ennen kuin aliluokan konstruktori käyttää
`this`-arvoa. `Object.create` palauttaa tyyppitarkistimelle tyypin
`any`, joten suorat prototyypit ovat nykykoodissa harvinaisia.

## Koostaminen periytymisen sijaan

Periytyminen sitoo aliluokan yliluokan toteutukseen, ja syvät
hierarkiat ovat vaikeita muuttaa. JavaScriptissa tavallisempia ovat
koostaminen (olio sisältää toisen ja delegoi sille), tehdasfunktiot
(luku 9) ja *erotellut unionit*: kaikki variantit ovat tavallista dataa,
ja `laji`-kenttä kertoo, mikä variantti on kyseessä.

```{.javascript tiedosto="esimerkit/07-unionit.js" osa="tyypit"}
```

```{.javascript tiedosto="esimerkit/07-unionit.js" osa="kattava"}
```

```{.tuloste tiedosto="esimerkit/07-unionit.odotettu"}
```

Tarkistin kaventaa tyyppiä `switch`-haarassa, joten `m.r` on käytettävissä
vain ympyrälle. Jos unioniin lisätään uusi laji, jota ei käsitellä,
`never`-tyyppinen sijoitus paljastaa sen:

```{.javascript tiedosto="esimerkit/07-kattavuus.ei-kaanny.js"}
```

```text
07-kattavuus.ei-kaanny.js(20,13): error TS2322: Type '{ tila:
"palautettu"; syy: string; }' is not assignable to type 'never'.
```

Malli vastaa Rustin `enum`-tyyppiä ja Kotlinin `sealed`-luokkia. Se
sopii tilakoneisiin, viesteihin ja jäsennyspuihin. Luokkahierarkia
sopii paremmin, kun uusia variantteja lisätään useammin kuin uusia
operaatioita (lausekeongelma).

## Geneeriset tyypit

JSDocin `@template` tekee tyypeistä ja funktioista geneerisiä. *Tulos*-
tyyppi (Rustin `Result`) ilmaisee odotetun epäonnistumisen ilman
poikkeusta:

```{.javascript tiedosto="esimerkit/07-geneerinen.js" osa="tulos"}
```

```{.javascript tiedosto="esimerkit/07-geneerinen.js" osa="kaytto"}
```

Rajoite `@template {keyof T} K` sallii vain `T`:n kenttien nimet, ja
paluutyyppi `Map<T[K], T[]>` johdetaan niistä:

```{.javascript tiedosto="esimerkit/07-geneerinen.js" osa="rajoite"}
```

```{.tuloste tiedosto="esimerkit/07-geneerinen.odotettu"}
```

## Käytännössä

- **Data ensin.** Jos tyyppi on pelkkää dataa, `@typedef` ja
  olioliteraali riittävät; luokkaa tarvitaan, kun datalla on
  invariantti, jota metodit valvovat.
- **`#yksityinen` sopimuksen sijaan.** Yksityiset kentät mahdollistavat
  toteutuksen muuttamisen rikkomatta käyttäjiä.
- **Tehdasmetodi monimutkaiselle luonnille**, konstruktori yksinkertaiselle.
  Asynkronista alustusta ei voi tehdä konstruktorissa; siihen sopii
  staattinen `async`-tehdas.
- **Erotellut unionit ja kattava `switch`** tilakoneisiin ja viesteihin.
  Kattavuustarkistus muuttaa unohtuneen tapauksen tyyppivirheeksi.
- **Koostaminen ennen periytymistä.** `extends` sopii lähinnä virheiden
  hierarkioihin (luku 8) ja kehysten kantaluokkiin.
- **Hinta.** Luokkien oliot saavat yhtenäisen muodon (luku 5) ja ovat
  siksi tehokkaita. Yksityiset kentät ovat yhtä nopeita kuin julkiset.
  Getterin kutsu laajennetaan yleensä inline-koodiksi.

## Itsearviointi

- Osaat luoda olion literaalilla, purkaa olion ja taulukon
  oletusarvoineen ja käydä olion kentät läpi.
- Osaat kirjoittaa luokan, jolla on yksityiset kentät, getterit,
  staattinen tehdasmetodi ja invariantti.
- Osaat selittää prototyyppiketjun ja sen, miten `class` ja `extends`
  rakentavat sen.
- Osaat kuvata erotellun unionin JSDoc-tyypeillä ja tarkistaa
  `switch`-lauseen kattavuuden `never`-tyypillä.
- Osaat kirjoittaa geneerisen funktion ja tyypin `@template`-
  merkinnällä ja rajoitteella.
