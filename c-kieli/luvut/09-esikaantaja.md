# Esikääntäjä ja ohjelman jakaminen tiedostoihin {.runko-modulit}

Tähän asti jokainen ohjelma on ollut yhdessä tiedostossa. Tässä luvussa
ohjelma jaetaan moduuleihin, joilla on julkinen rajapinta ja kätketty
toteutus. C:ssä jako nojaa esikääntäjään, joka liittää
otsikkotiedostot lähdekoodiin, joten luku alkaa siitä. Lopuksi
rajapinnasta tehdään vaihdettava funktio-osoittimien avulla.

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

### X-makrot

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

Operaattori `##` liittää kaksi sanasta yhdeksi tunnisteeksi
(`VIRHE_##nimi` → `VIRHE_OK`), ja `static_assert` varmistaa
käännösaikana, että taulukossa on teksti jokaiselle arvolle.

## Monen tiedoston ohjelmat

Suuremmat ohjelmat jaetaan *käännösyksiköihin*: jokainen `.c`-tiedosto
käännetään erikseen objektitiedostoksi, ja linkittäjä yhdistää ne.
Jotta tiedosto voi kutsua toisen tiedoston funktiota, sen on nähtävä
funktion esittely. Esittelyt kootaan *otsikkotiedostoon* (`.h`), joka
liitetään `#include`-direktiivillä sekä toteutukseen että käyttäjiin.

```{.dot otsikko="Kahden käännösyksikön ohjelma. Kumpikin lähdetiedosto liittää otsikon ja käännetään erikseen; linkittäjä yhdistää objektitiedostot ja kirjastot ohjelmaksi."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.45;
  h [label="pino.h"];
  mc [label="main.c"]; pc [label="pino.c"];
  mo [label="main.o"]; po [label="pino.o"];
  libc [label="libc", style="rounded,dashed"];
  ohjelma [label="pino", penwidth=1.6];
  h -> mc [label="#include", style=dashed];
  h -> pc [label="#include", style=dashed];
  mc -> mo [label="gcc -c"]; pc -> po [label="gcc -c"];
  mo -> ohjelma; po -> ohjelma [label="linkitys"];
  libc -> ohjelma;
  {rank=same; mc; pc}
}
```

Esimerkkinä on pino, jonka rajapinta on otsikkotiedostossa:

```{.c tiedosto="esimerkit/09-pino/pino.h"}
```

Otsikkotiedosto suojataan *include-vartijalla* (`#ifndef PINO_H`), jotta
sen liittäminen useampaan kertaan samaan käännösyksikköön ei aiheuta
virheitä.

Prototyyppi kertoo tyypit mutta ei *sopimusta*: kuka omistaa
palautetun olion, saako parametri olla tyhjä osoitin, mitä `bool`
tarkoittaa ja mitä tapahtuu, kun pino on tyhjä. Nämä kirjoitetaan
rajapintakommenttiin esittelyn viereen, koska otsikkotiedosto on se,
mitä käyttäjä lukee. Yllä kommentit ovat Doxygenin muodossa:
`/** ... */` aloittaa dokumentaatiokommentin, `@brief` on yhden rivin
tiivistelmä, `@param` kuvaa parametrin ja `@return` paluuarvon.

Doxygen kokoaa kommenteista selattavan viitedokumentaation ja
tarkistaa samalla, että ne vastaavat koodia: asetuksella
`WARN_AS_ERROR` dokumentoimaton parametri tai paluuarvo pysäyttää
käännöksen. Dokumentaation rakentamista ja ylläpitoa käsittelee taito
*Tekninen dokumentaatio*.

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
Tätä varten käytetään käännösjärjestelmää, kuten Makea tai CMakea;
niitä käsittelee taito *Käännösjärjestelmät, testaus ja CI*.

Otsikkotiedostoon kirjoitetaan vain esittelyjä: funktioiden
prototyyppejä, tyyppejä, makroja ja `extern`-esittelyjä globaaleista
muuttujista. Jos otsikkotiedostossa olisi funktion määrittely, se
syntyisi jokaiseen sen liittävään käännösyksikköön, ja linkitys
epäonnistuisi päällekkäisiin määrittelyihin. Poikkeus ovat
`static inline` -funktiot.

## Rajapinnat funktio-osoittimilla

Läpinäkymätön tyyppi kätkee yhden toteutuksen. Usein toteutuksia on
kuitenkin monta, ja käyttäjän pitäisi toimia niiden kaikkien kanssa:
loki voi mennä päätteelle, tiedostoon tai testin laskuriin. C:ssä ei
ole luokkia eikä virtuaalifunktioita, mutta sama asia toteutetaan
rakenteella, jossa on funktio-osoittimia (luku 5). Tätä mallia
käyttää esimerkiksi Linux-ydin: jokaisella tiedostojärjestelmällä ja
laiteajurilla on oma `struct file_operations` -taulunsa.

```{.c tiedosto="esimerkit/09-rajapinta.c" osa="rajapinta"}
```

Toteutus määrittelee omat funktionsa ja yhden vakiotaulun, joka on
kaikille saman toteutuksen olioille yhteinen. Olio itse sisältää vain
osoittimen tauluun ja omaan tilaansa.

```{.dot otsikko="Kutsu `loki_kirjoita(l, rivi)` kulkee olion `ops`-osoittimen kautta toteutuksen tauluun ja sieltä funktioon. Tila välitetään funktiolle `void *`-osoittimena."}
digraph {
  rankdir=LR; nodesep=0.25; ranksep=0.6;
  node [shape=record, style="filled", height=0.3];
  k [label="<t> Loki konsoli | <o> ops | <s> tila"];
  l [label="<t> Loki laskuri | <o> ops | <s> tila"];
  ko [label="<t> KONSOLI_OPS (static const) | <k> kirjoita | <d> tuhoa"];
  lo [label="<t> LASKURI_OPS (static const) | <k> kirjoita | <d> tuhoa"];
  node [shape=box, style="rounded,filled"];
  kk [label="konsoli_kirjoita()"]; kd [label="konsoli_tuhoa()"];
  lk [label="laskuri_kirjoita()"]; ld [label="laskuri_tuhoa()"];
  ks [label="Konsoli (keossa)", style="rounded,dashed"];
  ls [label="Laskuri tilasto", style="rounded,dashed"];
  k:o:e -> ko:t:w; l:o:e -> lo:t:w;
  ko:k:e -> kk; ko:d:e -> kd; lo:k:e -> lk; lo:d:e -> ld;
  k:s:e -> ks [style=dashed]; l:s:e -> ls [style=dashed];
}
```

```{.c tiedosto="esimerkit/09-rajapinta.c" osa="konsoli"}
```

Toinen toteutus laskee rivit tulostamatta niitä. Tällaisia korvikkeita
käytetään testeissä.

```{.c tiedosto="esimerkit/09-rajapinta.c" osa="laskuri"}
```

```{.c tiedosto="esimerkit/09-rajapinta.c" osa="kaytto"}
```

```{.tuloste tiedosto="esimerkit/09-rajapinta.odotettu"}
```

Funktio `kasittele_tilaus` ei tiedä, mihin loki menee. Uuden toteutuksen
voi lisätä muuttamatta käyttäjiä, ja testeissä todellinen kohde
korvataan laskurilla.

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
- **Rajapintakommentti kertoo sopimuksen.** Omistus, sallitut
  parametrien arvot, paluuarvon merkitys ja säieturvallisuus
  kirjoitetaan otsikkotiedostoon esittelyn viereen, ei toteutukseen.
- **Rajapinta funktio-osoitintaululla.** Taulu on `static const`, jotta
  se on yksi ja muuttumaton. Toteutuksen tila välitetään
  `void *`-osoittimena, ja kutsut kääritään pieniin `static inline`
  -funktioihin, jotka kätkevät epäsuoruuden käyttäjältä.
- **Makro vain, kun funktio ei riitä.** Makroja tarvitaan, kun koodin on
  tiedettävä lähdetiedosto ja rivi (`__FILE__`, `__LINE__`), kun
  tarvitaan merkkijonoksi muuttamista tai tunnisteiden liittämistä, tai
  kun luettelo halutaan pitää yhtenäisenä (X-makro).
- **Ehdollinen kääntäminen keskitetysti.** Alustakohtaiset erot kootaan
  yhteen otsikkoon tai omiin toteutustiedostoihin sen sijaan, että
  `#ifdef`-lohkoja olisi kaikkialla.
- **Riippuvuudet.** C:llä ei ole standardia paketinhallintaa.
  Kirjastot löydetään `pkg-config`illa tai järjestelmän paketeista,
  useaa alustaa tukevissa projekteissa usein vcpkg:llä tai Conanilla. Yksitiedostoiset
  kirjastot (esimerkiksi stb-sarja) liitetään lähdekoodina.

## Itsearviointi

- Osaat jakaa ohjelman otsikko- ja toteutustiedostoihin ja kääntää sen.
- Osaat kapseloida tietorakenteen läpinäkymättömällä tyypillä ja
  kirjoittaa sen rajapinnalle sopimuksen kertovat kommentit.
- Osaat toteuttaa rajapinnan funktio-osoitintaululla ja lisätä sille
  toteutuksen muuttamatta käyttäjiä.
- Osaat kirjoittaa turvallisen makron ja tunnistaa kaksoisevaluoinnin
  vaaran.
- Osaat pitää luettelon ja sen tekstit synkronissa X-makrolla.
