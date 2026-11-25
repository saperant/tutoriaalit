# CMake

Make kuvaa tiedostoja ja komentoja. Kun projekti on käännettävä
Linuxilla, macOS:llä ja Windowsilla, GCC:llä, Clangilla ja MSVC:llä,
komennot ovat eri alustoilla erilaisia, ja Makefile täyttyy ehdoista.
CMake nostaa kuvauksen tasoa: siinä kerrotaan, mitä rakennetaan
(kirjasto, ohjelma, testi) ja mitä ne tarvitsevat, ja CMake tuottaa
siitä varsinaisen rakennusjärjestelmän, esimerkiksi Makefilet,
Ninja-tiedostot tai Visual Studion projektin. CMake on C- ja
C++-projektien yleisin rakennusjärjestelmä, ja useimmat kirjastot,
IDE:t ja paketinhallinnat osaavat käyttää sitä. Samaa ajatusta
toteuttaa Meson, jota käyttävät muun muassa GNOME, systemd ja Mesa:
kuvauskieli on suppeampi ja tiukempi, ja taustalla on aina Ninja.
Tämän luvun käsitteet (kohteet, näkyvyys, erillinen rakennushakemisto)
pätevät siinäkin.

CMaken käyttö jakautuu kahteen vaiheeseen:

```text
cmake -S . -B build -G Ninja      konfigurointi: lukee CMakeLists.txt:n,
                                  etsii kääntäjän ja kirjastot
cmake --build build               rakennus: ajaa Ninjan tai Maken
ctest --test-dir build            testit
```

## Projekti

`CMakeLists.txt` alkaa vaaditulla CMake-versiolla ja projektin
kuvauksella:

```{.cmake tiedosto="esimerkit/06-cmake/CMakeLists.txt" osa="projekti"}
```

`cmake_minimum_required` ei ole muodollisuus: se valitsee, miten CMake
käyttäytyy (*policies*). Uudempi CMake käyttäytyy kuten pyydetty
versio, joten projekti ei rikkoudu CMaken päivittyessä. Kielistandardi
asetetaan muuttujilla eikä lipulla `-std=c17`, koska CMake osaa kertoa
sen jokaiselle kääntäjälle oikealla valitsimella. `CMAKE_C_EXTENSIONS
OFF` valitsee standardin C:n (`-std=c17`) GNU-laajennusten
(`-std=gnu17`) sijaan.

`CMAKE_EXPORT_COMPILE_COMMANDS` kirjoittaa tiedoston
`compile_commands.json`, jossa on jokaisen lähdetiedoston tarkka
käännöskomento. Editorien kielipalvelimet (clangd) ja analyysityökalut
(clang-tidy) lukevat sen, jotta ne näkevät koodin samoin kuin kääntäjä.

## Kohteet ja niiden ominaisuudet

Nykyaikaisen CMaken perusajatus on *kohde* (*target*). Kirjasto ja
ohjelma ovat kohteita, ja kaikki asetukset (otsakehakemistot, liput,
linkitettävät kirjastot) kiinnitetään kohteisiin `target_*`-komennoilla.
Vanhat globaalit komennot (`include_directories`, `add_definitions`,
`link_libraries`) koskevat kaikkea hakemistossa ja sen alla, ja niiden
vaikutusta on vaikea rajata. Niitä ei käytetä uudessa koodissa.

```{.cmake tiedosto="esimerkit/06-cmake/CMakeLists.txt" osa="kohteet"}
```

```{.dot otsikko="Esimerkin kohteet. Nuoli osoittaa kohteesta sen riippuvuuteen, ja nuolen teksti on linkityksen näkyvyys. Kirjaston `PUBLIC`-asetus siirtyy sitä käyttäville kohteille, `PRIVATE`-asetus ei."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.5;
  node [shape=record, style="filled"];
  cli [label="tilasto-cli | saa: -Ilahde"];
  testi [label="testaa_tilasto | saa: -Ilahde"];
  lib [label="tilasto | PUBLIC: -Ilahde | PRIVATE: -Wall -Wextra -Werror"];
  m [label="m", shape=box, style="rounded,dashed"];
  cli -> lib [label="PRIVATE"];
  testi -> lib [label="PRIVATE"];
  lib -> m [label="PRIVATE"];
}
```

Jokaisella `target_*`-asetuksella on näkyvyys, joka kertoo, kenelle
asetus kuuluu:

| Näkyvyys | Koskee kohdetta itseään | Siirtyy käyttäjille |
|----------|-------------------------|----------------------|
| `PRIVATE` | kyllä | ei |
| `INTERFACE` | ei | kyllä |
| `PUBLIC` | kyllä | kyllä |

Otsakehakemisto on `PUBLIC`, koska sekä kirjasto että sen käyttäjät
lukevat `tilasto.h`:n. Varoitusliput ovat `PRIVATE`: ne koskevat
kirjaston omaa koodia, eikä kirjaston pidä päättää, millä varoituksilla
sen käyttäjät kääntävät. `INTERFACE` sopii vain otsakkeista koostuvalle
kirjastolle, jolla ei ole omia lähteitä, tai asetukselle, jota
käyttäjät tarvitsevat mutta kirjasto ei. Näkyvyys tekee riippuvuuksista
transitiivisia: kun `tilasto-cli` linkittää `tilasto`-kirjaston, se saa
automaattisesti kirjaston `PUBLIC`- ja `INTERFACE`-asetukset.
Yksikään kohde ei tarvitse tietää, miten sen riippuvuudet on rakennettu.

`libm` on linkitetty `PRIVATE`-näkyvyydellä, koska se on toteutuksen
yksityiskohta. Staattisen kirjaston käyttäjän on silti linkitettävä
`libm`, koska `.a`-arkisto ei sisällä riippuvuuksiaan, ja CMake lisää
sen linkitykseen automaattisesti. Jaetulla kirjastolla riippuvuus
tallentuu kirjastoon itseensä.

## Testit

`enable_testing()` ja `add_test()` rekisteröivät testit CTestille:

```{.cmake tiedosto="esimerkit/06-cmake/CMakeLists.txt" osa="testit"}
```

Ensimmäinen testi on testiohjelma, joka onnistuu tai epäonnistuu
paluuarvollaan. Toinen ajaa varsinaisen ohjelman ja hyväksyy tuloksen
säännöllisellä lausekkeella. Lauseke `$<TARGET_FILE:tilasto-cli>` on
*generaattorilauseke* (*generator expression*): se laajenee vasta
rakennusvaiheessa ohjelman todelliseksi poluksi, joka riippuu
generaattorista ja käännöstyypistä. Testiohjelma on yksinkertainen,
`assert`-pohjainen:

```{.c tiedosto="esimerkit/06-cmake/testit/testaa_tilasto.c"}
```

Rivi `#undef NDEBUG` on tärkeä. Release-käännös määrittelee makron
`NDEBUG`, jolloin `assert` ei tee mitään, ja testi menisi läpi
testaamatta mitään. Luvun 8 testikehys välttää ongelman kokonaan
käyttämällä omia tarkistusmakroja.

## Esiasetukset

Konfigurointi tarvitsee usein monta valitsinta: generaattorin,
käännöstyypin, sanitoijat ja rakennushakemiston. Niiden kirjoittaminen
käsin on virhealtista, ja jokainen kehittäjä kirjoittaa ne vähän eri
tavalla. `CMakePresets.json` tallentaa ne versionhallintaan
nimettyinä *esiasetuksina*:

```{.json tiedosto="esimerkit/06-cmake/CMakePresets.json"}
```

Esiasetuksia on kolmenlaisia: konfigurointi (`configurePresets`),
rakennus (`buildPresets`) ja testaus (`testPresets`). Kehitysversio
kääntää debug-tiedolla ja sanitoijilla, julkaisuversio optimoiden.
Molemmat rakentuvat omaan hakemistoonsa `build/<nimi>`, joten ne
voivat olla olemassa yhtä aikaa. Kehittäjän omat asetukset (esimerkiksi
toinen kääntäjä) kuuluvat tiedostoon `CMakeUserPresets.json`, jota ei
lisätä versionhallintaan.

## Rakennus lähdepuun ulkopuolelle

CMake rakentaa aina erilliseen hakemistoon (*out-of-source build*).
Lähdepuu pysyy puhtaana, ja samasta lähteestä voi rakentaa monta
versiota rinnakkain. Ninja on generaattoreista nopein: se on
suunniteltu suoritettavaksi eikä kirjoitettavaksi, se käynnistyy
nopeasti ja rinnakkaistaa oletuksena kaikille prosessoreille.
Esimerkki rakentaa ja testaa molemmat esiasetukset:

```{.bash tiedosto="esimerkit/06-cmake/aja.sh" osa="kehitys"}
```

```{.bash tiedosto="esimerkit/06-cmake/aja.sh" osa="liput"}
```

```{.bash tiedosto="esimerkit/06-cmake/aja.sh" osa="julkaisu"}
```

```{.tuloste tiedosto="esimerkit/06-cmake.odotettu"}
```

Tiedosto `compile_commands.json` todistaa näkyvyyden toimivan:
otsakehakemisto `lahde` siirtyi kaikille kirjastoa käyttäville
kohteille (`PUBLIC`), mutta `-Werror` koskee vain kirjaston omaa
lähdettä (`PRIVATE`). Tulosteen viimeinen osa asentaa
julkaisuversion; asennussäännöt esitellään seuraavassa luvussa.

## Riippuvuudet: find_package

Järjestelmään asennetut kirjastot löydetään komennolla `find_package`.
Moderni kirjasto asentaa CMake-määrittelyn (`<Nimi>Config.cmake`),
joka luo tuodun kohteen. Sitä käytetään kuten omaa kohdetta:

```text
find_package(ZLIB REQUIRED)
target_link_libraries(tilasto PRIVATE ZLIB::ZLIB)
```

Nimiavaruudellinen nimi `ZLIB::ZLIB` on tunnistettava tuoduksi kohteeksi:
jos sitä ei löydy, CMake antaa virheen konfiguroinnissa eikä yritä
linkittää kirjastoa nimeltä `ZLIB::ZLIB`. `REQUIRED` pysäyttää
konfiguroinnin selvään virheeseen, jos kirjastoa ei ole. Kirjastoille,
joilla on vain `pkg-config`-kuvaus, on moduuli `FindPkgConfig`
(`pkg_check_modules(... IMPORTED_TARGET ...)`). Riippuvuuksien
hankkimista käsitellään seuraavassa luvussa.

## Käytännössä

- **Kohteet ja `target_*`, ei globaaleja komentoja.** Jokaisella
  asetuksella on omistaja ja näkyvyys. Tämä on yksittäinen tärkein ero
  vanhan ja nykyaikaisen CMaken välillä.
- **Oletuksena `PRIVATE`.** Asetus siirretään käyttäjille vain, jos he
  todella tarvitsevat sen. Liian laaja näkyvyys tekee riippuvuuksista
  tiukkoja ja käännöksistä hitaita.
- **Esiasetukset versionhallintaan.** `cmake --preset kehitys` on sama
  komento kehittäjän koneella ja CI:ssä. Kun liput ovat yhdessä
  paikassa, CI ei rakenna eri tavalla kuin kehittäjä.
- **Ninja generaattoriksi.** Se on nopea, rinnakkainen ja toimii
  samoin kaikilla alustoilla.
- **Älä kirjoita kääntäjäkohtaisia lippuja, jos CMakella on niille
  ominaisuus.** Standardi, sijaintiriippumaton koodi
  (`POSITION_INDEPENDENT_CODE`) ja linkkiaikainen optimointi
  (`INTERPROCEDURAL_OPTIMIZATION`) ovat ominaisuuksia, jotka toimivat
  jokaisella kääntäjällä.

## Itsearviointi

- Osaat kirjoittaa `CMakeLists.txt`:n, jossa on kirjasto, sitä käyttävä
  ohjelma ja testit.
- Osaat valita `PUBLIC`-, `PRIVATE`- ja `INTERFACE`-näkyvyyden ja
  selittää, miten asetukset siirtyvät riippuvuuksien kautta.
- Osaat kirjoittaa `CMakePresets.json`-tiedoston kehitys- ja
  julkaisuversiolle ja käyttää sitä komennoilla `cmake --preset`,
  `cmake --build --preset` ja `ctest --preset`.
- Osaat käyttää järjestelmän kirjastoa `find_package`-komennolla ja
  tuodulla kohteella.
