---
title: Java
subtitle: Pikaopas kokeneelle kehittäjälle · Java 21
---

# Työkalut

| Tarkoitus | Komento |
|-----------|---------|
| Käännös | `javac --release 21 -Xlint:all -Werror -d out *.java` |
| Ajo | `java -cp out Main`, suoraan `java Main.java` |
| Kokeilu | `jshell` |
| Rakennus | `mvn verify`, `./gradlew build` |
| Testit | `./mvnw test` (JUnit), `./gradlew test` |
| Dokumentaatio | `javadoc -Xdoclint:all -Werror -d doc` |
| Paketointi | `jar --create --file a.jar --main-class Main -C out .` |
| Riippuvuudet | `mvn dependency:tree`, `./gradlew dependencies` |
| Säievedos | `jcmd <pid> Thread.print` |
| Profiili | `jcmd <pid> JFR.start duration=60s filename=a.jfr` |
| Keko | `-Xmx2g`, `-XX:MaxRAMPercentage=75`, `-XX:+UseZGC` |
| Merkistö | `-Dstdout.encoding=UTF-8` |

# Perussyntaksi

```{.java tiedosto="esimerkit/pikaopas.java" osa="perus"}
```

- Primitiivit `int long double boolean char` ovat arvoja, kaikki muu
  viitteitä (voi olla `null`). `var` vain paikallisille muuttujille.
- `==` vertaa viitteitä: oliot `equals`illa. `Integer` `==` toimii vain
  −128…127.
- Kokonaislukujen ylivuoto kiertää: `Math.addExact`, `long`.
  Rahalle `long`-sentit tai `BigDecimal("6.95")`.
- `String.format(Locale.ROOT, ...)` ja `UTF_8` aina eksplisiittisesti.
- `switch`-lauseke `case A, B -> arvo;` on kattava ilman `default`ia.

# Tyypit

```{.java tiedosto="esimerkit/pikaopas.java" osa="tyypit"}
```

- `record`: muuttumaton, `equals`/`hashCode`/`toString` valmiina;
  kompakti konstruktori validoi, `List.copyOf` kokoelmakentille.
- `sealed` + recordit + `switch`-kuviot = summatyyppi; `when` ehtona.
- Luokka: kentät `private final`, konstruktori validoi, `static` kuuluu
  luokalle. Yksi `extends`, monta `implements`; `@Override` aina.
- Luokat `final`; koostaminen periytymisen sijaan. Sisäkkäinen luokka
  `static`, ellei se tarvitse ulompaa oliota.
- `enum`: kiinteä joukko olioita, kentät ja metodit; vertailu `==`.
- Rajapinnassa `default`-metodit; funktionaalinen rajapinta = lambda.
- Geneerisyys poistetaan ajossa. PECS: `? extends T` luetaan,
  `? super T` kirjoitetaan.
- Oma poikkeus ja `LinkedHashMap`-aliluokka tarvitsevat
  `serialVersionUID`:n (`-Xlint:serial`).

# Kokoelmat ja virrat

```{.java tiedosto="esimerkit/pikaopas.java" osa="kokoelmat"}
```

| Tarve | Valinta |
|-------|---------|
| lista, jono | `ArrayList`, `ArrayDeque` (ei `LinkedList`, `Stack`) |
| taulu, joukko | `HashMap`, `LinkedHashMap` (järjestys), `TreeMap` (lajiteltu) |
| enum-avaimet | `EnumMap`, `EnumSet` |
| muuttumaton | `List.of`, `List.copyOf`, `stream.toList()` |
| päivitys | `merge`, `computeIfAbsent`, `getOrDefault` |
| poisto läpikäynnissä | `removeIf`, `Iterator.remove` |
| vertailija | `Comparator.comparing(f).thenComparing(g)` |
| jako | `split(";", -1)`; parametri on säännöllinen lauseke |
| kokoaminen | `StringBuilder`, `String.join`, `Collectors.joining` |
| taulukko | `Arrays.toString`, `equals`, `copyOf`, `sort` |
| tiedosto | `Files.readString`, `writeString`; `Files.lines` `try`-lohkossa |
| aika | `Instant`, `Duration`, `LocalDate`, `ZonedDateTime`; ei `Date` |

# Virheet

```{.java tiedosto="esimerkit/pikaopas.java" osa="virheet"}
```

- Tarkistettu (`IOException`): ympäristö; tarkistamaton
  (`IllegalArgumentException`, `IllegalStateException`): ohjelmointivirhe.
- Kääri syyn kanssa: `new X("mitä tehtiin", e)`. Älä niele.
- Poikkeus maksaa mikrosekunteja (pinojälki): ei ohjausvuoksi.
- `Optional` vain paluuarvoksi: `map`, `orElse`, `orElseThrow`, ei `get`.
- `InterruptedException`: välitä tai `Thread.currentThread().interrupt()`.
- Resurssit: `try (var r = ...) { }`; suljetaan käänteisesti.

# Rinnakkaisuus

```{.java tiedosto="esimerkit/pikaopas.java" osa="saikeet"}
```

```{.tuloste tiedosto="esimerkit/pikaopas.odotettu"}
```

| Tarve | Väline |
|-------|--------|
| paljon I/O-tehtäviä | `Executors.newVirtualThreadPerTaskExecutor()` |
| CPU-työ | `newFixedThreadPool(ytimet)`, `parallel()` |
| jaettu laskuri | `AtomicLong`, `LongAdder` |
| jaettu taulu | `ConcurrentHashMap` (`merge`, `computeIfAbsent`) |
| useampi kenttä | `synchronized`, `ReentrantLock` |
| työjono | `ArrayBlockingQueue` (rajattu, vastapaine) |
| yhdistely | `CompletableFuture.thenCombine`, `orTimeout` |

- Näkyvyys vaatii happens-before-suhteen: lukko, `volatile`, `join`,
  concurrent-rakenteet. Jaa muuttumatonta dataa.
- Java 21: `synchronized` + pitkä odotus sitoo virtuaalisäikeen.

# Hinnat

| Halpaa | Kallista |
|--------|----------|
| olion luonti | suuret pitkäikäiset rakenteet |
| `int[]`, `IntStream` | `List<Integer>` (5–10 ×) |
| `try` ilman heittoa | poikkeuksen luonti |
| virtuaalisäie | käyttöjärjestelmän säie per tehtävä |
| `StringBuilder` | `+` silmukassa |
| lämmin JIT-koodi | käynnistys, lämpeneminen |

# Sudenkuopat

- Muuttuva hajautusavain hukkaa alkion.
- `List.of` ei salli muutoksia eikä `null`ia; `Arrays.asList` on
  kiinteäkokoinen.
- `BigDecimal.equals` vertaa myös skaalaa; käytä `compareTo`.
- `Map.get` palauttaa `null`; purku `int`iksi kaatuu.
- Lambda ei voi heittää tarkistettua poikkeusta; sulkeuman muuttujat
  käytännössä vakioita.
- Mikrovertailu ilman lämmittelyä mittaa tulkkia: JMH.
