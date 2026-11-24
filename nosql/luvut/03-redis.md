# Redis: tietorakenteet muistissa

Redis on avain-arvo-tietokanta, jonka arvot eivät ole pelkkiä
merkkijonoja vaan tietorakenteita: listoja, hajautustauluja, joukkoja,
järjestettyjä joukkoja ja virtoja. Kaikki data on muistissa, ja
palvelin käsittelee komennot yksi kerrallaan yhdessä säikeessä. Siitä
seuraa Redisin kaksi tärkeintä ominaisuutta: yksittäinen komento vie
mikrosekunteja, ja jokainen komento on atominen.

Redisiä käytetään välimuistina, istuntojen säilönä, laskureina,
tulostauluina, jonoina ja nopeusrajoittimina – kaikkeen, mikä on pientä,
kuumaa ja haetaan avaimella. Pääasiallinen tietovarasto se on harvoin,
koska data mahtuu vain muistiin ja pysyvyys on valinnaista (luku 4).

Rediksen avoin haara Valkey on komennoiltaan sama, ja kaikki tämän
luvun esimerkit toimivat sillä sellaisenaan.

## Avaimet

Avaimet ovat merkkijonoja, ja niille käytetään kaksoispisteillä
jäsenneltyä nimeämistapaa: `tuote:42:varasto`, `kayttaja:7`,
`istunto:<tunnus>`. Redis ei tunne hierarkiaa, mutta tapa auttaa
ihmisiä ja työkaluja. Avainavaruus on yksi tasainen nimiavaruus, ja
kaikkien avainten läpikäynti (`KEYS *`) pysäyttää palvelimen
suurella datalla; `SCAN` käy ne läpi paloittain.

## Merkkijonot ja laskurit

Merkkijono on yksinkertaisin arvo. Jos se näyttää kokonaisluvulta,
`INCR`, `INCRBY` ja `DECR` muuttavat sitä palvelimella atomisesti:

```{.python tiedosto="esimerkit/luku03/rakenteet.py" osa="merkkijonot"}
```

Atomisuus on tärkeämpi kuin miltä näyttää. Jos sovellus lukisi arvon,
laskisi uuden ja kirjoittaisi sen takaisin, kaksi samanaikaista
pyyntöä voisi lukea saman arvon ja toinen päivitys katoaisi. Luvussa 4
tämä näytetään toteen.

## Hajautustaulut

Hajautustaulu (*hash*) on avaimen takana oleva kenttien ja arvojen
joukko, kuin pieni rivi. Se sopii olioille, joiden kenttiä luetaan ja
päivitetään erikseen:

```{.python tiedosto="esimerkit/luku03/rakenteet.py" osa="hajautus"}
```

Hajautustaulun kentillä ei ole tyyppejä eikä elinaikaa erikseen;
vanhentuminen koskee koko avainta.

## Listat

Lista on kaksipäinen jono: lisäys ja poisto kummastakin päästä ovat
vakioaikaisia. `LTRIM` pitää listan rajatun mittaisena, mikä on
tavallinen tapa säilyttää esimerkiksi viimeisimmät tapahtumat:

```{.python tiedosto="esimerkit/luku03/rakenteet.py" osa="lista"}
```

Listaa voi käyttää myös työjonona (`LPUSH` ja estävä `BRPOP`), mutta
luvun 4 virrat ovat siihen parempia: ne muistavat, kuka on käsitellyt
minkäkin viestin.

## Joukot

Joukko sisältää kunkin alkion kerran, ja joukko-operaatiot (`SINTER`,
`SUNION`, `SDIFF`) lasketaan palvelimella:

```{.python tiedosto="esimerkit/luku03/rakenteet.py" osa="joukko"}
```

## Järjestetyt joukot

Järjestetyssä joukossa (*sorted set*) jokaisella alkiolla on
pistemäärä, ja joukko pysyy pistemäärän mukaan järjestettynä.
Lisäys, päivitys ja sijan haku ovat logaritmisia. Tulostaulu,
myydyimmät tuotteet ja aikaleimalla järjestetty jono ovat kaikki
järjestettyjä joukkoja:

```{.python tiedosto="esimerkit/luku03/rakenteet.py" osa="jarjestetty"}
```

```{.tuloste tiedosto="esimerkit/luku03/rakenteet.odotettu"}
```

Relaatiotietokannassa sama vaatisi indeksin ja `ORDER BY ... LIMIT`
-kyselyn jokaisella haulla; Redisissä järjestys on valmiina.

## Elinaika

Jokaiselle avaimelle voi antaa elinajan (TTL), jonka jälkeen Redis
poistaa sen. Istunnot ovat tyypillinen käyttö: jokainen pyyntö
pidentää elinaikaa, ja käyttämätön istunto katoaa itsestään.

```{.python tiedosto="esimerkit/luku03/elinaika.py" osa="istunto"}
```

`TTL` palauttaa jäljellä olevat sekunnit, `-1`, jos avaimella ei ole
elinaikaa, ja `-2`, jos avainta ei ole:

```{.python tiedosto="esimerkit/luku03/elinaika.py" osa="vanheneminen"}
```

```{.tuloste tiedosto="esimerkit/luku03/elinaika.odotettu"}
```

Vanhentunut avain poistetaan, kun sitä yritetään lukea, ja lisäksi
taustalla satunnaisotannalla. Muisti ei siis vapaudu täsmälleen
elinajan päättyessä, mutta vanhentunutta arvoa ei koskaan palauteta.

Kun muisti loppuu, `maxmemory-policy` päättää, mitä poistetaan.
Välimuistille sopii `allkeys-lru` tai `allkeys-lfu`; jos Redis on
ainoa tallennuspaikka jollekin datalle, oikea asetus on `noeviction`,
jolloin kirjoitukset epäonnistuvat eivätkä hiljaa poista dataa.

## Putkitus

Jokainen komento on edestakainen matka verkon yli. Paikallisessa
verkossa matka vie kymmeniä tai satoja mikrosekunteja, mikä on paljon
enemmän kuin komennon suoritus palvelimella. Putkitus (*pipelining*)
lähettää monta komentoa kerralla ja lukee vastaukset yhdessä:

```{.python tiedosto="esimerkit/luku03/putki.py" osa="putki"}
```

Monen avaimen komennot kuten `MGET` ja `MSET` tekevät saman yhdellä
komennolla:

```{.python tiedosto="esimerkit/luku03/putki.py" osa="mget"}
```

```{.tuloste tiedosto="esimerkit/luku03/putki.odotettu"}
```

Putkitus ei tee komennoista atomisia: muiden asiakkaiden komennot voivat
suorittua välissä. Atomisuuteen tarvitaan transaktio tai skripti
(luku 4).

## Käytännössä

- Valitse tietorakenne käytön mukaan: laskuri merkkijonona, olio
  hajautustauluna, viimeisimmät listana, tulostaulu järjestettynä
  joukkona.
- Anna avaimille elinaika aina, kun data on uudelleenluotavissa.
  Muuten muisti täyttyy hitaasti ja huomaamatta.
- Älä käytä `KEYS`-komentoa tuotannossa; käytä `SCAN`-komentoa tai
  pidä erillistä joukkoa avaimista.
- Pidä arvot pieninä. Yksi iso arvo (megatavuja) pysäyttää
  yksisäikeisen palvelimen siirron ajaksi kaikilta muilta.
- Putkita, kun lähetät monta komentoa. Edestakaisten matkojen määrä on
  usein Redis-koodin suurin hidaste.
- Asenna `maxmemory` ja poistopolitiikka tietoisesti: välimuistissa
  poistetaan vanhaa, pysyvässä datassa ei.

## Itsearviointi

- Osaat valita Redisin tietorakenteen laskurille, oliolle,
  aikajärjestetylle historialle ja tulostaululle.
- Osaat käyttää elinaikaa istunnoissa ja kertoa, mitä `TTL`:n
  arvot `-1` ja `-2` tarkoittavat.
- Osaat selittää, miksi putkitus nopeuttaa ja miksi se ei tee
  komennoista atomisia.
- Osaat kertoa, miksi Redisin yksittäiset komennot ovat atomisia.
