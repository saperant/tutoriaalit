# Esikääntäjä ja ohjelman jakaminen tiedostoihin {.runko-modulit}

## Esikääntäjä

Esikääntäjä käsittelee lähdekoodin ennen varsinaista kääntämistä. Se
toimii tekstin tasolla eikä tunne C:n tyyppejä tai näkyvyysalueita.
Sen direktiivit alkavat merkillä `#`.

### Makrot

`#define` määrittelee makron, jonka esiintymät korvataan sen
määrittelyllä. Parametrillinen makro näyttää funktiolta, mutta se on
pelkkää tekstin korvausta. Siksi parametrit ja koko lauseke on
suljettava sulkeisiin:

```{.c tiedosto="esimerkit/09-makrot.c" osa="sudenkuoppa"}
```

`NELIO_VAARIN(1 + 2)` laajenee muotoon `1 + 2 * 1 + 2`, jonka arvo on
5. Sulkeetkaan eivät auta, jos argumentilla on sivuvaikutuksia:
`NELIO(i++)` kasvattaisi muuttujaa kahdesti. Vakioille on parempi
käyttää `constexpr`-määrittelyä tai luetteloa ja pienille funktioille
`static inline` -funktioita. Makroja tarvitaan silti tilanteissa,
joihin funktiot eivät pysty.

Operaattori `#` muuttaa makron argumentin merkkijonoksi. Valmiit makrot
`__LINE__` ja `__FILE__` kertovat rivin ja tiedoston, ja `__func__`
on funktion nimi. Usean lauseen makro kääritään
`do { ... } while (0)` -rakenteeseen, jotta se käyttäytyy kuten yksi
lause myös `if`–`else`-rakenteessa. Rivin lopun `\` jatkaa makroa
seuraavalle riville.

```{.c tiedosto="esimerkit/09-makrot.c" osa="erikoiset"}
```

C11:n `_Generic` valitsee lausekkeen argumentin tyypin perusteella. Sen
avulla voi kirjoittaa makroja, jotka toimivat eri tyypeillä, kuten
`<tgmath.h>`-otsikon matemaattiset funktiot:

```{.c tiedosto="esimerkit/09-makrot.c" osa="generic"}
```

### Ehdollinen kääntäminen

`#if`, `#ifdef`, `#ifndef`, `#else` ja `#endif` valitsevat, mitkä
koodirivit käännetään. Niillä tehdään alustakohtaisia toteutuksia ja
käännösaikaisia asetuksia. Makron voi määritellä myös komentorivillä:
`gcc -DLOKITASO=2` ottaisi alla debug-tulosteet käyttöön.

```{.c tiedosto="esimerkit/09-makrot.c" osa="ehdollinen"}
```

```{.c tiedosto="esimerkit/09-makrot.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-makrot.odotettu"}
```

Tämän tutoriaalin testit käyttävät samaa tekniikkaa: virheelliset
esimerkit korjataan makrolla `-DKORJATTU`.

## Monen tiedoston ohjelmat

Suuremmat ohjelmat jaetaan *käännösyksiköihin*: jokainen `.c`-tiedosto
käännetään erikseen objektitiedostoksi, ja linkittäjä yhdistää ne.
Jotta tiedosto voi kutsua toisen tiedoston funktiota, sen on nähtävä
funktion esittely. Esittelyt kootaan *otsikkotiedostoon* (`.h`), joka
liitetään `#include`-direktiivillä sekä toteutukseen että käyttäjiin.

Esimerkkinä on pino, jonka rajapinta on otsikkotiedostossa:

```{.c tiedosto="esimerkit/09-pino/pino.h"}
```

Otsikkotiedosto suojataan *include-vartijalla* (`#ifndef PINO_H`), jotta
sen liittäminen useampaan kertaan samaan käännösyksikköön ei aiheuta
virheitä.

Rakenteen `struct pino` kenttiä ei esitellä otsikossa. Käyttäjä näkee
vain *epätäydellisen tyypin*, jota se voi käsitellä osoittimen kautta
mutta jonka kenttiin se ei pääse. Tämä on C:n tapa kapseloida
toteutus: pinon sisäistä rakennetta voi muuttaa ilman, että käyttäjien
koodia tarvitsee muuttaa tai edes kääntää uudelleen.

Toteutus määrittelee rakenteen ja funktiot. Apufunktio `kasvata` on
`static`, joten se ei näy muihin tiedostoihin eikä sen nimi voi
törmätä muiden tiedostojen nimiin.

```{.c tiedosto="esimerkit/09-pino/pino.c"}
```

Käyttäjä tuntee vain rajapinnan:

```{.c tiedosto="esimerkit/09-pino/main.c"}
```

```{.tuloste tiedosto="esimerkit/09-pino.odotettu"}
```

Ohjelma käännetään antamalla kääntäjälle molemmat lähdetiedostot:

```text
gcc-14 -std=c23 -Wall -Wextra main.c pino.c -o pino
```

Suuremmissa projekteissa kukin tiedosto käännetään erikseen
(`gcc -c pino.c`) ja vain muuttuneet tiedostot käännetään uudelleen.
Tätä varten käytetään käännösjärjestelmää, kuten Makea tai CMakea.

Otsikkotiedostoon kirjoitetaan vain esittelyjä: funktioiden
prototyyppejä, tyyppejä, makroja ja `extern`-esittelyjä globaaleista
muuttujista. Jos otsikkotiedostossa olisi funktion määrittely, se
syntyisi jokaiseen sen liittävään käännösyksikköön, ja linkitys
epäonnistuisi päällekkäisiin määrittelyihin. Poikkeus ovat
`static inline` -funktiot.

## X-makrot

Usein sama luettelo tarvitaan useassa muodossa: luettelotyyppinä,
tekstitaulukkona ja ehkä nimien taulukkona. Jos luettelo kirjoitetaan
monta kertaa, kopiot joutuvat ajan mittaan epäsynkroniin. *X-makrossa*
luettelo kirjoitetaan kerran makroksi, joka ottaa parametrina toisen
makron. Kukin käyttökohta määrittelee, mitä jokaisesta alkiosta tuotetaan.

```{.c tiedosto="esimerkit/09-xmakrot.c" osa="xmakro"}
```

```{.c tiedosto="esimerkit/09-xmakrot.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-xmakrot.odotettu"}
```

Operaattori `##` liittää kaksi merkkijonoa yhdeksi tunnisteeksi
(`VIRHE_##nimi` → `VIRHE_OK`), ja `static_assert` varmistaa
käännösaikana, että taulukossa on teksti jokaiselle arvolle.

## Käytännössä

- **Otsikkotiedosto on julkinen rajapinta.** Siinä on vain se, mitä
  käyttäjä tarvitsee, ja se kääntyy itsenäisesti: se liittää itse kaikki
  tarvitsemansa otsikot. Toteutustiedosto liittää oman otsikkonsa
  ensimmäisenä, kuten `pino.c`, jolloin puuttuvat liitokset paljastuvat
  heti.
- **Etuliite korvaa nimiavaruuden.** Kaikki julkiset nimet alkavat
  moduulin nimellä (`pino_luo`, `pino_lisaa`), jottei kahden kirjaston
  nimet törmää.
- **Läpinäkymätön tyyppi ja luonti- ja tuhoamisfunktio** kapseloivat
  toteutuksen. Rakenteen kenttiä voi muuttaa rikkomatta käyttäjien
  binäärejä.
- **Makro vain, kun funktio ei riitä.** Makroja tarvitaan, kun koodin on
  tiedettävä lähdetiedosto ja rivi (`__FILE__`, `__LINE__`), kun
  tarvitaan merkkijonoksi muuttamista tai tunnisteiden liittämistä, tai
  kun luettelo halutaan pitää yhtenäisenä (X-makro).
- **Ehdollinen kääntäminen keskitetysti.** Alustakohtaiset erot kootaan
  yhteen otsikkoon tai omiin toteutustiedostoihin sen sijaan, että
  `#ifdef`-lohkoja olisi kaikkialla.
- **Riippuvuudet.** C:llä ei ole standardia paketinhallintaa.
  Kirjastot löydetään `pkg-config`illa tai järjestelmän paketeista,
  ristiinkäännöksissä usein vcpkg:llä tai Conanilla. Yksitiedostoiset
  kirjastot (esimerkiksi stb-sarja) liitetään lähdekoodina.

## Itsearviointi

- Osaat jakaa ohjelman otsikko- ja toteutustiedostoihin ja kääntää sen.
- Osaat kapseloida tietorakenteen läpinäkymättömällä tyypillä.
- Osaat kirjoittaa turvallisen makron ja tunnistaa kaksoisevaluoinnin
  vaaran.
- Osaat pitää luettelon ja sen tekstit synkronissa X-makrolla.
