# Työkalut, testaus ja laatu {.runko-tyokalut}

Kieli on nyt käyty läpi. Tämä luku kertoo välineet, joilla
Java-koodia käännetään, dokumentoidaan, testataan, mitataan ja
tarkkaillaan tuotannossa. Yleiset käännös-, testaus- ja CI-käytännöt
käsitellään taidossa *Käännösjärjestelmät, testaus ja CI*; tässä ovat
Javan omat työkalut. Esimerkkinä on luvun 10 Maven-projekti
`esimerkit/10-toimitus`.

## Kääntäjä ja JDK:n työkalut

| Komento | Tarkoitus |
|---------|-----------|
| `javac --release 21 -Xlint:all -Werror` | käännös kaikilla varoituksilla |
| `java -ea` | `assert`-lauseet käyttöön (oletuksena pois) |
| `jshell` | kokeile rajapintaa: `jshell> "a,b,,".split(",").length` |
| `javadoc -d doc` | dokumentaatio `/** */`-kommenteista |
| `jdb`, IDE:n debuggeri | pysäytyskohdat; etädebuggaus `-agentlib:jdwp=...` |
| `jcmd <pid> Thread.print` | säikeiden pinot: lukkiutumisen ja jumien selvitys |
| `jcmd <pid> GC.heap_info` | keon tila |
| `java -XX:+HeapDumpOnOutOfMemoryError` | keon vedos muistin loppuessa; analyysi Eclipse MAT:lla |
| `jcmd <pid> JFR.start duration=60s filename=a.jfr` | Java Flight Recorder: profiili tuotannosta pienellä hinnalla |
| `jfr print --events jdk.ExecutionSample a.jfr` | JFR-tallenteen tapahtumat; graafisesti JDK Mission Control |

`-Xlint:all` kannattaa pitää päällä kaikissa projekteissa. Se varoittaa
muun muassa raakatyypeistä, tarkistamattomista muunnoksista,
puuttuvasta `serialVersionUID`-kentästä, vanhentuneiden rajapintojen
käytöstä, `switch`-haarojen läpivalumisesta ja konstruktorista
karkaavasta `this`-viitteestä.

## Javadoc

Javadoc-kommentti `/** … */` kirjoitetaan luokan, metodin tai kentän
eteen, ja työkalu `javadoc` tuottaa kommenteista HTML-dokumentaation.
JDK:n oma rajapintadokumentaatio on tehty samalla tavalla. Kommentin
ensimmäinen virke on yhteenveto, joka näkyy luetteloissa. Sen jälkeen
tulevat tarkennukset ja lopuksi tagit:

```{.java tiedosto="esimerkit/10-toimitus/src/main/java/fi/esimerkki/toimitus/Toimitus.java"}
```

| Merkintä | Tarkoitus |
|----------|-----------|
| `@param nimi` | parametrin merkitys, yksikkö ja sallitut arvot |
| `@return` | paluuarvo ja sen erikoistapaukset |
| `@throws Tyyppi` | milloin poikkeus heitetään; myös tarkistamattomat, jotka kuuluvat sopimukseen |
| `{@code teksti}` | koodia tekstin seassa |
| `{@link Luokka#metodi}`, `@see` | linkki toiseen kohtaan dokumentaatiossa |
| `{@value #VAKIO}` | vakion arvo, joka pysyy ajan tasalla |
| `{@snippet …}` | koodiesimerkki (Java 18) |

Kommentti kuvaa sopimuksen eli sen, mihin kutsuja voi luottaa: mitä
metodi vaatii, mitä se palauttaa ja milloin se epäonnistuu. Toteutusta
se ei toista. Pakkauksen yleiskuvaus kirjoitetaan tiedostoon
`package-info.java` ja moduulin kuvaus tiedostoon `module-info.java`.

`{@snippet}` voi sisältää koodin suoraan tai viitata tiedostoon.
Esimerkissä se viittaa testiluokan alueeseen, joka on rajattu
kommenteilla `// @start region="kaytto"` ja `// @end` (ks. seuraava
osio). Dokumentaation esimerkki on silloin koodia, joka käännetään ja
ajetaan testien mukana, joten se ei vanhene huomaamatta.

Dokumentaatio tuotetaan ja tarkistetaan komennolla

```
javadoc -quiet -Xdoclint:all -Werror --snippet-path src/test/java \
    -d target/javadoc $(find src/main/java -name '*.java')
```

`-Xdoclint:all` tarkistaa kommentit: puuttuva `@param`, `@return` tai
`@throws`, väärä parametrin nimi, rikkinäinen linkki ja virheellinen
HTML tuottavat varoituksen, esimerkiksi `warning: no @return`.
`-Werror` tekee varoituksista virheitä, jolloin puutteellinen
dokumentaatio pysäyttää CI:n samalla tavalla kuin käännösvirhe. Tämän
tutoriaalin testit ajavat komennon. Sama tarkistus toimii käännöksessä
(`javac -Xdoclint:all`). Mavenissa dokumentaation tuottaa
`maven-javadoc-plugin` ja Gradlessa tehtävä `javadoc`. Java 23:sta
lähtien kommentin voi kirjoittaa myös Markdown-muodossa
`///`-riveille.

Dokumentoi julkinen rajapinta: julkiset ja `protected`-jäsenet
pakkauksissa, joita muut käyttävät. Yksityisen apumetodin kommentti
on tavallinen `//`-kommentti silloin, kun nimi ei riitä. Yleiset
periaatteet, kuten lukijat ja dokumenttityypit, rajapintadokumentaation
tuottaminen koodista ja dokumentaation testaus, käsitellään taidossa
*Tekninen dokumentaatio*.

## Testaus: rakenne ja JUnit

Testi järjestää tilanteen, tekee toimenpiteen ja tarkistaa tuloksen
(*arrange, act, assert*). Javan vakiintunut testikehys on JUnit.
Testi on metodi, jossa on annotaatio `@Test`; kehys etsii annotoidut
metodit reflektiolla (luku 5), luo jokaista testiä varten uuden
testiluokan olion ja raportoi tulokset. Testiluokat ovat hakemistossa
`src/test/java` samassa pakkauksessa kuin testattava luokka, joten ne
näkevät myös pakkauksen sisäiset jäsenet. Edellisen osion luokan
testit:

```{.java tiedosto="esimerkit/10-toimitus/src/test/java/fi/esimerkki/toimitus/ToimitusTest.java"}
```

Testit ajetaan komennolla `./mvnw test` tai kehitysympäristön
painikkeesta. Maven kirjoittaa raportin hakemistoon
`target/surefire-reports`; sen yhteenveto on

```{.tuloste tiedosto="esimerkit/10-toimitus.odotettu"}
```

Parametrisoitu testi ajetaan kerran jokaisella rivillä, joten testejä
on seitsemän. Epäonnistunut vertailu heittää `AssertionError`in, jonka
viesti kertoo odotetun ja saadun arvon, ja Maven lopettaa virheeseen.

Huomioita:

- `assertEquals(odotettu, saatu)`: odotettu arvo on ensimmäinen
  parametri. Väärä järjestys tekee virheilmoituksesta harhaanjohtavan.
- `assertThrows` palauttaa poikkeuksen, jolloin myös viestin voi
  tarkistaa.
- Testit ovat rajatapauksia: täsmälleen ilmaisen toimituksen raja,
  5 000 ja 5 001 grammaa sekä virheellinen syöte. Odotetut arvot
  johdetaan vaatimuksesta (5 kg sisältyy perusmaksuun, jokainen alkava
  lisäkilo maksaa 100 senttiä), ei toteutuksesta; muuten testi vain
  toistaa koodin virheet.
- Testin nimi kertoo vaatimuksen. `@DisplayName` antaa raporttiin
  vapaamuotoisen nimen, ja `@BeforeEach` ajaa yhteisen alustuksen
  ennen jokaista testiä.

JUnitin nykyinen pääversio on 6 (2025), joka vaatii vähintään Java
17:n. Testien kirjoittamisen rajapinta (`org.junit.jupiter.api`) on
sama kuin JUnit 5:ssä, joten useimmat ohjeet ja esimerkit pätevät
molempiin. JUnit 4:n testit (`org.junit.Test`) näyttävät samalta mutta
ovat eri kehystä.

Muita yleisiä työkaluja ovat AssertJ (luettavammat vertailut:
`assertThat(lista).containsExactly(...)`), Mockito (testikaksoset
rajapinnoille), Testcontainers (oikea tietokanta kontissa testin
ajaksi) ja jqwik (ominaisuuspohjainen testaus). Kattavuuden mittaa
JaCoCo.

## Testattava rakenne

Testattavuus on suunnittelun ominaisuus, ei testikirjaston:

- **Riippuvuudet konstruktorin kautta.** Luvun 10 `TilausPalvelu`
  saa varaston ja kellon parametreina, joten testi antaa
  muistitoteutuksen ja kellon, jota se siirtää itse. Mockitoa
  tarvitaan vähemmän, kun rajapinnat ovat pieniä ja kaksonen on
  muutaman rivin lambda.
- **Satunnaisuus ja ympäristö ovat parametreja** samalla tavalla kuin
  aika: `RandomGenerator` ja asetusolio.
- **Puhdas ydin, ohut kuori.** Laskenta ja päätökset ovat puhtaita
  metodeja, jotka testataan ilman tiedostoja tai verkkoa. I/O on
  ohuessa kerroksessa, joka testataan integraatiotesteillä.

## Mikrovertailut: JMH

Lukujen 6 ja 9 mittaukset ovat suuntaa antavia. Luotettava mikrovertailu
tehdään JMH:lla (*Java Microbenchmark Harness*), joka ajaa jokaisen
mittauksen erillisessä JVM:ssä, lämmittää JIT:n, estää kuolleen koodin
poiston (`Blackhole`) ja raportoi hajonnan. Mittaus on luokka, jonka
metodeissa on annotaatio `@Benchmark`; JMH:n annotaatioprosessori
tuottaa niistä mittausohjelman. Seuraava luonnos näyttää rakenteen.
Sitä ei ajeta tämän tutoriaalin testeissä, koska JMH tarvitsee oman
rakennusprojektinsa ja tulokset riippuvat koneesta:

```
@State(Scope.Benchmark)
public class SummaBench {
    int[] taulukko = new int[1_000_000];

    @Benchmark
    public long silmukka() {
        long s = 0;
        for (int x : taulukko) s += x;
        return s;      // paluuarvo estää laskennan poiston
    }
}
```

Projektin pohja syntyy JMH:n Maven-arkkityypistä
(`jmh-java-benchmark-archetype`), ja tulos on taulukko, jossa on
jokaisen mittauksen keskiarvo ja virhemarginaali. Mittaa ensin
profiloimalla (JFR, async-profiler), mistä aika todella kuluu, ja
vasta sitten mikrovertaile yksittäisiä vaihtoehtoja.

## Koodin laatu

| Työkalu | Mitä tekee |
|---------|------------|
| Error Prone | kääntäjän laajennus; löytää yleiset virheet käännösaikana |
| NullAway | `null`-tarkistus annotaatioiden perusteella (Error Prone -laajennus) |
| SpotBugs | tavukoodin staattinen analyysi |
| Checkstyle, PMD | tyylisäännöt ja koodihajut |
| google-java-format, Spotless | automaattinen muotoilu |
| SonarQube | edellisten koonti ja seuranta |

## Lokit

Kirjastot kirjaavat SLF4J-rajapinnan kautta, ja sovellus valitsee
toteutuksen (Logback, Log4j 2). JDK:n oma `System.Logger` on vaihtoehto
kirjastolle, joka ei halua riippuvuuksia. Lokiviestit kirjoitetaan
parametrisoituina (`log.info("tilaus {} luotu", numero)`), jolloin
merkkijonoa ei koota, jos taso on pois päältä. Tuotannossa lokit ovat
rakenteisia (JSON), jotta niitä voi hakea kentittäin.

## Käytännössä

- **Varoitukset virheiksi.** `-Xlint:all -Werror`, `-Xdoclint`
  julkiselle rajapinnalle ja Error Prone CI:ssä. Uusi varoitus
  korjataan heti, kun konteksti on tuoreena.
- **Dokumentoi sopimus, älä toteutusta.** Javadoc julkisille
  tyypeille ja metodeille: mitä vaaditaan, mitä palautetaan, milloin
  epäonnistutaan. Esimerkit `{@snippet}`-viittauksina testattuun
  koodiin.
- **Testit kuvaavat käyttäytymistä.** Testin nimi kertoo vaatimuksen
  (`ilmainenToimitusRajalla`), ei metodia (`testMaksu2`).
  Parametrisoidut testit rajatapauksille.
- **Testikaksoset harkiten.** Liian moni mock testaa toteutusta, ei
  käyttäytymistä. Muistitoteutus (`MuistiVarasto`) on usein parempi kuin
  mock.
- **Profiloi tuotannossa JFR:llä.** Sen hinta on noin prosentti, ja se
  näyttää todelliset kuumat kohdat, allokaatiot ja lukkojen odotukset.
- **Säievedos jumiin.** `jcmd <pid> Thread.print` on ensimmäinen työkalu,
  kun palvelu ei vastaa.
- **Hinta.** Testien nopeus ratkaisee, ajetaanko niitä. Yksikkötestit
  ajetaan millisekunneissa; JVM:n käynnistys on kertaluonteinen hinta,
  joten testit ajetaan samassa JVM:ssä.

## Itsearviointi

- Osaat kääntää koodin kaikilla varoituksilla ja kertoa, mitä
  `-Xlint:all` tarkistaa.
- Osaat kirjoittaa Javadoc-kommentin, jossa on `@param`, `@return` ja
  `@throws`, ja tarkistaa dokumentaation `-Xdoclint`-valitsimella.
- Osaat kirjoittaa JUnit-testit rajatapauksille ja odotetuille
  poikkeuksille ja ajaa ne Mavenilla.
- Osaat rakentaa koodin testattavaksi riippuvuuksien, kellon ja puhtaan
  ytimen avulla.
- Osaat ottaa säievedoksen ja JFR-tallenteen käynnissä olevasta JVM:stä.
- Osaat kertoa, miksi mikrovertailuun tarvitaan JMH.
