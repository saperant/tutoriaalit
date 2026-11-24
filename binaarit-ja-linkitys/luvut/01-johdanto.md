# Johdanto {.runko-johdanto}

Kääntäjän työ loppuu objektitiedostoon. Sen jälkeen kaksi ohjelmaa,
joita harva kutsuu nimeltä, tekee loput: *linkkeri* yhdistää
objektitiedostot ja kirjastot yhdeksi ohjelmaksi, ja *lataaja*
(dynaaminen linkkeri) sijoittaa ohjelman muistiin, hakee sen jaetut
kirjastot ja korjaa osoitteet ennen kuin `main` saa vuoron. Useimmiten
tämä kaikki toimii näkymättömästi. Kun se ei toimi, virheilmoitus on
lyhyt ja lähdekoodista ei löydy vikaa:

- `undefined reference to 'keskiarvo'`, vaikka funktio on kirjastossa
- `error while loading shared libraries: libfoo.so.1: cannot open
  shared object file`, vaikka tiedosto on levyllä
- `multiple definition of 'koontinumero'` vanhassa koodissa, joka
  kääntyi ennen kääntäjän päivitystä
- ohjelma toimii väärin vasta, kun jaettu kirjasto päivitetään, vaikka
  kukaan ei kääntänyt sitä uudelleen
- kaatumisilmoitus kertoo vain osoitteen, ja asennetusta ohjelmasta
  puuttuvat rivinumerot.

Kaikki nämä selviävät, kun tietää, mitä objektitiedostossa on, miten
linkkeri valitsee symbolit ja mitä lataaja tekee käynnistyksessä.
Samat tiedot ovat pohjana sulautettujen järjestelmien muistikartoille,
takaisinmallinnukselle ja haavoittuvuuksien ymmärtämiselle: palautukseen
suuntautuneet hyökkäykset, GOT-taulun ylikirjoitus ja `LD_PRELOAD`
-kaappaus ovat linkityksen mekanismeja väärissä käsissä.

## Mitä tutoriaali kattaa

Tutoriaali käsittelee Linuxin ELF-muotoa (*Executable and Linkable
Format*) x86-64-arkkitehtuurilla ja GNU-työkaluilla: GCC, GNU
binutils (`ld`, `as`, `readelf`, `objdump`, `nm`, `ar`, `objcopy`,
`strip`, `addr2line`) ja glibc:n dynaaminen linkkeri `ld.so`. Samat
käsitteet pätevät muihinkin ympäristöihin: BSD-järjestelmät ja
useimmat sulautetut työkaluketjut käyttävät ELF:ää, macOS:n Mach-O ja
Windowsin PE/COFF ratkaisevat samat ongelmat eri nimillä.

| Luku | Aihe | Esimerkit |
|------|------|-----------|
| 2 | Käännöksestä ohjelmaksi | vaiheet, objektitiedoston tyyppi |
| 3 | ELF-tiedoston rakenne | osiot, segmentit, oikeudet |
| 4 | Symbolit | paikallinen, globaali, heikko |
| 5 | Relokaatiot | paikat, jotka linkkeri täyttää |
| 6 | Staattinen linkitys | arkistot, järjestys, kaksoismäärittely |
| 7 | Jaetut kirjastot | hakupolut, `RUNPATH`, `$ORIGIN` |
| 8 | Paikkariippumaton koodi | GOT, PLT, näkyvyys, sidonta |
| 9 | Kirjastojen versiointi | soname, symboliversiot |
| 10 | Symbolien sidonta ajossa | törmäykset, `LD_PRELOAD` |
| 11 | Linkkeriskriptit | omat osiot, muistikartta, rekisteri |
| 12 | Ohjelman käynnistys | `ld.so`, `_start`, alustukset |
| 13 | ABI | tyypit, asettelu, C++:n nimet |
| 14 | Virheenjäljitystieto | DWARF, `addr2line`, `strip` |
| 15 | Lopuksi | nyrkkisäännöt, lähteet |

Luvut 2–6 käsittelevät yhtä objektitiedostoa ja sen linkittämistä
ohjelmaksi, luvut 7–10 jaettuja kirjastoja ja luvut 11–14 linkityksen
hallintaa, käynnistystä ja binäärirajapintaa.

## Esitiedot ja jatkotaidot

Esitiedoiksi oletetaan *Assembly*: rekisterit, kutsukonventio, pino ja
x86-64:n osoitusmuodot, koska konekielen lukeminen on tämän
tutoriaalin perustyökalu. C-kielen osoittimet, rakenteet ja erillinen
kääntäminen oletetaan tutuiksi. Rinnakkainen taito *Rakennus ja
testaus* käsittelee samaa aihetta rakennusjärjestelmän näkökulmasta
(Make, CMake, riippuvuudet); tämä tutoriaali kertoo, mitä
rakennusjärjestelmän ajamat komennot tekevät.

Jatkotaitoja ovat *Mikrokontrollerit* (linkkeriskriptit ja
käynnistyskoodi ilman käyttöjärjestelmää), *Takaisinmallinnus*
(binäärien lukeminen ilman lähdekoodia) ja *Haavoittuvuudet*
(muistiturvallisuus, suojaukset kuten RELRO, PIE ja pinon suojaus).

## Työkalut ja esimerkit

Esimerkit on tehty Ubuntu 24.04:llä: GCC 14, binutils 2.42 ja glibc
2.39. Kehityskontti (`.devcontainer/binaarit-ja-linkitys`) sisältää
samat työkalut. Jokainen esimerkki on hakemisto `esimerkit/NN-nimi/`,
jossa on lähdekoodi ja skripti `aja.sh`. Skripti kääntää, linkittää,
tutkii tulokset ja ajaa ohjelmat; tutoriaalissa näytetyt komennot ja
tulosteet ovat näistä skripteistä. Tulosteet ovat sellaisenaan
tiedostoissa `odotettu`, ja testi vertaa jokaista ajoa niihin:

```text
make -C esimerkit          # ajaa kaikki esimerkit ja vertaa tulosteet
make -C esimerkit siivoa   # poistaa käännöstulokset
```

Kaikki skriptit lukevat tiedoston `yhteinen.sh`. Se asettaa kääntäjän
ja valitsimet (`-std=c17 -O2 -Wall -Wextra -Werror`) ja määrittelee
kaksi apufunktiota: `symbolit` tulostaa valittujen symbolien tyypit
`nm`:n tulosteesta, ja `virherivi` ajaa komennon, jonka odotetaan
epäonnistuvan, ja poimii linkkerin virheilmoituksesta sen olennaisen
osan:

```{.bash tiedosto="esimerkit/yhteinen.sh"}
```

Osoitteet, tiivisteet ja väliaikaisten tiedostojen nimet vaihtelevat
koneittain ja ajokerroittain. Siksi skriptit suodattavat tulosteista
kiinnostavat kentät ja korvaavat vaihtelevat osoitteet merkinnöillä,
kuten `SIIRTYMA` ja `OSOITE`. Omassa työssä komennot kannattaa ajaa
ilman suodatusta: kokonainen tuloste näyttää enemmän kuin tässä on
tilaa esittää.

> Ubuntun GCC kääntää oletuksena paikkariippumattoman ohjelman (PIE),
> sitoo symbolit käynnistyksessä (`-z now`) ja korvaa muotoilufunktiot
> tarkistavilla versioilla (`_FORTIFY_SOURCE`). Muissa jakeluissa
> oletukset voivat erota, ja tulosteet näyttävät silloin hieman
> erilaisilta. Tutoriaali kertoo kunkin oletuksen kohdalla, mistä se
> johtuu.
