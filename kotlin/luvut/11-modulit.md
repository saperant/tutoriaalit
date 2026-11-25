# Paketit, moduulit ja yhteiskäyttö Javan kanssa {.runko-modulit}

Kielen rakenteet on nyt käyty läpi, ja tämä luku siirtyy yhdestä
tiedostosta projektiin: miten koodi jaetaan paketteihin ja
moduuleihin, miten Gradle-projekti rakentuu ja miten Kotlin ja Java
elävät samassa koodikannassa. Viimeinen on käytännössä tärkein, koska
useimmat Kotlin-projektit käyttävät Java-kirjastoja tai alkavat
Java-projektin osana.

## Paketit ja tiedostot

Kotlinin paketti (`package varasto`) vastaa Javan pakettia, mutta
tiedoston paikka hakemistopuussa on vapaa: kääntäjä ei vaadi, että
paketti `a.b` on hakemistossa `a/b`. Käytäntö on silti seurata Javan
rakennetta, kun projektissa on myös Java-koodia. Yhdessä tiedostossa
voi olla useita luokkia ja ylätason funktioita; tiedosto nimetään
pääsisältönsä mukaan.

Ylätason funktiot ja ominaisuudet käännetään luokkaan, jonka nimi tulee
tiedostosta (`Varasto.kt` → `VarastoKt`). Javan staattisia apuluokkia
ei tarvita.

```{.kotlin tiedosto="esimerkit/11-varasto/Tuote.kt"}
```

```{.kotlin tiedosto="esimerkit/11-varasto/Varasto.kt"}
```

```{.kotlin tiedosto="esimerkit/11-varasto/main.kt"}
```

```{.tuloste tiedosto="esimerkit/11-varasto.odotettu"}
```

- Julkinen rajapinta on `interface Varasto`, suljettu tulostyyppi
  `Otto` ja tehdasfunktio `muistivarasto()`. Toteutus on `internal`,
  joten moduulin ulkopuolinen koodi ei voi riippua siitä.
- `internal` näkyy saman **moduulin** sisällä. Moduuli on joukko
  tiedostoja, jotka käännetään yhdessä: Gradle-aliprojekti,
  Maven-moduuli tai yksi `kotlinc`-kutsu.
- Paketti `varasto.malli` ei tunne pakettia `varasto`. Riippuvuudet
  kulkevat yhteen suuntaan, pääohjelmasta kohti mallia.
- Pääohjelma on ohut: se kokoaa osat ja tulostaa. Logiikkaa voi
  testata ilman sitä (luku 13).
- Julkiset tyypit ja funktiot on dokumentoitu KDoc-kommenteilla
  `/** … */` (luku 13).

```{.dot otsikko="Esimerkin paketit. Nuoli osoittaa riippuvuuden suunnan. `Muistivarasto` on `internal`, joten moduulin ulkopuolinen koodi näkee paketista `varasto` vain rajapinnan, tulostyypin ja tehdasfunktion."}
digraph {
  rankdir=LR; nodesep=0.3; ranksep=0.8;
  node [fontsize=9, height=0.4];
  main [label="main.kt\npääohjelma"];
  subgraph cluster_v { label="paketti varasto"; fontsize=10; color="#D9E0E3";
    api [label="Varasto, Otto\nmuistivarasto()"];
    impl [label="internal\nMuistivarasto", style="rounded,dashed", fillcolor="white"]; }
  subgraph cluster_m { label="paketti varasto.malli"; fontsize=10; color="#D9E0E3";
    malli [label="Koodi, Tuote"]; }
  main -> api; impl -> api [style=dashed, label="toteuttaa"];
  api -> malli; main -> malli;
}
```

## Projektin rakenne

Kotlin-projekti käännetään yleensä Gradlella. Tavallinen rakenne on
sama kuin Javassa:

```
tilaukset/
  settings.gradle.kts         # aliprojektit
  build.gradle.kts            # liitännäiset, riippuvuudet, JVM-versio
  gradle/libs.versions.toml   # versioluettelo
  src/main/kotlin/fi/esim/tilaukset/...
  src/test/kotlin/fi/esim/tilaukset/...
```

Käännösskripti `build.gradle.kts` on Kotlinia (luku 10 selittää,
miten tällainen DSL on tehty). Seuraava luonnos näyttää tyypillisen
sisällön; sitä ei käännetä tämän tutoriaalin testeissä, koska
esimerkit käännetään suoraan `kotlinc`-kääntäjällä:

```
plugins {
    kotlin("jvm") version "2.4.21"
    application
}
kotlin { jvmToolchain(21) }
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
    testImplementation(kotlin("test"))
}
tasks.test { useJUnitPlatform() }
application { mainClass = "fi.esim.tilaukset.MainKt" }
```

Suuremmassa projektissa jako aliprojekteihin (`:malli`, `:palvelu`,
`:sovellus`) tekee `internal`-näkyvyydestä ja riippuvuuksien suunnasta
käännösajan sääntöjä.

## Yhteiskäyttö Javan kanssa

Kotlin kutsuu Javaa suoraan: Javan getterit näkyvät ominaisuuksina,
SAM-rajapinnat toteutetaan lambdalla ja Javan kokoelmat ovat Kotlinin
kokoelmia. Toiseen suuntaan Kotlin-koodi näkyy Javalle tavallisina
luokkina ja metodeina, ja annotaatiot hienosäätävät tulosta.

```{.kotlin tiedosto="esimerkit/11-java.kt"}
```

```{.tuloste tiedosto="esimerkit/11-java.odotettu"}
```

| Annotaatio | Vaikutus Java-kutsujalle |
|------------|---------------------------|
| `@JvmOverloads` | oletusargumenteista ylikuormitetut metodit |
| `@JvmStatic` | `companion object` -jäsen staattisena metodina |
| `@JvmField` | ominaisuus julkisena kenttänä ilman getteriä |
| `@JvmName("nimi")` | metodin tai tiedostoluokan nimi |
| `@Throws(X::class)` | `throws`-määre, jotta Java voi siepata tarkistetun poikkeuksen |
| `@JvmRecord` | `data class` Javan `record`-luokkana |

Java-kutsujalle näkyvät myös Kotlinin null-tiedot: kääntäjä lisää
`@NotNull`- ja `@Nullable`-annotaatiot ja tarkistaa julkisten
funktioiden ei-null-parametrit ajonaikana.

## Käytännössä

- **Julkinen rajapinta pieneksi, toteutus `internal`-näkyvyydelle.**
  Kirjaston käyttäjä riippuu vain rajapinnasta ja tehdasfunktiosta,
  joten toteutuksen voi vaihtaa.
- **Kirjasto ja ohut pääohjelma.** Logiikka kuuluu paketteihin,
  joita testataan; `main` vain kokoaa ja käynnistää.
- **Versioluettelo (`libs.versions.toml`)** pitää riippuvuuksien
  versiot yhdessä paikassa monen aliprojektin projektissa.
- **Kun Java kutsuu Kotlinia**, lisää rajapintaan `@JvmOverloads`,
  `@JvmStatic` ja `@Throws`, jotta Java-kutsujan koodi on luontevaa.
  Kun Kotlin kutsuu Javaa, kääri Java-rajapinta ohueksi Kotlin-
  kerrokseksi, jossa nullable-tiedot ovat tarkkoja.
- **Hinta:** julkisen funktion jokainen ei-null-parametri tarkistetaan
  ajonaikana (`Intrinsics.checkNotNullParameter`). Tarkistus on halpa,
  ja JIT poistaa sen usein.
- **Sudenkuoppa:** `internal`-jäsenen nimi sekoitetaan tavukoodissa,
  joten Java-koodi näkee sen oudolla nimellä. Se ei ole tarkoitettu
  Javan käyttöön.

## Itsearviointi

- Osaat jakaa ohjelman paketteihin niin, että riippuvuudet kulkevat
  yhteen suuntaan, ja käyttää `internal`-näkyvyyttä.
- Osaat kertoa, mihin luokkaan ylätason funktiot käännetään.
- Osaat kirjoittaa Gradle-projektin perusrakenteen ja
  `build.gradle.kts`-tiedoston Kotlin-sovellukselle.
- Osaat käyttää `@JvmOverloads`-, `@JvmStatic`-, `@JvmField`- ja
  `@Throws`-annotaatioita Java-yhteiskäytössä.
