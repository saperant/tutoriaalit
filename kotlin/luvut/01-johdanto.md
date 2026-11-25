# Johdanto {.runko-johdanto}

Kotlin on JetBrainsin kehittämä staattisesti tyypitetty kieli, joka
käännetään ensisijaisesti Javan virtuaalikoneelle (JVM). JetBrains
julkisti kielen vuonna 2011, koska sen omat IntelliJ-työkalut olivat
kasvaneet Javalla suuriksi ja raskaiksi ylläpitää. Versio 1.0 ilmestyi
vuonna 2016. Kotlin on nimetty Suomenlahdella sijaitsevan Kotlinsaaren
mukaan, samaan tapaan kuin Java on nimetty saaren mukaan.

Kotlinin tavoite on käytännöllisyys: sama JVM, samat kirjastot ja sama
työkaluketju kuin Javassa, mutta vähemmän toistoa ja vähemmän
virheluokkia. Kieli poistaa `null`-viittausvirheet tyyppijärjestelmällä,
tekee arvo-olioista ja suljetuista hierarkioista yksirivisiä ja tuo
funktionaalisen ohjelmoinnin välineet ilman uutta ajonaikaista
ympäristöä. Kotlin-koodi kutsuu Javaa ja Java Kotlinia suoraan, joten
kielen voi ottaa käyttöön tiedosto kerrallaan.

## Esitiedot ja rajaus

Esitietona on taito *Java*: luokat ja rajapinnat, geneerisyys,
kokoelmat, poikkeukset sekä JVM:n muistimalli, roskienkeruu ja säikeet
oletetaan tunnetuiksi. Tämä tutoriaali kertoo, mikä Kotlinissa on
toisin, ja vertaa ratkaisuja Javaan.

Tutoriaali ei käsittele seuraavia aiheita:

- JVM:n muistimalli, roskienkeruu, JIT ja `java.util.concurrent`:
  taito *Java*
- rinnakkaisuuden yleiset käsitteet: taito *Rinnakkaisohjelmointi*
- Android ja Jetpack Compose: taito *Android-sovellukset*
- palvelinkehykset (Spring Boot, Ktor) ja tietokannat: taito
  *Taustapalvelut*
- Kotlin Multiplatform, Kotlin/Native ja Kotlin/JS.

## Mihin Kotlin sopii ja mihin ei

Kotlin on vakiintunut erityisesti

- Android-sovelluksiin: Google tuki Kotlinia virallisesti vuodesta 2017
  ja julisti sen Androidin ensisijaiseksi kieleksi vuonna 2019. Jetpack
  Compose -käyttöliittymäkirjasto on pelkkää Kotlinia.
- palvelinsovelluksiin: Spring Boot tukee Kotlinia suoraan, ja
  JetBrainsin Ktor on Kotlinille suunniteltu verkkokehys.
- käännösskripteihin: Gradlen Kotlin DSL (`build.gradle.kts`) on uusien
  Gradle-projektien oletus.
- monialustaiseen kehitykseen: Kotlin Multiplatform kääntää saman
  liiketoimintalogiikan JVM:lle, Androidille, iOS:lle (Kotlin/Native),
  selaimeen (Kotlin/JS, Wasm) ja palvelimelle.

Kotlin ei ole paras valinta, kun

- ohjelman on käynnistyttävä millisekunneissa tai mahduttava pieneen
  muistiin: JVM:n käynnistys ja lämpeneminen maksavat. Kotlin/Native ja
  GraalVM:n natiivikäännös auttavat, mutta Go, Rust ja C ovat
  luontevampia komentorivityökaluihin ja sulautettuihin laitteisiin.
- tarvitaan laitteistonläheistä koodia tai ennustettavaa viivettä ilman
  roskienkeruuta
- tehtävä on data-analyysiä tai koneoppimista, joiden ekosysteemi on
  Pythonissa
- tiimi ja koodikanta ovat Javaa, eikä Kotlinin hyöty ylitä kahden kielen
  ylläpidon hintaa. Moderni Java (recordit, sealed-tyypit, `switch`-
  hahmontunnistus, virtuaalisäikeet) on kaventanut eroa.

## Versiot ja toteutukset

Kotlin julkaisee kieliversion (2.x.0) puolen vuoden välein ja
työkaluversion (2.x.20) niiden välissä. Versio 2.0 (2024) toi uuden
K2-kääntäjän, joka on aiempaa nopeampi ja jonka tyyppipäättely on
johdonmukaisempi. Kieltä kehittää JetBrains, ja Kotlin Foundation
(JetBrains ja Google) valvoo sen kehitystä. Kielen määrittelee
*Kotlin Language Specification*.

Tämän tutoriaalin esimerkit on testattu Kotlin 2.4.21:llä ja JDK 21:llä.
Kotlin/JVM tuottaa tavallisia `.class`-tiedostoja, joten ohjelma tarvitsee
ajonaikana JVM:n ja Kotlinin vakiokirjaston (`kotlin-stdlib`, noin
1,8 Mt).

## Työkalut

| Työkalu | Tehtävä |
|---------|---------|
| `kotlinc` | komentorivikääntäjä (`-include-runtime -d ohjelma.jar`) |
| Gradle (`build.gradle.kts`) | projektien käännös, riippuvuudet, testit |
| Maven (`kotlin-maven-plugin`) | sama Maven-projekteissa |
| IntelliJ IDEA, Android Studio | ensisijaiset editorit, refaktorointi |
| ktlint, detekt | tyyli- ja staattinen analyysi |
| Dokka | API-dokumentaatio KDoc-kommenteista |

Tämän tutoriaalin esimerkit ovat yksittäisiä tiedostoja, jotka
käännetään varoitukset virheinä ja ajetaan näin:

```
kotlinc -Werror -include-runtime -d myynti.jar 01-myynti.kt
java -jar myynti.jar < 01-myynti.syote
```

Oikea projekti käyttää Gradlea (luvut 11 ja 13). Kehityskontissa
(`.devcontainer/kotlin`) on JDK 21 ja `kotlinc`. Korutiini- ja
testiesimerkit tarvitsevat kääntäjän mukana tulevia kirjastoja, ja ne
käännetään ja ajetaan komennolla `make` hakemistossa `esimerkit`.

## Ensimmäinen ohjelma

Ohjelma lukee myyntirivejä syötteestä ja tulostaa tuotteittaiset
summat suurimmasta pienimpään.

```{.kotlin tiedosto="esimerkit/01-myynti.kt"}
```

Syöte ja tuloste:

```{.tuloste tiedosto="esimerkit/01-myynti.syote"}
```

```{.tuloste tiedosto="esimerkit/01-myynti.odotettu"}
```

- `data class` saa automaattisesti `equals`-, `hashCode`-, `toString`-
  ja `copy`-metodit. Javassa vastaava on `record`.
- Funktio voi olla tiedoston ylätasolla; luokkaa ei tarvita.
  `fun main()` on ohjelman aloituskohta.
- Paluutyyppi `Myynti?` sallii arvon `null`. `?: return null` palaa
  heti, jos jäsennys epäonnistuu: virheellinen rivi ei kaada ohjelmaa.
- Rahaa ei lasketa liukulukuina vaan sentteinä (`Long`); desimaalit
  jäsennetään `BigDecimal`-tyypiksi.
- `generateSequence(::readlnOrNull)` lukee rivejä, kunnes syöte loppuu.
  `::readlnOrNull` on funktioviite.
- `groupBy`, `mapValues`, `sumOf` ja `sortedByDescending` korvaavat
  silmukat ja apumuuttujat.
- `"${...}"` on merkkijonopohja, ja `for ((tuote, sentit) in ...)` purkaa
  parin kahdeksi muuttujaksi.
- `main`-funktion ensimmäinen rivi asettaa tulosteen merkistöksi UTF-8.
  JVM valitsee `System.out`-virran merkistön käyttöjärjestelmän
  lokaalista, ja ympäristössä ilman lokaalia (konteissa ja CI:ssä usein
  `POSIX`) ä ja € tulostuisivat kysymysmerkkeinä. Siksi rivi on jokaisen
  ääkkösiä tulostavan esimerkin alussa. Saman voi tehdä ajaessa:
  `java -Dstdout.encoding=UTF-8 -jar ...`.

## Tutoriaalin rakenne

Luku 2 on tarkoitettu Java-kehittäjälle, joka haluaa nopean
yleiskuvan. Luvut 3 ja 4 käsittelevät tyypit ja null-turvallisuuden,
luku 5 funktiot ja ohjausrakenteet, luku 6 muistin, resurssit ja
abstraktioiden hinnan, luku 7 kokoelmat ja luku 8 luokat ja
geneerisyyden. Luku 9 käsittelee virheet, luku 10 DSL:t ja delegoinnin,
luku 11 paketit ja yhteiskäytön Javan kanssa, luku 12 rinnakkaisuuden
ja korutiinit ja luku 13 työkalut ja testauksen. Luku 14 kokoaa mallit,
hinnat ja lähteet.
