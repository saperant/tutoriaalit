# Lopuksi: käytännöt ja lähteet {.runko-kaytannot .runko-lahteet}

## Mallit ja idiomit

| Malli | Javassa | Luku |
|-------|---------|------|
| Arvo-olio | `record` validoivalla kompaktilla konstruktorilla | 7 |
| Algebrallinen tietotyyppi | `sealed`-rajapinta, recordit ja `switch`-kuviot | 7 |
| Tilakone | `enum`-tila ja -tapahtuma, `switch`-lauseke | 4 |
| Staattinen tehdasmetodi | `Raha.euroa`, `List.of`, `Path.of` | 7 |
| Rakentaja | valinnaiset kentät, validointi `rakenna`-metodissa | 7 |
| Koristelija | sama rajapinta, delegointi | 7 |
| Strategia | funktionaalinen rajapinta ja lambda | 4, 7 |
| Konstruktori-injektio | riippuvuudet parametreina, kokoonpanon juuri `main`issa | 9 |
| Resurssin hallinta | `AutoCloseable` ja `try`-with-resources | 5 |
| Kääritty poikkeus | `throw new X("mitä tehtiin", syy)` | 8 |
| Tulostyyppi | `sealed interface Tulos<T>`: `Ok` tai `Virheet` | 8 |
| Puuttuva arvo | `Optional` paluuarvona | 8 |
| Tuottaja–kuluttaja | `BlockingQueue` ja lopetusviesti | 10 |
| Singleton | `enum`, jolla on yksi arvo | 7 |

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
    CI:ssä.
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

## Jatko taitopuussa

- *Kotlin*: sama JVM ja kirjastot, null-turvallisuus tyyppijärjestelmässä
  ja korutiinit.
- *Taustapalvelut*: Spring Boot, REST-rajapinnat, tietokannat ja
  tuotantovalmius.
- *Rinnakkaisohjelmointi*: muistimallit, lukottomat rakenteet ja
  rinnakkaisalgoritmit kieliriippumattomasti.
- *Tietorakenteet* ja *Algoritmit*: kokoelmien toteutukset ja niiden
  aikavaativuudet.
- *Android-sovellukset*: Androidin sovelluskehys (Kotlinilla).

## Lähteet ja dokumentaatio

- **Java SE 21 -rajapintadokumentaatio:**
  <https://docs.oracle.com/en/java/javase/21/docs/api/>
- **Java Language Specification ja JVM Specification:**
  <https://docs.oracle.com/javase/specs/>
- **dev.java**, Oraclen oppimateriaalit ja kielen uudistukset:
  <https://dev.java/learn/>
- **OpenJDK:n JEP-luettelo** (kaikki kielen ja alustan muutokset
  perusteluineen): <https://openjdk.org/jeps/0>
- **Inside Java** -blogi ja podcast JDK-kehittäjiltä:
  <https://inside.java/>
- **JMH:n esimerkit** mittaamisen sudenkuopista:
  <https://github.com/openjdk/jmh/tree/master/jmh-samples>
- **JUnit 5 -käyttäjäopas:** <https://junit.org/junit5/docs/current/user-guide/>
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
- **JUnit 5**, **AssertJ**, **Mockito**, **Testcontainers**: testaus.
- **Error Prone**, **NullAway**: käännösaikainen analyysi.

## Lisenssi

Tämä tutoriaali on lisensoitu CC BY-SA 4.0 -lisenssillä. Esimerkkikoodi
on kirjoitettu tätä tutoriaalia varten. Lähteinä on käytetty Javan
virallista dokumentaatiota ja JEP-kuvauksia, joihin viitataan
linkein; niiden tekstiä ei ole kopioitu.
