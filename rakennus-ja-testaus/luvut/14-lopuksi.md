# Lopuksi {.runko-lahteet}

## Nyrkkisäännöt

1. **Riippuvuudet koneella.** `-MMD -MP` Makessa, kohteet ja
   `target_*` CMakessa. Käsin kirjoitettu riippuvuus vanhenee.
2. **Pakolliset liput erillään käyttäjän lipuista.** Käyttäjä vaihtaa
   optimoinnin, ei varoituksia.
3. **Rakennus lähdepuun ulkopuolelle.** `build/` tai `build/<esiasetus>`,
   ja samasta lähteestä voi rakentaa monta versiota.
4. **Oletuksena `PRIVATE`.** Asetus siirtyy kohteen käyttäjille vain,
   jos he tarvitsevat sen.
5. **Sama komento kaikkialla.** Esiasetukset ja Make-kohteet
   sisältävät rakennuslogiikan; CI ja kehittäjä kutsuvat samoja
   komentoja.
6. **Ulkoiset riippuvuudet saumoiksi.** Kello, satunnaisuus ja
   järjestelmäkutsut omiin rajapintoihinsa, jotka testi korvaa
   linkittämällä.
7. **ASan ja UBSan kehitykseen, TSan omaksi työkseen.** Virhe kaataa
   testin.
8. **Lue kattamattomat rivit.** Kattavuusluku kertoo vähän, puuttuvat
   rivit paljon.
9. **Varoitukset nollassa.** `-Werror` ja `WarningsAsErrors` CI:ssä,
   ohitukset perusteluineen.
10. **Kiinnitä työkalut ja riippuvuudet.** Tarkat versiot tekevät
    rakennuksesta toistettavan ja CI:stä vakaan.

## Mallit ja käytännöt

| Malli tai käytäntö | Mihin | Luku |
|--------------------|-------|------|
| erillinen käännös | vain muuttuneet tiedostot käännetään | 2 |
| valekohde (`.PHONY`) | komennot, jotka eivät tuota tiedostoa | 3 |
| automaattiset riippuvuudet | otsakkeiden muutokset | 4 |
| järjestysriippuvuus | käännöshakemisto | 4 |
| `SOURCE_DATE_EPOCH` | toistettava aika | 5 |
| kohde ja näkyvyys | CMake-asetusten omistajuus | 6 |
| esiasetukset | sama konfigurointi kaikkialla | 6 |
| soname ja versioskripti | jaetun kirjaston rajapinta | 7 |
| `$ORIGIN`-hakupolku | ohjelman mukana kulkevat kirjastot | 7 |
| `PREFIX` ja `DESTDIR` | asennus ja paketointi | 7 |
| testikaksonen linkkerillä | eristetyt, deterministiset testit | 8 |
| `--wrap` | virhepolkujen testaus | 8 |
| `-fno-sanitize-recover` | sanitoijan virhe kaataa testin | 9 |
| sumutuskohde | jäsentimen virheet syötteillä, joita kukaan ei keksinyt | 9 |
| kattavuuskynnys | kattavuuden laskun esto | 10 |
| analyysiasetukset tiedostossa | sama analyysi kaikilla | 11 |
| matriisi | useampi kääntäjä ja käännöstyyppi | 12 |
| artefakti | raportit ja lokit vianetsintään | 12 |
| gdb eräajona | toistettava vianetsintä, CI:n kutsupinot | 13 |

## Mihin tästä eteenpäin

- **Jatkuva integraatio ja toimitus:** putkien yleiset periaatteet,
  julkaisu ja toimitus tämän tutoriaalin rakennus- ja testiputken
  jatkoksi.
- **Sulautettu Linux:** ristiinkäännös, CMaken työkaluketjutiedostot
  (*toolchain file*), Buildroot ja Yocto sekä ohjelmien testaus
  emulaattorissa.
- **EDA-työkaluketjujen automatisointi:** simulaattorien ja
  synteesityökalujen ajaminen Makella ja CI:ssä, regressiotestaus ja
  tulosten raportointi.
- **Objektitiedostot, linkitys ja ABI:** linkkerin toiminta,
  symbolien näkyvyys ja jaettujen kirjastojen yhteensopivuus syvemmin.
- **Tietoturva kehitystyössä:** toimitusketjun turvallisuus,
  riippuvuuksien eheys, CI:n oikeudet ja salaisuudet sekä
  kovennusvalitsimet.

## Lähteet

- GNU Make Manual. Free Software Foundation, <https://www.gnu.org/software/make/manual/>.
  Säännöt, muuttujat, automaattiset riippuvuudet ja rinnakkaisuus.
- Peter Miller: ”Recursive Make Considered Harmful.” *AUUGN* 19(1),
  1998. Miksi yksi Makefile näkee riippuvuudet paremmin kuin monta.
- CMake Documentation. Kitware, <https://cmake.org/cmake/help/latest/>.
  Erityisesti *cmake-buildsystem(7)*, *cmake-presets(7)* ja
  *cmake-generator-expressions(7)*.
- Craig Scott: *Professional CMake: A Practical Guide*. Crascit,
  jatkuvasti päivittyvä e-kirja. Nykyaikaisen CMaken käytännöt.
- Reproducible Builds -projekti: <https://reproducible-builds.org/docs/>.
  `SOURCE_DATE_EPOCH`, tavalliset epätoistettavuuden syyt ja diffoscope.
- Ulrich Drepper: *How To Write Shared Libraries*, 2011.
  Jaettujen kirjastojen rakenne, symbolien näkyvyys ja versiointi.
- pkg-config Guide. freedesktop.org,
  <https://people.freedesktop.org/~dbn/pkg-config-guide.html>.
- James W. Grenning: *Test-Driven Development for Embedded C*.
  Pragmatic Bookshelf, 2011. Testikaksoset ja linkkerisaumat C:ssä.
- Konstantin Serebryany ym.: ”AddressSanitizer: A Fast Address Sanity
  Checker.” *USENIX ATC*, 2012.
- Clang Documentation: AddressSanitizer, UndefinedBehaviorSanitizer,
  ThreadSanitizer, <https://clang.llvm.org/docs/>.
- gcovr Documentation, <https://gcovr.com/>. Kattavuusraportit ja
  kynnykset.
- Clang-Tidy Documentation, <https://clang.llvm.org/extra/clang-tidy/>,
  ja Cppcheck Manual, <https://cppcheck.sourceforge.io/manual.pdf>.
- GitHub Actions Documentation, <https://docs.github.com/actions>.
  Työnkulun syntaksi, matriisit, välimuisti ja artefaktit.
- Debugging with GDB. Free Software Foundation,
  <https://sourceware.org/gdb/documentation/>. Eräajo, vahtipisteet ja
  ytimen vedokset.

## Lisenssi

Tämä teos on lisensoitu Creative Commons Nimeä–JaaSamoin 4.0
Kansainvälinen -lisenssillä (CC BY-SA 4.0). Esimerkkikoodia saa käyttää
saman lisenssin ehdoin.
