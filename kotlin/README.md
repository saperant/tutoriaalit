# Kotlin

Tiivis suomenkielinen Kotlin-tutoriaali Javan osaavalle (Kotlin 2.4,
JDK 21). Valmis dokumentti: [kotlin.pdf](kotlin.pdf), pikaopas:
[kotlin-pikaopas.pdf](kotlin-pikaopas.pdf).

## Sisältö

1. Johdanto – käyttökohteet, versiot, työkalut, ensimmäinen ohjelma
2. Kotlin kokeneelle – ajattelutapa, vastaavuudet Javaan, hinnat,
   sudenkuopat
3. Tyypit, lausekkeet ja syöte – muunnokset, `when`, `readlnOrNull`
4. Null-turvallisuus – `?.`, `?:`, älykäs tyyppimuunnos, alustatyypit
5. Ohjausrakenteet ja funktiot – välit, lambdat, laajennukset,
   scope-funktiot
6. Muisti, resurssit ja abstraktioiden hinta – `use`, arvoluokat,
   `inline` ja `reified`
7. Kokoelmat ja merkkijonot – vain luku -rajapinnat, ryhmittely,
   `Sequence`
8. Luokat, suljetut hierarkiat ja geneerisyys – `data class`, `sealed`,
   varianssi
9. Virheenkäsittely – `require`/`check`, `runCatching`, virheet tyyppeinä
10. DSL:t, operaattorit ja delegointi
11. Paketit, moduulit ja yhteiskäyttö Javan kanssa
12. Rinnakkaisuus ja korutiinit – virtuaalisäikeet, `suspend`,
    rakenteinen rinnakkaisuus, `Flow`
13. Työkalut, testaus ja laatu – Gradle, `kotlin.test`, ktlint, detekt
14. Lopuksi – mallit, nyrkkisäännöt, hinnat, kirjastot ja lähteet

## Rakentaminen

```text
make testaa   # kotlinc -Werror, esimerkkien ajo ja esimerkit/Makefile
make pdf      # rakentaa kotlin.pdf:n ja kotlin-pikaopas.pdf:n
```

Yksittäiset esimerkit testaa yhteinen testaaja. Korutiini- ja
testiesimerkit (`esimerkit/12-korutiinit`, `esimerkit/13-testit`)
tarvitsevat `kotlinc`-jakelun mukana tulevat kirjastot, ja ne
testataan tiedostolla `esimerkit/Makefile`. Kehityskontti:
`.devcontainer/kotlin`.
