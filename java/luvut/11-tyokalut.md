# Työkalut, testaus ja laatu {.runko-tyokalut}

Yleiset käännös-, testaus- ja CI-käytännöt käsitellään taidossa
*Käännösjärjestelmät, testaus ja CI*. Tämä luku kertoo Javan omat
välineet.

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

## Testaus: rakenne ja JUnit

Testi järjestää tilanteen, tekee toimenpiteen ja tarkistaa tuloksen
(*arrange, act, assert*). Tämän tutoriaalin esimerkit eivät käytä
ulkoisia kirjastoja, joten esimerkki toteuttaa pienen testiajurin.
Rakenne on sama kuin JUnitissa: nimetyt testit, vertailumetodit ja
odotettu poikkeus:

```{.java tiedosto="esimerkit/11-testit/Toimitus.java"}
```

```{.java tiedosto="esimerkit/11-testit/Testit.java"}
```

```{.java tiedosto="esimerkit/11-testit/Main.java"}
```

```{.tuloste tiedosto="esimerkit/11-testit.odotettu"}
```

Testit ovat rajatapauksia: täsmälleen ilmaisen toimituksen raja, 5 000
ja 5 001 grammaa sekä virheellinen syöte. Odotetut arvot johdetaan
vaatimuksesta (5 kg sisältyy perusmaksuun, jokainen alkava lisäkilo
maksaa 100 senttiä), ei toteutuksesta; muuten testi vain toistaa koodin
virheet.

JUnit 5:llä sama testi on luokka `src/test/java`-hakemistossa:

```
import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

class ToimitusTest {
    @ParameterizedTest
    @CsvSource({"manner, 800, 0, 590", "manner, 5001, 0, 690",
                "ahvenanmaa, 7500, 0, 1290"})
    void maksu(String alue, int paino, int ostokset, int odotettu) {
        assertEquals(odotettu, Toimitus.maksu(alue, paino, ostokset));
    }

    @Test
    void tuntematonAlue() {
        var e = assertThrows(IllegalArgumentException.class,
                () -> Toimitus.maksu("kuu", 100, 0));
        assertEquals("tuntematon alue: kuu", e.getMessage());
    }
}
```

Muita yleisiä työkaluja ovat AssertJ (luettavammat vertailut:
`assertThat(lista).containsExactly(...)`), Mockito (testikaksoset
rajapinnoille), Testcontainers (oikea tietokanta kontissa testin
ajaksi) ja jqwik (ominaisuuspohjainen testaus). Kattavuuden mittaa
JaCoCo.

## Testattava rakenne

Testattavuus on suunnittelun ominaisuus, ei testikirjaston:

- **Riippuvuudet konstruktorin kautta** (luku 9). Testi antaa
  muistitoteutuksen tai testikaksoisen. Mockitoa tarvitaan vähemmän,
  kun rajapinnat ovat pieniä ja kaksonen on muutaman rivin lambda.
- **Aika, satunnaisuus ja ympäristö ovat parametreja.** `Clock`,
  `RandomGenerator` ja asetusolio.
- **Puhdas ydin, ohut kuori.** Laskenta ja päätökset ovat puhtaita
  metodeja, jotka testataan ilman tiedostoja tai verkkoa. I/O on
  ohuessa kerroksessa, joka testataan integraatiotesteillä.

## Mikrovertailut: JMH

Luvun 5 ja 8 mittaukset ovat suuntaa antavia. Luotettava mikrovertailu
tehdään JMH:lla, joka ajaa jokaisen mittauksen erillisessä JVM:ssä,
lämmittää JIT:n, estää kuolleen koodin poiston (`Blackhole`) ja
raportoi hajonnan:

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

Mittaa ensin profiloimalla (JFR, async-profiler), mistä aika
todella kuluu, ja vasta sitten mikrovertaile yksittäisiä vaihtoehtoja.

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

- **Varoitukset virheiksi.** `-Xlint:all -Werror` ja Error Prone CI:ssä.
  Uusi varoitus korjataan heti, kun konteksti on tuoreena.
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
- Osaat kirjoittaa yksikkötestit rajatapauksille ja odotetuille
  poikkeuksille ja kertoa, miten ne kirjoitetaan JUnit 5:llä.
- Osaat rakentaa koodin testattavaksi riippuvuuksien, kellon ja puhtaan
  ytimen avulla.
- Osaat ottaa säievedoksen ja JFR-tallenteen käynnissä olevasta JVM:stä.
- Osaat kertoa, miksi mikrovertailuun tarvitaan JMH.
