# Johdanto {.runko-johdanto}

C-ohjelman kääntäminen on yksi komento: `gcc main.c`. Projektin
rakentaminen on paljon muuta. Kymmenien lähdetiedostojen on käännyttävä
uudelleen silloin, kun jokin niiden lukema otsake muuttuu, mutta ei
joka kerta kaikki. Kirjastot on löydettävä kehittäjän koneelta ja
CI-palvelimelta samoilla lipuilla. Testit on ajettava jokaisesta
muutoksesta, mieluiten useammalla kääntäjällä ja sanitoijilla, ja
rikkoutunut testi on saatava näkyviin ennen kuin muutos yhdistetään
päähaaraan. Kun jokin silti kaatuu, kaatumiskohta on löydettävä
nopeasti.

Tämä tutoriaali opettaa nuo taidot yhden pienen C-projektin avulla:

- **Käännösprosessi:** esikäsittely, käännös, kokoaminen ja linkitys
  erikseen, ja mitä kukin vaihe voi rikkoa.
- **Make:** säännöt, riippuvuudet, automaattiset otsakeriippuvuudet
  (`-MMD`), mallisäännöt, muuttujat, valekohteet ja rinnakkaisuus.
- **Toistettava rakennus:** miksi sama lähde tuottaa eri binäärin ja
  miten se korjataan.
- **CMake:** kohteet ja niiden ominaisuudet (`target_*`), `PUBLIC`,
  `PRIVATE` ja `INTERFACE`, esiasetukset (`CMakePresets.json`),
  rakennus lähdepuun ulkopuolelle ja Ninja.
- **Kirjastot ja riippuvuudet:** staattinen ja jaettu kirjasto,
  soname, viedyt symbolit, hakupolut, `pkg-config` sekä vendorointi ja
  paketinhallinnat (Conan, vcpkg).
- **Yksikkötestaus C:lle:** pieni oma testikehys, CTest ja
  testikaksoset linkkerin avulla.
- **Sanitoijat, kattavuus ja staattinen analyysi:** ASan, UBSan, TSan,
  gcov ja gcovr, clang-tidy, cppcheck ja `-Werror`.
- **CI-putket:** GitHub Actions -työnkulku matriiseineen,
  välimuisteineen ja artefakteineen.
- **Debuggaus:** gdb eräajona kaatumisen ja vahtipisteiden tutkimiseen.

## Esitiedot ja rajaus

Esitietoina ovat taidot *C-kieli*, *Versionhallinta (Git)* ja
*Bash-skriptaus*. C:n syntaksi, osoittimet ja muistinhallinta
oletetaan tutuiksi, samoin Gitin haarat ja komentorivin perusteet.
C-kielen tutoriaalin luku *Työkalut ja testaus* esitteli varoitukset,
gdb:n, sanitoijat ja staattisen analyysin yksittäisen ohjelman
kannalta. Tässä samat työkalut kytketään projektiin: rakennusjärjestelmään,
testeihin ja CI:hin, jossa ne ajetaan jokaisesta muutoksesta.

Objektitiedostojen rakenne, symbolien sidonta ja ABI käsitellään
syvemmin taidossa *Objektitiedostot, linkitys ja ABI*, ja
toimitusketjun turvallisuus (riippuvuuksien eheys, CI:n oikeudet ja
salaisuudet) taidossa *Tietoturva kehitystyössä*. Putkien yleiset
periaatteet, julkaisu ja toimitus ovat taidossa *Jatkuva integraatio ja
toimitus*.

## Esimerkkiprojekti

Kaikki luvut käsittelevät samaa projektia: pientä tilastokirjastoa ja
komentoriviohjelmaa, joka lukee mittausarvot syötteestä ja tulostaa
niiden tunnusluvut. Kirjaston rajapinta on yksi otsake:

```{.c tiedosto="esimerkit/lahde/tilasto.h"}
```

Toteutus käyttää matematiikkakirjaston `sqrt`-funktiota ja C-kirjaston
`qsort`-lajittelua, joten jo tässä on kaksi ulkoista riippuvuutta.
Ohjelma lukee rivit `fgets`-funktiolla, jäsentää ne `strtod`-funktiolla
ja hylkää virheellisen rivin sen sijaan, että ohittaisi sen hiljaa.

Projekti on tarkoituksella pieni, jotta jokaisen työkalun tuloste mahtuu
sivulle. Samat menetelmät toimivat sellaisinaan tuhansien tiedostojen
projektissa; juuri siellä niiden hyöty näkyy.

## Esimerkkien ajaminen

Hakemistossa `esimerkit/` on yksi alihakemisto kutakin lukua kohden
(hakemiston numero on luvun numero) ja yhteinen lähdekoodi hakemistossa
`lahde/`. Esimerkki on komentosarja
`aja.sh`, joka rakentaa, testaa tai analysoi projektin ja tulostaa
tuloksen. Ajaja kopioi esimerkin tilapäishakemistoon, ajaa sen ja
vertaa tulosteen tiedostoon `<esimerkki>.odotettu`:

```{.bash tiedosto="esimerkit/aja-esimerkki.sh"}
```

Kaikki tekstissä näkyvät tulosteet ovat noita odotettuja tulosteita,
joten ne on tuotettu juuri näytetyllä koodilla. Tulosteet ovat
deterministisiä: tilapäishakemiston polku korvataan sanalla `TYO`, ja
kun työkalu tulostaa osoitteita, prosessinumeroita tai aikoja, ne
suodatetaan pois. Suodatus näytetään aina, koska se on itsessään
hyödyllinen taito: CI-lokeja vertaillaan ja haetaan samalla tavalla.

Esimerkit käyttävät GCC 14:ää (`CC=gcc-14`), Clang 20:tä (clang-tidy
ja sumutus), cppcheckiä, CMakea, Ninjaa, gcovria ja gdb:tä. Kehityskontti
(`.devcontainer/rakennus-ja-testaus`) sisältää ne kaikki:

```text
make -C esimerkit            # kaikki esimerkit ja ShellCheck
make -C esimerkit 06-cmake   # yksi esimerkki
make -C esimerkit paivita    # odotetut tulosteet uudelleen
```

Komentosarjojen tyyli seuraa Bash-tutoriaalia: `set -euo pipefail`,
lainausmerkit muuttujien ympärillä ja ShellCheck, joka tarkistaa ne
kaikki osana testejä.
