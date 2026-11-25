# C-kieli

Tiivis suomenkielinen johdatus C-ohjelmointiin C17- ja C23-standardien
mukaan. Valmis dokumentti: [c-kieli.pdf](https://saperant.github.io/tutoriaalit/materiaalit/c-kieli.pdf).

## Sisältö

1. Johdanto – standardit, työkalut, käännösprosessi
2. C kokeneelle – erot muihin kieliin, sudenkuopat
3. Tyypit ja lausekkeet – kokonaisluvut, `<stdint.h>`, muunnokset,
   bittioperaatiot, operaattorien etusija, liukuluvut, `constexpr`
4. Ohjausrakenteet ja funktiot – prototyypit, arvovälitys, `static`
5. Osoittimet – olion elinaika, osoitinaritmetiikka, `const`, `void *`,
   funktio-osoittimet, `qsort`
6. Rakenteet, luettelot ja unionit – nimetyt alustimet, muistiasettelu,
   ketjutetut rakenteet, merkityt unionit
7. Taulukot ja merkkijonot – taulukkoparametrit, `<string.h>`,
   `snprintf`, `strtol`, viipale
8. Dynaaminen muistinhallinta – `malloc`, `realloc`, omistus, kasvava
   taulukko, areena, tyypilliset virheet
9. Esikääntäjä ja ohjelman jakaminen tiedostoihin – makrot, `_Generic`,
   X-makrot, otsikkotiedostot ja rajapintakommentit, epätäydelliset
   tyypit, rajapinnat funktio-osoittimilla
10. Syöte, tuloste ja tiedostot – `argv`, `fgets`, teksti- ja
    binääritiedostot, omat muotoilufunktiot (`<stdarg.h>`)
11. Virheenkäsittely – virhekoodit, `goto`-siivous, `assert`,
    määrittelemätön käyttäytyminen, `<stdckdint.h>`
12. Säikeet ja atomiset operaatiot – `<threads.h>`, `<stdatomic.h>`
13. Työkalut ja testaus – varoitukset, gdb, sanitoijat, staattinen
    analyysi, profilointi, yksikkötestaus
14. Lopuksi – C23-tiivistelmä, mallit, nyrkkisäännöt, lähteet

## Rakentaminen

```text
make testaa   # kääntää ja ajaa esimerkit (GCC 14 ja Clang 20)
make pdf      # rakentaa c-kieli.pdf:n
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
