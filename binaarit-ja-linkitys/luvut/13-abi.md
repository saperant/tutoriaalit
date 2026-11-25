# ABI: tyypit, asettelu ja kielten raja

*API* (*application programming interface*) on lähdekoodin sopimus:
funktioiden nimet, tyypit ja merkitys. *ABI* (*application binary
interface*) on sama sopimus käännettynä: mitkä rekisterit kuljettavat
argumentit, montako tavua `long` on, missä kohdassa rakennetta kukin
kenttä on, miten symbolien nimet muodostetaan ja miten poikkeukset
etenevät. Kaksi erikseen käännettyä osaa toimivat yhdessä vain, jos
niiden ABI on sama. Linuxin x86-64:llä sopimus on *System V AMD64
psABI*, ja sen kutsukonvention *Assembly*-tutoriaali käsitteli.

## Perustyyppien koot

C-standardi määrää vain vähimmäiskoot. Todelliset koot ovat ABI:n
päätös, ja ne eroavat järjestelmien välillä:

| Tyyppi | Linux x86-64 (LP64) | Windows x64 (LLP64) | 32-bittinen (ILP32) |
|--------|---------------------|---------------------|---------------------|
| `int` | 4 | 4 | 4 |
| `long` | 8 | 4 | 4 |
| `long long` | 8 | 8 | 8 |
| osoitin, `size_t` | 8 | 8 | 4 |
| `long double` | 16 (80-bittinen arvo) | 8 | 12 tai 8 |
| `wchar_t` | 4 | 2 | 4 |

Tiedostoihin, verkkoon ja kielten rajalle kuuluvat siksi kiinteän
kokoiset tyypit (`uint32_t`, `int64_t`). `long` on hyvä vain
osoittimen kokoisena laskurina Unix-järjestelmissä, ja sellaiseen on
selkeämpi käyttää `intptr_t`:tä tai `size_t`:tä.

## Rakenteen asettelu

Jokaisella tyypillä on *tasausvaatimus* (*alignment*): `uint64_t`:n
osoitteen on oltava jaollinen kahdeksalla, `uint32_t`:n neljällä.
Kääntäjä lisää kenttien väliin *täytettä* (*padding*) niin, että
jokainen kenttä on tasattu, ja rakenteen loppuun niin, että
taulukon seuraavakin alkio on tasattu. Rakenteen tasaus on sen
suurimman kentän tasaus. Kentät ovat C:ssä aina kirjoitusjärjestyksessä;
kääntäjä ei saa järjestää niitä uudelleen.

Esimerkin viestirakenteessa on samat neljä kenttää kolmella tavalla:

```{.c tiedosto="esimerkit/13-asettelu/viesti.h" osa="huono"}
```

```{.c tiedosto="esimerkit/13-asettelu/viesti.h" osa="hyva"}
```

```{.c tiedosto="esimerkit/13-asettelu/viesti.h" osa="pakattu"}
```

Ohjelma tulostaa koot, tasaukset ja siirtymät. GCC:n varoitus
`-Wpadded` kertoo jokaisesta lisätystä täytteestä:

```{.c tiedosto="esimerkit/13-asettelu/main.c" osa="tulostus"}
```

```{.bash tiedosto="esimerkit/13-asettelu/aja.sh" osa="asettelu"}
```

```{.tuloste tiedosto="esimerkit/13-asettelu/odotettu"}
```

```{.dot otsikko="Samat neljä kenttää kolmella tavalla. Harmaat ruudut ovat täytettä; numerot ovat siirtymiä tavuina."}
digraph {
  ranksep=0.12;
  node [shape=plaintext, style=""];
  edge [style=invis];
  a [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="6"><b>viesti_huono</b>, 24 tavua</td></tr>
    <tr><td bgcolor="#E4DCF0" width="16">t</td>
        <td bgcolor="#B8C4C8" width="112">täyte, 7 tavua</td>
        <td bgcolor="#F1E3CC" width="128">aikaleima</td>
        <td bgcolor="#E4DCF0" width="32">pit.</td>
        <td bgcolor="#B8C4C8" width="32">2</td>
        <td bgcolor="#F1E3CC" width="64">tarkiste</td></tr>
    <tr><td border="0" align="left"><font point-size="8" color="#5B6B70">0</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">1</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">8</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">16</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">18</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">20</font></td></tr>
  </table>>];
  b [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="6"><b>viesti</b>, 16 tavua</td></tr>
    <tr><td bgcolor="#F1E3CC" width="128">aikaleima</td>
        <td bgcolor="#F1E3CC" width="64">tarkiste</td>
        <td bgcolor="#E4DCF0" width="32">pit.</td>
        <td bgcolor="#E4DCF0" width="16">t</td>
        <td bgcolor="#EEF1F2" width="16">v</td>
        <td border="0" width="128"></td></tr>
    <tr><td border="0" align="left"><font point-size="8" color="#5B6B70">0</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">8</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">12</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">14</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">15</font></td><td border="0" align="left"></td></tr>
  </table>>];
  c [label=<<table border="0" cellborder="1" cellspacing="0" cellpadding="4">
    <tr><td border="0" align="left" colspan="5"><b>viesti_levy</b> (packed), 15 tavua</td></tr>
    <tr><td bgcolor="#E4DCF0" width="16">t</td>
        <td bgcolor="#F1E3CC" width="128">aikaleima</td>
        <td bgcolor="#E4DCF0" width="32">pit.</td>
        <td bgcolor="#F1E3CC" width="64">tarkiste</td>
        <td border="0" width="144"></td></tr>
    <tr><td border="0" align="left"><font point-size="8" color="#5B6B70">0</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">1</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">9</font></td><td border="0" align="left"><font point-size="8" color="#5B6B70">11</font></td><td border="0" align="left"></td></tr>
  </table>>];
  a -> b -> c;
}
```

Kirjoitusjärjestyksessä 15 tavun tieto vie 24 tavua: 7 tavua täytettä
ensimmäisen kentän jälkeen ja 2 tavua kentän `pituus` jälkeen.
Järjestämällä kentät suurimmasta pienimpään rakenne vie 16 tavua, ja
viimeinen tavu on nimetty varatuksi kentäksi. Nimetty täyte on
ABI-suunnittelun keino: kentän voi myöhemmin ottaa käyttöön ilman,
että koko tai muiden kenttien siirtymät muuttuvat.

`packed` poistaa täytteen, mutta hinta on suuri. Rakenteen tasaus on
yksi, joten sen kentät ovat tasaamattomia. Nykyinen x86-64 lukee
tasaamattoman kentän yhtä nopeasti kuin tasatun, ellei kenttä ylitä
välimuistirivin tai sivun rajaa, mutta monet muut suorittimet eivät
lue sitä lainkaan yhdellä käskyllä, joten kääntäjä tuottaa tavu
kerrallaan luvun.
Pakatun kentän osoitetta ei saa välittää tavallisena osoittimena
(`&v.aikaleima` on `uint64_t *`, joka lupaa tasauksen; GCC varoittaa
`-Waddress-of-packed-member`). Pakattu rakenne sopii levy- ja
verkkomuodon kuvaamiseen, jos tavujärjestys käsitellään erikseen,
mutta ei ohjelman sisäiseksi tietorakenteeksi.

## Asettelu lukitaan käännösaikana

Kun rakenne on osa ABI:a (kirjaston rajapinta, tiedostomuoto,
laiterekisterit), sen koko ja kenttien siirtymät kannattaa tarkistaa
käännösaikana. Edellä `viesti.h` tarkistaa ne `_Static_assert`:lla.
Kun joku lisää kentän keskelle, käännös pysähtyy:

```{.c tiedosto="esimerkit/13-asettelu/rikki.c" osa="rikki"}
```

```{.bash tiedosto="esimerkit/13-asettelu/aja.sh" osa="tarkistus"}
```

Tarkistus tekee ABI-muutoksesta tietoisen päätöksen. Sama muutos ilman
tarkistusta olisi ollut luvun 9 hiljainen virhe.

Muita asetteluun vaikuttavia asioita:

- **Bittikentät**: järjestys ja pakkaus ovat toteutuksen päätös.
  Laiterekistereiden ja protokollien kuvaamiseen maskit ja siirrot
  ovat siirrettävämpiä.
- **`enum`**: koko on yleensä `int`, mutta `-fshort-enums` ja C23:n
  `enum : uint8_t` muuttavat sen. Rajapinnoissa kiinteä kokonaislukutyyppi
  on turvallisempi.
- **`bool`**: yksi tavu, arvot 0 ja 1.
- **Tavujärjestys**: x86-64 ja useimmat ARM-järjestelmät ovat
  little endian, verkkoprotokollat big endian (`htonl`, `be32toh`).

## C++:n nimien koristelu

C++ sallii ylikuormituksen ja nimiavaruudet, mutta linkkeri tuntee
vain nimiä. Kääntäjä koodaa siksi nimiavaruuden, funktion nimen ja
parametrien tyypit symbolin nimeen (*name mangling*). Itanium C++ ABI
määrää koristelun, ja sitä käyttävät GCC ja Clang kaikilla
alustoilla Windowsia lukuun ottamatta.

Esimerkin suodinkirjasto on kirjoitettu C++:lla ja tarjoaa
C-rajapinnan. Otsake kelpaa molemmille kielille:

```{.cpp tiedosto="esimerkit/13-cpp-nimet/suodin.hpp" osa="otsake"}
```

```{.cpp tiedosto="esimerkit/13-cpp-nimet/suodin.cpp" osa="cpp"}
```

```{.bash tiedosto="esimerkit/13-cpp-nimet/aja.sh" osa="nimet"}
```

Nimen `_ZN6suodin9keskiarvoEPKdm` osat: `_Z` aloittaa koristellun
nimen, `N ... E` on sisäkkäinen nimi (`6suodin` ja `9keskiarvo`, luku
kertoo pituuden) ja loput ovat parametrien tyypit: `PKd` on `const
double *` (*pointer*, *konst*, *double*) ja `m` on `unsigned long`.
`c++filt` ja `nm -C` purkavat nimet. Funktio, joka on esitelty
`extern "C"` -lohkossa, saa C:n nimen ilman koristelua.

C-ohjelma voi kutsua C-rajapintaa, ja C++-kääntäjä linkittää
kokonaisuuden, koska se lisää C++:n standardikirjaston
(`libstdc++`) ja poikkeusten tuen:

```{.c tiedosto="esimerkit/13-cpp-nimet/main.c"}
```

```{.bash tiedosto="esimerkit/13-cpp-nimet/aja.sh" osa="linkitys"}
```

Jos otsakkeesta puuttuu `extern "C"`, C++-käännös koristelee
nimen, ja C-ohjelma etsii koristelematonta:

```{.cpp tiedosto="esimerkit/13-cpp-nimet/unohtunut.hpp"}
```

```{.bash tiedosto="esimerkit/13-cpp-nimet/aja.sh" osa="unohtui"}
```

```{.tuloste tiedosto="esimerkit/13-cpp-nimet/odotettu"}
```

Virheilmoitus `undefined reference to 'suodin_keskiarvo'`, kun
kirjastossa on `_Z16suodin_keskiarvoPKdi`, on tämän virheen
tunnusmerkki. Sama virhe toiseen suuntaan: C++-ohjelma ei löydä
C-kirjaston funktiota, koska C-otsakkeesta puuttuu
`#ifdef __cplusplus`-suojaus.

## C++:n ABI-sudenkuopat

Koristelu on vain C++:n ABI:n näkyvin osa. Kirjastorajapinnassa
myös nämä ovat ABI:a:

- **Standardikirjaston tyypit.** `std::string` ja `std::list`
  muuttivat asetteluaan GCC 5:ssä, ja `libstdc++` sisältää molemmat
  versiot (makro `_GLIBCXX_USE_CXX11_ABI`). Eri asetuksilla käännetyt
  osat eivät linkity: uudet nimet ovat nimiavaruudessa `__cxx11`.
- **Luokkien asettelu ja vtable.** Kentän tai virtuaalifunktion
  lisäys muuttaa asettelua. *Pimpl*-malli piilottaa toteutuksen
  osoittimen taakse, kuten C:n läpinäkymätön tyyppi.
- **Poikkeukset.** Poikkeus ei saa ylittää C-rajapintaa; C-kutsuja
  ei osaa purkaa pinoaan. C-rajapinnan funktiot merkitään
  `noexcept`:ksi ja muunnetaan poikkeukset virhekoodeiksi.
- **Mallit ja `inline`-funktiot** käännetään käyttäjän koodiin.
  Niiden muutos vaatii käyttäjien uudelleenkäännöksen.

Siksi kirjastot, joiden on tarkoitus säilyä yhteensopivina pitkään,
tarjoavat usein C-rajapinnan ja ohuen C++-kääreen otsakkeessa.

## Käytännössä

- **Käytä kiinteän kokoisia tyyppejä rajapinnoissa** ja
  tiedostomuodoissa. Tarkista rakenteiden koko ja siirtymät
  `_Static_assert`:lla ja `offsetof`:lla.
- **Järjestä kentät suurimmasta pienimpään** ja nimeä täyte
  varatuksi kentäksi. Rakenne pienenee, ja tulevat laajennukset ovat
  mahdollisia.
- **Älä käytä `packed`:ia sisäisiin tietorakenteisiin.** Lue ja
  kirjoita levy- ja verkkomuodot tavu kerrallaan tai `memcpy`:llä
  tasattuun rakenteeseen.
- **Kirjoita jokaiseen C-otsakkeeseen `extern "C"` -suojaus.** Se ei
  maksa mitään ja tekee kirjastosta käyttökelpoisen C++:sta.
- **Pidä poikkeukset ja standardikirjaston tyypit poissa
  C-rajapinnasta.**

## Itsearviointi

- Osaat selittää API:n ja ABI:n eron ja luetella ABI:n osat.
- Osaat laskea rakenteen koon, tasauksen ja kenttien siirtymät ja
  järjestää kentät täytteen minimoimiseksi.
- Osaat kertoa `packed`-rakenteen hinnat ja sopivan käytön.
- Osaat lukea koristellun C++-nimen pääpiirteet ja purkaa sen
  `c++filt`:llä.
- Osaat tunnistaa puuttuvan `extern "C"`:n linkkerivirheestä ja
  kirjoittaa otsakkeen, joka kelpaa C:lle ja C++:lle.
