# Esikääntäjä ja ohjelman jakaminen tiedostoihin

## Esikääntäjä

Esikääntäjä käsittelee lähdekoodin ennen varsinaista kääntämistä. Se
toimii tekstin tasolla eikä tunne C:n tyyppejä tai näkyvyysalueita.
Sen direktiivit alkavat merkillä `#`.

### Makrot

`#define` määrittelee makron, jonka esiintymät korvataan sen
määrittelyllä. Parametrillinen makro näyttää funktiolta, mutta se on
pelkkää tekstin korvausta. Siksi parametrit ja koko lauseke on
suljettava sulkeisiin:

```{.c tiedosto="esimerkit/08-makrot.c" osa="sudenkuoppa"}
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

```{.c tiedosto="esimerkit/08-makrot.c" osa="erikoiset"}
```

C11:n `_Generic` valitsee lausekkeen argumentin tyypin perusteella. Sen
avulla voi kirjoittaa makroja, jotka toimivat eri tyypeillä, kuten
`<tgmath.h>`-otsikon matemaattiset funktiot:

```{.c tiedosto="esimerkit/08-makrot.c" osa="generic"}
```

### Ehdollinen kääntäminen

`#if`, `#ifdef`, `#ifndef`, `#else` ja `#endif` valitsevat, mitkä
koodirivit käännetään. Niillä tehdään alustakohtaisia toteutuksia ja
käännösaikaisia asetuksia. Makron voi määritellä myös komentorivillä:
`gcc -DLOKITASO=2` ottaisi alla debug-tulosteet käyttöön.

```{.c tiedosto="esimerkit/08-makrot.c" osa="ehdollinen"}
```

```{.c tiedosto="esimerkit/08-makrot.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/08-makrot.odotettu"}
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

```{.c tiedosto="esimerkit/08-pino/pino.h"}
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

```{.c tiedosto="esimerkit/08-pino/pino.c"}
```

Käyttäjä tuntee vain rajapinnan:

```{.c tiedosto="esimerkit/08-pino/main.c"}
```

```{.tuloste tiedosto="esimerkit/08-pino.odotettu"}
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
