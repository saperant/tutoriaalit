# Johdanto {.runko-johdanto}

Taustapalvelu (*backend*) on ohjelma, joka ottaa vastaan pyyntöjä
verkosta, toteuttaa sovelluksen säännöt ja tallentaa tiedot. Selain- ja
mobiilisovellukset, toiset palvelut ja eräajot kutsuvat sitä, yleensä
HTTP:n yli. Hyvä taustapalvelu on oikein toimiva myös silloin, kun
pyyntöjä tulee yhtä aikaa, verkko katkeaa kesken ja asiakas yrittää
uudelleen, ja sen toimintaa voi seurata tuotannossa.

Tutoriaali rakentaa yhden pienen mutta tuotantotapaisen palvelun:
verkkokaupan tuote- ja tilausrajapinnan. Sitä ennen HTTP:n perusasiat
käydään läpi ilman kehystä, jotta näkyy, mitä kehys tekee puolestamme.

## Esitiedot ja rajaus

Tutoriaali olettaa taidot *Java* (luokat, recordit, rajapinnat,
poikkeukset, säikeet), *SQL ja relaatiotietokannat* (skeema,
liitokset, transaktiot, indeksit) ja *Tietoverkot* (TCP/IP, DNS, TLS).
Niitä ei toisteta: esimerkiksi transaktioiden eristystasot on selitetty
SQL-tutoriaalissa, ja tässä katsotaan, miten ne näkyvät sovelluksessa.

Kontit, orkestrointi ja pilvipalvelut ovat taidossa *Kontit ja pilvi*,
ja usean palvelun arkkitehtuuri (viestijonot, välimuistit, skaalaus)
taidossa *Järjestelmäsuunnittelu*. Tämä tutoriaali päättyy siihen,
mitä yksi palvelu tarvitsee ollakseen valmis niiden osaksi.

## Pino ja valinnat

| Osa | Valinta | Miksi |
|-----|---------|-------|
| Kieli | Java 21 | Taitopuun esitieto; recordit, virtuaalisäikeet |
| Kehys | Spring Boot 4.2 | Yleisin Java-taustakehys; laaja ekosysteemi |
| Web | Spring MVC | Säiekohtainen malli, virtuaalisäikeet |
| Tietokanta-avaus | Spring Data JDBC ja JdbcClient | Ennustettava SQL, ei laiskaa latausta |
| Migraatiot | Flyway | SQL-tiedostot versionhallinnassa |
| Tietokanta | H2 (PostgreSQL-tila) | Ei asennusta; tuotannossa PostgreSQL |
| Turva | Spring Security | Todennus, valtuutus, CORS |
| Havainnointi | Actuator, Micrometer | Terveys, metriikat |
| Testit | JUnit 5, AssertJ, MockMvc | Kehyksen viipale- ja integraatiotestit |
| Käännös | Maven Wrapper | Sama Maven-versio kaikilla |

Valinnoille on vaihtoehtoja. Kotlin toimii samassa pinossa
sellaisenaan, Quarkus ja Micronaut tekevät samat asiat pienemmällä
käynnistysajalla, ja Go:n `net/http` tai Pythonin FastAPI ovat
kevyempiä kokonaisuuksia. Periaatteet – rajapinnan suunnittelu,
transaktiorajat, idempotenssi, todennus ja havainnointi – ovat samat
kaikissa.

**Miksi JDBC eikä JPA.** JPA (Hibernate) on Javan yleisin tapa
tallentaa olioita, ja moni työpaikka käyttää sitä. Sen laiska lataus,
istunnon välimuisti ja automaattinen muutosten seuranta piilottavat
kuitenkin, milloin ja mitä SQL:ää ajetaan, mikä on suorituskyky- ja
oikeellisuusongelmien yleisin lähde. Spring Data JDBC tallentaa
aggregaatin kerralla eksplisiittisellä `save`-kutsulla ilman
laiskaa latausta, ja JdbcClient ajaa kirjoitetun SQL:n sellaisenaan.
Kun nämä ovat hallussa, JPA:n käsitteet on helppo oppia, ja luvussa
5 kerrotaan, missä kohdin se toimii toisin.

**Miksi H2.** Esimerkkien pitää toimia ilman tietokantapalvelinta ja
Dockeria. H2 on Javalla toteutettu tietokanta, joka käynnistyy samaan
prosessiin. PostgreSQL-tilassa (`MODE=PostgreSQL`) se hyväksyy
PostgreSQL:n syntaksin riittävän hyvin, ja Spring Data JDBC tuottaa
SQL:n PostgreSQL-murteella. Tuotannossa käytetään oikeaa
PostgreSQL:ää, ja integraatiotestit ajetaan sitä vastaan
Testcontainers-kirjastolla (luku 10). SQLite olisi toinen vaihtoehto,
mutta sen yksi kirjoittaja kerrallaan ja tyypitys poikkeavat
palvelintietokannoista enemmän.

## Esimerkkiprojekti

Esimerkit ovat yksi Maven-projekti, jossa on kaksi modulia:

```text
esimerkit/
├── pom.xml                 yhteinen: Spring Boot -versio, Java 21
├── mvnw, .mvn/             Maven Wrapper
├── Makefile                make = ./mvnw verify
├── http-perusteet/         luku 2: HTTP pelkällä JDK:lla
└── kauppa/                 luvut 3–10: Spring Boot -palvelu
    ├── src/main/java/fi/tutoriaalit/kauppa/
    │   ├── tuote/          ohjain, palvelu, repository, aggregaatti
    │   ├── tilaus/
    │   ├── raportti/       JdbcClient-kyselyt
    │   ├── virheet/        RFC 9457 -ongelmakuvaukset
    │   ├── turva/          Spring Security
    │   └── havainnointi/   korrelaatiotunnus
    ├── src/main/resources/
    │   ├── application.yaml
    │   └── db/migration/   Flyway: V1__tuotteet.sql ...
    └── src/test/           yksikkö-, viipale- ja integraatiotestit
```

Paketointi on *ominaisuuksittain* (tuote, tilaus) eikä kerroksittain
(controllers, services). Kun ominaisuus muuttuu, muutokset ovat samassa
paketissa, ja paketin sisäiset luokat voi pitää paketin näkyvyydellä.

Kauppa-modulin riippuvuudet ovat Spring Bootin *startereita*: kukin tuo
yhden ominaisuuden kirjastot ja automaattisen konfiguraation. Versioita
ei kirjoiteta, koska ylätason `spring-boot-starter-parent` kiinnittää
ne yhteensopiviksi.

```{.xml tiedosto="esimerkit/kauppa/pom.xml" osa="riippuvuudet"}
```

Esimerkit ajetaan kehityskontissa tai koneella, jossa on JDK 21:

```text
make                  # kääntää ja ajaa kaikki testit
make aja              # käynnistää palvelun porttiin 8080
./mvnw -pl kauppa test -Dtest=TilausIntegraatioTest   # yksi testiluokka
```

Kaikki tekstissä näytetty koodi ja kaikki HTTP-keskustelut ovat
projektin tiedostoista, ja testit varmistavat niiden toiminnan.
Ensimmäinen ajo lataa Mavenin ja riippuvuudet (noin 150 Mt); sen
jälkeen koko testisarja kestää alle minuutin.

## Työkalut

- **IDE:** IntelliJ IDEA (Spring-tuki maksullisessa versiossa) tai
  VS Code Java- ja Spring Boot -laajennuksilla. Kehityskontti asentaa
  jälkimmäiset.
- **HTTP-asiakas:** `curl -i` näyttää otsakkeet; HTTPie (`http`) ja
  IDE:n `.http`-tiedostot ovat mukavampia. Bruno ja Postman tallentavat
  pyyntökokoelmia.
- **Tietokanta:** H2:n konsoli, DBeaver tai `psql`.
- **Maven:** `./mvnw dependency:tree` näyttää, mistä kirjasto tulee,
  ja `./mvnw versions:display-dependency-updates` päivitykset.
