# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Linkkeri tuntee vain nimet.** Tyypit, otsakkeet ja nimiavaruudet
   ovat kääntäjän asioita. Kun linkitys epäonnistuu, katso nimiä:
   `nm`, `nm -C`, `readelf -s`.
2. **Kirjastot objektien jälkeen.** Staattinen arkisto ratkaisee vain
   sillä hetkellä puuttuvat symbolit.
3. **`-L` on linkkerille, `RUNPATH` lataajalle.** Ohjelma, joka
   linkittyy, ei välttämättä käynnisty. Käytä `$ORIGIN`-polkuja
   sovelluksen omille kirjastoille.
4. **Piilota kaikki, mikä ei ole rajapintaa.** `static` tiedoston
   sisällä, `-fvisibility=hidden` ja vientimakro kirjastossa,
   versioskripti `local: *;` varmuuden vuoksi.
5. **Soname vaihtuu, kun ABI rikkoutuu.** Rakenteen kenttien järjestys
   ja tyypit ovat ABI:a, vaikka lähdekoodi kääntyisi ennallaan.
6. **Lukitse asettelu.** `_Static_assert(sizeof ...)` ja `offsetof`
   jokaiselle rakenteelle, joka ylittää kirjasto-, tiedosto- tai
   kielirajan.
7. **`extern "C"` jokaiseen C-otsakkeeseen.**
8. **Välitön sidonta ja täysi RELRO.** Puuttuva symboli paljastuu
   käynnistyksessä, ja GOT on suojattu.
9. **Käännä `-g`:llä, riisu erikseen.** Säilytä debug-tiedostot
   koontitunnisteen mukaan.
10. **Lue linkkerikartta ja `LD_DEBUG`.** Ne kertovat, mitä linkkeri
    ja lataaja todella tekivät.

## Vianetsintä oireen mukaan

| Oire | Todennäköinen syy | Ensimmäinen komento |
|------|-------------------|---------------------|
| `undefined reference to 'f'` | kirjasto puuttuu tai väärässä järjestyksessä | `nm -A *.o *.a \| grep ' f$'` |
| `undefined reference to 'f'`, C++ | `extern "C"` puuttuu | `nm -C kirjasto \| grep f` |
| `multiple definition of 'x'` | määrittely otsakkeessa, `-fno-common` | `nm -A *.o \| grep ' x$'` |
| `cannot open shared object file` | hakupolku | `ldd ohjelma`, `LD_DEBUG=libs` |
| `version 'GLIBC_2.38' not found` | käännetty uudemmalla glibc:llä | `objdump -T ohjelma \| grep GLIBC_2.3` |
| `undefined symbol` käynnistyksessä | kirjaston ABI muuttui | `nm -D --defined-only libx.so` |
| väärät arvot päivityksen jälkeen | rakenteen asettelu muuttui | `abidiff vanha.so uusi.so` |
| väärä funktio kutsutaan | symbolitörmäys | `LD_DEBUG=bindings` |
| `No such file or directory`, tiedosto on | `INTERP`-polku puuttuu | `readelf -l ohjelma` |
| `relocation ... recompile with -fPIC` | ei-PIC-objekti kirjastossa | käännä `-fPIC`:llä |
| `region 'RAM' overflowed` | ohjelma ei mahdu | `-Wl,-Map`, `size` |

## Jatkotaidot

- **Mikrokontrollerit**: linkkeriskriptit muistialueineen,
  käynnistyskoodi, joka kopioi `.data`:n ja nollaa `.bss`:n,
  keskeytysvektorit heikkoina symboleina.
- **Takaisinmallinnus**: riisuttujen binäärien lukeminen, PLT:n ja
  GOT:n kautta tunnistetut kirjastokutsut, Ghidra ja radare2.
- **Haavoittuvuudet**: GOT:n ylikirjoitus, ROP-ketjut ja niiden
  suojaukset: ASLR ja PIE, RELRO, pinon suojaus, CET.
- **Rakennus ja testaus**: tämän tutoriaalin komennot
  rakennusjärjestelmän kautta, CMaken näkyvyys- ja `RPATH`-asetukset.

## Lähteet

Määrittelyt ja käsikirjat:

- *System V Application Binary Interface* (gABI), ELF-muodon yleinen
  määrittely. <https://www.sco.com/developers/gabi/>.
- *System V Application Binary Interface, AMD64 Architecture Processor
  Supplement* (psABI). <https://gitlab.com/x86-psABIs/x86-64-ABI>.
- *Itanium C++ ABI*, nimien koristelu ja luokkien asettelu.
  <https://itanium-cxx-abi.github.io/cxx-abi/abi.html>.
- *DWARF Debugging Information Format*, versio 5.
  <https://dwarfstd.org/>.
- *LD* (GNU-linkkerin käsikirja), erityisesti luku *Linker Scripts*.
  <https://sourceware.org/binutils/docs/ld/>.
- *GNU Binary Utilities* (`readelf`, `objdump`, `nm`, `ar`, `objcopy`,
  `strip`, `addr2line`). <https://sourceware.org/binutils/docs/binutils/>.
- *Using the GNU Compiler Collection*, attribuutit `visibility`,
  `weak`, `section`, `constructor` ja `symver`.
  <https://gcc.gnu.org/onlinedocs/gcc/>.
- Linuxin manuaalisivut: `ld.so(8)`, `ldconfig(8)`, `elf(5)`,
  `dlopen(3)`, `getauxval(3)`.

Artikkelit ja kirjat:

- Drepper, U.: *How To Write Shared Libraries*. Jaettujen kirjastojen
  suunnittelu, näkyvyys ja versiointi.
  <https://www.akkadia.org/drepper/dsohowto.pdf>.
- Levine, J.: *Linkers and Loaders*. Morgan Kaufmann.
- Bryant, R. ja O'Hallaron, D.: *Computer Systems: A Programmer's
  Perspective*, luku 7 (linkitys).
- Taylor, I. L.: *Linkers*, 20-osainen artikkelisarja gold-linkkerin
  tekijältä. <https://www.airs.com/blog/archives/38>.
- Libabigail (`abidiff`). <https://sourceware.org/libabigail/>.

Tämä tutoriaali on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
-lisenssillä (CC BY-SA 4.0). Esimerkkikoodit ovat saman lisenssin
alaisia.
