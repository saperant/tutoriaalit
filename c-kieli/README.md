# C-kieli

Tiivis suomenkielinen johdatus C-ohjelmointiin C17- ja C23-standardien
mukaan. Valmis dokumentti: [c-kieli.pdf](https://saperant.github.io/tutoriaalit/materiaalit/c-kieli.pdf).

## Sisältö

1. Johdanto – standardit, työkalut, käännösprosessi
2. Tyypit ja lausekkeet – kokonaisluvut, `<stdint.h>`, muunnokset,
   liukuluvut, `constexpr`, `bool`
3. Ohjausrakenteet ja funktiot – prototyypit, arvovälitys, `static`
4. Osoittimet – osoitinaritmetiikka, `const`, `void *`,
   funktio-osoittimet, `qsort`
5. Taulukot ja merkkijonot – taulukkoparametrit, `<string.h>`,
   `snprintf`, `strtol`
6. Dynaaminen muistinhallinta – `malloc`, `realloc`, omistus, kasvava
   taulukko, tyypilliset virheet
7. Rakenteet, luettelot ja unionit – nimetyt alustimet, muistiasettelu,
   merkityt unionit
8. Esikääntäjä ja ohjelman jakaminen tiedostoihin – makrot, `_Generic`,
   otsikkotiedostot, epätäydelliset tyypit
9. Syöte, tuloste ja tiedostot – `argv`, `fgets`, teksti- ja
   binääritiedostot
10. Virheenkäsittely – virhekoodit, `goto`-siivous, `assert`,
    määrittelemätön käyttäytyminen, `<stdckdint.h>`
11. Säikeet ja atomiset operaatiot – `<threads.h>`, `<stdatomic.h>`
12. Lopuksi – C23-tiivistelmä, nyrkkisäännöt, lähteet

## Rakentaminen

```text
make testaa   # kääntää ja ajaa esimerkit (GCC 14 ja Clang 20)
make pdf      # rakentaa c-kieli.pdf:n
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
