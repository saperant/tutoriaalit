# Ristiinkääntäminen ja työkaluketjut

Sulautetun laitteen ohjelmat käännetään kehityskoneella, koska laite on
hidas, siinä ei ole kääntäjää tai sitä ei ole vielä olemassa. Kääntäjä,
joka ajetaan yhdellä arkkitehtuurilla ja tuottaa koodia toiselle, on
*ristikääntäjä* (cross compiler). Kääntäjän lisäksi tarvitaan assembler,
linkkeri, binutilsin muut työkalut, C-kirjasto ja ytimen otsaketiedostot
kohdearkkitehtuurille. Kokonaisuus on *työkaluketju* (toolchain).

Kolmella koneella on omat nimensä. *Build* on kone, jolla työkaluketju
rakennetaan, *host* kone, jolla kääntäjä ajetaan, ja *target* kone, jolle
koodia tuotetaan. Tavallisessa ristiinkääntämisessä build ja host ovat
sama x86-64-työasema ja target on laite. Termit näkyvät GNU-ohjelmien
`configure`-skripteissä (`--build`, `--host`, `--target`), ja niiden
merkitys hämmentää: kun kirjasto ristiinkäännetään laitteelle,
`--host` on laite, koska kirjasto ajetaan siellä.

## Työkaluketjun nimi

Työkaluketju tunnistetaan *kohdetripletistä* (target triplet), josta
muodostuu työkalujen nimien etuliite:

| Tripletti | Arkkitehtuuri | Käyttöjärjestelmä ja ABI |
|-----------|---------------|--------------------------|
| `aarch64-linux-gnu` | 64-bittinen ARM | Linux, glibc |
| `arm-linux-gnueabihf` | 32-bittinen ARM | Linux, glibc, liukuluvut rekistereissä |
| `riscv64-linux-gnu` | 64-bittinen RISC-V | Linux, glibc |
| `aarch64-linux-musl` | 64-bittinen ARM | Linux, musl |
| `arm-none-eabi` | 32-bittinen ARM | ei käyttöjärjestelmää (bare metal) |

Kentät ovat arkkitehtuuri, valmistaja (usein jätetty pois tai
`unknown`), käyttöjärjestelmä ja ABI. Ubuntun paketti
`gcc-aarch64-linux-gnu` asentaa komennot `aarch64-linux-gnu-gcc`,
`aarch64-linux-gnu-ld`, `aarch64-linux-gnu-readelf` ja niin edelleen.
Kääntäjä kertoo oman kohteensa komennolla
`aarch64-linux-gnu-gcc -dumpmachine`.

Ytimen käännös saa etuliitteen muuttujasta `CROSS_COMPILE` ja
arkkitehtuurin muuttujasta `ARCH`. Ympäristön `ydin.mk` asettaa ne
muuttujaan `YMAKE` (luku 1), ja esimerkkien Makefile käyttää samaa
etuliitettä omiin ohjelmiinsa:

```{.make tiedosto="esimerkit/Makefile" osa="ristiin"}
```

## Sama ohjelma kahdelle arkkitehtuurille

Seuraava ohjelma kertoo, millaiselle alustalle se on käännetty. Siinä ei
ole yhtään arkkitehtuurikohtaista riviä:

```{.c tiedosto="esimerkit/01-ristiin/tietoja.c" osa="erot"}
```

Esimerkkien Makefile kääntää sen kolmesti: isännälle, ARM64:lle
staattisesti ja ARM64:lle dynaamisesti linkitettynä.

```{.make tiedosto="esimerkit/Makefile" osa="01"}
```

ARM64-ohjelmaa ei voi ajaa x86-64-koneella suoraan, mutta QEMU:n
*käyttäjätilan emulaattori* `qemu-aarch64` ajaa yksittäisen ohjelman
kääntämällä sen käskyt lennossa ja välittämällä järjestelmäkutsut
isännän ytimelle. Koko järjestelmää ei tarvita, joten tämä on nopein
tapa testata ristiinkäännettyä koodia CI:ssä.

```{.tuloste tiedosto="esimerkit/testit/01-ristiin.odotettu"}
```

Tuloste näyttää kolme asiaa.

1. **`char`-tyypin etumerkki vaihtuu.** C-standardi jättää sen
   toteutuksen päätettäväksi. x86-64:n ABI:ssa `char` on
   etumerkillinen, ARM:n ja RISC-V:n ABI:ssa etumerkitön. Koodi, joka
   vertaa `char`-muuttujaa negatiiviseen lukuun tai tallentaa
   `getchar()`:n paluuarvon `char`-muuttujaan ja vertaa sitä `EOF`:iin,
   toimii kehityskoneella ja rikkoutuu laitteessa. Käytä `int`- tai
   `unsigned char` -tyyppiä tai kiinteän levyisiä tyyppejä
   (`int8_t`, `uint8_t`), kun etumerkillä on väliä. GCC:n valitsin
   `-funsigned-char` tai `-fsigned-char` pakottaa saman käytöksen
   molemmille.
2. **Dynaamisesti linkitetty ohjelma tarvitsee kohteen dynaamisen
   linkittäjän.** Ohjelman otsakkeessa on polku `/lib/ld-linux-aarch64.so.1`,
   jota isännällä ei ole. Valitsin `-L /usr/aarch64-linux-gnu` kertoo
   emulaattorille, mistä kohteen kirjastot löytyvät.
3. **Staattisessa ohjelmassa ei ole tulkkia.** Se sisältää kaiken
   tarvitsemansa ja käynnistyy missä tahansa ARM64-Linuxissa.

## Sysroot

*Sysroot* on hakemisto, joka näyttää kohteen juuritiedostojärjestelmältä
kääntäjän kannalta: `usr/include` kohteen otsakkeille ja `lib` sekä
`usr/lib` kohteen kirjastoille. Ristikääntäjä etsii otsakkeet ja
kirjastot sysrootista eikä isännän `/usr/include`-hakemistosta. Ubuntun
ristikääntäjä käyttää hakemistoa `/usr/aarch64-linux-gnu`, joka on
käännetty kääntäjään sisään. Buildroot ja Yocto tekevät jokaiselle
projektille oman sysrootin, johon asennetaan myös projektin omat
kirjastot.

Kun ristiinkäännetään kolmannen osapuolen kirjastoa, kaksi virhettä
ovat yleisiä:

- **Isännän kirjasto vuotaa käännökseen.** `pkg-config` tai
  `cmake`-haku löytää isännän x86-64-kirjaston, ja linkitys epäonnistuu
  virheeseen "file in wrong format" tai, pahempaa, onnistuu väärää
  otsaketta vasten. Aseta `PKG_CONFIG_SYSROOT_DIR` ja `PKG_CONFIG_LIBDIR`
  osoittamaan sysrootiin ja käytä CMakessa työkaluketjutiedostoa, jossa
  `CMAKE_FIND_ROOT_PATH_MODE_LIBRARY` on `ONLY`.
- **Ohjelma ajetaan käännöksen aikana.** Monet `configure`-skriptit
  kääntävät ja ajavat testiohjelman selvittääkseen alustan ominaisuuden.
  Ristiinkäännöksessä testiohjelmaa ei voi ajaa, joten vastaus on
  annettava etukäteen välimuistimuuttujana.

## C-kirjasto: glibc, musl ja uClibc-ng

C-kirjasto on käyttäjätilan ja ytimen välinen kerros: se toteuttaa
`printf`in, `malloc`in, säikeet ja järjestelmäkutsujen kääreet.
Sulautetussa Linuxissa valitaan yleensä jokin kolmesta:

| Kirjasto | Vahvuudet | Heikkoudet |
|----------|-----------|------------|
| glibc | täydellisin, nopein, yhteensopiva kaiken kanssa | suuri; staattinen linkitys rajoittunutta (NSS, `dlopen`) |
| musl | pieni, selkeä, hyvä staattiseen linkitykseen | hitaampi `malloc`, osa glibc:n laajennuksista puuttuu |
| uClibc-ng | hyvin pieni, MMU:ttomat järjestelmät | pienempi käyttäjäkunta |

Esimerkkien staattinen ohjelma on glibc:llä noin 600 kt, musl-
työkaluketjulla vastaava ohjelma on kymmeniä kilotavuja. Ero on pieni
gigatavun eMMC:llä mutta merkittävä 16 megatavun SPI-flashilla.

## Staattinen vai dynaaminen

Staattinen linkitys kopioi tarvittavat kirjastofunktiot ohjelmaan.
Ohjelma ei riipu kohteen kirjastoista, se käynnistyy hieman nopeammin
eikä dynaamisen linkittäjän hakupolkuja tarvitse miettiä. Siksi tämän
tutoriaalin init-ohjelmat ovat staattisia: initramfsiin ei tarvitse
kopioida C-kirjastoa.

Dynaaminen linkitys on parempi, kun järjestelmässä on monta ohjelmaa:
kirjasto on levyllä ja muistissa kerran, ja tietoturvapäivitys
kirjastoon korjaa kaikki ohjelmat. Lisenssi vaikuttaa myös: LGPL-
lisensoitua kirjastoa käyttävä suljettu ohjelma on yleensä linkitettävä
dynaamisesti tai toimitettava niin, että käyttäjä voi linkittää sen
uudelleen.

## Työkaluketjun lähteet

Valmiita työkaluketjuja on kolmenlaisia:

- **Jakelun paketti**, kuten tämän tutoriaalin `gcc-aarch64-linux-gnu`.
  Helppo, mutta C-kirjaston versio on jakelun, ja se ei välttämättä
  vastaa laitteen kirjastoa.
- **Toimittajan tai yhteisön valmis ketju**, kuten Arm GNU Toolchain
  tai Bootlinin toolchains.bootlin.com-ketjut eri arkkitehtuureille ja
  C-kirjastoille.
- **Itse rakennettu**: crosstool-NG rakentaa ketjun valikosta valituilla
  versioilla, ja Buildroot sekä Yocto rakentavat ketjun osana koko
  järjestelmää. Tuotannossa ketju lukitaan versioon, koska kääntäjän
  vaihto muuttaa jokaista binääriä.

Clang on GCC:n vaihtoehto: yksi `clang` kääntää kaikille
arkkitehtuureille valitsimella `--target=aarch64-linux-gnu`, kunhan
sysroot ja linkkeri ovat saatavilla. Ytimen voi kääntää Clangilla
muuttujalla `LLVM=1`.

## Käytännössä

- **Lukitse työkaluketju ja kirjoita sen versio muistiin.** Laitteen
  ohjelmisto on toistettavissa vain, jos sama kääntäjä on saatavilla
  vuosien päästä. Tallenna ketju arkistoon tai konttikuvaan.
- **Testaa ristiinkäännetty koodi emulaattorissa CI:ssä.**
  `qemu-aarch64` ajaa yksikkötestit kohdearkkitehtuurilla ja paljastaa
  `char`-etumerkin, tavujärjestyksen ja kohdistuksen kaltaiset erot
  ennen kuin laitetta on edes olemassa.
- **Älä anna isännän otsakkeiden ja kirjastojen vuotaa.** Tarkista
  valmiista ohjelmasta `readelf -d`:llä, että `NEEDED`-kirjastot ja
  tulkki ovat kohteen, ja käytä rakennustyökalun sysrootia.
- **Käytä kiinteän levyisiä tyyppejä rajapinnoissa.** Laitteen ja
  palvelimen välinen protokolla tai tiedostomuoto ei saa riippua siitä,
  kuinka leveä `long` on tai onko `char` etumerkillinen.

## Itsearviointi

- Osaat selittää termit build, host ja target sekä kohdetripletin
  kentät.
- Osaat ristiinkääntää C-ohjelman ARM64:lle ja ajaa sen
  `qemu-aarch64`:llä staattisena ja dynaamisena.
- Osaat kertoa, mikä sysroot on ja miten isännän kirjastot vuotavat
  ristiinkäännökseen.
- Osaat vertailla glibc:tä, muslia ja uClibc-ng:tä ja perustella
  staattisen tai dynaamisen linkityksen valinnan.
- Osaat nimetä tavallisimmat alustojen väliset erot C-koodissa, kuten
  `char`-tyypin etumerkin.
