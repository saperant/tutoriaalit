# Java

Tiivis suomenkielinen Java-tutoriaali ohjelmoinnin perusteet osaavalle
(Java 21). Valmis dokumentti: [java.pdf](https://saperant.github.io/tutoriaalit/materiaalit/java.pdf), pikaopas:
[java-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/java-pikaopas.pdf).

## Sisältö

1. Johdanto – historia, käyttökohteet, esitiedot ja rajaus, JDK ja
   työkalut, ensimmäinen ohjelma
2. Java kokeneelle – ajattelutapa, vastaavuudet Pythoniin, C++:aan ja
   C#:iin, hinnat, sudenkuopat
3. Tyypit, lausekkeet ja syöte – ylivuoto, `BigDecimal`, kieliasetus ja
   merkistö, UTF-16, taulukot, syötteen jäsennys
4. Ohjausrakenteet, metodit ja lambdat – `switch`-lauseke, tilakone,
   funktionaaliset rajapinnat, sulkeumat
5. Luokat ja oliot – kentät ja konstruktorit, kapselointi, rajapinnat,
   periytyminen ja `abstract`, `enum`, sisäkkäiset luokat, annotaatiot
6. Muisti, roskienkeruu ja JIT – pino ja keko, `==` ja `equals`,
   boksaus, muistivuodot, `try`-with-resources, lämpeneminen
7. Kokoelmat, virrat, tiedostot ja aika – toteutusten valinta,
   muuttumattomuus, hajautusavaimet, `Collectors`, `java.nio.file`,
   `java.time`
8. Recordit, suljetut hierarkiat ja geneerisyys – `sealed` ja kuviot,
   koristelija, rakentaja, PECS
9. Poikkeukset ja virheenkäsittely – kääriminen, lambdat, poikkeusten
   hinta, `Optional`, tulostyyppi
10. Pakkaukset, moduulit ja rakennus – näkyvyys, konstruktori-injektio,
    JPMS, Maven ja Gradle, JAR
11. Säikeet, virtuaalisäikeet ja `java.util.concurrent` – jaettu tila,
    jonot, `CompletableFuture`
12. Työkalut, testaus ja laatu – `-Xlint`, Javadoc, JUnit, JMH, JFR,
    staattinen analyysi
13. Lopuksi – mallit, nyrkkisäännöt, hinnat, jatkotaidot ja lähteet

## Esimerkit

Kaikki koodi on hakemistossa `esimerkit/`, ja tekstiin se sisällytetään
tiedostoista. `make testaa` kääntää jokaisen esimerkin komennolla
`javac -Xlint:all -Werror`, ajaa sen ja vertaa tulostetta
`.odotettu`-tiedostoon. `.ei-kaanny`-esimerkkien on epäonnistuttava
käännöksessä ja `.kaatuu`-esimerkkien ajossa. Lisäksi
`esimerkit/Makefile` ajaa Maven-projektin `10-toimitus` JUnit-testit
ja tarkistaa sen Javadoc-kommentit (`javadoc -Xdoclint:all -Werror`).
Maven Wrapper lataa Mavenin ja JUnitin ensimmäisellä kerralla, joten
se tarvitsee verkkoyhteyden.

Yksittäisen esimerkin voi ajaa suoraan lähdetiedostosta:

```
cd esimerkit
java 03-syote.java < 03-syote.syote
javac -d /tmp/luokat 10-tilaukset/*.java && java -cp /tmp/luokat Main
(cd 10-toimitus && ./mvnw test)
```

Kehityskontti on konfiguraatiossa `.devcontainer/java` (OpenJDK 21).

## Rakentaminen

```
make testaa     # rakenteen tarkistus ja esimerkkien testit
make pdf        # java.pdf ja java-pikaopas.pdf
```

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
