# Käännösjärjestelmät, testaus ja CI

Tiivis suomenkielinen tutoriaali C-projektin rakentamisesta,
testaamisesta ja jatkuvasta integraatiosta: käännöksen vaiheet, Make ja
automaattiset riippuvuudet, toistettava rakennus, CMake kohteineen ja
esiasetuksineen, staattiset ja jaetut kirjastot sekä `pkg-config`,
yksikkötestaus testikaksosineen, sanitoijat, kattavuus, staattinen
analyysi, GitHub Actions -putket ja gdb eräajona.
Valmis dokumentti: [rakennus-ja-testaus.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rakennus-ja-testaus.pdf),
pikaopas: [rakennus-ja-testaus-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rakennus-ja-testaus-pikaopas.pdf).

## Sisältö

1. Johdanto – esimerkkiprojekti ja esimerkkien ajaminen
2. Käännösprosessi – esikäsittely, käännös, kokoaminen ja linkitys
3. Make – säännöt, muuttujat, valekohteet ja puuttuva riippuvuus
4. Make syvemmin – `-MMD`, mallisäännöt, käännöshakemisto ja `-j`
5. Toistettava rakennus – polut, `SOURCE_DATE_EPOCH` ja arkistot
6. CMake – kohteet, `PUBLIC`/`PRIVATE`/`INTERFACE`, esiasetukset ja Ninja
7. Kirjastot ja riippuvuudet – `.a` ja `.so`, soname, `$ORIGIN`,
   `pkg-config`, vendorointi, Conan ja vcpkg
8. Yksikkötestaus C:lle – oma testikehys, testikaksoset linkkerillä,
   `--wrap` ja CTest
9. Sanitoijat – ASan, UBSan ja TSan testeissä ja CI:ssä
10. Kattavuus – gcov, gcovr, haarakattavuus ja kynnykset
11. Staattinen analyysi – GCC:n varoitukset, clang-tidy, cppcheck ja
    `-Werror`
12. CI-putket – GitHub Actions: matriisi, välimuisti, artefaktit ja
    työnkulun tarkistus
13. Debuggaus gdb:llä – eräajo, kutsupino, vahtipisteet ja ytimen vedos
14. Lopuksi – nyrkkisäännöt, mallit, jatkotaidot ja lähteet

## Esimerkit

Hakemistossa `esimerkit/` on yhteinen tilastoprojekti (`lahde/`) ja
kullekin luvulle hakemisto, jonka `aja.sh` rakentaa, testaa tai
analysoi projektin. Ajaja `aja-esimerkki.sh` ajaa esimerkin
tilapäishakemistossa ja vertaa tulosteen tiedostoon
`<esimerkki>.odotettu`; ShellCheck tarkistaa kaikki komentosarjat.
Tarvittavat työkalut ovat GCC 14, CMake, Ninja, pkg-config, gcovr,
clang-tidy 20, cppcheck, gdb ja check-jsonschema. Kehityskontti
`.devcontainer/rakennus-ja-testaus` sisältää ne kaikki.

```text
make -C esimerkit            # kaikki esimerkit
make -C esimerkit 06-kirjastot
```

## Rakentaminen

```text
make testaa    # rakenne ja esimerkit
make pdf       # tutoriaali ja pikaopas
```

Lisenssi: CC BY-SA 4.0.
