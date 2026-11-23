# Työkalut, testaus ja laatu {.runko-tyokalut}

## Käännös ja ajo

| Tehtävä | Komento |
|---------|---------|
| käännös ajettavaksi JAR:ksi | `kotlinc -Werror -include-runtime -d app.jar src/*.kt` |
| ajo | `java -jar app.jar` tai `kotlin app.jar` |
| skripti | `kotlin skripti.main.kts` (riippuvuudet `@file:DependsOn`) |
| Gradle-projekti | `./gradlew build`, `./gradlew run`, `./gradlew test` |
| jatkuva testaus | `./gradlew test --continuous` |
| riippuvuuspuu | `./gradlew dependencies` |

Gradle Wrapper (`gradlew`) kiinnittää Gradlen version projektiin, ja
`jvmToolchain(21)` kiinnittää JDK:n. Kääntäjän valitsin
`allWarningsAsErrors = true` vastaa komentorivin `-Werror`-valitsinta.
K2-kääntäjä on Kotlin 2.0:sta lähtien oletus.

## Testaus

Kotlin-projektit testataan JUnit 5:llä. `kotlin.test` on ohut kerros,
joka antaa Kotlin-tyyliset väitteet (`assertEquals`, `assertFailsWith`,
`assertNull`) ja annotaatiot (`@Test`) ja toimii myös Kotlin
Multiplatformissa. Testin nimen saa kirjoittaa lauseena
lainausmerkkeihin: ``fun `tyhjä kori maksaa nolla`()``.

Testattava logiikka on omassa paketissaan:

```{.kotlin tiedosto="esimerkit/13-testit/src/Hinnoittelu.kt"}
```

Gradle-projektissa jokainen testi olisi `@Test`-funktio luokassa
`HinnoitteluTest`. Tämän tutoriaalin esimerkeissä ei ole Gradlea, joten
sama testilista ajetaan pienellä ajurilla:

```{.kotlin tiedosto="esimerkit/13-testit/testit/HinnoitteluTesti.kt"}
```

```{.tuloste tiedosto="esimerkit/13-testit/testit.odotettu"}
```

- Testi tarkistaa yhden asian ja kertoo nimessään, mitä odotetaan.
  Rajatapaukset (tyhjä kori, raja-arvo, virheellinen syöte) ovat
  omia testejään.
- `assertFailsWith<T> { }` palauttaa poikkeuksen, joten myös viestin
  voi tarkistaa.
- Vakiokirjaston ulkopuolisia testikirjastoja ovat Kotest (ominaisuus-
  ja BDD-testit), MockK (Kotlin-tietoiset mock-oliot) ja
  `kotlinx-coroutines-test` (`runTest` ja virtuaalinen aika
  korutiinien testaukseen).

## Laatu ja analyysi

| Työkalu | Tehtävä |
|---------|---------|
| ktlint | muotoilu ja tyyli, korjaa automaattisesti (`--format`) |
| detekt | koodin hajut, monimutkaisuus, mahdolliset virheet |
| Kover | testikattavuus Gradle-projektille |
| Dokka | API-dokumentaatio KDoc-kommenteista |
| binary-compatibility-validator | kirjaston julkisen API:n muutokset |

Kotlinin virallinen tyylisuositus (*Kotlin coding conventions*) on
IntelliJ:n ja ktlintin oletus: neljän välilyönnin sisennys, pilkku
viimeisen argumentin perässä monirivisissä listoissa (*trailing comma*)
ja lambdan parametrin nimeäminen pitkissä lohkoissa.

## Debuggaus ja profilointi

Kotlin-koodi on JVM-tavukoodia, joten JVM:n työkalut toimivat: IntelliJ:n
debuggeri, `jcmd`, Java Flight Recorder ja async-profiler. Korutiinien
debuggaukseen IntelliJ näyttää keskeytetyt korutiinit ja niiden pinot.
`kotlinx-coroutines-debug` lisää korutiinin luontikohdan
poikkeuspinoon. Tavukoodin voi tarkastella IntelliJ:n *Show Kotlin
Bytecode* -toiminnolla tai komennolla `javap -c -p`, mikä selittää
esimerkiksi `inline`-funktioiden ja arvoluokkien hinnan.

## Käytännössä

- **Varoitukset virheiksi** (`allWarningsAsErrors`). Kotlin varoittaa
  harvoin turhaan: käyttämätön muuttuja, tarpeeton `?.`, poistuva
  rajapinta.
- **Testaa julkinen rajapinta, ei toteutusta.** Kun toteutus on
  `internal`, saman moduulin testit näkevät sen, mutta testit pysyvät
  vakaampina rajapinnan kautta.
- **Korutiinien testit virtuaaliajalla.** `runTest` ohittaa `delay`-
  kutsut, joten aikakatkaisuja ja uudelleenyrityksiä voi testata
  nopeasti ja deterministisesti.
- **Ei mock-olioita arvoille.** `data class` -oliot luodaan suoraan;
  MockK kuuluu ulkoisten palvelujen rajoille.
- **Hinta:** Gradlen ensimmäinen käännös on hidas. Gradle-demoni,
  käännösvälimuisti (`org.gradle.caching=true`) ja inkrementaalinen
  käännös nopeuttavat seuraavia. `kotlinc` käynnistää JVM:n joka
  kerta, joten komentorivikäännös on aina muutaman sekunnin.
- **Sudenkuoppa:** `kotlinc` ilman `-include-runtime`-valitsinta
  tuottaa JAR:n, jota ei voi ajaa `java -jar`-komennolla, koska
  vakiokirjasto puuttuu.

## Itsearviointi

- Osaat kääntää ja ajaa Kotlin-ohjelman komentoriviltä ja
  Gradle-projektina.
- Osaat kirjoittaa yksikkötestit `kotlin.test`-väitteillä ja testata
  myös virhepolut.
- Osaat ottaa käyttöön ktlintin ja detektin ja asettaa varoitukset
  virheiksi.
- Osaat tarkastella Kotlin-koodista syntyvää tavukoodia ja käyttää
  JVM:n profilointityökaluja.
