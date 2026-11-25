# Johdanto {.runko-johdanto}

Java on vahvasti ja staattisesti tyypitetty oliokieli, jonka ohjelmat
käännetään tavukoodiksi ja ajetaan Javan virtuaalikoneessa (JVM). Kieli
julkaistiin vuonna 1995, ja se on edelleen yksi käytetyimmistä
ohjelmointikielistä erityisesti palvelinohjelmistoissa. Tämä tutoriaali
opettaa modernia Javaa (Java 21) lukijalle, joka osaa ohjelmoinnin
perusteet, ja kertoo, mitä JVM-alustalla mikin maksaa.

## Esitiedot ja rajaus

Esitietona on taito *Ohjelmoinnin perusteet (Python)*: muuttujat,
ehdot, silmukat, funktiot, listat ja sanakirjat sekä luokan käsite
ovat tuttuja. Javan oliomalli, staattinen tyypitys ja kirjasto
opetetaan alusta, ja eroja Pythoniin nostetaan esiin siellä, missä ne
yllättävät.

Tutoriaali ei käsittele seuraavia aiheita:

- sovelluskehykset (Spring Boot), REST-rajapinnat ja tietokantayhteydet:
  taito *Taustapalvelut*
- Android: taito *Android-sovellukset*
- rinnakkaisuuden yleinen teoria: taito *Rinnakkaisohjelmointi*
- algoritmien ja tietorakenteiden toteutus: taidot *Algoritmit* ja
  *Tietorakenteet*
- käyttöliittymäkirjastot (Swing, JavaFX) ja JVM:n sisäinen toteutus.

## Historia ja nykytila

| Vuosi | Versio | Merkittävää |
|-------|--------|-------------|
| 1995 | Java 1.0 | Sun Microsystems: "kirjoita kerran, aja kaikkialla" |
| 2004 | Java 5 | geneerisyys, autoboxing, `enum`, for-each, `java.util.concurrent` |
| 2006–2007 | OpenJDK | Javan toteutus avoimeksi lähdekoodiksi (GPLv2 + Classpath-poikkeus) |
| 2014 | Java 8 (LTS) | lambdat, streamit, `Optional`, `java.time` |
| 2017 | Java 9 | moduulijärjestelmä (JPMS), `jshell` |
| 2018 | Java 10 ja 11 (LTS) | `var`, `HttpClient`, lähdekooditiedoston suora ajo |
| 2021 | Java 17 (LTS) | `record`, `sealed`, tekstilohkot, kuvioiden sovitus `instanceof` |
| 2023 | Java 21 (LTS) | virtuaalisäikeet, kuvioiden sovitus `switch`, record-kuviot, järjestetyt kokoelmat |
| 2025 | Java 25 (LTS) | kompaktit lähdetiedostot ja instanssin `main`, moduulien tuonti |

Oracle osti Sunin vuonna 2010. Nykyään Java kehitetään avoimesti
OpenJDK-projektissa, ja vuodesta 2018 uusi versio on julkaistu
maaliskuussa ja syyskuussa. Joka toinen vuosi julkaistava versio on pitkäaikaisesti
tuettu (*LTS*), ja tuotannossa käytetään yleensä niitä. Tämä
tutoriaali käyttää Java 21:tä, joka on Ubuntu 24.04:n oletus-JDK. Uudet
ominaisuudet, joita ei vielä ole Java 21:ssä (esim. Java 22:n nimetön
muuttuja `_`), mainitaan erikseen.

## Käyttökohteet

- **Palvelinohjelmistot.** Pankit, vakuutusyhtiöt, kauppa,
  viranomaiset ja suuret verkkopalvelut ajavat Javaa. Spring Boot,
  Quarkus ja Micronaut ovat yleisimmät kehykset (taito *Taustapalvelut*).
- **Datan käsittely.** Kafka, Hadoop, Spark, Flink, Elasticsearch ja
  Cassandra on kirjoitettu Javalla tai muulla JVM-kielellä.
- **Android.** Androidin sovelluskehys on Javaa, vaikka uudet sovellukset
  kirjoitetaan nykyään Kotlinilla (taito *Kotlin*).
- **Työkalut.** IntelliJ IDEA, Eclipse, Gradle, Maven, Jenkins ja
  Bazel ovat Java-ohjelmia.
- **JVM-alusta.** Kotlin, Scala, Clojure ja Groovy käyttävät samaa
  virtuaalikonetta ja kirjastoja.

**Mihin Java ei sovellu hyvin:** lyhytikäisiin komentorivityökaluihin
(JVM:n käynnistys ja lämpeneminen kestävät satoja millisekunteja),
pieniin sulautettuihin laitteisiin ja ohjelmiin, joiden muistinkäytön ja
viiveen on oltava ennustettavia mikrosekunnin tarkkuudella. GraalVM:n
*native image* kääntää Java-ohjelman suoraan konekieleksi ja poistaa
käynnistysviiveen, mutta rajoittaa dynaamisia piirteitä, kuten
reflektiota.

## Toteutukset ja työkalut

Java-kehitysympäristö (*JDK*) sisältää kääntäjän, virtuaalikoneen ja
työkalut. OpenJDK:sta on useita ilmaisia jakeluita: Eclipse Temurin,
Amazon Corretto, Microsoft Build of OpenJDK, Azul Zulu ja Oraclen
OpenJDK-käännökset. Ne ovat käytännössä samaa koodia.

| Työkalu | Tehtävä |
|---------|---------|
| `javac` | kääntää `.java`-tiedostot `.class`-tavukoodiksi |
| `java` | käynnistää JVM:n ja ajaa ohjelman (myös suoraan lähdetiedostosta) |
| `jshell` | vuorovaikutteinen tulkki kokeiluihin |
| `jar` | paketoi luokat `.jar`-arkistoksi |
| `javadoc` | tuottaa dokumentaation `/** */`-kommenteista (luku 12) |
| `jcmd`, `jfr` | ajossa olevan JVM:n tila, Java Flight Recorder -profilointi |
| Maven, Gradle | rakennus, riippuvuudet ja testit (luku 10) |

Tämän tutoriaalin esimerkit käännetään valitsimilla
`javac -Xlint:all -Werror`, eli kaikki kääntäjän varoitukset ovat
virheitä. Kehityskontissa (`.devcontainer/java`) on OpenJDK 21.
Kehitysympäristöksi (IDE) sopivat IntelliJ IDEA, Eclipse ja Visual
Studio Code Java-laajennuksineen.

## Ensimmäinen ohjelma

Ensimmäinen ohjelma laskee syötteen yleisimmät sanat. Se näyttää
Java-ohjelman perusrakenteen: luokka, `main`-metodi, tuonnit
(`import`), kokoelmat ja virrat (*stream*).

```{.java tiedosto="esimerkit/01-sanat.java"}
```

```{.tuloste tiedosto="esimerkit/01-sanat.odotettu"}
```

Huomioita:

- Kaikki koodi on luokan sisällä. `main`-metodi on ohjelman
  aloituskohta, ja se on `public static`. Tässä luokka on vain kehys
  funktioille; luokat ja oliot käsitellään luvussa 5.
- Luokka on `final` ja sen konstruktori `private`, koska luokasta ei ole
  tarkoitus tehdä olioita. Tämä on Javan tapa tehdä pelkkiä staattisia
  metodeja sisältävä apuluokka.
- `throws IOException` kertoo, että metodi voi heittää tarkistetun
  poikkeuksen. Kääntäjä vaatii sen (luku 9).
- Syötteen ja tulosteen merkistö annetaan aina eksplisiittisesti
  (`UTF_8`). Syy selitetään luvussa 3.

Ohjelma ajetaan joko kääntämällä ensin tai suoraan lähdetiedostosta:

```
javac -d luokat 01-sanat.java
java -cp luokat Main < 01-sanat.syote
java 01-sanat.java < 01-sanat.syote    # kääntää muistiin ja ajaa
```

## Tämän tutoriaalin rakenne

Luku 2 on tiivistelmä kokeneelle kehittäjälle. Luvut 3–9 käyvät läpi
kielen: tyypit ja taulukot (3), ohjausrakenteet ja lambdat (4), luokat
ja oliot (5), muistimalli (6), kokoelmat, tiedostot ja aika (7),
recordit, suljetut hierarkiat ja geneerisyys (8) sekä virheet (9).
Luvut 10–12 käsittelevät projektin rakennetta, rinnakkaisuutta ja
työkaluja. Luku 13 kokoaa käytännöt ja lähteet. Jokaisen luvun lopussa
on *Käytännössä*-osio, joka kertoo, miten ammattilaiset asiaa käyttävät,
ja *Itsearviointi*, jonka avulla kokenut lukija voi ohittaa luvun.
Ohjelmoinnin perusteista tuleva lukee luvut järjestyksessä luvusta 3
alkaen ja palaa lukuun 2 kertauksena.

Esimerkit ovat hakemistossa `esimerkit`, ja ne ajetaan kuten edellä:
`java 03-lasku.java`. Pääluokan nimi on aina `Main`, ja tiedostonimi
kertoo luvun ja aiheen. Koska luokka ei ole `public`, tiedoston nimen
ei tarvitse olla sama kuin luokan. Tarkoituksella virheellisten
esimerkkien nimessä on `.ei-kaanny` ja ajossa kaatuvien `.kaatuu`.
Hakemistoesimerkki `10-tilaukset` käännetään komennolla
`javac -d luokat 10-tilaukset/*.java`, ja Maven-projekti `10-toimitus`
testataan komennolla `./mvnw test`. Valmis ympäristö on kehityskontti
`.devcontainer/java`.
