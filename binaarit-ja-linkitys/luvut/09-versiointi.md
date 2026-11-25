# Kirjastojen versiointi

Jaetun kirjaston etu on, että sen voi päivittää ilman ohjelmien
uudelleenlinkitystä. Etu muuttuu riskiksi, kun päivitys muuttaa
*binäärirajapintaa* (ABI): ohjelma on käännetty olettaen tietyt
funktiot, rakenteiden asettelun ja käytöksen, ja uusi kirjasto ei
enää täytä oletuksia. Lähdekoodi voi kääntyä ennallaan, vaikka
binäärinen yhteensopivuus on rikki. ELF tarjoaa kaksi mekanismia:
*soname* versioi koko kirjaston, *symboliversiot* yksittäiset
funktiot.

## Soname ja kolme nimeä

Kirjastolla on kolme nimeä, joista kaksi on symbolisia linkkejä:

| Nimi | Esimerkki | Käyttäjä |
|------|-----------|----------|
| todellinen nimi | `libasetukset.so.1.1` | tiedosto levyllä |
| soname | `libasetukset.so.1` | dynaaminen linkkeri ajossa |
| linkityksen nimi | `libasetukset.so` | linkkeri, `-lasetukset` |

Soname tallennetaan kirjastoon linkkerin valitsimella `-soname`.
Kun ohjelma linkitetään kirjastoa vasten, linkkeri kopioi
`NEEDED`-merkintään sonamen, ei tiedoston nimeä. Ajossa lataaja etsii
siis `libasetukset.so.1`:tä, ja symbolinen linkki osoittaa siihen
versioon, joka on asennettu. Linkityksen nimeä tarvitaan vain
kehityksessä, ja jakelut pakkaavat sen kehityspakettiin (`-dev`).

Esimerkin kirjasto täyttää asetusrakenteen oletusarvoilla:

```{.c tiedosto="esimerkit/09-soname/v1/asetukset.h"}
```

```{.c tiedosto="esimerkit/09-soname/asetukset.c"}
```

Skriptin apufunktio `kirjasto` kääntää kirjaston annetulla otsakkeella
ja versiolla ja asettaa sonamen:

```{.bash tiedosto="esimerkit/09-soname/aja.sh" osa="v1"}
```

Yhteensopiva korjausversio 1.1 vaihtaa vain linkin kohteen. Ohjelmaa
ei linkitetä uudelleen:

```{.bash tiedosto="esimerkit/09-soname/aja.sh" osa="v11"}
```

## Kun ABI muuttuu

Versiossa 2 rakenteen kenttien järjestys vaihtui. Muutos näyttää
harmittomalta: lähdekoodi, joka käyttää kenttiä nimillä, kääntyy
ennallaan.

```{.c tiedosto="esimerkit/09-soname/v2/asetukset.h"}
```

Jos kehittäjä unohtaa vaihtaa sonamen, vanha ohjelma lataa uuden
kirjaston, ja kirjasto kirjoittaa kentät eri järjestyksessä kuin
ohjelma ne lukee:

```{.bash tiedosto="esimerkit/09-soname/aja.sh" osa="rikki"}
```

Oikein tehtynä uusi versio saa uuden sonamen. Molemmat versiot ovat
asennettuina rinnakkain, vanhat ohjelmat käyttävät versiota 1 ja
uudet versiota 2:

```{.bash tiedosto="esimerkit/09-soname/aja.sh" osa="oikein"}
```

```{.tuloste tiedosto="esimerkit/09-soname/odotettu"}
```

Virheellinen tulos (`nopeus 5 mm/s, tarkkuus 120 um`) ei kaada
ohjelmaa eikä tuota virheilmoitusta. Väärät arvot kulkevat eteenpäin
hiljaa, mikä on ABI-rikon tyypillinen oire.

## Mikä rikkoo ABI:n

| Muutos | ABI | Huomioita |
|--------|-----|-----------|
| uusi funktio | säilyy | vanhat ohjelmat eivät käytä sitä |
| funktion poisto tai uudelleennimeäminen | rikkoo | `undefined symbol` käynnistyksessä tai kutsussa |
| parametrin tyypin tai paluuarvon muutos | rikkoo | ei virheilmoitusta, väärät arvot |
| rakenteen kentän lisäys, poisto tai siirto | rikkoo | jos käyttäjä varaa rakenteen tai lukee kenttiä |
| `enum`-arvojen uudelleennumerointi | rikkoo | vanhat arvot tarkoittavat eri asioita |
| makron tai `inline`-funktion muutos | rikkoo | vanha toteutus on käännetty ohjelmiin |
| C++: virtuaalifunktion lisäys | rikkoo | vtablen asettelu muuttuu |
| sisäisen, piilotetun funktion muutos | säilyy | ei näy rajapinnassa |

Kaksi suunnittelutapaa vähentää rikkoja. *Läpinäkymätön tyyppi*:
otsake esittelee vain `struct asetukset;`, ja kirjasto varaa ja
käsittelee rakenteen funktioiden kautta, joten kenttiä voi muuttaa
vapaasti. *Varatut kentät ja kokokenttä*: rakenteen alussa on sen
koko, jonka kutsuja asettaa (`a.koko = sizeof a`), jolloin kirjasto
tunnistaa, minkä version rakenteen kutsuja tuntee. Windowsin ja
Linuxin ytimen rajapinnat käyttävät jälkimmäistä.

Libabigail-projektin `abidiff` vertaa kahden kirjastoversion ABI:a
virheenjäljitystiedon perusteella ja raportoi muutokset, ja se sopii
jatkuvan integraation tarkistukseksi.

## Symboliversiot

Soname on karkea: jokainen rikko vaatii koko kirjaston uuden
version, ja kaikki ohjelmat on käännettävä uudelleen. glibc ei ole
vaihtanut sonameaan (`libc.so.6`) vuosikymmeniin, vaikka sen
funktioiden käytös on muuttunut. Keino on *symboliversiointi*: sama
funktio voi olla kirjastossa useana versiona, ja jokainen ohjelma
sidotaan siihen versioon, jota vasten se linkitettiin.

Esimerkin kirjaston ensimmäinen versio vertaa käyttäjätunnuksia
kirjainkoosta välittämättä:

```{.c tiedosto="esimerkit/09-versiointi/tunnus-v1.c"}
```

```{.c tiedosto="esimerkit/09-versiointi/main.c"}
```

Versioskripti antaa viedyille symboleille version ja piilottaa muut
(`local: *;`):

```{.text tiedosto="esimerkit/09-versiointi/tunnus-v1.map"}
```

```{.bash tiedosto="esimerkit/09-versiointi/aja.sh" osa="v1"}
```

Toinen versio muuttaa vertailun kirjainkoon huomioivaksi. Vanha
toteutus säilyy versiona `TUNNUS_1`, uusi on oletusversio `TUNNUS_2`
(kaksi `@`-merkkiä):

```{.c tiedosto="esimerkit/09-versiointi/tunnus-v2.c" osa="versiot"}
```

```{.text tiedosto="esimerkit/09-versiointi/tunnus-v2.map" osa="kartta"}
```

```{.bash tiedosto="esimerkit/09-versiointi/aja.sh" osa="v2"}
```

```{.tuloste tiedosto="esimerkit/09-versiointi/odotettu"}
```

Kirjaston dynaamisessa symbolitaulussa on nyt kaksi versiota samasta
nimestä. Ohjelmaan tallentuu nimen lisäksi versio: `vanha` pyytää
`vertaa_tunnus@TUNNUS_1` ja saa vanhan käytöksen ilman
uudelleenlinkitystä, `uusi` linkitettiin versiota 2 vasten ja pyytää
`@TUNNUS_2`. Versioskriptin `TUNNUS_2 { ... } TUNNUS_1;` kertoo, että
versio 2 periytyy versiosta 1.

Attribuutti `symver` on GCC 10:n lisäys; vanhemmassa koodissa sama
tehdään assembly-direktiivillä `__asm__(".symver vertaa_tunnus_v1,
vertaa_tunnus@TUNNUS_1");`. Ohjelman tarvitsemat versiot näkyvät
komennolla `readelf -V ohjelma` tai `objdump -T ohjelma`.

> Symboliversiot selittävät tutun virheen `version 'GLIBC_2.38' not
> found`. Ohjelma linkitettiin uudemman glibc:n kanssa ja sidottiin sen
> uusimpiin funktioversioihin, joita vanhemmassa järjestelmässä ei ole.
> Siirrettävät ohjelmat käännetään siksi vanhimmalla tuettavalla
> järjestelmällä, kuten `manylinux`-konteissa.

## Käytännössä

- **Anna jokaiselle jaetulle kirjastolle soname.** Vaihda pääversio,
  kun ABI rikkoutuu, ja pidä se, kun muutos on yhteensopiva. Älä sido
  sonamea ohjelmiston markkinointiversioon.
- **Suunnittele rajapinta muuttuvaksi.** Läpinäkymättömät tyypit ja
  rakenteen kokokenttä antavat lisätä kenttiä rikkomatta ABI:a.
- **Käytä versioskriptiä aina**, vaikka kirjastolla olisi vain yksi
  versio: `local: *;` piilottaa kaiken, mitä ei ole lueteltu, ja
  myöhemmät versiot voidaan lisätä yhteensopivasti.
- **Tarkista ABI automaattisesti.** Vertaa julkaisuehdokasta
  edelliseen versioon `abidiff`:llä ja `nm -D --defined-only`:lla.

## Itsearviointi

- Osaat selittää kirjaston todellisen nimen, sonamen ja linkityksen
  nimen roolit ja luoda ne.
- Osaat tunnistaa muutokset, jotka rikkovat ABI:n, vaikka lähdekoodi
  kääntyy ennallaan.
- Osaat päättää, milloin soname vaihdetaan, ja kertoa, miksi
  unohdettu vaihto aiheuttaa hiljaisia virheitä.
- Osaat kirjoittaa versioskriptin ja tarjota funktiosta kaksi
  versiota `symver`-attribuutilla.
- Osaat selittää virheen `version 'GLIBC_x' not found` ja sen
  välttämisen.
