# Paketit, modulit ja rakennus {.runko-modulit}

## Pakkaukset ja näkyvyys

*Pakkaus* (*package*) on nimiavaruus ja näkyvyyden yksikkö. Pakkauksen
nimi on käännetty verkkotunnus (`fi.esimerkki.tilaus`), ja lähdetiedostot
ovat sitä vastaavassa hakemistossa (`src/main/java/fi/esimerkki/tilaus/`).
Määre, jota ei kirjoiteta, tarkoittaa *pakkauksen sisäistä* näkyvyyttä.
Se on hyödyllisin näkyvyystaso: rajapinta on `public`, toteutus
pakkauksen sisäinen.

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

```{.java tiedosto="esimerkit/09-tilaukset/Tilaus.java"}
```

```{.java tiedosto="esimerkit/09-tilaukset/Varasto.java"}
```

```{.java tiedosto="esimerkit/09-tilaukset/MuistiVarasto.java"}
```

```{.java tiedosto="esimerkit/09-tilaukset/Varastot.java"}
```

## Riippuvuuksien injektointi ilman kehystä

`TilausPalvelu` ei luo riippuvuuksiaan, vaan saa ne konstruktorin
parametreina (*constructor injection*). Myös aika on riippuvuus:
`Clock` korvaa suoran `Instant.now()`-kutsun, jolloin testi voi
siirtää aikaa:

```{.java tiedosto="esimerkit/09-tilaukset/TilausPalvelu.java"}
```

Olioverkko kootaan yhdessä paikassa, *kokoonpanon juuressa*
(*composition root*), joka on yleensä `main`. Muu koodi ei tiedä,
mitkä toteutukset on valittu:

```{.java tiedosto="esimerkit/09-tilaukset/Main.java"}
```

```{.tuloste tiedosto="esimerkit/09-tilaukset.odotettu"}
```

Spring, Guice, Dagger ja Jakarta CDI automatisoivat saman kokoamisen.
Kehys on hyödyllinen suurissa sovelluksissa, mutta periaate on sama:
riippuvuudet tulevat konstruktorin kautta, ja luokka riippuu
rajapinnasta. Konstruktori-injektio toimii myös ilman kehystä ja tekee
riippuvuudet näkyviksi. Kenttä-injektiota (`@Autowired` kenttään) ei
suositella, koska olio voi olla olemassa ilman riippuvuuksiaan.

## Moduulijärjestelmä (JPMS)

Java 9:n *moduuli* on joukko pakkauksia, joilla on nimi, riippuvuudet ja
julkaistut pakkaukset. Moduulin kuvaus on juurihakemiston tiedostossa
`module-info.java`:

```
module fi.esimerkki.tilaus {
    requires java.net.http;
    exports fi.esimerkki.tilaus;          // julkinen rajapinta
    // fi.esimerkki.tilaus.sisainen ei näy muille moduuleille
}
```

Moduuli vahvistaa kapselointia: `public`-luokka on näkyvä moduulin
ulkopuolelle vain, jos sen pakkaus on `exports`-listalla. JDK itse on
jaettu moduuleiksi, ja `jlink` kokoaa niistä pienen ajoympäristön. Moni
sovellus käyttää kuitenkin edelleen pelkkää luokkapolkua (*classpath*),
ja kirjastot julkaisevat vähintään `Automatic-Module-Name`-tiedon.
Moduuli kannattaa kirjastolle, jonka sisäiset pakkaukset halutaan
piilottaa, ja sovellukselle, joka paketoidaan `jlink`illä.

## Rakennustyökalut: Maven ja Gradle

Oikeat projektit rakennetaan Mavenilla tai Gradlella. Ne lataavat
riippuvuudet Maven Central -palvelusta, kääntävät, ajavat testit ja
paketoivat. Hakemistorakenne on vakio:

```
tilaukset/
  pom.xml                       (Maven) tai build.gradle.kts (Gradle)
  src/main/java/fi/esimerkki/tilaus/*.java
  src/main/resources/           asetukset, mallit
  src/test/java/fi/esimerkki/tilaus/*Test.java
```

Mavenin `pom.xml` kuvaa projektin deklaratiivisesti:

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>fi.esimerkki</groupId>
  <artifactId>tilaukset</artifactId>
  <version>1.0.0</version>
  <properties>
    <maven.compiler.release>21</maven.compiler.release>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.junit.jupiter</groupId>
      <artifactId>junit-jupiter</artifactId>
      <version>5.11.3</version>
      <scope>test</scope>
    </dependency>
  </dependencies>
</project>
```

| Tehtävä | Maven | Gradle |
|---------|-------|--------|
| Käännös ja testit | `mvn verify` | `./gradlew build` |
| Pelkät testit | `mvn test` | `./gradlew test` |
| Riippuvuuspuu | `mvn dependency:tree` | `./gradlew dependencies` |
| Ajo | `mvn exec:java` | `./gradlew run` |

Kääre (`mvnw`, `gradlew`) kiinnittää työkalun version projektiin, joten
kaikki käyttävät samaa. Gradlen versioluettelo (`libs.versions.toml`) ja
Mavenin `dependencyManagement` (tai BOM) keskittävät riippuvuuksien
versiot.

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
- Osaat Mavenin ja Gradlen hakemistorakenteen ja peruskomennot.
