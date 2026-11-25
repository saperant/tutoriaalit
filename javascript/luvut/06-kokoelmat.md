# Kokoelmat, iteraattorit ja merkkijonot {.runko-kokoelmat}

Lähes jokainen ohjelma kokoaa, suodattaa ja järjestää dataa. Tässä
luvussa käydään läpi JavaScriptin kokoelmat (taulukko, `Map`, `Set`),
niitä yhdistävä iteraattoriprotokolla sekä merkkijonot ja JSON, joiden
kautta data tulee ohjelmaan ja lähtee siitä. Kokoelmien yleiset
ominaisuudet ja aikavaativuudet ovat taidossa *Tietorakenteet*.

## Taulukot

`Array` on dynaaminen taulukko, jonka metodit jakautuvat kahteen
ryhmään: muuttavat (`push`, `pop`, `splice`, `sort`, `reverse`) ja
uuden taulukon palauttavat (`map`, `filter`, `slice`, `concat`,
`toSorted`, `toReversed`, `with`). Jälkimmäiset ovat oletus, koska ne
eivät yllätä muuta koodia.

```{.javascript tiedosto="esimerkit/06-taulukot.js" osa="perus"}
```

| Tarve | Metodi |
|-------|--------|
| muunna jokainen | `map`, `flatMap` |
| valitse | `filter`, `find`, `findLast`, `findIndex` |
| kokoa yhdeksi arvoksi | `reduce` |
| onko jokin / ovatko kaikki | `some`, `every`, `includes` |
| indeksi lopusta | `at(-1)` |
| luo | `Array.from(iteroitava, f)`, `Array.from({ length: n }, f)` |
| ryhmittele | `Object.groupBy`, `Map.groupBy` |

### Lajittelu

`sort` ilman vertailufunktiota muuntaa alkiot merkkijonoiksi ja vertaa
UTF-16-koodiyksiköitä. Luvuille vertailufunktio on `(a, b) => a - b`,
ja tekstille kieliasetuksen mukainen `Intl.Collator`:

```{.javascript tiedosto="esimerkit/06-taulukot.js" osa="lajittelu"}
```

`Intl.Collator("fi").compare` järjestää suomen mukaan: isot ja pienet
kirjaimet sekaisin, å, ä ja ö aakkosten lopussa. Lajittelu on vakaa
(ES2019), joten monen avaimen lajittelu onnistuu ketjuttamalla tai
yhdistämällä vertailut `||`-operaattorilla.

### Ryhmittely

```{.javascript tiedosto="esimerkit/06-taulukot.js" osa="ryhmittely"}
```

`Object.groupBy` (ES2024) palauttaa olion, jonka avaimet ovat
merkkijonoja. Tyypissä ryhmä voi puuttua, joten purkamisessa on
oletusarvo `= []`.

### Reiät

```{.javascript tiedosto="esimerkit/06-taulukot.js" osa="reiat"}
```

```{.tuloste tiedosto="esimerkit/06-taulukot.odotettu"}
```

Reikäinen taulukko on sekä virhealtis (`map` ohittaa reiät) että
hidas. Taulukko luodaan `Array.from`-funktiolla tai `fill`-metodilla,
ei `new Array(n)`-kutsulla ja sijoittelemalla.

## Map ja Set

Tavallinen olio sopii tietueeksi, jonka kentät tunnetaan. Sanakirjaksi,
jonka avaimet tulevat datasta, se on huono:

```{.javascript tiedosto="esimerkit/06-map-set.js" osa="sanakirja"}
```

Olion avaimet muuttuvat merkkijonoiksi, ja prototyypistä perityt nimet
(`constructor`, `toString`, `__proto__`) näyttävät olemassa olevilta.
Käyttäjän syötteestä tuleva avain `__proto__` voi jopa muuttaa olion
prototyypin (*prototype pollution*). `Map` ei kärsi näistä, kertoo
kokonsa ja on nopeampi, kun avaimia lisätään ja poistetaan.

`Map` ja `Set` vertaavat avaimia samuuden mukaan (`SameValueZero`), joten
olioavain löytyy vain samalla oliolla:

```{.javascript tiedosto="esimerkit/06-map-set.js" osa="oliot"}
```

```{.javascript tiedosto="esimerkit/06-map-set.js" osa="joukot"}
```

```{.javascript tiedosto="esimerkit/06-map-set.js" osa="ryhmittely"}
```

```{.tuloste tiedosto="esimerkit/06-map-set.odotettu"}
```

`Set`-oliolla on myös valmiit joukko-operaatiot (`union`,
`intersection`, `difference`, `isSubsetOf`; ES2025, Node 22:sta
alkaen), jotka korvaavat esimerkin `filter`-rivit, kun tyyppitarkistimen
kirjasto on ES2025 (ks. seuraava osio).

## Iteraattorit ja generaattorit

Iteroitava on olio, jolla on metodi `[Symbol.iterator]()`. Sen palauttama
iteraattori antaa `next()`-kutsuilla olioita `{ value, done }`.
`for...of`, levitys, purkaminen, `Array.from` ja `Promise.all`
toimivat kaikilla iteroitavilla. Generaattorifunktio (`function*`) on
helpoin tapa toteuttaa protokolla:

```{.javascript tiedosto="esimerkit/06-iteraattorit.js" osa="protokolla"}
```

```{.tuloste tiedosto="esimerkit/06-iteraattorit.odotettu" rivit="1-3"}
```

Generaattori on laiska: se laskee seuraavan arvon vasta, kun sitä
pyydetään. Siksi äärettömästä jonosta voi suodattaa ja ottaa alun:

```{.javascript tiedosto="esimerkit/06-iteraattorit.js" osa="laiska"}
```

```{.tuloste tiedosto="esimerkit/06-iteraattorit.odotettu" rivit="4-4"}
```

Omat generaattorit `suodata` ja `ota` näyttävät mekanismin. Arjessa
niitä ei tarvitse kirjoittaa itse: ES2025 antaa iteraattoreille samat
apumetodit kuin taulukoille (`map`, `filter`, `take`, `drop`,
`flatMap`, `some`, `every`, `reduce`, `toArray`), ja ne ovat
molemmissa testatuissa Node-versioissa.

```{.javascript tiedosto="esimerkit/06-iteraattorit.js" osa="apumetodit"}
```

```{.tuloste tiedosto="esimerkit/06-iteraattorit.odotettu" rivit="5-6"}
```

Ero taulukon metodeihin on laiskuus: `taulukko.filter(...).map(...)`
luo välitaulukon jokaisessa vaiheessa, iteraattoriketju käsittelee
alkion kerrallaan eikä laske enempää kuin `take` pyytää.
Tyyppitarkistimen kirjastotyypit tulevat asetuksesta `target` (tässä
ES2024), joten esimerkkitiedoston alussa on rivi
`/// <reference lib="es2025" />`, joka ottaa uudemmat tyypit käyttöön
tälle tiedostolle.

Protokollan voi ajaa myös käsin `next`-kutsuilla:

```{.javascript tiedosto="esimerkit/06-iteraattorit.js" osa="kasin"}
```

```{.tuloste tiedosto="esimerkit/06-iteraattorit.odotettu" rivit="7-9"}
```

## Merkkijonot

Merkkijono on muuttumaton jono UTF-16-koodiyksiköitä. `length` ja
indeksointi laskevat koodiyksiköitä, joten Unicode-merkki voi viedä
kaksi paikkaa. Levitys `[...s]` jakaa koodipisteisiin, ja käyttäjän
näkemät merkit (*grafeemit*) erottaa `Intl.Segmenter`:

```{.javascript tiedosto="esimerkit/06-merkkijonot.js" osa="unicode"}
```

Sama näkyvä merkki voi olla koodattu monella tavalla. Vertailu tai
haku vaatii normalisoinnin:

```{.javascript tiedosto="esimerkit/06-merkkijonot.js" osa="normalisointi"}
```

Tavallisimmat käsittelyt ja säännöllinen lauseke nimetyin ryhmin:

```{.javascript tiedosto="esimerkit/06-merkkijonot.js" osa="kasittely"}
```

```{.javascript tiedosto="esimerkit/06-merkkijonot.js" osa="rakentaminen"}
```

```{.tuloste tiedosto="esimerkit/06-merkkijonot.odotettu"}
```

## Säännölliset lausekkeet

Säännöllinen lauseke kirjoitetaan literaalina `/malli/liput`. Mallien
kieli on lähes sama kuin muissa kielissä; JavaScriptille ominaista ovat
liput ja se, mitkä merkkijonon metodit lauseketta käyttävät.

| Lippu | Vaikutus |
|-------|----------|
| `g` | kaikki osumat, ei vain ensimmäistä |
| `i` | kirjainkoolla ei ole väliä |
| `m` | `^` ja `$` täsmäävät jokaisen rivin alkuun ja loppuun |
| `s` | piste täsmää myös rivinvaihtoon |
| `u` | Unicode: `\p{L}` (kirjain), koodipisteet kokonaisina |
| `y` | haku vain kohdasta `lastIndex` |

`match` ilman `g`-lippua palauttaa ensimmäisen osuman ryhmineen,
`matchAll` kaikki osumat iteraattorina:

```{.javascript tiedosto="esimerkit/06-saannolliset.js" osa="haku"}
```

```{.tuloste tiedosto="esimerkit/06-saannolliset.odotettu" rivit="1-3"}
```

```{.javascript tiedosto="esimerkit/06-saannolliset.js" osa="korvaus"}
```

```{.tuloste tiedosto="esimerkit/06-saannolliset.odotettu" rivit="4-5"}
```

`g`-lipullinen lauseke on tilallinen olio, mikä yllättää, kun sama
lauseke on tallennettu vakioon ja sitä käytetään `test`-metodilla:

```{.javascript tiedosto="esimerkit/06-saannolliset.js" osa="ansa"}
```

```{.tuloste tiedosto="esimerkit/06-saannolliset.odotettu" rivit="6-7"}
```

Käyttäjän antama teksti ei kelpaa malliksi sellaisenaan, koska siinä
voi olla erikoismerkkejä. Node 24:stä alkaen ne suojaa
`RegExp.escape(teksti)` (ES2025); vanhemmissa versioissa käytetään
`includes`- ja `replaceAll`-metodeja, jotka eivät tulkitse hakutekstiä
malliksi.

## JSON

`JSON.stringify` ja `JSON.parse` muuntavat datan tekstiksi ja takaisin.
Muunnos on häviöllinen:

```{.javascript tiedosto="esimerkit/06-json.js" osa="sarjallistus"}
```

`Date` muuttuu ISO-merkkijonoksi, `Map` ja `Set` tyhjiksi olioiksi,
ja `undefined`-arvoiset kentät ja funktiot jäävät pois. `bigint`
heittää poikkeuksen. Muunnosfunktio (*replacer*) korjaa tämän
sarjallistettaessa, ja *reviver* jäsennettäessä.

`JSON.parse` palauttaa tyypin `any`: se ei tiedä, mitä data sisältää.
Data validoidaan rajapinnassa, ja tyyppitarkistin seuraa tarkistuksia
(`typeof`, `in`) ja kaventaa tyyppiä:

```{.javascript tiedosto="esimerkit/06-json.js" osa="jasennys"}
```

```{.tuloste tiedosto="esimerkit/06-json.odotettu"}
```

Laajemmassa sovelluksessa validointiin käytetään skeemakirjastoa (Zod,
Valibot, Ajv), joka tuottaa sekä tarkistuksen että tyypin.

## Käytännössä

- **Kopioivat metodit oletuksena.** `toSorted` ja `map` eivät muuta
  alkuperäistä; `sort` ja `splice` muuttavat, ja niiden käyttö kannattaa
  rajata paikalliseen dataan.
- **Vertailufunktio aina `sort`-kutsuun**, ja suomenkieliselle tekstille
  `Intl.Collator("fi")`.
- **`Map` dynaamisille avaimille, olio tunnetuille kentille.** `Set`
  jäsenyydelle ja duplikaattien poistoon.
- **Generaattori laiskaan tai äärettömään dataan ja omiin
  tietorakenteisiin.** Se toteuttaa iteraattoriprotokollan, jolloin
  rakenne toimii `for...of`-silmukassa ja levityksessä.
- **Säännöllinen lauseke vakioon ilman `g`-lippua**, kun sitä käytetään
  `test`-metodilla; `g` kuuluu `matchAll`- ja `replace`-kutsuihin.
  Nimetyt ryhmät tekevät pitkästä mallista luettavan.
- **Validoi JSON rajapinnassa**, älä luota `JSON.parse`-tulokseen.
- **Ketjuta harkiten.** `filter().map().reduce()` luo välitaulukot.
  Datalle, jossa on miljoonia alkioita, yksi silmukka on nopeampi.
  Tavalliselle datalle luettavuus on tärkeämpää.
- **Hinta.** `includes` ja `indexOf` ovat lineaarisia; toistuvaan
  jäsenyystestiin kuuluu `Set` (vakioaikainen). `shift` ja `unshift`
  siirtävät koko taulukkoa. Jonoon sopii kaksi indeksiä tai rengaspuskuri.

## Itsearviointi

- Osaat käyttää taulukon tavallisimpia metodeja ja erottaa muuttavat
  metodit kopioivista.
- Osaat lajitella luvut ja suomenkielisen tekstin oikein.
- Osaat valita olion, `Map`-, `Set`- ja `WeakMap`-kokoelman välillä ja
  perustella valinnan.
- Osaat toteuttaa iteraattoriprotokollan generaattorilla ja koota
  laiskan putken sekä omilla generaattoreilla että iteraattorien
  apumetodeilla.
- Osaat hakea ja korvata säännöllisellä lausekkeella (`matchAll`,
  nimetyt ryhmät, korvausfunktio) ja selittää `g`-lipun
  `lastIndex`-ansan.
- Osaat käsitellä Unicode-merkkijonoja (koodiyksikkö, koodipiste,
  grafeemi, normalisointi) ja validoida jäsennetyn JSONin.
