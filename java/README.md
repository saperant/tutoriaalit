# Java

Tiivis suomenkielinen Java-tutoriaali ohjelmoinnin perusteet osaavalle
(Java 21). Valmis dokumentti: [java.pdf](java.pdf), pikaopas:
[java-pikaopas.pdf](java-pikaopas.pdf).

## Sisältö

1. Johdanto – historia, käyttökohteet, JDK ja työkalut, ensimmäinen
   ohjelma
2. Java kokeneelle – ajattelutapa, vastaavuudet Pythoniin, C++:aan ja
   C#:iin, hinnat, sudenkuopat
3. Tyypit, lausekkeet ja syöte – ylivuoto, `BigDecimal`, kieliasetus ja
   merkistö, UTF-16, syötteen jäsennys
4. Ohjausrakenteet, metodit ja lambdat – `switch`-lauseke, tilakone,
   funktionaaliset rajapinnat, sulkeumat
5. Muisti, roskienkeruu ja JIT – `==` ja `equals`, boksaus,
   muistivuodot, `try`-with-resources, lämpeneminen
6. Kokoelmat, merkkijonot ja virrat – toteutusten valinta,
   muuttumattomuus, hajautusavaimet, `Collectors`
7. Luokat, recordit, rajapinnat ja geneerisyys – `sealed` ja kuviot,
   koristelija, rakentaja, PECS
8. Poikkeukset ja virheenkäsittely – kääriminen, lambdat, poikkeusten
   hinta, `Optional`, tulostyyppi
9. Paketit, modulit ja rakennus – näkyvyys, konstruktori-injektio,
   JPMS, Maven ja Gradle
10. Säikeet, virtuaalisäikeet ja `java.util.concurrent` – jaettu tila,
    jonot, `CompletableFuture`
11. Työkalut, testaus ja laatu – `-Xlint`, testit ja JUnit, JMH, JFR,
    staattinen analyysi
12. Lopuksi – mallit, nyrkkisäännöt, hinnat ja lähteet

## Esimerkit

Kaikki koodi on hakemistossa `esimerkit/`, ja tekstiin se sisällytetään
tiedostoista. `make testaa` kääntää jokaisen esimerkin komennolla
`javac -Xlint:all -Werror`, ajaa sen ja vertaa tulostetta
`.odotettu`-tiedostoon. `.ei-kaanny`-esimerkkien on epäonnistuttava
käännöksessä ja `.kaatuu`-esimerkkien ajossa.

Yksittäisen esimerkin voi ajaa suoraan lähdetiedostosta:

```
cd esimerkit
java 03-syote.java < 03-syote.syote
javac -d /tmp/luokat 09-tilaukset/*.java && java -cp /tmp/luokat Main
```

Kehityskontti on konfiguraatiossa `.devcontainer/java` (OpenJDK 21).

## Rakentaminen

```
make testaa     # rakenteen tarkistus ja esimerkkien testit
make pdf        # java.pdf ja java-pikaopas.pdf
```
