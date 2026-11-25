# Pakkaukset, moduulit ja rakennus {.runko-modulit}

Tähän asti jokainen esimerkki on ollut yksi tiedosto. Oikea ohjelma
on satoja luokkia, joten tarvitaan tapa ryhmitellä ne, piilottaa
toteutus ja koota osat yhteen. Tämä luku etenee pienestä suureen:
pakkaus rajaa näkyvyyden, konstruktori-injektio kytkee luokat
toisiinsa rajapintojen kautta, moduuli rajaa pakkausten näkyvyyden ja
rakennustyökalu hoitaa riippuvuudet, käännöksen ja paketoinnin.

## Pakkaukset ja näkyvyys

*Pakkaus* (*package*) on nimiavaruus ja näkyvyyden yksikkö. Pakkauksen
nimi on käännetty verkkotunnus (`fi.esimerkki.tilaus`), ja lähdetiedostot
ovat sitä vastaavassa hakemistossa (`src/main/java/fi/esimerkki/tilaus/`).
Tiedoston ensimmäinen lause `package fi.esimerkki.tilaus;` kertoo
pakkauksen, ja toisen pakkauksen tyypit otetaan käyttöön
`import`-lauseella. Luvun 5 näkyvyysmääreet saavat pakkauksista
merkityksensä. Määre, jota ei kirjoiteta, tarkoittaa *pakkauksen
sisäistä* näkyvyyttä. Se on hyödyllisin näkyvyystaso: rajapinta on
`public`, toteutus pakkauksen sisäinen.

| Määre | Luokka | Pakkaus | Aliluokka | Kaikki |
|-------|--------|---------|-----------|--------|
| `private` | x | | | |
| (ei määrettä) | x | x | | |
| `protected` | x | x | x | |
| `public` | x | x | x | x |

Seuraava esimerkki on pieni tilaussovellus. Pakkaus `fi.esimerkki.tilaus`
julkaisee tyypin `Tilaus`, rajapinnan `Varasto`, tehdasluokan
`Varastot` ja palvelun `TilausPalvelu`. Toteutus `MuistiVarasto` on
pakkauksen sisäinen, joten sitä ei voi käyttää eikä siitä voi riippua
pakkauksen ulkopuolella:

```{.java tiedosto="esimerkit/10-tilaukset/Tilaus.java"}
```

```{.java tiedosto="esimerkit/10-tilaukset/Varasto.java"}
```

```{.java tiedosto="esimerkit/10-tilaukset/MuistiVarasto.java"}
```

```{.java tiedosto="esimerkit/10-tilaukset/Varastot.java"}
```

## Riippuvuuksien injektointi ilman kehystä

Pakkausjako kertoo, mitkä luokat näkevät toisensa. Seuraava kysymys
on, miten oliot saavat käyttöönsä toisensa. `TilausPalvelu` ei luo
riippuvuuksiaan, vaan saa ne konstruktorin parametreina (*constructor
injection*). Myös aika on riippuvuus: `Clock` korvaa suoran
`Instant.now()`-kutsun (luku 7), jolloin testi voi siirtää aikaa:

```{.java tiedosto="esimerkit/10-tilaukset/TilausPalvelu.java"}
```

Olioverkko kootaan yhdessä paikassa, *kokoonpanon juuressa*
(*composition root*), joka on yleensä `main`. Muu koodi ei tiedä,
mitkä toteutukset on valittu. Esimerkin kello on abstraktin luokan
`Clock` aliluokka, jota siirretään käsin:

```{.java tiedosto="esimerkit/10-tilaukset/Main.java"}
```

```{.tuloste tiedosto="esimerkit/10-tilaukset.odotettu"}
```

Spring, Guice, Dagger ja Jakarta CDI automatisoivat saman kokoamisen.
Kehys on hyödyllinen suurissa sovelluksissa, mutta periaate on sama:
riippuvuudet tulevat konstruktorin kautta, ja luokka riippuu
rajapinnasta. Konstruktori-injektio toimii myös ilman kehystä ja tekee
riippuvuudet näkyviksi. Kenttä-injektiota (`@Autowired` kenttään) ei
suositella, koska olio voi olla olemassa ilman riippuvuuksiaan.

## Moduulijärjestelmä (JPMS)

Java 9:n *moduuli* on joukko pakkauksia, joilla on nimi, riippuvuudet ja
julkaistut pakkaukset. Moduulin kuvaus on lähdekoodin juurihakemiston
tiedostossa `module-info.java`. Seuraavan osion projektin kuvaus on
lyhyt:

```{.java tiedosto="esimerkit/10-toimitus/src/main/java/module-info.java"}
```

`exports` julkaisee pakkauksen muille moduuleille, ja `requires` (jota
tässä ei tarvita) ilmoittaa moduulin, josta tämä riippuu; `java.base`
on aina mukana. Moduuli vahvistaa kapselointia: `public`-luokka näkyy
moduulin ulkopuolelle vain, jos sen pakkaus on `exports`-listalla.
Pakkaus, jota ei julkaista, on moduulin sisäinen, vaikka sen luokat
olisivat `public`. JDK itse on jaettu moduuleiksi, ja `jlink` kokoaa
niistä pienen ajoympäristön. Moni sovellus käyttää kuitenkin edelleen
pelkkää luokkapolkua (*classpath*), ja kirjastot julkaisevat vähintään
`Automatic-Module-Name`-tiedon. Moduuli kannattaa kirjastolle, jonka
sisäiset pakkaukset halutaan piilottaa, ja sovellukselle, joka
paketoidaan `jlink`illä.

## Rakennustyökalut: Maven ja Gradle

Oikeat projektit rakennetaan Mavenilla tai Gradlella. Ne lataavat
riippuvuudet Maven Central -palvelusta, kääntävät, ajavat testit ja
paketoivat. Hakemistorakenne on vakio. Esimerkkiprojekti
`esimerkit/10-toimitus` laskee toimitusmaksuja; sen koodi ja testit
käydään läpi luvussa 12:

```
10-toimitus/
  pom.xml                       projektin kuvaus
  mvnw, .mvn/                   Maven Wrapper ja sen asetukset
  src/main/java/module-info.java
  src/main/java/fi/esimerkki/toimitus/Toimitus.java
  src/test/java/fi/esimerkki/toimitus/ToimitusTest.java
  target/                       käännöstuotteet (ei versionhallintaan)
```

Resurssit, kuten asetustiedostot ja mallit, ovat hakemistossa
`src/main/resources`. Gradle-projektissa `pom.xml`in tilalla on
`build.gradle.kts`, muu rakenne on sama. Mavenin `pom.xml` kuvaa
projektin deklaratiivisesti:

```{.xml tiedosto="esimerkit/10-toimitus/pom.xml"}
```

Projekti käännetään ja testataan komennolla `./mvnw test`. Maven lataa
JUnitin ja sen riippuvuudet paikalliseen välimuistiin (`~/.m2`), kääntää
lähdekoodin hakemistoon `target/classes` ja ajaa testit.

| Tehtävä | Maven | Gradle |
|---------|-------|--------|
| Käännös ja testit | `mvn verify` | `./gradlew build` |
| Pelkät testit | `mvn test` | `./gradlew test` |
| Paketointi | `mvn package` | `./gradlew jar` |
| Riippuvuuspuu | `mvn dependency:tree` | `./gradlew dependencies` |
| Ajo | `mvn exec:java` | `./gradlew run` |

Kääre (`mvnw`, `gradlew`) kiinnittää työkalun version projektiin, joten
kaikki käyttävät samaa. Gradlen versioluettelo (`libs.versions.toml`) ja
Mavenin `dependencyManagement` (tai BOM) keskittävät riippuvuuksien
versiot.

Käännetyt luokat jaetaan JAR-arkistona, joka on zip-tiedosto luokkia,
resursseja ja kuvaustiedosto `META-INF/MANIFEST.MF`. `mvn package`
tekee arkiston hakemistoon `target`. Ilman rakennustyökalua sama
tehdään JDK:n komennolla `jar`; kun kuvaustiedostossa on pääluokka,
arkiston voi ajaa suoraan:

```
javac -d luokat 10-tilaukset/*.java
jar --create --file tilaukset.jar --main-class Main -C luokat .
java -jar tilaukset.jar
```

## Käytännössä

- **Pakkaus ominaisuuden mukaan, ei kerroksen mukaan.** `tilaus`,
  `asiakas`, `lasku`, joissa kussakin on omat tyypit, palvelut ja
  varastot, on parempi kuin `controller`, `service`, `repository`,
  koska ominaisuuden sisäiset luokat voivat olla pakkauksen sisäisiä.
- **Pienin mahdollinen näkyvyys.** Oletuksena pakkauksen sisäinen tai
  `private`; `public` vain rajapinnalle.
- **Konstruktori-injektio ja kokoonpanon juuri.** Luokka ei kutsu
  `new`iä riippuvuuksilleen eikä hae niitä staattisesta rekisteristä.
  Kello, satunnaisluvut ja ympäristö ovat riippuvuuksia.
- **Riippuvuudet harkiten.** Jokainen kirjasto tuo transitiivisia
  riippuvuuksia ja haavoittuvuuksia. Tarkista `dependency:tree` ja
  käytä riippuvuuksien tarkistusta (OWASP Dependency-Check, Dependabot).
- **`--release 21`.** Kääntäjän valitsin `--release` (Mavenissa
  `maven.compiler.release`) takaa, ettei koodi käytä uudempien
  JDK-versioiden rajapintoja.
- **Hinta.** Luokkien lataus ja alustus tapahtuvat ensimmäisellä
  käytöllä, mikä näkyy käynnistysajassa. Suuri luokkapolku hidastaa
  käynnistystä; *Class Data Sharing* (CDS) ja AOT-välimuisti (Java 24)
  lyhentävät sitä.

## Itsearviointi

- Osaat jakaa koodin pakkauksiin ja käyttää pakkauksen sisäistä
  näkyvyyttä toteutuksen piilottamiseen.
- Osaat toteuttaa konstruktori-injektion ja koota olioverkon
  kokoonpanon juuressa ilman kehystä.
- Osaat tehdä ajasta testattavan `Clock`-riippuvuudella.
- Osaat kertoa, mitä `module-info.java` lisää pakkausten näkyvyyteen.
- Osaat Mavenin ja Gradlen hakemistorakenteen ja peruskomennot ja lukea
  `pom.xml`-tiedoston.
- Osaat paketoida ohjelman JAR-arkistoksi ja ajaa sen.
