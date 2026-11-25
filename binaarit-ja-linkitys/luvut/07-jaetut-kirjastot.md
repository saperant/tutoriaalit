# Jaetut kirjastot ja hakupolut

Jaettu kirjasto (`libnimi.so`, *shared object*) linkitetään ohjelmaan
vasta käynnistyksessä. Linkityksen aikana linkkeri vain tarkistaa,
että kirjasto määrittelee tarvittavat symbolit, ja kirjoittaa
ohjelmaan riippuvuuden. Käynnistyksessä dynaaminen linkkeri
(`ld.so`) etsii kirjaston, kartoittaa sen muistiin ja yhdistää
symbolit. Kaksi vaihetta etsii kirjastoa eri paikoista, ja se on
jaettujen kirjastojen yleisimmän virheen syy.

## Kirjasto ja sen käyttäjä

Esimerkin kirjasto muuntaa lämpötiloja. Se asennetaan
asennushakemiston rakenteeseen `lib/` ja `bin/`, kuten paketit
yleensä:

```{.c tiedosto="esimerkit/07-jaettu/yksikot.c"}
```

```{.bash tiedosto="esimerkit/07-jaettu/aja.sh" osa="rakennus"}
```

`-fPIC` kääntää paikkariippumatonta koodia (luku 8) ja `-shared`
linkittää jaetun kirjaston. Ohjelman linkityksessä `-L` kertoo
*linkkerille*, mistä `-lyksikot` löytyy. Ohjelmaan tallentuu
riippuvuus dynaamiseen osioon (`readelf -d`) merkintänä `NEEDED`,
mutta ei hakemistoa:

```{.tuloste tiedosto="esimerkit/07-jaettu/odotettu" alkaen="== riippuvuudet" asti="libc.so.6"}
```

## Miksi kirjastoa ei löydy

`-L` vaikuttaa vain linkitykseen. Käynnistyksessä `ld.so` ei tiedä
siitä mitään:

```{.bash tiedosto="esimerkit/07-jaettu/aja.sh" osa="ilman"}
```

```{.tuloste tiedosto="esimerkit/07-jaettu/odotettu" alkaen="== ajo ilman hakupolkua" asti="not found"}
```

Virheilmoitus on kokonaisuudessaan `error while loading shared
libraries: libyksikot.so: cannot open shared object file: No such
file or directory`. `ldd` kertoo saman ennen ajoa: `not found`.

Dynaaminen linkkeri etsii kirjastoa tässä järjestyksessä:

| Järjestys | Lähde | Huomioita |
|-----------|-------|-----------|
| 1 | `DT_RPATH` ohjelmassa | vain jos `DT_RUNPATH` puuttuu; vanhentunut |
| 2 | `LD_LIBRARY_PATH` | ympäristömuuttuja, ei setuid-ohjelmissa |
| 3 | `DT_RUNPATH` ohjelmassa tai kirjastossa | koskee vain sen omia suoria riippuvuuksia |
| 4 | `/etc/ld.so.cache` | `ldconfig` kokoaa `/etc/ld.so.conf`:sta |
| 5 | `/lib`, `/usr/lib` ja arkkitehtuurin hakemistot | oletuspolut |

Jos riippuvuuden nimessä on vinoviiva (`./libx.so`), hakua ei tehdä,
vaan nimi on polku. Linkkeri tallentaa sellaisen nimen, jos kirjasto
annetaan polkuna eikä sillä ole sonamea (luku 9).

## Kolme tapaa kertoa sijainti

**Ympäristömuuttuja** `LD_LIBRARY_PATH` sopii kehitykseen ja testeihin:

```{.bash tiedosto="esimerkit/07-jaettu/aja.sh" osa="ymparisto"}
```

```{.tuloste tiedosto="esimerkit/07-jaettu/odotettu" alkaen="== LD_LIBRARY_PATH" asti="yksikot 1.0"}
```

Tuotannossa se on huono ratkaisu. Se vaikuttaa kaikkiin ohjelmiin,
jotka perivät ympäristön, ohittaa järjestelmän kirjastot ja on
helppo unohtaa käynnistysskriptistä.

**Järjestelmän hakupolku**: kirjasto asennetaan oletuspolkuun tai
hakemisto lisätään tiedostoon `/etc/ld.so.conf.d/oma.conf`, ja
`ldconfig` päivittää välimuistin. Tämä on jakelupakettien tapa.

**`RUNPATH` ohjelmassa**: linkkerin valitsin `-rpath` tallentaa
hakupolun ohjelmaan. Erikoismuuttuja `$ORIGIN` tarkoittaa ohjelman
omaa hakemistoa, joten polku voi olla suhteellinen asennukseen:

```{.bash tiedosto="esimerkit/07-jaettu/aja.sh" osa="runpath"}
```

```{.tuloste tiedosto="esimerkit/07-jaettu/odotettu" alkaen="== RUNPATH ohjelman sijainnin mukaan"}
```

`$ORIGIN/../lib` löytää kirjaston, vaikka koko asennushakemisto
siirretään. Tämä on oikea tapa jakaa sovellusta, joka tuo omat
kirjastonsa, kuten työpöytäsovellukset ja ohjelmistotyökalut.
Kuoressa `$ORIGIN` on lainattava, jotta kuori ei laajenna sitä;
Makefilessä se kirjoitetaan `'$$ORIGIN/../lib'` ja CMakessa
`$ORIGIN` suoraan (`BUILD_RPATH`, `INSTALL_RPATH`).

## RPATH ja RUNPATH

Valitsin `-rpath` tuottaa nykyisillä linkkereillä merkinnän
`DT_RUNPATH`. Vanha `DT_RPATH` (`-Wl,--disable-new-dtags`) erosi
kahdella tavalla: se haetaan *ennen* `LD_LIBRARY_PATH`:ia, joten
käyttäjä ei voi ohittaa sitä, ja se periytyy kirjastojen
riippuvuuksiin. `DT_RUNPATH` koskee vain sen tiedoston omia suoria
riippuvuuksia: jos `libyksikot.so` tarvitsisi kirjastoa
`libapu.so`, sen hakupolku tulisi `libyksikot.so`:n omasta
`RUNPATH`:sta, ei ohjelman.

Käytännössä jokainen jaettu kirjasto, joka tarvitsee toista
sovelluksen omaa kirjastoa, linkitetään omalla
`-rpath,'$ORIGIN'`-polullaan. Valmiin tiedoston polun voi muuttaa
työkalulla `patchelf --set-rpath '$ORIGIN/../lib' ohjelma`.

Setuid-ohjelmissa (`AT_SECURE`) `ld.so` jättää `LD_LIBRARY_PATH`:n
huomiotta ja hyväksyy `$ORIGIN`-polut vain luotetuista hakemistoista,
koska muuten käyttäjä voisi ladata oman koodinsa korotetuin
oikeuksin.

## Mitä lataaja tekee

`LD_DEBUG` näyttää dynaamisen linkkerin toiminnan. Arvo `libs`
kertoo jokaisen hakupolun, jota yritettiin, ja `help` luettelee
kaikki vaihtoehdot:

```text
LD_DEBUG=libs ./ohjelma           # mistä kirjastoja etsittiin
LD_DEBUG=bindings ./ohjelma       # mihin kirjastoon kukin symboli sidottiin
LD_DEBUG=files,versions ./ohjelma # mitkä tiedostot ja versiot ladattiin
LD_DEBUG_OUTPUT=loki ./ohjelma    # tulosteet tiedostoon loki.PID
```

`ldd ohjelma` tulostaa riippuvuudet ja polut, joista ne löytyisivät.
Se toimii ajamalla dynaamisen linkkerin erikoistilassa, joten
epäluotettavalle tiedostolle käytetään `readelf -d`:tä tai
`objdump -p`:tä, jotka vain lukevat. Riippuvuuspuun näkee
`lddtree`-työkalulla tai toistamalla `readelf -d` jokaiselle
`NEEDED`-merkinnälle.

## Käytännössä

- **Älä jätä `LD_LIBRARY_PATH`:ia tuotantoon.** Käytä
  järjestelmäasennukseen `ldconfig`-polkuja ja sovelluksen omiin
  kirjastoihin `RUNPATH`:ia polulla `$ORIGIN`.
- **Älä tallenna rakennushakemiston polkua.** Absoluuttinen polku
  `/home/kehittaja/build/lib` toimii vain kehittäjän koneella ja voi
  olla tietoturvariski, jos hakemisto on muiden kirjoitettavissa.
  CMake vaihtaa polun asennuksessa (`INSTALL_RPATH`).
- **Aloita vianetsintä `ldd`:llä ja `LD_DEBUG=libs`:llä.** Ne
  kertovat heti, puuttuuko kirjasto vai löytyykö väärä versio.
- **Tarkista riisuttu asennus.** `readelf -d ohjelma` näyttää
  `NEEDED`-, `RUNPATH`- ja `SONAME`-merkinnät, jotka määräävät
  käynnistyksen.

## Itsearviointi

- Osaat selittää, miksi `-L` ei auta ajonaikaisessa haussa ja miten
  `NEEDED`-merkintä syntyy.
- Osaat luetella dynaamisen linkkerin hakujärjestyksen ja valita
  tilanteeseen sopivan tavan kertoa kirjaston sijainti.
- Osaat käyttää `$ORIGIN`-polkua siirrettävässä asennuksessa ja
  kirjoittaa sen oikein kuoressa ja Makefilessä.
- Osaat kertoa `RPATH`:n ja `RUNPATH`:n eron ja sen, miksi setuid-ohjelmat
  rajoittavat hakupolkuja.
- Osaat tutkia latausta `ldd`:llä, `readelf -d`:llä ja `LD_DEBUG`:lla.
