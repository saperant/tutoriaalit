# Työkalut, testaus ja laatu {.runko-tyokalut}

Kotlin käyttää JVM:n työkaluketjua, joten Javan debuggerit,
profiloijat ja rakennustyökalut toimivat sellaisinaan (taito *Java*).
Tämä luku kertoo Kotlinin omat lisät: kääntäjän ja Gradlen käytön,
testauksen `kotlin.test`-kirjastolla, dokumentaation ja staattisen
analyysin. Yleiset testaus- ja CI-käytännöt ovat taidossa
*Käännösjärjestelmät, testaus ja CI*.

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

Kotlin-projektit testataan JUnitilla. `kotlin.test` on ohut kerros,
joka antaa Kotlin-tyyliset väitteet (`assertEquals`, `assertFailsWith`,
`assertNull`) ja annotaatiot (`@Test`) ja toimii myös Kotlin
Multiplatformissa. Testin nimen saa kirjoittaa lauseena
lainausmerkkeihin: ``fun `tyhjä kori maksaa nolla`()``.

Testattava logiikka on omassa paketissaan:

```{.kotlin tiedosto="esimerkit/13-testit/src/Hinnoittelu.kt"}
```

Gradle-projektissa jokainen testi olisi `@Test`-funktio luokassa
`HinnoitteluTest`, ja JUnit etsisi ja ajaisi ne. Tämän tutoriaalin
esimerkeissä ei ole Gradlea eikä JUnitia, joten sama testilista ajetaan
pienellä omalla ajurilla. Väitteet ovat oikeaa `kotlin.test`-kirjastoa,
joten testien sisältö siirtyy JUnit-projektiin sellaisenaan:

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

## KDoc ja Dokka

Kotlinin dokumentaatiokommentti on *KDoc*: `/** … */` esittelyn edellä,
kuten Javadoc, mutta muotoilu on Markdownia eikä HTML:ää. Luvun 11
varastoesimerkin julkiset tyypit on dokumentoitu KDocilla. Rajapinnan
`Varasto` kommenteissa (luku 11) ovat `@param` ja `@return`;
tietotyypeissä kuvataan ominaisuudet ja konstruktorin poikkeus:

```{.kotlin tiedosto="esimerkit/11-varasto/Tuote.kt"}
```

Ensimmäinen kappale on yhteenveto. Viittaus toiseen nimeen
kirjoitetaan hakasulkeisiin (`[arvo]`, `[Otto.Ok]`, `[muistivarasto]`),
ja työkalu tekee siitä linkin. Tageja on vähemmän kuin Javadocissa:

| Tagi | Tarkoitus |
|------|-----------|
| `@param nimi` | funktion parametri tai luokan tyyppiparametri |
| `@return` | paluuarvo |
| `@throws Tyyppi` | poikkeus ja ehto, jolla se heitetään |
| `@property nimi` | pääkonstruktorissa esitelty ominaisuus |
| `@constructor` | pääkonstruktorin kuvaus |
| `@receiver` | laajennusfunktion vastaanottaja |
| `@sample polku.funktio` | upottaa nimetyn funktion rungon esimerkiksi |
| `@see`, `@since` | viittaus ja versio |

Kotlinissa ei ole tarkistettuja poikkeuksia, joten `@throws` on ainoa
paikka, josta kutsuja näkee, mitä funktio voi heittää. `@sample`
viittaa oikeaan, käännettävään funktioon, esimerkiksi testiin, jolloin
dokumentaation esimerkki ei vanhene huomaamatta. Vanhentunut rajapinta
merkitään annotaatiolla `@Deprecated`, ei tagilla.

HTML-dokumentaation tuottaa *Dokka*, joka lukee myös samassa
projektissa olevan Java-koodin Javadoc-kommentit. Se on
Gradle-liitännäinen. Seuraavaa luonnosta ei ajeta tämän tutoriaalin
testeissä; tehtävien ja asetusten nimet on syytä tarkistaa käytetyn
Dokka-version ohjeesta, koska ne muuttuivat versiossa 2:

```
plugins {
    id("org.jetbrains.dokka") version "2.3.0"
}
kotlin {
    explicitApi()            // julkinen näkyvyys ja tyypit kirjoitettava
}
dokka {
    dokkaSourceSets.configureEach {
        reportUndocumented.set(true)   // varoitus puuttuvasta KDocista
    }
    dokkaPublications.configureEach {
        failOnWarning.set(true)        // varoitus pysäyttää CI:n
    }
}
```

`./gradlew dokkaGenerate` kirjoittaa sivut hakemistoon `build/dokka`.
`explicitApi()` on kirjastoille tarkoitettu kääntäjän tila, jossa
jokaisen julkisen esittelyn näkyvyys ja paluutyyppi on kirjoitettava
näkyviin; se estää toteutuksen yksityiskohtien päätymisen rajapintaan
vahingossa. Kommentti kuvaa sopimuksen: mitä funktio vaatii, mitä se
palauttaa ja milloin se epäonnistuu. Yleiset periaatteet, kuten
rajapintadokumentaation tuottaminen koodista ja dokumentaation testaus,
käsitellään taidossa *Tekninen dokumentaatio*.

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
- **KDoc julkiselle rajapinnalle.** Kirjastossa `explicitApi()` ja
  Dokkan `reportUndocumented` pitävät rajapinnan tarkoituksellisena ja
  dokumentoituna. Sovelluksen sisäinen koodi ei tarvitse kommenttia
  jokaiseen funktioon.
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
- Osaat kirjoittaa KDoc-kommentin tageineen ja viittauksineen ja
  kertoa, miten Dokka tuottaa siitä dokumentaation.
- Osaat tarkastella Kotlin-koodista syntyvää tavukoodia ja käyttää
  JVM:n profilointityökaluja.
