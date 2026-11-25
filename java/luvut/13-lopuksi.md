# Lopuksi: käytännöt ja lähteet {.runko-kaytannot .runko-lahteet}

Tämä luku ei tuo uutta asiaa. Se kokoaa edellisten lukujen mallit,
säännöt ja hinnat yhteen paikkaan ja kertoo, mistä jatkaa.

## Mallit ja idiomit

| Malli | Javassa | Luku |
|-------|---------|------|
| Kapseloitu tila | luokka, `private`-kentät, validoiva konstruktori | 5 |
| Mallimetodi | abstrakti luokka, `final`-runko ja abstraktit vaiheet | 5 |
| Arvo-olio | `record` validoivalla kompaktilla konstruktorilla | 8 |
| Algebrallinen tietotyyppi | `sealed`-rajapinta, recordit ja `switch`-kuviot | 8 |
| Tilakone | `enum`-tila ja -tapahtuma, `switch`-lauseke | 4 |
| Staattinen tehdasmetodi | `Raha.euroa`, `List.of`, `Path.of` | 8 |
| Rakentaja | valinnaiset kentät, validointi `rakenna`-metodissa | 8 |
| Koristelija | sama rajapinta, delegointi | 8 |
| Strategia | funktionaalinen rajapinta ja lambda | 4, 8 |
| Konstruktori-injektio | riippuvuudet parametreina, kokoonpanon juuri `main`issa | 10 |
| Resurssin hallinta | `AutoCloseable` ja `try`-with-resources | 6 |
| Kääritty poikkeus | `throw new X("mitä tehtiin", syy)` | 9 |
| Tulostyyppi | `sealed interface Tulos<T>`: `Ok` tai `Virheet` | 9 |
| Puuttuva arvo | `Optional` paluuarvona | 9 |
| Tuottaja–kuluttaja | `BlockingQueue` ja lopetusviesti | 11 |
| Singleton | `enum`, jolla on yksi arvo | 5 |

## Nyrkkisäännöt

1. Kirjoita modernia Javaa: `record`, `sealed`, `switch`-lausekkeet,
   `var`, tekstilohkot, `List.of`, virtuaalisäikeet.
2. Tee luokista, kentistä ja kokoelmista muuttumattomia oletuksena.
3. Tee virheellisistä tiloista mahdottomia: validoi konstruktorissa ja
   käytä vahvoja tyyppejä.
4. Käytä `equals`ia olioille, toteuta `equals` ja `hashCode` yhdessä
   tai käytä `record`ia.
5. Älä palauta `null`ia kokoelmasta tai `Optional`ista.
6. Rahalle `long`-sentit tai `BigDecimal`, ei `double`.
7. Anna merkistö (`UTF_8`) ja kieliasetus (`Locale.ROOT`) aina
   eksplisiittisesti.
8. Poikkeukset poikkeuksille; odotetut virheet paluuarvoina. Kääri syyn
   kanssa, älä niele.
9. Sulje resurssit `try`-with-resources-lohkolla.
10. Koostaminen periytymisen sijaan; luokat `final`iksi.
11. Riippuvuudet konstruktorin kautta; aika `Clock`ina.
12. I/O-rinnakkaisuus virtuaalisäikeillä, CPU-rinnakkaisuus kiinteällä
    altaalla. Jaa vain muuttumatonta dataa.
13. `-Xlint:all -Werror`, staattinen analyysi ja automaattinen muotoilu
    CI:ssä. Julkinen rajapinta dokumentoidaan Javadocilla.
14. Mittaa ennen optimointia: JFR ja JMH.

## Hinnat yhdellä silmäyksellä

| Halpaa | Kallista |
|--------|----------|
| olion luonti, lyhytikäiset oliot | pitkäikäiset suuret rakenteet (GC:n työ) |
| rajapintakutsu yhdellä tai kahdella toteutuksella | megamorfinen kutsukohta (monta toteutusta) |
| `try` ilman heittoa | poikkeuksen luonti pinojälkineen |
| `int[]`, `IntStream` | `List<Integer>`, boksaus kuumassa silmukassa |
| kilpailematon `synchronized` | kilpailtu lukko, kontekstinvaihto |
| virtuaalisäie | käyttöjärjestelmän säie tehtävää kohden |
| `StringBuilder` | `+` silmukassa |
| lämmin JIT-käännetty koodi | JVM:n käynnistys ja lämpeneminen |

## Jatkotaidot

- *Kotlin*: sama JVM ja kirjastot, null-turvallisuus tyyppijärjestelmässä
  ja korutiinit.
- *Taustapalvelut*: Spring Boot, REST-rajapinnat, tietokannat ja
  tuotantovalmius.
- *Rinnakkaisohjelmointi*: muistimallit, lukottomat rakenteet ja
  rinnakkaisalgoritmit kieliriippumattomasti.
- *Tietorakenteet* ja *Algoritmit*: kokoelmien toteutukset ja niiden
  aikavaativuudet.
- *Android-sovellukset*: Androidin sovelluskehys (Kotlinilla).
- *Tekninen dokumentaatio*: rajapintadokumentaation periaatteet ja
  dokumentaation testaus.
- *Käännösjärjestelmät, testaus ja CI*: testauksen ja jatkuvan
  integraation yleiset käytännöt.

## Lähteet ja dokumentaatio

- **Java SE 21 -rajapintadokumentaatio:**
  <https://docs.oracle.com/en/java/javase/21/docs/api/>
- **Java Language Specification ja JVM Specification:**
  <https://docs.oracle.com/javase/specs/>
- **Javadoc-opas** (tagit, `{@snippet}`, doclint):
  <https://docs.oracle.com/en/java/javase/21/javadoc/>
- **dev.java**, Oraclen oppimateriaalit ja kielen uudistukset:
  <https://dev.java/learn/>
- **OpenJDK:n JEP-luettelo** (kaikki kielen ja alustan muutokset
  perusteluineen): <https://openjdk.org/jeps/0>
- **Inside Java** -blogi ja podcast JDK-kehittäjiltä:
  <https://inside.java/>
- **JMH:n esimerkit** mittaamisen sudenkuopista:
  <https://github.com/openjdk/jmh/tree/master/jmh-samples>
- **JUnitin käyttäjäopas:** <https://junit.org/junit5/docs/current/user-guide/>
- **Maven:** <https://maven.apache.org/guides/>,
  **Gradle:** <https://docs.gradle.org/>

### Kirjat

- Joshua Bloch: *Effective Java*, 3. painos (2018). Javan
  suunnittelusääntöjen perusteos; useimmat tämän tutoriaalin
  käytännöistä löytyvät siitä perusteluineen.
- Brian Goetz ym.: *Java Concurrency in Practice* (2006). Muistimalli ja
  rinnakkaisuus; ennen virtuaalisäikeitä kirjoitettu, mutta perusteet
  ovat ennallaan.
- Scott Oaks: *Java Performance*, 2. painos (2020). JIT, roskienkeruu ja
  mittaaminen.
- Cay Horstmann: *Core Java*, 13. painos (2024). Kattava kielen ja
  kirjaston käsikirja.

### Kirjastot

- **Guava** (Google): kokoelmat, välimuistit, apuluokat.
- **Caffeine**: suorituskykyinen välimuisti.
- **Jackson**: JSON-sarjallistus.
- **SLF4J** ja **Logback**: lokitus.
- **JUnit**, **AssertJ**, **Mockito**, **Testcontainers**: testaus.
- **Error Prone**, **NullAway**: käännösaikainen analyysi.
